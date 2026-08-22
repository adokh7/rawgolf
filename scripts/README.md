# Article registry

`articles.json` (repo root) is the single source of truth for every article on
the site: URL, title, excerpt, category, section, date, image and keywords.

## The one rule: edit `articles.json`, never `search.html`

`sync_site.py` **regenerates these files wholesale or in marked sections** from
`articles.json`:

| File | Rebuilt from registry |
| --- | --- |
| `index.html` | marked 15-story homepage feed; newest first with priority crawl targets |
| `news.html` | every article, newest first |
| `guides.html`, `liv-golf.html`, `pga-tour.html`, `tournaments.html` | filtered by `section` |
| `search.html` | the whole `ARTICLES` array |
| `sitemap.xml` | every article + static pages |
| `feed.xml` | newest 40 articles, with WebSub hub links |

Anything you hand-edit in a generated file (or the marked homepage feed) is
**destroyed on the next sync**, silently and with no error. Change the registry
and re-run instead.

This is not hypothetical. Commit `485dff9` regenerated `search.html` from a
registry that did not yet carry a `keywords` field, and wiped 63 hand-written
keyword sets in one run. Nothing failed and nothing warned; the loss was only
found later by digging through git history. They were recovered from commit
`de36ddf` — but only because the old file was still in history. Do not rely on
that a second time.

Safe to edit by hand: the article HTML files themselves, the non-generated
homepage regions, `analysis.html`, `vault.html`, `ratings.html`, and everything
under `public/`.

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


## Fast indexing (WebSub + IndexNow)

Google retired its sitemap-ping endpoint, so new articles are pushed rather
than waited on. Two channels, because neither reaches everyone:

- **WebSub** — `scripts/fast_index.py --websub` POSTs `hub.mode=publish` to
  both hubs, which then fetch `feed.xml` and fan it out. Google subscribes to
  `pubsubhubbub.appspot.com`. A hub only accepts the ping because `feed.xml`
  advertises it via `<atom:link rel="hub">`; strip those and pings start
  failing silently.
- **IndexNow** — `scripts/fast_index.py --indexnow <urls>` submits changed
  URLs to Bing, Yandex, Seznam and Naver. **Google does not use IndexNow.**
  Ownership is proved by `<key>.txt` at the site root, which must stay
  deployed or every submission 403s.

### Ordering matters

`sync_site.py` does **not** fire the ping. Sync runs before the deploy, so a
ping at that moment makes the hub fetch the *old* live feed and find nothing
new. Sync records the changed URLs and prints the command instead:

    python3 scripts/sync_site.py     # writes feed.xml, queues changed URLs
    git push                          # deploy
    python3 scripts/fast_index.py     # NOW ping — the feed is live

Pass `--notify` or set `FAST_INDEX=1` to fire inline anyway. Failures never
break a sync; indexing is best-effort by design.

# The Locker (`lib/locker/`)

Local-first storage shared by the tool pages. Everything stays in the reader's
browser; nothing here ever touches the network.

| File | Role |
| --- | --- |
| `lib/locker/schema.js` | structural validator (`window.GolfrawSchema`) |
| `lib/locker/store.js` | IndexedDB + public API (`window.GolfrawLocker`) |
| `lib/locker/drawer.js` | the My Bag / Locker slide-out (`window.GolfrawDrawer`) |

## Why hand-written instead of Dexie + Zod

This site has no bundler, no `package.json` and no npm runtime — every page is
static HTML with inline scripts. Adding Dexie and Zod means adding a build step
in front of 283 pages. The parts we actually need (a promise API over IndexedDB,
store versioning, and safeParse-style validation that never throws) are small
enough to own outright, so they are written directly against the platform. The
API is deliberately shaped like the libraries it replaces, so swapping either in
later is mechanical.

`node_modules/` in the repo root is unrelated — it is left over from the Google
Indexing API work and is gitignored.

## Data model

`profile` (one record) · `bags` · `rounds` · `toolState` · `meta`

Every write is schema-validated first, so invalid data never reaches disk. Bad
records are rejected individually: one out-of-range yardage costs the reader
that club, not the other thirteen.

## Wiring it into a page

`scripts/wire_locker.py` injects the loader — and, for the three connected
tools, a bridge — into every `tools-*.html` between `<!-- LOCKER:START -->` and
`<!-- LOCKER:END -->`. It is idempotent: it replaces the managed block rather
than appending, so re-running it is always safe.

    python3 scripts/wire_locker.py

Connected tools: `tools-bag-audit` (#07, clubs), `tools-plays-like` (#05,
conditions) and `tools-handicap-detector` (#04, rounds + claimed handicap). The
other six tool pages get the drawer and the storage layer but no bridge.

### Bump `VER` when you edit `lib/locker/`

`vercel.json` serves `.js` with a one-year `immutable` Cache-Control. The
`?v=` query string on each `<script src>` is the only cache-buster, so a change
under `lib/locker/` that does not bump `VER` in `wire_locker.py` reaches nobody
who has already visited. Bump it, re-run the script, and commit both.

### Tools keep their own `localStorage` writes

Each bridge sits *alongside* the tool's existing `persist()`/`restore()` rather
than replacing it. Legacy keys are migrated into IndexedDB once (guarded by a
`meta` flag) and then left in place, so a reader still holding a cached copy of
an older page does not lose their bag. Do not delete those code paths.
