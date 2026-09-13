#!/usr/bin/env python3
"""Regression checks for the Task 2 canonical-route contracts."""

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.golfraw.com"

REDIRECTS = {
    "/news-2026-michael-block-leads-ally-challenge-final-round":
        "/news-2026-michael-block-lead-ally-challenge",
    "/news-2026-hovland-leads-tour-championship-final-day":
        "/news-2026-tour-championship-final-round-hovland-leads",
    "/blog/morikawa-61-travelers-championship-2026":
        "/morikawa-61-travelers-championship-2026",
    "/golf-deals-equipment-tee-times-guide":
        "/equipment/golf-deals-equipment-tee-times-guide",
    "/golf-tournaments-rules-formats-tax-guide":
        "/rules/golf-tournaments-rules-formats-tax-guide",
    "/news-2026-angel-yin-solheim-cup-fitness-team-usa-europe":
        "/angel-yin-solheim-cup-fitness-team-usa-europe",
    "/news-2026-asian-tour-ceo-liv-golf-dp-world-tour-pivot":
        "/asian-tour-ceo-liv-golf-dp-world-tour-pivot",
    "/news-2026-bryson-dechambeau-liv-golf-2027":
        "/bryson-dechambeau-liv-golf-2027",
    "/news-2026-charley-hull-solheim-cup-late-arrival-drinks-denial":
        "/charley-hull-solheim-cup-late-arrival-drinks-denial",
    "/news-2026-david-puig-crans-sur-sierre-position-over-power":
        "/david-puig-crans-sur-sierre-position-over-power",
    "/news-2026-european-solheim-cup-team":
        "/2026-european-solheim-cup-team",
    "/news-2026-grehan-comeback-stout-walker-cup-saturday-singles":
        "/grehan-comeback-stout-walker-cup-saturday-singles",
    "/news-2026-jon-rahm-dodges-pga-tour-pathway-liv-golf-contract":
        "/jon-rahm-dodges-pga-tour-pathway-liv-golf-contract",
    "/news-2026-jon-rahm-liv-golf-major-champions-leaving":
        "/jon-rahm-liv-golf-major-champions-leaving",
    "/news-2026-liv-golfer-disqualified-dp-world-tour-q-school":
        "/liv-golfer-disqualified-dp-world-tour-q-school",
    "/news-2026-mcilroy-keep-heads-down-trump-irish-open-doonbeg":
        "/mcilroy-keep-heads-down-trump-irish-open-doonbeg",
    "/news-2026-nelly-korda-solheim-cup-european-drought-2026":
        "/nelly-korda-solheim-cup-european-drought-2026",
    "/news-2026-paul-casey-charity-vow-omega-european-masters":
        "/paul-casey-charity-vow-omega-european-masters",
    "/news-2026-presidents-cup-captain-liv-golf-restrictions-international-team":
        "/presidents-cup-captain-liv-golf-restrictions-international-team",
    "/news-2026-rory-mcilroy-30-pga-tour-wins":
        "/rory-mcilroy-30-pga-tour-wins",
    "/news-2026-rory-mcilroy-liv-bankruptcy-dp-world-tour":
        "/rory-mcilroy-liv-bankruptcy-dp-world-tour",
    "/news-2026-rory-mcilroy-scottie-scheffler-legend":
        "/rory-mcilroy-scottie-scheffler-legend",
    "/news-2026-rory-mcilroy-trump-irish-open-doonbeg":
        "/rory-mcilroy-trump-irish-open-doonbeg",
    "/news-2026-solheim-cup-all-star-challenge":
        "/solheim-cup-all-star-challenge-2026",
    "/news-2026-solheim-cup-rosters-finalized-captains-picks":
        "/2026-solheim-cup-rosters-finalized-captains-picks",
    "/news-2026-thriston-lawrence-european-masters-halfway-lead":
        "/thriston-lawrence-european-masters-halfway-lead",
    "/news-2026-thriston-lawrence-omega-european-masters-playoff-paul-casey":
        "/thriston-lawrence-omega-european-masters-2026-playoff-paul-casey",
    "/news-2026-trump-west-palm-beach-presidential-golf-course-proposal":
        "/trump-west-palm-beach-presidential-golf-course-proposal",
    "/news-2026-trump-martin-doonbeg-irish-open-united-ireland":
        "/trump-martin-doonbeg-irish-open-united-ireland",
    "/news-2026-irish-open-2026-final-round-tee-times-tv":
        "/irish-open-2026-final-round-tee-times-tv",
    "/news-2026-solheim-cup-prize-money-ryder-cup-500k":
        "/solheim-cup-prize-money-ryder-cup-500k",
    "/news-2026-europe-wins-solheim-cup-sunday-singles-rout":
        "/europe-wins-solheim-cup-sunday-singles-rout",
}

