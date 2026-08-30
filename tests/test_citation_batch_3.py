"""Regression checks for Task 5 citation implementation batch 3."""

import re
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]

TARGETS = {
    "news-2026-liv-golf-line-of-credit-debt-rahm.html": {
        "citations": {
            "https://news.bloomberglaw.com/bankruptcy-law/bc-partners-credit-arm-explores-extending-lifeline-to-liv-golf",
            "https://www.livgolf.com/news/liv-golf-reaches-agreement-with-lead-investor-for-its-next-era",
            "https://www.golfmonthly.com/features/what-next-for-jon-rahm",
            "https://www.europeantour.com/dpworld-tour/news/articles/detail/statement-from-the-dp-world-tour/",
        },
    },
    "jessica-bang-2008-2026.html": {
        "citations": {
            "https://www.cbsnews.com/news/jessica-bang-dies-golfer-age-18-brain-hemorrhage/",
            "https://www.golfmonthly.com/news/promising-australian-pro-jessica-bang-dies-at-age-of-18",
        },
    },
    "news-2026-liv-golf-equity-dp-world-tour-fines-2027.html": {
        "citations": {
            "https://www.europeantour.com/dpworld-tour/news/articles/detail/statement-from-the-dp-world-tour/",
            "https://www.golfmonthly.com/news/dp-world-tour-set-to-resume-fines-and-sanctions-for-liv-golf-members",
            "https://www.skysports.com/golf/news/12040/13540403/jon-rahm-agrees-deal-to-play-on-dp-world-tour-after-paying-off-outstanding-fines-leaving-him-free-to-feature-in-ryder-cup",
            "https://www.livgolf.com/news/liv-golf-reaches-agreement-with-lead-investor-for-its-next-era",
            "https://news.bloomberglaw.com/bankruptcy-law/bc-partners-credit-arm-explores-extending-lifeline-to-liv-golf",
        },
    },
    "news-2026-solheim-cup-dewi-weber-dutch-eligibility-let.html": {
        "citations": {
            "https://www.solheimcup2026.golf/faqs/",
            "https://www.ngf.nl/solheimcup",
            "https://www.skysports.com/golf/news/29304/13571590/solheim-cup-2026-why-dutchwoman-dewi-weber-was-ineligible-to-be-potential-team-europe-captains-pick-for-home-edition",
        },
    },
    "news-2026-liv-golf-investor-bc-partners-dechambeau.html": {
        "citations": {
            "https://news.bloomberglaw.com/bankruptcy-law/bc-partners-credit-arm-explores-extending-lifeline-to-liv-golf",
            "https://www.bcpartners.com/news/gse-worldwide-to-accelerate-growth-with-strategic-investment-from-bc-partners-credit-and-continued-support-from-gatemore-capital-management/",
            "https://golf.com/news/inside-liv-golf-wild-week-bedminster/?amp=1",
            "https://www.europeantour.com/dpworld-tour/news/articles/detail/asian-tour-dp-world-tour-and-pga-tour-agree-multi-year-partnership/",
            "https://www.livgolf.com/news/liv-golf-reaches-agreement-with-lead-investor-for-its-next-era",
        },
    },
}


class CitationParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.h1 = []
        self.meta = {}
        self.canonical = []
        self.links = []
        self._title = False
        self._heading = None
        self._buffer = []
        self._link = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self._title = True
            self._buffer = []
        elif tag == "h1":
            self._heading = tag
            self._buffer = []
        elif tag == "meta":
            key = (attrs.get("name") or attrs.get("property") or "").lower()
            if key:
                self.meta.setdefault(key, []).append(attrs.get("content", ""))
        elif tag == "link" and "canonical" in attrs.get("rel", "").split():
            self.canonical.append(attrs.get("href", ""))
        elif tag == "a":
            self._link = [attrs.get("href", ""), []]

    def handle_data(self, data):
        if self._title or self._heading:
            self._buffer.append(data)
        if self._link is not None:
            self._link[1].append(data)

    def handle_endtag(self, tag):
        if tag == "title" and self._title:
            self.title = " ".join("".join(self._buffer).split())
            self._title = False
        elif tag == "h1" and self._heading:
            self.h1.append(" ".join("".join(self._buffer).split()))
            self._heading = None
        elif tag == "a" and self._link is not None:
            href, text = self._link
            self.links.append((href, " ".join("".join(text).split())))
            self._link = None


def parse_html(value):
    parser = CitationParser()
    parser.feed(value)
    return parser


def parse(path):
    return parse_html(path.read_text(encoding="utf-8"))


def first_meta(parser, key):
    return parser.meta.get(key, [""])[0]


class CitationBatch3Tests(unittest.TestCase):
    def test_all_expected_article_files_exist(self):
        for name in TARGETS:
            self.assertTrue((ROOT / name).is_file(), name)

    def test_all_pages_contain_expected_claim_specific_citations(self):
        for name, expected in TARGETS.items():
            actual = {href for href, _ in parse(ROOT / name).links}
            self.assertTrue(expected["citations"] <= actual, name)

    def test_citation_hrefs_are_real_external_https_links(self):
        forbidden = {"source", "click here", "here", "read more"}
        for name, expected in TARGETS.items():
            links = dict(parse(ROOT / name).links)
            for href in expected["citations"]:
                parsed = urlsplit(href)
                self.assertEqual("https", parsed.scheme, f"non-HTTPS citation: {name} {href}")
                self.assertTrue(parsed.netloc and parsed.path, f"malformed citation: {name} {href}")
                self.assertNotIn("example.com", parsed.netloc.lower(), href)
                self.assertNotIn("javascript:", href.lower(), href)
                self.assertNotRegex(href, r"[<>\s]", href)
                anchor = links.get(href, "").strip()
                self.assertGreaterEqual(len(anchor), 16, f"short citation anchor: {name} {href}")
                self.assertNotIn(anchor.lower(), forbidden, f"generic citation anchor: {name} {href}")

    def test_metadata_h1_and_indexability_are_unchanged(self):
        for name in TARGETS:
            current = parse(ROOT / name)
            original = parse_html(
                subprocess.check_output(["git", "show", f"HEAD:{name}"], text=True)
            )
            self.assertEqual(original.title, current.title, name)
            self.assertEqual(original.h1, current.h1, name)
            for key in ("description", "og:title", "og:description", "og:url", "robots"):
                self.assertEqual(first_meta(original, key), first_meta(current, key), f"{name} {key}")
            self.assertEqual(original.canonical, current.canonical, name)
            self.assertNotIn("noindex", first_meta(current, "robots").lower(), name)

    def test_no_placeholder_or_template_contamination(self):
        stale = ("Oakmont", "article-template", "Average score 74.8")
        for name in TARGETS:
            source = (ROOT / name).read_text(encoding="utf-8")
            for marker in stale:
                self.assertNotIn(marker, source, f"{marker} leaked into {name}")

    def test_article_body_and_citation_anchors_are_present(self):
        for name in TARGETS:
            source = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn('class="article-body"', source, name)
            self.assertGreater(source.count("<p>"), 5, name)
            self.assertRegex(source, r'<a\s+[^>]*href="https://[^" ]+"[^>]*>[^<]+</a>')


if __name__ == "__main__":
    unittest.main()
