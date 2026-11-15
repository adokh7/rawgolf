"""Task 13 (15 November 2026): titles cut mid-phrase, and the Topgolf cluster.

An earlier version of scripts/fix_seo_audit.py cut long headlines at a word
boundary and wrote the fragment back as the <title>, so pages earning real
search demand went out as "The 4 Golf Majors Explained: Winners" or "Going to
Topgolf for the First Time? Here's". Eight of them were rewritten for the
queries each page earns, and registered in scripts/seo_metadata.py so the repair
script cannot rebuild them from the H1 and cut them again.

The three Topgolf pages each lead a different intent in Search Console (dress
code, first visit and rain, what Topgolf is). They stay separate, link to one
another, and use the brand's own spelling.
"""
import html
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from seo_metadata import ARTICLE_SEO_OVERRIDES  # noqa: E402

FIXED = {
    "golf-majors-guide": "The 4 Golf Majors Explained: Winners Since 2006 | GolfRaw",
    "topgolf-first-timers": "Topgolf First Time: Rain, Clubs and What to Expect | GolfRaw",
    "news-2026-fedexcup-bonus-pool-payout-structure-east-lake": "FedExCup Payout 2026: The $100M Bonus Pool | GolfRaw",
    "news-2026-fm-championship-field-tpc-boston": "2026 FM Championship: Field, Entry List and Winner | GolfRaw",
    "news-2026-jack-nicklaus-career-earnings-vs-modern-pga-tour": "Jack Nicklaus Career Earnings: $5.7M From 73 Wins | GolfRaw",
    "news-2026-jackson-koivun-tpc-southwind-fedex-st-jude": "Koivun at the 2026 FedEx St. Jude: How He Finished | GolfRaw",
    "news-2026-fedex-st-jude-round-1-tee-times-jackson-koivun": "Jackson Koivun Tee Time: FedEx St. Jude Round 1 | GolfRaw",
    "news-2026-tony-romo-withdraws-texas-state-open": "Tony Romo Out of Texas State Open: What's Confirmed",
    "what-to-wear-to-topgolf": "Topgolf Dress Code: What You Can (and Can't) Wear | GolfRaw",
}

