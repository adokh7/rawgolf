#!/usr/bin/env python3
"""Regression coverage for the Justin Thomas comeback analysis article."""

import json
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SLUG = "news-2026-justin-thomas-mental-capacity-bay-hill"
CANONICAL = f"https://www.golfraw.com/{SLUG}"
IMAGE = "/public/justin-thomas-mental-capacity-bay-hill-2026.webp"
TITLE = "Justin Thomas's 'Mental Capacity' Line, Six Months On | GOLFRAW"
DESCRIPTION = (
    "He shot 79-79 and couldn't concentrate on the back nine. Two months later he finished "
    "fourth in a major. What that gap teaches about coming back."
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


class JustinThomasMentalCapacityTests(unittest.TestCase):
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

    def test_registry_entry_is_first_and_uses_pga_tour_section(self):
        first = self.registry["articles"][0]
        self.assertEqual(SLUG, first.get("slug"))
        self.assertEqual(f"/{SLUG}", first.get("url"))
        self.assertEqual(f"/{SLUG}", first.get("canonical"))
        self.assertEqual(TITLE, first.get("title"))
        self.assertEqual(DESCRIPTION, first.get("excerpt"))
        self.assertEqual(IMAGE, first.get("image"))
        self.assertEqual(["PGA TOUR", "OPINION", "NEWS"], first.get("category"))
        self.assertEqual("PGA TOUR", first.get("section"))

    def test_metadata_layout_and_hero_are_page_specific(self):
        alt = (
            "Justin Thomas walking off the green at Bay Hill during the 2026 Arnold Palmer "
            "Invitational following his post-surgery return."
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
            "PGA TOUR • OPINION",
        ):
            self.assertIn(marker, self.html, marker)

    def test_timeline_sections_sources_and_internal_links_exist(self):
        for marker in (
            "Justin Thomas 2026 Comeback Timeline &amp; Progression",
            "Microdiscectomy for disc/hip pain",
            "Arnold Palmer Invitational",
            "79-79 (+14, MC, Dead Last)",
            "Decoding the Quote: Concentration Stamina",
            "The Scorecard &amp; Hidden Stat",
            "The Bay Hill Hazard",
            "The Microdiscectomy Precedents",
            "The Aronimink Vindication",
            "Fact-Checking 5 March Narratives",
            "The Raw Verdict",
            "Frequently Asked Questions",
            "Sources",
            "/news-2026-brandt-jobe-ally-challenge-jackson",
            "/news-2026-scheffler-true-strokes-gained",
            "/news-2026-hovland-tour-championship-runner-up",
        ):
            self.assertIn(marker, self.html, marker)

    def test_claim_specific_sources_are_present(self):
        for href in (
            "https://www.pgatour.com/article/news/latest/2025/11/14/justin-thomas-pulls-out-of-skins-game-after-undergoing-minor-medical-procedure-health-update",
            "https://www.pgatour.com/article/news/latest/2026/02/23/justin-thomas-returns-shakes-off-rust-at-tgl-atlanta-drive-announces-return-to-tour-play-at-arnold-palmer-inviational-injury-microdiscectomy",
            "https://www.pgatour.com/article/news/latest/2026/03/05/justin-thomas-return-to-pga-tour-arnold-palmer-invitational-back-surgery-bay-hill",
            "https://asaptext.com/orgs/pgatour/1204/transcripts/164325.pdf",
            "https://www.pgachampionship.com/news-media/articles/justin-thomas-saves-his-best-for-last-at-aronimink",
            "https://www.pgatour.com/tournaments/2026/pga-championship/R2026033/leaderboard",
        ):
            self.assertIn(f'href="{href}"', self.html, href)

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
                (3, "PGA Tour", "https://www.golfraw.com/pga-tour"),
                (4, "JT Mental Capacity", CANONICAL),
            ],
            [
                (item["position"], item["name"], item["item"])
                for item in breadcrumb["itemListElement"]
            ],
        )

    def test_synced_surfaces_include_article(self):
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
                yield from JustinThomasMentalCapacityTests._objects(child)
        elif isinstance(value, list):
            for child in value:
                yield from JustinThomasMentalCapacityTests._objects(child)


if __name__ == "__main__":
    unittest.main()
