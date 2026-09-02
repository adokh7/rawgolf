# SEO Metadata Quality Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the site one explicit, reusable source for approved SEO title and meta-description overrides, apply it to the current outliers, and prevent social metadata drift without changing visible content, URLs, canonicals, schema, links, sitemaps, or Core Web Vitals.

**Architecture:** Store only deliberate metadata exceptions in `scripts/seo_metadata.py`, keyed by canonical route. The shared HTML finalizers and `sync_site.py` will apply those values to `<title>`, description, Open Graph, and Twitter tags while leaving all other page fields unchanged. Regression tests will scan canonical indexable output for missing/duplicate metadata, outlier values, canonical changes, and redirected-route reintroduction.

**Tech Stack:** Python 3 standard library, static HTML, JSON registry, `unittest`.

**Spec:** `/Users/adnan/.codex/attachments/5f01e67c-b2fe-4ff2-94de-0845377e3991/pasted-text.txt`

## Global Constraints

- Rewrite only metadata that genuinely needs improvement; length is a screening signal, not the goal.
- Preserve factual accuracy, article intent, visible H1s, article content, URLs, canonicals, schema identity, links, sitemaps, and Task 1–6 behavior.
- Do not mechanically truncate strong titles or descriptions.
- Do not invent facts, dates, entities, or promises.
- Do not commit, push, deploy, or modify unrelated SEO systems.

---

### Task 1: Add the shared SEO metadata override source

**Files:**
- Create: `scripts/seo_metadata.py`
- Test: `tests/test_seo_metadata.py`

**Interfaces:**
- Produces `metadata_override_for(path: str | Path) -> dict[str, str]`.
- Produces `apply_metadata_overrides(source: str, path: str | Path) -> str`.
- Produces `audit_metadata(source: str) -> dict[str, object]` for title, description, canonical, and social-tag counts.

- [ ] **Step 1: Write failing regression tests**

  Add tests asserting that the 38 audited title routes receive their approved title values, the four description routes receive their approved description values, both pro-am pages have distinct titles, and an unlisted page is unchanged. Assert that applying an override updates exactly the title/description social mirrors while preserving its canonical and body.

- [ ] **Step 2: Run the focused tests and verify the expected failure**

  Run `python3 -m unittest tests.test_seo_metadata`.

  Expected result: failure because `scripts.seo_metadata` does not yet exist.

- [ ] **Step 3: Implement the override source and attribute-only transformer**

  Add route-keyed values for the 38 title outliers and the duplicate pro-am title correction. Use concise factual titles, omit the brand suffix where it consumes space without adding meaning, and shorten only the five cores that remain over 60 characters. Add descriptions only for the four descriptions over 160 characters. The transformer must require at most one matching tag per managed field, replace `<title>`, `description`, `og:title`, `og:description`, `twitter:title`, and `twitter:description`, and leave canonicals, H1s, JSON-LD, images, and article text untouched.

- [ ] **Step 4: Run the focused tests and verify they pass**

  Run `python3 -m unittest tests.test_seo_metadata`.

  Expected result: all new tests pass.

---

### Task 2: Connect the shared source to metadata finalization and synchronization

**Files:**
- Modify: `scripts/fix_seo_audit.py`
- Modify: `scripts/article_header.py`
- Modify: `scripts/sync_site.py`
- Test: `tests/test_seo_metadata.py`

**Interfaces:**
- `fix_seo_audit.repair_source` uses the route override before emitting the managed head block.
- `article_header.finalize_article_template_metadata` applies the shared override after its existing schema/image normalization.
- `sync_site.py` exposes a metadata normalization pass that changes only routes listed in `scripts/seo_metadata.py` and validates the resulting social mirrors.

- [ ] **Step 1: Extend the failing tests for integration**

  Add tests that call the finalizer on a representative scaffold-generated article and verify the override survives finalization. Add a synchronization test using a temporary copy of an affected HTML page and assert that only the six managed title/description fields change.

- [ ] **Step 2: Run the integration tests and verify failure**

  Run `python3 -m unittest tests.test_seo_metadata`.

  Expected result: the direct override tests pass, while integration assertions fail because the existing finalizers do not call the new shared layer.

- [ ] **Step 3: Add the shared layer calls**

  Import the new functions without changing canonical, image, schema, or content code paths. Run the sync metadata pass after generated HTML exists and before final validation. Make `--check` report metadata override drift rather than rewriting files.

- [ ] **Step 4: Run the integration tests and verify pass**

  Run `python3 -m unittest tests.test_seo_metadata` and `python3 scripts/sync_site.py --check`.

  Expected result: both commands exit successfully.

---

### Task 3: Apply only approved metadata changes to current output

**Files:**
- Modify: the 38 affected article HTML files identified by the audit
- Modify: the 4 affected article HTML files with long descriptions
- Modify: the two pro-am article HTML files with duplicate titles

- [ ] **Step 1: Run the shared metadata generator against the explicit override routes**

  Use the new shared transformer to update only pages with entries in `scripts/seo_metadata.py`; do not run the broad legacy repair over every root HTML file.

- [ ] **Step 2: Verify the generated diff is metadata-only**

  Compare each changed page before and after and assert that only `<title>`, the description meta tag, and their Open Graph/Twitter mirrors changed. Confirm H1, canonical, JSON-LD, hero image, and article body are byte-for-byte unchanged.

- [ ] **Step 3: Run the page-level metadata audit**

  Scan `sitemap_page_records()` and report exact after counts for title/description length, missing values, duplicates, and intent alignment. Review the homepage, `/news`, `/analysis`, `/ratings`, `/full-board`, ten recent articles, five evergreen guides, and five tool/data pages.

---

### Task 4: Run regression and full validation

**Files:**
- Test: `tests/test_seo_metadata.py`
- Test: existing metadata, route, schema, image, sitemap, and template tests

- [ ] **Step 1: Run focused SEO metadata tests**

  Run `python3 -m unittest tests.test_seo_metadata tests.test_onpage_seo tests.test_article_schema`.

- [ ] **Step 2: Verify protected contracts**

  Confirm all canonicals and JSON-LD article identities remain unchanged, the two Task 6B redirect sources remain absent from internal hrefs and sitemap locations, and no H1 or article body changes occurred.

- [ ] **Step 3: Run the full test suite**

  Run `python3 -m unittest discover -s tests` and report any failures that predate or fall outside Task 7 without changing unrelated systems.

- [ ] **Step 4: Run final diff and status checks**

  Run `git diff --check`, `git diff --stat`, and `git status --short --branch`. Confirm no commit, push, or deployment occurred.

---