# Titles that still stop mid-sentence partway through their own H1 (15 Nov 2026).
# This list may only shrink: fix a page, then delete its line.
KNOWN_CUT_TITLES = {
    "best-golf-courses-washington-state-golfweek-2026",
    "charity-golf-scrambles-access-guide",
    "golf-clubs-for-beginners",
    "greg-norman-1996-masters",
    "guides-playing-golf-in-your-fifties-distance-loss",
    "jean-van-de-velde-1999-open",
    "morikawa-61-travelers-championship-2026",
    "news-2026-7-wood-vs-3-iron-australian-golfers",
    "news-2026-aig-womens-open-lytham-yardage-history",
    "news-2026-aig-womens-open-tee-times-korda-hull",
    "news-2026-aussies-kiwis-ryan-fox-scottish-open",
    "news-2026-bmw-championship-round-3-scores-odds-recap",
    "news-2026-bmw-championship-tee-times-top-30-cut",
    "news-2026-brooks-koepka-absent-bellerive-bmw-championship",
    "news-2026-brooks-koepka-pga-tour-return-season-verdict",
    "news-2026-bryson-dechambeau-open-penalty-trump",
    "news-2026-bryson-dechambeau-pga-tour-return",
    "news-2026-bryson-dechambeau-water-bottle-bedminster",
    "news-2026-bryson-open-birkdale-penalty",
    "news-2026-charley-hull-four-putt-anna-huang-pif-london",
    "news-2026-corey-conners-australian-pga-presidents-cup",
    "news-2026-fedex-st-jude-championship-tpc-southwind-demotion",
    "news-2026-fox-62-open-rory-unloads",
    "news-2026-golf-ball-rollback-paused-colin-montgomerie",
    "news-2026-haeran-ryu-aig-womens-open",
    "news-2026-herbert-burns-62-record-birkdale",
    "news-2026-jeeno-thitikul-aig-womens-open",
    "news-2026-jordan-spieth-zero-top-10s-fedexcup-playoffs",
    "news-2026-koepka-wyndham-fedexcup-returning-member",
    "news-2026-lee-westwood-liv-golf-bedminster-expectations",
    "news-2026-lexi-thompson-pregnant-baby-daughter-lpga",
    "news-2026-liv-golf-bankruptcy-what-is-confirmed",
    "news-2026-liv-golf-equity-dp-world-tour-fines-2027",
    "news-2026-liv-golf-investor-bc-partners-dechambeau",
    "news-2026-liv-golf-line-of-credit-debt-rahm",
    "news-2026-liv-golf-michigan-martin-kaymer",
    "news-2026-liv-golf-michigan-team-championship-cancelled",
    "news-2026-liv-golf-staff-terminations",
    "news-2026-liv-players-pga-tour-value-data-gap",
    "news-2026-lucas-herbert-liv-golf-uk-61",
    "news-2026-maverick-mcnealy-fedexcup-top-50-bubble",
    "news-2026-max-homa-verdict-rory-mcilroy-swing",
    "news-2026-mcilroy-brutal-dechambeau-verdict",
    "news-2026-mcilroy-memphis-fedex-st-jude",
    "news-2026-megha-ganne-lpga-debut-inkster-award",
    "news-2026-memphis-championship-series-fedexcup",
    "news-2026-michigan-golf-tournaments-rocket-classic-liv-cancelled",
    "news-2026-nelly-korda-aig-womens-open",
    "news-2026-nick-faldo-liv-golf-comments",
    "news-2026-rob-bolton-rocket-classic-detroit-course-history",
    "news-2026-rocket-classic-detroit-golf-club-par-70",
    "news-2026-rory-mcilroy-fedex-st-jude-ceo-brian-rolapp",
    "news-2026-ryan-fox-62-record-birkdale",
    "news-2026-ryder-cup-qualifying-schedule",
    "news-2026-scheffler-mcilroy-bmw-championship-tee-times",
    "news-2026-scheffler-tour-championship-fedexcup-format-east-lake",
    "news-2026-scottie-scheffler-3m-open-round-2-unravels",
    "news-2026-scottie-scheffler-61-tpc-southwind-course-record",
    "news-2026-scottie-scheffler-bryson-dechambeau-penalty",
    "news-2026-si-woo-kim-open-choke",
    "news-2026-solheim-cup-big-names-missing",
    "news-2026-solheim-cup-dewi-weber-dutch-eligibility-let",
    "news-2026-texas-scramble-golf-survey",
    "news-2026-us-amateur-final-jack-whaley-jay-leng-merion",
    "news-2026-wildhorse-ladies-golf-classic-race-for-the-card",
    "news-2026-wyndham-championship-brennan-fedexcup-bubble-resolution",
    "rocket-classic-odds-cameron-young-detroit-golf-club",
    "scheffler-witb",
    "scottie-scheffler-footwork",
    "swing-guide",
    "the-viking-golf-event-denmark-norway-2027",
    "us-open-2026-prize-money",
    "us-open-final-pairing-scheffler-birthday",
    "us-open-shinnecock-setup-debate",
    "what-is-topgolf",
}

TOPGOLF_LINKS = {
    "what-to-wear-to-topgolf": ["/topgolf-first-timers", "/what-is-topgolf"],
    "topgolf-first-timers": ["/what-to-wear-to-topgolf"],
    "what-is-topgolf": ["/what-to-wear-to-topgolf", "/topgolf-first-timers"],
}


def page(slug):
    return (ROOT / f"{slug}.html").read_text(encoding="utf-8")


def head_value(source, pattern):
    match = re.search(pattern, source, re.S)
    return html.unescape(match.group(1)).strip() if match else None


def h1_text(source):
    raw = re.search(r"<h1[^>]*>(.*?)</h1>", source, re.S).group(1)
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", raw))).strip()


