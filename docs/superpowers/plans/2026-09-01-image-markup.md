# Image Markup and Responsive Delivery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give every local raster image in deployable HTML accurate intrinsic dimensions and safe responsive candidates while preserving the current visual treatment and loading priority.

**Architecture:** A shared build-time image utility will resolve local assets, read their real dimensions, discover only existing variant files, and normalize `<img>` attributes without changing article content or CSS. `sync_site.py` and both existing article finalizers will use the utility for future output; a one-time repository normalizer will repair current static HTML through the same code path. Missing 400/800 variants will be generated only for local raster bases that can be resized without upscaling or cropping.

**Tech Stack:** Python 3, `html.parser`, Pillow for build-time raster metadata/resizing, pytest, static HTML/Vercel output.

**Spec:** User request in the current task: “TASK 3 ONLY — Fix image dimensions, responsive image delivery, and CLS risk.”

## Global Constraints

- Do not modify article content, structured-data URLs, schema semantics, navigation, titles, sitemaps, or unrelated SEO issues.
- Do not modify SVGs, icons, logos, tracking pixels, third-party embeds, or remote images.
- Derive `width` and `height` from actual source assets; never use display-size placeholders as intrinsic dimensions.
- Preserve `width:100%; height:auto`, existing card cropping, and existing CSS/layout.
- Emit `srcset` and `sizes` only for real local candidates; never invent nonexistent variants or upscale a source asset.
- Article lead/LCP images remain eager/high priority; cards and below-fold secondary images remain lazy; do not add broad preloads.
- Do not deploy or commit.

---

### Task 1: Lock the image rules with regression tests

**Files:**
- Create: `tests/test_image_markup.py`
- Test fixtures: existing files under `public/` and current representative HTML pages

**Interfaces:**
- The tests will define the required public interfaces `image_dimensions(src, root)`, `responsive_candidates(src, root)`, `normalize_image_markup(source, page_path, root)`, and `normalize_site(root)` before implementation.

- [ ] **Step 1: Write failing tests**

  Add tests that:

  - read a known WebP and assert its real dimensions are returned;
  - assert `responsive_candidates()` returns only existing `-400`/`-800` files and uses their actual pixel widths;
  - normalize a card image and assert exact intrinsic dimensions, `srcset`, card `sizes`, and `loading="lazy"`;
  - normalize an article lead image and assert exact intrinsic dimensions, `srcset`, `sizes`, `loading="eager"`, and `fetchpriority="high"`;
  - normalize a secondary article image and assert dimensions, `srcset`, `sizes`, and `loading="lazy"`;
  - assert a remote/SVG image is unchanged;
  - assert the production scan has no local-raster image missing either dimension and no eligible local-raster image missing `srcset` after the output repair;
  - assert all `srcset` candidates exist and their `w` descriptors match the candidate file width;
  - assert the homepage has 21 images, all with dimensions, with cards lazy and no card preload.

- [ ] **Step 2: Run the focused tests and verify the red state**

  Run:

  ```bash
  pytest -q tests/test_image_markup.py
  ```

  Expected: failures because the shared utility does not yet exist and current output still contains the audited omissions.

### Task 2: Implement the shared image metadata and markup utility

**Files:**
- Create: `scripts/image_markup.py`
- Test: `tests/test_image_markup.py`

**Interfaces:**
- `image_dimensions(src: str, root: Path) -> tuple[int, int] | None`
- `responsive_candidates(src: str, root: Path) -> list[tuple[str, int]]`
- `normalize_image_markup(source: str, page_path: Path, root: Path) -> str`
- `normalize_site(root: Path) -> tuple[int, int]` returning `(files_changed, images_changed)`

- [ ] **Step 1: Implement local asset resolution and real dimensions**

  Resolve `/public/...`, root-level asset URLs, and relative `public/...` paths against `root`. Restrict processing to raster suffixes (`.webp`, `.jpg`, `.jpeg`, `.png`, `.avif`). Use Pillow only at build/test time, return `None` for missing, remote, data, SVG, or unsupported assets, and never mutate those tags.

- [ ] **Step 2: Implement exact variant discovery**

  Discover same-stem `-400`, `-800`, and `-1200` files in the source directory, plus the existing `/public` equivalent for legacy root-level duplicates. Include only files that exist and whose actual width matches the descriptor. Return URL/width pairs in ascending order.

