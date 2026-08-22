# GolfRaw Premium Tools Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a premium, mobile-first sports analytics visual system across all GolfRaw interactive tools and the shared Locker without changing behavior or content.

**Architecture:** Add one late-loading shared CSS layer that overrides the duplicated incumbent tool styles, then update the shared Locker's injected CSS to the same system. Keep route logic untouched and update generator scripts so the two generated priority pages retain the shared link.

**Tech Stack:** Static HTML5, CSS, vanilla JavaScript, Python generator scripts, Node.js assertion tests, Vercel.

**Spec:** `docs/superpowers/specs/2026-08-22-premium-tools-redesign.md`

## Global Constraints

- Preserve all calculations, JavaScript behavior, storage, URLs, SEO copy, structured data, and editorial language.
- Use `#0F392B` as the primary action color, warm zinc canvas, white cards, 1px zinc borders, 12–20px radii, and soft elevation.
- Keep actionable targets at least 44px where practical, visible focus, safe-area support, and reduced-motion behavior.
- Do not add runtime dependencies.

---

### Task 1: Structural Contract Tests

**Files:**
- Create: `tests/premium-tools-ui.test.js`

**Interfaces:**
- Consumes: the list of root `tools-*.html` pages, generator source, and Locker source.
- Produces: a zero-dependency Node test command that fails until the shared system is wired correctly.

- [ ] Write assertions that every tool page loads `/public/tool-premium.css?v=1` after embedded style blocks.
- [ ] Assert that the stylesheet defines premium tokens, priority route selectors, safe-area sticky actions, focus-visible states, reduced motion, and responsive rules.
- [ ] Assert both generator scripts emit the stylesheet link.
- [ ] Assert the Locker source contains modern border, radius, shadow, and backdrop treatment while retaining dialog/accessibility wiring.
- [ ] Run `node tests/premium-tools-ui.test.js` and verify it fails because the stylesheet is absent.

### Task 2: Shared Premium Tool System

**Files:**
- Create: `public/tool-premium.css`
- Modify: every root `tools-*.html`
- Modify: `scripts/build_tendency_engine.py`
- Modify: `scripts/build_field_reader.py`

**Interfaces:**
- Consumes: existing class names and CSS variables in each tool page.
- Produces: `/public/tool-premium.css?v=1`, loaded last in each tool `<head>`.

- [ ] Define scoped color, radius, shadow, spacing, focus, and motion tokens.
- [ ] Restyle the shared page shell, hero, panels, forms, buttons, tables, result cards, explainers, FAQs, ads, and footers.
- [ ] Add route-specific refinements for `.te-*` and `.fr-*` controls without changing markup or event behavior.
- [ ] Add mobile safe-area sticky treatment for the Tendency Engine action region and representative shared action bars.
- [ ] Insert the stylesheet link in every interactive tool and both generator templates.
- [ ] Run `node tests/premium-tools-ui.test.js` and verify the shared-system assertions pass.

### Task 3: Premium Locker Sheet

**Files:**
- Modify: `lib/locker/drawer.js`

**Interfaces:**
- Consumes: existing `GolfrawLocker` API and existing `gr-lk-*` markup.
- Produces: the same `window.GolfrawDrawer` behavior with redesigned injected CSS.

- [ ] Replace hard 2–3px borders and square surfaces with 1px lines, 14–20px radii, and soft shadows.
- [ ] Turn the launcher into a blurred tournament-green pill and the panel into an elevated responsive sheet.
- [ ] Preserve focus trap, Escape behavior, focus return, 44px targets, live regions, and safe areas.
- [ ] Run `node --check lib/locker/drawer.js` and `node tests/premium-tools-ui.test.js`.

### Task 4: Local Functional and Responsive Verification

**Files:**
- Create or update only test evidence under `.impeccable/review/`.

**Interfaces:**
- Consumes: the completed static site.
- Produces: validated mobile and desktop screenshots plus interaction evidence.

- [ ] Run Python syntax checks for both generator scripts and regenerate priority pages in a clean diff check.
- [ ] Start a local static server and inspect 375px and 1440px renders for Tendency Engine, Field Reader, a representative shared tool, and the Locker.
- [ ] Exercise hole progress and option selection, Field Reader sliders and picks, and Locker open/close controls.
- [ ] Batch-fix material visual or responsive defects and capture one confirmation round.
- [ ] Run the Impeccable detector once on changed UI targets and resolve mechanical findings.

### Task 5: Documentation, Commit, Push, and Production Deploy

**Files:**
- Create: `DESIGN.md`
- Update: plan checkboxes as execution evidence.

**Interfaces:**
- Consumes: verified build, screenshots, detector output, and direction contract.
- Produces: committed source on GitHub and a verified Vercel production deployment.

- [ ] Record the shipped design system in `DESIGN.md` from the implemented result.
- [ ] Run fresh full verification: structural test, JS checks, Python checks, HTML link audit, and local HTTP smoke test.
- [ ] Review `git diff` for unintended copy, logic, SEO, or data changes.
- [ ] Commit with a scoped redesign message and push the current branch to `origin`.
- [ ] Deploy with Vercel production tooling and verify the production URLs return successful responses.