WINNERS = {
    "/news-2026-michael-block-lead-ally-challenge":
        "news-2026-michael-block-lead-ally-challenge.html",
    "/news-2026-tour-championship-final-round-hovland-leads":
        "news-2026-tour-championship-final-round-hovland-leads.html",
    "/morikawa-61-travelers-championship-2026":
        "morikawa-61-travelers-championship-2026.html",
    "/equipment/golf-deals-equipment-tee-times-guide":
        "equipment/golf-deals-equipment-tee-times-guide.html",
    "/rules/golf-tournaments-rules-formats-tax-guide":
        "rules/golf-tournaments-rules-formats-tax-guide.html",
    "/liv-golf-pga-tour-return": "liv-golf-pga-tour-return.html",
    "/news-2026-liv-golf-players-return-pga-tour-rules":
        "news-2026-liv-golf-players-return-pga-tour-rules.html",
}


def vercel_redirects():
    return {
        item["source"]: item
        for item in json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))[
            "redirects"
        ]
    }


def canonical_in(path):
    match = re.search(
        r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)',
        path.read_text(encoding="utf-8"),
        re.IGNORECASE,
    )
    return match.group(1) if match else ""


def page_title_and_h1(path):
    source = path.read_text(encoding="utf-8")
    title = re.search(r"<title>(.*?)</title>", source, re.IGNORECASE | re.DOTALL)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", source, re.IGNORECASE | re.DOTALL)
    clean = lambda value: re.sub(r"<[^>]+>", "", value or "").strip()
    return clean(title.group(1) if title else ""), clean(h1.group(1) if h1 else "")


