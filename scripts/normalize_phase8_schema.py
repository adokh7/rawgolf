#!/usr/bin/env python3
"""Check or apply the Phase 8 JSON-LD contract on the public page set."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.schema_normalizer import normalize_phase8_pages


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write normalized JSON-LD to the scoped pages")
    parser.add_argument("--check", action="store_true", help="check the scoped pages without writing")
    args = parser.parse_args(argv)
    changed, errors = normalize_phase8_pages(apply=args.apply)
    mode = "updated" if args.apply else "drifted"
    print(f"Phase 8 schema pages {mode}: {changed}")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    if not args.apply and changed:
        print("Run with --apply to update the scoped pages.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
