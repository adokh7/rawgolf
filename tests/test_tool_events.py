"""Wiring contract for the shared tool-events layer (lib/analytics/tool-events.js).

The behaviour of the layer itself is covered by tests/tool-events.test.js. These
checks keep every tool page wired to it, keep its registry in step with the
tool inventory, and keep golfer-entered values out of every call site.
"""

import re
import subprocess
import unittest
from pathlib import Path

from scripts import tool_inventory as inventory
from scripts import wire_tool_events


ROOT = Path(__file__).resolve().parents[1]
HELPER = (ROOT / "lib" / "analytics" / "tool-events.js").read_text(encoding="utf-8")
HAND_WRITTEN = (
    "tools-settle-up-calculator", "tools-tee-box-check", "tools-plays-like", "tools-bag-audit",
    "tools-handicap-detector", "tools-round-autopsy", "tools-tilt-meter", "tools-gimme-audit",
    "tools-the-grudge-match",
)
GENERATED = {
    "tools-standing-order": "build_standing_order.py",
    "tools-tendency-engine": "build_tendency_engine.py",
    "tools-field-reader": "build_field_reader.py",
    "tools-coach-report": "build_coach_report.py",
}
# Every argument a page may pass to GRTrack: fixed modes, share methods, codes.
ALLOWED_ARGS = {
    "", "'manual'", "'sample'", "'import'", "'copy_result'", "'copy_link'", "'native_share'",
    "'download'", "'print'", "'import_too_large'", "'import_unreadable'", "'feed_unavailable'",
    "'share_link_too_long'", "'shared_link_invalid'", "method",
    # The Distance Check reports which kind of number it started from; the
    # helper enum-validates it (tests/tool-events.test.js) and the model can only
    # return the four anchor ids checked below.
    "{ anchor_type: res.anchor }",
    # The Settle Up reports which games were settled and gross or net: two
    # enums the helper validates, built from the page's own fixed choices.
    "{ game_type: gameType, scoring_mode: scoringMode }",
    # The Round Card reports nine or eighteen holes and whether putts and
    # penalties were entered: two enums, never a value from the card.
    "{ round_length: a.holes === 18 ? 'eighteen' : 'nine', detail_mode: a.detail }",
}
CALL = re.compile(r"GRTrack\.(\w+)\(([^()]*)\)")


def page(slug):
    return (ROOT / f"{slug}.html").read_text(encoding="utf-8")


class ToolEventsWiringTests(unittest.TestCase):
    def test_helper_registry_matches_the_tool_inventory(self):
        registry = dict(re.findall(r"'(tools-[a-z0-9-]+)': \['[a-z_]+', '([^']+)'", HELPER))
        # Legacy pages (off the hub, still live) keep their analytics.
        expected = {tool["slug"]: tool["name"] for tool in inventory.tracked_pages()}
        self.assertEqual(expected, registry)
        self.assertIn("'tools-coach-report': ['coach_report', 'The Coach Report', 'pro_preview']", HELPER)

    def test_every_tool_page_loads_the_helper_once_at_the_current_version(self):
        tag = f'<script src="/lib/analytics/tool-events.js?v={wire_tool_events.VER}" defer></script>'
        for tool in inventory.tracked_pages():
            with self.subTest(tool["slug"]):
                source = page(tool["slug"])
                self.assertEqual(1, source.count(tag))
                self.assertEqual(1, source.count('src="/lib/analytics/tool-events.js'))
        self.assertEqual(0, wire_tool_events.main(["--check"]))

    def test_hand_written_tools_complete_only_on_the_valid_result_path(self):
        for slug in HAND_WRITTEN:
            with self.subTest(slug):
                source = page(slug)
                # The Settle Up passes two enums (game and scoring); the rest pass nothing.
                call = (r"GRTrack\.completed\(\{ game_type: gameType, scoring_mode: scoringMode \}\)"
                        if slug == "tools-settle-up-calculator" else r"GRTrack\.completed\(\)")
                self.assertEqual(1, len(re.findall(call, source)))
                self.assertEqual(1, source.count("GRTrack.completed("))
                self.assertRegex(
                    source,
                    r"if \(window\.GRTrack\) " + call + r";\n\s*if \(window\.RawGolf\) RawGolf\.save\(cardData\(\)\);",
                )
                self.assertIn('src="./rawgolf-tools.js?v=2"', source)
                self.assertIn("data-gr-inputs", source)

    def test_generated_tools_are_wired_in_their_builders(self):
        for slug, builder in GENERATED.items():
            with self.subTest(slug):
                source = (ROOT / "scripts" / builder).read_text(encoding="utf-8")
                self.assertIn("GRTrack.completed()", source)
                self.assertIn("GRTrack.completed()", page(slug))

    def test_calls_only_pass_fixed_values(self):
        sources = {slug: page(slug) for slug in [t["slug"] for t in inventory.TOOLS]}
        sources["rawgolf-tools.js"] = (ROOT / "rawgolf-tools.js").read_text(encoding="utf-8")
        for name, source in sources.items():
            for fn, args in CALL.findall(source):
                with self.subTest(file=name, call=f"GRTrack.{fn}({args})"):
                    self.assertIn(args.strip(), ALLOWED_ARGS)
                    self.assertNotEqual("track", fn, "pages use the named helpers, not raw track()")

    def test_helper_has_no_value_bearing_parameters(self):
        events = re.search(r"var EVENTS = \{(.*?)\};", HELPER, re.S).group(1)
        keys = set(re.findall(r"'([a-z_]+)'", events))
        self.assertEqual(
            {"tool_id", "tool_name", "tool_access", "page_path", "view_type", "input_mode",
             "share_method", "from_tool", "to_tool", "placement", "error_code", "anchor_type",
             "game_type", "scoring_mode", "round_length", "detail_mode"},
            keys,
        )
        for reserved in ("round_logged", "pro_preview_viewed", "pro_waitlist_joined", "review_unlocked"):
            self.assertNotIn(reserved + ":", events)

    def test_distance_anchor_types_are_the_helper_enum(self):
        helper_enum = set(re.search(r"anchor_type: \[([^\]]*)\]", HELPER).group(1).replace("'", "").replace(" ", "").split(","))
        model = (ROOT / "lib" / "distance" / "club-distance.js").read_text(encoding="utf-8")
        page = (ROOT / "tools-club-distance-calculator.html").read_text(encoding="utf-8")
        radios = set(re.findall(r'name="cdAnchor" value="([a-z_]+)"', page))
        self.assertEqual({"driver_carry", "iron_carry", "swing_speed", "handicap_band"}, helper_enum)
        self.assertEqual(helper_enum, radios)
        self.assertIn("anchor: anchor", model)

    def test_chained_score_never_reaches_the_query_string(self):
        gimme = page("tools-gimme-audit")
        self.assertIn("'tools-handicap-detector#score=' + chained", gimme)
        self.assertNotIn("?score=", gimme)
        detector = page("tools-handicap-detector")
        scrub = detector.index("window.history.replaceState(null, '', window.location.pathname")
        self.assertLess(scrub, detector.index("score < 55"), "scrub before validation")
        self.assertLess(scrub, detector.index("gtag('config'"), "scrub before the GA4 page_view")

    def test_behaviour_contract_passes(self):
        result = subprocess.run(
            ["node", str(ROOT / "tests" / "tool-events.test.js")], capture_output=True, text=True
        )
        self.assertEqual(0, result.returncode, result.stderr or result.stdout)


if __name__ == "__main__":
    unittest.main()
