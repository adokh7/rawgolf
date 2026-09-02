#!/usr/bin/env python3
"""Regression coverage for the Michael Block Ally Challenge article."""

import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SLUG = "news-2026-michael-block-ally-challenge"
CANONICAL = f"https://www.golfraw.com/{SLUG}"
IMAGE = "/public/michael-block-ally-challenge-2026.webp"


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


class MichaelBlockArticleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = ROOT / f"{SLUG}.html"
        cls.html = cls.path.read_text(encoding="utf-8") if cls.path.exists() else ""
        cls.registry = json.loads((ROOT / "articles.json").read_text(encoding="utf-8"))

    def test_article_and_neutral_image_exist(self):
        self.assertTrue(self.path.exists())
        asset = ROOT / IMAGE.lstrip("/")
        self.assertTrue(asset.exists())
        self.assertGreater(asset.stat().st_size, 0)
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
        self.assertEqual(["PGA TOUR CHAMPIONS", "TOURNAMENTS", "NEWS"], record.get("category"))
        self.assertEqual("PGA TOUR", record.get("section"))

    def test_metadata_and_hero_are_page_specific(self):
        title = "Michael Block's Ally Challenge: A 36-Hole Record, Then 74"
        description = (
            "He set the tournament's 36-hole scoring record, led by two, then shot 74. "
            "Why a T3 is still the best result of his senior career, and what it buys him."
        )
        alt = (
            "Michael Block reacting to his shot at Warwick Hills during the 2026 Ally Challenge "
            "after setting the 36-hole scoring record."
        )
        self.assertIn(f"<title>{title}</title>", self.html)
        self.assertIn(f'<meta name="description" content="{description}">', self.html)
        self.assertIn(f'<link rel="canonical" href="{CANONICAL}">', self.html)
        self.assertIn(f'<meta property="og:url" content="{CANONICAL}">', self.html)
        self.assertIn(f'<meta property="og:image" content="https://www.golfraw.com{IMAGE}">', self.html)
        self.assertIn(f'<img src="{IMAGE}" alt="{alt}"', self.html)
        self.assertIn("MICHAEL BLOCK SET THE ALLY CHALLENGE 36-HOLE RECORD", self.html)

    def test_standard_article_layout_and_content_sections_exist(self):
        for marker in (
            '<main class="main-content" style="padding-top: 48px;">',
            '<div class="page-grid">',
            '<article class="article-body">',
            '<aside class="sidebar"',
            '<div class="takeaways">',
            'class="related-grid"',
            "Michael Block Senior Tour Performance",
            "Anatomy of the 36-Hole Record",
            "Sunday Reality Check",
            "Career Senior Impact",
            "The 2023 Oak Hill Comparison",
            "5 Claims Fact-Checked",
            "Frequently Asked Questions",
            "Sources",
        ):
            self.assertIn(marker, self.html, marker)
        self.assertIn("This Week's Ratings", self.html)
        self.assertIn(">Tools<", self.html)

    def test_verified_performance_numbers_are_used(self):
        for value in ("66-70-67", "65-65-67", "66-65-74", "13-under 131", "$132,000", "13th career"):
            self.assertIn(value, self.html, value)
        self.assertNotIn("71-68-67", self.html)

    def test_json_ld_contains_article_breadcrumb_faq_person_and_organization(self):
        parser = JsonLdParser()
        parser.feed(self.html)
        documents = [json.loads(block) for block in parser.blocks]
        types = {item.get("@type") for document in documents for item in self._objects(document)}
        self.assertIn("NewsArticle", types)
        self.assertIn("BreadcrumbList", types)
        self.assertIn("FAQPage", types)
        self.assertIn("Person", types)
        self.assertIn("Organization", types)
        article = next(
            item for document in documents for item in self._objects(document)
            if item.get("@type") == "NewsArticle"
        )
        self.assertEqual(CANONICAL, article.get("mainEntityOfPage"))
        self.assertEqual(IMAGE, re.sub(r"https://www\.golfraw\.com", "", article["image"][0]))

    @staticmethod
    def _objects(value):
        if isinstance(value, dict):
            yield value
            for child in value.values():
                yield from MichaelBlockArticleTests._objects(child)
        elif isinstance(value, list):
            for child in value:
                yield from MichaelBlockArticleTests._objects(child)


if __name__ == "__main__":
    unittest.main()
