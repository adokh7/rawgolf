#!/usr/bin/env python3
"""Regression coverage for the Scottie Scheffler / Ted Scott strategy article."""

import json
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SLUG = "news-2026-scheffler-ted-scott-finding-the-number"
CANONICAL = f"https://www.golfraw.com/{SLUG}"
IMAGE = "/public/scheffler-ted-scott-finding-the-number-2026.webp"


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


class SchefflerTedScottArticleTests(unittest.TestCase):
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

    def test_registry_entry_routes_to_pga_tour(self):
        record = next(
            record for record in self.registry["articles"] if record.get("slug") == SLUG
        )
        self.assertEqual(SLUG, record.get("slug"))
        self.assertEqual(f"/{SLUG}", record.get("url"))
        self.assertEqual(f"/{SLUG}", record.get("canonical"))
        self.assertEqual(IMAGE, record.get("image"))
        self.assertEqual(["PGA TOUR", "GUIDES", "NEWS"], record.get("category"))
        self.assertEqual("PGA TOUR", record.get("section"))

    def test_metadata_hero_and_standard_layout_are_page_specific(self):
        title = "Scottie Scheffler and Ted Scott: How They Find the Number"
        description = (
            "He passed Hovland for good with a birdie at the 16th. What goes into that club decision, "
            "and the rule stopping your rangefinder doing it for you."
        )
        alt = (
            "Scottie Scheffler and caddie Ted Scott analyzing yardage and calculating the landing number "
            "on the fairway during the 2026 Tour Championship."
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

    def test_strategy_sections_and_requested_data_are_present(self):
        for marker in (
            "Yardage Math: The Amateur Habit vs Tour Pro Protocol",
            "Where the Tournament Turned",
            'The Definition of "Finding the Number"',
            "USGA Rule 4.3a Breakdown",
            "Ted Scott's Preparation Dynamic",
            "5 Club Selection Myths Fact-Checked",
            "The Three-Number Protocol for Your Home Course",
            "The Raw Verdict",
            "Frequently Asked Questions",
            "Sources",
            "birdie at the 16th",
            "15 greens in regulation",
            "66 for 16-under 264",
            "two-stroke penalty",
            "slope, wind and club recommendations",
            "backup caddies",
        ):
            self.assertIn(marker, self.html, marker)

    def test_json_ld_contains_requested_entities_and_breadcrumbs(self):
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
        self.assertTrue({"NewsArticle", "FAQPage", "Organization", "Person", "BreadcrumbList"} <= types)
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

    def test_internal_links_and_synced_public_surfaces_include_article(self):
        for href in (
            "/news-2026-hovland-tour-championship-runner-up",
            "/news-2026-scheffler-brandel-chamblee",
            "/news-2026-tour-championship-points-and-payouts",
        ):
            self.assertIn(f'href="{href}"', self.html)
        for name in ("index.html", "news.html", "pga-tour.html", "search.html", "feed.xml", "sitemap.xml"):
            self.assertIn(SLUG, (ROOT / name).read_text(encoding="utf-8"), name)

    @staticmethod
    def _objects(value):
        if isinstance(value, dict):
            yield value
            for child in value.values():
                yield from SchefflerTedScottArticleTests._objects(child)
        elif isinstance(value, list):
            for child in value:
                yield from SchefflerTedScottArticleTests._objects(child)


if __name__ == "__main__":
    unittest.main()
