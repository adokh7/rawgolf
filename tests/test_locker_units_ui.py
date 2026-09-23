"""Unit wording in the shared Locker drawer and the tools that read it.

The conversion maths is pinned in tests/units.test.js and
tests/locker-units.test.js, and The Standing Order's own unit helpers in
tests/standing-order-units.test.js. These checks keep the *labels* honest:
a stored carry is shown in the unit the profile records it in, the interface
spells it "metres", and nothing on a tool page announces a unit it did not
check.
"""

import re
import unittest
from pathlib import Path

from scripts import tool_inventory, wire_locker

ROOT = Path(__file__).resolve().parents[1]
DRAWER = (ROOT / "lib" / "locker" / "drawer.js").read_text(encoding="utf-8")
TOOL_PAGES = sorted(ROOT.glob("tools-*.html"))


class LockerUnitsUiTests(unittest.TestCase):
    def test_the_drawer_labels_a_carry_with_the_profile_unit(self):
        self.assertIn("var unit = profile.units === 'meters' ? 'm' : 'yd';", DRAWER)
        self.assertIn("' ' + unit + '</span>", DRAWER)
        self.assertNotIn(" yd</span>", DRAWER, "a stored carry must never be labelled yd on a metric profile")
        row = DRAWER.split("var rows = [];")[1].split("clubsHtml =")[0]
        self.assertNotIn("yd", row, "the row markup carries no unit of its own: " + row.strip()[:120])

    def test_the_drawer_switch_offers_metres_and_stores_meters(self):
        # The stored value stays 'meters': it is the profile's enum, and
        # renaming it would orphan every profile already on a device.
        self.assertIn("<option value=\"meters\"'", DRAWER)
        self.assertIn(">Metres</option>", DRAWER)
        self.assertNotIn(">Meters</option>", DRAWER)
        self.assertIn("'yards', 'meters'", (ROOT / "lib" / "locker" / "store.js").read_text(encoding="utf-8"))

    def test_a_units_save_keeps_the_typed_profile_and_confirms_on_screen(self):
        # setUnits emits a store event, and the refresh it triggers rebuilds the
        # panel: the fields must be read before that, and the confirmation
        # written after it, or the typed name is lost and nobody sees the save.
        handler = DRAWER.split("$('gr-lk-save').addEventListener")[1].split("$('gr-lk-export')")[0]
        self.assertLess(handler.index("var profile = {"), handler.index("L.setUnits"))
        self.assertIn("return L.saveProfile(profile);", handler)
        self.assertLess(handler.index("return refresh();"), handler.index("'Profile saved on this device.'"))

    def test_no_tool_page_says_meters_in_its_interface(self):
        for page in TOOL_PAGES:
            s = page.read_text(encoding="utf-8")
            with self.subTest(page.name):
                self.assertNotIn(">Meters<", s)
                self.assertNotIn("meters carry", s)
                # value="meters" and === 'meters' are data, not words on screen
                visible = re.sub(r"(value=\"meters\"|'meters'|\"meters\")", "", s)
                self.assertNotRegex(visible, r"\bmeters\b", "the interface spells it metres")

    def test_the_standing_order_keeps_its_thresholds_in_yards(self):
        s = (ROOT / "tools-standing-order.html").read_text(encoding="utf-8")
        self.assertIn("var M_PER_YD = 0.9144;", s)
        self.assertIn("var hole = thr(GAP_HOLE), dup = thr(GAP_DUP);", s)
        self.assertRegex(s, r"GAP_HOLE = 25;\s*/\* yards")
        self.assertIn("25-yard hole in the bag stays a 25-yard hole", s)

    def test_a_unit_change_elsewhere_reaches_the_standing_order(self):
        s = (ROOT / "tools-standing-order.html").read_text(encoding="utf-8")
        self.assertIn("else if (kind === 'profile') syncUnits();", s)
        self.assertIn("return L.getOrStartSession();", s.split("function syncUnits(")[1].split("function setState(")[0])

    def test_every_page_that_loads_the_drawer_loads_the_current_version(self):
        tag = '<script src="/lib/locker/drawer.js?v=%s" defer></script>' % wire_locker.VER
        for tool in tool_inventory.tracked_pages():
            page = ROOT / (tool["slug"] + ".html")
            with self.subTest(tool["slug"]):
                self.assertIn(tag, page.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
