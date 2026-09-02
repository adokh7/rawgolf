"""Regression checks for the Task 8 internal-link architecture changes."""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def hrefs(path):
    return set(re.findall(r'href=["\']([^"\']+)', path.read_text(encoding="utf-8")))


class InternalLinkingTests(unittest.TestCase):
    def test_homepage_ratings_strip_exposes_ratings_and_full_board(self):
        links = hrefs(ROOT / "index.html")
        self.assertIn("/ratings", links)
        self.assertIn("/full-board", links)

    def test_ratings_context_exposes_full_board(self):
        self.assertIn("/full-board", hrefs(ROOT / "ratings.html"))


if __name__ == "__main__":
    unittest.main()
