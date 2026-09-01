"""Shared replacements for scaffold-based article pages."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

try:
    from scripts.image_markup import ROOT, normalize_image_markup
    from scripts.article_schema import normalize_article_schema
except ImportError:  # direct execution from the scripts directory
    from image_markup import ROOT, normalize_image_markup
    from article_schema import normalize_article_schema


H1_RE = re.compile(r"<h1(?:\s+[^>]*)?>.*?</h1>", re.IGNORECASE | re.DOTALL)
STANDFIRST_RE = re.compile(
    r'<p\s+class=["\']standfirst["\'][^>]*>.*?</p>',
    re.IGNORECASE | re.DOTALL,
)
JSON_LD_RE = re.compile(
    r'<script\s+type=["\']application/ld\+json["\']\s*>(.*?)</script\s*>',
    re.IGNORECASE | re.DOTALL,
)
LEAD_IMAGE_RE = re.compile(
    r'<figure\s+class=["\']lead-img["\'][^>]*>.*?'
    r'<img\b[^>]*\balt=["\']([^"\']+)["\']',
    re.IGNORECASE | re.DOTALL,
)


def _walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _article_schema(source: str) -> dict:
    for block in JSON_LD_RE.findall(source):
        try:
            document = json.loads(block)
        except json.JSONDecodeError:
            continue
        for node in _walk(document):
            if node.get("@type") in {"Article", "NewsArticle"}:
                return node
    raise ValueError("expected one Article/NewsArticle JSON-LD node")


def _replace_single_meta(source: str, property_name: str, value: str) -> str:
    pattern = re.compile(
        rf'(<meta\s+property=["\']{re.escape(property_name)}["\']\s+'
        r'content=["\'])[^"\']*(["\'])',
        re.IGNORECASE,
    )
    updated, count = pattern.subn(rf'\g<1>{html.escape(value, quote=True)}\g<2>', source, count=1)
    if count != 1:
        raise ValueError(f"expected one {property_name} meta tag, found {count}")
    return updated


def _remove_meta(source: str, property_name: str) -> str:
    pattern = re.compile(
        rf'(?m)^[ \t]*<meta\s+property=["\']{re.escape(property_name)}["\'][^>]*>'
        r'[ \t]*(?:\r?\n|$)',
        re.IGNORECASE,
    )
    return pattern.sub("", source)


def replace_article_header(source: str, headline: str, standfirst: str) -> str:
    """Replace the scaffold's visible H1 and standfirst, failing if either is absent."""

    updated, h1_count = H1_RE.subn(
        f"<h1>{html.escape(headline)}</h1>",
        source,
        count=1,
    )
    if h1_count != 1:
        raise ValueError(f"expected one article h1, found {h1_count}")

    updated, standfirst_count = STANDFIRST_RE.subn(
        f'<p class="standfirst">{html.escape(standfirst)}</p>',
        updated,
        count=1,
    )
    if standfirst_count != 1:
        raise ValueError(f"expected one article standfirst, found {standfirst_count}")

    return updated


def finalize_article_template_metadata(
    source: str, output_path: str | Path = "article.html"
) -> str:
    """Replace scaffold-only head fields from the generated hero and schema.

    The article generators already write page-specific title, description,
    canonical, image, and JSON-LD. This final pass prevents less-visible
    scaffold fields from surviving into production and fails loudly if the
    generated structure changes.
    """

    article = _article_schema(source)
    lead_match = LEAD_IMAGE_RE.search(source)
    if not lead_match:
        raise ValueError("expected article lead image with alt text")

    source = _replace_single_meta(source, "og:image:alt", html.unescape(lead_match.group(1)))
    source = _replace_single_meta(
        source,
        "article:published_time",
        str(article.get("datePublished", "")),
    )
    modified = str(article.get("dateModified", ""))
    if modified:
        source = _replace_single_meta(source, "article:modified_time", modified)
    else:
        source = _remove_meta(source, "article:modified_time")
    source = _replace_single_meta(
        source,
        "article:section",
        str(article.get("articleSection", "")),
    )

    keywords = article.get("keywords", "")
    tags = [part.strip() for part in str(keywords).split(",") if part.strip()]
    if not tags:
        raise ValueError("Article/NewsArticle JSON-LD has no keywords for article tags")
    tag_pattern = re.compile(
        r'(?m)^[ \t]*<meta\s+property=["\']article:tag["\']\s+'
        r'content=["\'][^"\']*["\']\s*/?>[ \t]*(?:\r?\n|$)',
        re.IGNORECASE,
    )
    source, count = tag_pattern.subn("", source)
    if count == 0:
        raise ValueError("expected scaffold article:tag meta tags")
    tag_block = "".join(
        f'  <meta property="article:tag" content="{html.escape(tag, quote=True)}">\n'
        for tag in tags
    )
    marker = '  <meta property="article:section"'
    marker_index = source.find(marker)
    if marker_index < 0:
        raise ValueError("expected article:section meta tag")
    line_end = source.find("\n", marker_index)
    if line_end < 0:
        raise ValueError("article:section meta tag has no line ending")
    normalized = source[: line_end + 1] + tag_block + source[line_end + 1 :]
    normalized_schema = normalize_article_schema(normalized, Path(output_path))
    return normalize_image_markup(normalized_schema, Path(output_path), ROOT)
