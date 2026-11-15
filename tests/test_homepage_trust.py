"""Homepage trust and freshness (15 November 2026).

The homepage carried claims nothing backed: an "UNSOURCED RUMOURS 0" counter,
a newsletter promising a Friday email that has never been sent, a Vault that
"drops every Sunday", a June story still flagged NEW, and a hand-written
ticker that announced summer events in November. These checks keep that from
coming back, and keep the ticker and hero lead generated from the registry so
they cannot go stale.
"""
import html
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import sync_site  # noqa: E402


def visible(source):
    """The page as rendered: comments, scripts and styles removed."""
    source = re.sub(r"<!--.*?-->", " ", source, flags=re.S)
    return re.sub(r"<(script|style)\b.*?</\1>", " ", source, flags=re.S | re.I)


def homepage():
    return (ROOT / "index.html").read_text(encoding="utf-8")


def registry():
    data = json.loads((ROOT / "articles.json").read_text(encoding="utf-8"))
    articles = data if isinstance(data, list) else data.get("articles", data)
    return [a for a in articles if not a.get("alias_of")]


def between(source, start, end):
    return source[source.index(start) + len(start):source.index(end)]


class HomepageTrustTests(unittest.TestCase):
    def test_no_unbacked_promises_or_dead_story_links(self):
        page = html.unescape(visible(homepage()))
        for phrase in (
            "UNSOURCED RUMOURS",
            "No unsourced rumours",
            "Every Friday",
            "tour leaks",
            "PR reps tried to kill",
            "every Sunday",
            "currently sealed",
            "Rocket Classic: Detroit Golf Club debuts",
        ):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase.lower(), page.lower())
        self.assertNotIn('href="#"', visible(homepage()))
        self.assertNotRegex(visible(homepage()), r">NEW</span>")

    def test_placeholder_teasers_are_gone_from_the_source(self):
        source = homepage()
        for phrase in ("We tracked 50 club golfers", "what the medical file really said", "PLACEHOLDER"):
            self.assertNotIn(phrase, source)

    def test_newsletter_signup_is_hidden_until_sending_is_live(self):
        source = visible(homepage())
        self.assertNotIn("rawgolf-newsletter-form", source)
        self.assertNotIn("api.hsforms.com", homepage())

    def test_ticker_and_lead_are_generated_from_the_newest_articles(self):
        source = homepage()
        newest = sync_site.newest_articles(registry(), sync_site.HOMEPAGE_TICKER_LIMIT)
        ticker = between(source, sync_site.HOMEPAGE_TICKER_START, sync_site.HOMEPAGE_TICKER_END)
        shown = re.findall(r'<span>• <b>[^<]*</b> <a href="([^"]+)">', ticker)
        self.assertEqual([sync_site.get_url(a) for a in newest], shown)
        self.assertEqual(len(shown), ticker.count('aria-hidden="true"'))
        lead = between(source, sync_site.HOMEPAGE_LEAD_START, sync_site.HOMEPAGE_LEAD_END)
        self.assertIn(f'href="{sync_site.get_url(newest[0])}"', lead)
        self.assertIn(sync_site.display_date(newest[0]), lead)

    def test_card_headings_do_not_repeat_the_brand_suffix(self):
        for page in ("index.html", "news.html", "pga-tour.html", "guides.html", "tournaments.html",
                     "liv-golf.html", "gear.html", "players.html", "vintage-golf-history.html"):
            with self.subTest(page=page):
                source = (ROOT / page).read_text(encoding="utf-8")
                self.assertNotRegex(source, r"\|\s*GolfRaw\s*(</a>)?</h3>")

    def test_card_title_strips_only_a_trailing_brand(self):
        self.assertEqual("A | B", sync_site.card_title({"title": "A | B | GolfRaw"}))
        self.assertEqual("GolfRaw Guides", sync_site.card_title({"title": "GolfRaw Guides"}))


if __name__ == "__main__":
    unittest.main()
