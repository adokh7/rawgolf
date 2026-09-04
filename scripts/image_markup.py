"""Build-time helpers for stable, responsive local raster image markup.

The site is deployed as static HTML.  This module deliberately works on the
HTML source without serialising the document, so normalising image attributes
cannot rewrite article copy, JSON-LD, or the surrounding design.
"""

from __future__ import annotations

import html
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit, urlunsplit

try:
    from PIL import Image
except ImportError:  # pragma: no cover - the build environment supplies Pillow
    Image = None


ROOT = Path(__file__).resolve().parents[1]
RASTER_EXTENSIONS = {".avif", ".jpeg", ".jpg", ".png", ".webp"}
CARD_SIZES = "(max-width: 700px) 92vw, 360px"
ARTICLE_SIZES = "(max-width: 700px) 100vw, 740px"
BRAND_SIZES = "(max-width: 768px) 260px, 300px"
VARIANT_WIDTHS = (400, 800, 1200)

DEPLOY_IGNORED_DIRS = {
    ".agents",
    ".gemini",
    ".github",
    ".git",
    ".system_generated",
    ".vercel",
    "__pycache__",
    "node_modules",
    "out",
    "public",
    "skills",
    ".email-preview",
    "golfraw.com-audit",
}
NON_PRODUCTION_HTML = {"404.html", "article-template.html"}

ATTR_RE = re.compile(
    r"([:\w-]+)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+))", re.S
)
ATTR_REMOVE_RE = re.compile(
    r"\s+([:\w-]+)(?:\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+))?",
    re.S,
)


def _parse_attrs(tag: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for match in ATTR_RE.finditer(tag):
        value = next(group for group in match.groups()[1:] if group is not None)
        parsed[match.group(1).lower()] = html.unescape(value)
    return parsed


def _safe_path(path: Path, root: Path) -> Path | None:
    try:
        resolved = path.resolve()
        resolved.relative_to(root.resolve())
    except (OSError, ValueError):
        return None
    return resolved


def _asset_path(src: str, root: Path) -> Path | None:
    """Resolve a local source URL without allowing a path outside ``root``."""

    if not src:
        return None
    parsed = urlsplit(src)
    if parsed.scheme or parsed.netloc:
        return None
    path = unquote(parsed.path)
    if not path or Path(path).suffix.lower() not in RASTER_EXTENSIONS:
        return None
    relative = path.lstrip("/")
    if relative.startswith("./"):
        relative = relative[2:]
    return _safe_path(root / relative, root)


def _dimensions(path: Path) -> tuple[int, int] | None:
    if Image is None or not path.is_file():
        return None
    try:
        with Image.open(path) as source:
            return tuple(int(value) for value in source.size)
    except (OSError, ValueError):
        return None


def image_dimensions(src: str, root: Path = ROOT) -> tuple[int, int] | None:
    """Return actual source dimensions for a local raster image."""

    path = _asset_path(src, root)
    return _dimensions(path) if path else None


def _candidate_url(src: str, candidate: Path, root: Path) -> str:
    """Map a candidate asset path back to the URL style used by the page."""

    relative = candidate.resolve().relative_to(root.resolve()).as_posix()
    parsed = urlsplit(src)
    source_path = parsed.path
    if source_path.startswith("./"):
        candidate_path = "./" + relative
    elif source_path.startswith("/"):
        candidate_path = "/" + relative
    else:
        candidate_path = relative
    return urlunsplit(("", "", candidate_path, parsed.query, ""))


def _variant_paths(src: str, root: Path) -> list[tuple[Path, str]]:
    base = _asset_path(src, root)
    if not base:
        return []

    paths: list[tuple[Path, str]] = []
    for width in VARIANT_WIDTHS:
        names = [base.with_name(f"{base.stem}-{width}{base.suffix}")]
        # A handful of legacy pages reference a duplicate root-level asset,
        # while its generated variants live under /public/.
        if base.parent == root:
            names.append(root / "public" / f"{base.stem}-{width}{base.suffix}")
        for candidate in names:
            if not candidate.is_file():
                continue
            actual = _dimensions(candidate)
            if not actual or actual[0] != width:
                continue
            paths.append((candidate, _candidate_url(src, candidate, root)))
            break
    return paths


def responsive_candidates(src: str, root: Path = ROOT) -> list[tuple[str, int]]:
    """Return existing, non-upscaled variant URLs and their actual widths."""

    base_dimensions = image_dimensions(src, root)
    if not base_dimensions:
        return []
    candidates: list[tuple[str, int]] = []
    seen_widths: set[int] = set()
    for path, url in _variant_paths(src, root):
        actual = _dimensions(path)
        if not actual or actual[0] >= base_dimensions[0] or actual[0] in seen_widths:
            continue
        seen_widths.add(actual[0])
        candidates.append((url, actual[0]))
    return candidates


class _ImageParser(HTMLParser):
    """Collect image start-tag spans and ancestor context from source HTML."""

    VOID_TAGS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self, source: str):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.images: list[dict[str, object]] = []
        self.stack: list[tuple[str, dict[str, str]]] = []
        self.line_starts = [0]
        self.line_starts.extend(
            index + 1 for index, char in enumerate(source) if char == "\n"
        )

    def _span(self) -> tuple[int, int]:
        line, column = self.getpos()
        start = self.line_starts[line - 1] + column
        raw = self.get_starttag_text() or ""
        return start, start + len(raw)

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[no-untyped-def]
        tag = tag.lower()
        parsed = {str(key).lower(): (value or "") for key, value in attrs}
        if tag == "img":
            start, end = self._span()
            self.images.append(
                {
                    "start": start,
                    "end": end,
                    "raw": self.source[start:end],
                    "attrs": parsed,
                    "ancestors": list(self.stack),
                }
            )
        if tag not in self.VOID_TAGS:
            self.stack.append((tag, parsed))

    def handle_startendtag(self, tag: str, attrs) -> None:  # type: ignore[no-untyped-def]
        if tag.lower() != "img":
            return
        start, end = self._span()
        self.images.append(
            {
                "start": start,
                "end": end,
                "raw": self.source[start:end],
                "attrs": {str(key).lower(): (value or "") for key, value in attrs},
                "ancestors": list(self.stack),
            }
        )

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break


