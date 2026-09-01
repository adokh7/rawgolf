#!/usr/bin/env python3
"""Finalize page-specific metadata after an article is built from the scaffold.

The repository is a static site, so article generators copy a shared HTML
scaffold before writing the article body. This module is the final guardrail
that replaces the scaffold's article-specific OG and JSON-LD fields with data
from the generated page itself.

It can be used by generators as ``finalize_html(html, output_path, force=True)``
or run against the current tree with ``--apply``/``--check``. The command-line
mode only touches pages carrying the known scaffold markers.
"""

from __future__ import annotations

import argparse
import calendar
import html
import json
import re
import sys
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

try:
    from scripts.image_markup import normalize_image_markup
    from scripts.article_schema import normalize_article_schema
except ImportError:  # direct execution from the scripts directory
    from image_markup import normalize_image_markup
    from article_schema import normalize_article_schema


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.golfraw.com"
TEMPLATE_NAME = "article-template.html"
STALE_HEADLINE = "Oakmont Is Eating the Field Alive — and the USGA Planned It That Way"
STALE_IMAGE_ALT = (
    "The first green at Oakmont Country Club during US Open 2026 setup, "
    "with championship rough visible"
)
STALE_SCHEMA_IMAGE = f"{SITE}/public/img/oakmont-2026-setup-og.jpg"
TEMPLATE_URL = f"{SITE}/article-template"
STALE_TOP_TITLE = "Oakmont Is Eating the Field Alive | GOLFRAW"
STALE_DESCRIPTION_PREFIX = "Average score 74.8"
STALE_PUBLISHED = "2026-06-13T07:30:00+02:00"
STALE_MODIFIED = "2026-06-13T09:42:00+02:00"
STALE_TAGS = {"US Open", "Oakmont", "Course Setup"}
DEFAULT_ROBOTS = "index, follow, max-image-preview:large"
DEPLOY_IGNORED_DIRS = {
    ".agents",
    ".gemini",
    ".github",
    ".git",
    ".system_generated",
    ".vercel",
    "__pycache__",
    "node_modules",
}

ATTR_RE = re.compile(
    r"([:\w-]+)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+))", re.S
)
META_TAG_RE = re.compile(r"<meta\b[^>]*>", re.I | re.S)
LINK_TAG_RE = re.compile(r"<link\b[^>]*>", re.I | re.S)
HEAD_RE = re.compile(r"(<head\b[^>]*>)(.*?)(</head\s*>)", re.I | re.S)
TITLE_RE = re.compile(r"<title\b[^>]*>(.*?)</title\s*>", re.I | re.S)
MANAGED_COMMENT_RE = re.compile(
    r"(?m)^[ \t]*<!-- SEO audit metadata: managed by scripts/fix_seo_audit\.py -->"
    r"[ \t]*(?:\r?\n|$)",
    re.I,
)
HEAD_TAG_LINE_RE = re.compile(
    r"(?m)^[ \t]*(?:<title\b.*?</title\s*>|<link\b[^>]*>|<meta\b[^>]*>)"
    r"[ \t]*(?:\r?\n|$)",
    re.I | re.S,
)
SCRIPT_RE = re.compile(
    r"<script\b[^>]*type\s*=\s*[\"']application/ld\+json[\"'][^>]*>"
    r"(.*?)</script\s*>",
    re.I | re.S,
)
PUBLISHED_RE = re.compile(
    r"PUBLISHED\s*(?:<[^>]+>\s*)*"
    r"(?:(?:[A-Z]{3}\s+)?(\d{1,2})\s+([A-Z]{3})"
    r"|(?:[A-Z]{3}\s+)?([A-Z]{3})\s+(\d{1,2}))"
    r"(?:\s+(\d{4}))?",
    re.I,
)


def attrs(tag: str) -> dict[str, str]:
    result = {}
    for match in ATTR_RE.finditer(tag):
        value = next(group for group in match.groups()[1:] if group is not None)
        result[match.group(1).lower()] = html.unescape(value)
    return result


