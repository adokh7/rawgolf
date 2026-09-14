"""Google Search Console ownership must never silently disappear.

The HTML-tag verification lives on the homepage only. scripts/fix_seo_audit.py
owns it: every repair strips stray copies and re-emits exactly one, and
validation fails when it is missing or changed.
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import fix_seo_audit as audit  # noqa: E402

TOKEN = "vOoo-SAOJObX4sDlOxnabLsAX2gnOOGdloMJ0ePIHvY"
TAG = f'<meta name="google-site-verification" content="{TOKEN}" />'
HOME = ROOT / "index.html"
TAG_RE = re.compile(r'<meta\b[^>]*name="google-site-verification"[^>]*>', re.I)


def head_of(source: str) -> str:
    return source[: source.index("</head>")]


class SiteVerificationTests(unittest.TestCase):
    def test_homepage_carries_exactly_one_exact_tag_in_head(self):
        source = HOME.read_text(encoding="utf-8")
        self.assertEqual([TAG], TAG_RE.findall(source))
        self.assertIn(TAG, head_of(source))

    def test_generator_constant_matches_the_verified_token(self):
        self.assertEqual(TOKEN, audit.GOOGLE_SITE_VERIFICATION)
        self.assertEqual(TAG, audit.GOOGLE_VERIFICATION_TAG)

    def test_repair_keeps_exactly_one_tag_on_the_homepage(self):
        repaired, _ = audit.repair_source(HOME, HOME.read_text(encoding="utf-8"))
        self.assertEqual([TAG], TAG_RE.findall(repaired))
        self.assertIn(TAG, head_of(repaired))

    def test_repair_restores_a_removed_or_duplicated_tag(self):
        source = HOME.read_text(encoding="utf-8")
        stripped = source.replace(TAG, "")
        self.assertEqual([], TAG_RE.findall(stripped))
        restored, _ = audit.repair_source(HOME, stripped)
        self.assertEqual([TAG], TAG_RE.findall(restored))

        doubled = source.replace("</head>", f"  {TAG}\n</head>", 1)
        self.assertEqual(2, len(TAG_RE.findall(doubled)))
        deduped, _ = audit.repair_source(HOME, doubled)
        self.assertEqual([TAG], TAG_RE.findall(deduped))

    def test_validation_fails_when_the_homepage_tag_is_missing(self):
        source = HOME.read_text(encoding="utf-8")
        errors = audit.validate_page(HOME, source.replace(TAG, ""))
        self.assertTrue(any("google-site-verification" in e for e in errors), errors)
        self.assertFalse(
            any("google-site-verification" in e for e in audit.validate_page(HOME, source))
        )

    def test_other_pages_are_not_given_the_tag(self):
        page = ROOT / "news.html"
        repaired, _ = audit.repair_source(page, page.read_text(encoding="utf-8"))
        self.assertEqual([], TAG_RE.findall(repaired))


if __name__ == "__main__":
    unittest.main()
