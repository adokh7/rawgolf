#!/usr/bin/env python3
"""Regression coverage for the Brandt Jobe / Jackson Jobe feature."""

import json
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SLUG = "news-2026-brandt-jobe-ally-challenge-jackson"
CANONICAL = f"https://www.golfraw.com/{SLUG}"
IMAGE = "/public/brandt-jobe-ally-challenge-jackson-2026.webp"


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


class BrandtJobeArticleTests(unittest.TestCase):
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
        first = self.registry["articles"][0]
        self.assertEqual(SLUG, first.get("slug"))
        self.assertEqual(f"/{SLUG}", first.get("url"))
        self.assertEqual(f"/{SLUG}", first.get("canonical"))
        self.assertEqual(IMAGE, first.get("image"))
        self.assertEqual(
            ["PGA TOUR CHAMPIONS", "TOURNAMENTS", "NEWS"], first.get("category")
        )
        self.assertEqual("PGA TOUR", first.get("section"))

    def test_metadata_hero_and_standard_layout_are_page_specific(self):
        title = "Brandt Jobe's Ally Challenge: Best Week in Over a Year | GOLFRAW"
        description = (
            "A 69 on Sunday for his best result since last August, and a Tuesday night at Comerica "
            "watching his son pitch. The week nobody put on a highlight reel."
        )
        alt = (
            "Brandt Jobe watching his tee shot at Warwick Hills during the 2026 Ally Challenge "
            "after shooting 8-under 208."
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
            "PGA TOUR CHAMPIONS",
        ):
            self.assertIn(marker, self.html, marker)

    def test_required_sections_table_data_and_links_exist(self):
        for marker in (
            "The Scorecard Breakdown",
            "Why T12 is a Victory",
            "Tuesday Night at Comerica Park",
            "Parallel Rehabs",
            "The 2006 Augusta Flashback",
            "Fact-Checking 4 Claims",
            "The Raw Verdict",
            "Frequently Asked Questions",
            "Sources",
            "Brandt Jobe (Father, 61)",
            "Jackson Jobe (Son, 24)",
            "Both hips &amp; shoulder reconstruction",
            "Tommy John elbow reconstruction",
            "67-72-69",
            "3.93 ERA",
            "4.1 IP",
            "4 Ks",
            "4-1 Win vs Tampa Bay",
            "/news-2026-michael-block-ally-challenge",
            "/news-2026-tour-championship-points-and-payouts",
            "/news-2026-hovland-tour-championship-runner-up",
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
                yield from BrandtJobeArticleTests._objects(child)
        elif isinstance(value, list):
            for child in value:
                yield from BrandtJobeArticleTests._objects(child)


if __name__ == "__main__":
    unittest.main()
