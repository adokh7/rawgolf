#!/usr/bin/env python3
"""Regression contract for Phase 8 structured-data normalization."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

from scripts import tool_inventory as inventory
from scripts.schema_normalizer import (
    ARTICLE_ROUTES,
    JSON_LD_RE,
    extract_page_metadata,
    extract_visible_faq,
    walk,
)


ROOT = Path(__file__).resolve().parents[1]
PRO_ROUTE = "/pro"


def _read(route: str) -> str:
    path = ROOT / route.lstrip("/")
    if not path.exists():
        path = path.with_suffix(".html")
    return path.read_text(encoding="utf-8")


def _docs(source: str) -> list[object]:
    return [json.loads(match.group(2)) for match in JSON_LD_RE.finditer(source)]


def _nodes(source: str, schema_type: str | None = None) -> list[dict]:
    result = []
    for document in _docs(source):
        for node in walk(document):
            if not isinstance(node, dict):
                continue
            types = node.get("@type", [])
            types = [types] if isinstance(types, str) else types
            if schema_type is None or schema_type in types:
                result.append(node)
    return result


def _schema_faq(node: dict) -> list[tuple[str, str]]:
    pairs = []
    for question in node.get("mainEntity", []):
        answer = question.get("acceptedAnswer", {})
        pairs.append((question.get("name", ""), answer.get("text", "")))
    return pairs


class Phase8SchemaContractTests(unittest.TestCase):
    def test_tool_pages_have_one_consistent_schema_document(self):
        self.assertEqual(13, len(inventory.TOOLS))
        for tool in inventory.TOOLS:
            with self.subTest(tool=tool["slug"]):
                source = _read(tool["route"])
                docs = _docs(source)
                self.assertEqual(1, len(docs), "tool pages should not emit competing JSON-LD blocks")
                app = _nodes(source, "WebApplication")
                if not app:
                    app = _nodes(source, "SoftwareApplication")
                self.assertEqual(1, len(app))
                app = app[0]
                canonical = inventory.SITE + tool["route"]
                self.assertEqual(canonical + "#application", app.get("@id"))
                self.assertEqual(tool["name"], app.get("name"))
                self.assertEqual(canonical, app.get("url"))
                visible_h1 = extract_page_metadata(source)["h1"]
                if visible_h1 != tool["name"]:
                    self.assertEqual(visible_h1, app.get("alternateName"))
                self.assertEqual("SportsApplication", app.get("applicationCategory"))
                self.assertEqual("Any browser", app.get("operatingSystem"))
                self.assertEqual("Requires JavaScript", app.get("browserRequirements"))
                self.assertEqual(
                    extract_page_metadata(source)["description"],
                    app.get("description"),
                )
                self.assertNotIn("aggregateRating", app)
                self.assertNotIn("review", app)
                self.assertNotIn("priceValidUntil", app)
                if tool["access"] == "free":
                    self.assertTrue(app.get("isAccessibleForFree"))
                    self.assertEqual("0", app.get("offers", {}).get("price"))
                    self.assertEqual("USD", app.get("offers", {}).get("priceCurrency"))
                else:
                    self.assertNotIn("offers", app)
                    self.assertNotIn("price", json.dumps(app))

                breadcrumbs = _nodes(source, "BreadcrumbList")
                self.assertEqual(1, len(breadcrumbs))
                self.assertEqual(canonical + "#breadcrumb", breadcrumbs[0].get("@id"))
                items = breadcrumbs[0]["itemListElement"]
                self.assertEqual(
                    [inventory.SITE + "/", inventory.HUB_CANONICAL, canonical],
                    [item["item"] for item in items],
                )
                self.assertEqual(tool["search_name"], items[-1]["name"])

                faq = _nodes(source, "FAQPage")
                visible_faq = extract_visible_faq(source)
                self.assertEqual(bool(visible_faq), bool(faq))
                if faq:
                    self.assertEqual(1, len(faq))
                    self.assertEqual(visible_faq, _schema_faq(faq[0]))
                self.assertEqual([], _nodes(source, "HowTo"))

    def test_hub_schema_uses_the_authoritative_thirteen_tool_catalog(self):
        source = _read("/tools")
        self.assertEqual(1, len(_docs(source)))
        collection = _nodes(source, "CollectionPage")
        self.assertEqual(1, len(collection))
        collection = collection[0]
        self.assertEqual(inventory.HUB_CANONICAL + "#webpage", collection.get("@id"))
        self.assertEqual("GolfRaw Tools Suite", collection.get("name"))
        self.assertEqual(inventory.HUB_DESCRIPTION, collection.get("description"))
        item_list = collection["mainEntity"]
        self.assertEqual("ItemList", item_list["@type"])
        self.assertEqual(13, item_list["numberOfItems"])
        self.assertEqual(13, len(item_list["itemListElement"]))
        for tool, list_item in zip(inventory.TOOLS, item_list["itemListElement"]):
            app = list_item["item"]
            with self.subTest(tool=tool["slug"]):
                self.assertEqual(tool["name"], app["name"])
                self.assertEqual(tool["description"], app["description"])
                self.assertEqual(inventory.SITE + tool["route"], app["url"])
                self.assertEqual("SportsApplication", app["applicationCategory"])
                self.assertNotIn("priceValidUntil", app)
                if tool["access"] == "free":
                    self.assertEqual("0", app["offers"]["price"])
                else:
                    self.assertNotIn("offers", app)

    def test_pro_schema_describes_verified_features_without_an_offer(self):
        source = _read(PRO_ROUTE)
        self.assertEqual(1, len(_docs(source)))
        app = _nodes(source, "SoftwareApplication")
        self.assertEqual(1, len(app))
        app = app[0]
        pro = inventory.PRODUCT_MODEL["pro"]
        self.assertEqual(inventory.SITE + pro["route"] + "#product", app["@id"])
        self.assertEqual(pro["label"], app["name"])
        self.assertEqual(
            [feature["label"] + ": " + feature["summary"] for feature in pro["features"]],
            app["featureList"],
        )
        self.assertNotIn("offers", app)
        self.assertNotIn("price", json.dumps(app))
        page = _nodes(source, "WebPage")
        self.assertEqual(1, len(page))
        self.assertEqual({"@id": app["@id"]}, page[0]["mainEntity"])

    def test_selected_articles_have_complete_canonical_article_contract(self):
        self.assertIn("/amateur-tournament-guide", ARTICLE_ROUTES)
        for route in ARTICLE_ROUTES:
            with self.subTest(route=route):
                source = _read(route)
                self.assertGreaterEqual(len(_docs(source)), 1)
                articles = _nodes(source)
                articles = [
                    node for node in articles
                    if set(node.get("@type", []) if isinstance(node.get("@type"), list) else [node.get("@type")])
                    & {"Article", "NewsArticle"}
                ]
                self.assertEqual(1, len(articles))
                article = articles[0]
                canonical = inventory.SITE + route
                for field in ("headline", "image", "datePublished", "author", "publisher", "mainEntityOfPage", "articleSection"):
                    self.assertTrue(article.get(field), field)
                self.assertEqual(canonical, article["mainEntityOfPage"]["@id"] if isinstance(article["mainEntityOfPage"], dict) else article["mainEntityOfPage"])
                image_value = article["image"]
                if isinstance(image_value, list):
                    image_value = image_value[0] if image_value else ""
                image_url = image_value.get("url") if isinstance(image_value, dict) else image_value
                self.assertTrue(str(image_url).startswith("https://"))
                self.assertRegex(article["datePublished"], r"^\d{4}-\d{2}-\d{2}")
                if article.get("dateModified"):
                    self.assertRegex(article["dateModified"], r"^\d{4}-\d{2}-\d{2}")
                if route == "/how-long-do-golf-clubs-last":
                    self.assertEqual(["GEAR", "GUIDES"], article["articleSection"])
                breadcrumbs = _nodes(source, "BreadcrumbList")
                self.assertEqual(1, len(breadcrumbs))
                self.assertEqual(canonical + "#breadcrumb", breadcrumbs[0].get("@id"))
                self.assertEqual(canonical, breadcrumbs[0]["itemListElement"][-1]["item"])

    def test_entity_ids_are_unique_and_canonical(self):
        routes = ["/tools", PRO_ROUTE, *[tool["route"] for tool in inventory.TOOLS], *ARTICLE_ROUTES]
        for route in routes:
            with self.subTest(route=route):
                ids = [
                    node["@id"]
                    for node in _nodes(_read(route))
                    if node.get("@id") and node.get("@type")
                ]
                self.assertEqual(len(ids), len(set(ids)))
                for entity_id in ids:
                    self.assertTrue(entity_id.startswith(inventory.SITE + "/") or entity_id == inventory.SITE + "#organization")

    def test_selected_article_faq_is_current_when_present(self):
        for route in ARTICLE_ROUTES:
            source = _read(route)
            visible = extract_visible_faq(source)
            faq = _nodes(source, "FAQPage")
            if not faq:
                continue
            with self.subTest(route=route):
                self.assertEqual(1, len(faq))
                self.assertEqual(visible, _schema_faq(faq[0]))

    def test_normalization_is_idempotent_and_does_not_touch_page_body(self):
        from scripts.schema_normalizer import normalize_phase8_page

        for route in ("/tools", PRO_ROUTE, "/tools-coach-report", ARTICLE_ROUTES[0]):
            source = _read(route)
            normalized = normalize_phase8_page(source, route)
            self.assertEqual(normalized, normalize_phase8_page(normalized, route))
            self.assertEqual(
                JSON_LD_RE.sub("", source),
                JSON_LD_RE.sub("", normalized),
            )

    def test_generated_tool_builders_use_the_normalizer(self):
        for name in ("build_tendency_engine.py", "build_standing_order.py", "build_field_reader.py", "build_coach_report.py"):
            with self.subTest(builder=name):
                source = (ROOT / "scripts" / name).read_text(encoding="utf-8")
                self.assertIn("normalize_tool_page", source)

    def test_phase8_check_command_passes_after_normalization(self):
        result = subprocess.run(
            [sys.executable, "scripts/normalize_phase8_schema.py", "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
