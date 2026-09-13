"""Regression checks for the Phase 5 reusable in-article Tool CTA system."""

import html
import importlib
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSS_PATH = ROOT / "public" / "tool-cta.css"


class CtaParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ctas = []
        self._cta = None
        self._depth = 0
        self._capture_id = None
        self._capture = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self._cta is not None:
            self._depth += 1
        if tag == "aside" and "data-tool-cta" in attrs:
            self._cta = {
                "attrs": attrs,
                "tags": [],
                "text": {},
                "links": [],
                "badges": [],
            }
            self._depth = 0
        elif self._cta is not None:
            self._cta["tags"].append(tag)
            if tag == "h3":
                self._capture_id = attrs.get("id")
                self._capture = []
            elif tag == "a":
                self._cta["links"].append(attrs)
            if "tool-cta__badge" in attrs.get("class", "").split():
                self._capture_id = "badge"
                self._capture = []

    def handle_data(self, data):
        if self._cta is not None and self._capture_id:
            self._capture.append(data)

    def handle_endtag(self, tag):
        if self._cta is None:
            return
        if self._capture_id and tag in {"h3", "span"}:
            self._cta["text"][self._capture_id] = " ".join("".join(self._capture).split())
            if self._capture_id == "badge":
                self._cta["badges"].append(self._cta["text"][self._capture_id])
            self._capture_id = None
            self._capture = []
        if tag == "aside":
            self.ctas.append(self._cta)
            self._cta = None
            self._depth = 0
        elif self._depth:
            self._depth -= 1


def parse_ctas(path):
    parser = CtaParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.ctas


class Phase5ToolCtaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cta = importlib.import_module("scripts.tool_cta")
        cls.inventory = importlib.import_module("scripts.tool_inventory")
        cls.phase4 = importlib.import_module("scripts.internal_link_map")

    def test_cta_config_uses_valid_tool_ids_and_all_supported_variants(self):
        tools = {tool["slug"]: tool for tool in self.inventory.TOOLS}
        configs = self.cta.ARTICLE_TOOL_CTAS
        self.assertEqual(14, len(configs))
        self.assertEqual({"inline", "card", "banner"}, {item["variant"] for item in configs.values()})
        self.assertEqual(len(configs), len({(route, item["tool_id"]) for route, item in configs.items()}))
        for route, item in configs.items():
            self.assertTrue((ROOT / f"{route.lstrip('/')}.html").exists(), route)
            self.assertIn(item["tool_id"], tools)
            self.assertTrue(item["anchor"].strip())

    def test_badges_hooks_and_destinations_come_from_inventory(self):
        tools = {tool["slug"]: tool for tool in self.inventory.TOOLS}
        for route, config in self.cta.ARTICLE_TOOL_CTAS.items():
            tool = tools[config["tool_id"]]
            rendered = self.cta.render_tool_cta(route, config)
            badge = "FREE" if tool["access"] == "free" else "PRO"
            self.assertIn(f'data-tool-id="{html.escape(tool["slug"])}"', rendered)
            self.assertIn(f'href="{html.escape(tool["route"])}"', rendered)
            self.assertIn(html.escape(tool["name"]), rendered)
            self.assertIn(f">{badge}</span>", rendered)
            self.assertIn(html.escape(config["anchor"]), rendered)
            self.assertIn(self.cta.first_sentence(tool["description"]), rendered)

    def test_cta_destinations_are_phase4_relevant_guide_to_tool_pairs(self):
        pairs = {
            (item["source"], item["target"])
            for item in self.phase4.CONTEXTUAL_LINKS
            if item["direction"] == "guide_to_tool"
        }
        for route, config in self.cta.ARTICLE_TOOL_CTAS.items():
            tool = next(tool for tool in self.inventory.TOOLS if tool["slug"] == config["tool_id"])
            self.assertIn((route, tool["route"]), pairs, route)

    def test_rendered_ctas_have_accessible_landmark_heading_and_link(self):
        for route in self.cta.ARTICLE_TOOL_CTAS:
            ctas = parse_ctas(ROOT / f"{route.lstrip('/')}.html")
            self.assertEqual(1, len(ctas), route)
            cta = ctas[0]
            labelled_by = cta["attrs"].get("aria-labelledby")
            self.assertTrue(labelled_by, route)
            self.assertIn(labelled_by, cta["text"], route)
            self.assertTrue(cta["text"][labelled_by], route)
            self.assertEqual(1, len(cta["links"]), route)
            self.assertTrue(cta["links"][0].get("href"), route)
            self.assertTrue(cta["badges"], route)
            self.assertRegex(cta["badges"][0], r"^(FREE|PRO)$")

    def test_checked_in_ctas_match_inventory_access_routes_and_copy(self):
        tools = {tool["slug"]: tool for tool in self.inventory.TOOLS}
        for route, config in self.cta.ARTICLE_TOOL_CTAS.items():
            tool = tools[config["tool_id"]]
            path = ROOT / f"{route.lstrip('/')}.html"
            source = path.read_text(encoding="utf-8")
            cta = parse_ctas(path)[0]
            classes = cta["attrs"].get("class", "").split()
            self.assertIn(f"tool-cta--{config['variant']}", classes, route)
            self.assertEqual(tool["slug"], cta["attrs"].get("data-tool-id"), route)
            self.assertEqual(tool["access"], cta["attrs"].get("data-access"), route)
            self.assertIn(f'href="{html.escape(tool["route"])}">{html.escape(config["anchor"])}', source)

    def test_injector_is_idempotent_and_does_not_duplicate_ctas(self):
        route = "/golf-clubs-for-beginners"
        config = self.cta.ARTICLE_TOOL_CTAS[route]
        source = (
            '<html><head></head><body><main><div class="wrap page-grid">'
            '<article><div class="article-body"><nav class="tag-row" aria-label="Article tags"></nav>'
            "</div></article></div></main></body></html>"
        )
        once = self.cta.inject_content(source, route, config)
        twice = self.cta.inject_content(once, route, config)
        self.assertEqual(once, twice)
        self.assertEqual(1, once.count("data-tool-cta"))
        self.assertEqual(1, once.count(self.cta.STYLESHEET_LINK))

    def test_stylesheet_has_lightweight_responsive_accessible_contract(self):
        self.assertTrue(CSS_PATH.exists())
        css = CSS_PATH.read_text(encoding="utf-8") if CSS_PATH.exists() else ""
        for needle in (".tool-cta", "@media", ":focus-visible", "prefers-reduced-motion", "min-height: 44px"):
            self.assertIn(needle, css)

    def test_cta_injection_is_scoped_to_curated_guides(self):
        expected = {
            f"{route.lstrip('/')}.html" for route in self.cta.ARTICLE_TOOL_CTAS
        }
        actual = {
            path.name
            for path in ROOT.glob("*.html")
            if "data-tool-cta" in path.read_text(encoding="utf-8")
        }
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
