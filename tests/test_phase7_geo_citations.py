import html
import re
import unittest
from pathlib import Path

from scripts.geo_citations import CITATION_UPGRADES, render_citation_block


ROOT = Path(__file__).resolve().parents[1]


class Phase7GeoCitationTests(unittest.TestCase):
    def test_catalog_is_small_explicit_and_source_backed(self):
        self.assertEqual(
            set(CITATION_UPGRADES),
            {
                "/news-2026-golf-club-distances-guide",
                "/guides-playing-golf-in-your-fifties-distance-loss",
                "/guides-the-three-feet-that-decide-whether-you-three-putt",
                "/how-long-do-golf-clubs-last",
            },
        )
        for route, config in CITATION_UPGRADES.items():
            self.assertTrue((ROOT / f"{route.lstrip('/')}.html").exists(), route)
            self.assertTrue(config["entity"], route)
            self.assertTrue(config["methodology"], route)
            self.assertTrue(config["freshness"], route)
            self.assertGreaterEqual(len(config["sources"]), 1, route)
            for source in config["sources"]:
                self.assertTrue(source["url"].startswith("https://"), source)
                self.assertTrue(source["name"], source)
                self.assertTrue(source["role"], source)

    def test_each_upgrade_has_one_accessible_citation_block(self):
        for route, config in CITATION_UPGRADES.items():
            page = (ROOT / f"{route.lstrip('/')}.html").read_text()
            block = render_citation_block(route, config)
            self.assertEqual(page.count(block), 1, route)
            self.assertEqual(
                page.count(f"<!-- GEO-CITATION:START route={route} id={config['id']} -->"),
                1,
                route,
            )
            self.assertEqual(page.count("<!-- GEO-CITATION:END -->"), 1, route)
            self.assertEqual(page.count('/public/geo-citation.css?v=1'), 1, route)
            self.assertIn('role="note"', block)
            self.assertIn('aria-label="Source and methodology"', block)
            self.assertIn('data-geo-citation="true"', block)

    def test_citation_block_has_explicit_entity_and_source_links(self):
        for route, config in CITATION_UPGRADES.items():
            page = (ROOT / f"{route.lstrip('/')}.html").read_text()
            block = render_citation_block(route, config)
            self.assertIn(
                html.unescape(config["entity"]),
                html.unescape(block),
                route,
            )
            self.assertIn("Source:", block, route)
            self.assertIn("GolfRaw", block, route)
            hrefs = re.findall(r'<a\b[^>]*\bhref="([^"]+)"', block)
            self.assertEqual(
                hrefs,
                [source["url"] for source in config["sources"]],
                route,
            )
            self.assertEqual(len(hrefs), len(set(hrefs)), route)
            self.assertEqual(block.count('target="_blank"'), len(hrefs), route)
            self.assertEqual(block.count('rel="noopener noreferrer"'), len(hrefs), route)
            self.assertIn(
                config["freshness"].removeprefix("Reporting context: "),
                block,
                route,
            )
            self.assertNotIn("According to", block, route)

            # The block is intentionally a source/method note, not a schema payload.
            self.assertNotIn("application/ld+json", block, route)
            self.assertNotIn("FAQPage", block, route)
            self.assertNotIn("HowTo", block, route)

            # Confirm the rendered source links are not HTML-escaped into a different URL.
            for href in hrefs:
                self.assertEqual(html.unescape(href), href, (route, href))

    def test_blocks_are_in_their_configured_context_and_not_duplicated(self):
        method_texts = []
        for route, config in CITATION_UPGRADES.items():
            page = (ROOT / f"{route.lstrip('/')}.html").read_text()
            marker = f"<!-- GEO-CITATION:START route={route} id={config['id']} -->"
            marker_position = page.index(marker)
            anchor_position = page.index(config["placement_anchor"])
            if config["placement"] == "after":
                self.assertGreater(marker_position, anchor_position, route)
            else:
                self.assertLess(marker_position, anchor_position, route)
            self.assertEqual(page.count(config["methodology"]), 1, route)
            method_texts.append(config["methodology"])

        self.assertEqual(len(method_texts), len(set(method_texts)))

    def test_no_unsupported_claim_shortcuts_in_managed_blocks(self):
        forbidden_phrases = (
            "we tested",
            "our testing",
            "proven",
            "guarantee",
            "the definitive",
            "best on the market",
            "ai-optimized",
        )
        for route, config in CITATION_UPGRADES.items():
            block = render_citation_block(route, config).lower()
            for phrase in forbidden_phrases:
                self.assertNotIn(phrase, block, (route, phrase))


if __name__ == "__main__":
    unittest.main()
