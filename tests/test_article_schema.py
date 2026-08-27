#!/usr/bin/env python3
"""Regression checks for structured data on registered article pages."""

import json
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class JsonLdParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._capturing = False
        self._buffer = []
        self.blocks = []

    def handle_starttag(self, tag, attrs):
        if tag == "script" and dict(attrs).get("type") == "application/ld+json":
            self._capturing = True
            self._buffer = []

    def handle_data(self, data):
        if self._capturing:
            self._buffer.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._capturing:
            self.blocks.append("".join(self._buffer))
            self._capturing = False


def objects(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from objects(child)


def article_documents():
    registry = json.loads((ROOT / "articles.json").read_text(encoding="utf-8"))
    for article in registry["articles"]:
        path = ROOT / f"{article['slug']}.html"
        if not path.exists():
            continue
        parser = JsonLdParser()
        parser.feed(path.read_text(encoding="utf-8"))
        documents = [json.loads(block) for block in parser.blocks]
        nodes = [node for document in documents for node in objects(document)]
        if any(node.get("@type") in ("Article", "NewsArticle") for node in nodes):
            yield path, nodes


class ArticleSchemaTests(unittest.TestCase):
    def test_general_articles_do_not_emit_event_schema(self):
        offenders = []
        for path, nodes in article_documents():
            events = [node.get("name", "unnamed event") for node in nodes
                      if node.get("@type") == "SportsEvent"]
            if events:
                offenders.append(f"{path.name}: {', '.join(events)}")
        self.assertEqual([], offenders)

    def test_dustin_johnson_page_has_complete_news_article(self):
        target = ROOT / "news-2026-dustin-johnson-liv-golf-2-0.html"
        parser = JsonLdParser()
        parser.feed(target.read_text(encoding="utf-8"))
        nodes = [node for block in parser.blocks for node in objects(json.loads(block))]
        article = next(node for node in nodes if node.get("@type") == "NewsArticle")
        required = {
            "headline", "description", "image", "datePublished", "dateModified",
            "author", "publisher", "mainEntityOfPage",
        }
        self.assertEqual(set(), required - article.keys())

    def test_tour_championship_odds_page_has_clean_news_schema(self):
        target = ROOT / "news-2026-tour-championship-odds-even-par.html"
        self.assertTrue(target.exists(), "new Tour Championship odds article is missing")
        parser = JsonLdParser()
        parser.feed(target.read_text(encoding="utf-8"))
        nodes = [node for block in parser.blocks for node in objects(json.loads(block))]
        self.assertFalse(any(node.get("@type") == "SportsEvent" for node in nodes))
        article = next(node for node in nodes if node.get("@type") == "NewsArticle")
        self.assertEqual(
            "https://www.golfraw.com/news-2026-tour-championship-odds-even-par#article",
            article.get("@id"),
        )
        required = {
            "headline", "description", "image", "datePublished", "dateModified",
            "author", "publisher", "mainEntityOfPage", "articleSection",
        }
        self.assertEqual(set(), required - article.keys())

    def test_tour_championship_odds_page_is_registered_in_tournament_feeds(self):
        slug = "news-2026-tour-championship-odds-even-par"
        registry = json.loads((ROOT / "articles.json").read_text(encoding="utf-8"))
        record = next((a for a in registry["articles"] if a.get("slug") == slug), None)
        self.assertIsNotNone(record, "article is missing from articles.json")
        self.assertEqual("PGA TOUR", record.get("category"))
        self.assertEqual("TOURNAMENTS", record.get("section"))
        for generated in ("news.html", "tournaments.html", "search.html", "sitemap.xml"):
            self.assertIn(slug, (ROOT / generated).read_text(encoding="utf-8"), generated)

    def test_scheffler_tour_championship_odds_page_has_clean_news_schema(self):
        target = ROOT / "news-2026-scottie-scheffler-tour-championship-odds.html"
        self.assertTrue(target.exists(), "Scheffler odds article is missing")
        parser = JsonLdParser()
        parser.feed(target.read_text(encoding="utf-8"))
        nodes = [node for block in parser.blocks for node in objects(json.loads(block))]
        self.assertFalse(any(node.get("@type") == "SportsEvent" for node in nodes))
        article = next(node for node in nodes if node.get("@type") == "NewsArticle")
        required = {
            "headline", "description", "image", "datePublished", "dateModified",
            "author", "publisher", "mainEntityOfPage", "articleSection",
        }
        self.assertEqual(set(), required - article.keys())
        self.assertTrue(article["image"]["url"].endswith("scottie-scheffler-tour-championship-2026-odds.webp"))
        html = target.read_text(encoding="utf-8")
        self.assertIn("Scottie Scheffler's 2026 Tour Championship odds: +310 | GOLFRAW", html)
        self.assertIn("24.39%", html)
        self.assertIn("7.3x", html)
        self.assertIn("+3735", html)
        self.assertIn("SCOTTIE SCHEFFLER ENTERS EAST LAKE AS THE +310 BETTING FAVOURITE. PHOTO: RAWGOLF", html)

    def test_scheffler_tour_championship_odds_page_is_registered(self):
        slug = "news-2026-scottie-scheffler-tour-championship-odds"
        registry = json.loads((ROOT / "articles.json").read_text(encoding="utf-8"))
        record = next((a for a in registry["articles"] if a.get("slug") == slug), None)
        self.assertIsNotNone(record, "Scheffler odds article is missing from articles.json")
        self.assertEqual("PGA TOUR", record.get("category"))
        self.assertEqual("TOURNAMENTS", record.get("section"))
        for generated in ("news.html", "tournaments.html", "search.html", "sitemap.xml"):
            self.assertIn(slug, (ROOT / generated).read_text(encoding="utf-8"), generated)


    def test_tour_championship_purse_page_has_clean_news_schema(self):
        target = ROOT / "news-2026-tour-championship-purse-east-lake.html"
        self.assertTrue(target.exists(), "Tour Championship purse article is missing")
        parser = JsonLdParser()
        parser.feed(target.read_text(encoding="utf-8"))
        nodes = [node for block in parser.blocks for node in objects(json.loads(block))]
        self.assertFalse(any(node.get("@type") == "SportsEvent" for node in nodes))
        article = next(node for node in nodes if node.get("@type") == "NewsArticle")
        self.assertEqual(
            "https://www.golfraw.com/news-2026-tour-championship-purse-east-lake#article",
            article.get("@id"),
        )
        required = {
            "headline", "description", "image", "datePublished", "dateModified",
            "author", "publisher", "mainEntityOfPage", "articleSection",
        }
        self.assertEqual(set(), required - article.keys())
        self.assertTrue(article["image"]["url"].endswith("tour-championship-2026-purse-east-lake.webp"))
        html = target.read_text(encoding="utf-8")
        self.assertIn("2026 Tour Championship Purse: The Winner Gets $10 Million | GOLFRAW", html)
        self.assertIn("$40,000,000", html)
        self.assertIn("$10,000,000", html)
        self.assertIn("$23,000,000", html)
        self.assertIn("THE 2026 TOUR CHAMPIONSHIP CARRIES A $40 MILLION OFFICIAL PURSE WITH $10 MILLION TO THE WINNER. PHOTO: RAWGOLF", html)

    def test_tour_championship_purse_page_is_registered(self):
        slug = "news-2026-tour-championship-purse-east-lake"
        registry = json.loads((ROOT / "articles.json").read_text(encoding="utf-8"))
        record = next((a for a in registry["articles"] if a.get("slug") == slug), None)
        self.assertIsNotNone(record, "Tour Championship purse article is missing from articles.json")
        self.assertEqual("PGA TOUR", record.get("category"))
        self.assertEqual("TOURNAMENTS", record.get("section"))
        for generated in ("news.html", "tournaments.html", "search.html", "sitemap.xml"):
            self.assertIn(slug, (ROOT / generated).read_text(encoding="utf-8"), generated)


    def test_tour_championship_2028_match_play_page_has_clean_news_schema(self):
        target = ROOT / "news-2026-tour-championship-2028-match-play-format.html"
        self.assertTrue(target.exists(), "2028 Tour Championship match play article is missing")
        parser = JsonLdParser()
        parser.feed(target.read_text(encoding="utf-8"))
        nodes = [node for block in parser.blocks for node in objects(json.loads(block))]
        self.assertFalse(any(node.get("@type") == "SportsEvent" for node in nodes))
        article = next(node for node in nodes if node.get("@type") == "NewsArticle")
        self.assertEqual(
            "https://www.golfraw.com/news-2026-tour-championship-2028-match-play-format#article",
            article.get("@id"),
        )
        required = {
            "headline", "description", "image", "datePublished", "dateModified",
            "author", "publisher", "mainEntityOfPage", "articleSection",
        }
        self.assertEqual(set(), required - article.keys())
        self.assertTrue(article["image"]["url"].endswith("tour-championship-2028-match-play-format.webp"))
        html = target.read_text(encoding="utf-8")
        self.assertIn("The Tour Championship 2028 Match Play Format, Explained Without the Spin | GOLFRAW", html)
        self.assertIn("32 Players", html)
        self.assertIn("16 Players", html)
        self.assertIn("SCOTTIE SCHEFFLER ADDRESSED THE 2028 TWO-WEEK MATCH PLAY RESTRUCTURE AT EAST LAKE. PHOTO: RAWGOLF", html)

    def test_tour_championship_2028_match_play_page_is_registered(self):
        slug = "news-2026-tour-championship-2028-match-play-format"
        registry = json.loads((ROOT / "articles.json").read_text(encoding="utf-8"))
        record = next((a for a in registry["articles"] if a.get("slug") == slug), None)
        self.assertIsNotNone(record, "2028 Tour Championship match play article is missing from articles.json")
        self.assertEqual("PGA TOUR", record.get("category"))
        self.assertEqual("TOURNAMENTS", record.get("section"))
        for generated in ("news.html", "tournaments.html", "search.html", "sitemap.xml"):
            self.assertIn(slug, (ROOT / generated).read_text(encoding="utf-8"), generated)


if __name__ == "__main__":
    unittest.main()