def title_core(title):
    return re.sub(r"\s*\|\s*GolfRaw\s*$", "", title).strip()


def cut_mid_sentence(source):
    core = title_core(head_value(source, r"<title>(.*?)</title>") or "")
    heading = h1_text(source) if "<h1" in source else ""
    return bool(core) and heading.startswith(core) and len(heading) > len(core) and heading[len(core)] == " "


class TitleRepairTests(unittest.TestCase):
    def test_fixed_titles_are_registered_and_rendered_in_every_mirror(self):
        for slug, title in FIXED.items():
            with self.subTest(slug=slug):
                self.assertEqual(title, ARTICLE_SEO_OVERRIDES["/" + slug]["title"])
                source = page(slug)
                self.assertEqual(title, head_value(source, r"<title>(.*?)</title>"))
                self.assertEqual(title, head_value(source, r'property="og:title" content="([^"]*)"'))
                self.assertEqual(title, head_value(source, r'name="twitter:title" content="([^"]*)"'))
                self.assertFalse(cut_mid_sentence(source))

    def test_schema_headline_is_the_reviewed_title_not_a_fragment(self):
        # article_schema.py mirrors the registry title into the headline.
        for slug in FIXED:
            with self.subTest(slug=slug):
                source = page(slug)
                headlines = []
                for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', source, re.S):
                    data = json.loads(block)
                    stack = [data]
                    while stack:
                        node = stack.pop()
                        if isinstance(node, dict):
                            if "headline" in node:
                                headlines.append(node["headline"])
                            stack.extend(node.values())
                        elif isinstance(node, list):
                            stack.extend(node)
                self.assertEqual([title_core(FIXED[slug])], headlines)

    def test_registry_card_titles_match_the_reviewed_titles(self):
        data = json.loads((ROOT / "articles.json").read_text(encoding="utf-8"))
        articles = data if isinstance(data, list) else data.get("articles", data)
        by_slug = {a.get("slug"): a for a in articles}
        for slug, title in FIXED.items():
            with self.subTest(slug=slug):
                self.assertEqual(title_core(title), html.unescape(by_slug[slug]["title"]))

    def test_no_new_title_is_cut_mid_sentence(self):
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        cut = set()
        for route in re.findall(r"<loc>https://www\.golfraw\.com/?([^<]*)</loc>", sitemap):
            path = ROOT / f"{route or 'index'}.html"
            if path.exists() and cut_mid_sentence(path.read_text(encoding="utf-8")):
                cut.add(route)
        self.assertEqual(set(), cut - KNOWN_CUT_TITLES, "new mid-sentence title cuts")
        self.assertEqual(set(), KNOWN_CUT_TITLES - cut, "fixed pages: delete them from KNOWN_CUT_TITLES")


class TopgolfClusterTests(unittest.TestCase):
    def test_pages_stay_separate_canonical_and_indexable(self):
        for slug in TOPGOLF_LINKS:
            with self.subTest(slug=slug):
                source = page(slug)
                self.assertIn(f'<link rel="canonical" href="https://www.golfraw.com/{slug}"', source)
                self.assertIn('name="robots" content="index, follow', source)

    def test_cluster_pages_link_to_each_other_in_the_article(self):
        for slug, targets in TOPGOLF_LINKS.items():
            source = page(slug)
            body = source[source.index('<div class="article-body">'):source.index("</article>")]
            for target in targets:
                with self.subTest(slug=slug, target=target):
                    self.assertIn(f'href="{target}"', body)

    def test_brand_spelling_and_dress_code_answer(self):
        for slug in TOPGOLF_LINKS:
            self.assertNotIn("TopGolf", page(slug))
        description = head_value(page("what-to-wear-to-topgolf"), r'name="description" content="([^"]*)"')
        self.assertTrue(description.startswith("Topgolf has no formal dress code."))
        self.assertIn("topgolf.com/us/faq", page("what-to-wear-to-topgolf"))


if __name__ == "__main__":
    unittest.main()
