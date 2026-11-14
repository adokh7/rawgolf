"""Regression guards for the Task 7 high-risk verification batch (15 November 2026).

Fifteen articles flagged by the Task 6 trust audit were checked claim by claim
against published reporting. Each check below pins one confirmed correction, so
a later edit or a regeneration from an old draft cannot quietly bring back the
error. Phrases quoted in an update note or in the corrections log's struck-
through "We wrote" column are allowed, because those quote the error on purpose.
"""
import html
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# slug -> (phrases that must not return, phrases the corrected page must keep)
BATCH = {
    "news-2026-trey-mullinax-pga-tour-suspension": (
        ["Mullinax told us", "Mullinax sits 150th", "That's the whole description",
         "a banned performance-enhancing drug", "rather more bluntly than his lawyers"],
        ["ban on the use of performance-enhancing substances", "finished 150th in the 2025 FedExCup",
         "a week before the 2027 season begins"],
    ),
    "news-2026-muzzy-donohue-3m-open-wild-debut": (
        ["friend from his time in Sea Island"],
        ["australiangolfdigest.com.au", "golf.com/news/underdog-improbable-3m-open-run-inspired-grandma"],
    ),
    "news-2026-liv-golf-staff-terminations": (
        ['voided if they put together a smaller schedule for less money," DeChambeau said',
         "scrapped its New Orleans event in June", "have already returned to the PGA Tour",
         "a PIF spokesperson said", "under contract until 2029"],
        ["anonymous player agent told Skratch", "called off its late-June New Orleans event in April",
         "Commercial Court on 16 April"],
    ),
    "news-2026-trump-lindsey-graham-100-hours-golf": (
        ["and now he's a great friend of mine", "photographed them from across the Potomac",
         "send him packing", "lasting more than four hours"],
        ["now he's a great friend of mine", "Tell Donald Trump to go to hell", "our estimate"],
    ),
    "news-2026-harry-kane-donald-trump-golf-round": (
        ["during World Cup quarter-final week", "former president", "an excellent golfer",
         "Surreal about covers it", "Secret Service", "nearly 80"],
        ["about 18 months earlier", "He's a good golfer", "2-1 after extra time"],
    ),
    "jon-rahm-dodges-pga-tour-pathway-liv-golf-contract": (
        ["its Team Championship cancelled", "$600 million by CBC", "the league's biggest creditor",
         "$25 million charity payment", "may be in bankruptcy court within days",
         "Rahm told Field Level Media"],
        ["was decided at Indianapolis", "$500 million range", "one of the league&rsquo;s largest creditors"],
    ),
    "news-2026-liv-golf-bankruptcy-what-is-confirmed": (
        ["It was a loan, not an investment", "PIF financed LIV through debt rather than equity",
         "on the record.", "turned down the exit in February", "qualified term sheets",
         "designed to generate world ranking points"],
        ["the ownership structure has not changed", "filed for Chapter 11 in New Jersey on 8 September 2026"],
    ),
    "pga-tour-fan-code-of-conduct-gambling": (
        ["first PGA Tour\n            player to partner with a sportsbook", "first PGA Tour player to partner",
         "speak two weeks later", "39\n            states", "39 STATES", "per Sports Illustrated"],
        ["DeChambeau signed with DraftKings in November 2020", "on 30 June"],
    ),
    "news-2026-scottie-scheffler-bryson-dechambeau-penalty": (
        ["Chief referee Grant Moir", '"inadvertent improving"', "more than £200,000",
         "marched to the R&amp;A offices", "I felt like when I played basketball"],
        ["inadvertently improving the area of his intended swing", "$279,887", "Bryson ya cheat"],
    ),
    "news-2026-wyndham-championship-preview": (
        ["think your way around", "said one player on the bubble", "said one analyst",
         "Sungjae Im (+1800)", "Davis Thompson (+4000)", "Justin Thomas (No. 48)", "28-year-old American",
         "Five high-profile withdrawals"],
        ["Sungjae Im (+6100)", "Justin Thomas (No. 40)", "Jordan Spieth (No. 55)", "29-year-old American",
         "7,131 yards"],
    ),
    "news-2026-liv-golf-michigan-martin-kaymer": (
        ["Kaymer told reporters at JCB", "Commissioner Scott O'Neil", "September funding deadline",
         "a September deadline", "linked up back in 2021", "in late June after heat"],
        ["todays-golfer.com", "CEO Scott O'Neil", "when contacted by"],
    ),
    "news-2026-mcilroy-faldo-royal-birkdale": (
        ["career Grand Slam earlier this year", "impromptu interview for Sky Sports",
         "richest regular tournament on tour", "repeated preparatory trips"],
        ["defended his Masters title in April", "posted on X"],
    ),
    "news-2026-jack-nicklaus-career-earnings-vs-modern-pga-tour": (
        ["104 majors", "less than four modern paydays", "never really became wealthy",
         "349th on the career money list", "treat it as an older interview", "first on the career money list"],
        ["won 34 majors", "less than six of Koivun"],
    ),
    "liv-golfer-disqualified-dp-world-tour-q-school": (
        ["Four over on Thursday", "disqualification is mandatory", "decision rather than an accident",
         "Two outlets", "On-site report", "Rule 5.3a has no flex"],
        ["exceptional circumstances", "A 74 in the first round"],
    ),
    "news-2026-blades-brown-19-pga-tour-card": (
        ["10-under 61", "lowest score by a 16- or 17-year-old", "3.5 strokes on approach",
         "Tennessee State Open and Junior Amateur titles", "top 125", "Korn Ferry Tour finals",
         "rounds of 64-72"],
        ["72-67-66-69", "12-under 60", "low amateur at the Tennessee Open", "top 100"],
    ),
}

# Corrections logged for this batch (Donohue needed attribution, not a correction).
LOGGED = set(BATCH) - {"news-2026-muzzy-donohue-3m-open-wild-debut"}


def without_documented_errors(source):
    source = re.sub(r'<aside class="update-note".*?</aside>', " ", source, flags=re.S)
    return re.sub(r'<span class="wrong">.*?</span>', " ", source, flags=re.S)


def page(slug):
    return (ROOT / f"{slug}.html").read_text(encoding="utf-8")


class HighRiskBatchTests(unittest.TestCase):
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

    def test_each_page_has_a_dated_note_and_linked_sources(self):
        for slug in BATCH:
            source = page(slug)
            with self.subTest(slug=slug):
                self.assertIn("Updated 15 November 2026.", source)
                self.assertIn('class="sources"', source)
                article = re.search(r"<article.*?</article>", source, re.S).group(0)
                external = set(re.findall(r'href="(https?://(?!www\.golfraw\.com)[^"]+)"', article))
                self.assertGreaterEqual(len(external), 2, "needs primary-source links")

    def test_dates_and_schema_agree(self):
        for slug in BATCH:
            source = page(slug)
            with self.subTest(slug=slug):
                self.assertIn('"dateModified": "2026-11-15T12:00:00+01:00"', source)
                self.assertIn('<meta property="article:modified_time" content="2026-11-15T12:00:00+01:00">', source)
                for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', source, re.S):
                    json.loads(block)

    def test_corrections_log_records_the_batch(self):
        log = (ROOT / "corrections.html").read_text(encoding="utf-8")
        for slug in LOGGED:
            with self.subTest(slug=slug):
                self.assertRegex(
                    log,
                    r'(?s)<span>LOGGED 15 NOV 2026</span>.*?<div class="e-story"><a href="/' + re.escape(slug) + '"',
                )


if __name__ == "__main__":
    unittest.main()
