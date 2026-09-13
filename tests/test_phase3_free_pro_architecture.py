#!/usr/bin/env python3
"""Regression checks for the Phase 3 public Free/Pro product architecture."""

import importlib
import json
import re
import subprocess
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "scripts" / "tool_inventory.py"
PRO_BUILDER_PATH = ROOT / "scripts" / "build_pro_page.py"
PRO_PAGE_PATH = ROOT / "pro.html"
HUB_PATH = ROOT / "tools.html"
COACH_PATH = ROOT / "tools-coach-report.html"
STANDING_ORDER_PATH = ROOT / "tools-standing-order.html"


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.meta = {}
        self.canonical = ""
        self.links = []
        self.json_ld = []
        self._capture = None
        self._buffer = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self._capture = "title"
            self._buffer = []
        elif tag == "meta":
            key = (attrs.get("name") or attrs.get("property") or "").lower()
            if key:
                self.meta[key] = attrs.get("content", "")
        elif tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href", "")
        elif tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        elif tag == "script" and attrs.get("type") == "application/ld+json":
            self._capture = "json"
            self._buffer = []

    def handle_data(self, data):
        if self._capture:
            self._buffer.append(data)

    def handle_endtag(self, tag):
        if tag == "title" and self._capture == "title":
            self.title = " ".join("".join(self._buffer).split())
            self._capture = None
            self._buffer = []
        elif tag == "script" and self._capture == "json":
            try:
                self.json_ld.append(json.loads("".join(self._buffer)))
            except json.JSONDecodeError:
                pass
            self._capture = None
            self._buffer = []


def parse(path):
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def schema_nodes(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from schema_nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from schema_nodes(child)


class FreeProArchitectureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT))
        cls.inventory = importlib.import_module("scripts.tool_inventory")

    def test_inventory_defines_one_verified_public_free_pro_model(self):
        model = self.inventory.PRODUCT_MODEL
        counts = self.inventory.tool_counts()

        self.assertEqual("Free", model["free"]["label"])
        self.assertEqual(counts["free"], model["free"]["tool_count"])
        self.assertIn("free forever", model["free"]["promise"].lower())
        self.assertIn("no login", model["free"]["promise"].lower())

        pro = model["pro"]
        self.assertEqual("/pro", pro["route"])
        self.assertEqual("preview", pro["status"])
        self.assertEqual(
            {"lm-import", "coach-report"},
            {feature["id"] for feature in pro["features"]},
        )
        self.assertTrue(all(feature["verified_current"] for feature in pro["features"]))
        self.assertNotIn("history", json.dumps(pro).lower())
        self.assertNotIn("monte carlo", json.dumps(pro).lower())
        self.assertNotIn("strokes-gained", json.dumps(pro).lower())

    def test_public_pro_builder_exists_and_page_has_no_generation_drift(self):
        self.assertTrue(PRO_BUILDER_PATH.exists())
        self.assertTrue(PRO_PAGE_PATH.exists())
        if not PRO_BUILDER_PATH.exists() or not PRO_PAGE_PATH.exists():
            return
        result = subprocess.run(
            [sys.executable, str(PRO_BUILDER_PATH), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_public_pro_page_is_indexable_truthful_and_pricing_neutral(self):
        parser = parse(PRO_PAGE_PATH)
        source = PRO_PAGE_PATH.read_text(encoding="utf-8")
        pro = self.inventory.PRODUCT_MODEL["pro"]

        self.assertEqual(pro["title"], parser.title)
        self.assertEqual(pro["description"], parser.meta["description"])
        self.assertEqual(self.inventory.SITE + "/pro", parser.canonical)
        self.assertEqual("index, follow, max-image-preview:large", parser.meta["robots"])
        self.assertIn('href="/tools"', source)
        self.assertIn("12", source)
        self.assertRegex(source.lower(), r"free forever")
        self.assertRegex(source.lower(), r"no login")
        self.assertIn("What Pro adds", source)
        self.assertIn("Launch-monitor CSV import", source)
        self.assertIn("Coach &amp; Fitter Report", source)
        self.assertIn("PDF", source)
        self.assertIn("share link", source)

        # No amount, currency, or unverified roadmap promise may leak into the
        # public marketing surface until product facts are confirmed.
        self.assertNotRegex(source, r"[$€£]")
        for unsupported in ("history", "multiple bags", "Monte Carlo", "strokes-gained", "client folders"):
            self.assertNotIn(unsupported.lower(), source.lower())

        nodes = [node for document in parser.json_ld for node in schema_nodes(document)]
        types = {node.get("@type") for node in nodes}
        self.assertIn("WebPage", types)
        self.assertIn("SoftwareApplication", types)
        self.assertFalse(any("offers" in node or "price" in node for node in nodes))

    def test_tools_hub_exposes_public_pro_value_path(self):
        source = HUB_PATH.read_text(encoding="utf-8")
        self.assertIn('TOOLS-HUB-PRO-VALUE:START', source)
        self.assertIn('TOOLS-HUB-PRO-VALUE:END', source)
        self.assertIn('href="/pro"', source)
        self.assertIn("Free forever", source)
        self.assertIn("What Pro adds", source)

    def test_pro_entry_points_link_to_the_public_value_surface(self):
        coach_source = COACH_PATH.read_text(encoding="utf-8")
        standing_source = STANDING_ORDER_PATH.read_text(encoding="utf-8")
        coach_builder = (ROOT / "scripts" / "build_coach_report.py").read_text(encoding="utf-8")
        standing_builder = (ROOT / "scripts" / "build_standing_order.py").read_text(encoding="utf-8")

        for source in (coach_source, standing_source, coach_builder, standing_builder):
            self.assertIn('href="/pro"', source)
            self.assertIn("what stays free and what Pro adds", source.lower())

    def test_existing_free_and_pro_schema_surfaces_remain_truthful(self):
        hub = parse(HUB_PATH)
        coach = parse(COACH_PATH)
        hub_source = HUB_PATH.read_text(encoding="utf-8")
        coach_source = COACH_PATH.read_text(encoding="utf-8")

        self.assertEqual(12, hub_source.count('data-access="free"'))
        self.assertEqual(1, hub_source.count('data-access="pro_preview"'))
        coach_nodes = [node for document in coach.json_ld for node in schema_nodes(document)]
        coach_apps = [node for node in coach_nodes if node.get("@type") == "WebApplication"]
        self.assertTrue(coach_apps)
        self.assertFalse(any("offers" in node for node in coach_apps))
        self.assertIn("Golf Raw Pro", coach.meta["description"])
        self.assertIn("every free tool stays free", coach_source.lower())


if __name__ == "__main__":
    unittest.main()
