#!/usr/bin/env python3
"""Regression checks for the maintainable Phase 2 tools hub architecture."""

import html
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
BUILDER_PATH = ROOT / "scripts" / "build_tools_hub.py"
HUB_PATH = ROOT / "tools.html"

EXPECTED_ROUTES = {
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


class HubParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta = {}
        self.title = ""
        self.json_ld = []
        self.tool_slugs = []
        self.tool_routes = []
        self.groups = []
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
        elif tag == "a" and attrs.get("data-tool-slug"):
            self.tool_slugs.append(attrs["data-tool-slug"])
            self.tool_routes.append(attrs.get("href", ""))
        elif tag == "section" and "tool-group" in attrs.get("class", "").split():
            self.groups.append(attrs.get("data-tool-group", ""))

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


def parse_hub():
    parser = HubParser()
    parser.feed(HUB_PATH.read_text(encoding="utf-8"))
    return parser


def schema_nodes(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from schema_nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from schema_nodes(child)


class ToolsHubArchitectureTests(unittest.TestCase):
    def test_single_inventory_defines_thirteen_tools_and_access_counts(self):
        self.assertTrue(INVENTORY_PATH.exists())
        if not INVENTORY_PATH.exists():
            return
        sys.path.insert(0, str(ROOT))
        inventory = importlib.import_module("scripts.tool_inventory")
        tools = inventory.TOOLS
        self.assertEqual(13, len(tools))
        self.assertEqual(EXPECTED_ROUTES, {tool["route"] for tool in tools})
        self.assertEqual(12, sum(tool["access"] == "free" for tool in tools))
        self.assertEqual(1, sum(tool["access"] == "pro_preview" for tool in tools))
        self.assertEqual(
            {"performance-practice", "course-management", "bag-equipment", "games-scoring", "pro-output"},
            {tool["group"] for tool in tools},
        )
        self.assertEqual(len(tools), len({tool["slug"] for tool in tools}))
        for tool in tools:
            self.assertTrue((ROOT / f"{tool['slug']}.html").exists(), tool["slug"])
            self.assertTrue(tool["name"] and tool["description"] and tool["cta"], tool["slug"])

    def test_builder_exists_and_current_hub_has_no_drift(self):
        self.assertTrue(BUILDER_PATH.exists())
        if not BUILDER_PATH.exists():
            return
        result = subprocess.run(
            [sys.executable, str(BUILDER_PATH), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_hub_renders_inventory_groups_access_badges_and_schema(self):
        parser = parse_hub()
        source = HUB_PATH.read_text(encoding="utf-8")
        self.assertEqual("Golf Tools: 12 Free Utilities + Coach Report | GolfRaw", parser.title)
        self.assertNotRegex(source, r"\beight\b")
        self.assertEqual(13, len(parser.tool_slugs))
        self.assertEqual(13, len(set(parser.tool_slugs)))
        self.assertEqual(EXPECTED_ROUTES, set(parser.tool_routes))
        self.assertEqual(5, len(parser.groups))
        self.assertIn('data-access="free"', source)
        self.assertIn('data-access="pro_preview"', source)
        self.assertEqual(12, source.count('data-access="free"'))
        self.assertEqual(1, source.count('data-access="pro_preview"'))

        collection = next(
            node
            for document in parser.json_ld
            for node in schema_nodes(document)
            if node.get("@type") == "CollectionPage"
        )
        item_list = collection["mainEntity"]
        items = [entry["item"] for entry in item_list["itemListElement"]]
        self.assertEqual(13, item_list["numberOfItems"])
        self.assertEqual(EXPECTED_ROUTES, {item["url"].replace("https://www.golfraw.com", "") for item in items})
        self.assertEqual(12, sum("offers" in item for item in items))
        coach = next(item for item in items if item["url"].endswith("tools-coach-report"))
        self.assertNotIn("offers", coach)
        self.assertIn("GolfRaw Pro", coach["description"])

    def test_inventory_metadata_is_shared_by_visible_cards_and_schema(self):
        sys.path.insert(0, str(ROOT))
        inventory = importlib.import_module("scripts.tool_inventory")
        parser = parse_hub()
        collection = next(
            node
            for document in parser.json_ld
            for node in schema_nodes(document)
            if node.get("@type") == "CollectionPage"
        )
        items = {
            item["url"]: item
            for entry in collection["mainEntity"]["itemListElement"]
            for item in (entry["item"],)
        }
        source = HUB_PATH.read_text(encoding="utf-8")

        self.assertEqual(inventory.HUB_TITLE, parser.title)
        self.assertEqual(inventory.HUB_DESCRIPTION, parser.meta["description"])
        self.assertEqual(inventory.HUB_TITLE, parser.meta["og:title"])
        self.assertEqual(inventory.HUB_TITLE, parser.meta["twitter:title"])
        free_count = inventory.tool_counts()["free"]
        self.assertIn(f"Every result from the {free_count} free tools", source)
        self.assertIn(f"Run any of the {free_count} free tools above", source)
        for tool in inventory.TOOLS:
            self.assertEqual(1, source.count(f'data-tool-slug="{tool["slug"]}"'))
            self.assertIn(html.escape(tool["description"]), source)
            schema_item = items[inventory.SITE + tool["route"]]
            self.assertEqual(tool["name"], schema_item["name"])
            self.assertEqual(tool["description"], schema_item["description"])
            if tool["access"] == "free":
                self.assertIn("offers", schema_item)
            else:
                self.assertNotIn("offers", schema_item)

        for group in inventory.GROUPS:
            self.assertEqual(1, source.count(f'data-tool-group="{group["id"]}"'))
            self.assertIn(html.escape(group["label"]), source)

    def test_hub_managed_regions_are_present(self):
        source = HUB_PATH.read_text(encoding="utf-8")
        for name in ("METADATA", "SCHEMA", "HERO", "CARDS", "DASHBOARD", "EMPTY"):
            self.assertIn(f"TOOLS-HUB-{name}:START", source)
            self.assertIn(f"TOOLS-HUB-{name}:END", source)


if __name__ == "__main__":
    unittest.main()
