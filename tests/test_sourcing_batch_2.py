"""Content pruning phase 2, batch 2 (15 November 2026): the next 15
highest-demand articles that cited no external source.

Each page was checked against published reporting, given a linked Sources
list, and corrected where the record differed. These checks pin the
corrections so a later edit or regeneration cannot bring the errors back.
Phrases quoted in an update note or in the corrections log's struck-through
"We wrote" column are allowed, because those quote the error on purpose.
"""
import html
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# slug -> (phrases that must not return, phrases the corrected page must keep)
BATCH = {
    "news-2026-bmw-championship-round-1-tee-times-local-time": (
        [],
        ["Wyndham Clark won the 2026 BMW Championship"],
    ),
    "news-2026-pga-tour-winners-2026": (
        ["28 Names, 35 Events", "three men who won three times"],
        ["29 Names, 37 Events", "Aaron Rai", "Shinnecock Hills"],
    ),
    "club-championship-divisions-flights-explained": (
        ["2.4 or lower", "set a 2.4 Handicap Index", "BREAKING NEWS", "audits attested physical scorecards"],
        ["Rule 3.3b"],
    ),
    "irish-open-2026-final-round-tee-times-tv": (
        ["two official sources disagree on", "missed the cut after a Friday 78"],
        ["probably the longest round of golf I ever played"],
    ),
    "news-2026-wyndham-fedexcup-bubble-koivun": (
        ["by exactly 12 points"],
        ["fewer than 12 points"],
    ),
    "news-2026-jackson-koivun-tpc-southwind-fedex-st-jude": (
        ["Quadrupled playoff points", "closely monitored the live leaderboard"],
        ["750"],
    ),
    "pga-tour-2028-two-series-model": (
        ["by winning two Challenger events", "about nine months studying"],
        ["in early 2027"],
    ),
    "news-2026-phil-mickelson-open-withdrawal-majors": (
        ["Official records confirm", "tournament records indicate"],
        ["GolfMagic"],
    ),
    "lpga-2026-kpmg-prize-money-12m": (
        ["$1.8 million going to the winner", "tied with the U.S. Women's Open as the richest"],
        ["$13 million", "$1.95 million"],
    ),
    "news-2026-the-renaissance-club-course-guide": (
        ["7,300-yard masterpiece", "It is his only design in Scotland"],
        ["7,282"],
    ),
    "news-2026-john-deere-classic-power-rankings": (
        ["peaking approach numbers", "2023 champion J.T. Poston"],
        ["119th"],
    ),
    "news-2026-how-much-pro-am-costs": (
        ["$200 to $400", "$200–$400", "The Left Rough", "€7,500", "two hundred quid", "I can't reconcile"],
        ["Covid made us get innovative and creative", "hidden-value-pro-ams-years"],
    ),
    "news-2026-us-presidents-cup-team-standings": (
        ["Jim Furyk", "by 79 points", "Sahith Theegala"],
        ["Brandt Snedeker"],
    ),
    "presidents-cup-captain-liv-golf-restrictions-international-team": (
        ["Asked the PGA Tour Three Times", "every year since taking the job", "got hurt a little harder"],
        ["a few times"],
    ),
    "strokes-gained": (
        ["Week 24", "2.81", "UPDATED WEEKLY"],
        ["assessing_golfer_performance"],
    ),
}

# Pages whose errors were logged (the others needed sourcing and minor edits only).
LOGGED = {
    "news-2026-the-renaissance-club-course-guide", "news-2026-john-deere-classic-power-rankings",
    "news-2026-pga-tour-winners-2026", "club-championship-divisions-flights-explained",
    "irish-open-2026-final-round-tee-times-tv", "news-2026-wyndham-fedexcup-bubble-koivun",
    "news-2026-jackson-koivun-tpc-southwind-fedex-st-jude",
    "news-2026-phil-mickelson-open-withdrawal-majors", "lpga-2026-kpmg-prize-money-12m",
    "news-2026-us-presidents-cup-team-standings",
    "presidents-cup-captain-liv-golf-restrictions-international-team", "strokes-gained",
    "news-2026-how-much-pro-am-costs",
}


def without_documented_errors(source):
    source = re.sub(r'<aside class="update-note".*?</aside>', " ", source, flags=re.S)
    return re.sub(r'<span class="wrong">.*?</span>', " ", source, flags=re.S)


def page(slug):
    return (ROOT / f"{slug}.html").read_text(encoding="utf-8")


class SourcingBatchTwoTests(unittest.TestCase):
    def test_corrected_errors_do_not_return(self):
        problems = []
        for slug, (banned, _) in BATCH.items():
            source = without_documented_errors(page(slug))
            for variant in (source, html.unescape(source)):
                for phrase in banned:
                    if phrase in variant:
                        problems.append((slug, phrase))
        self.assertEqual([], sorted(set(problems)))

    def test_corrected_facts_stay(self):
        problems = []
        for slug, (_, required) in BATCH.items():
            source = page(slug)
            for phrase in required:
                if phrase not in source and phrase not in html.unescape(source):
                    problems.append((slug, phrase))
        self.assertEqual([], problems)

    def test_each_page_cites_published_sources(self):
        for slug in BATCH:
            with self.subTest(slug=slug):
                source = page(slug)
                self.assertIn('class="sources"', source)
                article = re.search(r"<article.*?</article>", source, re.S).group(0)
                external = set(re.findall(r'href="(https?://(?!www\.golfraw\.com)[^"]+)"', article))
                self.assertGreaterEqual(len(external), 2)

    def test_dates_and_schema(self):
        for slug in BATCH:
            with self.subTest(slug=slug):
                source = page(slug)
                self.assertIn('"dateModified": "2026-11-15T12:00:00+01:00"', source)
                for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', source, re.S):
                    json.loads(block)

    def test_corrections_log_records_the_batch(self):
        log = (ROOT / "corrections.html").read_text(encoding="utf-8")
        for slug in LOGGED:
            with self.subTest(slug=slug):
                self.assertIn(f'<div class="e-story"><a href="/{slug}">', log)


if __name__ == "__main__":
    unittest.main()
