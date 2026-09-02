#!/usr/bin/env python3
"""Regression coverage for the Scottie Scheffler True Strokes Gained feature."""

import json
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SLUG = "news-2026-scheffler-true-strokes-gained"
CANONICAL = f"https://www.golfraw.com/{SLUG}"
IMAGE = "/public/scheffler-true-strokes-gained-2026.webp"


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


class SchefflerTrueStrokesGainedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = ROOT / f"{SLUG}.html"
        cls.html = cls.path.read_text(encoding="utf-8") if cls.path.exists() else ""
        cls.registry = json.loads((ROOT / "articles.json").read_text(encoding="utf-8"))

    def test_article_and_requested_asset_exist(self):
        self.assertTrue(self.path.exists())
        asset = ROOT / IMAGE.lstrip("/")
        self.assertTrue(asset.exists())
        self.assertEqual(b"RIFF", asset.read_bytes()[:4])
        self.assertEqual(b"WEBP", asset.read_bytes()[8:12])

    def test_registry_entry_is_first_and_routes_to_pga_tour(self):
        entry = next(
            article for article in self.registry["articles"] if article.get("slug") == SLUG
        )
        self.assertEqual(SLUG, entry.get("slug"))
        self.assertEqual(f"/{SLUG}", entry.get("url"))
        self.assertEqual(f"/{SLUG}", entry.get("canonical"))
        self.assertEqual(IMAGE, entry.get("image"))
        self.assertEqual(["PGA TOUR", "RATINGS", "NEWS"], entry.get("category"))
        self.assertEqual("PGA TOUR", entry.get("section"))

    def test_metadata_hero_and_standard_layout_are_page_specific(self):
        title = "Scottie Scheffler's True Strokes Gained: 12th Since 1983"
        description = (
            "His 2026 rates as the 12th-best statistical season in 43 years, and eight above it belong to Tiger Woods. "
            "What the number does and doesn't say."
        )
        alt = (
            "Scottie Scheffler following through on an approach shot at East Lake during his historic 2026 True Strokes Gained season."
        )
        for marker in (
            f"<title>{title}</title>",
            f'<meta name="description" content="{description}">',
            f'<link rel="canonical" href="{CANONICAL}">',
            f'<meta property="og:url" content="{CANONICAL}">',
            f'<meta property="og:image" content="https://www.golfraw.com{IMAGE}">',
            '<main class="main-content" style="padding-top: 48px;">',
            '<div class="page-grid">',
            '<article class="article-body">',
            '<aside class="sidebar"',
            '<div class="takeaways">',
            'class="related-grid"',
            f'<img src="{IMAGE}" alt="{alt}"',
        ):
            self.assertIn(marker, self.html, marker)

    def test_required_sections_table_metrics_and_links_exist(self):
        for marker in (
            "Defining True Strokes Gained vs Raw PGA Tour SG",
            "The DG Points Dilemma",
            "The Bounce-Back Rate Collapse",
            "The Rate Stats vs Counting Stats Debate",
            "5 Golf Analytics Myths Debunked",
            "The Raw Verdict",
            "Frequently Asked Questions",
            "Sources",
            "Tiger Woods (Peak Era)",
            "Scottie Scheffler (2025)",
            "Scottie Scheffler (2026)",
            "+2.92 (PGA Tour Raw: +2.374)",
            "2.374",
            "1.694",
            "72.9%",
            "67.9",
            ".680",
            "/news-2026-scheffler-ted-scott-finding-the-number",
            "/news-2026-hovland-tour-championship-runner-up",
            "/news-2026-scheffler-brandel-chamblee",
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
        self.assertIn(f"https://www.golfraw.com{IMAGE}", article.get("image", []))
        breadcrumb = next(item for item in entities if item.get("@type") == "BreadcrumbList")
        self.assertEqual(
            [item["item"] for item in breadcrumb["itemListElement"]],
            [
                "https://www.golfraw.com/",
                "https://www.golfraw.com/news",
                "https://www.golfraw.com/pga-tour",
                CANONICAL,
            ],
        )

    def test_synced_public_surfaces_include_article(self):
        for name in (
            "index.html",
            "news.html",
            "pga-tour.html",
            "search.html",
            "feed.xml",
            "sitemap.xml",
        ):
            self.assertIn(SLUG, (ROOT / name).read_text(encoding="utf-8"), name)

    @staticmethod
    def _objects(value):
        if isinstance(value, dict):
            yield value
            for child in value.values():
                yield from SchefflerTrueStrokesGainedTests._objects(child)
        elif isinstance(value, list):
            for child in value:
                yield from SchefflerTrueStrokesGainedTests._objects(child)


if __name__ == "__main__":
    unittest.main()
