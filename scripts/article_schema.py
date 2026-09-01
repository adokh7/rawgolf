#!/usr/bin/env python3
"""Shared Article/NewsArticle JSON-LD normalization and auditing helpers.

The site has several historical article generators, so this module operates at
the final HTML boundary. It derives schema values from page-owned metadata,
preserves unrelated JSON-LD, and guarantees at most one article entity per
page.
"""

from __future__ import annotations

import html
import json
import re
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.golfraw.com"
ARTICLE_TYPES = {"Article", "NewsArticle"}
EDITORIAL_ID = f"{SITE}/about#editorial"
PUBLISHER_ID = f"{SITE}#organization"
PUBLISHER_URL = f"{SITE}/"
PUBLISHER_LOGO = f"{SITE}/public/favicon-192.webp"
PUBLISHER_LOGO_SIZE = 1254
REQUIRED_FIELDS = (
    "headline",
    "image",
    "datePublished",
    "dateModified",
    "author",
    "publisher",
    "mainEntityOfPage",
)

JSON_LD_RE = re.compile(
    r'(<script\b[^>]*type\s*=\s*["\']application/ld\+json["\'][^>]*>)'
    r'(.*?)'
    r'(</script\s*>)',
    re.IGNORECASE | re.DOTALL,
)
BRAND_SUFFIX_RE = re.compile(r"\s*\|\s*(?:GOLFRAW|GOLF RAW|GOLFRaw|RawGolf)\s*$", re.I)
TOKEN_RE = re.compile(r"[a-z0-9]+", re.I)


def _clean(value: object) -> str:
    return re.sub(r"\s+", " ", html.unescape(str(value or ""))).strip()


def _node_type(node: object) -> set[str]:
    if not isinstance(node, dict):
        return set()
    value = node.get("@type")
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return {item for item in value if isinstance(item, str)}
    return set()


def _is_article(node: object) -> bool:
    return bool(_node_type(node) & ARTICLE_TYPES)


def walk(value: object):
    """Yield nested JSON objects, including the root object."""

    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


