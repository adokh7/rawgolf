#!/usr/bin/env python3
"""Regression coverage for the LIV Golf bankruptcy deadlock feature."""

import json
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SLUG = "news-2026-liv-golf-bankruptcy-player-settlements-deadlock"
CANONICAL = f"https://www.golfraw.com/{SLUG}"
IMAGE = "/public/liv-golf-bankruptcy-deadlock-2026.webp"
TITLE = "LIV Golf Bankruptcy: The Deadlock Nobody Can Break | GolfRaw"
DESCRIPTION = (
    "The investor won't commit until players sign. Players won't sign for cents on the dollar. "
    "That standoff is why Chapter 11 is now the likeliest exit."
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


class LivGolfBankruptcyDeadlockTests(unittest.TestCase):
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

    def test_registry_entry_uses_liv_section(self):
        entry = next(
            article for article in self.registry["articles"] if article.get("slug") == SLUG
        )
        self.assertEqual(SLUG, entry.get("slug"))
        self.assertEqual(f"/{SLUG}", entry.get("url"))
        self.assertEqual(f"/{SLUG}", entry.get("canonical"))
        self.assertEqual(TITLE, entry.get("title"))
        self.assertEqual(DESCRIPTION, entry.get("excerpt"))
        self.assertEqual(IMAGE, entry.get("image"))
        self.assertEqual(["LIV GOLF", "TOURNAMENTS", "NEWS"], entry.get("category"))
        self.assertEqual("LIV GOLF", entry.get("section"))

    def test_metadata_layout_and_hero_are_page_specific(self):
        alt = (
            "LIV Golf corporate branding and tournament staging standing empty amid Chapter 11 "
            "bankruptcy standoff and player settlement disputes."
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
            "LIV GOLF • INVESTIGATION",
        ):
            self.assertIn(marker, self.html, marker)

    def test_standoff_table_sections_and_internal_links_exist(self):
        for marker in (
            "The LIV Golf Bankruptcy Standoff Matrix",
            "Private Equity (BC Partners)",
            "LIV Golf Players",
            "PIF (Saudi Wealth Fund)",
            "League Operations",
            "The Anatomy of the Standoff",
            "The Legal Mechanics of Chapter 11",
            "The Financing Nuance",
            "What Has Already Been Cut",
            "The LIV 2.0 Reality",
            "Debunking 5 Viral Bankruptcy Myths",
            "The Raw Verdict",
            "Frequently Asked Questions",
            "Sources",
            "/news-2026-the-end-of-liv-golf-bankruptcy",
            "/news-2026-scott-oneil-linkedin-post-liv-golf",
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
                (2, "News", "https://www.golfraw.com/news"),
                (3, "LIV Golf", "https://www.golfraw.com/liv-golf"),
                (4, "LIV Bankruptcy Deadlock", CANONICAL),
            ],
            [
                (item["position"], item["name"], item["item"])
                for item in breadcrumb["itemListElement"]
            ],
        )

    def test_synced_surfaces_include_article(self):
        for name in ("index.html", "news.html", "liv-golf.html", "search.html", "feed.xml", "sitemap.xml"):
            self.assertIn(SLUG, (ROOT / name).read_text(encoding="utf-8"), name)

    @staticmethod
    def _objects(value):
        if isinstance(value, dict):
            yield value
            for child in value.values():
                yield from LivGolfBankruptcyDeadlockTests._objects(child)
        elif isinstance(value, list):
            for child in value:
                yield from LivGolfBankruptcyDeadlockTests._objects(child)


if __name__ == "__main__":
    unittest.main()
