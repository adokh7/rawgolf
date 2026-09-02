#!/usr/bin/env python3
"""Repair and validate SEO metadata on every root-level HTML page.

Usage:
    python3 scripts/fix_seo_audit.py
    python3 scripts/fix_seo_audit.py --check

The default command updates files in place and then validates the result.
``--check`` is read-only and exits non-zero if any managed field has drifted.
The script is intentionally standard-library only so it can also run in CI.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urlparse

try:
    from fix_template_metadata import finalize_html, has_template_contamination
    from seo_metadata import apply_metadata_overrides, metadata_override_for
except ModuleNotFoundError:  # imported as scripts.fix_seo_audit
    from scripts.fix_template_metadata import finalize_html, has_template_contamination
    from scripts.seo_metadata import apply_metadata_overrides, metadata_override_for


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.golfraw.com"
BRAND_SUFFIX = " | GOLFRAW"
ROBOTS_VALUE = "index, follow, max-image-preview:large"

# Pages that must stay out of the index. Internal search results are thin
# and near-duplicate by nature, and Google's own guidance is to keep them
# out; "follow" is retained so link equity still flows through them.
NOINDEX_ROBOTS_VALUE = "noindex, follow"
NOINDEX_PAGES = {"search.html"}


def robots_for(name: str) -> str:
    """Robots directive for a page, honouring the noindex exceptions."""
    return NOINDEX_ROBOTS_VALUE if name in NOINDEX_PAGES else ROBOTS_VALUE
DEFAULT_IMAGE = "/public/raw-golf-practice.webp"

OG_PROPERTIES = {
    "og:site_name",
    "og:type",
    "og:title",
    "og:description",
    "og:url",
    "og:image",
}
TWITTER_NAMES = {
    "twitter:card",
    "twitter:title",
    "twitter:description",
    "twitter:image",
}
MANAGED_NAMES = {"description", "robots"} | TWITTER_NAMES

# Home, section, archive, utility and policy pages represent a website rather
# than a single editorial story. Everything else defaults to an article.
WEBSITE_PAGES = {
    "index.html",
    "about.html",
    "analysis.html",
    "contact.html",
    "corrections.html",
    "full-board.html",
    "guides.html",
    "liv-golf.html",
    "manifesto.html",
    "news.html",
    "past-issues.html",
    "pga-tour.html",
    "privacy.html",
    "ratings-manual.html",
    "ratings.html",
    "in-memoriam.html",
    "search.html",
    "terms.html",
    "the-card.html",
    "tools.html",
    "tournaments.html",
    "vault.html",
}

# These existing titles are too short even after the brand suffix. Explicit
# rewrites are clearer than padding them with generic words.
SHORT_TITLE_OVERRIDES = {
    "full-board.html": "Full Golf Player Ratings & Rankings",
    "guides.html": "Golf Guides, Tips & Practical Advice",
    "index.html": "Golf News, Course Guides & PGA Tour Analysis",
    "liv-golf.html": "LIV Golf News, Results & Analysis",
    "search.html": "Search Golf News, Guides & Analysis",
    "what-does-lpga-stand-for.html": "What Does LPGA Stand For? Meaning Explained",
}

ATTR_RE = re.compile(
    r"([:\w-]+)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+))",
    re.S,
)
HEAD_RE = re.compile(r"(<head\b[^>]*>)(.*?)(</head\s*>)", re.I | re.S)
TITLE_RE = re.compile(r"<title\b[^>]*>.*?</title\s*>", re.I | re.S)
META_RE = re.compile(r"<meta\b[^>]*>", re.I | re.S)
LINK_RE = re.compile(r"<link\b[^>]*>", re.I | re.S)
MANAGED_COMMENT_RE = re.compile(
    r"\s*<!-- SEO audit metadata: managed by scripts/fix_seo_audit\.py -->\s*",
    re.I,
)


def clean_text(value: str) -> str:
    """Decode entities, strip embedded markup and collapse whitespace."""
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def attributes(tag: str) -> dict[str, str]:
    """Return lower-cased attributes from a single HTML tag."""
    result: dict[str, str] = {}
    for match in ATTR_RE.finditer(tag):
        value = next(group for group in match.groups()[1:] if group is not None)
        result[match.group(1).lower()] = html.unescape(value)
    return result


class PageParser(HTMLParser):
    """Collect SEO fields and useful visible copy without rewriting the DOM."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.titles: list[str] = []
        self.meta: dict[str, list[str]] = {}
        self.canonicals: list[str] = []
        self.h1 = ""
        self.standfirst = ""
        self.article_paragraph = ""
        self.body_paragraph = ""
        self.body_images: list[str] = []
        self._buffers: dict[str, list[str]] = {}
        self._stack: list[dict[str, object]] = []
        self._in_head = 0
        self._in_body = 0
        self._in_article = 0
        self._in_article_body = 0

    def _capture(self, key: str) -> bool:
        return key not in self._buffers and not getattr(self, key, "")

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[no-untyped-def]
        tag = tag.lower()
        attr = {str(k).lower(): (v or "") for k, v in attrs}

        if tag == "head":
            self._in_head += 1
        if tag == "body":
            self._in_body += 1

        classes = set(attr.get("class", "").split())
        enters_article = tag == "article"
        enters_article_body = "article-body" in classes
        if enters_article:
            self._in_article += 1
        if enters_article_body:
            self._in_article_body += 1

        capture = ""
        if tag == "title":
            capture = f"title_{len(self.titles)}"
            self._buffers[capture] = []
        elif tag == "h1" and self._capture("h1"):
            capture = "h1"
            self._buffers[capture] = []
        elif "standfirst" in classes and self._capture("standfirst"):
            capture = "standfirst"
            self._buffers[capture] = []
        elif tag == "p" and self._in_body:
            if (self._in_article_body or self._in_article) and self._capture("article_paragraph"):
                capture = "article_paragraph"
                self._buffers[capture] = []
            elif self._capture("body_paragraph"):
                capture = "body_paragraph"
                self._buffers[capture] = []

        if tag == "meta":
            key = (attr.get("name") or attr.get("property") or "").lower()
            if key:
                self.meta.setdefault(key, []).append(attr.get("content", ""))
        elif tag == "link":
            rels = {part.lower() for part in attr.get("rel", "").split()}
            if "canonical" in rels:
                self.canonicals.append(attr.get("href", ""))
        elif tag == "img" and self._in_body and attr.get("src"):
            self.body_images.append(attr["src"])

        # Void elements never receive a matching end tag.
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}:
            self._stack.append(
                {
                    "tag": tag,
                    "capture": capture,
                    "article": enters_article,
                    "article_body": enters_article_body,
                }
            )

    def handle_startendtag(self, tag: str, attrs) -> None:  # type: ignore[no-untyped-def]
        self.handle_starttag(tag, attrs)

    def handle_data(self, data: str) -> None:
        for frame in self._stack:
            capture = str(frame.get("capture") or "")
            if capture:
                self._buffers[capture].append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        index = next(
            (i for i in range(len(self._stack) - 1, -1, -1) if self._stack[i]["tag"] == tag),
            None,
        )
        if index is not None:
            closing = self._stack[index:]
            self._stack = self._stack[:index]
            for frame in reversed(closing):
                capture = str(frame.get("capture") or "")
                if capture:
                    value = clean_text(" ".join(self._buffers.pop(capture, [])))
                    if capture.startswith("title_"):
                        self.titles.append(value)
                    else:
                        setattr(self, capture, value)
                if frame.get("article"):
                    self._in_article = max(0, self._in_article - 1)
                if frame.get("article_body"):
                    self._in_article_body = max(0, self._in_article_body - 1)
        if tag == "head":
            self._in_head = max(0, self._in_head - 1)
        if tag == "body":
            self._in_body = max(0, self._in_body - 1)


