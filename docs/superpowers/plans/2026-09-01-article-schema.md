# Article Schema Completeness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Normalize the shared Article/NewsArticle JSON-LD output so every eligible indexable editorial page has one valid, canonical, metadata-derived article entity.

**Architecture:** Add a focused schema normalizer that parses page-owned JSON-LD, derives values from canonical/meta/registry/byline sources, preserves existing non-article JSON-LD, removes duplicate article entities, and emits one consistent article node. Call it from both existing article finalization paths and provide a repository-wide repair/validation command for legacy direct-generator output.

**Tech Stack:** Python 3 standard library, `html.parser`, JSON-LD, `unittest`, static HTML generators.

**Spec:** User request “TASK 4 ONLY — Fix Article / NewsArticle structured data completeness and consistency.”

## Global Constraints

- Do not invent authors, dates, images, or editorial facts.
- Do not change visible article content or Task 3 image optimization behavior.
- Use absolute public GolfRaw URLs for canonical, `mainEntityOfPage`, and schema images.
- Preserve non-article JSON-LD and the existing publisher logo configuration.
- Do not deploy or commit.

---

### Task 1: Add failing shared-schema regression tests

**Files:**
- Modify: `tests/test_article_schema.py`
- Test fixtures: existing production HTML and `articles.json`

**Interfaces:**
- Consumes: current JSON-LD parser and production article inventory.
- Produces: failing checks for one article entity per eligible page, required fields, canonical identity, valid authors/images/dates, and publisher consistency.

- [ ] **Step 1: Write the failing test**

Add inventory-level tests that parse every self-canonical article/news page and assert exactly one Article/NewsArticle entity, required fields, valid JSON-LD, `mainEntityOfPage` equal to canonical, schema image equal to the page’s authoritative `og:image`, and author values equal to a page byline/meta source. Add focused tests for duplicate Hovland output, missing Hovland `mainEntityOfPage`, and the five pages with no authoritative `dateModified` so those pages are explicitly reported rather than assigned a fabricated date.

- [ ] **Step 2: Run test to verify it fails**

Run `python3 -m unittest tests.test_article_schema -v`.

Expected: failure against the current duplicate entities, missing `mainEntityOfPage`, missing author/image/dateModified fields, and inconsistent publisher/URL values.

---

### Task 2: Implement the shared article-schema normalizer

**Files:**
- Create: `scripts/article_schema.py`
- Modify: `scripts/fix_template_metadata.py`
- Modify: `scripts/article_header.py`

**Interfaces:**
- Consumes: page HTML, canonical/meta tags, `articles.json`, existing JSON-LD documents, and existing body/OG image metadata.
- Produces: `normalize_article_schema(source: str, path: Path) -> str`, `audit_article_schema(source: str, path: Path) -> dict`, and one normalized Article/NewsArticle entity while preserving unrelated JSON-LD.

- [ ] **Step 1: Implement source resolution**

Resolve canonical from the page canonical link and registry fallback; resolve the primary image from `og:image` and validate it as a GolfRaw/public URL; resolve publication date from existing article metadata or registry date; resolve modification date only from an existing explicit modification source; resolve author from `article:author`, `meta[name=author]`, existing author JSON-LD, or an explicit `GOLFRAW Editorial` byline, otherwise return an unresolved-data diagnostic.

- [ ] **Step 2: Implement entity normalization**

Keep the original Article/NewsArticle type, set headline from the page’s authoritative article metadata, set canonical `@id` and `mainEntityOfPage`, normalize image to an absolute primary-image URL without changing `<img>` markup, preserve truthful dates, normalize author references to the existing editorial identity or real person metadata, and normalize publisher to the existing GolfRaw organization identity with its current logo.

- [ ] **Step 3: Deduplicate article entities**

Retain non-article nodes in every JSON-LD document, retain one article node for the page, and remove duplicate Article/NewsArticle nodes or duplicate article-only scripts. Fail with a diagnostic when an article page has no usable article entity or conflicting irreconcilable source metadata.

- [ ] **Step 4: Wire both finalizers**

Call `normalize_article_schema` from `finalize_html` after head metadata rewriting and from `finalize_article_template_metadata` before image normalization. The schema pass must not alter visible body content or image delivery attributes.

- [ ] **Step 5: Run focused tests**

Run `python3 -m unittest tests.test_article_schema tests.test_template_metadata -v`.

Expected: the new schema regression tests pass and existing template/schema tests remain green.

---

### Task 3: Repair current legacy direct-generator output through the shared command

**Files:**
- Create: `scripts/normalize_article_schema.py`
- Modify: eligible generated article HTML files through the command’s controlled output pass
- Modify: `tests/test_article_schema.py` for command/diagnostic coverage

**Interfaces:**
- Consumes: production HTML discovered using the same indexability rules as `scripts/sync_site.py`.
- Produces: normalized current HTML, a `--check` audit, and explicit unresolved-data output.

- [ ] **Step 1: Add check/apply CLI**

Implement `python3 scripts/normalize_article_schema.py --check` as read-only validation and `--apply` as an in-place repair of eligible indexable article pages. Exclude templates, redirects, non-indexable pages, tools, and unrelated JSON-LD-only pages.

- [ ] **Step 2: Run the repair**

Run `python3 scripts/normalize_article_schema.py --apply` from the repository root. The command must report changed pages, duplicate entities removed, and unresolved fields without modifying visible article content.

- [ ] **Step 3: Run the check**

Run `python3 scripts/normalize_article_schema.py --check` and verify zero malformed JSON-LD, duplicate article entities, missing required fields where source data exists, and URL/image mismatches. Record any intentionally unresolved author or date data.

---

### Task 4: Full validation and regression review

**Files:**
- No additional production files unless a test exposes a source-resolution defect.

**Interfaces:**
- Consumes: normalized production pages and shared normalizer audit output.
- Produces: evidence for all required Task 4 validation checks.

- [ ] **Step 1: Parse every eligible JSON-LD block**

Run the complete article inventory parser and verify valid JSON, exactly one Article/NewsArticle entity per eligible page, canonical equality, valid ISO dates, truthful authors, consistent publisher, and image-to-`og:image` correspondence.

- [ ] **Step 2: Run relevant tests**

Run `python3 -m unittest tests.test_article_schema tests.test_template_metadata tests.test_onpage_seo tests.test_legacy_route_references -v`.

- [ ] **Step 3: Run the full suite**

Run `python3 -m unittest discover -s tests -p 'test_*.py'` and report the exact result.

- [ ] **Step 4: Inspect the diff scope**

Run `git status --short` and `git diff --stat`; confirm no deploy or commit occurred and no Task 3 image markup/source files were changed by the schema pass.
