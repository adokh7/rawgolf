"""Regression checks for Task 4 page-level SEO quality fixes."""

import re
import subprocess
import unittest
from html.parser import HTMLParser
from html import unescape
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.golfraw.com"
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

ARTICLE_TITLES = {
    "news-2026-tour-championship-winners-losers-friday.html": "Tour Championship Winners & Losers: Scheffler Surges | GOLFRAW",
    "news-2026-tour-championship-prize-money-payout.html": "2026 Tour Championship Payout: $355K for 30th | GOLFRAW",
    "news-2026-cameron-young-new-putter-62-tour-championship.html": "Cameron Young's New Putter Led to a 62 | GOLFRAW",
    "news-2026-hovland-tie-for-lead-tour-championship.html": "Hovland Ties Tour Championship Lead: 12 of 14 | GOLFRAW",
    "news-2026-henrik-stenson-pga-tour-champions-debut.html": "Henrik Stenson's PGA Tour Champions Debut | GOLFRAW",
    "news-2026-good-good-golf-ad-backlash.html": "Good Good Golf Ad Backlash: What Was Pulled | GOLFRAW",
    "news-2026-tour-championship-2028-match-play-format.html": "Tour Championship 2028 Match Play Format Explained | GOLFRAW",
    "news-2026-tour-championship-purse-east-lake.html": "2026 Tour Championship Purse: $10 Million to Win | GOLFRAW",
    "news-2026-liv-golf-players-return-pga-tour-rules.html": "LIV Golf to PGA Tour: What the Rules Say | GOLFRAW",
    "news-2026-scheffler-illness-update-95-percent-recovered.html": "Scheffler Illness Update: 95% Recovered | GOLFRAW",
    "news-2026-scottie-scheffler-tour-championship-odds.html": "Scottie Scheffler's 2026 Tour Championship Odds | GOLFRAW",
    "news-2026-tour-championship-odds-even-par.html": "2026 Tour Championship Odds at Even Par | GOLFRAW",
    "news-2026-us-presidents-cup-team-standings.html": "2026 U.S. Presidents Cup Team Standings | GOLFRAW",
    "news-2026-scottie-scheffler-hand-foot-and-mouth-disease.html": "Scottie Scheffler's Hand-Foot-and-Mouth Disease | GOLFRAW",
}

EXPECTED_DESCRIPTIONS = {
    "liv-golf.html": "LIV Golf news, schedules, results, players, rankings and analysis, with the major developments shaping the league.",
    "news-2026-good-good-golf-ad-backlash.html": "Good Good Golf ad backlash: retailers pull merch and Big Break is postponed, but the PGA Tour Good Good Championship is still on. What is confirmed.",
    "news-2026-liv-golf-players-return-pga-tour-rules.html": "LIV Golf players returning to the PGA Tour? The route closed on 2 February 2026. Here is what the rules allow and what remains a 2027 question.",
    "news-2026-scheffler-illness-update-95-percent-recovered.html": "Scottie Scheffler says he is 95 percent recovered from hand, foot and mouth disease. Why his BMW Championship T12 looked worse than it was.",
    "tools-round-autopsy.html": "Free golf round analyser. Enter 18 holes of scores, fairways, greens and putts to see exactly where your strokes went: tee, approach, short game or putting.",
    "tools-tilt-meter.html": "Free golf tilt calculator. Enter 18 holes relative to par to see how many shots your temper cost you after a blow-up hole, plus your bounce-back rate.",
}

EXPECTED_TOOL_TITLES = {
    "tools-round-autopsy.html": "The Round Autopsy: Golf Round Stats Analyser | GOLFRAW",
    "tools-tilt-meter.html": "The Tilt Meter: Amateur Meltdown Index | GOLFRAW",
}

TASK5_INLINE_CITATION_HREFS = {
    "https://www.livgolf.com/news/liv-golf-reaches-agreement-with-lead-investor-for-its-next-era",
    "https://news.bloomberglaw.com/bankruptcy-law/bc-partners-credit-arm-explores-extending-lifeline-to-liv-golf",
    "https://golf.com/news/liv-golf-financial-woes-lawsuit/",
    "https://www.golfmonthly.com/news/they-removed-my-ankle-bracelet-henrik-stenson-discusses-future-plans-as-liv-golf-penalty-comes-to-an-end",
    "https://theallychallenge.com/media/latest-news/2026/283-the-concert-17-presented-soaring-eagle-casino-resort-returns-friday-the-2026-the-ally-challenge-presented-mclaren/",
    "https://qualifying.pgatourhq.com/static-assets/uploads/2026-PGA%20TOUR%20Player%20Handbook%20and%20Regulations-2-23-26.pdf",
    "https://www.espnradio941.com/2026/08/26/scheffler-says-hes-95-recovered-from-illness/",
    "https://www.foxnews.com/outkick-sports/scottie-scheffler-reveals-he-played-through-pretty-painful-illness-during-bmw-championship",
}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.meta = {}
        self.h1 = []
        self.h2 = []
        self.in_title = False
        self.heading = None
        self.buffer = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.in_title = True
            self.buffer = []
        elif tag in {"h1", "h2"}:
            self.heading = tag
            self.buffer = []
        elif tag == "meta":
            key = (attrs.get("name") or attrs.get("property") or "").lower()
            if key:
                self.meta.setdefault(key, []).append(attrs.get("content", ""))

    def handle_data(self, data):
        if self.in_title or self.heading:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if tag == "title" and self.in_title:
            self.title = " ".join("".join(self.buffer).split())
            self.in_title = False
        elif tag == self.heading:
            value = " ".join("".join(self.buffer).split())
            getattr(self, self.heading).append(value)
            self.heading = None


