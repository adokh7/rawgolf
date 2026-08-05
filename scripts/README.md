# Article registry

`articles.json` (repo root) is the single source of truth for every article on
the site: URL, title, excerpt, category, section, date and image.

## Workflow when you add an article

1. Write the article HTML as usual. Make sure its `<head>` carries
   `og:title`, `description`, `article:published_time`, `og:image` and a
   self-referencing `rel="canonical"` — the registry reads all of these.
2. Rebuild the registry:

       python3 scripts/build_registry.py

3. Check the rest of the site agrees, and regenerate the sitemap:

       python3 scripts/sync_site.py

   It reports anything missing from `news.html`, the section page or
   `search.html`, plus broken images. Add those cards, then re-run.

4. To fail a build on drift (CI):

       python3 scripts/sync_site.py --check

## Categories and sections

`category` is the badge shown on cards: `GUIDES`, `LIV GOLF`, `PGA TOUR`.
It comes from the live search index, with a keyword fallback for new articles.

`section` decides which page owns the article. `PGA TOUR` articles split into:

- **PGA TOUR** -> `pga-tour.html` — tour news, results, players, business
- **TOURNAMENTS** -> `tournaments.html` — majors, championships, courses, venues

This split keeps the two pages from being duplicates of each other. The rule
lives in `MAJOR` in `build_registry.py`.

## Why grids are checked, not regenerated

`sync_site.py` deliberately does **not** rewrite the grids or `search.html`.
Those carry hand-curated ordering, hero blocks, "New" badges and per-entry
search keywords that a generator would flatten. Only `sitemap.xml` is fully
generated, because it has no hand-authored content.
