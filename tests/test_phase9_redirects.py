#!/usr/bin/env python3
"""Regression checks for Phase 9 duplicate-route and redirect contracts."""

import json
import re
import unittest
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.golfraw.com"
NON_PRODUCTION_FILES = {"article-template.html", "404.html"}
NO_CANONICAL_FILES = {"pinterest-b7225cf07b728cc1691b9a4c7a938dbe.html"}

# These are the two remaining route findings confirmed by the Phase 9 audit.
EXPECTED_PHASE9_REDIRECTS = {
    "/news/2026-solheim-cup-rosters-finalized-captains-picks":
        "/2026-solheim-cup-rosters-finalized-captains-picks",
    "/courses/doonbeg-links-review-cost":
        "/news-2026-donald-trump-amgen-irish-open-doonbeg",
}


def redirect_rules():
    return json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))["redirects"]


def redirect_map():
    return {rule["source"]: rule for rule in redirect_rules()}


def site_html_files():
    return tuple(
        sorted(
            path
            for path in ROOT.glob("*.html")
            if path.name not in NON_PRODUCTION_FILES
        )
    ) + tuple(sorted((ROOT / "equipment").glob("*.html"))) + tuple(
        sorted((ROOT / "rules").glob("*.html"))
    )


def clean_route_for_file(path):
    relative = path.relative_to(ROOT).as_posix()
    return "/" if relative == "index.html" else "/" + relative[:-5]


def canonical_route(path):
    source = path.read_text(encoding="utf-8")
    match = re.search(
        r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)',
        source,
        re.IGNORECASE,
    )
    return urlsplit(match.group(1)).path if match else ""


def indexable(path):
    source = path.read_text(encoding="utf-8")
    return bool(canonical_route(path)) and not re.search(
        r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*noindex',
        source,
        re.IGNORECASE,
    )


def page_for_route(route):
    route = route.rstrip("/") or "/"
    return ROOT / "index.html" if route == "/" else ROOT / (route.lstrip("/") + ".html")


class HrefParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.hrefs.append(href)


def local_route_links(path):
    parser = HrefParser()
    parser.feed(path.read_text(encoding="utf-8"))
    for href in parser.hrefs:
        parsed = urlsplit(href)
        if parsed.scheme or parsed.netloc or not parsed.path or not parsed.path.startswith("/"):
            continue
        route = parsed.path.rstrip("/") or "/"
        if route.startswith(("/public/", "/api/")) or "." in route.rsplit("/", 1)[-1]:
            continue
        yield route


class Phase9RedirectTests(unittest.TestCase):
    def test_known_phase9_findings_have_verified_permanent_redirects(self):
        redirects = redirect_map()
        for source, destination in EXPECTED_PHASE9_REDIRECTS.items():
            self.assertIn(source, redirects)
            self.assertEqual(destination, redirects[source]["destination"])
            self.assertTrue(redirects[source]["permanent"])

    def test_redirect_sources_are_unique_and_permanent(self):
        rules = redirect_rules()
        sources = [rule.get("source") for rule in rules]
        self.assertEqual(len(sources), len(set(sources)))
        for rule in rules:
            self.assertTrue(rule.get("source"))
            self.assertTrue(rule.get("destination"))
            self.assertTrue(rule.get("permanent"))

    def test_all_redirects_resolve_directly_to_a_self_canonical_local_page(self):
        redirects = redirect_map()
        for source in redirects:
            current = source
            seen = set()
            while current in redirects:
                self.assertNotIn(current, seen, f"redirect loop at {current}")
                seen.add(current)
                current = redirects[current]["destination"]
            self.assertNotIn(current, seen, f"redirect chain loops at {current}")
            target = page_for_route(current)
            self.assertTrue(target.exists(), f"invalid redirect target: {source} -> {current}")
            self.assertTrue(indexable(target), f"redirect target is not indexable: {current}")
            self.assertEqual(current, canonical_route(target), source)
            self.assertEqual(current, redirects[source]["destination"], source)

    def test_noncanonical_local_pages_have_redirects_to_their_canonical_route(self):
        redirects = redirect_map()
        for path in site_html_files():
            if path.name in NO_CANONICAL_FILES or not indexable(path):
                continue
            local_route = clean_route_for_file(path)
            canonical = canonical_route(path)
            if canonical == local_route:
                continue
            self.assertIn(local_route, redirects, f"missing redirect for {path}")
            self.assertEqual(canonical, redirects[local_route]["destination"], path.name)

    def test_duplicate_canonical_groups_have_one_authoritative_route(self):
        by_canonical = defaultdict(list)
        for path in site_html_files():
            if path.name in NO_CANONICAL_FILES or not indexable(path):
                continue
            by_canonical[canonical_route(path)].append(path)
        redirects = redirect_map()
        for canonical, pages in by_canonical.items():
            if len(pages) < 2:
                continue
            self.assertTrue(any(clean_route_for_file(path) == canonical for path in pages), canonical)
            for path in pages:
                route = clean_route_for_file(path)
                if route == canonical:
                    continue
                self.assertIn(route, redirects, f"duplicate route is reachable without redirect: {route}")
                self.assertEqual(canonical, redirects[route]["destination"], route)

    def test_internal_local_route_variants_are_resolvable(self):
        redirects = redirect_map()
        missing = []
        for path in site_html_files():
            for route in local_route_links(path):
                if page_for_route(route).exists() or route in redirects:
                    continue
                missing.append(f"{path.name} -> {route}")
        self.assertEqual([], missing)

    def test_clean_urls_is_the_single_html_variant_policy(self):
        config = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
        self.assertTrue(config.get("cleanUrls"))
        self.assertFalse(config.get("trailingSlash"))
        for path in site_html_files():
            if path.name in NO_CANONICAL_FILES or not indexable(path):
                continue
            route = canonical_route(path)
            self.assertFalse(route.endswith(".html"), path.name)
            if route != "/":
                self.assertFalse(route.endswith("/"), path.name)


if __name__ == "__main__":
    unittest.main()