def parse(path):
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def meta(parser, key):
    return parser.meta.get(key.lower(), [""])[0]


def route_for(name):
    return "/" if name == "index.html" else "/" + name[:-5]


def sitemap_paths():
    root = ElementTree.parse(ROOT / "sitemap.xml").getroot()
    return {
        urlsplit(node.findtext("sm:loc", "", SITEMAP_NS)).path
        for node in root.findall("sm:url", SITEMAP_NS)
    }


def comparable_article(source):
    """Compare article copy while allowing Task 5 citation markup only."""
    body = re.search(r"<article\b.*?</article>", source, re.I | re.S)
    if body is None:
        return ""
    value = body.group(0)
    value = re.sub(r'<section\b[^>]*class=["\'][^"\']*\bsources\b[^"\']*["\'][^>]*>.*?</section>', "", value, flags=re.I | re.S)
    for href in TASK5_INLINE_CITATION_HREFS:
        tag = rf'<a\b[^>]*href=["\']{re.escape(href)}["\'][^>]*>(.*?)</a>'
        value = re.sub(tag, r"\1", value, flags=re.I | re.S)
    return re.sub(r"\s+", " ", value).strip()


class OnPageSeoTests(unittest.TestCase):
    def test_news_and_liv_have_distinct_intent_specific_descriptions(self):
        news = parse(ROOT / "news.html")
        liv = parse(ROOT / "liv-golf.html")
        news_description = meta(news, "description")
        liv_description = meta(liv, "description")
        self.assertTrue(news_description)
        self.assertEqual(EXPECTED_DESCRIPTIONS["liv-golf.html"], liv_description)
        self.assertNotEqual(news_description, liv_description)
        self.assertEqual(liv_description, meta(liv, "og:description"))
        self.assertEqual(liv_description, meta(liv, "twitter:description"))
        for term in ("news", "schedules", "results", "players", "rankings", "analysis"):
            self.assertIn(term, liv_description.lower())

    def test_affected_pages_have_exactly_one_h1(self):
        for name in ("ratings.html", "tools-standing-order.html"):
            parser = parse(ROOT / name)
            self.assertEqual(1, len(parser.h1), name)
        ratings = parse(ROOT / "ratings.html")
        standing = parse(ROOT / "tools-standing-order.html")
        self.assertIn("Raw Player Ratings", ratings.h2)
        self.assertIn("Bag Gapping Chart", standing.h2)
        self.assertIn("#printArea h2", (ROOT / "tools-standing-order.html").read_text(encoding="utf-8"))

    def test_flagged_titles_are_specific_and_synchronised(self):
        for name, expected in {**ARTICLE_TITLES, **EXPECTED_TOOL_TITLES}.items():
            parser = parse(ROOT / name)
            self.assertEqual(expected, parser.title, name)
            self.assertEqual(expected, meta(parser, "og:title"), name)
            self.assertEqual(expected, meta(parser, "twitter:title"), name)
            self.assertLessEqual(len(expected), 62, name)

    def test_flagged_descriptions_are_specific_and_synchronised(self):
        for name, expected in EXPECTED_DESCRIPTIONS.items():
            parser = parse(ROOT / name)
            self.assertEqual(expected, meta(parser, "description"), name)
            self.assertEqual(expected, meta(parser, "og:description"), name)
            self.assertEqual(expected, meta(parser, "twitter:description"), name)
            self.assertLessEqual(len(expected), 160, name)

    def test_thin_placeholder_pages_are_noindex_and_omitted_from_sitemap(self):
        paths = sitemap_paths()
        for name in ("past-issues.html", "the-card.html"):
            parser = parse(ROOT / name)
            robots = meta(parser, "robots").lower().replace(",", " ").split()
            self.assertIn("noindex", robots, name)
            self.assertIn("follow", robots, name)
            self.assertEqual(BASE + route_for(name), meta(parser, "og:url"), name)
            self.assertNotIn(route_for(name), paths, name)

    def test_full_board_remains_indexable_with_explanatory_context(self):
        path = ROOT / "full-board.html"
        parser = parse(path)
        source = path.read_text(encoding="utf-8")
        self.assertEqual(["Raw Player Ratings"], parser.h1)
        self.assertNotIn("noindex", meta(parser, "robots").lower())
        self.assertIn("How to read the Full Board", source)
        for term in ("Data Golf", "Official World Golf Ranking", "FedExCup", "updated weekly"):
            self.assertIn(term, source)

    def test_edited_articles_keep_their_article_body(self):
        for name in ARTICLE_TITLES:
            current = (ROOT / name).read_text(encoding="utf-8")
            base = subprocess.check_output(["git", "show", f"HEAD:{name}"], text=True)
            self.assertTrue(comparable_article(current), name)
            self.assertTrue(comparable_article(base), name)
            self.assertEqual(comparable_article(base), comparable_article(current), name)

    def test_affected_metadata_is_not_stale_template_data(self):
        stale = ("Oakmont", "article-template", "Average score 74.8")
        names = list(ARTICLE_TITLES) + list(EXPECTED_TOOL_TITLES) + ["liv-golf.html", "full-board.html"]
        for name in names:
            source = (ROOT / name).read_text(encoding="utf-8")
            for marker in stale:
                self.assertNotIn(marker, source, f"{marker} leaked into {name}")


if __name__ == "__main__":
    unittest.main()