def parse_page(source: str) -> PageParser:
    parser = PageParser()
    parser.feed(source)
    parser.close()
    return parser


# Words that must never end a title. Cutting at a word boundary is not enough:
# "…tour cards, down from" and "…The PGA claim is" are both valid word
# boundaries and both read as broken.
DANGLING_WORDS = {
    "a", "an", "and", "as", "at", "but", "by", "down", "for", "from", "in",
    "into", "is", "it", "its", "of", "on", "or", "the", "their", "this",
    "to", "up", "was", "were", "who", "with", "his", "her", "that", "than",
}


def _strip_dangling(value: str) -> str:
    """Drop trailing filler words, bare numbers and punctuation from a cut title."""
    prev = None
    while value and value != prev:
        prev = value
        value = value.rstrip(" |—–-:;,.")
        if " " not in value:
            break
        head, last = value.rsplit(" ", 1)
        drop = last.casefold() in DANGLING_WORDS
        # A bare number is only a fragment when it trails a list ("entrants, 34").
        # In "Round 1" or "Top 30" it belongs to the phrase.
        if last.isdigit() and head.rstrip().endswith(","):
            drop = True
        if not drop:
            break
        value = head
    return value


def truncate_words(value: str, limit: int) -> str:
    value = clean_text(value).strip(" |—–-:;,.")
    if len(value) <= limit:
        return value

    # A clause boundary reads far better than a mid-phrase cut, so prefer the
    # longest comma/colon/dash clause that still fits.
    best = ""
    for match in re.finditer(r"[,:;—–]", value):
        clause = value[: match.start()].strip(" |—–-:;,.")
        if len(clause) <= limit and len(clause) > len(best):
            best = clause
    if len(best) >= 30:
        return best

    shortened = _strip_dangling(value[: limit + 1].rsplit(" ", 1)[0])
    # A short trailing word is usually half of a phrase the cut split ("… tee"
    # from "tee times"). Drop it when there is room to spare.
    if " " in shortened:
        head, last = shortened.rsplit(" ", 1)
        if len(last) <= 4 and len(_strip_dangling(head)) >= 30:
            shortened = _strip_dangling(head)
    if len(shortened) >= 30:
        return shortened
    return shortened or value[:limit].rstrip(" |—–-:;,.")


