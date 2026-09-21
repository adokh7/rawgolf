import json
import re
import sys
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.golfraw.com"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
NEWS_NS = "http://www.google.com/schemas/sitemap-news/0.9"
sys.path.insert(0, str(ROOT))
from scripts import tool_inventory
from scripts import sync_site


def sitemap_nodes(path):
    return ElementTree.parse(path).getroot().findall(f"{{{SITEMAP_NS}}}url")


def route_from_node(node):
    loc = node.findtext(f"{{{SITEMAP_NS}}}loc", "")
    return urlsplit(loc).path or "/"


def redirect_sources():
    config = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
    return {item["source"] for item in config["redirects"]}


def page_inventory():
    return {
        route: Path(path)
        for route, path in sync_site.production_html_pages()
    }


class Phase10SitemapTests(unittest.TestCase):
    def test_standard_sitemap_is_canonical_only_and_redirect_free(self):
        nodes = sitemap_nodes(ROOT / "sitemap.xml")
        routes = [route_from_node(node) for node in nodes]
        inventory = page_inventory()
        redirects = redirect_sources()

        self.assertEqual(len(routes), len(set(routes)))
        self.assertEqual(set(sync_site.sitemap_page_records()), set(routes))
        self.assertTrue(redirects.isdisjoint(routes))
        self.assertNotIn("/article-template", routes)

        for node in nodes:
            loc = node.findtext(f"{{{SITEMAP_NS}}}loc", "")
            parsed = urlsplit(loc)
            self.assertEqual(BASE, f"{parsed.scheme}://{parsed.netloc}")
            self.assertEqual("", parsed.query)
            self.assertEqual("", parsed.fragment)
            self.assertNotIn(".html", parsed.path)
            self.assertTrue(parsed.path == "/" or not parsed.path.endswith("/"))
            self.assertIn(parsed.path, inventory)
            metadata = sync_site.page_metadata(inventory[parsed.path])
            self.assertEqual(loc, metadata.canonical)
            self.assertNotIn("noindex", ",".join(metadata.meta.get("robots", [])).lower())

    def test_standard_sitemap_does_not_emit_deprecated_priority_or_changefreq(self):
        source = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        self.assertNotRegex(source, r"<(?:priority|changefreq)>")

    def test_standard_sitemap_lastmod_is_valid_and_page_owned(self):
        inventory = page_inventory()
        for node in sitemap_nodes(ROOT / "sitemap.xml"):
            route = route_from_node(node)
            value = node.findtext(f"{{{SITEMAP_NS}}}lastmod", "")
            if not value:
                continue
            parsed = date.fromisoformat(value)
            self.assertLessEqual(parsed, date.today(), route)
            self.assertEqual(sync_site.reliable_lastmod(inventory[route]), value, route)

    def test_root_is_the_only_authoritative_indexing_artifact_location(self):
        self.assertFalse((ROOT / "public" / "sitemap.xml").exists())
        self.assertFalse((ROOT / "public" / "robots.txt").exists())


class Phase10NewsSitemapTests(unittest.TestCase):
    def test_news_sitemap_matches_the_truthful_current_two_day_window(self):
        path = ROOT / "news-sitemap.xml"
        nodes = sitemap_nodes(path)
        actual = {}
        for node in nodes:
            route = route_from_node(node)
            news = node.find(f"{{{NEWS_NS}}}news")
            actual[route] = {
                "publication_date": news.findtext(f"{{{NEWS_NS}}}publication_date", ""),
                "title": news.findtext(f"{{{NEWS_NS}}}title", ""),
            }

        expected = {
            record["route"]: record
            for record in sync_site.news_article_records(sync_site.load(), today=date.today())
        }
        self.assertEqual(set(expected), set(actual))
        for route, record in expected.items():
            self.assertEqual(record["publication_date"], actual[route]["publication_date"])
            self.assertEqual(record["title"], actual[route]["title"])

    def test_news_sitemap_entries_are_unique_recent_canonical_news_pages(self):
        standard_routes = {route_from_node(node) for node in sitemap_nodes(ROOT / "sitemap.xml")}
        redirects = redirect_sources()
        routes = []
        for node in sitemap_nodes(ROOT / "news-sitemap.xml"):
            route = route_from_node(node)
            routes.append(route)
            self.assertIn(route, standard_routes)
            self.assertNotIn(route, redirects)
            news = node.find(f"{{{NEWS_NS}}}news")
            self.assertIsNotNone(news)
            publication_date = news.findtext(f"{{{NEWS_NS}}}publication_date", "")
            parsed = datetime.fromisoformat(publication_date.replace("Z", "+00:00"))
            self.assertGreaterEqual(parsed.date(), date.today() - timedelta(days=2))
            self.assertLessEqual(parsed.date(), date.today())
            self.assertTrue(news.findtext(f"{{{NEWS_NS}}}title", "").strip())

        self.assertEqual(len(routes), len(set(routes)))
        self.assertLessEqual(len(routes), 1000)


class Phase10RobotsAndIndexabilityTests(unittest.TestCase):
    def test_robots_allows_public_crawl_and_references_root_sitemaps(self):
        source = (ROOT / "robots.txt").read_text(encoding="utf-8")
        self.assertRegex(source, r"(?m)^User-agent:\s*\*\s*$")
        self.assertRegex(source, r"(?m)^Allow:\s*/\s*$")
        self.assertNotRegex(source, r"(?m)^Disallow:\s*/\s*$")
        self.assertNotRegex(source, r"(?im)^User-agent:\s*(?:GPTBot|ChatGPT-User|ClaudeBot|PerplexityBot|Google-Extended|CCBot)\s*$")

        expected = {
            "Sitemap: https://www.golfraw.com/sitemap.xml",
            "Sitemap: https://www.golfraw.com/news-sitemap.xml",
        }
        actual = {line.strip() for line in source.splitlines() if line.startswith("Sitemap:")}
        self.assertEqual(expected, actual)
        for line in expected:
            self.assertTrue((ROOT / urlsplit(line.split(": ", 1)[1]).path.lstrip("/")).exists())

    def test_pro_and_all_fourteen_tools_are_indexable_self_canonical_and_sitemapped(self):
        inventory = page_inventory()
        sitemap_routes = {route_from_node(node) for node in sitemap_nodes(ROOT / "sitemap.xml")}
        required = {"/tools", "/pro", *(tool["route"] for tool in tool_inventory.TOOLS)}

        self.assertEqual(16, len(required))
        for route in required:
            self.assertIn(route, inventory, route)
            self.assertIn(route, sitemap_routes, route)
            metadata = sync_site.page_metadata(inventory[route])
            self.assertEqual(BASE + route, metadata.canonical, route)
            self.assertNotIn("noindex", ",".join(metadata.meta.get("robots", [])).lower(), route)


if __name__ == "__main__":
    unittest.main()
