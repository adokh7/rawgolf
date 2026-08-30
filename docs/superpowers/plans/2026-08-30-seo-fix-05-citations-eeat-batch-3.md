# Task 5 Batch 3 Citation Implementation Plan

> **For agentic workers:** Use the test-first and verification workflows for each step. Do not commit this plan or any implementation from this task.

**Goal:** Add only verified, claim-specific outbound citations to five GolfRaw pages while preserving their metadata, structure, content, and prior SEO fixes.

**Architecture:** Treat the five checked-in article HTML files as the deployable content source. Add a focused regression test that parses those files and verifies exact HTTPS citation hrefs, unchanged canonical/title/H1/description metadata, and indexability. Validate the same links through a restricted localhost served fixture.

**Tech Stack:** Static HTML, Python `unittest`, `html.parser`, `pathlib`, local HTTP server.

**Spec:** User request for TASK 5 — BATCH 3: VERIFIED CITATION / E-E-A-T IMPLEMENTATION.

## Global Constraints

- Modify only the five Batch 3 article pages and `tests/test_citation_batch_3.py` plus this process-only plan.
- Preserve Tasks 1–5 Batch 1 and Batch 2 fixes.
- Use claim-specific HTTPS sources; never invent URLs or use generic homepages.
- Do not change article intent, metadata, canonical, schema, sitemap, layout, CSS, JavaScript, images, or unrelated internal links.
- Do not commit, push, merge, or deploy.

### Task 1: Audit and verify Batch 3 sources

**Files:** Read the five target HTML files and `articles.json`; create no implementation changes.

- [ ] Identify every material factual claim on each target page.
- [ ] Classify existing sourcing and identify only claims needing citations.
- [ ] Open each selected source and confirm it directly supports the nearby claim.
- [ ] Treat Jessica Bang claims conservatively and leave unverifiable claims uncited.

### Task 2: Write the failing regression test

**Files:** Create `tests/test_citation_batch_3.py`.

- [ ] Assert all five target files exist.
- [ ] Assert the selected exact external HTTPS hrefs are present as real anchors.
- [ ] Reject placeholders, `example.com`, `javascript:`, malformed, and generic-homepage hrefs.
- [ ] Compare title, H1, description, and canonical values to `HEAD`.
- [ ] Assert target pages remain indexable.
- [ ] Run the test before page edits and confirm it fails because citations are absent.

### Task 3: Add minimal verified citations

**Files:** Modify only the five target article HTML files.

- [ ] Add each verified citation beside the claim it supports using descriptive anchor text.
- [ ] Update existing Sources sections only with sources actually used in the article.
- [ ] Make no prose change unless a source requires a necessary factual qualification.

### Task 4: Verify generated/served HTML and regressions

**Files:** No additional application files.

- [ ] Serve a restricted fixture containing the five final HTML files and verify HTTP 200 plus every intended href.
- [ ] Run Task 1–5 regression tests, schema tests, `sync_site.py --check`, Python compilation, and `git diff --check`.
- [ ] Confirm article bodies, metadata, canonicals, sitemap behavior, and prior template/route fixes remain intact.
- [ ] Review the final diff and report all remaining unsupported claims and risks without committing.