def strip_decoration(value: str) -> str:
    """Remove eyebrow decoration that belongs in an H1 but not in a <title>.

    Headings here open with things like "⛳ LPGA PREVIEW:" or "· GOLF MAGIC:".
    Carried into a title they waste characters the truncator then reclaims from
    the actual headline.
    """
    value = clean_text(value)
    # leading emoji, bullets, dashes and other non-word decoration
    value = re.sub(r"^[^\w(\[]+", "", value).strip()
    # a leading SHOUTED LABEL: prefix
    value = re.sub(r"^[A-Z0-9][A-Z0-9 &''’.-]{2,28}:\s*", "", value).strip()
    return value


def title_core(value: str) -> str:
    value = strip_decoration(value)
    value = re.sub(r"\s*(?:\||—|–|-)\s*(?:GOLFRAW|GolfRaw|Rawgolf)\s*$", "", value, flags=re.I)
    value = re.sub(r"\s*(?:—|–|-)\s*Raw Take\s*$", "", value, flags=re.I)
    return value.strip(" |—–-")


def sanitize_title(path: Path, parsed: PageParser) -> str:
    existing = parsed.titles[0] if parsed.titles else ""
    core = SHORT_TITLE_OVERRIDES.get(path.name) or title_core(existing)
    heading = title_core(strip_decoration(parsed.h1))

    if not core:
        core = heading or path.stem.replace("-", " ").title()
    if len(core) < 30 and 30 <= len(heading) <= 50:
        core = heading

    # An earlier version of this script truncated mid-phrase and wrote the result
    # back, so the stored <title> is often a fragment of the real headline. The
    # H1 is intact, so prefer it whenever it carries more of the headline than
    # the stored title does. Without this the script keeps re-truncating its own
    # output and pads the remains with " Explained".
    if heading and len(heading) > len(core):
        core = heading

    max_core = 60 - len(BRAND_SUFFIX)
    if len(core) > max_core:
        # A complete first clause is usually stronger than a mechanical cut.
        first_clause = re.split(r"\s*(?::|—|–|\|)\s*", core, maxsplit=1)[0].strip()
        if 30 <= len(first_clause) <= max_core:
            core = first_clause
        else:
            core = truncate_words(core, max_core)

    if len(core) < 30:
        addon = " Meaning Explained" if core.endswith("?") else " Explained"
        if len(core) + len(addon) <= max_core:
            core += addon
    if len(core) < 30 and len(core) + len(" Golf Guide") <= max_core:
        core += " Golf Guide"

    core = truncate_words(core, max_core)
    title = core + BRAND_SUFFIX
    # A pathological one-word source can still be short; add a useful label.
    if len(title) < 40:
        core = truncate_words(core + " Golf News & Analysis", max_core)
        title = core + BRAND_SUFFIX
    return title


