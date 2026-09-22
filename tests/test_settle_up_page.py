"""Page contract for The Settle Up (tools-settle-up-calculator.html), V2.

The rules and the money are pinned in tests/settle-up.test.js. These checks
keep the page honest: the search positioning from the retitle stays, the
engine loads before the page uses it, the FAQ schema mirrors the visible FAQ,
nothing about a round ever goes into a URL or to analytics, and the copy
stays practical rather than casino.
"""

import json
import re
import unittest
from html import unescape
from pathlib import Path

from scripts.seo_metadata import audit_metadata


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "tools-settle-up-calculator.html"


def text(fragment):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def version(path):
    return re.search(r"^\s*version: (\d+),", (ROOT / path).read_text(encoding="utf-8"), re.M).group(1)


class SettleUpPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PAGE.read_text(encoding="utf-8")
        cls.body = cls.source.split("<body>")[1]
        cls.script = max(re.findall(r"<script>(.*?)</script>", cls.source, re.S), key=len)

    def test_search_positioning_is_unchanged(self):
        meta = audit_metadata(self.source)
        self.assertEqual("Golf Skins Calculator: Carryovers & Nassau | GolfRaw", meta["title"])
        self.assertEqual(["Golf Skins Calculator"], [text(h) for h in re.findall(r"<h1\b[^>]*>(.*?)</h1>", self.source, re.S)])
        self.assertIn('<p class="tool-brand">The Settle Up</p>', self.source)
        self.assertIn('<link rel="canonical" href="https://www.golfraw.com/tools-settle-up-calculator">', self.source)

    def test_the_calculator_comes_before_the_explainers(self):
        self.assertLess(self.body.index('id="suSetup"'), self.body.index('class="faq-block'))
        self.assertIn('How do golf skins work?', self.body)

    def test_engine_loads_before_the_page_uses_it(self):
        core = f'<script src="/lib/games/settle-core.js?v={version("lib/games/settle-core.js")}"></script>'
        rules = f'<script src="/lib/games/settle-up.js?v={version("lib/games/settle-up.js")}"></script>'
        self.assertEqual(1, self.source.count(core))
        self.assertEqual(1, self.source.count(rules))
        self.assertLess(self.source.index(core), self.source.index(rules))
        self.assertLess(self.source.index(rules), self.source.index("window.GolfrawSettleUp"))

    def test_faq_schema_mirrors_the_visible_faq(self):
        visible = [text(q) for q in re.findall(r'<div class="faq-item">\s*<h3>(.*?)</h3>', self.body, re.S)]
        self.assertEqual(["What is a skin in golf?", "What happens when a skin is tied?",
                          "What is the difference between gross and net skins?", "How does a Nassau work?",
                          "How do presses work in golf?"], visible)
        doc = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', self.source, re.S).group(1))
        faq = next(n for n in doc["@graph"] if n["@type"] == "FAQPage")
        self.assertEqual(visible, [q["name"] for q in faq["mainEntity"]])
        types = [n["@type"] for n in doc["@graph"]]
        self.assertIn("WebApplication", types)
        self.assertIn("BreadcrumbList", types)

    def test_money_is_not_dollars_by_default_of_code(self):
        self.assertIn("var SYMBOLS = { usd: '$', eur: '€', gbp: '£', pts: 'pts' };", self.script)
        self.assertNotRegex(self.script, r"'\$' \+")
        for label in ('aria-label="Dollars">$', 'aria-label="Euros">€', 'aria-label="Pounds">£', 'data-v="pts"'):
            self.assertIn(label, self.body)

    def test_nothing_about_a_round_goes_into_a_url(self):
        for forbidden in ("location.hash", "location.search", "pushState", "replaceState", "encodeURIComponent", "btoa("):
            with self.subTest(forbidden):
                self.assertNotIn(forbidden, self.script)
        share = self.script.split("function doShare()")[1].split("function cardData()")[0]
        self.assertIn("url = 'https://www.golfraw.com/tools-settle-up-calculator'", share)
        self.assertIn("if (err && err.name === 'AbortError') return;", share)

    def test_analytics_sends_only_the_game_labels(self):
        calls = re.findall(r"GRTrack\.(\w+)\(([^()]*)\)", self.script)
        self.assertIn(("completed", "{ game_type: gameType, scoring_mode: scoringMode }"), calls)
        self.assertIn(("shared", "'copy_result'"), calls)
        self.assertIn(("shared", "'native_share'"), calls)
        self.assertEqual({"completed", "shared"}, {c[0] for c in calls})
        self.assertRegex(self.script, r"var gameType = state\.games\.skins && state\.games\.nassau \? 'skins_nassau' : state\.games\.skins \? 'skins' : 'nassau';")
        self.assertIn("var scoringMode = state.scoring;", self.script)

    def test_score_boxes_are_labelled_and_numeric(self):
        self.assertIn("'aria-label=\"' + esc(nameOf(q)) + ', hole ' + (h + 1) + '\"></td>'", self.script)
        self.assertIn('inputmode="numeric" pattern="[0-9]*" enterkeyhint="next"', self.script)
        self.assertIn('id="scoreErr" role="alert"', self.body)

    def test_player_count_changes_keep_the_card_in_step(self):
        fn = self.script.split("function setCount(n)")[1].split("/* ==================== SETUP")[0]
        self.assertIn("while (state.scores.length < n) state.scores.push(new Array(HOLES).fill(null));", fn)
        self.assertIn("state.scores.length = n;", fn)
        self.assertIn("state.players.length = n;", fn)

    def test_required_guide_links_stay(self):
        for href in ("/guides-how-to-play-in-a-golf-pro-am-costs-etiquette", "/charity-golf-scrambles-access-guide"):
            self.assertEqual(1, self.body.count(f'href="{href}"'))

    def test_copy_is_practical_not_casino(self):
        visible = text(self.body.split("<footer")[0]).lower()
        for phrase in ("crush", "dominate", "win big", "maximi", "atm", "bandit", "jackpot", "choker",
                       "seamless", "unlock", "whether you"):
            with self.subTest(phrase):
                self.assertNotIn(phrase, visible)
        self.assertIn("round's over. settle it cleanly.", visible)


if __name__ == "__main__":
    unittest.main()
