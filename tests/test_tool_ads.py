"""Ads and consent across GolfRaw (monetization M1).

The module's behaviour is pinned in tests/tool-ads.test.js. These checks pin
the pages: where a slot may sit and where it never may, one ad bootstrap at
most, consent defaults ahead of every Google tag, Pro kept ad-free on the
article loader too, and switches that cannot carry an invented ad unit id.
"""

import glob
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

from scripts import tool_inventory as inventory
from scripts import wire_ads

ROOT = Path(__file__).resolve().parents[1]
MODULE = (ROOT / "lib" / "ads" / "tool-ads.js").read_text(encoding="utf-8")
PILOTS = {
    "tools-club-distance-calculator": "cdOut",
    "tools-tee-box-check": "outWrap",
    "tools-bag-audit": "outWrap",
    "tools-plays-like": "outWrap",
}


def page(slug):
    return (ROOT / f"{slug}.html").read_text(encoding="utf-8")


class Tree(HTMLParser):
    """Records, for each ad slot, its ancestors' ids and data attributes, and
    the document order of slots, buttons and FAQ blocks."""

    VOID = {"br", "img", "input", "meta", "link", "hr", "col", "source", "wbr", "area", "base", "embed", "param", "track"}

    def __init__(self):
        super().__init__()
        self.stack, self.order, self.slots = [], [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "data-gr-ad" in a:
            self.slots.append({"placement": a["data-gr-ad"], "when": a.get("data-gr-ad-when"), "hidden": "hidden" in a,
                               "ancestors": [(t, dict(x)) for t, x in self.stack], "pos": len(self.order)})
            self.order.append(("slot", a["data-gr-ad"]))
        elif tag == "button":
            self.order.append(("button", a.get("id", ""), tuple(x.get("id", "") for _, x in self.stack)))
        elif "faq-block" in (a.get("class") or ""):
            self.order.append(("faq", ""))
        if tag not in self.VOID:
            self.stack.append((tag, a))

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        while self.stack:
            if self.stack.pop()[0] == tag:
                break


def tree(slug):
    t = Tree()
    t.feed(page(slug))
    return t


class ToolAdsTests(unittest.TestCase):
    def test_switches_carry_no_invented_unit_ids(self):
        units = dict(re.findall(r"(after_result|lower): '([^']*)'", MODULE.split("var UNITS = ")[1].split(";")[0]))
        for placement, unit in units.items():
            with self.subTest(placement):
                self.assertRegex(unit, r"^(\d{10})?$", "an AdSense ad unit id is ten digits, or empty")
        if "var AUTO_ADS_EXCLUDED = true" in MODULE:
            self.assertTrue(any(units.values()), "turning ads on needs at least one real unit id")
        self.assertIn("var CLIENT = 'ca-pub-8933725159594062';", MODULE)
        self.assertIn("var LABEL = 'Advertisements';", MODULE, "Google allows only 'Advertisements' or 'Sponsored Links'")
        pages = set(re.findall(r"'(tools-[a-z0-9-]+)': true", MODULE.split("var PAGES = ")[1].split("};")[0]))
        free = {t["slug"] for t in inventory.TOOLS if t["access"] == "free"}
        self.assertTrue(pages <= free, "ads only on free tools, never the Pro preview")
        self.assertEqual(set(PILOTS), pages, "phase A is the four pilots")

    def test_every_tool_page_has_one_ads_block_and_no_static_ad_code(self):
        block = '<script src="/lib/ads/tool-ads.js?v=%s" defer></script>' % wire_ads.VER
        for tool in inventory.tracked_pages():
            src = page(tool["slug"])
            with self.subTest(tool["slug"]):
                self.assertEqual(1, src.count(block))
                self.assertNotIn("Ads + consent are deferred", src, "the inline Auto ads loader is gone from tools")
                self.assertNotIn("adsbygoogle.js", src.replace("lib/ads/tool-ads.js", ""), "no static AdSense bootstrap")
                self.assertNotIn('class="adsbygoogle"', src)
                self.assertNotIn('class="ad-zone"', src, "the old empty placeholders are gone")
                self.assertIn("window.__gr_ads=false", src, "tools never opt into Auto ads")
        self.assertEqual(0, wire_ads.main(["--check"]))

    def test_slots_only_on_rollout_pages(self):
        for tool in inventory.tracked_pages():
            with self.subTest(tool["slug"]):
                n = len(tree(tool["slug"]).slots)
                self.assertEqual(2 if tool["slug"] in PILOTS else 0, n)

    def test_pilot_slots_sit_after_the_result_and_its_actions(self):
        for slug, result_id in PILOTS.items():
            t = tree(slug)
            with self.subTest(slug):
                a = next(s for s in t.slots if s["placement"] == "after_result")
                b = next(s for s in t.slots if s["placement"] == "lower")
                ids = [x.get("id") for _, x in a["ancestors"]]
                self.assertIn(result_id, ids, "slot A lives inside the result container")
                self.assertTrue(a["hidden"] and b["hidden"], "slots start hidden, so nothing shows if the module never runs")
                for s in (a, b):
                    self.assertFalse(any("data-gr-inputs" in x for _, x in s["ancestors"]), "never inside an input panel")
                    self.assertFalse(any(tag in ("form", "table", "button", "a") for tag, _ in s["ancestors"]))
                # every button in the result container comes before slot A
                buttons_in_result = [i for i, o in enumerate(t.order) if o[0] == "button" and result_id in o[2]]
                self.assertTrue(buttons_in_result and max(buttons_in_result) < a["pos"], "slot A follows every result action")
                self.assertEqual("#" + result_id, b["when"], "slot B waits for the result")
                faq = next(i for i, o in enumerate(t.order) if o[0] == "faq")
                self.assertLess(b["pos"], faq, "slot B sits before the FAQ")
                self.assertLess(a["pos"], b["pos"])

    def test_round_card_and_settle_up_entry_and_payments_carry_no_slot(self):
        for slug in ("tools-scorecard-analyzer", "tools-settle-up-calculator"):
            src = page(slug)
            with self.subTest(slug):
                self.assertNotIn("data-gr-ad=", src)
        self.assertNotIn("tools-scorecard-analyzer", MODULE.split("var PAGES = ")[1].split("};")[0])
        self.assertNotIn("tools-settle-up-calculator", MODULE.split("var PAGES = ")[1].split("};")[0])

    def test_consent_defaults_run_before_every_google_tag(self):
        pages = [p for p in glob.glob(str(ROOT / "*.html")) if "googletagmanager.com/gtag/js" in Path(p).read_text(encoding="utf-8")]
        self.assertGreater(len(pages), 300)
        for p in pages:
            src = Path(p).read_text(encoding="utf-8")
            with self.subTest(Path(p).name):
                self.assertEqual(1, src.count(wire_ads.CM_START))
                default = src.index("gtag('consent','default'")
                self.assertLess(default, src.index("googletagmanager.com/gtag/js"))
                config = re.search(r"gtag\(\s*['\"]config['\"]", src)
                if config:
                    self.assertLess(default, config.start())
        block = wire_ads.CONSENT_BLOCK
        for code in ("GB", "CH", "NO", "IS", "LI", "DE", "FR", "IE", "NL"):
            self.assertIn("'%s'" % code, block)
        self.assertEqual(32, len(wire_ads.REGIONS))
        for key in ("ad_storage", "ad_user_data", "ad_personalization", "analytics_storage"):
            self.assertIn(key + ":'denied'", block)
        self.assertIn("wait_for_update:500", block)

    def test_article_loader_skips_ads_for_pro(self):
        loaders = 0
        for p in glob.glob(str(ROOT / "*.html")):
            src = Path(p).read_text(encoding="utf-8")
            if "function loadAds()" not in src:
                continue
            loaders += 1
            with self.subTest(Path(p).name):
                self.assertIn("if (adsQueued || !window.__gr_ads || proPass()) return;", src)
                self.assertIn("localStorage.getItem('golfraw_pro_pass')", src)
        self.assertGreater(loaders, 300)
        for rel in wire_ads.BUILDER_SOURCES:
            self.assertIn("proPass()", (ROOT / rel).read_text(encoding="utf-8"), rel)

    def test_analytics_layer_gains_no_ad_events(self):
        helper = (ROOT / "lib" / "analytics" / "tool-events.js").read_text(encoding="utf-8")
        events = re.search(r"var EVENTS = \{(.*?)\};", helper, re.S).group(1)
        self.assertNotRegex(events, r"ad_|adsense|revenue")
        self.assertNotIn("GRTrack", MODULE, "the ads module reports nothing to analytics")


if __name__ == "__main__":
    unittest.main()
