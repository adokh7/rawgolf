# Article registry

`articles.json` (repo root) is the single source of truth for every article on
the site: URL, title, excerpt, category, section, date, image and keywords.

## The one rule: edit `articles.json`, never `search.html`

`sync_site.py` **regenerates these files wholesale** from `articles.json`:

| File | Rebuilt from registry |
| --- | --- |
| `news.html` | every article, newest first |
| `guides.html`, `liv-golf.html`, `pga-tour.html`, `tournaments.html` | filtered by `section` |
| `search.html` | the whole `ARTICLES` array |
| `sitemap.xml` | every article + static pages |

Anything you hand-edit in those six files is **destroyed on the next sync**,
silently and with no error. Change the registry and re-run instead.

This is not hypothetical. Commit `485dff9` regenerated `search.html` from a
registry that did not yet carry a `keywords` field, and wiped 63 hand-written
keyword sets in one run. Nothing failed and nothing warned; the loss was only
found later by digging through git history. They were recovered from commit
`de36ddf` — but only because the old file was still in history. Do not rely on
that a second time.

Safe to edit by hand: the article HTML files themselves, `index.html`,
`analysis.html`, `vault.html`, `ratings.html`, and everything under `public/`.

### This table is enforced, not just written down

`sync_site.py --check` asserts the table above against what the script actually
regenerates, derived from `SECTION_PAGE` and friends rather than from prose. It
fails if a generated file is missing from the table, if the table names a file
that is not generated, or if the safe-to-edit list above names a generated one.

So if you extend the script to regenerate another page, `--check` fails until
you add it here. That is deliberate: this document already went stale once and
the silent mismatch is what made the keyword loss possible.

## Workflow when you add an article

1. Write the article HTML as usual. Make sure its `<head>` carries
   `og:title`, `description`, `article:published_time`, `og:image` and a
   self-referencing `rel="canonical"` — the registry reads all of these.
2. Rebuild the registry:

       python3 scripts/build_registry.py

3. Regenerate the grids, search index and sitemap:

       python3 scripts/sync_site.py

4. To fail a build on drift (CI):

       python3 scripts/sync_site.py --check

## Keywords

`keywords` feeds the `k:` field of each `search.html` entry, which is what
makes a query match an article that its title and excerpt do not mention.

No article carries `<meta name="keywords">`, so keywords **cannot be re-derived
from the HTML**. They only exist in the registry. `build_registry.py` therefore
calls `existing_keywords()`, which merges what is already in `articles.json`
with what is already in `search.html` before rebuilding, so a rebuild never
drops them. The registry wins on conflict.

To add or change keywords, edit the `keywords` field in `articles.json` and
re-run `sync_site.py`. Editing `k:` in `search.html` will not survive.

## Categories and sections

`category` is the badge shown on cards: `GUIDES`, `LIV GOLF`, `PGA TOUR`.
It comes from the search index, with a keyword fallback for new articles and
explicit `OVERRIDES` in `build_registry.py` where that tag is wrong.

`section` decides which page owns the article. `PGA TOUR` articles split into:

- **PGA TOUR** -> `pga-tour.html` — tour news, results, players, business
- **TOURNAMENTS** -> `tournaments.html` — majors, championships, courses, venues

This split keeps the two pages from being duplicates of each other. The rule
lives in `MAJOR` in `build_registry.py`.

Swing, drill and instructional articles are pinned to `GUIDES` via `OVERRIDES`
so `PGA TOUR` stays strictly news, bubble updates and results. `analysis.html`
still features the swing collection — it is a curated section, not a category
page, so it is not regenerated and its picks are unaffected by `section`.

## Dates

`date` is ISO `YYYY-MM-DD` in the registry and is also used as card display
text. `sitemap.xml` must carry strict W3C dates, so `write_sitemap()` passes
every value through `iso_date()`, which normalises formats like `AUG 07 2026`
and omits `<lastmod>` entirely rather than emit something invalid. A single
malformed date makes Search Console reject the whole sitemap.

## Gotchas in the HTML

`meta()` in `extract.py` handles attributes in either order and in any quote
style — this repo contains `name="x" content="y"`, `content="y" name="x"`, and
mixed `content='y' name="x"`. A parser that assumes one form silently returns
empty and blanks the field rather than failing, so keep it permissive.
