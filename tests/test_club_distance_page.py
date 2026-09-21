"""Page contract for The Distance Check (tools-club-distance-calculator.html).

The model has its own sweep in tests/club-distance.test.js. These checks keep
the generated page honest: one search H1 with the product subtitle, reviewed
metadata, the handoffs to other tools, accessible inputs, and a static example
table that always matches what the model returns.
"""

import json
import re
import subprocess
import unittest
from html import unescape
from pathlib import Path

from scripts import tool_inventory as inventory
from scripts.seo_metadata import audit_metadata


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "tools-club-distance-calculator.html"
BUILDER = ROOT / "scripts" / "build_club_distance.py"
SITE = "https://www.golfraw.com"


def text(fragment):
    return unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


class ClubDistancePageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PAGE.read_text(encoding="utf-8")
        cls.builder = BUILDER.read_text(encoding="utf-8")

    def test_inventory_names_the_tool_for_search_and_brand(self):
        tool = next(t for t in inventory.TOOLS if t["slug"] == "tools-club-distance-calculator")
        self.assertEqual("The Distance Check", tool["name"])
        self.assertEqual("Golf Club Distance Calculator", tool["search_name"])
        self.assertEqual("free", tool["access"])
        self.assertEqual("bag-equipment", tool["group"])

    def test_one_search_h1_with_the_product_subtitle(self):
        h1s = [text(h) for h in re.findall(r"<h1\b[^>]*>(.*?)</h1>", self.source, re.S)]
        self.assertEqual(["Golf Club Distance Calculator"], h1s)
        self.assertRegex(self.source, r'</h1>\s*<p class="tool-brand">The Distance Check</p>')

    def test_head_metadata_is_complete_and_mirrored(self):
        meta = audit_metadata(self.source)
        self.assertEqual("Golf Club Distance Calculator: Yards or Metres | GolfRaw", meta["title"])
        self.assertLessEqual(len(meta["title"]), 60)
        self.assertTrue(120 <= len(meta["description"]) <= 155, len(meta["description"]))
        for field in ("og:title", "twitter:title"):
            self.assertEqual(meta["title"], meta[field])
        for field in ("og:description", "twitter:description"):
            self.assertEqual(meta["description"], meta[field])
        self.assertIn(f'<link rel="canonical" href="{SITE}/tools-club-distance-calculator">', self.source)
        self.assertIn(f"<loc>{SITE}/tools-club-distance-calculator</loc>",
                      (ROOT / "sitemap.xml").read_text(encoding="utf-8"))

    def test_schema_names_the_app_and_uses_the_search_breadcrumb(self):
        docs = re.findall(r'<script type="application/ld\+json">(.*?)</script>', self.source, re.S)
        self.assertEqual(1, len(docs))
        graph = json.loads(docs[0])["@graph"]
        app = next(n for n in graph if n["@type"] == "WebApplication")
        crumb = next(n for n in graph if n["@type"] == "BreadcrumbList")
        self.assertEqual("The Distance Check", app["name"])
        self.assertEqual("Golf Club Distance Calculator", app["alternateName"])
        self.assertEqual("Golf Club Distance Calculator", crumb["itemListElement"][-1]["name"])
        self.assertTrue(any(n["@type"] == "FAQPage" for n in graph))

    def test_scripts_load_at_the_versions_the_builders_declare(self):
        ver = re.search(r"^MODEL_VER = '(\d+)'", self.builder, re.M).group(1)
        self.assertEqual(1, self.source.count(f'<script src="/lib/distance/club-distance.js?v={ver}"></script>'))
        self.assertIn("/lib/analytics/tool-events.js?v=", self.source)
        self.assertIn("/lib/locker/store.js?v=", self.source)
        self.assertLess(self.source.index("club-distance.js?v="), self.source.index("window.GolfrawDistance"))

    def test_handoffs_link_each_related_tool_once(self):
        for route, placement in (("/tools-bag-audit", "result_bag_gaps"),
                                 ("/tools-tee-box-check", "result_tee_check"),
                                 ("/tools-standing-order", "result_measured_carry")):
            with self.subTest(route):
                self.assertEqual(1, len(re.findall(rf'href="{route}"', self.source)))
                self.assertIn(f'data-gr-placement="{placement}"', self.source)
        self.assertEqual(1, self.source.count('href="/news-2026-golf-club-distances-guide"'))

    def test_inputs_are_labelled_and_phone_friendly(self):
        self.assertIn('<input type="number" id="cdValue" inputmode="decimal"', self.source)
        self.assertIn('<label for="cdValue" id="cdValueLabel">', self.source)
        self.assertIn('<label for="cdBand">', self.source)
        self.assertEqual(3, self.source.count("<legend"))  # anchor, units, comparison group
        self.assertIn('role="alert"', self.source)
        self.assertIn('data-gr-inputs', self.source)
        self.assertIn('id="cdGo" data-gr-run', self.source)
        self.assertNotIn("<form", self.source.split('id="cdOut"')[0].split('class="panel cd-panel"')[1])

    def test_static_examples_match_the_model(self):
        script = (
            "const D=require('./lib/distance/club-distance.js');"
            "const g=(r,id)=>{const c=r.clubs.find(c=>c.id===id);return Math.round(c.typical[0])+'-'+Math.round(c.typical[1]);};"
            "console.log(JSON.stringify([120,145,170].map(v=>{const r=D.estimate({anchor:'iron_carry',value:v});"
            "return [v+' yards',g(r,'driver'),g(r,'5i'),g(r,'pw')];})));"
        )
        expected = json.loads(subprocess.run(["node", "-e", script], cwd=ROOT, capture_output=True,
                                             text=True, check=True).stdout)
        table = self.source.split('<table class="cd-examples">')[1].split("</table>")[0]
        rows = [[text(td).replace("–", "-") for td in re.findall(r"<td>(.*?)</td>", tr, re.S)]
                for tr in re.findall(r"<tr>(.*?)</tr>", table.split("<tbody>")[1], re.S)]
        self.assertEqual(expected, rows)

    def test_builder_owns_the_page(self):
        for marker in ('<p class="tool-brand">The Distance Check</p>', "How this estimate works",
                       "What it returns for three golfers", "window.GolfrawDistance"):
            with self.subTest(marker):
                self.assertIn(marker, self.builder)
                self.assertIn(marker, self.source)

    def test_model_contract_passes(self):
        result = subprocess.run(["node", str(ROOT / "tests" / "club-distance.test.js")],
                                capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr or result.stdout)


if __name__ == "__main__":
    unittest.main()
