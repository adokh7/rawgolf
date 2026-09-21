#!/usr/bin/env python3
"""Central JSON-LD normalizer for the Phase 8 public schema surface.

This module works at the rendered HTML boundary.  Tool identity and access
come from ``tool_inventory``; article values come from page-owned metadata and
the existing article normalizer.  It deliberately does not add ratings,
reviews, prices, or product capabilities that are not verified in the site.
"""

from __future__ import annotations

import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

from scripts import tool_inventory as inventory
from scripts.article_schema import normalize_article_schema


ROOT = Path(__file__).resolve().parents[1]
SITE = inventory.SITE
PUBLISHER_ID = f"{SITE}#organization"
EDITORIAL_ID = f"{SITE}/about#editorial"
PUBLISHER_URL = f"{SITE}/"
PUBLISHER_LOGO = f"{SITE}/icon-512.png"

JSON_LD_RE = re.compile(
    r'(<script\b[^>]*type\s*=\s*["\']application/ld\+json["\'][^>]*>)'
    r'(.*?)'
    r'(</script\s*>)',
    re.IGNORECASE | re.DOTALL,
)

ARTICLE_ROUTES = (
    "/news-2026-golf-club-distances-guide",
    "/news-2026-raw-golf-honest-practice-guide",
    "/golf-clubs-for-beginners",
    "/golf-swing-analysis-apps",
    "/guides-the-three-feet-that-decide-whether-you-three-putt",
    "/guides-playing-golf-in-your-fifties-distance-loss",
    "/amateur-tournament-guide",
    "/guides-how-to-play-in-a-golf-pro-am-costs-etiquette",
    "/news-2026-the-renaissance-club-course-guide",
    "/how-long-do-golf-clubs-last",
)

COACH_FEATURES = (
    "One-page report from your range session, bag and rounds",
    "Print or save the report as PDF",
    "Share the report by link",
)


def _clean(value: object) -> str:
    return re.sub(r"\s+", " ", html.unescape(str(value or ""))).strip()


def _types(node: object) -> set[str]:
    if not isinstance(node, dict):
        return set()
    value = node.get("@type")
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return {item for item in value if isinstance(item, str)}
    return set()


def walk(value: object):
    """Yield every nested JSON object, including the root."""

    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


class _MetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.meta: dict[str, list[str]] = {}
        self.canonical = ""
        self.title = ""
        self.h1 = ""
        self._capture: str | None = None
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[no-untyped-def]
        values = {str(key).lower(): str(value or "") for key, value in attrs}
        tag = tag.lower()
        if tag == "meta":
            key = values.get("name") or values.get("property")
            if key and values.get("content") is not None:
                self.meta.setdefault(key.lower(), []).append(_clean(values["content"]))
        elif tag == "link" and values.get("rel", "").lower() == "canonical":
            self.canonical = urljoin(SITE + "/", values.get("href", ""))
        elif tag in {"title", "h1"}:
            self._capture = tag
            self._buffer = []

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._capture == tag.lower():
            value = _clean("".join(self._buffer))
            if tag.lower() == "title":
                self.title = value
            else:
                self.h1 = value
            self._capture = None
            self._buffer = []


def extract_page_metadata(source: str) -> dict[str, object]:
    parser = _MetadataParser()
    parser.feed(source)
    parser.close()
    description = (parser.meta.get("description") or [""])[0]
    image = (parser.meta.get("og:image") or [""])[0]
    return {
        "canonical": parser.canonical,
        "title": parser.title,
        "h1": parser.h1,
        "description": description,
        "image": urljoin(SITE + "/", image) if image else "",
        "published": (parser.meta.get("article:published_time") or [""])[0],
        "modified": (parser.meta.get("article:modified_time") or [""])[0],
        "section": (parser.meta.get("article:section") or [""])[0],
        "author": (parser.meta.get("article:author") or parser.meta.get("author") or [""])[0],
    }