def _classes(ancestors: list[tuple[str, dict[str, str]]]) -> set[str]:
    classes: set[str] = set()
    for _, attrs in ancestors:
        classes.update(attrs.get("class", "").lower().split())
    return classes


def _context(
    info: dict[str, object],
    index: int,
    first_non_card: int | None,
    page_path: Path,
) -> str:
    attrs = info["attrs"]
    assert isinstance(attrs, dict)
    ancestors = info["ancestors"]
    assert isinstance(ancestors, list)
    classes = _classes(ancestors)
    card_classes = {
        "card-thumb",
        "guide-card",
        "guide-grid",
        "news",
        "news-grid",
        "related-card",
        "related-grid",
        "rel-card",
    }
    if classes & card_classes:
        return "card"
    # The vintage flashback uses four archival figures rather than a single
    # lead hero; keep every scan lazy so the long-form page does not compete
    # with the article text for first paint.
    if page_path.name in {
        "1980-golf-ads-golf-digest-flashback.html",
        "news-2026-solheim-cup-all-star-challenge.html",
        "solheim-cup-all-star-challenge-2026.html",
        "news-2026-jon-rahm-liv-golf-major-champions-leaving.html",
        "jon-rahm-liv-golf-major-champions-leaving.html",
        "bobby-jones-grand-slam-1930-merion-flashback.html",
    }:
        return "secondary"
    if "manifesto-video" in classes:
        return "brand"
    if (
        "lead-img" in classes
        or "hero" in classes
        or attrs.get("fetchpriority") == "high"
        or attrs.get("loading") == "eager"
        or (first_non_card is not None and index == first_non_card)
    ):
        return "hero"
    return "secondary"


def _replace_attrs(
    raw: str,
    replacements: dict[str, str],
    removals: set[str],
) -> str:
    wanted = {name.lower(): value for name, value in replacements.items()}
    remove = {name.lower() for name in removals} | set(wanted)

    def remove_match(match: re.Match[str]) -> str:
        return "" if match.group(1).lower() in remove else match.group(0)

    cleaned = ATTR_REMOVE_RE.sub(remove_match, raw)
    close = "/>" if cleaned.rstrip().endswith("/>") else ">"
    body = cleaned[: -len(close)]
    additions = "".join(f' {name}="{html.escape(value, quote=True)}"' for name, value in replacements.items())
    return body + additions + close


def _render_srcset(candidates: list[tuple[str, int]]) -> str:
    return ", ".join(f"{url} {width}w" for url, width in candidates)


def normalize_image_markup(
    source: str,
    page_path: str | Path,
    root: Path = ROOT,
) -> str:
    """Normalize local raster ``<img>`` attributes without reserializing HTML."""

    page = Path(page_path)
    parser = _ImageParser(source)
    parser.feed(source)

    card_indices = {
        index
        for index, info in enumerate(parser.images)
        if _context(info, index, None, page) == "card"
    }
    first_non_card = next(
        (index for index in range(len(parser.images)) if index not in card_indices),
        None,
    )

    replacements: list[tuple[int, int, str]] = []
    for index, info in enumerate(parser.images):
        attrs = info["attrs"]
        assert isinstance(attrs, dict)
        src = attrs.get("src", "")
        dimensions = image_dimensions(src, root)
        if not dimensions:
            continue

        context = _context(info, index, first_non_card, page)
        candidates = responsive_candidates(src, root)
        if context == "card":
            sizes = CARD_SIZES
        elif context == "brand":
            sizes = BRAND_SIZES
        else:
            sizes = ARTICLE_SIZES

        image_attrs = {
            "width": str(dimensions[0]),
            "height": str(dimensions[1]),
        }
        if candidates:
            image_attrs["srcset"] = _render_srcset(candidates)
            image_attrs["sizes"] = sizes

        removals = {"width", "height"}
        if candidates:
            removals.update({"srcset", "sizes"})

        if context == "card":
            image_attrs["loading"] = "lazy"
            removals.add("fetchpriority")
        elif context == "hero":
            image_attrs["loading"] = "eager"
            image_attrs["fetchpriority"] = "high"
            removals.add("loading")
            removals.add("fetchpriority")
        elif context == "secondary":
            image_attrs["loading"] = "lazy"
            removals.add("fetchpriority")

        raw = info["raw"]
        assert isinstance(raw, str)
        replacements.append(
            (
                int(info["start"]),
                int(info["end"]),
                _replace_attrs(raw, image_attrs, removals),
            )
        )

    normalized = source
    for start, end, replacement in reversed(replacements):
        normalized = normalized[:start] + replacement + normalized[end:]
    return normalized


