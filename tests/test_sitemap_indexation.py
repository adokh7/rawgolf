import json
import re
import shutil
import subprocess
import tempfile
import unittest
from collections import Counter
from html import unescape
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.golfraw.com"
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
NON_PRODUCTION_FILES = {"article-template.html", "404.html"}
TASK_2_ALIASES = {
    "/blog/morikawa-61-travelers-championship-2026",
    "/golf-deals-equipment-tee-times-guide",
    "/golf-tournaments-rules-formats-tax-guide",
}


def route_for(path):
    relative = path.relative_to(ROOT).as_posix()
    return "/" if relative == "index.html" else "/" + relative[:-5]


def html_files(root=ROOT):
    files = []
    for path in root.rglob("*.html"):
        relative = path.relative_to(root)
        if any(part.startswith(".") or part in {"node_modules", "public"} for part in relative.parts):
            continue
        if path.name in NON_PRODUCTION_FILES:
            continue
        files.append(path)
    return sorted(files)


def attr(tag, name):
    match = re.search(rf"\b{name}\s*=\s*([\"'])(.*?)\1", tag, re.I | re.S)
    return unescape(match.group(2)).strip() if match else ""


def meta_values(source, key):
    values = []
    for tag in re.findall(r"<meta\b[^>]*>", source, re.I):
        if attr(tag, "property").lower() == key.lower():
            values.append(attr(tag, "content"))
    return values


def jsonld_values(source, key):
    return re.findall(rf'"{key}"\s*:\s*"([^\"]+)"', source)


def normalize_date(value):
    match = re.match(r"^(\d{4}-\d{2}-\d{2})", value or "")
    return match.group(1) if match else ""


def reliable_lastmod(path):
    source = path.read_text(encoding="utf-8")
    modified = meta_values(source, "article:modified_time") + jsonld_values(source, "dateModified")
    published = meta_values(source, "article:published_time") + jsonld_values(source, "datePublished")
    for candidates in (modified, published):
        normalized = [normalize_date(value) for value in candidates]
        if not candidates:
            continue
        if not all(normalized) or len(set(normalized)) != 1:
            return ""
        return normalized[0]
    return ""


def canonical(path):
    source = path.read_text(encoding="utf-8")
    for tag in re.findall(r"<link\b[^>]*>", source, re.I):
        if "canonical" in {part.lower() for part in attr(tag, "rel").split()}:
            return urlsplit(attr(tag, "href")).path or "/"
    return ""


def canonical_href(path):
    source = path.read_text(encoding="utf-8")
    for tag in re.findall(r"<link\b[^>]*>", source, re.I):
        if "canonical" in {part.lower() for part in attr(tag, "rel").split()}:
            return attr(tag, "href")
    return ""


def robots(path):
    source = path.read_text(encoding="utf-8")
    for tag in re.findall(r"<meta\b[^>]*>", source, re.I):
        if attr(tag, "name").lower() == "robots":
            return attr(tag, "content").lower()
    return ""


def production_indexable_routes(root=ROOT):
    routes = {}
    for path in html_files(root):
        relative = path.relative_to(root).as_posix()
        route = "/" if relative == "index.html" else "/" + relative[:-5]
        if "noindex" in robots(path):
            continue
        if canonical(path) != route:
            continue
        routes[route] = path
    redirects = {item["source"] for item in json.loads((root / "vercel.json").read_text())["redirects"]}
    return {route: path for route, path in routes.items() if route not in redirects}


def sitemap_entries(path=ROOT / "sitemap.xml"):
    root = ElementTree.parse(path).getroot()
    entries = []
    for node in root.findall("sm:url", SITEMAP_NS):
        loc = node.findtext("sm:loc", "", SITEMAP_NS)
        entries.append(
            {
                "path": urlsplit(loc).path or "/",
                "lastmod": node.findtext("sm:lastmod", "", SITEMAP_NS),
            }
        )
    return entries


class SitemapIndexationTests(unittest.TestCase):
    def test_sitemap_has_unique_locations(self):
        paths = [entry["path"] for entry in sitemap_entries()]
        duplicates = {path: count for path, count in Counter(paths).items() if count > 1}
        self.assertEqual({}, duplicates)

    def test_sitemap_matches_all_indexable_self_canonical_production_routes(self):
        sitemap_paths = {entry["path"] for entry in sitemap_entries()}
        expected_paths = set(production_indexable_routes())
        self.assertEqual(expected_paths, sitemap_paths)

    def test_sitemap_excludes_redirects_template_and_task_2_aliases(self):
        paths = {entry["path"] for entry in sitemap_entries()}
        redirects = {item["source"] for item in json.loads((ROOT / "vercel.json").read_text())["redirects"]}
        self.assertNotIn("/article-template", paths)
        self.assertTrue(redirects.isdisjoint(paths))
        self.assertTrue(TASK_2_ALIASES.isdisjoint(paths))

    def test_each_sitemap_page_is_local_indexable_and_self_canonical(self):
        inventory = production_indexable_routes()
        for entry in sitemap_entries():
            self.assertIn(entry["path"], inventory)
            self.assertEqual(entry["path"], canonical(inventory[entry["path"]]))
            self.assertEqual(BASE + entry["path"], canonical_href(inventory[entry["path"]]))
            self.assertNotIn("noindex", robots(inventory[entry["path"]]))

    def test_lastmod_uses_page_dates_and_omits_unreliable_values(self):
        entries = {entry["path"]: entry["lastmod"] for entry in sitemap_entries()}
        for path, page in production_indexable_routes().items():
            expected = reliable_lastmod(page)
            if path in entries:
                self.assertEqual(expected, entries[path], path)
        self.assertEqual("2026-08-11", entries["/news-2026-liv-golf-bedminster-crushers-six-over-par"])
        self.assertEqual("2026-08-26", entries["/liv-golf-pga-tour-return"])
        self.assertEqual("", entries["/news-2026-wyndham-championship-odds-day-bradley"])
        self.assertEqual("", entries["/"])

    def test_fresh_generator_recreates_the_checked_in_sitemap_contract(self):
        import sys

        sys.path.insert(0, str(ROOT))
        import scripts.sync_site as sync_site

        with tempfile.TemporaryDirectory(prefix="sitemap-generator-") as temporary:
            temporary_root = Path(temporary)
            for path in html_files():
                destination = temporary_root / path.relative_to(ROOT)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, destination)
            for name in ("articles.json", "vercel.json"):
                shutil.copy2(ROOT / name, temporary_root / name)

            original_root = sync_site.ROOT
            try:
                sync_site.ROOT = str(temporary_root)
                sync_site.write_sitemap(sync_site.load())
            finally:
                sync_site.ROOT = original_root

            generated = sitemap_entries(temporary_root / "sitemap.xml")
            self.assertEqual(sitemap_entries(), generated)


if __name__ == "__main__":
    unittest.main()
