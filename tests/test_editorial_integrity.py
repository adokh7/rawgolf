"""Site-wide editorial integrity checks (Task 5, 2026-11-14).

Each check guards a defect that was found on live pages and fixed:
fabricated quotes attributed to real people, invented sourcing in article
text, dollar figures stripped by a publishing error, corrections that were
never logged, and pages referencing images that do not exist.
"""
import html
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Quotes that were found to be fabricated or misattributed and removed.
# None of these may reappear on a production page.
REMOVED_FABRICATIONS = [
    "make the golf swing more important than the golf shot",
    "I'm so bad, just awful",
    "a genuine integrity problem, not just etiquette",
    "subconsciously trying not to hurt yourself",
    "the math simply doesn't support that",
    "championship finish line frequently turns into a procession",
    "a great buzz around the tournament because Shane",
    "going to be leading my home tournament",
    "didn't make anything over a bogey",
    "Former Ryder Cup captain, speaking off the record",
    "RawGolf Hardware Testing Lab",
    "Tour caddie, 14 years on the bag",
    "East Lake Media Availability",
    "We had a defined window earlier this year",
    "blisters are gone now, energy is back",
    "driver showed up uninvited",
    "Earning your way on points is always the goal",
    "transformative private equity transaction",
    "My commitment to European golf and the Ryder Cup has never wavered",
    "great natural wonders of links golf",
    "lines that fit your eye",
    "no warm-up holes out there",
    "LPGA Tour Player Financial Ledger Disclosure",
]

# Phrases that claim first-hand or confidential sourcing GolfRaw does not have.
INVENTED_SOURCING = re.compile(
    r"told GolfRaw|to GolfRaw off the record|speaking off the record|GolfRaw has learned|"
    r"sources (?:close to|told) GolfRaw|GolfRaw (?:obtained|spoke (?:to|with))",
    re.IGNORECASE,
)

# A thousands group with no digit or currency sign in front of it: "$500,000"
# printed as ",000" when a publishing step swallowed "$500".
STRIPPED_FIGURE = re.compile(r"(?<![\$\d.,\w€£])(?:,\d{3})+(?!\d)")

HOUSE = {"GolfRaw Editorial"}


def sitemap_routes():
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    return re.findall(r"<loc>https://www\.golfraw\.com/([^<]*)</loc>", sitemap)


def production_pages():
    pages = []
    for route in sitemap_routes():
        path = ROOT / f"{route or 'index'}.html"
        if path.exists():
            pages.append((route or "index", path))
    return pages


def without_documented_errors(source):
    """Drop text that quotes an error on purpose: update notes and the
    struck-through "We wrote" column of the corrections log."""
    source = re.sub(r'<aside class="update-note".*?</aside>', " ", source, flags=re.S)
    return re.sub(r'<span class="wrong">.*?</span>', " ", source, flags=re.S)