class PageParser(HTMLParser):
    """Collect only the page-owned values needed to replace scaffold fields."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.meta: dict[str, list[str]] = {}
        self.canonical = ""
        self.json_ld: list[str] = []
        self.h1 = ""
        self.standfirst = ""
        self.category = ""
        self.body_images: list[tuple[str, str]] = []
        self.tags: list[str] = []
        self._capture = ""
        self._buffer: list[str] = []
        self._head_depth = 0
        self._body_depth = 0
        self._tag_row_tag = ""

    def handle_starttag(self, tag: str, attributes_list) -> None:  # type: ignore[no-untyped-def]
        tag = tag.lower()
        attr = {str(key).lower(): (value or "") for key, value in attributes_list}
        if tag == "head":
            self._head_depth += 1
        elif tag == "body":
            self._body_depth += 1

        if tag == "meta":
            key = (attr.get("name") or attr.get("property") or "").lower()
            if key:
                self.meta.setdefault(key, []).append(attr.get("content", ""))
        elif tag == "link" and "canonical" in attr.get("rel", "").lower().split():
            self.canonical = attr.get("href", "")
        elif tag == "script" and attr.get("type") == "application/ld+json":
            self._capture = "json"
            self._buffer = []
        elif tag == "h1":
            self._capture = "h1"
            self._buffer = []
        elif tag == "p" and "standfirst" in attr.get("class", "").split():
            self._capture = "standfirst"
            self._buffer = []
        elif (
            self._body_depth
            and not self.category
            and "cat" in attr.get("class", "").split()
        ):
            self._capture = "category"
            self._buffer = []
        elif tag == "img" and self._body_depth and not self._head_depth:
            src = attr.get("src", "")
            if src:
                self.body_images.append((src, attr.get("alt", "")))
        elif "tag-row" in attr.get("class", "").split():
            self._tag_row_tag = tag
        elif tag == "a" and self._tag_row_tag:
            self._capture = "tag"
            self._buffer = []

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "script" and self._capture == "json":
            self.json_ld.append("".join(self._buffer))
            self._capture = ""
            self._buffer = []
        elif tag == "h1" and self._capture == "h1":
            self.h1 = " ".join("".join(self._buffer).split())
            self._capture = ""
            self._buffer = []
        elif tag == "p" and self._capture == "standfirst":
            self.standfirst = " ".join("".join(self._buffer).split())
            self._capture = ""
            self._buffer = []
        elif self._capture == "category" and tag in {"span", "div"}:
            self.category = " ".join("".join(self._buffer).split())
            self._capture = ""
            self._buffer = []
        elif tag == "a" and self._capture == "tag":
            self.tags.append(" ".join("".join(self._buffer).split()))
            self._capture = ""
            self._buffer = []
        elif tag == self._tag_row_tag:
            self._tag_row_tag = ""
        elif tag == "head":
            self._head_depth = max(0, self._head_depth - 1)
        elif tag == "body":
            self._body_depth = max(0, self._body_depth - 1)


def parse_page(source: str) -> tuple[PageParser, list[object]]:
    parser = PageParser()
    parser.feed(source)
    documents: list[object] = []
    for block in parser.json_ld:
        try:
            documents.append(json.loads(block))
        except json.JSONDecodeError:
            continue
    return parser, documents


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def article_nodes(documents: list[object]):
    return [
        node
        for document in documents
        for node in walk(document)
        if node.get("@type") in ("Article", "NewsArticle")
    ]


def load_registry() -> dict[str, dict[str, str]]:
    data = json.loads((ROOT / "articles.json").read_text(encoding="utf-8"))
    return {record.get("slug", ""): record for record in data.get("articles", [])}


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def page_record(path: Path) -> dict[str, str]:
    registry = load_registry()
    return registry.get(path.stem, {})


def is_stale_scaffold_value(value: str) -> bool:
    value = clean(value)
    return value in {
        STALE_TOP_TITLE,
        TEMPLATE_URL,
        STALE_SCHEMA_IMAGE,
    } or value.startswith(STALE_DESCRIPTION_PREFIX)


def published_date(source: str, parser: PageParser, record: dict[str, str]) -> str:
    match = PUBLISHED_RE.search(source)
    if match:
        if match.group(1):
            day = int(match.group(1))
            month_name = match.group(2)
        else:
            month_name = match.group(3)
            day = int(match.group(4))
        month = list(calendar.month_abbr).index(month_name.title())
        year = match.group(5)
        if not year:
            record_date = record.get("date", "")
            year = record_date[:4] if re.match(r"^\d{4}-\d{2}-\d{2}$", record_date) else ""
        if year:
            return date(int(year), month, day).isoformat()

    existing = (parser.meta.get("article:published_time") or [""])[0]
    if re.match(r"^\d{4}-\d{2}-\d{2}", existing):
        return existing[:10]
    if re.match(r"^\d{4}-\d{2}-\d{2}$", record.get("date", "")):
        return record["date"]
    raise ValueError("page has no page-specific publication date")


def local_url(raw: str) -> str:
    raw = html.unescape((raw or "").strip())
    if not raw:
        return ""
    parsed = urlparse(raw if "://" in raw else SITE + "/" + raw.lstrip("/"))
    if parsed.netloc and parsed.netloc.lower() not in {"golfraw.com", "www.golfraw.com"}:
        return ""
    return SITE + parsed.path if parsed.path.startswith("/public/") else ""


def page_data(source: str, path: Path) -> dict[str, object]:
    parser, documents = parse_page(source)
    record = page_record(path)
    title_match = TITLE_RE.search(source)
    title = clean(title_match.group(1)) if title_match else ""
    h1 = parser.h1 or title.split(" | ", 1)[0]
    if not title or is_stale_scaffold_value(title):
        title = h1

    description = clean((parser.meta.get("description") or [""])[0])
    if not description or is_stale_scaffold_value(description):
        description = clean(parser.standfirst) or clean(record.get("excerpt", ""))

    canonical = clean(parser.canonical)
    if not canonical or canonical == TEMPLATE_URL:
        canonical = SITE + "/" + path.stem

    image = clean((parser.meta.get("og:image") or [""])[0])
    if (
        not image
        or image == SITE + "/public/raw-golf-practice.webp"
        or image == STALE_SCHEMA_IMAGE
    ) and parser.body_images:
        image = local_url(parser.body_images[0][0])
    tags = [tag for tag in parser.tags if tag]
    if not tags:
        keywords = record.get("keywords", "")
        tags = [part.strip() for part in keywords.split(",") if part.strip()]
    section = record.get("section") or record.get("category") or ""
    if not section:
        section = clean((parser.meta.get("article:section") or [""])[0])
    if parser.category and section.casefold() == "tournaments":
        section = clean(parser.category.split("·", 1)[0]).upper()
    author = clean((parser.meta.get("article:author") or parser.meta.get("author") or [""])[0])
    lead_alt = parser.body_images[0][1] if parser.body_images else ""
    published = published_date(source, parser, record)
    modified = clean((parser.meta.get("article:modified_time") or [""])[0])
    if modified == STALE_MODIFIED:
        modified = ""
    if not modified:
        for node in article_nodes(documents):
            candidate = clean(node.get("dateModified", ""))
            if candidate and candidate != STALE_MODIFIED:
                modified = candidate
                break
    robots = clean((parser.meta.get("robots") or [""])[0]) or DEFAULT_ROBOTS
    og_type = clean((parser.meta.get("og:type") or [""])[0]) or "article"

    required = {
        "title": title,
        "description": description,
        "canonical": canonical,
        "image": image,
        "h1": h1,
        "lead_alt": lead_alt,
        "section": section,
        "robots": robots,
        "og_type": og_type,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise ValueError(f"missing page-specific values: {', '.join(missing)}")

    return {
        **required,
        "tags": tags,
        "author": author,
        "published": published,
        "modified": modified,
        "documents": documents,
    }


def escape(value: str) -> str:
    return html.escape(str(value), quote=True)


ARTICLE_META_PROPERTIES = {
    "og:image:alt",
    "article:published_time",
    "article:modified_time",
    "article:author",
    "article:section",
    "article:tag",
}

PRIMARY_META_PROPERTIES = {
    "og:site_name",
    "og:type",
    "og:title",
    "og:description",
    "og:url",
    "og:image",
}

PRIMARY_META_NAMES = {
    "description",
    "robots",
    "twitter:card",
    "twitter:title",
    "twitter:description",
    "twitter:image",
}


def article_meta_block(data: dict[str, object]) -> str:
    tags = "\n".join(
        f'  <meta property="article:tag" content="{escape(tag)}">'
        for tag in data["tags"]
    )
    lines = [
        f'  <meta property="og:image:alt" content="{escape(data["lead_alt"])}">',
        f'  <meta property="article:published_time" content="{escape(data["published"])}">',
    ]
    if data["modified"]:
        lines.append(
            f'  <meta property="article:modified_time" content="{escape(data["modified"])}">'
        )
    if data["author"]:
        lines.append(f'  <meta property="article:author" content="{escape(data["author"])}">')
    lines.append(f'  <meta property="article:section" content="{escape(data["section"])}">')
    if tags:
        lines.append(tags)
    return "\n".join(lines) + "\n"


def primary_meta_block(data: dict[str, object]) -> str:
    return f'''  <!-- SEO audit metadata: managed by scripts/fix_seo_audit.py -->
  <title>{escape(data["title"])}</title>
  <meta name="description" content="{escape(data["description"])}">
  <link rel="canonical" href="{escape(data["canonical"])}">
  <meta name="robots" content="{escape(data["robots"])}">
  <meta property="og:site_name" content="GolfRaw">
  <meta property="og:type" content="{escape(data["og_type"])}">
  <meta property="og:title" content="{escape(data["title"])}">
  <meta property="og:description" content="{escape(data["description"])}">
  <meta property="og:url" content="{escape(data["canonical"])}">
  <meta property="og:image" content="{escape(data["image"])}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{escape(data["title"])}">
  <meta name="twitter:description" content="{escape(data["description"])}">
  <meta name="twitter:image" content="{escape(data["image"])}">
{article_meta_block(data)}'''


def clean_removed_tag_whitespace(head: str) -> str:
    """Remove blank-line indentation left by deleted head tags, not CSS/JS."""
    parts = re.split(
        r"(<(?:style|script)\b[^>]*>.*?</(?:style|script)\s*>)",
        head,
        flags=re.I | re.S,
    )
    for index in range(0, len(parts), 2):
        parts[index] = re.sub(r"(?m)^[ \t]+\r?\n", "\n", parts[index])
        parts[index] = re.sub(r"\n{4,}", "\n\n\n", parts[index])
    return "".join(parts)


def rewrite_head(source: str, data: dict[str, object]) -> str:
    match = HEAD_RE.search(source)
    if not match:
        raise ValueError("missing <head> element")
    head = match.group(2)

    def keep_meta(tag_match: re.Match[str]) -> str:
        tag_attrs = attrs(tag_match.group(0))
        prop = tag_attrs.get("property", "").lower()
        name = tag_attrs.get("name", "").lower()
        managed = prop in PRIMARY_META_PROPERTIES | ARTICLE_META_PROPERTIES
        managed = managed or name in PRIMARY_META_NAMES
        return "" if managed else tag_match.group(0)

    head = MANAGED_COMMENT_RE.sub("", head)

    def keep_head_tag(tag_match: re.Match[str]) -> str:
        tag = tag_match.group(0)
        if tag.lstrip().lower().startswith("<title"):
            return ""
        if tag.lstrip().lower().startswith("<link"):
            return "" if "canonical" in attrs(tag).get("rel", "").lower().split() else tag
        tag_attrs = attrs(tag)
        prop = tag_attrs.get("property", "").lower()
        name = tag_attrs.get("name", "").lower()
        managed = prop in PRIMARY_META_PROPERTIES | ARTICLE_META_PROPERTIES
        managed = managed or name in PRIMARY_META_NAMES
        return "" if managed else tag

    head = HEAD_TAG_LINE_RE.sub(keep_head_tag, head)
    head = TITLE_RE.sub("", head)
    head = LINK_TAG_RE.sub(
        lambda tag_match: ""
        if "canonical" in attrs(tag_match.group(0)).get("rel", "").lower().split()
        else tag_match.group(0),
        head,
    )
    head = META_TAG_RE.sub(keep_meta, head)
    head = clean_removed_tag_whitespace(head)
    block = primary_meta_block(data)

    anchor_end = 0
    for tag_match in META_TAG_RE.finditer(head):
        tag_attrs = attrs(tag_match.group(0))
        if tag_attrs.get("name", "").casefold() == "viewport":
            anchor_end = tag_match.end()
            break
        if "charset" in tag_attrs:
            anchor_end = tag_match.end()
    prefix = head[:anchor_end]
    suffix = head[anchor_end:]
    joined = prefix + "\n\n" + block + suffix

    new_head = match.group(1) + joined + match.group(3)
    return source[: match.start()] + new_head + source[match.end() :]


def update_image(value, image: str):
    if isinstance(value, list):
        return [image]
    if isinstance(value, dict):
        value["url"] = image
        return value
    return image


def update_main_entity(value, canonical: str):
    if isinstance(value, dict):
        value["@id"] = canonical
        value.setdefault("@type", "WebPage")
        return value
    return canonical


def rewrite_json_ld(source: str, data: dict[str, object]) -> str:
    canonical = str(data["canonical"])
    tags = data["tags"]
    replacement_count = 0

    def replace_script(match: re.Match[str]) -> str:
        nonlocal replacement_count
        try:
            document = json.loads(match.group(1))
        except json.JSONDecodeError:
            return match.group(0)

        nodes = article_nodes([document])
        if not nodes:
            return match.group(0)
        for article in nodes:
            article["headline"] = data["h1"]
            article["description"] = data["description"]
            article["image"] = update_image(article.get("image"), str(data["image"]))
            article["datePublished"] = data["published"]
            if data["modified"]:
                article["dateModified"] = data["modified"]
            else:
                article.pop("dateModified", None)
            article["mainEntityOfPage"] = update_main_entity(
                article.get("mainEntityOfPage"), canonical
            )
            article["articleSection"] = data["section"]
            if tags:
                article["keywords"] = ", ".join(str(tag) for tag in tags)
            article["@id"] = canonical.rstrip("/") + "#article"
        replacement_count += 1
        payload = json.dumps(document, ensure_ascii=False, indent=2)
        return match.group(0)[: match.start(1) - match.start()] + payload + match.group(0)[match.end(1) - match.start():]

    rewritten = SCRIPT_RE.sub(replace_script, source)
    if replacement_count == 0:
        raise ValueError("missing Article/NewsArticle JSON-LD")
    return rewritten


def has_template_contamination(source: str) -> bool:
    if any(
        marker in source
        for marker in (
            STALE_HEADLINE,
            STALE_TOP_TITLE,
            STALE_DESCRIPTION_PREFIX,
            STALE_IMAGE_ALT,
            STALE_SCHEMA_IMAGE,
            STALE_PUBLISHED,
            STALE_MODIFIED,
            TEMPLATE_URL,
        )
    ):
        return True

    tag_values = {
        match.group(1)
        for match in re.finditer(
            r'<meta\b[^>]*property=["\']article:tag["\'][^>]*content=["\']([^"\']+)',
            source,
            re.I,
        )
    }
    return STALE_TAGS.issubset(tag_values) and (
        STALE_PUBLISHED in source or STALE_MODIFIED in source
    )


def finalize_html(source: str, output_path: str | Path, force: bool = False) -> str:
    path = Path(output_path)
    if path.name == TEMPLATE_NAME:
        return source
    if not force and not has_template_contamination(source):
        normalized_schema = normalize_article_schema(source, path, prefer_h1=True)
        return normalize_image_markup(normalized_schema, path, ROOT)
    data = page_data(source, path)
    rewritten = rewrite_json_ld(rewrite_head(source, data), data)
    normalized_schema = normalize_article_schema(rewritten, path, prefer_h1=True)
    return normalize_image_markup(normalized_schema, path, ROOT)


def affected_pages() -> list[Path]:
    return [
        path
        for path in sorted(ROOT.rglob("*.html"))
        if path.name != TEMPLATE_NAME
        and not DEPLOY_IGNORED_DIRS.intersection(path.relative_to(ROOT).parts)
        and has_template_contamination(path.read_text(encoding="utf-8"))
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="repair affected pages in place")
    parser.add_argument("--check", action="store_true", help="check affected pages without writing")
    args = parser.parse_args()
    if args.apply and args.check:
        parser.error("choose --apply or --check")
    if not args.apply and not args.check:
        parser.error("choose --apply or --check")

    pages = affected_pages()
    failures = []
    changed = 0
    for path in pages:
        try:
            source = path.read_text(encoding="utf-8")
            repaired = finalize_html(source, path, force=True)
            if args.apply and repaired != source:
                path.write_text(repaired, encoding="utf-8")
                changed += 1
        except Exception as exc:  # report every page so one bad file is visible
            failures.append(f"{path.name}: {exc}")

    if failures:
        for failure in failures:
            print(f"ERROR {failure}", file=sys.stderr)
        return 1

    mode = "repaired" if args.apply else "checked"
    print(f"Template metadata: {mode} {len(pages)} affected page(s); {changed} file(s) changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
