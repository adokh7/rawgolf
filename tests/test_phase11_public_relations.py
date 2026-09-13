import csv
import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.golfraw.com"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
REQUIRED_ASSET_ROUTES = {
    "/tools",
    "/tools-standing-order",
    "/ratings-manual",
    "/corrections",
    "/about",
    "/pro",
    "/golf-swing-drills",
    "/swing-speed-guide",
    "/golf-clubs-for-beginners",
    "/rules/golf-tournaments-rules-formats-tax-guide",
    "/equipment/golf-deals-equipment-tee-times-guide",
}


def local_route(path):
    return "/" if path == ROOT / "index.html" else "/" + path.relative_to(ROOT).as_posix()[:-5]


def path_for_route(route):
    if route == "/":
        return ROOT / "index.html"
    return ROOT / (route.lstrip("/") + ".html")


class Phase11PressPageTests(unittest.TestCase):
    def test_press_page_exists_with_indexable_canonical_and_verified_contact_path(self):
        path = ROOT / "press.html"
        self.assertTrue(path.is_file(), path)
        source = path.read_text(encoding="utf-8")
        self.assertRegex(source, r"<title>Press &amp; Media \| GolfRaw</title>")
        self.assertIn('<link rel="canonical" href="https://www.golfraw.com/press">', source)
        self.assertRegex(source, r'<meta name="robots" content="index, follow[^>]*>')
        self.assertIn("13 tools", source)
        self.assertIn("12 Free tools", source)
        self.assertIn("Coach Report Pro preview", source)
        self.assertIn("GolfRaw Editorial", source)
        self.assertIn('href="/ratings-manual"', source)
        self.assertIn('href="/corrections"', source)
        self.assertIn('href="mailto:contact@golfraw.com"', source)

    def test_press_page_does_not_make_unverified_product_or_authority_claims(self):
        source = (ROOT / "press.html").read_text(encoding="utf-8").lower()
        for phrase in ("history sync", "advanced modelling", "advanced modeling", "pricing", "guaranteed", "award-winning", "revolutionary"):
            self.assertNotIn(phrase, source)

    def test_press_links_resolve_to_existing_canonical_pages(self):
        source = (ROOT / "press.html").read_text(encoding="utf-8")
        routes = {
            urlsplit(href).path
            for href in re.findall(r'\bhref=["\']([^"\']+)', source)
            if href.startswith("/") and not href.startswith("//")
        }
        for route in routes:
            # static assets: anything under /public/, plus the root-served brand
            # files (favicons, apple-touch-icon, manifest) Google expects at /
            if route.startswith("/public/") or Path(route).suffix:
                self.assertTrue((ROOT / route.lstrip("/")).is_file(), route)
                continue
            if route in {"/press"}:
                path = ROOT / "press.html"
            else:
                path = path_for_route(route)
            self.assertTrue(path.is_file(), route)
            page = path.read_text(encoding="utf-8")
            self.assertIn(f'<link rel="canonical" href="{BASE}{route}">', page, route)

    def test_press_page_is_in_the_standard_sitemap(self):
        root = ElementTree.parse(ROOT / "sitemap.xml").getroot()
        routes = {
            urlsplit(node.findtext(f"{{{SITEMAP_NS}}}loc", "")).path
            for node in root.findall(f"{{{SITEMAP_NS}}}url")
        }
        self.assertIn("/press", routes)


class Phase11AssetRegistryTests(unittest.TestCase):
    def test_linkable_asset_registry_uses_existing_routes_and_verified_claims(self):
        path = ROOT / "docs" / "pr" / "linkable-assets.json"
        self.assertTrue(path.is_file(), path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual("2026-09-13", payload["verified_on"])
        assets = payload["assets"]
        self.assertGreaterEqual(len(assets), 8)
        routes = {asset["route"] for asset in assets}
        self.assertTrue(REQUIRED_ASSET_ROUTES.issubset(routes))
        for asset in assets:
            self.assertTrue(asset["id"])
            self.assertTrue(asset["type"])
            self.assertTrue(asset["link_reason"])
            self.assertTrue(asset["pitch_angles"])
            route = asset["route"]
            path = path_for_route(route)
            self.assertTrue(path.is_file(), route)
            source = path.read_text(encoding="utf-8")
            self.assertIn(f'<link rel="canonical" href="{BASE}{route}">', source, route)

    def test_prospecting_framework_contains_relevant_categories_and_earned_link_guardrails(self):
        path = ROOT / "docs" / "pr" / "README.md"
        self.assertTrue(path.is_file(), path)
        source = path.read_text(encoding="utf-8").lower()
        for category in (
            "golf media",
            "golf newsletters",
            "equipment publications",
            "amateur golf organizations",
            "data/sports journalists",
            "course/travel publications",
        ):
            self.assertIn(category, source)
        for guardrail in ("paid-link", "link exchange", "pbn", "mass directory", "do not send"):
            self.assertIn(guardrail, source)


class Phase11TrackingTests(unittest.TestCase):
    def test_prospect_tracker_has_required_operational_columns(self):
        path = ROOT / "docs" / "pr" / "prospect-tracker.csv"
        self.assertTrue(path.is_file(), path)
        with path.open(newline="", encoding="utf-8") as handle:
            columns = next(csv.reader(handle))
        for column in (
            "target",
            "contact_or_source",
            "pitch_angle",
            "linked_asset",
            "status",
            "response",
            "acquired_link_or_mention",
        ):
            self.assertIn(column, columns)
        self.assertEqual(len(columns), len(set(columns)))


if __name__ == "__main__":
    unittest.main()