def visible_text(source):
    source = re.sub(r"<(script|style)\b.*?</\1>", " ", source, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", " ", source))


class EditorialIntegrityTests(unittest.TestCase):
    def test_removed_fabricated_quotes_do_not_return(self):
        problems = []
        for route, path in production_pages():
            text = html.unescape(without_documented_errors(path.read_text(encoding="utf-8")))
            text = text.replace("’", "'")
            for phrase in REMOVED_FABRICATIONS:
                if phrase in text:
                    problems.append((route, phrase))
        self.assertEqual([], problems)

    def test_no_invented_first_hand_sourcing(self):
        problems = []
        for route, path in production_pages():
            article = re.search(r"<article.*?</article>", path.read_text(encoding="utf-8"), re.S)
            if not article:
                continue
            body = re.sub(r'<aside class="update-note".*?</aside>', " ", article.group(0), flags=re.S)
            match = INVENTED_SOURCING.search(visible_text(body))
            if match:
                problems.append((route, match.group(0)))
        self.assertEqual([], problems)

    def test_no_stripped_dollar_figures(self):
        problems = []
        for route, path in production_pages():
            source = without_documented_errors(path.read_text(encoding="utf-8"))
            for text in (visible_text(source), html.unescape(" ".join(re.findall(r'content="([^"]*)"', source)))):
                match = STRIPPED_FIGURE.search(text)
                if match:
                    problems.append((route, text[max(0, match.start() - 30):match.end() + 10]))
                    break
        self.assertEqual([], problems)

    def test_cite_attributions_are_house_or_linked(self):
        problems = []
        for route, path in production_pages():
            source = path.read_text(encoding="utf-8")
            for block in re.findall(r"<blockquote\b.*?</blockquote>", source, re.S):
                cite = re.search(r"<cite>(.*?)</cite>", block, re.S)
                if not cite:
                    continue
                label = html.unescape(re.sub(r"<[^>]+>", "", cite.group(1))).strip(" —-")
                if label not in HOUSE and "href=" not in block:
                    problems.append((route, label))
        self.assertEqual([], problems)


class CorrectionsLogTests(unittest.TestCase):
    def setUp(self):
        self.source = (ROOT / "corrections.html").read_text(encoding="utf-8")
        self.entries = re.findall(r'<article class="entry">.*?</article>', self.source, re.S)

    def test_tally_matches_entries(self):
        total = len(self.entries)
        factual = sum('class="sev factual"' in e for e in self.entries)
        minor = sum('class="sev minor"' in e for e in self.entries)
        self.assertIn(f'<span class="n">{total}</span><span class="l">Corrections to date</span>', self.source)
        self.assertIn(f'<span class="n red">{factual}</span><span class="l">Factual errors</span>', self.source)
        self.assertIn(f'<span class="n">{minor}</span><span class="l">Minor / typo class</span>', self.source)

    def test_entry_ids_are_unique_and_dated(self):
        ids = [re.search(r"ERR-(\d+)", e).group(1) for e in self.entries]
        self.assertEqual(len(ids), len(set(ids)))
        for entry in self.entries:
            self.assertRegex(entry, r"LOGGED \d{2} [A-Z]{3} \d{4}")

    def test_unverifiable_legacy_entries_keep_their_editors_note(self):
        # ERR-001 to ERR-003 describe articles that were never published.
        for entry in self.entries:
            number = int(re.search(r"ERR-(\d+)", entry).group(1))
            if number <= 3:
                self.assertIn("Editor&rsquo;s note", entry, f"ERR-{number:03d}")
                self.assertIn("not a record of a real correction", entry, f"ERR-{number:03d}")

    def test_new_entries_link_to_live_pages(self):
        routes = set(sitemap_routes())
        for entry in self.entries:
            number = int(re.search(r"ERR-(\d+)", entry).group(1))
            href = re.search(r'<div class="e-story"><a href="([^"]*)"', entry).group(1)
            if number <= 3:
                continue  # legacy entries predate this check; see the trust audit
            self.assertIn(href.lstrip("/"), routes, f"ERR-{number:03d} links to {href}")


class ReferencedImagesExistTests(unittest.TestCase):
    def test_every_image_on_a_production_page_exists(self):
        missing = []
        for route, path in production_pages():
            source = path.read_text(encoding="utf-8")
            refs = set(re.findall(r'(?:src|content|href)="(?:https://www\.golfraw\.com)?(/[^"?#]+\.(?:webp|png|jpe?g|gif|avif))', source))
            for srcset in re.findall(r'srcset="([^"]+)"', source):
                for candidate in srcset.split(","):
                    url = candidate.strip().split(" ")[0].split("?")[0]
                    if url.startswith("/"):
                        refs.add(url)
            refs |= set(re.findall(r'"(?:url|contentUrl|image)":\s*"https://www\.golfraw\.com(/[^"?]+\.(?:webp|png|jpe?g))', source))
            for url in refs:
                if not (ROOT / url.lstrip("/")).exists():
                    missing.append((route, url))
        self.assertEqual([], missing)


if __name__ == "__main__":
    unittest.main()
