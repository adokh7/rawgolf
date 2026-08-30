"""Regression checks for Task 5 citation implementation batch 1."""

import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.golfraw.com"

TARGETS = {
    "news-2026-liv-golf-300-million-funding-explained.html": {
        "title": "LIV Golf $300 Million Funding: It Might Be a Loan | GOLFRAW",
        "description": "The CEO says an investor signed. Bloomberg says it's a loan. Four vendors are suing. Here's what's actually confirmed, and the September date that decides it.",
        "canonical": f"{BASE}/news-2026-liv-golf-300-million-funding-explained",
        "citations": {
            "https://www.livgolf.com/news/liv-golf-reaches-agreement-with-lead-investor-for-its-next-era",
            "https://news.bloomberglaw.com/bankruptcy-law/bc-partners-credit-arm-explores-extending-lifeline-to-liv-golf",
            "https://golf.com/news/liv-golf-financial-woes-lawsuit/",
        },
    },
    "news-2026-henrik-stenson-pga-tour-champions-debut.html": {
        "title": "Henrik Stenson's PGA Tour Champions Debut | GOLFRAW",
        "description": "He didn't leave LIV. LIV dropped him. Here is the real date his ban ended, where he tees it up this week, and the one thing nobody can confirm yet.",
        "canonical": f"{BASE}/news-2026-henrik-stenson-pga-tour-champions-debut",
        "citations": {
            "https://www.golfmonthly.com/news/they-removed-my-ankle-bracelet-henrik-stenson-discusses-future-plans-as-liv-golf-penalty-comes-to-an-end",
            "https://theallychallenge.com/media/latest-news/2026/283-the-concert-17-presented-soaring-eagle-casino-resort-returns-friday-the-2026-the-ally-challenge-presented-mclaren/",
        },
    },
    "news-2026-liv-golf-players-return-pga-tour-rules.html": {
        "title": "LIV Golf to PGA Tour: What the Rules Say | GOLFRAW",
        "description": "LIV Golf players returning to the PGA Tour? The route closed on 2 February 2026. Here is what the rules allow and what remains a 2027 question.",
        "canonical": f"{BASE}/news-2026-liv-golf-players-return-pga-tour-rules",
        "citations": {
            "https://qualifying.pgatourhq.com/static-assets/uploads/2026-PGA%20TOUR%20Player%20Handbook%20and%20Regulations-2-23-26.pdf",
        },
    },
    "news-2026-scheffler-illness-update-95-percent-recovered.html": {
        "title": "Scheffler Illness Update: 95% Recovered | GOLFRAW",
        "description": "Scottie Scheffler says he is 95 percent recovered from hand, foot and mouth disease. Why his BMW Championship T12 looked worse than it was.",
        "canonical": f"{BASE}/news-2026-scheffler-illness-update-95-percent-recovered",
        "citations": {
            "https://www.espnradio941.com/2026/08/26/scheffler-says-hes-95-recovered-from-illness/",
        },
    },
    "news-2026-scottie-scheffler-hand-foot-and-mouth-disease.html": {
        "title": "Scottie Scheffler's Hand-Foot-and-Mouth Disease | GOLFRAW",
        "description": "Scottie Scheffler played the 2026 BMW Championship with hand-foot-and-mouth disease. The World No. 1 shot 68 on Sunday despite painful grip blisters.",
        "og_description": "World No. 1 golfer Scottie Scheffler fought through painful blisters to finish T12 at the 2026 BMW Championship, revealing his pediatric viral illness on Sunday.",
        "canonical": f"{BASE}/news-2026-scottie-scheffler-hand-foot-and-mouth-disease",
        "citations": {
            "https://www.foxnews.com/outkick-sports/scottie-scheffler-reveals-he-played-through-pretty-painful-illness-during-bmw-championship",
            "https://www.pgatour.com/tournaments/2026/bmw-championship/R2026028/leaderboard",
        },
    },
}


class CitationParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.meta = {}
        self.canonical = []
        self.links = []
        self._in_title = False
        self._title_buffer = []
        self._link = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self._in_title = True
            self._title_buffer = []
        elif tag == "meta":
            key = (attrs.get("name") or attrs.get("property") or "").lower()
            if key:
                self.meta.setdefault(key, []).append(attrs.get("content", ""))
        elif tag == "link" and "canonical" in attrs.get("rel", "").split():
            self.canonical.append(attrs.get("href", ""))
        elif tag == "a":
            self._link = [attrs.get("href", ""), []]

    def handle_data(self, data):
        if self._in_title:
            self._title_buffer.append(data)
        if self._link is not None:
            self._link[1].append(data)

    def handle_endtag(self, tag):
        if tag == "title" and self._in_title:
            self.title = " ".join("".join(self._title_buffer).split())
            self._in_title = False
        elif tag == "a" and self._link is not None:
            href, text = self._link
            self.links.append((href, " ".join("".join(text).split())))
            self._link = None


def parse(path):
    parser = CitationParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def first_meta(parser, key):
    return parser.meta.get(key, [""])[0]


class CitationBatch1Tests(unittest.TestCase):
    def test_all_batch_pages_contain_claim_specific_citations(self):
        for name, expected in TARGETS.items():
            parser = parse(ROOT / name)
            actual = {href for href, _ in parser.links}
            self.assertTrue(expected["citations"] <= actual, name)

    def test_citation_anchors_are_descriptive_and_non_empty(self):
        forbidden = {"source", "click here", "here", "read more"}
        for name, expected in TARGETS.items():
            parser = parse(ROOT / name)
            links = dict(parser.links)
            for href in expected["citations"]:
                anchor = links.get(href, "").strip()
                self.assertGreaterEqual(len(anchor), 16, f"short citation anchor: {name} {href}")
                self.assertNotIn(anchor.lower(), forbidden, f"generic citation anchor: {name} {href}")

    def test_external_links_are_https_and_not_generic_homepages(self):
        for name, expected in TARGETS.items():
            parser = parse(ROOT / name)
            for href, _ in parser.links:
                if not href.startswith("http"):
                    continue
                self.assertTrue(href.startswith("https://"), f"non-HTTPS external link: {name}")
                self.assertNotRegex(href, r"^https://[^/]+/?$", f"generic homepage citation: {name} {href}")
            self.assertTrue(expected["citations"] <= {href for href, _ in parser.links}, name)

    def test_existing_page_metadata_is_unchanged(self):
        for name, expected in TARGETS.items():
            parser = parse(ROOT / name)
            self.assertEqual(expected["title"], parser.title, name)
            self.assertEqual(expected["description"], first_meta(parser, "description"), name)
            self.assertEqual(expected.get("og_description", expected["description"]), first_meta(parser, "og:description"), name)
            self.assertEqual(expected["canonical"], parser.canonical[0], name)

    def test_batch_pages_have_no_template_or_oakmont_contamination(self):
        stale = ("Oakmont", "article-template", "Average score 74.8")
        for name in TARGETS:
            source = (ROOT / name).read_text(encoding="utf-8")
            for marker in stale:
                self.assertNotIn(marker, source, f"{marker} leaked into {name}")


if __name__ == "__main__":
    unittest.main()
