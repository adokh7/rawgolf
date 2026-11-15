"""DeChambeau 2027 page, rewritten 15 November 2026 (Task 14).

The page was published on 3 September around a report that DeChambeau was
"all in" on LIV 2.0. LIV then moved to wind down, so the premise no longer
held, and none of its eight external source links worked: three led to pages
that do not exist and five pointed to publishers' home pages. These checks keep
the rewrite sourced, current and consistent with its schema.
"""
import html
import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
SLUG = "bryson-dechambeau-liv-golf-2027"

REMOVED_LINKS = (
    "https://www.hitc.com/en-gb/2026/09/03/bryson-dechambeau-liv-golf-future/",
    "https://sports.yahoo.com/golf/article/bryson-dechambeau-liv-contract-expired-indianapolis-2026/",
    "https://heavy.com/sports/golf/liv-golf-investors-bc-partners/",
    "https://www.si.com/golf/",
    "https://www.cbssports.com/golf/",
    "https://www.reuters.com/world/",
    "https://frontofficesports.com/",
    "https://golf.com/news/liv-golf/",
)

# Analysis that no longer applies or could not be sourced.
REMOVED_CLAIMS = (
    "everything that can be verified points to him staying",
    "I couldn't open",
    "$7 million to $9 million",
    "2.6 million",
    "25% equity stake",
    "BC Partners holds a stake in his agency",
)

# Facts the rewrite rests on, each quoted from its linked source.
REQUIRED = (
    "value-maximizing wind-down",
    "full playing privileges on the European circuit in 2027",
    "a one-time, defined window",
    "contracted through 2026",
    "go about whatever is next the right way",
    "August 2027",
    "As of 15 November",
)


def page():
    return (ROOT / f"{SLUG}.html").read_text(encoding="utf-8")


def article(source):
    return source[source.index("<article"):source.index("</article>")]


def text(fragment):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragment)))


class DeChambeauUpdateTests(unittest.TestCase):
    def test_dead_and_homepage_links_are_gone(self):
        source = page()
        for url in REMOVED_LINKS:
            with self.subTest(url=url):
                self.assertNotIn(f'href="{url}"', source)

    def test_every_external_source_is_a_specific_article(self):
        body = article(page())
        external = re.findall(r'href="(https?://(?!www\.golfraw\.com)[^"]+)"', body)
        self.assertGreaterEqual(len(set(external)), 8)
        for url in external:
            with self.subTest(url=url):
                path = [part for part in urlsplit(url).path.split("/") if part]
                self.assertGreaterEqual(len(path), 2, "a home or section page is not a source")

    def test_obsolete_analysis_is_removed_and_current_facts_stay(self):
        body = text(article(page()))
        for phrase in REMOVED_CLAIMS:
            with self.subTest(removed=phrase):
                self.assertNotIn(phrase, body)
        for phrase in REQUIRED:
            with self.subTest(required=phrase):
                self.assertIn(phrase, body)

    def test_update_is_dated_and_points_to_the_record(self):
        source = page()
        self.assertIn('class="update-note"', source)
        self.assertIn("Updated 15 November 2026.", text(source))
        self.assertIn('"dateModified": "2026-11-15T12:00:00+01:00"', source)
        self.assertIn('content="2026-11-15T12:00:00+01:00"', source)
        body = article(source)
        for target in ("/liv-golf", "/corrections", "/news-2026-liv-golf-bankruptcy-chapter-11-explained"):
            self.assertIn(f'href="{target}"', body)

    def test_faq_schema_matches_the_visible_faq(self):
        source = page()
        visible = [text(q).strip() for q in re.findall(r'<div class="faq-item"><h3>(.*?)</h3>', source)]
        schema = []
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', source, re.S):
            data = json.loads(block)
            stack = [data]
            while stack:
                node = stack.pop()
                if isinstance(node, dict):
                    if node.get("@type") == "FAQPage":
                        schema = [q["name"] for q in node["mainEntity"]]
                    stack.extend(node.values())
                elif isinstance(node, list):
                    stack.extend(node)
        self.assertEqual(4, len(visible))
        self.assertEqual(visible, schema)

    def test_lead_photo_caption_matches_its_2024_signage(self):
        source = page()
        self.assertIn("AT LIV GOLF INDIANAPOLIS IN 2024", source)
        self.assertNotIn("CONTRACT EXPIRY LOOMS", source)

    def test_corrections_log_records_the_rewrite(self):
        log = (ROOT / "corrections.html").read_text(encoding="utf-8")
        self.assertIn('<span class="eid">ERR-071</span>', log)
        self.assertIn(f'<div class="e-story"><a href="/{SLUG}">', log)


if __name__ == "__main__":
    unittest.main()
