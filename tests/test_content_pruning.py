"""Content pruning phase 1 (15 November 2026).

See docs/seo/2026-11-15-content-pruning-plan.md (local, untracked) and the
per-page inventory beside it. Pages are noindexed or merged, never deleted:
every URL keeps resolving.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

NOINDEXED = [
    "lpga-2026-nelly-korda-hazeltine-preview",
    "news-2026-cameron-smith-bedminster-liv-winning-margin",
    "news-2026-collin-morikawa-61-travelers-weather",
    "news-2026-dechambeau-faldo-suber-birkdale",
    "news-2026-detroit-golf-club-full-scorecard-par-70",
    "news-2026-fleetwood-birkdale-open-round-3",
    "news-2026-fleetwood-open-birkdale",
    "news-2026-golf-ball-deals-buying-guide",
    "news-2026-golf-driver-upgrades-weights",
    "news-2026-hovland-one-shot-lead-tour-championship",
    "news-2026-liv-golf-250m-investment-rescue",
    "news-2026-liv-golf-secures-lead-investor",
    "news-2026-rocket-classic-numbers-par-4",
    "news-2026-rory-bryson-open-verdict",
    "news-2026-scheffler-mcilroy-birkdale-press-conference",
    "news-2026-travelers-betting-preview",
    "news-2026-travelers-championship-round-1-recap",
    "news-2026-travelers-championship-signature-events",
    "news-2026-trump-east-potomac-fazio-major",
    "news-2026-us-womens-amateur-match-play-malixi",
    "news-2026-wyndham-championship-odds-day-bradley",
    "news-2026-wyndham-championship-sedgefield-preview",
    "news-2026-xander-schauffele-jackson-koivun-reaction",
    "pga-2026-travelers-championship-preview",
    "us-open-2026-clark-on-the-brink",
    "us-open-round-1-shinnecock",
    "us-open-round-2-highlights",
    "us-open-round-2-shinnecock",
    "us-open-round-3-clark-lead",
]

MERGED = {
    "news-2026-tour-championship-sunday-tee-times-round-4": "news-2026-tour-championship-tee-times-round-4",
    "news-2026-michael-block-lead-ally-challenge": "news-2026-michael-block-ally-challenge",
    "news-2026-lucas-herbert-liv-uk-record-asterisk": "news-2026-lucas-herbert-liv-golf-uk-record-win",
    "news-2028-pga-tour-overhaul-winners-losers": "news-2026-pga-tour-2028-overhaul-analysis",
}

# Matched a pruning rule but stay indexed: linked from the Corrections Log, or
# the target of an earlier duplicate-route redirect (noindexing a redirect
# target would discard the signals the redirect consolidated).
STAY_INDEXED = [
    "us-open-2026-final-round-live-updates",
    "news-2026-hovland-tie-for-lead-tour-championship",
    "news-2026-tour-championship-final-round-hovland-leads",
    "morikawa-61-travelers-championship-2026",
    "equipment/golf-deals-equipment-tee-times-guide",
]


def read(name):
    return (ROOT / name).read_text(encoding="utf-8")


def sitemap_routes():
    return set(re.findall(r"<loc>https://www\.golfraw\.com/([^<]*)</loc>", read("sitemap.xml")))


def robots(slug):
    match = re.search(r'<meta name="robots" content="([^"]*)">', read(f"{slug}.html"))
    return match.group(1) if match else ""


class NoindexTests(unittest.TestCase):
    def test_pruned_pages_are_noindex_follow_and_out_of_the_sitemap(self):
        routes = sitemap_routes()
        for slug in NOINDEXED:
            with self.subTest(slug=slug):
                self.assertTrue((ROOT / f"{slug}.html").exists(), "URL must keep resolving")
                self.assertEqual(robots(slug), "noindex, follow")
                self.assertNotIn(slug, routes)

    def test_pruned_pages_are_registered_with_the_audit(self):
        audit = read("scripts/fix_seo_audit.py")
        for slug in NOINDEXED:
            with self.subTest(slug=slug):
                self.assertIn(f'"{Path(slug).name}.html"', audit)

    def test_corrected_pages_stay_indexed(self):
        routes = sitemap_routes()
        for slug in STAY_INDEXED:
            with self.subTest(slug=slug):
                self.assertNotIn("noindex", robots(slug))
                self.assertIn(slug, routes)


class MergeTests(unittest.TestCase):
    def setUp(self):
        self.redirects = json.loads(read("vercel.json"))["redirects"]
        self.registry = {a["slug"]: a for a in json.loads(read("articles.json"))["articles"]}

    def test_merged_pages_redirect_permanently_to_their_target(self):
        table = {r["source"]: r for r in self.redirects}
        for source, target in MERGED.items():
            with self.subTest(source=source):
                rule = table.get(f"/{source}")
                self.assertIsNotNone(rule)
                self.assertEqual(rule["destination"], f"/{target}")
                self.assertTrue(rule["permanent"])
                self.assertEqual(self.registry[source]["alias_of"], target)
                self.assertNotIn("noindex", robots(target))

    def test_no_redirect_into_a_noindexed_page(self):
        targets = [r["destination"].lstrip("/") for r in self.redirects]
        self.assertEqual([], [t for t in targets if t in NOINDEXED])

    def test_no_redirect_chains(self):
        sources = {r["source"] for r in self.redirects}
        chains = [(r["source"], r["destination"]) for r in self.redirects if r["destination"] in sources]
        self.assertEqual([], chains)

    def test_nothing_links_to_a_merged_page(self):
        routes = sitemap_routes()
        problems = []
        for route in routes:
            path = ROOT / f"{route or 'index'}.html"
            if not path.exists():
                continue
            source = path.read_text(encoding="utf-8")
            for old in MERGED:
                if re.search(r'(?:href="|l:")(?:https://www\.golfraw\.com)?/?' + re.escape(old) + r'(?:\.html)?["#?]', source):
                    problems.append((route, old))
            for old in MERGED:
                self.assertNotIn(old, routes)
        self.assertEqual([], problems)


if __name__ == "__main__":
    unittest.main()
