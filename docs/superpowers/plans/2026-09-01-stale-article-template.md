# Stale Article Template Output Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every article generator replace the shared scaffold’s visible article header reliably, then regenerate and verify the 11 routes that currently expose the Oakmont sample header.

**Architecture:** Keep the existing static HTML publishing model and shared `article-template.html` scaffold. Add one small helper in `scripts/article_header.py` that replaces the actual `<h1>` and `.standfirst` elements and raises if either element is missing. Each affected generator calls that helper with its existing page-specific headline and description before writing its static output.

**Tech Stack:** Python 3, regular expressions, `unittest`, static HTML, existing generator scripts.

**Spec:** User request in the current Codex task: fix only stale article template/output on the 11 identified live URLs, show root cause before editing, verify H1, title, canonical, hero image, Article/NewsArticle data, and article content, and do not deploy or commit.

## Global Constraints

- Change only the stale article-template/output issue; do not address other SEO audit priorities.
- Fix the shared generator behavior, not the 11 pages through unrelated manual edits.
- Preserve each generator’s existing page-specific body, metadata, JSON-LD, canonical, and hero image values.
- Run the failing regression test before implementation, then run the full relevant test suite and the 11-route verification.
- Do not deploy or commit.

---

### Task 1: Add the failing regression coverage

**Files:**
- Modify: `tests/test_template_metadata.py`
- Test fixture input: `article-template.html`
- Test generator: `create_hovland.py`

**Interfaces:**
- Consumes: The current scaffold and the existing Hovland generator.
- Produces: A regression test that fails while the generator still searches for nonexistent legacy header selectors.

- [ ] **Step 1: Add a test for visible header replacement from the scaffold.**

Add a test that copies the scaffold and `create_hovland.py` into a temporary directory, runs the generator, then asserts that the generated file contains the Hovland H1 and description, does not contain the Oakmont H1 or standfirst, and still contains the page-specific body marker and hero image.

```python
    def test_fresh_scaffold_replaces_visible_article_header(self):
        with tempfile.TemporaryDirectory(prefix="article-header-test-") as raw_dir:
            temp = Path(raw_dir)
            shutil.copy2(ROOT / "article-template.html", temp / "article-template.html")
            generator = (ROOT / "create_hovland.py").read_text(encoding="utf-8")
            (temp / "create_hovland.py").write_text(generator, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "create_hovland.py"],
                cwd=temp,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)

            source = (temp / "news-2026-hovland-one-shot-lead-tour-championship.html").read_text(
                encoding="utf-8"
            )
            self.assertIn("Hovland's One-Shot Lead Came From Six Straight Putts", source)
            self.assertIn("Six putts from seven feet or longer built it.", source)
            self.assertNotIn("Oakmont Is Eating the Field Alive", source)
            self.assertNotIn("Average score: 74.8", source)
            self.assertIn("<h2>The Six-Putt Survival Clinic</h2>", source)
            self.assertIn("/public/hovland-one-shot-lead-tour-championship-2026.webp", source)
```

- [ ] **Step 2: Run the new test and confirm the expected failure.**

Run: `python3 -m unittest tests.test_template_metadata.TemplateMetadataTests.test_fresh_scaffold_replaces_visible_article_header -v`

Expected: FAIL because the generated page still contains the Oakmont H1 and standfirst. The failure must be caused by the missing visible header replacement, not by a test import or fixture error.

### Task 2: Implement one shared header replacement helper

**Files:**
- Create: `scripts/article_header.py`
- Modify: `create_hovland.py`, `create_hovland_leads.py`, `create_block.py`, `create_block2.py`, `create_season_recap.py`, `create_money_list.py`, `create_r4.py`, `create_r3.py`, `create_sunday_times.py`, `create_hybrid.py`, `create_tiger.py`

**Interfaces:**
- Consumes: HTML string, page-specific headline, and page-specific standfirst.
- Produces: HTML with exactly one updated visible `<h1>` and one updated `<p class="standfirst">`, or a `ValueError` if the scaffold shape changes.

- [ ] **Step 1: Create the helper with fail-fast replacement behavior.**

Create `scripts/article_header.py` with this interface:

```python
import re


def replace_article_header(html: str, headline: str, standfirst: str) -> str:
    updated, h1_count = re.subn(
        r"<h1(?:\s+[^>]*)?>.*?</h1>",
        f"<h1>{headline}</h1>",
        html,
        count=1,
        flags=re.DOTALL,
    )
    if h1_count != 1:
        raise ValueError(f"expected one article h1, found {h1_count}")

    updated, standfirst_count = re.subn(
        r'<p\s+class=["\']standfirst["\'][^>]*>.*?</p>',
        f'<p class="standfirst">{standfirst}</p>',
        updated,
        count=1,
        flags=re.DOTALL,
    )
    if standfirst_count != 1:
        raise ValueError(f"expected one article standfirst, found {standfirst_count}")
    return updated
```

- [ ] **Step 2: Replace each affected generator’s brittle header substitutions.**

For each generator, import `replace_article_header` and replace its two legacy `re.sub` calls with one call using the existing page-specific strings:

```python
from scripts.article_header import replace_article_header

html = replace_article_header(
    html,
    "Hovland's One-Shot Lead Came From Six Straight Putts",
    description,
)
```