def finish_description(value: str, limit: int = 155) -> str:
    """Return natural, word-safe copy no longer than limit, ending in a period."""
    value = clean_text(value).strip()
    if not value:
        return value
    # A word-boundary cut can otherwise leave copy ending in "with." or
    # "within.". Remove dangling connector words before final punctuation.
    dangling = {
        "a", "an", "and", "as", "at", "by", "for", "from", "in", "into",
        "of", "on", "or", "the", "to", "with", "within", "without",
    }
    terminal = value[-1] if value[-1] in ".!?" else ""
    words = value.rstrip(".!?").split()
    while len(words) > 1 and words[-1].strip("'\"()[]{}:,;").casefold() in dangling:
        words.pop()
    value = " ".join(words) + terminal
    if len(value) < limit and value[-1] not in ".!?":
        value += "."
    if len(value) <= limit:
        return value

    body_limit = limit - 1
    window = value[: body_limit + 1]
    sentence_ends = [m.end() for m in re.finditer(r"[.!?](?=\s|$)", window)]
    viable = [end for end in sentence_ends if end >= 120]
    if viable:
        cut = window[: viable[-1]].rstrip(".!?")
    else:
        cut = window.rsplit(" ", 1)[0].rstrip(" ,;:—–-.!?")
    return cut + "."


def description_for(title: str, parsed: PageParser) -> str:
    existing = clean_text((parsed.meta.get("description") or [""])[0])
    if len(existing) >= 120:
        return finish_description(existing)

    standfirst = clean_text(parsed.standfirst)
    article_p = clean_text(parsed.article_paragraph)
    body_p = clean_text(parsed.body_paragraph)

    # Prefer one coherent passage when it already meets the target length.
    for candidate in (standfirst, article_p, body_p):
        if len(candidate) >= 120:
            return finish_description(candidate)

    pieces: list[str] = []
    for candidate in (existing, standfirst, article_p, body_p):
        if len(candidate) < 20:
            continue
        lowered = candidate.casefold()
        if any(lowered in piece.casefold() or piece.casefold() in lowered for piece in pieces):
            if pieces and len(candidate) > len(pieces[-1]):
                pieces[-1] = candidate
            continue
        pieces.append(candidate)
        if len(" ".join(pieces)) >= 120:
            break

    core = title_core(title)
    fallback = (
        f"Explore {core} with GolfRaw's evidence-led reporting, practical context "
        "and independent analysis for golfers and fans."
    )
    combined = " ".join(pieces)
    if len(combined) < 120:
        combined = (combined + " " + fallback).strip()
    if len(combined) < 120:
        combined += " Get the facts, context and useful takeaways in one clear guide."
    return finish_description(combined)


def canonical_for(path: Path, parsed: PageParser) -> str:
    existing = clean_text(parsed.canonicals[0]) if parsed.canonicals else ""
    if existing:
        parsed_url = urlparse(existing if "://" in existing else SITE + "/" + existing.lstrip("/"))
        clean_path = parsed_url.path or "/"
    else:
        clean_path = "/" if path.name == "index.html" else "/" + path.stem
    if clean_path != "/":
        clean_path = clean_path.rstrip("/")
    return SITE + clean_path


def local_image_url(raw: str) -> str:
    raw = html.unescape((raw or "").strip())
    if not raw or raw.startswith("data:"):
        return ""
    parsed = urlparse(raw if "://" in raw else SITE + "/" + raw.lstrip("/"))
    if parsed.netloc and parsed.netloc.lower() not in {"golfraw.com", "www.golfraw.com"}:
        return ""
    image_path = parsed.path
    if not image_path.startswith("/public/"):
        return ""
    disk_path = ROOT / image_path.lstrip("/")
    if not disk_path.is_file():
        return ""
    return SITE + quote(image_path, safe="/%:@-._~!$&'()*+,;=")


def image_for(parsed: PageParser) -> str:
    previous_fallbacks = {
        "/public/favicon-192.webp",
        SITE + "/public/favicon-192.webp",
    }
    candidates = (
        [value for value in (parsed.meta.get("og:image") or []) if value not in previous_fallbacks]
        + [value for value in (parsed.meta.get("twitter:image") or []) if value not in previous_fallbacks]
        + parsed.body_images
        + [DEFAULT_IMAGE]
    )
    for candidate in candidates:
        url = local_image_url(candidate)
        if url:
            return url
    raise RuntimeError(f"Default social image is missing: {ROOT / DEFAULT_IMAGE.lstrip('/')}")


