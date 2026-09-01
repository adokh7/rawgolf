import re
import sys
import unittest
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.golfraw.com"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
NEWS_NS = "http://www.google.com/schemas/sitemap-news/0.9"
sys.path.insert(0, str(ROOT))
from scripts.sync_site import load, news_article_records


def xml_root(path):
    return ElementTree.parse(path).getroot()


def entries(path):
    root = xml_root(path)
    return root.findall(f"{{{SITEMAP_NS}}}url")


def route_from_node(node):
    loc = node.findtext(f"{{{SITEMAP_NS}}}loc", "")
    return urlsplit(loc).path or "/"


class StandardSitemapRegressionTests(unittest.TestCase):
    def test_lastmod_is_omitted_when_only_publication_metadata_exists(self):
        nodes = {route_from_node(node): node for node in entries(ROOT / "sitemap.xml")}
        lastmod = nodes["/golf-swing-drills"].findtext(
            f"{{{SITEMAP_NS}}}lastmod", ""
        )
        self.assertEqual("", lastmod)

    def test_standard_sitemap_does_not_emit_ignored_change_frequency_or_priority(self):
        source = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        self.assertNotRegex(source, r"<(?:changefreq|priority)>")


class NewsSitemapRegressionTests(unittest.TestCase):
    def test_news_window_excludes_future_articles_and_stops_at_two_days(self):
        records = news_article_records(load(), today=date(2026, 8, 31))
        routes = {record["route"] for record in records}
        self.assertNotIn("/news-2026-justin-thomas-mental-capacity-bay-hill", routes)
        self.assertIn("/news-2026-liv-golf-bankruptcy-player-settlements-deadlock", routes)
        self.assertNotIn("/news-2026-end-of-season-driver-deals", routes)
        for record in records:
            self.assertIn(record["publication_date"][:10], {"2026-08-29", "2026-08-30", "2026-08-31"})

    def test_news_sitemap_is_present_and_uses_required_namespace(self):
        path = ROOT / "news-sitemap.xml"
        self.assertTrue(path.is_file(), path)
        root = xml_root(path)
        self.assertEqual(f"{{{SITEMAP_NS}}}urlset", root.tag)
        self.assertTrue(root.findall(f".//{{{NEWS_NS}}}news"))

    def test_news_sitemap_contains_only_recent_news_section_articles(self):
        path = ROOT / "news-sitemap.xml"
        self.assertTrue(path.is_file(), path)
        nodes = entries(path)
        routes = [route_from_node(node) for node in nodes]
        self.assertEqual([], [route for route, count in Counter(routes).items() if count > 1])
        self.assertNotIn("/news-2026-end-of-season-driver-deals", routes)
        self.assertNotIn("/news-every-shot-tiger-woods-80th-win-2018", routes)
        self.assertIn("/news-2026-justin-thomas-mental-capacity-bay-hill", routes)
        self.assertIn("/news-2026-liv-golf-bankruptcy-player-settlements-deadlock", routes)
        self.assertLessEqual(len(nodes), 1000)

        for node in nodes:
            loc = node.findtext(f"{{{SITEMAP_NS}}}loc", "")
            self.assertTrue(loc.startswith(BASE + "/"), loc)
            news = node.find(f"{{{NEWS_NS}}}news")
            publication = news.find(f"{{{NEWS_NS}}}publication")
            self.assertEqual("GOLFRAW", publication.findtext(f"{{{NEWS_NS}}}name"))
            self.assertEqual("en", publication.findtext(f"{{{NEWS_NS}}}language"))
            publication_date = news.findtext(f"{{{NEWS_NS}}}publication_date", "")
            self.assertRegex(publication_date, r"^2026-(08-(30|31)|09-01)T")
            title = news.findtext(f"{{{NEWS_NS}}}title", "")
            self.assertTrue(title)
            self.assertNotRegex(title, r"\s\|\sGOLFRAW$")

    def test_news_sitemap_publication_dates_are_real_page_dates(self):
        path = ROOT / "news-sitemap.xml"
        self.assertTrue(path.is_file(), path)
        root = xml_root(path)
        expected = {
            "/news-2026-justin-thomas-mental-capacity-bay-hill": "2026-09-01T10:00:00+02:00",
            "/news-2026-jon-rahm-liv-money-owed": "2026-09-01T21:30:00+02:00",
            "/news-2026-liv-golf-bankruptcy-player-settlements-deadlock": "2026-08-31T15:00:00+02:00",
        }
        actual = {}
        for node in root.findall(f"{{{SITEMAP_NS}}}url"):
            route = route_from_node(node)
            news = node.find(f"{{{NEWS_NS}}}news")
            actual[route] = news.findtext(f"{{{NEWS_NS}}}publication_date", "")
        for route, publication_date in expected.items():
            self.assertEqual(publication_date, actual[route])

    def test_robots_references_standard_and_news_sitemaps(self):
        robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
        self.assertIn("Sitemap: https://www.golfraw.com/sitemap.xml", robots)
        self.assertIn("Sitemap: https://www.golfraw.com/news-sitemap.xml", robots)


if __name__ == "__main__":
    unittest.main()
