"""Search-intent titles for four free tools, and the description cut that broke them.

The Aug 2026 SEO pass cut every over-long description at a word boundary and
added a period, publishing fragments such as "...and the club you." The first
tests pin the repaired helper against those real inputs; the rest pin the
search-name / product-name split on the four retitled tool pages.
"""

import html
import re
import unittest
from pathlib import Path

from scripts import tool_inventory as inventory
from scripts.fix_seo_audit import finish_description
from scripts.seo_metadata import audit_metadata, metadata_override_for


ROOT = Path(__file__).resolve().parents[1]

# Descriptions as they stood before the word-cut pass (git 63c4a860^).
ORIGINAL_DESCRIPTIONS = {
    "plays-like": (
        "Free golf plays-like calculator. Enter yardage, temperature, wind, altitude "
        "and slope to get the real distance your shot is playing — and the club you "
        "should actually pull."
    ),
    "bag-audit": (
        "Free golf club gapping calculator. Enter your carry distances, how often you "
        "use each club and how much you trust it, and find out which clubs are "
        "passengers, which are redundant, and where the holes are."
    ),
    "settle-up": (
        "Free golf betting calculator. Work out Nassau, skins with carryovers, automatic "
        "2-down presses and junk, then get a clean who-owes-who card for the group chat."
    ),
}

RETITLED = {
    "tools-settle-up-calculator": ("Golf Skins Calculator", "The Settle Up"),
    "tools-tee-box-check": ("What Tees Should I Play?", "The Tee Box Reality Check"),
    "tools-plays-like": ("Golf Altitude & Elevation Distance Calculator", "The Plays Like Calculator"),
    "tools-bag-audit": ("Golf Club Gapping Calculator", "The Bag Audit"),
}


def _text(fragment):
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


class FinishDescriptionTests(unittest.TestCase):
    def test_word_cut_never_ends_in_a_fake_period(self):
        for key, original in ORIGINAL_DESCRIPTIONS.items():
            with self.subTest(key):
                result = finish_description(original)
                self.assertLessEqual(len(result), 155)
                if result.endswith("."):
                    # A period is only allowed where the source had a real break.
                    body = result[:-1]
                    boundary = original[len(body):len(body) + 3]
                    self.assertRegex(boundary, r"^(?:[.!?]|\s[—–]\s|[;:]\s)", result)
                else:
                    self.assertTrue(result.endswith("…"), result)

    def test_clause_break_is_preferred_over_a_word_cut(self):
        result = finish_description(ORIGINAL_DESCRIPTIONS["plays-like"])
        self.assertTrue(result.endswith("the real distance your shot is playing."), result)

    def test_copy_within_the_limit_is_unchanged(self):
        copy = (
            "Enter each club's carry to find gaps over 20 yards and clubs less than "
            "8 yards apart, then see which clubs earn their spot in your bag."
        )
        self.assertEqual(copy, finish_description(copy))


class RetitledToolPageTests(unittest.TestCase):
    def test_inventory_carries_the_search_name(self):
        tools = {tool["slug"]: tool for tool in inventory.TOOLS}
        for slug, (search_name, product_name) in RETITLED.items():
            with self.subTest(slug):
                self.assertEqual(search_name, tools[slug]["search_name"])
                self.assertEqual(product_name, tools[slug]["name"])

    def test_pages_lead_with_the_search_name_and_keep_the_product_subtitle(self):
        for slug, (search_name, product_name) in RETITLED.items():
            with self.subTest(slug):
                source = (ROOT / f"{slug}.html").read_text(encoding="utf-8")
                h1s = re.findall(r"<h1\b[^>]*>(.*?)</h1>", source, re.S)
                self.assertEqual([search_name], [_text(h) for h in h1s])
                brand = re.search(r'</h1>\s*<p class="tool-brand">(.*?)</p>', source, re.S)
                self.assertIsNotNone(brand, "product subtitle must follow the H1")
                self.assertEqual(product_name, _text(brand.group(1)))

    def test_head_metadata_matches_the_reviewed_override(self):
        for slug in RETITLED:
            with self.subTest(slug):
                source = (ROOT / f"{slug}.html").read_text(encoding="utf-8")
                override = metadata_override_for("/" + slug)
                meta = audit_metadata(source)
                self.assertEqual(override["title"], meta["title"])
                self.assertEqual(override["description"], meta["description"])
                for field in ("og:title", "twitter:title"):
                    self.assertEqual(meta["title"], meta[field])
                for field in ("og:description", "twitter:description"):
                    self.assertEqual(meta["description"], meta[field])
                self.assertIn(
                    f'<link rel="canonical" href="{inventory.SITE}/{slug}">', source
                )

    def test_settle_up_net_claim_is_backed_by_the_engine(self):
        source = (ROOT / "tools-settle-up-calculator.html").read_text(encoding="utf-8")
        description = metadata_override_for("/tools-settle-up-calculator")["description"]
        self.assertIn("gross or net scores", description)
        # Since Settle Up V2 the engine applies handicap strokes by stroke index,
        # so the page must say which handicap it expects and load that engine.
        self.assertIn("playing handicap", source)
        self.assertIn("stroke index", source)
        self.assertIn('<script src="/lib/games/settle-up.js?v=', source)


if __name__ == "__main__":
    unittest.main()