def page_type(path: Path) -> str:
    if path.name in WEBSITE_PAGES or path.name.startswith("tools-"):
        return "website"
    return "article"


def is_managed_meta(tag: str) -> bool:
    attr = attributes(tag)
    name = attr.get("name", "").lower()
    prop = attr.get("property", "").lower()
    return name in MANAGED_NAMES or prop in OG_PROPERTIES


def is_canonical_link(tag: str) -> bool:
    rel = attributes(tag).get("rel", "")
    return "canonical" in {part.lower() for part in rel.split()}


def escaped(value: str) -> str:
    return html.escape(value, quote=True)


def metadata_block(
    title: str,
    description: str,
    canonical: str,
    og_type: str,
    image: str,
    robots_value: str = ROBOTS_VALUE,
) -> str:
    return f'''  <!-- SEO audit metadata: managed by scripts/fix_seo_audit.py -->
  <title>{escaped(title)}</title>
  <meta name="description" content="{escaped(description)}">
  <link rel="canonical" href="{escaped(canonical)}">
  <meta name="robots" content="{robots_value}">
  <meta property="og:site_name" content="GolfRaw">
  <meta property="og:type" content="{og_type}">
  <meta property="og:title" content="{escaped(title)}">
  <meta property="og:description" content="{escaped(description)}">
  <meta property="og:url" content="{escaped(canonical)}">
  <meta property="og:image" content="{escaped(image)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{escaped(title)}">
  <meta name="twitter:description" content="{escaped(description)}">
  <meta name="twitter:image" content="{escaped(image)}">'''


def repair_source(path: Path, source: str) -> tuple[str, dict[str, str]]:
    parsed = parse_page(source)
    title = sanitize_title(path, parsed)
    description = description_for(title, parsed)
    override = metadata_override_for(path)
    title = override.get("title", title)
    description = override.get("description", description)
    canonical = canonical_for(path, parsed)
    image = image_for(parsed)
    og_type = page_type(path)

    match = HEAD_RE.search(source)
    if not match:
        raise ValueError("missing <head> element")

    head = match.group(2)
    head = MANAGED_COMMENT_RE.sub("\n", head)
    head = TITLE_RE.sub("", head)
    head = META_RE.sub(lambda m: "" if is_managed_meta(m.group(0)) else m.group(0), head)
    head = LINK_RE.sub(lambda m: "" if is_canonical_link(m.group(0)) else m.group(0), head)
    head = re.sub(r"[ \t]+\n", "\n", head)
    head = re.sub(r"\n{4,}", "\n\n\n", head).rstrip()
    block = metadata_block(title, description, canonical, og_type, image, robots_for(path.name))

    # Keep discovery metadata near the top of <head>, after the viewport (or
    # charset fallback), rather than below large inline stylesheets.
    anchor_end = 0
    for meta_match in META_RE.finditer(head):
        attr = attributes(meta_match.group(0))
        if attr.get("name", "").casefold() == "viewport":
            anchor_end = meta_match.end()
            break
        if "charset" in attr:
            anchor_end = meta_match.end()
    prefix = head[:anchor_end].rstrip()
    suffix = head[anchor_end:].lstrip("\n")
    joined = prefix + "\n\n" + block + "\n" + suffix
    new_head = match.group(1) + joined.rstrip() + "\n" + match.group(3)
    repaired = source[: match.start()] + new_head + source[match.end() :]
    return repaired, {
        "title": title,
        "description": description,
        "canonical": canonical,
        "image": image,
        "type": og_type,
    }


def one(values: list[str], label: str, errors: list[str]) -> str:
    if len(values) != 1:
        errors.append(f"{label} count is {len(values)}, expected 1")
    return clean_text(values[0]) if values else ""


