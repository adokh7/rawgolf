"""Normalize local raster image attributes in the deployable static output."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from scripts.image_markup import (
        ROOT,
        _ImageParser,
        audit_image_markup,
        normalize_image_markup,
        production_html_files,
    )
except ImportError:  # direct execution from the scripts directory
    from image_markup import (
        ROOT,
        _ImageParser,
        audit_image_markup,
        normalize_image_markup,
        production_html_files,
    )


def normalize_output(root: Path = ROOT, write: bool = False) -> tuple[int, int]:
    changed_files = 0
    changed_images = 0
    for page_path in production_html_files(root):
        source = page_path.read_text(encoding="utf-8")
        normalized = normalize_image_markup(source, page_path, root)
        if normalized == source:
            continue
        changed_files += 1
        # The normalizer only replaces existing start tags. Count changed tags
        # from the two parsed inventories rather than comparing total counts.
        before_parser = _ImageParser(source)
        before_parser.feed(source)
        after_parser = _ImageParser(normalized)
        after_parser.feed(normalized)
        changed_images += sum(
            1
            for before, after in zip(before_parser.images, after_parser.images)
            if before.get("raw") != after.get("raw")
        )
        if write:
            page_path.write_text(normalized, encoding="utf-8")
    return changed_files, changed_images


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write normalized HTML")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    before = audit_image_markup(root)
    changed_files, _ = normalize_output(root, write=args.apply)
    after = audit_image_markup(root) if args.apply else before
    mode = "normalized" if args.apply else "would normalize"
    print(f"Image markup: {mode} {changed_files} file(s)")
    print(
        "Image markup counts: "
        f"missing dimensions {after['missing_dimensions']}, "
        f"missing srcset {after['missing_srcset']}, "
        f"invalid candidates {after['invalid_srcset_candidates']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
