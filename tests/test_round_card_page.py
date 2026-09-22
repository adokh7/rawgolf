"""Page contract for The Round Card (tools-scorecard-analyzer.html).

The analysis is pinned in tests/round-card.test.js. These checks keep the
page honest: search positioning, the engine loading before the page uses it,
FAQ schema that mirrors the visible FAQ, labelled score boxes, nothing about a
round in a URL or in analytics, rounds kept in the Locker's scorecards store
(never the Handicap Lie Detector's `rounds`), and copy without filler.
"""

import json
import re
import unittest
from html import unescape
from pathlib import Path

from scripts import tool_inventory as inventory
from scripts.seo_metadata import audit_metadata


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "tools-scorecard-analyzer.html"
BUILDER = ROOT / "scripts" / "build_round_card.py"


def text(fragment):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


class RoundCardPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PAGE.read_text(encoding="utf-8")
        cls.body = cls.source.split("<body")[1]
        cls.script = max(re.findall(r"<script>(.*?)</script>", cls.source, re.S), key=len)

    def test_search_positioning(self):
        meta = audit_metadata(self.source)
        self.assertEqual("Golf Scorecard Analyzer: Find Your Blow-Up Holes | GolfRaw", meta["title"])
        self.assertLessEqual(len(meta["title"]), 60)
        self.assertLessEqual(len(meta["description"]), 160)
        self.assertEqual(["Golf Scorecard Analyzer"], [text(h) for h in re.findall(r"<h1\b[^>]*>(.*?)</h1>", self.source, re.S)])
        self.assertIn('<p class="tool-brand">The Round Card</p>', self.source)
        self.assertIn('<link rel="canonical" href="https://www.golfraw.com/tools-scorecard-analyzer">', self.source)

    def test_inventory_lists_it_in_place_of_the_round_autopsy(self):
        slugs = [tool["slug"] for tool in inventory.TOOLS]
        self.assertIn("tools-scorecard-analyzer", slugs)
        self.assertNotIn("tools-round-autopsy", slugs)
        legacy = {tool["slug"]: tool for tool in inventory.LEGACY_TOOLS}
        self.assertEqual("tools-scorecard-analyzer", legacy["tools-round-autopsy"]["replaced_by"])
        self.assertTrue((ROOT / "tools-round-autopsy.html").exists(), "the legacy URL stays live")
        card = next(t for t in inventory.TOOLS if t["slug"] == "tools-scorecard-analyzer")
        self.assertEqual(("The Round Card", "Golf Scorecard Analyzer", "free"), (card["name"], card["search_name"], card["access"]))

    def test_the_tool_comes_before_the_explainers(self):
        self.assertLess(self.body.index('id="rcSetup"'), self.body.index('class="faq-block'))
        self.assertIn("What is a blow-up hole in golf?", self.body)

    def test_engine_loads_before_the_page_uses_it(self):
        version = re.search(r"^\s*version: (\d+),", (ROOT / "lib/round/round-card.js").read_text(encoding="utf-8"), re.M).group(1)
        model_ver = re.search(r"MODEL_VER = '(\d+)'", BUILDER.read_text(encoding="utf-8")).group(1)
        tag = f'<script src="/lib/round/round-card.js?v={model_ver}"></script>'
        self.assertEqual(version, model_ver, "bump MODEL_VER with the engine version")
        self.assertEqual(1, self.source.count(tag))
        self.assertLess(self.source.index(tag), self.source.index("window.GolfrawRoundCard"))

    def test_faq_schema_mirrors_the_visible_faq(self):
        visible = [text(q) for q in re.findall(r"<summary>(.*?)</summary>", self.body.split('class="faq-block')[1], re.S)]
        self.assertEqual(5, len(visible))
        doc = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', self.source, re.S).group(1))
        nodes = {n["@type"]: n for n in doc["@graph"]}
        self.assertEqual(visible, [q["name"] for q in nodes["FAQPage"]["mainEntity"]])
        self.assertEqual("The Round Card", nodes["WebApplication"]["name"])
        self.assertEqual("Golf Scorecard Analyzer", nodes["BreadcrumbList"]["itemListElement"][-1]["name"])

    def test_nothing_about_a_round_goes_into_a_url(self):
        for forbidden in ("location.hash", "location.search", "pushState", "replaceState", "encodeURIComponent", "btoa("):
            with self.subTest(forbidden):
                self.assertNotIn(forbidden, self.script)
        share = self.script.split("function doShare()")[1].split("function doPrint()")[0]
        self.assertIn("url: URL", share)
        self.assertIn("if (err && err.name === 'AbortError') return;", share)
        self.assertIn("var URL = 'https://www.golfraw.com/tools-scorecard-analyzer';", self.script)

    def test_analytics_sends_only_the_card_labels(self):
        calls = re.findall(r"GRTrack\.(\w+)\(([^()]*(?:\([^()]*\)[^()]*)*)\)", self.script)
        self.assertIn(("completed", "{ round_length: a.holes === 18 ? 'eighteen' : 'nine', detail_mode: a.detail }"), calls)
        for method in ("'copy_result'", "'native_share'", "'print'"):
            self.assertIn(("shared", method), calls)
        self.assertIn(("inputMode", "'import'"), calls)
        self.assertEqual({"completed", "shared", "inputMode"}, {c[0] for c in calls})
        for c in calls:
            self.assertNotRegex(c[1], r"course|score|putts|pen|date|saved|summary")

    def test_score_boxes_are_labelled_numeric_and_errors_name_the_hole(self):
        self.assertIn("box('score', h, 'Hole ' + no + ' score', state.score[h])", self.script)
        self.assertIn("box('putts', h, 'Hole ' + no + ' putts', state.putts[h])", self.script)
        self.assertIn("box('pen', h, 'Hole ' + no + ' penalty strokes', state.pen[h], '0')", self.script)
        self.assertIn('inputmode="numeric" pattern="[0-9]*" enterkeyhint="next"', self.script)
        self.assertIn("'aria-label=\"Hole ' + no + ', par ' + state.pars[h] + '. Change par\">'", self.script)
        self.assertIn('id="rcErr" role="alert"', self.body)
        self.assertIn("'Hole ' + e.hole + ': putts go from 0 to 6.'", self.script)
        self.assertNotIn('data-k="fir"', self.script, "fairways are not collected")

    def test_rounds_live_in_the_scorecards_store(self):
        self.assertIn("L.saveScorecard(record())", self.script)
        self.assertIn("L.listScorecards()", self.script)
        for forbidden in ("saveRounds", "pushScoresToRounds", "L.clear("):
            self.assertNotIn(forbidden, self.script)
        self.assertIn("var LS_DRAFT = 'golfraw_roundcard_draft';", self.script)
        self.assertIn("if (state.id && L && dirty) saveRound(true);", self.script, "opening a round must not rewrite it")

    def test_delete_asks_first(self):
        self.assertIn("Delete this round for good?", self.script)
        self.assertIn('data-act="keep">Keep it</button>', self.script)
        self.assertIn("li.querySelector('[data-act=\"keep\"]').focus();", self.script, "focus lands on the safe choice")

    def test_required_guide_links_are_there_once(self):
        for href in ("/guides-the-three-feet-that-decide-whether-you-three-putt", "/news-2026-raw-golf-honest-practice-guide",
                     "/tools-tendency-engine"):
            self.assertEqual(1, self.body.count(f'href="{href}"'), href)

    def test_copy_is_plain_golf_not_filler(self):
        visible = text(self.body.split("<footer")[0]).lower()
        for phrase in ("unlock", "seamless", "elevate", "game-changing", "ultimate", "whether you", "advanced analytics",
                       "leverage", "journey", "cause of death"):
            with self.subTest(phrase):
                self.assertNotIn(phrase, visible)
        self.assertIn("round’s done.", visible)
        self.assertIn("what cost you this round?", visible)

    def test_legacy_pages_point_here(self):
        for page in ("tools-round-autopsy.html", "tools-tilt-meter.html"):
            source = (ROOT / page).read_text(encoding="utf-8")
            with self.subTest(page):
                self.assertEqual(1, source.count('data-gr-placement="legacy_notice"'))
                self.assertIn('<a href="/tools-scorecard-analyzer"', source)


if __name__ == "__main__":
    unittest.main()
