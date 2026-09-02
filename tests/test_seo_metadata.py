import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scripts import sync_site
from scripts.article_header import finalize_article_template_metadata
from scripts.fix_seo_audit import repair_source, validate_override_page
from scripts.seo_metadata import (
    ARTICLE_SEO_OVERRIDES,
    apply_metadata_overrides,
    audit_metadata,
    metadata_override_for,
)


EXPECTED_TITLES = {
    "/equipment/golf-deals-equipment-tee-times-guide": "Golf Deals: Save $2,176 Annually on Equipment and Rounds",
    "/news-2026-tiger-woods-pleads-guilty-reckless-driving-jupiter-island": "Tiger Woods Pleads Guilty: 5-Year Ban and $1,000 Fine",
    "/news-2026-bmw-championship-round-3-scores-odds-recap": "BMW Championship Round 3: Wyndham Clark Leads by 5",
    "/news-2026-brandt-jobe-ally-challenge-jackson": "Brandt Jobe's Ally Challenge: Best Week in Over a Year",
    "/news-2026-charlotte-womens-golf-begins-season-quail-hollow": "Charlotte Women's Golf Begins 2026 Season at Quail Hollow",
    "/news-2026-end-of-season-driver-deals": "End-of-Season Driver Deals: What's Actually Worth Buying",
    "/news-2026-hovland-on-what-makes-scheffler-successful": "Hovland on What Makes Scheffler Successful, in 8 Words",
    "/news-2026-hovland-one-shot-lead-tour-championship": "Hovland's One-Shot Lead Came From Six Straight Putts",
    "/news-2026-hovland-tour-championship-runner-up": "Hovland's Tour Championship Runner-Up and What He Said",
    "/news-2026-jon-rahm-liv-golf-future": "Jon Rahm LIV Golf Future: August 2026 Update",
    "/news-2026-jon-rahm-liv-money-owed": "Jon Rahm's LIV Money: What He's Owed and Who Gets Paid",
    "/news-2026-justin-thomas-mental-capacity-bay-hill": "Justin Thomas's 'Mental Capacity' Line, Six Months On",
    "/news-2026-kevin-hart-golf-youtube-132": "Kevin Hart Shot 132 on His New Golf YouTube Channel",
    "/news-2026-liv-golf-bankruptcy-chapter-11-explained": "LIV Golf Bankruptcy: What Chapter 11 Would Actually Do",
    "/news-2026-liv-golf-pif-withdrawal-season-end": "LIV Golf Ends 2026 Season Early Following PIF Withdrawal",
    "/news-2026-liv-golf-settlement-offers-bankruptcy": "LIV Golf Settlement Offers: Cents on the Dollar, Explained",
    "/news-2026-lpga-tour-golfer-costs-alexa-pano-expenses": "LPGA Tour Golfer Costs: $250k Earnings Yields $37,620",
    "/news-2026-michael-block-ally-challenge": "Michael Block's Ally Challenge: A 36-Hole Record, Then 74",
    "/news-2026-michael-block-lead-ally-challenge": "Michael Block's 2-Shot Lead at the Ally Challenge Explained",
    "/news-2026-pga-tour-winners-2026": "PGA Tour Winners 2026: 28 Names, 35 Events, One Left",
    "/news-2026-scheffler-ted-scott-finding-the-number": "Scottie Scheffler and Ted Scott: How They Find the Number",
    "/news-2026-scheffler-true-strokes-gained": "Scottie Scheffler's True Strokes Gained: 12th Since 1983",
    "/news-2026-scott-oneil-linkedin-post-liv-golf": "Scott O'Neil's LinkedIn Post on LIV Golf 1.0, Fact-Checked",
    "/news-2026-scottie-scheffler-captures-fedex-cup": "Scottie Scheffler Captures the FedEx Cup and Passes Tiger",
    "/news-2026-scottie-scheffler-final-press-conference-answer": "Scottie Scheffler's Final Press Conference Answers",
    "/news-2026-small-grip-change-big-swing-improvement": "Small Grip Change, Big Swing Improvement",
    "/news-2026-the-end-of-liv-golf-bankruptcy": "The End of LIV Golf? What a Bankruptcy Would Really Mean",
    "/news-2026-tiger-woods-career-money-list-record": "Tiger Woods' Career Money List Record May Fall Today",
    "/news-2026-tour-championship-final-round-hovland-leads": "Tour Championship Final Round: Hovland Leads by One",
    "/news-2026-tour-championship-points-and-payouts": "Tour Championship Points and Payouts: All 29 Checks",
    "/news-2026-tour-championship-round-3-tee-times-leaderboard": "Tour Championship Round 3: Hovland's 65 and Every Score",
    "/news-2026-tour-championship-sunday-tee-times-round-4": "2026 Tour Championship Sunday Tee Times: Everything Moved",
    "/news-2026-tour-championship-tee-times-round-4": "2026 Tour Championship Tee Times: Round 4 at East Lake",
    "/news-2026-tour-championship-winners-losers-friday": "Tour Championship Winners & Losers: Scheffler Surges",
    "/news-2026-trump-honorary-chairman-presidents-cup-2026": "Trump Named Honorary Chairman of the Presidents Cup Again",
    "/news-2026-wyndham-clark-gary-woodland-bmw-championship-recap": "Wyndham Clark Leads BMW Championship by 5",
    "/news-every-shot-tiger-woods-80th-win-2018": "Every Shot From Tiger Woods' 80th Win: What to Watch For",
    "/scottie-scheffler-swing-explained": "Scottie Scheffler's Swing: The Foot Slide Is a Symptom",
    "/strokes-gained": "What Does Strokes Gained Mean? A Simple Golf Explanation",
    "/golf-clubs-for-beginners": "Golf Clubs for Beginners: What You Actually Need",
    "/why-pros-are-ditching-hybrids": "Why Pros Are Ditching Hybrids, and Why You Shouldn't",
    "/guides-how-to-play-in-a-golf-pro-am-costs-etiquette": "How to Play in a Golf Pro-Am: Costs & Etiquette",
    "/news-2026-how-much-pro-am-costs": "How Much Does a Pro-Am Cost? PGA vs Local Events",
}