- [ ] **Step 3: Implement context-aware, idempotent markup normalization**

  Parse tag positions and ancestor classes without reserializing whole HTML documents. For each local raster `<img>`:

  - replace or add actual `width` and `height`;
  - replace/add `srcset` only when candidates exist;
  - add the appropriate `sizes` (`(max-width: 700px) 92vw, 360px` for cards; `(max-width: 700px) 100vw, 740px` for article media; the existing manifesto display size for the brand asset);
  - identify `.news-grid`, `.guide-grid`, `.guide-card`, `.news`, and related-card images as lazy cards;
  - identify the first non-card article image, `.lead-img`, or current high-priority image as the lead/LCP image and enforce eager/high priority;
  - mark later article media lazy;
  - preserve all other attributes, styles, URLs, alt text, and content;
  - skip SVGs, icons/logos, remote images, tracking pixels, and missing assets;
  - be idempotent on a second pass.

- [ ] **Step 4: Run focused tests**

  Run `pytest -q tests/test_image_markup.py` and expect all tests to pass for the utility behavior.

### Task 3: Wire the utility into future generators and card templates

**Files:**
- Modify: `scripts/sync_site.py:119-161` and its main validation path
- Modify: `scripts/fix_template_metadata.py:559-566`
- Modify: `scripts/article_header.py:82-129`
- Test: `tests/test_image_markup.py`

**Interfaces:**
- `news_card()` and `guide_card()` will call the shared utility’s attribute builder or emit markup that normalizes through `normalize_image_markup()`.
- `finalize_html()` and `finalize_article_template_metadata()` will return image-normalized source as their final step.

- [ ] **Step 1: Update `sync_site.py` card output**

  Replace the omitted dimensions in `news_card()` and the hard-coded `1672x941` in `guide_card()` with real asset dimensions and existing/generated responsive candidates. Keep card CSS, `loading="lazy"`, and `decoding="async"` unchanged.

- [ ] **Step 2: Update both article finalizers**

  Run `normalize_image_markup()` after metadata/schema work has completed so all scaffold-based generators receive the same hero/body behavior without touching schema URLs or article text.

- [ ] **Step 3: Add image validation to the generator check path**

  Make `sync_site.py --check` fail for a local raster `<img>` with missing dimensions, an invalid candidate, or a missing `srcset` when a real candidate exists. Keep explicit exceptions only for skipped non-raster/remote assets.

- [ ] **Step 4: Run generator and focused regression tests**

  Run:

  ```bash
  pytest -q tests/test_image_markup.py tests/test_template_metadata.py
  python3 scripts/sync_site.py --check
  ```

### Task 4: Generate missing safe variants and repair current static output

**Files:**
- Create: `scripts/generate_image_variants.py`
- Modify: current deployable HTML files through `scripts/image_markup.py` (generated output)
- Add: generated `public/*-400.webp`, `public/*-800.webp`, or same-format JPEG variants only where the source is wide enough
- Test: `tests/test_image_markup.py`

**Interfaces:**
- `generate_variants(root: Path, sources: Iterable[str]) -> list[Path]`
- CLI: `python3 scripts/generate_image_variants.py`

- [ ] **Step 1: Add the safe variant generator**

  Resize with Pillow while preserving the source aspect ratio, never crop, never upscale, and emit only widths no larger than the original. Preserve JPEG format for JPEG bases; emit WebP for WebP bases. Do not process SVGs, icons, logos, remote assets, or unrelated files.

- [ ] **Step 2: Generate variants for all used local raster bases without usable variants**

  Derive the source set from deployable/indexable HTML, not a broad public-directory glob. This includes the existing portrait manifesto asset because it is a local raster `<img>` and can safely use a 400px candidate; no content changes are made.

- [ ] **Step 3: Normalize all current deployable HTML**

  Run the shared site normalizer once. It must update only `<img>` attributes and leave article text, JSON-LD, CSS, canonical URLs, and image `src`/schema URLs unchanged.

- [ ] **Step 4: Verify idempotence and diff scope**

  Run the normalizer a second time and assert zero additional changes. Review the diff summary to ensure only image attributes and generated variant files changed.

### Task 5: Full validation and handoff

**Files:**
- Test: `tests/test_image_markup.py` and existing test suite

- [ ] **Step 1: Re-scan counts**

  Report before/after image totals, missing dimensions, missing responsive candidates, homepage counts, and remaining deliberate exceptions.

- [ ] **Step 2: Verify representative pages**

  Verify `/`, `/news`, `/guides`, `/pga-tour`, `/tournaments`, `/analysis`, `/vault`, representative article pages with one hero, multi-image article pages, representative tool pages, and both nested article routes. Confirm local URLs resolve to files, ratios match source assets, and schema image URLs remain unchanged and valid.

- [ ] **Step 3: Run all regression and full tests**

  Run:

  ```bash
  pytest -q
  python3 scripts/sync_site.py --check
  ```

  If a pre-existing unrelated test fails, record the exact failure without changing unrelated SEO behavior.

- [ ] **Step 4: Final review**

  Confirm no deploy or commit occurred. Report files changed, URLs/pages verified, LCP loading changes, tests passed, remaining exceptions, and any limitation that still requires a future image/CDN pipeline.
