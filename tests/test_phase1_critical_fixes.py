#!/usr/bin/env python3
"""Regression checks for Phase 1 critical SEO and access-label fixes."""

import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.golfraw.com"

TOOL_ROUTES = {
    "/tools-settle-up-calculator",
    "/tools-round-autopsy",
    "/tools-tee-box-check",
    "/tools-handicap-detector",
    "/tools-plays-like",
    "/tools-tilt-meter",
    "/tools-bag-audit",
    "/tools-gimme-audit",
    "/tools-the-grudge-match",
    "/tools-standing-order",
    "/tools-tendency-engine",
    "/tools-field-reader",
    "/tools-coach-report",
}

STALE_LINKS = {
    "/donald-trump-amgen-irish-open-doonbeg": 6,
    "/brooks-koepka-pga-tour-return-season-verdict": 2,
}


class HeadParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.meta = {}
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
    parser = HeadParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def nodes(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)


def schema_nodes(parser, schema_type):
    return [
        node
        for document in parser.json_ld
        for node in nodes(document)
        if node.get("@type") == schema_type
    ]


class Phase1CriticalFixTests(unittest.TestCase):
    def test_tools_hub_metadata_and_visible_copy_match_thirteen_tool_model(self):
        path = ROOT / "tools.html"
        parser = parse(path)
        source = path.read_text(encoding="utf-8")
        self.assertEqual(
            "Golf Tools: 12 Free Utilities + Coach Report | GOLFRAW", parser.title
        )
        expected_description = (
            "Twelve free client-side golf tools plus the Coach Report Pro preview. "
            "Run them in your browser with no signup, account or data upload."
        )
        self.assertEqual(expected_description, parser.meta["description"])
        self.assertEqual(expected_description, parser.meta["og:description"])
        self.assertEqual(expected_description, parser.meta["twitter:description"])
        self.assertNotRegex(source, r"\beight\b")
        for marker in ("13", "12", "Pro preview", "Tools live", "Free tools"):
            self.assertIn(marker, source)

    def test_tools_hub_schema_contains_each_tool_once_and_no_false_free_claim(self):
        parser = parse(ROOT / "tools.html")
        collection = schema_nodes(parser, "CollectionPage")[0]
        item_list = collection["mainEntity"]
        self.assertEqual("ItemList", item_list["@type"])
        self.assertEqual(13, item_list["numberOfItems"])
        self.assertEqual("The 13 Raw Golf tools", item_list["name"])
        items = [entry["item"] for entry in item_list["itemListElement"]]
        self.assertEqual(TOOL_ROUTES, {item["url"].replace(SITE, "") for item in items})
        self.assertEqual(13, len(items))
        coach = next(item for item in items if item["url"].endswith("tools-coach-report"))
        self.assertNotIn("offers", coach)
        self.assertIn("Golf Raw Pro", coach["description"])
        self.assertIn("preview", coach["description"].lower())
        self.assertNotIn("isAccessibleForFree", collection)

    def test_coach_report_schema_and_generator_do_not_advertise_zero_price(self):
        page = ROOT / "tools-coach-report.html"
        parser = parse(page)
        app = schema_nodes(parser, "WebApplication")[0]
        self.assertNotIn("offers", app)
        self.assertIn("Golf Raw Pro", app["description"])
        self.assertIn("preview", app["description"].lower())

        generator = (ROOT / "scripts/build_coach_report.py").read_text(encoding="utf-8")
        self.assertNotIn('"offers": { "@type": "Offer", "price": "0"', generator)
        self.assertIn("Golf Raw Pro", generator)

    def test_all_eight_stale_internal_links_are_gone(self):
        found = {target: 0 for target in STALE_LINKS}
        for path in ROOT.rglob("*.html"):
            if "public" in path.parts or "golfraw.com-audit" in path.parts:
                continue
            source = path.read_text(encoding="utf-8")
            for target in found:
                found[target] += source.count(f'href="{target}"')
        self.assertEqual({target: 0 for target in STALE_LINKS}, found)


if __name__ == "__main__":
    unittest.main()
