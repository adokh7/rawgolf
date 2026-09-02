"""Regression checks for Task 5 citation implementation batch 2."""

import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.golfraw.com"

TARGETS = {
    "news-2026-liv-golf-pif-withdrawal-season-end.html": {
        "title": "LIV Golf Ends 2026 Season Early Following PIF Withdrawal",
        "description": "LIV Golf packed up its 2026 season two weeks early. The cancellation of the Team Championship traces to PIF's April withdrawal. See the full timeline.",
        "canonical": f"{BASE}/news-2026-liv-golf-pif-withdrawal-season-end",
        "citations": {
            "https://www.aljazeera.com/amp/sports/2026/4/30/liv-golf-has-a-new-chairman-and-seeks-to-new-funding-without-saudi-backing",
            "https://www.livgolf.com/news/liv-golf-individual-and-team-winners-to-be-crowned-in-indianapolis",
            "https://www.livgolf.com/news/liv-golf-indianapolis-2026-results-final-recap",
            "https://www.livgolf.com/news/liv-golf-reaches-agreement-with-lead-investor-for-its-next-era",
        },
    },
    "news-2026-jon-rahm-liv-golf-future.html": {
        "title": "Jon Rahm LIV Golf Future: August 2026 Update",
        "description": "Jon Rahm faces a short window to return to the PGA Tour. He settled a $3 million DP World Tour fine in May, but 2028 rules approach.",
        "canonical": f"{BASE}/news-2026-jon-rahm-liv-golf-future",
        "citations": {
            "https://www.golfchannel.com/dp-world-tour/news/jon-rahm-reaches-agreement-with-dp-world-tour-pays-outstanding-fines",
            "https://irishgolfer.ie/latest-golf-news/2026/05/05/rahm-agrees-deal-to-play-on-dp-world-tour/",
            "https://www.livgolf.com/news/liv-golf-indianapolis-2026-results-final-recap",
            "https://www.livgolf.com/news/liv-golf-reaches-agreement-with-lead-investor-for-its-next-era",
        },
    },
    "news-2026-liv-golf-vendor-lawsuit-settlement-offers.html": {
        "title": "The LIV Golf vendor lawsuit: a $1.23m claim | GOLFRAW",
        "canonical": f"{BASE}/news-2026-liv-golf-vendor-lawsuit-settlement-offers",
        "citations": {
            "https://frontofficesports.com/liv-golf-sued-for-1-2m-by-company-that-produced-preseason-event/",
            "https://frontofficesports.com/liv-golf-ceo-i-hope-we-can-pay-unpaid-vendors/",
            "https://frontofficesports.com/liv-golf-returns-after-47-day-break-facing-1-1m-lawsuit/",
            "https://www.golfchannel.com/news/news/liv-golf-purse-cut-in-half-for-season-finale-in-indianapolis",
        },
    },
    "news-2026-jon-rahm-pga-tour-return-2027-unconfirmed.html": {
        "title": "Jon Rahm PGA Tour return 2027: What is confirmed | GOLFRAW",
        "description": "Jon Rahm PGA Tour return 2027 remains unconfirmed. We trace the PGA rules, his real DP World Tour deal and the 197-day gap since the window shut.",
        "canonical": f"{BASE}/news-2026-jon-rahm-pga-tour-return-2027-unconfirmed",
        "citations": {
            "https://qualifying.pgatourhq.com/static-assets/uploads/2026-PGA%20TOUR%20Player%20Handbook%20and%20Regulations-2-23-26.pdf",
            "https://www.golfchannel.com/dp-world-tour/news/jon-rahm-reaches-agreement-with-dp-world-tour-pays-outstanding-fines",
            "https://www.asapsports.com/show_interview.php?id=214625",
        },
    },
    "news-2026-jon-rahm-liv-money-list-contract-debt.html": {
        "title": 'Jon Rahm Has "Earned" $87.7 Million on LIV | GOLFRAW',
        "description": "Rahm tops LIV's earnings list at $87.7m — but $36m of that is bonus, and none of it includes his reported $300m signing fee. What the numbers really show.",
        "canonical": f"{BASE}/news-2026-jon-rahm-liv-money-list-contract-debt",
        "citations": {
            "https://www.compleatgolfer.com/liv-golf/liv-golf-money-list-leaders-since-2022/",
            "https://www.golfmonthly.com/features/what-next-for-jon-rahm",
            "https://www.livgolf.com/news/liv-golf-reaches-agreement-with-lead-investor-for-its-next-era",
            "https://www.livgolf.com/news/liv-golf-announces-competition-format-updates-for-2026-season",
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
        self.in_title = False
        self.title_buffer = []
        self.link = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.in_title = True
            self.title_buffer = []
        elif tag == "meta":
            key = (attrs.get("name") or attrs.get("property") or "").lower()
            if key:
                self.meta.setdefault(key, []).append(attrs.get("content", ""))
        elif tag == "link" and "canonical" in attrs.get("rel", "").split():
            self.canonical.append(attrs.get("href", ""))
        elif tag == "a":
            self.link = [attrs.get("href", ""), []]

    def handle_data(self, data):
        if self.in_title:
            self.title_buffer.append(data)
        if self.link is not None:
            self.link[1].append(data)

    def handle_endtag(self, tag):
        if tag == "title" and self.in_title:
            self.title = " ".join("".join(self.title_buffer).split())
            self.in_title = False
        elif tag == "a" and self.link is not None:
            href, text = self.link
            self.links.append((href, " ".join("".join(text).split())))
            self.link = None


def parse_html(html):
    parser = CitationParser()
    parser.feed(html)
    return parser


def parse(path):
    return parse_html(path.read_text(encoding="utf-8"))


def first_meta(parser, key):
    return parser.meta.get(key, [""])[0]


class CitationBatch2Tests(unittest.TestCase):
    def test_all_batch_pages_contain_claim_specific_citations(self):
        for name, expected in TARGETS.items():
            parser = parse(ROOT / name)
            actual = {href for href, _ in parser.links}
            self.assertTrue(expected["citations"] <= actual, name)

    def test_citation_anchors_are_descriptive_and_non_empty(self):
        forbidden = {"source", "click here", "here", "read more"}
        for name, expected in TARGETS.items():
            links = dict(parse(ROOT / name).links)
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
            if "description" in expected:
                self.assertEqual(expected["description"], first_meta(parser, "description"), name)
                self.assertEqual(expected["description"], first_meta(parser, "og:description"), name)
            self.assertEqual(expected["canonical"], parser.canonical[0], name)
            original = parse_html(subprocess.check_output(["git", "show", f"HEAD:{name}"], text=True))
            self.assertEqual(original.title, parser.title, name)
            self.assertEqual(first_meta(original, "description"), first_meta(parser, "description"), name)
            self.assertEqual(original.canonical, parser.canonical, name)

    def test_batch_pages_have_no_template_or_oakmont_contamination(self):
        stale = ("Oakmont", "article-template", "Average score 74.8")
        for name in TARGETS:
            source = (ROOT / name).read_text(encoding="utf-8")
            for marker in stale:
                self.assertNotIn(marker, source, f"{marker} leaked into {name}")

    def test_article_bodies_are_present(self):
        for name in TARGETS:
            source = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn('<div class="article-body">', source, name)
            self.assertGreater(source.count("<p>"), 5, name)


if __name__ == "__main__":
    unittest.main()
