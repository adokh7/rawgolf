#!/usr/bin/env python3
"""Regression coverage for the Viktor Hovland runner-up article."""

import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SLUG = "news-2026-hovland-tour-championship-runner-up"
CANONICAL = f"https://www.golfraw.com/{SLUG}"
IMAGE = "/public/hovland-tour-championship-runner-up-2026.webp"


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


class HovlandArticleTests(unittest.TestCase):
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
        record = self.registry["articles"][0]
        self.assertEqual(SLUG, record.get("slug"))
        self.assertEqual(f"/{SLUG}", record.get("url"))
        self.assertEqual(f"/{SLUG}", record.get("canonical"))
        self.assertEqual(IMAGE, record.get("image"))
        self.assertEqual(["PGA TOUR", "TOURNAMENTS", "NEWS"], record.get("category"))
        self.assertEqual("PGA TOUR", record.get("section"))

    def test_metadata_hero_and_standard_layout_are_page_specific(self):
        title = "Hovland's Tour Championship Runner-Up and What He Said | GOLFRAW"
        description = (
            "He led the field in putting by six strokes and still said his ceiling was nowhere close. "
            "The misses that cost him, and the coach he's gone back to."
        )
        alt = (
            "Viktor Hovland reacting on the green at East Lake during the 2026 Tour Championship "
            "after finishing solo second."
        )
        for marker in (
            f"<title>{title}</title>",
            f'<meta name="description" content="{description}">',
            f'<link rel="canonical" href="{CANONICAL}">',
            f'<meta property="og:url" content="{CANONICAL}">',
            f'<meta property="og:image" content="https://www.golfraw.com{IMAGE}">',
            f'<main class="main-content" style="padding-top: 48px;">',
            '<div class="page-grid">',
            '<article class="article-body">',
            '<aside class="sidebar"',
            '<div class="takeaways">',
            'class="related-grid"',
            f'<img src="{IMAGE}" alt="{alt}"',
        ):
            self.assertIn(marker, self.html, marker)

    def test_requested_sections_and_verified_round_data_are_present(self):
        for marker in (
            "Correcting the Round Sequence",
            "Where the Tournament Slipped",
            "The Ceiling Quote Decoded",
            "The Putting Reality",
            "The Joe Mayo Reunion",
            "Debunking 5 Post-Tournament Misconceptions",
            "The Raw Verdict",
            "Frequently Asked Questions",
            "Sources",
            "64-66-65-72",
            "6 consecutive putts of 7+ feet",
            "+6.0",
            "$5,000,000",
            "100 yards",
        ):
            self.assertIn(marker, self.html, marker)
        self.assertNotIn("64-65-66-72", self.html)

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
            "/news-2026-tour-championship-points-and-payouts",
            "/news-2026-scheffler-brandel-chamblee",
            "/news-2026-hovland-on-what-makes-scheffler-successful",
        ):
            self.assertIn(f'href="{href}"', self.html)
        for name in ("index.html", "news.html", "pga-tour.html", "search.html", "feed.xml", "sitemap.xml"):
            self.assertIn(SLUG, (ROOT / name).read_text(encoding="utf-8"), name)

    @staticmethod
    def _objects(value):
        if isinstance(value, dict):
            yield value
            for child in value.values():
                yield from HovlandArticleTests._objects(child)
        elif isinstance(value, list):
            for child in value:
                yield from HovlandArticleTests._objects(child)


if __name__ == "__main__":
    unittest.main()
