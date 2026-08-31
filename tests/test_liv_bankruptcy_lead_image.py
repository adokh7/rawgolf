#!/usr/bin/env python3
"""Regression checks for the LIV bankruptcy article's lead image wiring."""

import json
import re
import unittest
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
SLUG = "news-2026-the-end-of-liv-golf-bankruptcy"
IMAGE_PATH = "/public/the-end-of-liv-golf-bankruptcy-2026.webp"
IMAGE_URL = f"https://www.golfraw.com{IMAGE_PATH}"


class LivBankruptcyLeadImageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.article_path = ROOT / f"{SLUG}.html"
        cls.html = cls.article_path.read_text(encoding="utf-8")
        cls.registry = json.loads((ROOT / "articles.json").read_text(encoding="utf-8"))

    def test_target_asset_is_a_nonempty_webp(self):
        asset = ROOT / IMAGE_PATH.lstrip("/")
        self.assertTrue(asset.exists(), "target lead image is missing")
        data = asset.read_bytes()
        self.assertGreater(len(data), 0)
        self.assertEqual(b"RIFF", data[:4])
        self.assertEqual(b"WEBP", data[8:12])

    def test_article_and_registry_use_target_asset(self):
        record = next(
            article for article in self.registry["articles"]
            if article.get("slug") == SLUG
        )
        self.assertEqual(IMAGE_PATH, record.get("image"))
        self.assertIn(f'<img src="{IMAGE_PATH}"', self.html)
        self.assertIn(f'property="og:image" content="{IMAGE_URL}"', self.html)
        self.assertIn(f'name="twitter:image" content="{IMAGE_URL}"', self.html)
        self.assertIn(f'preload" as="image" href="{IMAGE_PATH}"', self.html)
        self.assertNotIn("scheffler-brandel-chamblee-2026.webp", self.html)

    def test_image_alt_and_layout_are_page_specific(self):
        expected_alt = (
            "LIV Golf tournament branding and signage at a venue amid Chapter 11 "
            "bankruptcy reports and purse cuts."
        )
        self.assertIn(f'property="og:image:alt" content="{expected_alt}"', self.html)
        self.assertIn(f'<img src="{IMAGE_PATH}" alt="{expected_alt}"', self.html)
        self.assertIn('<div class="wrap page-grid"', self.html)
        self.assertIn('<aside class="article-aside sidebar"', self.html)
        self.assertIn('<div class="key-takeaways"', self.html)
        self.assertIn("This Week's Ratings", self.html)
        self.assertIn('<div class="rel-grid">', self.html)

    def test_feed_enclosure_length_matches_target_asset(self):
        feed = (ROOT / "feed.xml").read_text(encoding="utf-8")
        match = re.search(
            rf"<item>.*?<link>https://www\.golfraw\.com/{re.escape(SLUG)}</link>.*?"
            rf'<enclosure url="{re.escape(IMAGE_URL)}" length="(\d+)"',
            feed,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match, "target article feed item is missing")
        self.assertEqual(
            (ROOT / IMAGE_PATH.lstrip("/")).stat().st_size,
            int(match.group(1)),
        )

    def test_json_ld_uses_target_image(self):
        self.assertGreaterEqual(self.html.count(IMAGE_URL), 3)


if __name__ == "__main__":
    unittest.main()