EXPECTED_DESCRIPTIONS = {
    "/equipment/golf-deals-equipment-tee-times-guide": "Save $2,176 annually on golf equipment, balls and tee times with data on release cycles, urethane balls and twilight rates.",
    "/news-2026-donald-trump-amgen-irish-open-doonbeg": "President Donald Trump is scheduled to attend the 2026 Amgen Irish Open at his Doonbeg golf course. The visit brings major security to County Clare.",
    "/news-2026-scottie-scheffler-final-press-conference-answer": "After winning $10 million and a second FedEx Cup, Scottie Scheffler passed Tiger Woods on the money list and discussed wind and family travel.",
    "/news-2026-wyndham-clark-gary-woodland-bmw-championship-recap": "Wyndham Clark leads the BMW Championship by five at Bellerive as Gary Woodland's 199 protects his Tour Championship bubble.",
}


class SeoMetadataTests(unittest.TestCase):
    def test_override_catalog_contains_expected_title_and_description_repairs(self):
        self.assertEqual(
            set(EXPECTED_TITLES) | set(EXPECTED_DESCRIPTIONS),
            set(ARTICLE_SEO_OVERRIDES),
        )
        for route, title in EXPECTED_TITLES.items():
            self.assertEqual(ARTICLE_SEO_OVERRIDES[route]["title"], title)
        for route, description in EXPECTED_DESCRIPTIONS.items():
            self.assertEqual(ARTICLE_SEO_OVERRIDES[route]["description"], description)

    def test_metadata_values_fit_search_snippet_limits(self):
        for override in ARTICLE_SEO_OVERRIDES.values():
            if "title" in override:
                self.assertLessEqual(len(override["title"]), 60)
            if "description" in override:
                self.assertLessEqual(len(override["description"]), 160)

    def test_apply_overrides_updates_head_metadata_but_preserves_page_identity(self):
        source = '''<!doctype html><html><head>
<title>Old title | GOLFRAW</title>
<meta name="description" content="Old description">
<meta property="og:title" content="Old title | GOLFRAW">
<meta property="og:description" content="Old description">
<meta name="twitter:title" content="Old title | GOLFRAW">
<meta name="twitter:description" content="Old description">
<link rel="canonical" href="https://golfraw.com/news-2026-bmw-championship-round-3-scores-odds-recap">
</head><body><h1>BMW Championship Round 3: Wyndham Clark Leads by 5 at Bellerive</h1>
<article>Article body remains unchanged.</article>
<script type="application/ld+json">{"headline":"BMW Championship Round 3: Wyndham Clark Leads by 5 at Bellerive"}</script>
</body></html>'''

        updated = apply_metadata_overrides(
            source, "/news-2026-bmw-championship-round-3-scores-odds-recap"
        )
        metadata = audit_metadata(updated)
        self.assertEqual(
            metadata["title"],
            EXPECTED_TITLES["/news-2026-bmw-championship-round-3-scores-odds-recap"],
        )
        self.assertEqual(metadata["description"], "Old description")
        self.assertEqual(metadata["og:title"], metadata["title"])
        self.assertEqual(metadata["twitter:title"], metadata["title"])
        self.assertIn(
            'href="https://golfraw.com/news-2026-bmw-championship-round-3-scores-odds-recap"',
            updated,
        )
        self.assertIn(
            "<h1>BMW Championship Round 3: Wyndham Clark Leads by 5 at Bellerive</h1>",
            updated,
        )
        self.assertIn("Article body remains unchanged.", updated)
        self.assertIn(
            '"headline":"BMW Championship Round 3: Wyndham Clark Leads by 5 at Bellerive"',
            updated,
        )

    def test_description_only_override_preserves_title(self):
        source = '''<html><head>
<title>Donald Trump at Doonbeg | GOLFRAW</title>
<meta name="description" content="Old Donald Trump description">
<meta property="og:title" content="Donald Trump at Doonbeg | GOLFRAW">
<meta property="og:description" content="Old Donald Trump description">
<meta name="twitter:title" content="Donald Trump at Doonbeg | GOLFRAW">
<meta name="twitter:description" content="Old Donald Trump description">
</head><body></body></html>'''

        updated = apply_metadata_overrides(
            source, "/news-2026-donald-trump-amgen-irish-open-doonbeg"
        )
        metadata = audit_metadata(updated)
        self.assertEqual(metadata["title"], "Donald Trump at Doonbeg | GOLFRAW")
        self.assertEqual(metadata["description"], EXPECTED_DESCRIPTIONS["/news-2026-donald-trump-amgen-irish-open-doonbeg"])
        self.assertEqual(metadata["og:description"], metadata["description"])
        self.assertEqual(metadata["twitter:description"], metadata["description"])

    def test_duplicate_pro_am_titles_are_distinct(self):
        self.assertNotEqual(
            ARTICLE_SEO_OVERRIDES["/guides-how-to-play-in-a-golf-pro-am-costs-etiquette"]["title"],
            ARTICLE_SEO_OVERRIDES["/news-2026-how-much-pro-am-costs"]["title"],
        )

    def test_nested_route_lookup_preserves_the_route_prefix(self):
        self.assertEqual(
            metadata_override_for("/equipment/golf-deals-equipment-tee-times-guide")["title"],
            EXPECTED_TITLES["/equipment/golf-deals-equipment-tee-times-guide"],
        )

    def test_unlisted_route_is_unchanged(self):
        source = "<html><head><title>Keep me</title></head></html>"
        self.assertEqual(metadata_override_for("/news"), {})
        self.assertEqual(apply_metadata_overrides(source, "/news"), source)

    def test_seo_repair_source_uses_the_shared_override(self):
        path = Path(__file__).resolve().parents[1] / "news-2026-bmw-championship-round-3-scores-odds-recap.html"
        repaired, _ = repair_source(path, path.read_text(encoding="utf-8"))
        metadata = audit_metadata(repaired)
        self.assertEqual(
            metadata["title"],
            EXPECTED_TITLES["/news-2026-bmw-championship-round-3-scores-odds-recap"],
        )
        self.assertEqual(metadata["og:title"], metadata["title"])
        self.assertEqual(metadata["twitter:title"], metadata["title"])

    def test_article_template_finalizer_uses_the_shared_override(self):
        path = Path(__file__).resolve().parents[1] / "news-2026-bmw-championship-round-3-scores-odds-recap.html"
        source = path.read_text(encoding="utf-8").replace(
            "<figure>\n          <img", "<figure class=\"lead-img\">\n          <img", 1
        )
        finalized = finalize_article_template_metadata(
            source, path
        )
        metadata = audit_metadata(finalized)
        self.assertEqual(
            metadata["title"],
            EXPECTED_TITLES["/news-2026-bmw-championship-round-3-scores-odds-recap"],
        )
        self.assertEqual(metadata["og:title"], metadata["title"])
        self.assertEqual(metadata["twitter:title"], metadata["title"])

    def test_sync_metadata_normalizer_applies_overrides_to_supplied_pages(self):
        source_path = Path(__file__).resolve().parents[1] / "news-2026-bmw-championship-round-3-scores-odds-recap.html"
        source = source_path.read_text(encoding="utf-8")
        expected_title = EXPECTED_TITLES["/news-2026-bmw-championship-round-3-scores-odds-recap"]
        source = source.replace(
            f"<title>{expected_title}</title>",
            "<title>Old title | GolfRaw</title>",
            1,
        )
        source = source.replace(
            f'content="{expected_title}"',
            'content="Old title | GolfRaw"',
        )
        with TemporaryDirectory() as directory:
            target = Path(directory) / source_path.name
            target.write_text(source, encoding="utf-8")
            with patch.object(
                sync_site,
                "production_html_pages",
                return_value=[
                    ("/news-2026-bmw-championship-round-3-scores-odds-recap", str(target))
                ],
            ):
                changed, pages = sync_site.normalize_seo_metadata()
            self.assertEqual((changed, pages), (1, 1))
            self.assertEqual(
                audit_metadata(target.read_text(encoding="utf-8"))["title"],
                expected_title,
            )

    def test_sync_validator_passes_the_current_title_description_contract(self):
        self.assertEqual(sync_site.validate_seo_metadata(), [])

    def test_current_pages_use_every_catalog_override(self):
        pages = dict(sync_site.production_html_pages())
        mismatches = []
        for route, override in ARTICLE_SEO_OVERRIDES.items():
            metadata = audit_metadata(Path(pages[route]).read_text(encoding="utf-8"))
            mismatches.extend(
                (route, field)
                for field, expected in override.items()
                if metadata[field] != expected
            )
        self.assertEqual([], mismatches)

    def test_override_only_validator_ignores_unrelated_page_contracts(self):
        pages = dict(sync_site.production_html_pages())
        problems = []
        for route in ARTICLE_SEO_OVERRIDES:
            path = Path(pages[route])
            problems.extend(validate_override_page(path, path.read_text(encoding="utf-8")))
        self.assertEqual([], problems)


if __name__ == "__main__":
    unittest.main()
