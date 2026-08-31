import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTICLE_PATH = ROOT / "news-2026-scheffler-brandel-chamblee.html"
ARTICLE_URL = "/news-2026-scheffler-brandel-chamblee"
CANONICAL_URL = f"https://www.golfraw.com{ARTICLE_URL}"
IMAGE_PATH = "/public/scheffler-brandel-chamblee-2026.webp"


class SchefflerBrandelChambleeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = ARTICLE_PATH.read_text(encoding="utf-8")

    def test_article_and_requested_asset_exist(self):
        self.assertTrue(ARTICLE_PATH.is_file())
        image = ROOT / IMAGE_PATH.lstrip("/")
        self.assertTrue(image.is_file())
        self.assertTrue(image.read_bytes().startswith(b"RIFF"))
        self.assertIn(b"WEBP", image.read_bytes()[:16])

    def test_page_metadata_and_hero_are_page_specific(self):
        self.assertIn(
            "<title>Scheffler and Brandel Chamblee: The Full 2026 Arc | GOLFRAW</title>",
            self.html,
        )
        self.assertIn(
            '<meta name="description" content="In April he didn\'t recognise Scheffler\'s swing. In August he called him miles ahead. Both takes were right, and the record proves it.">',
            self.html,
        )
        self.assertIn(f'<link rel="canonical" href="{CANONICAL_URL}">', self.html)
        self.assertIn(f'<meta property="og:url" content="{CANONICAL_URL}">', self.html)
        self.assertIn(
            f'<meta property="og:image" content="https://www.golfraw.com{IMAGE_PATH}">',
            self.html,
        )
        self.assertIn(
            '<meta property="og:image:alt" content="Scottie Scheffler and Brandel Chamblee on the Golf Central set after the 2026 Tour Championship.">',
            self.html,
        )
        self.assertIn(
            f'<link rel="preload" as="image" href="{IMAGE_PATH}" fetchpriority="high">',
            self.html,
        )
        self.assertIn('<div class="wrap page-grid" style="padding-top: 48px;">', self.html)
        self.assertIn(
            f'<img src="{IMAGE_PATH}" alt="Scottie Scheffler and Brandel Chamblee on the Golf Central set after the 2026 Tour Championship." width="1200" height="675"',
            self.html,
        )
        self.assertIn(
            "SCOTTIE SCHEFFLER JOINED BRANDEL CHAMBLEE ON GOLF CENTRAL POSTGAME AFTER WINNING THE 2026 TOUR CHAMPIONSHIP, CAPPING A SEASON-LONG NARRATIVE ARC. PHOTO: RAWGOLF",
            self.html,
        )

    def test_sitewide_layout_and_article_content_are_present(self):
        for marker in (
            "font-family:'Archivo'",
            "font-family:'IBM Plex Mono'",
            'class="nav-links" id="navLinks"',
            'class="burger" id="burger"',
            "/lib/locker/schema.js?v=6",
            "/lib/locker/store.js?v=6",
            "/lib/locker/drawer.js?v=6",
            "<footer",
            "Key Takeaways",
            "Chamblee's 2026 Scheffler Timeline",
            "Verifying the Postgame Interview",
            "The Spring Critique vs Reality",
            "The Player of the Year Turn",
            "How Sunday Sealed the Argument",
            "Debunking 5 Viral Media Misconceptions",
            "The Raw Verdict",
            "Frequently Asked Questions",
        ):
            self.assertIn(marker, self.html)
        for timeframe, take in (
            ("April (Masters/Spring)", '"Don\'t recognize this swing"'),
            ("May (PGA Championship", '"Worst golf in years"'),
            ("June (POTY Debate)", '"Brilliantly consistent"'),
            ("August (Playoffs)", '"Scottie is miles ahead"'),
        ):
            self.assertIn(timeframe, self.html)
            self.assertIn(take, self.html)

    def test_sidebar_tools_and_required_internal_links_are_present(self):
        sidebar = re.search(r'<aside class="article-aside sidebar".*?</aside>', self.html, re.DOTALL)
        self.assertIsNotNone(sidebar)
        self.assertIn("This Week's Ratings", sidebar.group(0))
        self.assertRegex(sidebar.group(0), r"Tools")
        for href in (
            "/news-2026-scottie-scheffler-final-press-conference-answer",
            "/scottie-scheffler-swing-explained",
            "/news-2026-hovland-on-what-makes-scheffler-successful",
            "/news-2026-tour-championship-points-and-payouts",
        ):
            self.assertIn(f'href="{href}"', self.html)
        self.assertRegex(self.html, r'<section class="sources"[^>]*>')

    def test_json_ld_contains_complete_requested_entities(self):
        blocks = re.findall(
            r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
            self.html,
            re.DOTALL,
        )
        self.assertGreaterEqual(len(blocks), 1)
        for block in blocks:
            graph = json.loads(block)["@graph"]
            types = {entity["@type"] for entity in graph}
            self.assertTrue({"NewsArticle", "FAQPage", "Organization", "Person", "BreadcrumbList"} <= types)
            article = next(entity for entity in graph if entity["@type"] == "NewsArticle")
            self.assertEqual(article["mainEntityOfPage"]["@id"], CANONICAL_URL)
            breadcrumb = next(entity for entity in graph if entity["@type"] == "BreadcrumbList")
            self.assertEqual(
                [item["item"] for item in breadcrumb["itemListElement"]],
                [
                    "https://www.golfraw.com/",
                    "https://www.golfraw.com/pga-tour",
                    CANONICAL_URL,
                ],
            )

    def test_registry_and_public_surfaces_register_the_article(self):
        registry = json.loads((ROOT / "articles.json").read_text(encoding="utf-8"))
        article = next(
            record for record in registry["articles"]
            if record.get("canonical") == ARTICLE_URL
        )
        self.assertEqual(article["image"], IMAGE_PATH)
        self.assertEqual(article["category"], ["PGA TOUR", "TOURNAMENTS", "NEWS"])
        for name in ("index.html", "news.html", "pga-tour.html", "search.html", "feed.xml", "sitemap.xml"):
            self.assertIn(ARTICLE_URL, (ROOT / name).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