class PageParser(HTMLParser):
    """Collect only page metadata needed by the article schema contract."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.meta: dict[str, list[str]] = {}
        self.canonical = ""
        self.title = ""
        self.h1 = ""
        self.json_blocks: list[str] = []
        self.body_images: list[str] = []
        self._capture = ""
        self._buffer: list[str] = []
        self._body_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[no-untyped-def]
        tag = tag.lower()
        attributes = {str(key).lower(): (value or "") for key, value in attrs}
        if tag == "body":
            self._body_depth += 1
        if tag == "meta":
            key = (attributes.get("name") or attributes.get("property") or "").lower()
            if key:
                self.meta.setdefault(key, []).append(attributes.get("content", ""))
        elif tag == "link" and "canonical" in attributes.get("rel", "").lower().split():
            self.canonical = attributes.get("href", "")
        elif tag == "title":
            self._capture = "title"
            self._buffer = []
        elif tag == "h1":
            self._capture = "h1"
            self._buffer = []
        elif tag == "script" and attributes.get("type", "").lower() == "application/ld+json":
            self._capture = "json"
            self._buffer = []
        elif tag == "img" and self._body_depth:
            src = attributes.get("src", "")
            if src:
                self.body_images.append(src)

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "script" and self._capture == "json":
            self.json_blocks.append("".join(self._buffer))
            self._capture = ""
            self._buffer = []
        elif tag == "title" and self._capture == "title":
            self.title = _clean("".join(self._buffer))
            self._capture = ""
            self._buffer = []
        elif tag == "h1" and self._capture == "h1":
            self.h1 = _clean("".join(self._buffer))
            self._capture = ""
            self._buffer = []
        elif tag == "body":
            self._body_depth = max(0, self._body_depth - 1)


def parse_page(source: str) -> tuple[PageParser, list[object], int]:
    parser = PageParser()
    parser.feed(source)
    documents: list[object] = []
    malformed = 0
    for raw in parser.json_blocks:
        try:
            documents.append(json.loads(raw))
        except (TypeError, ValueError):
            malformed += 1
    return parser, documents, malformed


def article_nodes(documents: list[object]) -> list[dict]:
    return [node for document in documents for node in walk(document) if _is_article(node)]


def _registry_for(path: Path) -> dict[str, dict]:
    candidates = [path.parent / "articles.json", ROOT / "articles.json"]
    for candidate in candidates:
        try:
            data = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        return {
            str(record.get("slug", "")): record
            for record in data.get("articles", [])
            if record.get("slug")
        }
    return {}


def _record_for(path: Path) -> dict:
    records = _registry_for(path)
    record = records.get(path.stem, {})
    if record:
        return record
    relative = path.resolve().relative_to(ROOT).with_suffix("") if path.resolve().is_relative_to(ROOT) else None
    route = f"/{relative.as_posix()}" if relative else ""
    return next((item for item in records.values() if item.get("url") == route), {})


def _site_url(raw: object, *, require_public_image: bool = False) -> str:
    value = html.unescape(_clean(raw))
    if not value:
        return ""
    parsed = urlparse(value if "://" in value else urljoin(f"{SITE}/", value))
    if parsed.scheme not in {"http", "https"}:
        return ""
    if parsed.netloc.lower() in {"golfraw.com", "www.golfraw.com"}:
        path = re.sub(r"/+/", "/", parsed.path or "/")
        return f"{SITE}{path}{('?' + parsed.query) if parsed.query else ''}"
    if require_public_image:
        return value
    return value


def _image_url(parser: PageParser, record: dict) -> str:
    # The first body image is the rendered lead/primary image. Prefer it over
    # stale historical OG values so Article.image describes the article the
    # reader actually sees. Query strings are delivery cache keys, not a
    # distinct editorial image URL.
    for body_image in parser.body_images:
        image = _site_url(body_image, require_public_image=True)
        if image:
            parsed = urlparse(image)
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path or '/'}"
    image = _site_url((parser.meta.get("og:image") or [""])[0], require_public_image=True)
    if image:
        parsed = urlparse(image)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path or '/'}"
    image = _site_url(record.get("image", ""), require_public_image=True)
    if image:
        parsed = urlparse(image)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path or '/'}"
    return ""


def _iso(value: object) -> str:
    value = _clean(value)
    if not value:
        return ""
    match = re.match(r"^(\d{4}-\d{2}-\d{2})(?:T|$)", value)
    if not match:
        return ""
    try:
        date.fromisoformat(match.group(1))
    except ValueError:
        return ""
    return value


def _registry_date(value: object) -> str:
    raw = _clean(value)
    if _iso(raw):
        return raw
    for fmt in ("%b %d %Y", "%d %b %Y"):
        try:
            return datetime.strptime(raw.title(), fmt).date().isoformat()
        except ValueError:
            continue
    return ""


def _date_value(parser: PageParser, nodes: list[dict], field: str, record: dict) -> str:
    meta_key = {
        "datePublished": "article:published_time",
        "dateModified": "article:modified_time",
    }[field]
    for value in parser.meta.get(meta_key, []):
        if _iso(value):
            return value
    for node in nodes:
        if _iso(node.get(field)):
            return _clean(node.get(field))
    if field == "datePublished":
        return _registry_date(record.get("date", ""))
    return ""


def _author_name(value: object) -> str:
    if isinstance(value, dict):
        return _clean(value.get("name"))
    return _clean(value)


def _editorial_author() -> dict[str, str]:
    return {
        "@type": "Organization",
        "@id": EDITORIAL_ID,
        "name": "GOLFRAW Editorial",
        "url": f"{SITE}/about",
    }


def _author_value(parser: PageParser, nodes: list[dict]) -> object:
    raw = ""
    for key in ("article:author", "author"):
        raw = _clean((parser.meta.get(key) or [""])[0])
        if raw:
            break

    existing = next((node.get("author") for node in nodes if node.get("author")), None)
    source = raw or existing
    if isinstance(source, dict):
        name = _author_name(source)
        identifier = _clean(source.get("@id"))
        if name.casefold() == "golfraw editorial" or "#editorial" in identifier:
            return _editorial_author()
        if name:
            result = dict(source)
            result.setdefault("@type", "Person")
            return result
        if identifier and "golfraw.com" in identifier:
            return _editorial_author()
        return source
    if not source:
        return ""
    if source.casefold() == "golfraw editorial":
        return _editorial_author()
    if source.casefold() == "marcus keane":
        return {
            "@type": "Person",
            "name": "Marcus Keane",
            "url": f"{SITE}/about",
        }
    return source


def _tokens(value: object) -> set[str]:
    return set(TOKEN_RE.findall(_clean(value).casefold()))


def _similarity(left: object, right: object) -> float:
    a, b = _tokens(left), _tokens(right)
    return len(a & b) / max(1, len(a | b))


def _without_brand(value: object) -> str:
    return BRAND_SUFFIX_RE.sub("", _clean(value))


def _headline(parser: PageParser, nodes: list[dict], record: dict) -> str:
    h1 = parser.h1
    og_title = _without_brand((parser.meta.get("og:title") or [""])[0])
    existing = _clean(nodes[0].get("headline")) if nodes else ""

    # A stale visible H1 can survive a direct-generator rewrite. If the
    # existing schema headline agrees with the page's OG title and the H1 is
    # unrelated, retain the metadata-backed headline without touching body
    # content. Normal pages continue to use their visible H1.
    if existing and og_title and h1:
        h1_score = _similarity(h1, og_title)
        existing_score = _similarity(existing, og_title)
        if h1_score < 0.2 and existing_score > h1_score:
            return existing
    return h1 or existing or og_title or _without_brand(record.get("title", ""))


def _publisher_object() -> dict:
    return {
        "@type": "Organization",
        "@id": PUBLISHER_ID,
        "name": "GOLFRAW",
        "url": PUBLISHER_URL,
        "logo": {
            "@type": "ImageObject",
            "url": PUBLISHER_LOGO,
            "width": PUBLISHER_LOGO_SIZE,
            "height": PUBLISHER_LOGO_SIZE,
        },
    }


def _set_publisher(document: object, article: dict) -> None:
    publisher = _publisher_object()
    if isinstance(document, dict) and isinstance(document.get("@graph"), list):
        organizations = [
            node for node in document["@graph"]
            if isinstance(node, dict)
            and "Organization" in _node_type(node)
            and (
                _clean(node.get("@id")).endswith("#organization")
                or _clean(node.get("name")).casefold() in {"golfraw", "golf raw"}
            )
        ]
        if organizations:
            organizations[0].update(publisher)
        else:
            document["@graph"].append(publisher)
        article["publisher"] = {"@id": PUBLISHER_ID}
    else:
        article["publisher"] = publisher


def _replace_image(existing: object, image: str) -> object:
    if isinstance(existing, dict):
        result = dict(existing)
        result["url"] = image
        if "contentUrl" in result:
            result["contentUrl"] = image
        return result
    if isinstance(existing, list):
        return [image]
    return image


def _normalize_article(
    document: object,
    article: dict,
    parser: PageParser,
    nodes: list[dict],
    record: dict,
) -> None:
    canonical = _site_url(parser.canonical) or _site_url(record.get("url"))
    if not canonical:
        canonical = f"{SITE}/{record.get('slug') or 'article'}"
    image = _image_url(parser, record)
    published = _date_value(parser, nodes, "datePublished", record)
    modified = _date_value(parser, nodes, "dateModified", record)
    author = _author_value(parser, nodes)

    article["headline"] = _headline(parser, nodes, record)
    if image:
        article["image"] = _replace_image(article.get("image"), image)
    else:
        article.pop("image", None)
    if published:
        article["datePublished"] = published
    else:
        article.pop("datePublished", None)
    if modified:
        article["dateModified"] = modified
    else:
        article.pop("dateModified", None)
    if author:
        article["author"] = author
    else:
        article.pop("author", None)
    article["mainEntityOfPage"] = canonical
    article["@id"] = canonical.rstrip("/") + "#article"
    _set_publisher(document, article)


def _transform(value: object, state: dict, parser: PageParser, nodes: list[dict], record: dict) -> object:
    if _is_article(value):
        if state["seen"]:
            return None
        state["seen"] = True
        _normalize_article(state["root"], value, parser, nodes, record)  # type: ignore[arg-type]
        return value
    if isinstance(value, list):
        transformed = []
        for child in value:
            result = _transform(child, state, parser, nodes, record)
            if result is not None:
                transformed.append(result)
        return transformed
    if isinstance(value, dict):
        transformed = {}
        for key, child in value.items():
            result = _transform(child, state, parser, nodes, record)
            if result is not None:
                transformed[key] = result
        if any(_is_article(child) for child in value.values()) and "@context" not in transformed:
            transformed["@context"] = "https://schema.org"
        return transformed
    return value


def normalize_article_schema(source: str, path: str | Path) -> str:
    """Normalize the page's article JSON-LD and preserve unrelated scripts.

    Pages without Article/NewsArticle JSON-LD are returned unchanged so the
    helper can safely run over the complete static output tree.
    """

    page_path = Path(path)
    parser, documents, malformed = parse_page(source)
    if malformed:
        raise ValueError(f"cannot normalize malformed JSON-LD ({malformed} block(s))")
    nodes = article_nodes(documents)
    if not nodes:
        return source
    record = _record_for(page_path)
    state = {"seen": False, "root": None}
    document_index = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal document_index
        raw = match.group(2)
        try:
            document = json.loads(raw)
        except (TypeError, ValueError):
            return match.group(0)
        if not any(_is_article(node) for node in walk(document)):
            return match.group(0)
        state["root"] = document
        transformed = _transform(document, state, parser, nodes, record)
        document_index += 1
        if transformed is None:
            return ""
        payload = json.dumps(transformed, ensure_ascii=False, indent=2)
        return match.group(1) + "\n" + payload + "\n" + match.group(3)

    normalized = JSON_LD_RE.sub(replace, source)
    if not state["seen"]:
        raise ValueError("Article/NewsArticle nodes disappeared during normalization")
    return normalized


def _schema_image_values(value: object) -> list[str]:
    if isinstance(value, str):
        return [_site_url(value, require_public_image=True)] if value else []
    if isinstance(value, list):
        return [item for child in value for item in _schema_image_values(child)]
    if isinstance(value, dict):
        return _schema_image_values(value.get("url") or value.get("contentUrl"))
    return []


def _main_entity_url(value: object) -> str:
    if isinstance(value, str):
        return _site_url(value)
    if isinstance(value, dict):
        return _site_url(value.get("@id"))
    return ""


def audit_article_schema(source: str, path: str | Path) -> dict:
    """Return machine-readable schema findings for one HTML page."""

    parser, documents, malformed = parse_page(source)
    nodes = article_nodes(documents)
    record = _record_for(Path(path))
    canonical = _site_url(parser.canonical) or _site_url(record.get("url"))
    og_image = _image_url(parser, record)
    missing_fields = {field: 0 for field in REQUIRED_FIELDS}
    mismatches = {"mainEntityOfPage": 0, "image": 0}
    unresolved: list[str] = []
    for node in nodes:
        for field in REQUIRED_FIELDS:
            if field not in node or node.get(field) in (None, "", [], {}):
                missing_fields[field] += 1
        if canonical and _main_entity_url(node.get("mainEntityOfPage")) != canonical:
            mismatches["mainEntityOfPage"] += 1
        schema_images = set(_schema_image_values(node.get("image")))
        if og_image and og_image not in schema_images:
            mismatches["image"] += 1
    if missing_fields["author"] and not _author_value(parser, nodes):
        unresolved.append("author")
    if missing_fields["dateModified"] and not _date_value(parser, nodes, "dateModified", record):
        unresolved.append("dateModified")
    missing = [field for field, count in missing_fields.items() if count]
    return {
        "path": str(path),
        "article_count": len(nodes),
        "duplicate": max(0, len(nodes) - 1),
        "malformed": malformed,
        "missing": missing,
        "missing_fields": missing_fields,
        "mismatches": mismatches,
        "unresolved": unresolved,
        "canonical": canonical,
    }


def has_article_schema(source: str) -> bool:
    _, documents, _ = parse_page(source)
    return bool(article_nodes(documents))


def normalize_paths(paths: list[Path], apply: bool = False) -> tuple[int, int, list[dict]]:
    """Normalize or check explicit paths; return changed count, article count, findings."""

    changed = 0
    article_pages = 0
    findings = []
    for path in sorted(paths):
        source = path.read_text(encoding="utf-8")
        if not has_article_schema(source):
            continue
        article_pages += 1
        try:
            normalized = normalize_article_schema(source, path)
        except ValueError as exc:
            findings.append({"path": str(path), "error": str(exc)})
            continue
        if apply and normalized != source:
            path.write_text(normalized, encoding="utf-8")
            changed += 1
        findings.append(audit_article_schema(normalized if apply else source, path))
    return changed, article_pages, findings
