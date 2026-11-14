"""Publisher identity pages must describe the site as it actually runs (Task 6, 2026-11-15).

The About and Terms pages said GolfRaw had "no premium tier... and no plan to
add one" while GolfRaw Pro was live as a paid Stripe subscription. Contact and
Manifesto described a newsroom ("the office wall") and a sourcing record the
site did not have, and 16 live articles credited an "Editorial Staff" that does
not exist. These checks keep those statements from coming back.
"""
import html
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read(name):
    return (ROOT / name).read_text(encoding="utf-8")


def visible(name):
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", read(name), flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s)))


def redirected_routes():
    config = json.loads(read("vercel.json"))
    return {r["source"].lstrip("/") for r in config.get("redirects", [])}


class IdentityPagesTests(unittest.TestCase):
    def test_about_describes_pro_and_drops_no_premium_claim(self):
        text = visible("about.html")
        self.assertNotIn("no premium tier", text)
        self.assertNotIn("no plan to add one", text)
        self.assertIn("GolfRaw Pro", text)
        self.assertIn("Stripe", text)

    def test_terms_and_privacy_describe_pro_payments(self):
        terms = visible("terms.html")
        self.assertNotIn("eventually, reader newsletter engagement", terms)
        self.assertIn("GolfRaw Pro", terms)
        self.assertIn("Stripe", terms)
        privacy = visible("privacy.html")
        self.assertIn("Stripe", privacy)
        self.assertIn("Resend", privacy)

    def test_about_schema_points_only_at_real_policies(self):
        about = read("about.html")
        self.assertNotIn('"diversityPolicy"', about)
        self.assertIn('"ownershipFundingInfo": "https://www.golfraw.com/about"', about)

    def test_no_invented_newsroom_claims(self):
        self.assertNotIn("office wall", visible("contact.html"))
        self.assertNotIn("Best correction of the month", read("contact.html"))
        manifesto = visible("manifesto.html")
        self.assertNotIn("Rawgolf", manifesto)
        self.assertNotIn("Every claim we publish traces back", manifesto)

    def test_no_live_page_credits_an_editorial_staff(self):
        redirected = redirected_routes()
        offenders = [
            p.name
            for p in sorted(ROOT.glob("*.html"))
            if p.stem not in redirected and "Editorial Staff" in p.read_text(encoding="utf-8")
        ]
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
