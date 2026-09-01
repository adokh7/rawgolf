#!/usr/bin/env python3
"""Regenerate only the standard and Google News sitemap outputs."""

import argparse
import sys
from datetime import date

try:
    from scripts.sync_site import load, write_news_sitemap, write_sitemap
except ImportError:
    from sync_site import load, write_news_sitemap, write_sitemap


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--as-of",
        type=date.fromisoformat,
        default=None,
        help="date used for the two-day News sitemap window (YYYY-MM-DD)",
    )
    args = parser.parse_args(argv)
    articles = load()
    standard_count = write_sitemap(articles)
    news_count = write_news_sitemap(articles, today=args.as_of)
    print(f"sitemap.xml: {standard_count} URLs")
    print(f"news-sitemap.xml: {news_count} recent news URLs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
