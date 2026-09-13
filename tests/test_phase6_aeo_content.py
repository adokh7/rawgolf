#!/usr/bin/env python3
"""Regression checks for the Phase 6 answer-first article upgrades."""

import importlib
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Phase6AeoContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aeo = importlib.import_module("scripts.aeo_answers")

    def _source(self, route):
        return (ROOT / f"{route.lstrip('/')}.html").read_text(encoding="utf-8")

    def _block(self, route):
        source = self._source(route)
        start = f"<!-- AEO-ANSWER:START route={route} -->"
        end = "<!-- AEO-ANSWER:END -->"
        self.assertEqual(1, source.count(start), route)
        self.assertEqual(1, source.count(end), route)
        return source.split(start, 1)[1].split(end, 1)[0]

    def test_catalog_contains_only_existing_tool_connected_guides(self):
        catalog = self.aeo.ARTICLE_AEO_UPGRADES
        self.assertEqual(9, len(catalog))
        self.assertEqual(set(catalog), set(self.aeo.PHASE6_ROUTES))
        for route, config in catalog.items():
            self.assertTrue((ROOT / f"{route.lstrip('/')}.html").exists(), route)
            self.assertTrue(config["tool_id"].startswith("tools-"), route)
            self.assertTrue(config["heading"], route)

    def test_each_catalogued_page_has_one_managed_answer_after_its_heading(self):
        for route, config in self.aeo.ARTICLE_AEO_UPGRADES.items():
            source = self._source(route)
            block = self._block(route)
            heading_pattern = rf"<h[23][^>]*>{re.escape(config['heading'])}</h[23]>"
            heading = re.search(heading_pattern, source)
            self.assertIsNotNone(heading, route)
            self.assertGreater(source.find("AEO-ANSWER:START", heading.end()), heading.end(), route)
            self.assertEqual(1, source.count('/public/aeo-answer.css?v=1'), route)
            self.assertIn('data-aeo-answer="true"', block, route)
            self.assertIn('role="note"', block, route)
            self.assertIn('class="aeo-answer__text"', block, route)
            self.assertIn('class="aeo-answer__basis"', block, route)
            self.assertIn(config["answer"], block, route)
            self.assertIn(config["basis"], block, route)

    def test_answer_copy_is_compact_and_page_specific(self):
        answers = []
        basis_labels = []
        for route, config in self.aeo.ARTICLE_AEO_UPGRADES.items():
            block = self._block(route)
            text = re.search(r'class="aeo-answer__text">(.*?)</p>', block, re.S).group(1)
            words = re.sub(r"<[^>]+>", " ", text).split()
            self.assertGreaterEqual(len(words), 24, route)
            self.assertLessEqual(len(words), 95, route)
            answers.append(config["answer"])
            basis_labels.append(config["basis_label"])
            self.assertNotIn("the short answer", text.lower(), route)
            self.assertNotIn("in today's fast-paced", text.lower(), route)
        self.assertEqual(len(answers), len(set(answers)))
        self.assertGreaterEqual(len(set(basis_labels)), 4)

    def test_basis_is_explicit_and_no_new_rich_result_schema_was_added(self):
        for route in self.aeo.PHASE6_ROUTES:
            source = self._source(route)
            block = self._block(route)
            self.assertRegex(block, r"<(?:strong|span)[^>]*>[^<]*(?:Source|Evidence|basis|Basis|Benchmark|Format|Course|Preparation)", route)
            self.assertNotIn('"@type": "FAQPage"', source, route)
            self.assertNotIn('"@type": "HowTo"', source, route)

    def test_no_phase6_answer_marker_exists_on_unselected_articles(self):
        selected = set(self.aeo.PHASE6_ROUTES)
        for path in ROOT.glob("*.html"):
            route = "/" + path.stem
            if route not in selected:
                self.assertNotIn("AEO-ANSWER:START", path.read_text(encoding="utf-8"), path.name)

    def test_managed_blocks_are_idempotent_and_have_no_duplicate_links(self):
        for route, config in self.aeo.ARTICLE_AEO_UPGRADES.items():
            source = self._source(route)
            block = self._block(route)
            rendered = self.aeo.render_answer_block(route, config)
            self.assertEqual(1, source.count(rendered), route)
            hrefs = re.findall(r'<a\b[^>]*href="([^"]+)"', block)
            self.assertEqual(len(hrefs), len(set(hrefs)), route)

    def test_all_answer_block_links_are_valid_public_destinations(self):
        for route in self.aeo.PHASE6_ROUTES:
            block = self._block(route)
            for href in re.findall(r'<a\b[^>]*href="([^"]+)"', block):
                if href.startswith("/"):
                    self.assertTrue((ROOT / f"{href.lstrip('/')}.html").exists(), (route, href))


if __name__ == "__main__":
    unittest.main()
