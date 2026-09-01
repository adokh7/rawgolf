#!/usr/bin/env python3
"""Repair and validate Article/NewsArticle JSON-LD in production HTML."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from scripts.article_schema import normalize_paths
    from scripts.sync_site import sitemap_page_records
except ImportError:  # direct execution from the scripts directory
    from article_schema import normalize_paths
    from sync_site import sitemap_page_records


def _paths() -> list[Path]:
    return [Path(record["path"]) for record in sitemap_page_records().values()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true", help="repair production HTML in place")
    mode.add_argument("--check", action="store_true", help="audit without writing")
    args = parser.parse_args()

    changed, article_pages, findings = normalize_paths(_paths(), apply=args.apply)
    errors = [finding for finding in findings if "error" in finding]
    remaining = []
    unresolved = []
    duplicates = 0
    malformed = 0
    for finding in findings:
        if "error" in finding:
            continue
        duplicates += finding["duplicate"]
        malformed += finding["malformed"]
        unresolved.extend((finding["path"], field) for field in finding["unresolved"])
        invalid_missing = set(finding["missing"]) - set(finding["unresolved"])
        invalid_mismatch = {
            field for field, count in finding["mismatches"].items() if count
        }
        if invalid_missing or invalid_mismatch:
            remaining.append((finding["path"], sorted(invalid_missing | invalid_mismatch)))

    verb = "repaired" if args.apply else "checked"
    print(f"Article schema: {verb} {article_pages} page(s); changed {changed}")
    print(f"  duplicate article entities: {duplicates}")
    print(f"  malformed JSON-LD blocks: {malformed}")
    if errors:
        for finding in errors:
            print(f"  ERROR {finding['path']}: {finding['error']}", file=sys.stderr)
    if remaining:
        for path, fields in remaining:
            print(f"  REMAINING {path}: {', '.join(fields)}")
    if unresolved:
        print(f"  unresolved authoritative data: {len(unresolved)}")
        for path, field in unresolved:
            print(f"    {path}: {field}")
    else:
        print("  unresolved authoritative data: 0")

    return 1 if errors or remaining else 0


if __name__ == "__main__":
    raise SystemExit(main())

