"""Content pruning phase 2, batch 1 (15 November 2026): the 15 highest-demand
articles that cited no external source.

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
    "golf-majors-guide": (
        ["filled from the PGA Tour money list", "strongest field in golf", "nearly half the field"],
        ["10,201 entries in 2026"],
    ),
    "topgolf-first-timers": (
        ["roughly 240 yards wide", "more than a dozen to choose from", "microchipped balls"],
        ["topgolf.com/us/faq"],
    ),
    "news-2026-kane-brown-golf-accident": (
        ["doctors diagnosed a slight concussion", "rest rather than push through", "several outlets ran warnings"],
        ["It was my own buddy", "Never stand ahead of or beside a playing partner"],
    ),
    "us-open-2026-prize-money": (
        ["Raymond Floyd won $126,000", "fifth purse increase in six years", "more than 35 times"],
        ["Raymond Floyd won $115,000", "Wyndham Clark won the 2026 U.S. Open"],
    ),
    "thriston-lawrence-european-masters-halfway-lead": (
        ["ESPN's tournament page says 6,808", "on-the-ground tournament reporting", "weeks before his 63rd birthday", "1,500 Ryder Cup points"],
        ["$3.75 million", "Lawrence won"],
    ),
    "news-2026-3m-open-prize-money-payout": (
        ["may shift only if the published payout sheet differs", "Full Payout Breakdown by</a>"],
        ["Jackson Koivun won the 2026 3M Open"],
    ),
    "news-2026-fedex-st-jude-championship-prize-money-payouts": (
        ["$582,800", "$369,571.44", "$42,200", "Robert MacIntyre (Knee issue)"],
        ["$582,000", "$368,571.43", "$41,600", "neither received a payout"],
    ),
    "news-2026-bmw-championship-tee-times-top-30-cut": (
        ["J.T. Poston, and Alex Noren"],
        ["Nicolai Højgaard", "Wyndham Clark won the 2026 BMW Championship"],
    ),
    "news-2026-bmw-championship-bellerive-par-70-course-setup": (
        ["Bellerive Is a Par 72", "operated as a par-72 championship test", "converted two par 5s",
         "75.0 course rating", "Zoysia fairways", "financial conclusion of the regular season"],
        ["Bellerive Plays a Par 70", "par 70 for the 2018 PGA Championship"],
    ),
    "what-is-topgolf": (
        ["Climate-controlled bays", "a set number of balls", "reward pure distance", "screen tells you how far"],
        ["fans for summer and heaters for winter"],
    ),
    "bmw-championship-2026-bellerive-yardage": (
        ["17 of the 50 players", "Rees Jones rebuilt every green", "venue preview on 17 August 2026"],
        ["course preview on 18 August 2026", "T1 bentgrass"],
    ),
    "news-2026-donald-trump-amgen-irish-open-doonbeg": (
        ["30 nautical miles", "over 1,000 officers", "Garda Press Office", "property land registries",
         "€20 million", "has confirmed his schedule to attend"],
        ["10 nautical miles", "about 4,000", "GolfRaw was not at Doonbeg"],
    ),
    "golf-swing-analysis-apps": (
        ["used to be called Hudl Technique", "no lasting free tier", "less keen on its wireframe"],
        ["took over the Hudl Technique app", "14-day free trial"],
    ),
    "history-pga-championship-winners-list": (
        ["265, by David Toms in 2001, later matched", "small group of English players", "Michees", "🏆"],
        ["263, by Xander Schauffele in 2024", "since Jim Barnes in 1919", "Micheels"],
    ),
    "news-2026-the-open-heroes-classic-birkdale": (
        ["actress Kathryn Newton", "relaxed yet spirited environment", "**"],
        ["Paula Martín Sampedro", "It&rsquo;s a great concept"],
    ),
}

# Pages whose errors were logged (the others needed sourcing and minor edits only).
LOGGED = {
    "history-pga-championship-winners-list", "news-2026-the-open-heroes-classic-birkdale",
    "golf-swing-analysis-apps", "news-2026-fedex-st-jude-championship-prize-money-payouts",
    "news-2026-bmw-championship-bellerive-par-70-course-setup",
    "news-2026-bmw-championship-tee-times-top-30-cut", "news-2026-donald-trump-amgen-irish-open-doonbeg",
    "us-open-2026-prize-money", "thriston-lawrence-european-masters-halfway-lead",
    "news-2026-kane-brown-golf-accident", "bmw-championship-2026-bellerive-yardage",
}


def without_documented_errors(source):
    source = re.sub(r'<aside class="update-note".*?</aside>', " ", source, flags=re.S)
    return re.sub(r'<span class="wrong">.*?</span>', " ", source, flags=re.S)


def page(slug):
    return (ROOT / f"{slug}.html").read_text(encoding="utf-8")


class SourcingBatchOneTests(unittest.TestCase):
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
