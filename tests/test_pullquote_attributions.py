"""Pull-quotes may not cite invented or anonymous sources.

Trust audit, 2026-11-14: pull-quotes across the site were credited to
bodies that do not exist ("TOUR GOVERNANCE AUDIT", "GolfRaw Editorial Board",
"RawGolf Hardware Testing Lab"), to anonymous insiders ("Former Ryder Cup
captain, speaking off the record to GolfRaw") and to real people without a
source. A pull-quote footer must now be either the house byline or a real,
named person whose quote has been checked against a published source and
listed in SOURCED below together with that source.
"""
import html
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOUSE = "— GolfRaw Editorial"

# (page, footer text) -> URL of the published source the quote was checked against.
SOURCED = {
    ("morikawa-61-travelers-championship-2026", "— Collin Morikawa, Travelers Championship transcript"):
        "https://asaptext.com/orgs/pgatour/1006/transcripts/168800.pdf",
    ("news-2026-jordan-spieth-golf-betting-problem-warning", "— Jordan Spieth, John Deere Classic transcript"):
        "https://asaptext.com/orgs/pgatour/1007/transcripts/168864.pdf",
    ("news-2026-liv-golf-players-return-pga-tour-rules", "— Brian Rolapp, PGA Tour CEO, via Front Office Sports"):
        "https://frontofficesports.com/pga-tour-not-offering-another-lifeline-to-liv-players-just-yet/",
    ("news-2026-scheffler-illness-update-95-percent-recovered", "— Scottie Scheffler, to ESPN, via TSN"):
        "https://www.tsn.ca/golf/pga-tour/article/scheffler-says-hes-95-recovered-from-viral-illness-n1-49731922/",
    ("news-2026-scottie-scheffler-61-tpc-southwind-course-record", "— Scottie Scheffler, FedEx St. Jude Championship interview"):
        "https://www.asapsports.com/show_interview.php?id=221225",
    ("news-2026-scottie-scheffler-misses-first-cut-in-four-years", "— Scottie Scheffler, via NBC Sports"):
        "https://www.nbcsports.com/golf/news/scottie-scheffler-misses-cut-for-first-time-in-4-years",
    ("news-2026-ryan-fox-open-22-seconds", "— Ryan Fox, via PGA TOUR"):
        "https://www.pgatour.com/article/news/latest/2026/07/19/ryan-fox-2026-british-open-fastest-player-in-the-world-superpower-is-his-speed-pace-of-play",
}

# Upper-case desk labels ("TOUR GOVERNANCE AUDIT") are matched case-sensitively so
# ordinary words such as "watch" or "analysis" inside a real quote stay allowed.
BANNED_LABELS = re.compile(r"\b(AUDIT|ANALYSIS|DIRECTIVE|DESK|INVESTIGATION|DISPATCH|ARITHMETIC|WATCH)\b")
BANNED_PHRASES = re.compile(
    r"Editorial Board|Testing Lab|Research Committee|off the record|\bcaddie\b|"
    r"tour veteran|tour rival|anonymous|\binsider\b",
    re.IGNORECASE,
)


def production_pages():
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    routes = re.findall(r"<loc>https://www\.golfraw\.com/([^<]*)</loc>", sitemap)
    pages = [ROOT / f"{route}.html" for route in routes if route]
    pages.append(ROOT / "article-template.html")
    return [page for page in pages if page.exists()]


def pull_quotes(path):
    source = path.read_text(encoding="utf-8")
    for block in re.findall(r'<blockquote class="pull">(.*?)</blockquote>', source, re.S):
        footer = re.search(r"<footer>(.*?)</footer>", block, re.S)
        footer_text = html.unescape(re.sub(r"<[^>]+>", "", footer.group(1))).strip() if footer else ""
        body = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<footer>.*?</footer>", "", block, flags=re.S)))
        yield footer_text, body


class PullQuoteAttributionTests(unittest.TestCase):
    def test_footers_are_house_or_sourced_people(self):
        problems = []
        for path in production_pages():
            route = path.relative_to(ROOT).with_suffix("").as_posix()
            for footer, _ in pull_quotes(path):
                if not footer or footer == HOUSE:
                    continue
                if (route, footer) not in SOURCED:
                    problems.append((route, footer))
        self.assertEqual([], problems)

    def test_no_invented_or_anonymous_source_anywhere_in_a_pull_quote(self):
        problems = []
        for path in production_pages():
            route = path.relative_to(ROOT).with_suffix("").as_posix()
            for footer, body in pull_quotes(path):
                for text in (footer, body):
                    match = BANNED_LABELS.search(text) or BANNED_PHRASES.search(text)
                    if match:
                        problems.append((route, match.group(0)))
        self.assertEqual([], problems)

    def test_sourced_quotes_link_their_source_on_the_page(self):
        for (route, footer), url in SOURCED.items():
            source = (ROOT / f"{route}.html").read_text(encoding="utf-8")
            self.assertIn(f'href="{url}"', source, route)


if __name__ == "__main__":
    unittest.main()