def validate_page(path: Path, source: str) -> list[str]:
    parsed = parse_page(source)
    errors: list[str] = []
    title = one(parsed.titles, "title", errors)
    description = one(parsed.meta.get("description", []), "description", errors)
    canonical = one(parsed.canonicals, "canonical", errors)
    robots = one(parsed.meta.get("robots", []), "robots", errors)
    site_name = one(parsed.meta.get("og:site_name", []), "og:site_name", errors)
    og_type = one(parsed.meta.get("og:type", []), "og:type", errors)
    og_title = one(parsed.meta.get("og:title", []), "og:title", errors)
    og_description = one(parsed.meta.get("og:description", []), "og:description", errors)
    og_url = one(parsed.meta.get("og:url", []), "og:url", errors)
    og_image = one(parsed.meta.get("og:image", []), "og:image", errors)
    twitter_card = one(parsed.meta.get("twitter:card", []), "twitter:card", errors)
    twitter_title = one(parsed.meta.get("twitter:title", []), "twitter:title", errors)
    twitter_description = one(parsed.meta.get("twitter:description", []), "twitter:description", errors)
    twitter_image = one(parsed.meta.get("twitter:image", []), "twitter:image", errors)

    if not 40 <= len(title) <= 60:
        errors.append(f"title length is {len(title)}, expected 40-60")
    if not 120 <= len(description) <= 155:
        errors.append(f"description length is {len(description)}, expected 120-155")
    expected_robots = robots_for(path.name)
    if robots.casefold() != expected_robots.casefold():
        errors.append(f"robots is {robots!r}, expected {expected_robots!r}")
    if path.name not in NOINDEX_PAGES and (
        "noindex" in robots.casefold() or "nofollow" in robots.casefold()
    ):
        errors.append("robots still blocks indexing or following")
    if not canonical.startswith(SITE + "/"):
        errors.append(f"canonical is outside {SITE}: {canonical!r}")
    if site_name != "GolfRaw":
        errors.append(f"og:site_name is {site_name!r}")
    if og_type != page_type(path):
        errors.append(f"og:type is {og_type!r}, expected {page_type(path)!r}")
    if og_title != title or twitter_title != title:
        errors.append("social title does not match <title>")
    if og_description != description or twitter_description != description:
        errors.append("social description does not match meta description")
    if og_url != canonical:
        errors.append("og:url does not exactly match canonical")
    if twitter_card != "summary_large_image":
        errors.append(f"twitter:card is {twitter_card!r}")
    if twitter_image != og_image:
        errors.append("twitter:image does not match og:image")
    if not local_image_url(og_image):
        errors.append(f"og:image is not a live local /public asset: {og_image!r}")
    if path.name != "article-template.html" and has_template_contamination(source):
        errors.append("template-derived Oakmont metadata remains in production HTML")
    return errors


def main() -> int:
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--check", action="store_true", help="validate without writing files")
    args.add_argument(
        "--only-overrides",
        action="store_true",
        help="process only pages with an explicit reviewed metadata override",
    )
    options = args.parse_args()

    pages = sorted(ROOT.glob("*.html"))
    if options.only_overrides:
        pages = [path for path in pages if metadata_override_for(path)]
    if not pages:
        print("ERROR: no root-level HTML pages found", file=sys.stderr)
        return 1

    changed = 0
    failures: list[tuple[Path, str]] = []
    if not options.check:
        for path in pages:
            try:
                source = path.read_text(encoding="utf-8")
                repaired, _ = repair_source(path, source)
                if path.name != "article-template.html":
                    repaired = finalize_html(repaired, path)
                if repaired != source:
                    path.write_text(repaired, encoding="utf-8")
                    changed += 1
            except Exception as exc:  # report all files instead of stopping at one
                failures.append((path, str(exc)))

    validation_failures: list[tuple[Path, str]] = []
    for path in pages:
        try:
            for error in validate_page(path, path.read_text(encoding="utf-8")):
                validation_failures.append((path, error))
        except Exception as exc:
            validation_failures.append((path, f"validation failed: {exc}"))

    mode = "checked" if options.check else "processed"
    print(f"SEO audit: {mode} {len(pages)} HTML pages; {changed} file(s) changed")
    for path, error in failures + validation_failures:
        print(f"  ERROR {path.name}: {error}")
    if failures or validation_failures:
        print(f"SEO audit: FAILED with {len(failures) + len(validation_failures)} issue(s)")
        return 1
    print("SEO audit: PASS — titles, descriptions, indexability and social tags are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
