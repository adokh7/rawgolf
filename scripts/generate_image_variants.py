"""Generate safe responsive image variants for assets used by the site.

Only local raster images referenced by deployable HTML are considered.  The
generator never overwrites an existing variant, upscales, crops, or changes
the original asset.
"""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover - exercised only without Pillow
    raise SystemExit("Pillow is required to generate responsive image variants") from exc

try:
    from scripts.image_markup import ROOT, _asset_path, iter_image_records
except ImportError:  # direct execution from the scripts directory
    from image_markup import ROOT, _asset_path, iter_image_records


TARGET_WIDTHS = (400, 800, 1200)


def _used_assets(root: Path) -> list[Path]:
    assets: set[Path] = set()
    for _, info in iter_image_records(root):
        attrs = info["attrs"]
        assert isinstance(attrs, dict)
        path = _asset_path(attrs.get("src", ""), root)
        if path and path.suffix.lower() in {".avif", ".jpeg", ".jpg", ".png", ".webp"}:
            assets.add(path)
    return sorted(assets)


def _output_base(source: Path, root: Path) -> Path:
    """Keep generated files under public/ for legacy root-level source URLs."""

    if source.parent == root:
        public_copy = root / "public" / source.name
        if public_copy.is_file():
            return public_copy
        return root / "public" / source.name
    return source


def _save_variant(source: Path, target: Path, width: int) -> None:
    with Image.open(source) as image:
        source_width, source_height = image.size
        height = max(1, round(source_height * width / source_width))
        resized = image.resize((width, height), Image.Resampling.LANCZOS)
        if target.suffix.lower() in {".jpg", ".jpeg"}:
            if resized.mode not in {"RGB", "L"}:
                resized = resized.convert("RGB")
            resized.save(target, format="JPEG", quality=84, optimize=True, progressive=True)
        elif target.suffix.lower() == ".webp":
            resized.save(target, format="WEBP", quality=82, method=6)
        else:
            resized.save(target)


def generate_variants(root: Path = ROOT, sources=None) -> list[Path]:
    """Create missing non-upscaled variants and return files created."""

    source_paths = _used_assets(root) if sources is None else [Path(path) for path in sources]
    created: list[Path] = []
    seen_targets: set[Path] = set()
    for source in source_paths:
        if not source.is_file():
            continue
        with Image.open(source) as image:
            source_width = image.width
        output_base = _output_base(source, root)
        output_base.parent.mkdir(parents=True, exist_ok=True)
        for width in TARGET_WIDTHS:
            if width >= source_width:
                continue
            target = output_base.with_name(f"{output_base.stem}-{width}{output_base.suffix}")
            if target in seen_targets or target.exists():
                continue
            _save_variant(source, target, width)
            seen_targets.add(target)
            created.append(target)
    return created


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="site root (defaults to the repository root)",
    )
    args = parser.parse_args()
    created = generate_variants(args.root.resolve())
    print(f"Responsive variants: created {len(created)} file(s)")
    for path in created:
        print(f"  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
