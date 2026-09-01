import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TIGER_LIVE_ROUTE = "/news-every-shot-tiger-woods-80th-win-2018"
TIGER_LEGACY_ROUTE = "/every-shot-tiger-woods-80th-win-2018"
BAG_LIVE_ROUTE = "/tools-bag-audit"
BAG_LEGACY_ROUTE = "/tools/bag-audit"

TIGER_REFERENCE_RE = re.compile(
    r'(?:href=["\']|https://www\.golfraw\.com|"canonical"\s*:\s*["\'])'
    r'/every-shot-tiger-woods-80th-win-2018(?:[#"\'/?]|$)'
)
BAG_REFERENCE_RE = re.compile(
    r'href=["\']/tools/bag-audit(?:[#"\'/?]|$)'
)

SOURCE_AND_OUTPUTS = (
    "create_money_list.py",
    "create_tiger.py",
    "add_tiger_registry.py",
    "create_hybrid.py",
    "news-2026-tiger-woods-career-money-list-record.html",
    "news-every-shot-tiger-woods-80th-win-2018.html",
    "why-pros-are-ditching-hybrids.html",
    "articles.json",
    "sitemap.xml",
)


class LegacyRouteReferenceTests(unittest.TestCase):
    def test_deployable_sources_and_outputs_use_live_routes(self):
        for relative in SOURCE_AND_OUTPUTS:
            with self.subTest(file=relative):
                source = (ROOT / relative).read_text(encoding="utf-8")
                self.assertIsNone(TIGER_REFERENCE_RE.search(source))
                self.assertIsNone(BAG_REFERENCE_RE.search(source))

        money_source = (ROOT / "news-2026-tiger-woods-career-money-list-record.html").read_text(
            encoding="utf-8"
        )
        hybrid_source = (ROOT / "why-pros-are-ditching-hybrids.html").read_text(
            encoding="utf-8"
        )
        self.assertEqual(3, money_source.count(f'href="{TIGER_LIVE_ROUTE}"'))
        self.assertEqual(3, hybrid_source.count(f'href="{BAG_LIVE_ROUTE}"'))
        self.assertNotIn(TIGER_LEGACY_ROUTE, money_source)
        self.assertNotIn(BAG_LEGACY_ROUTE, hybrid_source)


if __name__ == "__main__":
    unittest.main()