def production_html_files(root: Path = ROOT) -> list[Path]:
    files = []
    for path in root.rglob("*.html"):
        relative_parts = path.relative_to(root).parts
        if path.name in NON_PRODUCTION_HTML:
            continue
        if DEPLOY_IGNORED_DIRS.intersection(relative_parts):
            continue
        files.append(path)
    return sorted(files)


def iter_image_records(root: Path = ROOT):
    for page_path in production_html_files(root):
        source = page_path.read_text(encoding="utf-8")
        parser = _ImageParser(source)
        parser.feed(source)
        for info in parser.images:
            yield page_path, info


def _srcset_candidates(value: str):
    for part in value.split(","):
        bits = part.strip().split()
        if not bits:
            continue
        width = None
        if len(bits) > 1 and bits[1].endswith("w") and bits[1][:-1].isdigit():
            width = int(bits[1][:-1])
        yield bits[0], width


def audit_image_markup(root: Path = ROOT) -> dict[str, int]:
    """Return deterministic image markup counts for regression checks."""

    report = {
        "images": 0,
        "missing_dimensions": 0,
        "missing_srcset": 0,
        "invalid_srcset_candidates": 0,
        "dimension_mismatches": 0,
        "files_with_missing_dimensions": 0,
        "homepage_images": 0,
        "homepage_missing_dimensions": 0,
        "homepage_missing_srcset": 0,
    }
    files_missing_dimensions: set[Path] = set()

    for page_path, info in iter_image_records(root):
        attrs = info["attrs"]
        assert isinstance(attrs, dict)
        src = attrs.get("src", "")
        dimensions = image_dimensions(src, root)
        if not dimensions:
            continue

        report["images"] += 1
        homepage = page_path.name == "index.html"
        if homepage:
            report["homepage_images"] += 1

        try:
            declared = (int(attrs.get("width", "")), int(attrs.get("height", "")))
        except (TypeError, ValueError):
            declared = None
        if declared != dimensions:
            if not declared or not attrs.get("width") or not attrs.get("height"):
                report["missing_dimensions"] += 1
                files_missing_dimensions.add(page_path)
                if homepage:
                    report["homepage_missing_dimensions"] += 1
            else:
                report["dimension_mismatches"] += 1

        candidates = responsive_candidates(src, root)
        if not attrs.get("srcset"):
            report["missing_srcset"] += 1
            if homepage:
                report["homepage_missing_srcset"] += 1

        for candidate_url, descriptor in _srcset_candidates(attrs.get("srcset", "")):
            path = _asset_path(candidate_url, root)
            candidate_dimensions = _dimensions(path) if path else None
            if not candidate_dimensions or (
                descriptor is not None and candidate_dimensions[0] != descriptor
            ):
                report["invalid_srcset_candidates"] += 1

    report["files_with_missing_dimensions"] = len(files_missing_dimensions)
    return report


def normalize_site(root: Path = ROOT) -> tuple[int, int]:
    """Normalize all deployable pages; return changed files and image counts."""

    changed_files = 0
    changed_images = 0
    for page_path in production_html_files(root):
        source = page_path.read_text(encoding="utf-8")
        normalized = normalize_image_markup(source, page_path, root)
        if normalized == source:
            continue
        changed_files += 1
        before_parser = _ImageParser(source)
        before_parser.feed(source)
        after_parser = _ImageParser(normalized)
        after_parser.feed(normalized)
        changed_images += sum(
            1 for before, after in zip(
                before_parser.images, after_parser.images
            ) if before.get("raw") != after.get("raw")
        )
        page_path.write_text(normalized, encoding="utf-8")
    return changed_files, changed_images


def image_attribute_string(src: str, context: str, root: Path = ROOT) -> str:
    """Render attributes for a newly generated card or article image."""

    dimensions = image_dimensions(src, root)
    attrs: list[tuple[str, str]] = []
    if dimensions:
        attrs.extend([("width", str(dimensions[0])), ("height", str(dimensions[1]))])
    candidates = responsive_candidates(src, root)
    if candidates:
        attrs.append(("srcset", _render_srcset(candidates)))
        sizes = CARD_SIZES if context == "card" else ARTICLE_SIZES
        attrs.append(("sizes", sizes))
    return "".join(
        f' {name}="{html.escape(value, quote=True)}"' for name, value in attrs
    )
