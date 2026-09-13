"""Regression checks for the Phase 4 tool and guide link architecture."""

import importlib
import json
import re
import unittest
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self._href = None
        self._text = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attrs = dict(attrs)
            self._href = attrs.get("href")
            self._text = []

    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            self.links.append((self._href, " ".join("".join(self._text).split())))
            self._href = None
            self._text = []


def page_links(path):
    parser = LinkParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.links


def route_for(path):
    relative = path.relative_to(ROOT).with_suffix("")
    return "/" + str(relative).replace("\\", "/")


def local_target(source_path, href):
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    if parsed.path.startswith("/"):
        route = parsed.path.rstrip("/") or "/"
        target = ROOT / ("index.html" if route == "/" else route.lstrip("/") + ".html")
        if target.exists():
            return target
        target = ROOT / route.lstrip("/")
        return target if target.exists() else None
    target = (source_path.parent / parsed.path).resolve()
    if target.suffix:
        return target if target.exists() else None
    target = target.with_suffix(".html")
    return target if target.exists() else None


def all_contextual_links():
    from scripts.internal_link_map import CONTEXTUAL_LINKS

    return tuple(CONTEXTUAL_LINKS)


def site_html_files():
    """Return only published site HTML, excluding local skill/audit fixtures."""
    return tuple(ROOT.glob("*.html")) + tuple((ROOT / "equipment").glob("*.html"))


class Phase4InternalLinkingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = importlib.import_module("scripts.tool_inventory")
        cls.links = all_contextual_links()
        cls.by_source = Counter(link["source"] for link in cls.links)
        cls.by_target = Counter(link["target"] for link in cls.links)

    def test_contextual_map_has_unique_pairs_and_natural_anchor_text(self):
        pairs = [(link["source"], link["target"]) for link in self.links]
        self.assertEqual(len(pairs), len(set(pairs)))
        for link in self.links:
            self.assertTrue(link["anchor"].strip())
            self.assertNotIn("click here", link["anchor"].lower())
            self.assertNotEqual(link["source"], link["target"])

    def test_every_tool_has_tool_to_guide_and_guide_to_tool_coverage(self):
        tool_routes = {tool["route"] for tool in self.inventory.TOOLS}
        tool_to_guide = {
            link["source"]
            for link in self.links
            if link["source"] in tool_routes and link["target"] not in tool_routes
        }
        guide_to_tool = {
            link["target"]
            for link in self.links
            if link["target"] in tool_routes and link["source"] not in tool_routes
        }
        self.assertEqual(tool_routes, tool_to_guide)
        self.assertEqual(tool_routes, tool_to_guide | guide_to_tool)
        self.assertEqual(tool_routes, guide_to_tool)

    def test_generated_tool_builders_preserve_contextual_links(self):
        builders = {
            "/tools-standing-order": ROOT / "scripts/build_standing_order.py",
            "/tools-field-reader": ROOT / "scripts/build_field_reader.py",
            "/tools-tendency-engine": ROOT / "scripts/build_tendency_engine.py",
            "/tools-coach-report": ROOT / "scripts/build_coach_report.py",
        }
        for route, builder in builders.items():
            source = builder.read_text(encoding="utf-8").lower()
            for link in self.links:
                if link["source"] != route:
                    continue
                self.assertIn(link["target"].lower(), source, builder.name)
                self.assertIn(link["anchor"].lower(), source, builder.name)

    def test_each_curated_guide_has_a_return_path_and_is_not_an_orphan(self):
        tool_routes = {tool["route"] for tool in self.inventory.TOOLS}
        guide_routes = {
            link["target"]
            for link in self.links
            if link["source"] in tool_routes and link["target"] not in tool_routes
        }
        self.assertTrue(guide_routes)
        for guide in guide_routes:
            self.assertGreaterEqual(self.by_target[guide], 1, guide)
            self.assertTrue(
                any(link["source"] == guide and link["target"] in tool_routes for link in self.links),
                guide,
            )

    def test_every_declared_contextual_link_is_present_once_on_its_source_page(self):
        for link in self.links:
            source = ROOT / link["source"].lstrip("/")
            if not source.suffix:
                source = source.with_suffix(".html")
            self.assertTrue(source.exists(), link["source"])
            source_links = page_links(source)
            target_matches = [
                href for href, _ in source_links if urlsplit(href).path.rstrip("/") == link["target"]
            ]
            self.assertEqual(1, len(target_matches), f"duplicate contextual target on {source.name}: {link}")
            matches = [
                (href, text)
                for href, text in source_links
                if urlsplit(href).path.rstrip("/") == link["target"]
                and link["anchor"].lower() in text.lower()
            ]
            self.assertEqual(1, len(matches), f"{source.name}: {link}")

    def test_declared_contextual_routes_resolve(self):
        for link in self.links:
            source = ROOT / link["source"].lstrip("/")
            if not source.suffix:
                source = source.with_suffix(".html")
            target = local_target(source, link["target"])
            self.assertIsNotNone(target, link["target"])

    def test_all_site_internal_links_resolve_or_use_a_configured_redirect(self):
        redirect_sources = {
            item["source"]
            for item in json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))["redirects"]
        }
        missing = []
        for source in site_html_files():
            for href, _ in page_links(source):
                parsed = urlsplit(href)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                if local_target(source, href) is None and parsed.path.rstrip("/") not in redirect_sources:
                    missing.append((source.name, href))
        self.assertEqual([], missing)


if __name__ == "__main__":
    unittest.main()
