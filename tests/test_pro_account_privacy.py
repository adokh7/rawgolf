"""The Pro account pages must never hand their URL credential to analytics.

pro-thanks carries Stripe's ?session_id= (GET /api/pro-claim turns it into a Pro
pass) and pro-restore carries a restore token in #t=. The URLs stay
bookmarkable, so the protection is: GA4 sees the path only, and the referrer
policy stops the full URL becoming the next page's page_referrer.
"""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGES = ("pro-thanks.html", "pro-restore.html")


class ProAccountPrivacyTests(unittest.TestCase):
    def test_ga4_sees_the_path_only(self):
        for name in PAGES:
            with self.subTest(name):
                source = (ROOT / name).read_text(encoding="utf-8")
                configs = re.findall(r"gtag\('config', 'G-PMECW4VW66'(.*?)\);", source, re.S)
                self.assertEqual(1, len(configs), "exactly one GA4 config")
                self.assertIn("page_location: location.origin + location.pathname", configs[0])
                self.assertIn("page_referrer: document.referrer.replace(", configs[0])

    def test_referrer_policy_is_in_the_head(self):
        # Cross-origin fetches already send only the origin by default; the
        # policy matters for same-origin navigation away from the page.
        for name in PAGES:
            with self.subTest(name):
                source = (ROOT / name).read_text(encoding="utf-8")
                meta = source.find('<meta name="referrer" content="strict-origin">')
                self.assertGreater(meta, -1)
                self.assertLess(meta, source.find("</head>"))
                self.assertEqual(1, source.count('name="referrer"'))

    def test_builder_owns_the_protection(self):
        builder = (ROOT / "scripts" / "build_pro_pages.py").read_text(encoding="utf-8")
        self.assertIn("def account_safe(", builder)
        self.assertIn('REFERRER_META = \'<meta name="referrer" content="strict-origin">\'', builder)

    def test_claim_flow_still_reads_the_session_id(self):
        # The fix must not change the thank-you flow: the page still claims by
        # the session id in its own URL.
        source = (ROOT / "pro-thanks.html").read_text(encoding="utf-8")
        self.assertIn("sid = q.get('session_id')", source)
        self.assertIn("Pro.claim(sid)", source)


if __name__ == "__main__":
    unittest.main()
