"""Methodology contract for The Plays Like Calculator and The Tee Box Reality Check.

The models have their own sweeps in tests/plays-like.test.js and
tests/tee-box.test.js. These checks keep the hand-written pages honest: the
unsupported rules of thumb stay gone, every method line has a source, the
static numbers in the copy match what the models return, and the search-facing
title and H1 from the retitle work stay put.
"""

import json
import re
import subprocess
import unittest
from html import unescape
from pathlib import Path

from scripts.seo_metadata import audit_metadata


ROOT = Path(__file__).resolve().parents[1]
PLAYS = ROOT / "tools-plays-like.html"
TEE = ROOT / "tools-tee-box-check.html"


def text(fragment):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def node(script):
    out = subprocess.run(["node", "-e", script], cwd=ROOT, capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def module_version(path):
    return re.search(r"^\s*version: (\d+),", (ROOT / path).read_text(encoding="utf-8"), re.M).group(1)


class PlaysLikeMethodTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PLAYS.read_text(encoding="utf-8")
        cls.visible = text(cls.source.split("<body>")[1])

    def test_search_title_and_h1_are_unchanged(self):
        self.assertEqual("Golf Altitude & Elevation Distance Calculator | GolfRaw", audit_metadata(self.source)["title"])
        h1s = [text(h) for h in re.findall(r"<h1\b[^>]*>(.*?)</h1>", self.source, re.S)]
        self.assertEqual(["Golf Altitude & Elevation Distance Calculator"], h1s)
        self.assertIn('<p class="tool-brand">The Plays Like Calculator</p>', self.source)

    def test_model_loads_at_its_version_before_the_page_uses_it(self):
        ver = module_version("lib/distance/plays-like.js")
        tag = f'<script src="/lib/distance/plays-like.js?v={ver}"></script>'
        self.assertEqual(1, self.source.count(tag))
        self.assertLess(self.source.index(tag), self.source.index("window.GolfrawPlaysLike"))

    def test_unsupported_rules_of_thumb_are_gone(self):
        for stale in ("ALT_PCT_PER_1000FT", "TEMP_YDS_PER_10F", "2% extra carry", "2 yards per 10",
                      "2 percent extra carry", "16 yards shorter", "designed to be opened mid-round"):
            with self.subTest(stale):
                self.assertNotIn(stale, self.source)

    def test_method_sources_limits_and_rules_are_visible(self):
        for heading in ("Method &amp; Sources", "How the estimate works", "Limitations", "Using it on the course"):
            with self.subTest(heading):
                self.assertIn(heading, self.source)
        for url in ("https://www.titleist.com/learning-lab/performance/altitude-and-golf-ball-flight",
                    "https://www.titleist.com/learning-lab/performance/temperature-and-golf-ball-performance",
                    "https://www.andrewricegolf.com/andrew-rice-golf/2023/3/a-better-way-to-play-in-the-wind",
                    "https://www.randa.org/en/rog/the-rules-of-golf/rule-4"):
            with self.subTest(url):
                self.assertIn(f'href="{url}"', self.source)
        self.assertIn("Rule 4.3", self.visible)
        self.assertIn("does not let you measure elevation changes", self.visible)
        self.assertIn("Doing the sums before the round is allowed", self.visible)

    def test_static_numbers_match_the_model(self):
        got = node(
            "const P=require('./lib/distance/plays-like.js');"
            "const b={temp:70,alt:0,wind:0,windDir:'head',slope:0};"
            "const r=o=>P.compute(Object.assign({},b,o));"
            "console.log(JSON.stringify({denver150:Math.round(r({yards:150,alt:5280}).playsLike),"
            "cold150:r({yards:150,temp:40}).playsLike,cold250:r({yards:250,temp:40}).parts.temp,"
            "head10:Math.round(r({yards:150,wind:10}).playsLike),t200:r({yards:200,temp:50}).parts.temp}));"
        )
        self.assertEqual(141, got["denver150"])
        self.assertIn("A full 150-yard shot there plays about 141", self.visible)
        self.assertTrue(153 <= got["cold150"] <= 154)
        self.assertIn("150-yard shot plays about 153 to 154 yards", self.visible)
        self.assertEqual(6, round(got["cold250"]))
        self.assertIn("a 250-yard drive loses about 6 yards", self.visible)
        self.assertEqual(160, got["head10"])
        self.assertEqual(3, round(got["t200"]))

    def test_faq_schema_includes_the_rules_question(self):
        doc = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', self.source, re.S).group(1))
        faq = next(n for n in doc["@graph"] if n["@type"] == "FAQPage")
        names = [q["name"] for q in faq["mainEntity"]]
        self.assertIn("Can I use a plays-like calculator in a competition?", names)
        self.assertFalse(any("2 percent" in q["acceptedAnswer"]["text"] for q in faq["mainEntity"]))

    def test_analytics_wiring_is_unchanged_and_the_handoff_is_marked(self):
        self.assertEqual(1, self.source.count("GRTrack.completed()"))
        self.assertIn("data-gr-inputs", self.source)
        self.assertIn('id="runBtn" data-gr-run', self.source)
        self.assertRegex(self.source, r'data-gr-placement="result_distance_check">[^<]*<a href="/tools-club-distance-calculator">')


class TeeBoxMethodTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = TEE.read_text(encoding="utf-8")
        cls.visible = text(cls.source.split("<body>")[1])

    def test_search_title_and_h1_are_unchanged(self):
        meta = audit_metadata(self.source)
        self.assertEqual("What Tees Should I Play? Tee Calculator by Driver Distance", meta["title"])
        h1s = [text(h) for h in re.findall(r"<h1\b[^>]*>(.*?)</h1>", self.source, re.S)]
        self.assertEqual(["What Tees Should I Play?"], h1s)
        self.assertIn('<p class="tool-brand">The Tee Box Reality Check</p>', self.source)

    def test_description_names_the_chart_and_is_mirrored(self):
        meta = audit_metadata(self.source)
        self.assertIn("Tee It Forward chart", meta["description"])
        self.assertTrue(120 <= len(meta["description"]) <= 155, len(meta["description"]))
        for field in ("og:description", "twitter:description"):
            self.assertEqual(meta["description"], meta[field])

    def test_models_load_in_order_at_their_versions(self):
        dist = f'<script src="/lib/distance/club-distance.js?v={module_version("lib/distance/club-distance.js")}"></script>'
        tee = f'<script src="/lib/distance/tee-box.js?v={module_version("lib/distance/tee-box.js")}"></script>'
        self.assertEqual(1, self.source.count(dist))
        self.assertEqual(1, self.source.count(tee))
        self.assertLess(self.source.index(dist), self.source.index(tee))
        self.assertLess(self.source.index(tee), self.source.index("window.GolfrawTeeBox"))

    def test_the_multiplier_and_the_unsourced_stroke_rule_are_gone(self):
        for stale in ("YARD_MULTIPLIER", "SHOTS_PER_200", "carry by 28", "× 28", "x 28", "1.5 shots",
                      "six shots"):
            with self.subTest(stale):
                self.assertNotIn(stale, self.source)

    def test_method_sources_and_limits_are_visible(self):
        for heading in ("Method &amp; Sources", "How the estimate works", "A second opinion", "Limitations"):
            with self.subTest(heading):
                self.assertIn(heading, self.source)
        self.assertIn('href="https://pdf.pgalinks.com/p-g-a/Tee_It_Forward_Guidelines.pdf"', self.source)
        self.assertIn("golfer-experience-information.html", self.source)
        self.assertIn("1 stroke per 220 yards", self.visible)

    def test_static_chart_numbers_match_the_model(self):
        got = node(
            "const T=require('./lib/distance/tee-box.js');"
            "console.log(JSON.stringify([100,200,250,275].map(t=>T.courseRange(t).range)));"
        )
        self.assertEqual([[2100, 2300], [5200, 5400], [6200, 6400], [6700, 6900]], got)
        self.assertIn("a 200-yard drive suggests 5,200 to 5,400 yards, a 250-yard drive 6,200 to 6,400", self.visible)
        self.assertIn("from 2,100 to 2,300 yards for a 100-yard drive up to 6,700 to 6,900 for a 275-yard drive", self.visible)
        bogey600 = node("const T=require('./lib/distance/tee-box.js');console.log(T.strokesPerYard(92)*600);")
        self.assertTrue(3.5 <= bogey600 < 4)
        self.assertIn("close to four strokes a round", self.visible)

    def test_analytics_wiring_is_unchanged_and_the_handoff_is_marked(self):
        self.assertEqual(1, self.source.count("GRTrack.completed()"))
        self.assertIn('id="runBtn" data-gr-run', self.source)
        self.assertRegex(self.source, r'data-gr-placement="input_distance_check">[^<]*<a href="/tools-club-distance-calculator">')

    def test_model_contracts_pass(self):
        for script in ("plays-like.test.js", "tee-box.test.js"):
            with self.subTest(script):
                result = subprocess.run(["node", str(ROOT / "tests" / script)], capture_output=True, text=True)
                self.assertEqual(0, result.returncode, result.stderr or result.stdout)


if __name__ == "__main__":
    unittest.main()