Use the generator’s existing headline and description values for these outputs:

- `create_hovland_leads.py`: `Hovland Leads the Tour Championship by One Into Sunday`
- `create_hovland.py`: `Hovland's One-Shot Lead Came From Six Straight Putts`
- `create_block.py`: `Michael Block's 2-Shot Lead at the Ally Challenge Explained`
- `create_block2.py`: `Michael Block Leads the Ally Challenge Into Sunday by Two`
- `create_season_recap.py`: `PGA Tour Winners 2026: 28 Names, 35 Events, One Left`
- `create_money_list.py`: `Tiger Woods' Career Money List Record May Fall Today`
- `create_r4.py`: `Tour Championship Final Round: Hovland Leads by One`
- `create_r3.py`: `Tour Championship Round 3: Hovland's 65 and Every Score`
- `create_sunday_times.py`: `2026 Tour Championship Sunday Tee Times: Everything Moved`
- `create_hybrid.py`: `Why Pros Are Ditching Hybrids, and Why You Shouldn't`
- `create_tiger.py`: `Every Shot From Tiger Woods' 80th Win: What to Watch For`

- [ ] **Step 3: Run the focused regression test.**

Run: `python3 -m unittest tests.test_template_metadata.TemplateMetadataTests.test_fresh_scaffold_replaces_visible_article_header -v`

Expected: PASS, with the generated Hovland page containing its own H1, standfirst, body, and hero image and no Oakmont header text.

### Task 3: Regenerate the affected static pages

**Files:**
- Modify: `news-2026-hovland-leads-tour-championship-final-day.html`, `news-2026-hovland-one-shot-lead-tour-championship.html`, `news-2026-michael-block-lead-ally-challenge.html`, `news-2026-michael-block-leads-ally-challenge-final-round.html`, `news-2026-pga-tour-winners-2026.html`, `news-2026-tiger-woods-career-money-list-record.html`, `news-2026-tour-championship-final-round-hovland-leads.html`, `news-2026-tour-championship-round-3-tee-times-leaderboard.html`, `news-2026-tour-championship-sunday-tee-times-round-4.html`, `why-pros-are-ditching-hybrids.html`, `news-every-shot-tiger-woods-80th-win-2018.html`
- Run: the 11 corresponding generator scripts listed in Task 2

**Interfaces:**
- Consumes: The corrected scaffold generators.
- Produces: Static pages whose visible header and article body match their existing page-specific metadata and JSON-LD.

- [ ] **Step 1: Run each generator from the repository root.**

Run:

```bash
python3 create_hovland_leads.py
python3 create_hovland.py
python3 create_block.py
python3 create_block2.py
python3 create_season_recap.py
python3 create_money_list.py
python3 create_r4.py
python3 create_r3.py
python3 create_sunday_times.py
python3 create_hybrid.py
python3 create_tiger.py
```

Expected: each command exits with code 0 and writes its existing output file. No deployment or commit is performed.

### Task 4: Verify all 11 required page fields

**Files:**
- Create: `tests/test_stale_article_template_routes.py`
- Verify: the 11 generated HTML files and corresponding live URLs after deployment is outside this task

**Interfaces:**
- Consumes: The 11 generated pages and the exact expected route metadata.
- Produces: A repeatable test that checks visible H1, title, canonical, hero image, Article/NewsArticle JSON-LD, and page-specific body marker for all 11 files.

- [ ] **Step 1: Add expected route data and parser assertions.**

The test must assert for each route that:

```python
assert expected_h1 in source
assert f"<title>{expected_title} | GOLFRAW</title>" in source
assert f'<link rel="canonical" href="https://www.golfraw.com/{slug}">' in source
assert expected_image in source
assert expected_h1 in article_schema["headline"]
assert expected_canonical in str(article_schema["mainEntityOfPage"])
assert body_marker in source
assert "Oakmont Is Eating the Field Alive" not in source
assert "Average score: 74.8" not in source
```

Use the existing JSON-LD parser utilities in `tests/test_template_metadata.py` or extract them into a shared test utility only if the extraction does not change production code.

- [ ] **Step 2: Run the new 11-route regression test.**

Run: `python3 -m unittest tests.test_stale_article_template_routes -v`

Expected: 11 route cases pass with zero Oakmont contamination.

- [ ] **Step 3: Run the existing template metadata suite.**

Run: `python3 -m unittest tests.test_template_metadata -v`

Expected: all existing metadata and contamination tests pass.

- [ ] **Step 4: Run the complete available test suite.**

Run: `python3 -m unittest discover -s tests -p 'test*.py' -v`

Expected: all tests pass. If an unrelated pre-existing test fails, report its exact failure without modifying other SEO areas.

- [ ] **Step 5: Run a final repository diff and contamination check.**

Run:

```bash
git diff --check
rg -l -i 'Oakmont Is Eating the Field Alive|Average score: 74\.8|oakmont-2026-setup-og\.jpg' --glob '*.html' --glob '!article-template.html' --glob '!golfraw.com-audit/**' .
git status --short
```

Expected: no production HTML file is returned by the contamination search. The status lists only the intended helper, 11 generators, tests, and 11 regenerated pages, plus pre-existing user changes that remain untouched.

