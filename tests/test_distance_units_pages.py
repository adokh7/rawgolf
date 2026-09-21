"""Units wiring on the four distance tools.

The conversion maths and the equivalence of yards and metres are pinned in
tests/units.test.js and tests/locker-units.test.js. These checks keep the
pages honest: one URL per tool, every page on the shared units layer, a
labelled switch the analytics layer ignores, and no unit data sent anywhere.
"""

import re
import unittest
from html import unescape
from pathlib import Path

from scripts import wire_locker


ROOT = Path(__file__).resolve().parents[1]
PAGES = {
    "tools-club-distance-calculator.html": ("Golf Club Distance Calculator", "Golf Club Distance Calculator: Yards or Metres | GolfRaw"),
    "tools-plays-like.html": ("Golf Altitude & Elevation Distance Calculator", "Golf Altitude & Elevation Distance Calculator | GolfRaw"),
    "tools-tee-box-check.html": ("What Tees Should I Play?", "What Tees Should I Play? Tee Calculator by Driver Distance"),
    "tools-bag-audit.html": ("Golf Club Gapping Calculator", "Golf Club Gapping Calculator: Find Gaps & Overlaps | GolfRaw"),
}


def text(fragment):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def version(path):
    return re.search(r"^\s*version: (\d+),", (ROOT / path).read_text(encoding="utf-8"), re.M).group(1)


class DistanceUnitsPagesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = {name: (ROOT / name).read_text(encoding="utf-8") for name in PAGES}

    def test_titles_and_h1s_are_unchanged(self):
        for name, (h1, title) in PAGES.items():
            with self.subTest(name):
                s = self.src[name]
                self.assertEqual(title, unescape(re.search(r"<title>(.*?)</title>", s).group(1)))
                self.assertEqual([h1], [text(h) for h in re.findall(r"<h1\b[^>]*>(.*?)</h1>", s, re.S)])

    def test_one_url_per_tool(self):
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"/(meters|metres|yards|metric|imperial)\b", sitemap))
        for name in PAGES:
            self.assertFalse((ROOT / name.replace(".html", "-metres.html")).exists())
            self.assertFalse((ROOT / name.replace(".html", "-meters.html")).exists())

    def test_every_page_loads_the_units_layer_before_using_it(self):
        tag = f'<script src="/lib/distance/units.js?v={version("lib/distance/units.js")}"></script>'
        for name in PAGES:
            with self.subTest(name):
                s = self.src[name]
                self.assertEqual(1, s.count(tag))
                self.assertLess(s.index(tag), s.index("window.GolfrawUnits"))

    def test_the_locker_version_is_the_same_everywhere(self):
        for page in sorted(ROOT.glob("*.html")):
            s = page.read_text(encoding="utf-8")
            for v in re.findall(r"/lib/locker/(?:schema|store|drawer)\.js\?v=(\d+)", s):
                with self.subTest(page.name):
                    self.assertEqual(wire_locker.VER, v)

    def test_switches_are_labelled_and_ignored_by_analytics(self):
        dc = self.src["tools-club-distance-calculator.html"]
        self.assertRegex(dc, r'<fieldset class="cd-seg cd-units" data-gr-ignore>\s*<legend class="cd-legend">Units')
        self.assertIn('<input type="radio" name="cdUnit" value="m">', dc)
        for name, group in (("tools-plays-like.html", "plUnits"), ("tools-tee-box-check.html", "tbUnits"),
                            ("tools-bag-audit.html", "baUnits")):
            with self.subTest(name):
                s = self.src[name]
                block = s.split(f'id="{group}"')[1].split("</div>")[0]
                self.assertEqual(2, len(re.findall(r'<button type="button" data-(?:v|units)="(?:yards|meters)" data-gr-ignore aria-pressed="(?:true|false)">', block)))
                self.assertRegex(s, r'aria-labelledby="(plUnitLab|tbUnitLab|baUnitLab)"')
        pl = self.src["tools-plays-like.html"]
        for group, label in (("tempUnit", "Temperature unit"), ("windUnit", "Wind speed unit")):
            self.assertIn(f'id="{group}" role="group" aria-label="{label}"', pl)

    def test_the_preference_claim_is_visible_where_it_is_true(self):
        for name in PAGES:
            with self.subTest(name):
                self.assertIn("GolfRaw remembers it on this device", text(self.src[name]))

    def test_no_unit_or_value_reaches_analytics(self):
        helper = (ROOT / "lib" / "analytics" / "tool-events.js").read_text(encoding="utf-8")
        self.assertNotIn("unit_system", helper)
        self.assertNotRegex(helper, r"\bunits?\b\s*:")
        for name in PAGES:
            with self.subTest(name):
                for call in re.findall(r"GRTrack\.(?:completed|shared)\(([^)]*)\)", self.src[name]):
                    self.assertNotRegex(call, r"unit|yard|metre|meter|temp|wind")

    def test_bag_audit_switch_styles_stay_out_of_the_shared_shell(self):
        self.assertIn("<!-- UNITS:START -->", self.src["tools-bag-audit.html"])
        for generated in ("tools-field-reader.html", "tools-tendency-engine.html", "tools-club-distance-calculator.html"):
            with self.subTest(generated):
                self.assertNotIn(".unit-seg", (ROOT / generated).read_text(encoding="utf-8"))

    def test_bag_audit_keeps_yard_thresholds_and_says_so(self):
        s = self.src["tools-bag-audit.html"]
        self.assertIn("var GAP_BIG = BA.GAP_BIG;", s)
        self.assertIn("20 yards stays 20 yards, not 20 metres", text(s))
        self.assertNotRegex(s, r"GAP_BIG\s*=\s*\d")

    def test_tee_box_and_distance_check_share_the_chart(self):
        tee = (ROOT / "lib" / "distance" / "tee-box.js").read_text(encoding="utf-8")
        self.assertIn("D.teeRange(total, total)", tee)
        self.assertNotIn("TEE_IT_FORWARD[", tee.replace("D.TEE_IT_FORWARD", ""))
        dc = self.src["tools-club-distance-calculator.html"]
        self.assertIn("res.tee.courseRaw[0]", dc)


if __name__ == "__main__":
    unittest.main()