class DuplicateRouteTests(unittest.TestCase):
    def test_duplicate_routes_have_direct_permanent_redirects(self):
        redirects = vercel_redirects()
        for source, destination in REDIRECTS.items():
            self.assertIn(source, redirects)
            rule = redirects[source]
            self.assertEqual(destination, rule["destination"])
            self.assertTrue(rule["permanent"])
            self.assertNotIn(destination, REDIRECTS)

    def test_canonical_registry_contains_only_the_selected_route(self):
        registry = json.loads((ROOT / "articles.json").read_text(encoding="utf-8"))
        articles = registry["articles"]
        records = {article["url"]: article for article in articles}
        for winner in (
            "/news-2026-michael-block-lead-ally-challenge",
            "/news-2026-tour-championship-final-round-hovland-leads",
            "/morikawa-61-travelers-championship-2026",
            "/equipment/golf-deals-equipment-tee-times-guide",
            "/rules/golf-tournaments-rules-formats-tax-guide",
        ):
            self.assertIn(winner, records)
            self.assertEqual("", records[winner].get("alias_of", ""))
        for deprecated in REDIRECTS:
            self.assertNotIn(deprecated, records)

    def test_sitemap_contains_each_winner_once_and_no_redirect_source(self):
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        for winner in (
            "/news-2026-michael-block-lead-ally-challenge",
            "/news-2026-tour-championship-final-round-hovland-leads",
            "/morikawa-61-travelers-championship-2026",
            "/equipment/golf-deals-equipment-tee-times-guide",
            "/rules/golf-tournaments-rules-formats-tax-guide",
            "/news-2026-liv-golf-players-return-pga-tour-rules",
        ):
            self.assertEqual(1, sitemap.count(f"<loc>{SITE}{winner}</loc>"))
        for deprecated in REDIRECTS:
            self.assertNotIn(f"<loc>{SITE}{deprecated}</loc>", sitemap)

    def test_news_sitemap_contains_no_redirect_source(self):
        news_sitemap = (ROOT / "news-sitemap.xml").read_text(encoding="utf-8")
        for deprecated in REDIRECTS:
            self.assertNotIn(f"<loc>{SITE}{deprecated}</loc>", news_sitemap)

    def test_production_html_has_no_direct_links_to_redirect_sources(self):
        offenders = []
        for path in ROOT.rglob("*.html"):
            if path.name == "article-template.html" or ".git" in path.parts:
                continue
            source = path.read_text(encoding="utf-8")
            for deprecated in REDIRECTS:
                if re.search(
                    rf'(?:href|content)=["\']{re.escape(deprecated)}(?:[?#"\']|$)',
                    source,
                    re.IGNORECASE,
                ):
                    offenders.append(f"{path.relative_to(ROOT)} -> {deprecated}")
        self.assertEqual([], offenders)

    def test_selected_pages_are_self_canonical_and_indexable(self):
        for route, filename in WINNERS.items():
            path = ROOT / filename
            self.assertTrue(path.exists(), filename)
            source = path.read_text(encoding="utf-8")
            self.assertEqual(f"{SITE}{route}", canonical_in(path))
            self.assertNotRegex(source, r'<meta[^>]+name=["\']robots["\'][^>]+noindex')

    def test_guide_generators_only_emit_the_nested_canonical_files(self):
        for generator, nested in (
            (
                "scripts/build_equipment_guide.py",
                "equipment/golf-deals-equipment-tee-times-guide.html",
            ),
            (
                "scripts/build_rules_guide.py",
                "rules/golf-tournaments-rules-formats-tax-guide.html",
            ),
        ):
            with tempfile.TemporaryDirectory() as directory:
                temp_root = Path(directory)
                script = temp_root / Path(generator).name
                shutil.copy(ROOT / generator, script)
                subprocess.run(
                    [sys.executable, str(script)],
                    cwd=temp_root,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertTrue((temp_root / nested).exists(), nested)
                self.assertFalse(
                    (temp_root / Path(nested).name).exists(),
                    f"legacy root output from {generator}",
                )

    def test_liv_pages_have_distinct_primary_titles_and_headings(self):
        old_title, old_h1 = page_title_and_h1(ROOT / WINNERS["/liv-golf-pga-tour-return"])
        new_title, new_h1 = page_title_and_h1(
            ROOT / WINNERS["/news-2026-liv-golf-players-return-pga-tour-rules"]
        )
        self.assertTrue(old_title and old_h1 and new_title and new_h1)
        self.assertNotEqual(old_title, new_title)
        self.assertNotEqual(old_h1, new_h1)

    def test_canonical_duplicate_winners_exist_and_are_self_canonical(self):
        redirects = set(REDIRECTS)
        for source, destination in REDIRECTS.items():
            if source in {
                "/news-2026-michael-block-leads-ally-challenge-final-round",
                "/news-2026-hovland-leads-tour-championship-final-day",
                "/blog/morikawa-61-travelers-championship-2026",
                "/golf-deals-equipment-tee-times-guide",
                "/golf-tournaments-rules-formats-tax-guide",
                "/what-beginners-actually-search",
                "/news-2026-lee-westwood-liv-golf-bedminster-different-course",
                "/news-2026-pga-tour-fan-code-of-conduct-gambling",
            }:
                continue
            winner = ROOT / (destination.lstrip("/") + ".html")
            self.assertTrue(winner.exists(), destination)
            self.assertEqual(f"{SITE}{destination}", canonical_in(winner), destination)
            self.assertNotRegex(
                winner.read_text(encoding="utf-8"),
                r'<meta[^>]+name=["\']robots["\'][^>]+noindex',
            )

    def test_task6b_hubs_have_useful_context_sections(self):
        expectations = {
            "ratings.html": ("ratings-methodology", "/ratings-manual"),
            "full-board.html": ("full-board-scope", "/ratings-manual"),
            "analysis.html": ("analysis-start-here", "/golf-swing-drills"),
        }
        for filename, (section_id, supporting_route) in expectations.items():
            source = (ROOT / filename).read_text(encoding="utf-8")
            self.assertIn(f'id="{section_id}"', source, filename)
            self.assertIn(f'href="{supporting_route}"', source, filename)

    def test_liv_return_has_contextual_inbound_links(self):
        expected_sources = {
            "news-2026-liv-golf-secures-lead-investor.html",
            "news-2026-liv-golf-players-return-pga-tour-rules.html",
        }
        actual_sources = set()
        for path in ROOT.rglob("*.html"):
            if path.name == "article-template.html" or ".git" in path.parts:
                continue
            source = path.read_text(encoding="utf-8")
            if re.search(r'href=["\']/liv-golf-pga-tour-return(?:[?#"\']|$)', source):
                actual_sources.add(path.name)
        self.assertTrue(expected_sources <= actual_sources)


if __name__ == "__main__":
    unittest.main()
