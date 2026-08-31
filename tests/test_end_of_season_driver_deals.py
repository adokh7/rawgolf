#!/usr/bin/env python3
"""Regression coverage for the end-of-season driver deals buying guide."""

import json
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SLUG = "news-2026-end-of-season-driver-deals"
CANONICAL = f"https://www.golfraw.com/{SLUG}"
IMAGE = "/public/end-of-season-driver-deals-2026.webp"
TITLE = "End-of-Season Driver Deals: What's Actually Worth Buying | GOLFRAW"
DESCRIPTION = (
    "The driver with the most PGA Tour wins in 2026 costs $449, less than some new fairway woods. "
    "What's discounted now, and the one check before you buy."
)


class JsonLdParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.blocks = []
        self._capturing = False
        self._buffer = []

    def handle_starttag(self, tag, attrs):
        if tag == "script" and dict(attrs).get("type") == "application/ld+json":
            self._capturing = True
            self._buffer = []

    def handle_data(self, data):
        if self._capturing:
            self._buffer.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._capturing:
            self.blocks.append("".join(self._buffer))
            self._capturing = False


class EndOfSeasonDriverDealsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = ROOT / f"{SLUG}.html"
        cls.html = cls.path.read_text(encoding="utf-8") if cls.path.exists() else ""
        cls.registry = json.loads((ROOT / "articles.json").read_text(encoding="utf-8"))

    def test_article_and_asset_exist(self):
        self.assertTrue(self.path.exists())
        asset = ROOT / IMAGE.lstrip("/")
        self.assertTrue(asset.exists())
        self.assertEqual(b"RIFF", asset.read_bytes()[:4])
        self.assertEqual(b"WEBP", asset.read_bytes()[8:12])

    def test_registry_entry_is_first_and_uses_guides_section(self):
        first = self.registry["articles"][0]
        self.assertEqual(SLUG, first.get("slug"))
        self.assertEqual(f"/{SLUG}", first.get("url"))
        self.assertEqual(f"/{SLUG}", first.get("canonical"))
        self.assertEqual(TITLE, first.get("title"))
        self.assertEqual(DESCRIPTION, first.get("excerpt"))
        self.assertEqual(IMAGE, first.get("image"))
        self.assertEqual(["GUIDES", "GEAR", "NEWS"], first.get("category"))
        self.assertEqual("GUIDES", first.get("section"))

    def test_metadata_layout_and_hero_are_page_specific(self):
        alt = (
            "Discounted 2026 flagship drivers including PING G440 and Titleist GT on display "
            "in a golf fitting studio."
        )
        for marker in (
            f"<title>{TITLE}</title>",
            f'<meta name="description" content="{DESCRIPTION}">',
            f'<link rel="canonical" href="{CANONICAL}">',
            '<meta name="robots" content="index, follow, max-image-preview:large">',
            f'<meta property="og:title" content="{TITLE}">',
            f'<meta property="og:description" content="{DESCRIPTION}">',
            f'<meta property="og:url" content="{CANONICAL}">',
            f'<meta property="og:image" content="https://www.golfraw.com{IMAGE}">',
            '<main class="main-content" style="padding-top: 48px;">',
            '<div class="page-grid">',
            '<article class="article-body">',
            '<aside class="sidebar"',
            '<div class="takeaways">',
            'class="related-grid"',
            f'<img src="{IMAGE}" alt="{alt}"',
            "GUIDES • GEAR",
        ):
            self.assertIn(marker, self.html, marker)

    def test_content_table_sections_and_internal_links_exist(self):
        for marker in (
            "2026 End-of-Season Driver Deals Comparison",
            "PING G440",
            "$449",
            "Titleist GT",
            "Callaway Elyte Lineup",
            "Cobra Darkspeed X",
            "TaylorMade Qi4D",
            "The Anatomy of Current Cuts",
            "The Early Discount Mystery",
            "Performance vs Price",
            "The TaylorMade Cycle Shift",
            "USGA Rule 4.1a &amp; Conforming List Check",
            "5 Discount Season Myths Debunked",
            "The Practical Buyer's Guide",
            "The Raw Verdict",
            "Frequently Asked Questions",
            "Sources",
            "/news-2026-scheffler-ted-scott-finding-the-number",
            "/news-2026-scheffler-true-strokes-gained",
            "/news-2026-tour-championship-points-and-payouts",
        ):
            self.assertIn(marker, self.html, marker)

    def test_json_ld_contains_required_entities_and_breadcrumbs(self):
        parser = JsonLdParser()
        parser.feed(self.html)
        documents = [json.loads(block) for block in parser.blocks]
        entities = [
            item
            for document in documents
            for item in self._objects(document)
            if isinstance(item, dict)
        ]
        types = {item.get("@type") for item in entities}
        self.assertTrue(
            {"NewsArticle", "FAQPage", "Organization", "Person", "BreadcrumbList"}
            <= types
        )
        article = next(item for item in entities if item.get("@type") == "NewsArticle")
        self.assertEqual(CANONICAL, article.get("mainEntityOfPage"))
        self.assertEqual(TITLE, article.get("headline"))
        self.assertIn(f"https://www.golfraw.com{IMAGE}", article.get("image", []))
        breadcrumb = next(item for item in entities if item.get("@type") == "BreadcrumbList")
        self.assertEqual(
            [
                (1, "Home", "https://www.golfraw.com/"),
                (2, "Guides", "https://www.golfraw.com/guides"),
                (3, "Equipment", "https://www.golfraw.com/gear"),
                (4, "End-of-Season Driver Deals", CANONICAL),
            ],
            [
                (item["position"], item["name"], item["item"])
                for item in breadcrumb["itemListElement"]
            ],
        )

    def test_synced_surfaces_include_article(self):
        for name in ("index.html", "news.html", "guides.html", "search.html", "feed.xml", "sitemap.xml"):
            self.assertIn(SLUG, (ROOT / name).read_text(encoding="utf-8"), name)

    @staticmethod
    def _objects(value):
        if isinstance(value, dict):
            yield value
            for child in value.values():
                yield from EndOfSeasonDriverDealsTests._objects(child)
        elif isinstance(value, list):
            for child in value:
                yield from EndOfSeasonDriverDealsTests._objects(child)


if __name__ == "__main__":
    unittest.main()
