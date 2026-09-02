#!/usr/bin/env python3
"""Regression checks for structured data on registered article pages."""

import json
import html
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

from scripts.article_schema import (
    audit_article_schema,
    normalize_article_schema,
    parse_page as parse_schema_page,
)
from scripts.sync_site import sitemap_page_records


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
    def test_indexable_article_schema_inventory_is_complete(self):
        failures = []
        unresolved = []
        registry = {
            article["slug"]: article
            for article in json.loads((ROOT / "articles.json").read_text(encoding="utf-8"))["articles"]
        }
        expected_unresolved = {
            str(ROOT / "fix-over-the-top.html"),
            str(ROOT / "golf-clubs-for-beginners.html"),
            str(ROOT / "golf-swing-analysis-apps.html"),
            str(ROOT / "golf-swing-drills.html"),
            str(ROOT / "match-play.html"),
        }
        page_count = 0
        for route, record in sitemap_page_records().items():
            path = Path(record["path"])
            parser = JsonLdParser()
            source = path.read_text(encoding="utf-8")
            parser.feed(source)
            page_parser, _, _ = parse_schema_page(source)
            documents = [json.loads(block) for block in parser.blocks]
            articles = [
                node for document in documents for node in objects(document)
                if node.get("@type") in ("Article", "NewsArticle")
            ]
            if not articles:
                continue
            page_count += 1
            audit = audit_article_schema(source, path)
            if audit["malformed"] or audit["duplicate"]:
                failures.append(f"{route}: malformed/duplicate article JSON-LD")
            missing = set(audit["missing"]) - {"dateModified"}
            if missing:
                failures.append(f"{route}: missing {sorted(missing)}")
            if any(audit["mismatches"].values()):
                failures.append(f"{route}: {audit['mismatches']}")
            if "dateModified" in audit["unresolved"]:
                unresolved.append(str(path))

            article = articles[0]
            article_context = any(
                isinstance(document, dict)
                and document.get("@context") == "https://schema.org"
                for document in documents
                if any(node is article for node in objects(document))
            ) or any(
                isinstance(document, list)
                and any(
                    isinstance(item, dict)
                    and item.get("@context") == "https://schema.org"
                    and any(node is article for node in objects(item))
                    for item in document
                )
                for document in documents
            )
            if not article_context:
                failures.append(f"{route}: missing schema context")
            if not article.get("headline"):
                failures.append(f"{route}: empty headline")
            headline = str(article["headline"]).strip()
            og_title = page_parser.meta.get("og:title", [""])[0].strip()
            og_without_brand = re.sub(
                r"\s*\|\s*(?:GOLFRAW|GolfRaw|RawGolf)\s*$", "", og_title, flags=re.I
            )
            visible_h1 = page_parser.h1
            registry_title = html.unescape(registry.get(path.stem, {}).get("title", ""))
            if headline not in {og_title, og_without_brand, visible_h1, registry_title}:
                failures.append(f"{route}: headline does not match page metadata")
            if not article.get("datePublished") or not re.match(r"^\d{4}-\d{2}-\d{2}", str(article["datePublished"])):
                failures.append(f"{route}: invalid datePublished")
            if article.get("dateModified") and not re.match(r"^\d{4}-\d{2}-\d{2}", str(article["dateModified"])):
                failures.append(f"{route}: invalid dateModified")
            if not article.get("author") or not article.get("publisher"):
                failures.append(f"{route}: missing author/publisher")

        self.assertEqual(308, page_count)
        self.assertEqual(expected_unresolved, set(unresolved))
        self.assertEqual([], failures)

    def test_normalizer_completes_and_deduplicates_article_entity(self):
        source = '''<!doctype html>
<html><head>
  <title>Example story | GOLFRAW</title>
  <meta name="author" content="GOLFRAW Editorial">
  <meta property="og:image" content="https://www.golfraw.com/public/example.webp">
  <meta property="article:published_time" content="2026-08-31T10:00:00+02:00">
  <meta property="article:modified_time" content="2026-08-31T12:00:00+02:00">
  <link rel="canonical" href="https://www.golfraw.com/example-story">
  <script type="application/ld+json">
  {"@context":"https://schema.org","@type":"NewsArticle",
   "headline":"Old headline","datePublished":"2026-08-31",
   "publisher":{"@type":"Organization","name":"GOLFRAW"}}
  </script>
  <script type="application/ld+json">
  {"@context":"https://schema.org","@type":"NewsArticle",
   "headline":"Old headline","datePublished":"2026-08-31",
   "publisher":{"@type":"Organization","name":"GOLFRAW"}}
  </script>
</head><body><h1>Example story</h1></body></html>'''

        normalized = normalize_article_schema(source, ROOT / "example-story.html")
        parser = JsonLdParser()
        parser.feed(normalized)
        documents = [json.loads(block) for block in parser.blocks]
        articles = [
            node for document in documents for node in objects(document)
            if node.get("@type") in ("Article", "NewsArticle")
        ]
        self.assertEqual(1, len(articles))
        article = articles[0]
        self.assertEqual("https://www.golfraw.com/example-story", article["mainEntityOfPage"])
        self.assertEqual("https://www.golfraw.com/public/example.webp", article["image"])
        self.assertEqual("GOLFRAW Editorial", article["author"]["name"])
        self.assertEqual("2026-08-31T12:00:00+02:00", article["dateModified"])

    def test_normalizer_reports_missing_authoritative_modification_date(self):
        source = '''<html><head>
  <meta property="og:image" content="https://www.golfraw.com/public/example.webp">
  <meta property="article:published_time" content="2026-08-31">
  <link rel="canonical" href="https://www.golfraw.com/example-story">
  <script type="application/ld+json">{"@context":"https://schema.org","@type":"Article","headline":"Example story","image":"https://www.golfraw.com/public/example.webp","datePublished":"2026-08-31","author":{"@id":"https://www.golfraw.com/about#editorial"},"publisher":{"@id":"https://www.golfraw.com#organization"},"mainEntityOfPage":"https://www.golfraw.com/example-story"}</script>
</head><body><h1>Example story</h1></body></html>'''

        audit = audit_article_schema(source, ROOT / "example-story.html")
        self.assertIn("dateModified", audit["missing"])

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


    def test_brooks_koepka_motor_city_tgl_page_has_clean_news_schema(self):
        target = ROOT / "news-2026-brooks-koepka-motor-city-golf-club-tgl.html"
        self.assertTrue(target.exists(), "Brooks Koepka TGL article is missing")
        parser = JsonLdParser()
        parser.feed(target.read_text(encoding="utf-8"))
        nodes = [node for block in parser.blocks for node in objects(json.loads(block))]
        self.assertFalse(any(node.get("@type") == "SportsEvent" for node in nodes))
        article = next(node for node in nodes if node.get("@type") == "NewsArticle")
        self.assertEqual(
            "https://www.golfraw.com/news-2026-brooks-koepka-motor-city-golf-club-tgl#article",
            article.get("@id"),
        )
        required = {
            "headline", "description", "image", "datePublished", "dateModified",
            "author", "publisher", "mainEntityOfPage", "articleSection",
        }
        self.assertEqual(set(), required - article.keys())
        self.assertTrue(article["image"]["url"].endswith("brooks-koepka-motor-city-golf-club-tgl.webp"))
        html = target.read_text(encoding="utf-8")
        self.assertIn("Koepka Joins Detroit's TGL Team. Catch: No Detroit | GOLFRAW", html)
        self.assertIn("Motor City Golf Club", html)
        self.assertIn("SoFi Center", html)
        self.assertIn("BROOKS KOEPKA WAS NAMED THE FIRST PLAYER FOR TGL'S MOTOR CITY GOLF CLUB AHEAD OF ITS 2027 DEBUT. PHOTO: RAWGOLF", html)

    def test_brooks_koepka_motor_city_tgl_page_is_registered(self):
        slug = "news-2026-brooks-koepka-motor-city-golf-club-tgl"
        registry = json.loads((ROOT / "articles.json").read_text(encoding="utf-8"))
        record = next((a for a in registry["articles"] if a.get("slug") == slug), None)
        self.assertIsNotNone(record, "Brooks Koepka TGL article is missing from articles.json")
        self.assertEqual("PGA TOUR", record.get("category"))
        self.assertEqual("PGA TOUR", record.get("section"))
        for generated in ("news.html", "pga-tour.html", "search.html", "sitemap.xml"):
            self.assertIn(slug, (ROOT / generated).read_text(encoding="utf-8"), generated)


    def test_good_good_ad_backlash_page_has_clean_news_schema(self):
        target = ROOT / "news-2026-good-good-golf-ad-backlash.html"
        self.assertTrue(target.exists(), "Good Good Golf ad backlash article is missing")
        parser = JsonLdParser()
        parser.feed(target.read_text(encoding="utf-8"))
        nodes = [node for block in parser.blocks for node in objects(json.loads(block))]
        self.assertFalse(any(node.get("@type") == "SportsEvent" for node in nodes))
        article = next(node for node in nodes if node.get("@type") == "NewsArticle")
        self.assertEqual(
            "https://www.golfraw.com/news-2026-good-good-golf-ad-backlash#article",
            article.get("@id"),
        )
        required = {
            "headline", "description", "image", "datePublished", "dateModified",
            "author", "publisher", "mainEntityOfPage", "articleSection",
        }
        self.assertEqual(set(), required - article.keys())
        self.assertTrue(article["image"]["url"].endswith("good-good-golf-ad-backlash-callaway-2026.webp"))
        html = target.read_text(encoding="utf-8")
        self.assertIn("Good Good Golf Ad Backlash: What's Actually Been Pulled | GOLFRAW", html)
        self.assertIn("Dick's Sporting Goods", html)
        self.assertIn("Golf Galaxy", html)
        self.assertIn("PGA Tour Superstore", html)
        self.assertIn("GOOD GOOD GOLF MERCHANDISE WAS PULLED BY THREE MAJOR RETAILERS FOLLOWING THE AUGUST 2026 ADVERT. PHOTO: RAWGOLF", html)

    def test_good_good_ad_backlash_page_is_registered(self):
        slug = "news-2026-good-good-golf-ad-backlash"
        registry = json.loads((ROOT / "articles.json").read_text(encoding="utf-8"))
        record = next((a for a in registry["articles"] if a.get("slug") == slug), None)
        self.assertIsNotNone(record, "Good Good Golf ad backlash article is missing from articles.json")
        self.assertEqual("PGA TOUR", record.get("category"))
        self.assertEqual("PGA TOUR", record.get("section"))
        for generated in ("news.html", "pga-tour.html", "search.html", "sitemap.xml"):
            self.assertIn(slug, (ROOT / generated).read_text(encoding="utf-8"), generated)


if __name__ == "__main__":
    unittest.main()
