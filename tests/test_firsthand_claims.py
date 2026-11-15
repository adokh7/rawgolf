"""Guards against unsupported first-hand reporting and withheld false graphics (Task 8, 15 Nov 2026).

GolfRaw publishes as a desk and does not report on site. An article template
carried a sample standfirst ("We walked the setup with two tour caddies who told
us...") and an "ON SITE, OAKMONT PA" byline, and both leaked into 15 published
pages. Two hero graphics also carried demonstrably false claims. These checks
keep both problems from coming back.

If GolfRaw genuinely reports a story first-hand, add the page to
FIRSTHAND_VERIFIED with a note on who did the reporting and when.
"""
import html
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FIRSTHAND = re.compile(
    r"\btold us\b|\btold GolfRaw\b|\bwalked (?:the course|the setup) with us\b|\bwe walked\b|"
    r"\bwalked us through\b|\bour caddie conversations\b|\bon the ground (?:all weekend|at)\b|"
    r"\bwe (?:spoke|talked) (?:to|with)\b|\bin an interview with GolfRaw\b",
    re.IGNORECASE,
)
# The template's byline tag, matched in capitals so ordinary reporting
# ("Lilia Vu is on site as the alternate") is not caught.
ONSITE_BYLINE = re.compile(r"\bON SITE\b")

# slug -> who reported it first-hand and when. Empty until GolfRaw has real reporting.
FIRSTHAND_VERIFIED: dict[str, str] = {}

# Graphics withheld because they contain demonstrably false claims (see ERR-046).
# The files stay in the repo; nothing may display them or offer them as a social preview.
WITHHELD_IMAGES = [
    "news-2026-blades-brown-19-pga-tour-card",
    "news-2026-kevin-hart-golf-youtube-132",
]
PLACEHOLDER = "/public/golfraw-card-placeholder.webp"


def sitemap_routes():
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    return re.findall(r"<loc>https://www\.golfraw\.com/([^<]*)</loc>", sitemap)


def production_pages():
    for route in sitemap_routes():
        path = ROOT / f"{route or 'index'}.html"
        if path.exists():
            yield route or "index", path


def without_documented_errors(source):
    source = re.sub(r'<aside class="update-note".*?</aside>', " ", source, flags=re.S)
    return re.sub(r'<span class="wrong">.*?</span>', " ", source, flags=re.S)


def readable(source):
    """Visible text plus metadata, so a claim in a description or JSON-LD counts too."""
    source = without_documented_errors(source)
    meta = " ".join(re.findall(r'content="([^"]*)"', source))
    ld = " ".join(re.findall(r'<script type="application/ld\+json">(.*?)</script>', source, re.S))
    body = re.sub(r"<(script|style)\b.*?</\1>", " ", source, flags=re.S)
    return html.unescape(" ".join([re.sub(r"<[^>]+>", " ", body), meta, ld]))


class FirsthandClaimTests(unittest.TestCase):
    def test_no_unsupported_firsthand_reporting_on_production_pages(self):
        problems = []
        for route, path in production_pages():
            if route in FIRSTHAND_VERIFIED:
                continue
            text = readable(path.read_text(encoding="utf-8"))
            match = FIRSTHAND.search(text) or ONSITE_BYLINE.search(text)
            if match:
                problems.append((route, match.group(0)))
        self.assertEqual([], problems)

    def test_article_template_does_not_seed_firsthand_claims(self):
        source = (ROOT / "article-template.html").read_text(encoding="utf-8")
        match = FIRSTHAND.search(readable(source)) or ONSITE_BYLINE.search(readable(source))
        self.assertIsNone(match, match and match.group(0))
        self.assertNotIn("PHOTO: GolfRaw", source)

    def test_template_sample_text_did_not_leak(self):
        # The template's sample standfirst, byline date and update time.
        for route, path in production_pages():
            source = html.unescape(without_documented_errors(path.read_text(encoding="utf-8")))
            with self.subTest(route=route):
                self.assertNotIn("Greens running 15 on the stimp", source)
                self.assertNotIn("FRI 13 JUN 2026 · 07:30", source)
                self.assertNotIn("UPDATED 09:42", source)


class WithheldGraphicsTests(unittest.TestCase):
    def published_sources(self):
        for _, path in production_pages():
            yield path.name, path.read_text(encoding="utf-8")
        for name in ("articles.json", "feed.xml", "sitemap.xml", "news-sitemap.xml"):
            path = ROOT / name
            if path.exists():
                yield name, path.read_text(encoding="utf-8")

    def test_withheld_graphics_are_not_displayed_or_shared(self):
        problems = []
        for name, source in self.published_sources():
            for stem in WITHHELD_IMAGES:
                if re.search(re.escape(stem) + r"(?:-\d+)?\.webp", source):
                    problems.append((name, stem))
        self.assertEqual([], problems)

    def test_withheld_files_are_preserved(self):
        for stem in WITHHELD_IMAGES:
            with self.subTest(stem=stem):
                self.assertTrue((ROOT / f"{stem}.webp").exists())
                for width in (400, 800, 1200):
                    self.assertTrue((ROOT / "public" / f"{stem}-{width}.webp").exists())

    def test_withheld_articles_use_the_placeholder_preview(self):
        registry = {a["slug"]: a for a in json.loads((ROOT / "articles.json").read_text(encoding="utf-8"))["articles"]}
        for stem in WITHHELD_IMAGES:
            with self.subTest(stem=stem):
                source = (ROOT / f"{stem}.html").read_text(encoding="utf-8")
                self.assertIn(f'<meta property="og:image" content="https://www.golfraw.com{PLACEHOLDER}">', source)
                self.assertIn(f'<meta name="twitter:image" content="https://www.golfraw.com{PLACEHOLDER}">', source)
                self.assertEqual(registry[stem]["image"], PLACEHOLDER)
        self.assertTrue((ROOT / PLACEHOLDER.lstrip("/")).exists())


if __name__ == "__main__":
    unittest.main()