class _FAQParser(HTMLParser):
    """Read the visible Q&A pair from the site's small FAQ variants."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.faq_scopes: list[int] = []
        self.capture_kind: str | None = None
        self.capture_tag = ""
        self.capture_depth = 0
        self.capture_buffer: list[str] = []
        self.question = ""
        self.pairs: list[tuple[str, str]] = []

    @staticmethod
    def _classes(attrs) -> set[str]:  # type: ignore[no-untyped-def]
        values = {str(key).lower(): str(value or "") for key, value in attrs}
        return set(values.get("class", "").split())

    def _start_capture(self, kind: str, tag: str) -> None:
        self.capture_kind = kind
        self.capture_tag = tag
        self.capture_depth = self.depth
        self.capture_buffer = []

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[no-untyped-def]
        tag = tag.lower()
        self.depth += 1
        classes = self._classes(attrs)
        if classes.intersection({"faq", "faq-block", "faq-item", "faq-in", "faq-section"}):
            self.faq_scopes.append(self.depth)
        in_faq = bool(self.faq_scopes)
        if self.capture_kind is not None:
            return
        if in_faq and (tag == "summary" or "faq-q" in classes or tag == "h3"):
            self._start_capture("question", tag)
        elif in_faq and tag == "p" and self.question:
            self._start_capture("answer", tag)

    def handle_data(self, data: str) -> None:
        if self.capture_kind is not None:
            self.capture_buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self.capture_kind is not None and tag == self.capture_tag and self.depth == self.capture_depth:
            value = _clean("".join(self.capture_buffer))
            if self.capture_kind == "question":
                self.question = value
            elif self.question and value:
                self.pairs.append((self.question, value))
                self.question = ""
            self.capture_kind = None
            self.capture_tag = ""
            self.capture_buffer = []
        if self.faq_scopes and self.faq_scopes[-1] == self.depth:
            self.faq_scopes.pop()
        self.depth = max(0, self.depth - 1)


def extract_visible_faq(source: str) -> list[tuple[str, str]]:
    parser = _FAQParser()
    parser.feed(source)
    parser.close()
    result = []
    seen = set()
    for question, answer in parser.pairs:
        if question and answer and (question, answer) not in seen:
            result.append((question, answer))
            seen.add((question, answer))
    return result


def _organization() -> dict:
    return {
        "@type": "Organization",
        "@id": PUBLISHER_ID,
        "name": "GolfRaw",
        "alternateName": ["GOLFRAW", "Golf Raw"],
        "url": PUBLISHER_URL,
        "logo": {
            "@type": "ImageObject",
            "url": PUBLISHER_LOGO,
            "width": 512,
            "height": 512,
        },
    }


def _canonical_for_route(route: str) -> str:
    return SITE + route


def _tool_for_route(route: str) -> dict:
    for tool in inventory.TOOLS:
        if tool["route"] == route:
            return tool
    raise ValueError(f"route is not in the authoritative tool inventory: {route}")


def _tool_application(tool: dict, description: str | None = None) -> dict:
    canonical = _canonical_for_route(tool["route"])
    app = {
        "@type": "WebApplication",
        "@id": canonical + "#application",
        "name": tool["name"],
        "url": canonical,
        "applicationCategory": "SportsApplication",
        "operatingSystem": "Any browser",
        "browserRequirements": "Requires JavaScript",
        "description": description or tool["description"],
        "publisher": {"@id": PUBLISHER_ID},
        "inLanguage": "en",
    }
    if tool["access"] == "free":
        app["isAccessibleForFree"] = True
        app["offers"] = {
            "@type": "Offer",
            "url": canonical,
            "price": "0",
            "priceCurrency": "USD",
        }
    if tool["slug"] == "tools-coach-report":
        app["featureList"] = list(COACH_FEATURES)
    return app


def _breadcrumbs(canonical: str, label: str, section: str = "Tools", section_url: str | None = None) -> dict:
    return {
        "@type": "BreadcrumbList",
        "@id": canonical + "#breadcrumb",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": section, "item": section_url or SITE + "/tools"},
            {"@type": "ListItem", "position": 3, "name": label, "item": canonical},
        ],
    }


def _faq_node(canonical: str, pairs: list[tuple[str, str]]) -> dict | None:
    if not pairs:
        return None
    return {
        "@type": "FAQPage",
        "@id": canonical + "#faq",
        "mainEntity": [
            {
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {"@type": "Answer", "text": answer},
            }
            for question, answer in pairs
        ],
    }


def _json_document(payload: object) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False).replace("</script>", "<\\/script>")


def _script(payload: object) -> str:
    return '<script type="application/ld+json">\n' + _json_document(payload) + "\n  </script>"


def _replace_all_json_ld(source: str, payload: object) -> str:
    rendered = _script(payload)
    matches = list(JSON_LD_RE.finditer(source))
    if not matches:
        head_end = re.search(r"</head\s*>", source, re.IGNORECASE)
        if not head_end:
            raise ValueError("cannot insert JSON-LD without a head element")
        return source[: head_end.start()] + rendered + "\n" + source[head_end.start() :]
    # Remove only the JSON-LD blocks.  Stylesheets and other head assets can
    # legitimately sit between historical schema blocks and must survive the
    # normalization pass.
    parts: list[str] = []
    cursor = 0
    for index, match in enumerate(matches):
        parts.append(source[cursor : match.start()])
        if index == 0:
            parts.append(rendered)
        cursor = match.end()
    parts.append(source[cursor:])
    return "".join(parts)


def _ensure_tool_stylesheet(source: str) -> str:
    link = '  <link rel="stylesheet" href="/public/tool-premium.css?v=4">'
    if link in source:
        return source
    head_end = re.search(r"</head\s*>", source, re.IGNORECASE)
    if not head_end:
        raise ValueError("cannot restore the tool stylesheet without a head element")
    return source[: head_end.start()] + link + "\n" + source[head_end.start() :]


def _replace_json_documents(source: str, transform) -> str:
    def replace(match: re.Match[str]) -> str:
        try:
            document = json.loads(match.group(2))
        except (TypeError, ValueError) as exc:
            raise ValueError("malformed JSON-LD in selected page") from exc
        result = transform(document)
        return match.group(1) + "\n" + _json_document(result) + "\n" + match.group(3)

    return JSON_LD_RE.sub(replace, source)


def _normalize_tool(source: str, route: str) -> str:
    tool = _tool_for_route(route)
    metadata = extract_page_metadata(source)
    canonical = _canonical_for_route(route)
    application = _tool_application(tool, str(metadata["description"]))
    if metadata["h1"] and metadata["h1"] != tool["name"]:
        # Some tools use a campaign-style H1 while the inventory keeps the
        # stable product name.  Preserve both without making the H1 the
        # canonical entity name.
        application["alternateName"] = str(metadata["h1"])
    nodes = [
        _organization(),
        application,
        _breadcrumbs(canonical, tool["search_name"]),
    ]
    faq = _faq_node(canonical, extract_visible_faq(source))
    if faq:
        nodes.append(faq)
    return _ensure_tool_stylesheet(
        _replace_all_json_ld(source, {"@context": "https://schema.org", "@graph": nodes})
    )


def normalize_tool_page(source: str, path_or_route: str | Path) -> str:
    """Normalize one public tool page from the inventory."""

    route = _route_from_path(path_or_route)
    return _normalize_tool(source, route)


def _hub_schema() -> dict:
    items = []
    for position, tool in enumerate(inventory.TOOLS, start=1):
        app = _tool_application(tool)
        items.append({"@type": "ListItem", "position": position, "item": app})
    collection = {
        "@type": "CollectionPage",
        "@id": inventory.HUB_CANONICAL + "#webpage",
        "name": "GolfRaw Tools Suite",
        "url": inventory.HUB_CANONICAL,
        "description": inventory.HUB_DESCRIPTION,
        "publisher": {"@id": PUBLISHER_ID},
        "mainEntity": {
            "@type": "ItemList",
            "@id": inventory.HUB_CANONICAL + "#tool-list",
            "name": f"The {len(inventory.TOOLS)} GolfRaw tools",
            "numberOfItems": len(inventory.TOOLS),
            "itemListElement": items,
        },
        "inLanguage": "en",
    }
    return {"@context": "https://schema.org", "@graph": [_organization(), collection]}


def normalize_tools_hub(source: str) -> str:
    return _replace_all_json_ld(source, _hub_schema())


def _pro_schema() -> dict:
    free = inventory.PRODUCT_MODEL["free"]
    pro = inventory.PRODUCT_MODEL["pro"]
    page_url = _canonical_for_route(pro["route"])
    features = [feature["label"] + ": " + feature["summary"] for feature in pro["features"]]
    application = {
        "@type": "SoftwareApplication",
        "@id": page_url + "#product",
        "name": pro["label"],
        "url": page_url,
        "applicationCategory": "SportsApplication",
        "operatingSystem": "Any browser",
        "browserRequirements": "Requires JavaScript",
        "description": (
            f"{free['tool_count']} free browser-based golf tools remain available. "
            "The current Pro surface adds the following verified capabilities."
        ),
        "featureList": features,
        "publisher": {"@id": PUBLISHER_ID},
        "inLanguage": "en",
    }
    page = {
        "@type": "WebPage",
        "@id": page_url + "#webpage",
        "name": pro["title"],
        "url": page_url,
        "description": pro["description"],
        "mainEntity": {"@id": application["@id"]},
        "publisher": {"@id": PUBLISHER_ID},
        "inLanguage": "en",
    }
    return {
        "@context": "https://schema.org",
        "@graph": [_organization(), page, application, _breadcrumbs(page_url, pro["label"])],
    }


def normalize_pro_page(source: str) -> str:
    return _replace_all_json_ld(source, _pro_schema())


def _load_record(route: str) -> dict:
    registry = json.loads((ROOT / "articles.json").read_text(encoding="utf-8"))
    slug = route.strip("/")
    for record in registry.get("articles", []):
        if record.get("slug") == slug or str(record.get("canonical", "")).strip("/") == slug:
            return record
    return {}


def _article_node(metadata: dict[str, object], route: str) -> dict:
    canonical = _canonical_for_route(route)
    record = _load_record(route)
    headline = str(record.get("title") or metadata.get("title") or route.lstrip("/"))
    author_name = str(metadata.get("author") or "GolfRaw Editorial")
    if author_name.casefold() == "golfraw editorial":
        author_name = "GolfRaw Editorial"
    published = str(metadata.get("published") or "")
    node = {
        "@type": "Article",
        "@id": canonical + "#article",
        "headline": headline,
        "description": str(metadata.get("description") or ""),
        "image": str(metadata.get("image") or ""),
        "datePublished": published,
        "author": {
            "@type": "Organization",
            "@id": EDITORIAL_ID,
            "name": author_name,
            "url": SITE + "/about",
        },
        "publisher": _organization(),
        "mainEntityOfPage": canonical,
        "articleSection": str(metadata.get("section") or record.get("section") or "Guides"),
    }
    if metadata.get("modified"):
        node["dateModified"] = str(metadata["modified"])
    return node


def _enrich_article_documents(source: str, route: str) -> str:
    metadata = extract_page_metadata(source)
    canonical = _canonical_for_route(route)
    found_article = False
    found_breadcrumb = False

    def transform(document: object) -> object:
        nonlocal found_article, found_breadcrumb
        for node in walk(document):
            if not isinstance(node, dict):
                continue
            if _types(node).intersection({"Article", "NewsArticle"}) and not found_article:
                found_article = True
                if not node.get("articleSection"):
                    node["articleSection"] = str(metadata.get("section") or "Guides")
                node["mainEntityOfPage"] = canonical
            if "BreadcrumbList" in _types(node):
                found_breadcrumb = True
                node["@id"] = canonical + "#breadcrumb"
                elements = node.get("itemListElement")
                if isinstance(elements, list) and elements:
                    for element in elements:
                        if isinstance(element, dict) and element.get("item"):
                            element["item"] = urljoin(SITE + "/", str(element["item"]))
                    if isinstance(elements[-1], dict):
                        elements[-1]["item"] = canonical
        return document

    normalized = _replace_json_documents(source, transform)
    if found_article:
        return normalized
    # A selected article without an Article node gets one additive, canonical
    # entity. Existing WebSite/BreadcrumbList markup remains intact.
    return _insert_json_ld_before_first(normalized, _article_node(metadata, route))


def _insert_json_ld_before_first(source: str, payload: object) -> str:
    rendered = _script({"@context": "https://schema.org", **payload} if isinstance(payload, dict) else payload)
    match = JSON_LD_RE.search(source)
    if match:
        return source[: match.start()] + rendered + "\n" + source[match.start() :]
    head_end = re.search(r"</head\s*>", source, re.IGNORECASE)
    if not head_end:
        raise ValueError("cannot insert JSON-LD without a head element")
    return source[: head_end.start()] + rendered + "\n" + source[head_end.start() :]


def normalize_selected_article(source: str, path_or_route: str | Path) -> str:
    route = _route_from_path(path_or_route)
    page_path = _page_path(route)
    if any(_types(node).intersection({"Article", "NewsArticle"}) for document in _documents(source) for node in walk(document)):
        source = normalize_article_schema(source, page_path)
    return _enrich_article_documents(source, route)


def _documents(source: str) -> list[object]:
    documents = []
    for match in JSON_LD_RE.finditer(source):
        try:
            documents.append(json.loads(match.group(2)))
        except (TypeError, ValueError) as exc:
            raise ValueError("malformed JSON-LD") from exc
    return documents


def _page_path(route: str) -> Path:
    path = ROOT / route.lstrip("/")
    return path if path.exists() else path.with_suffix(".html")


def _route_from_path(path_or_route: str | Path) -> str:
    value = str(path_or_route)
    if value.startswith("/") and "/" not in value[1:]:
        return value[:-5] if value.endswith(".html") else value
    path = Path(value)
    name = path.name
    return "/" + name[:-5] if name.endswith(".html") else "/" + name


def normalize_phase8_page(source: str, route: str) -> str:
    if route == inventory.HUB_ROUTE:
        return normalize_tools_hub(source)
    if route == inventory.PRODUCT_MODEL["pro"]["route"]:
        return normalize_pro_page(source)
    if route in {tool["route"] for tool in inventory.TOOLS}:
        return normalize_tool_page(source, route)
    if route in ARTICLE_ROUTES:
        return normalize_selected_article(source, route)
    raise ValueError(f"route is outside Phase 8 scope: {route}")


def phase8_paths() -> list[tuple[str, Path]]:
    routes = [inventory.HUB_ROUTE, inventory.PRODUCT_MODEL["pro"]["route"]]
    routes.extend(tool["route"] for tool in inventory.TOOLS)
    routes.extend(ARTICLE_ROUTES)
    return [(route, _page_path(route)) for route in routes]


def normalize_phase8_pages(apply: bool = False) -> tuple[int, list[str]]:
    changed = 0
    errors: list[str] = []
    for route, path in phase8_paths():
        if not path.exists():
            errors.append(f"{route}: missing {path.name}")
            continue
        source = path.read_text(encoding="utf-8")
        try:
            normalized = normalize_phase8_page(source, route)
        except (ValueError, KeyError) as exc:
            errors.append(f"{route}: {exc}")
            continue
        if normalized != source:
            changed += 1
            if apply:
                path.write_text(normalized, encoding="utf-8")
    return changed, errors
