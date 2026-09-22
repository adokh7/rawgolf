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
| `guides.html`, `liv-golf.html`, `lpga-tour.html`, `pga-tour.html`, `players.html`, `tournaments.html`, `vintage-golf-history.html` | filtered by `section` |
| `search.html` | the whole `ARTICLES` array |
| `sitemap.xml` | every deployable, indexable, self-canonical HTML page |
| `news-sitemap.xml` | only indexable news-section articles published in the last two days |
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

4. If a new local raster image was added, generate its safe responsive
   variants before syncing:

       python3 scripts/generate_image_variants.py

   The generator preserves the source aspect ratio, never upscales or crops,
   and only creates widths that are missing and smaller than the source. The
   sync then writes the source dimensions, `srcset`, `sizes`, and loading
   priority into every deployable image tag.

5. To fail a build on drift (CI):

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
text. Standard sitemap `<lastmod>` values come only from each page's own
`article:modified_time` or JSON-LD `dateModified`. The generator emits no
`<lastmod>` when the page has no reliable modification date or when its
metadata sources disagree. It never uses today's date, filesystem mtime, or a
registry date that could have drifted from the page.

`news-sitemap.xml` is a separate Google News sitemap. It uses the page's
authoritative `article:published_time`/JSON-LD `datePublished` for the
publication timestamp and keeps only indexable articles in the news sections
from the last two days. Run `python3 scripts/generate_sitemaps.py` to rebuild
both sitemap files without rebuilding the content grids.

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

`profile` (one record) · `bags` · `rounds` · `toolState` · `sessions` · `scorecards` · `meta`

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


# The Standing Order (`tools-standing-order.html`)

Tool 10, the range-session gapping logger. The page is **generated**, not
hand-written:

    python3 scripts/build_standing_order.py
    python3 scripts/wire_locker.py

`build_standing_order.py` lifts the head (fonts, design tokens, shared CSS),
the site header and the footer verbatim out of `tools-bag-audit.html`, so the
tool cannot drift from the rest of the site. Only the metadata, the structured
data and the tool itself are new. **Edits made directly to
`tools-standing-order.html` are destroyed on the next build** — change the
generator instead.

## What it stores

Shots go to the `sessions` store as a `RangeSession`: one record per visit,
each holding the clubs hit and the raw carry yardages in entry order. Only raw
shots are persisted. Every statistic is derived on read, so deleting a
mis-tapped shot recomputes the whole chart correctly.

Sessions are per-day: `getOrStartSession()` reuses the newest session started
since midnight and opens a fresh one otherwise. A bag gapped in July is never
averaged with one gapped in December.

## Statistics

Medians and percentiles throughout, never means. Nine 7-irons at 160 plus one
thinned 105 averages to 154.5 — a club nobody owns — while the median stays at
160. `stdev()` is the sample (n-1) deviation. The "80% band" is the empirical
p10–p90 of the reader's own shots: a description of dispersion, **not** a
confidence interval around the median, and the page says so rather than
dressing it up. Clubs with fewer than 5 shots are drawn greyed out and excluded
from the gap checks entirely.

The dispersion chart is hand-built SVG. No chart library, nothing to download,
nothing to parse before the page is usable. Club names are escaped into it.

## Two ordering traps this page already hit

1. `window.GolfrawLocker` **must not** be captured at parse time. The locker
   scripts are `defer`red, so the inline tool script runs first and would pin
   the reference to `null` — every shot then silently fails to save while the
   UI behaves perfectly. It is resolved inside `boot()`.
2. Club names from the bag **extend** the default club list, they never replace
   it. Replacing means a reader whose bag holds three clubs cannot log a
   fourth.

## The chart is not emailed

The modal generates the chart client-side and hands it over through the
browser's own print/save-as-PDF. There is no server on this site and therefore
nothing that can render or send a PDF. The newsletter field beside it is a
genuine opt-in to the existing HubSpot list and is deliberately not a gate: the
chart never depends on giving up an address. Do not reword this into a promise
to email the chart unless a HubSpot workflow that actually sends one exists.


# The Tendency Engine (`tools-tendency-engine.html`)

Tool 11, the post-round miss-pattern tracker. **Generated**, not hand-written:

    python3 scripts/build_tendency_engine.py
    python3 scripts/wire_locker.py

Edits made directly to the HTML are destroyed on the next build.

## `scorecards`, not `rounds`

Hole-by-hole cards go to the `scorecards` store. They must **never** go into
`rounds`: that store belongs to the Handicap Lie Detector, whose `saveRounds()`
calls `clear('rounds')` and rewrites the whole store on every keystroke. Hole
data written there is destroyed the moment the reader opens that tool, and
`RoundSchema` has no fields for it anyway.

The handoff between the two goes through `pushScoresToRounds()`, which reads the
existing rounds, appends only scores not already present, and writes the union
back. It merges; it never replaces. Repeated presses add nothing.

## What the numbers are

**Not strokes gained.** Real SG needs the distance and lie of every shot. This
compares four recordable rates — fairways, greens, scrambling, putts — against a
15-handicap benchmark (45% / 30% / 28% / 2.0 putts) and converts the gap into
shots via a fixed cost per event. Reliable about *which* category is worst,
rough about by how much. The page says exactly this, in those words. Do not
retitle it "Strokes Gained".

Bias detection is deliberately conservative: no directional call below 3 rounds
or 8 missed fairways, and only when one side takes 60%+. `bias()` returns
`count` — the *majority side's* count. Reporting `a` next to a side of `labelB`
prints a sentence that contradicts its own percentage; that shipped once in
testing and is covered by a regression test.

## The persist race

`persist()` binds the current card into a local `target` before the async save.
Reading the shared `card` inside the `.then` lets a save that began before
"New round" write the old card's id onto the new object — the new round then
overwrites the old record and a round vanishes. Caught in testing; keep the
local binding.

## No Monday digest

The newsletter opt-in is the site's existing Friday list and is described as
that. Nothing here can generate or send a personalised weekly trend digest, so
nothing promises one. The trend already updates on-device the moment a round is
logged.

# The Field Reader (`tools-field-reader.html`)

Tool 12, the weekly course-fit board. **Generated**, not hand-written:

    python3 scripts/build_field_reader.py
    python3 scripts/wire_locker.py

Edits to the HTML are destroyed on the next build.

## The weekly feed

`data/tournament-field.json` drives it. Update `event`, replace `players`, done.
`vercel.json` already serves `.json` with `max-age=0, must-revalidate`, so a new
feed reaches readers on their next visit with no cache-busting needed.

The file carries its own `_readme` array with the field-by-field rules, so
whoever updates it next week does not have to come here first.

## Archetypes, not invented players

The shipped field is twelve **archetypes**, every one flagged `"archetype": true`
and labelled on the board. They exist so the model works out of the box.

If you load a real field, use real numbers converted from a public source you
can point at — PGA Tour strokes-gained splits rescaled to 0-100. Do not estimate
a named player's ratings by feel. Publishing invented statistics about a real,
identifiable person is not a modelling shortcut, and the tool ships without
doing it precisely so nobody inherits that decision by accident.

## Fatal vs dropped

`validateFeed()` separates two things that are not interchangeable:

- **fatal** — a malformed `event`. An unknown `surface` makes every putting
  lookup `undefined` and the whole board becomes nonsense, so the board is
  refused with the reason instead of rendered.
- **dropped** — one malformed player. That entry is skipped, the rest of the
  field still ranks, and the count is reported.

An earlier version treated "at least one valid player" as success, which
rendered a full board off an invalid surface. Covered by a regression test.

## Scoring

Weighted mean of four 0-100 skills, putting read off the surface in play. All
weights at zero returns `null`, not `NaN`, and the board says so. Ties share a
rank and break alphabetically so the order is stable between renders.

Verdicts are **derived from the numbers**, not written by hand, so they cannot
drift out of step when the weights move. Note the single-driver case: when only
one category carries weight, `best` and `worst` are the same driver and the
two-sided phrasing silently drops it — that branch is handled explicitly.

## Focus survives the re-render

The board is rebuilt wholesale on every slider move and every lock, which
destroys the element the reader just activated. `renderBoard()` captures and
restores focus by player name; without it, a keyboard or screen-reader user is
thrown to the top of the document on every pick.

## Not a betting product

A fit score is not a probability, and the page says so. The site's own Terms
state it "does not facilitate wagering ... and is not gambling software" — keep
this tool on the right side of that line. No Wednesday board is promised in the
email capture either, because nothing here can assemble or send one.

# The weekly email pipeline (`api/`)

Vercel serverless functions, zero dependencies, CommonJS, native `fetch`. They
deploy alongside the static site; nothing is bundled or compiled.

| Path | Role |
| --- | --- |
| `api/cron/weekly.js` | the scheduled entry point |
| `api/unsubscribe.js` | RFC 8058 one-click unsubscribe (POST) and the human link (GET) |
| `api/_lib/config.js` | env, auth, and the safety gates |
| `api/_lib/templates.js` | both email templates, HTML + plaintext |
| `api/_lib/subscribers.js` | reads the list from HubSpot |
| `api/_lib/send.js` | dispatch via Resend |
| `api/_lib/token.js` | HMAC-signed unsubscribe tokens |

Files under `api/_lib/` are not routes: Vercel excludes anything prefixed with
an underscore.

## It will not send by accident

Three independent gates, and all three must be cleared:

1. **Auth.** `api/cron/weekly` returns 401 without `Authorization: Bearer
   $CRON_SECRET`. Vercel sends that automatically on scheduled runs. Nobody can
   trigger a send by visiting the URL.
2. **Dry run by default.** `EMAIL_DRY_RUN` must be *exactly* `"0"` to send.
   Unset, `"1"`, `"true"`, `"yes"` and every typo all mean dry run.
3. **Compliance and audience.** Missing `RESEND_API_KEY`,
   `MAIL_POSTAL_ADDRESS`, `UNSUBSCRIBE_SECRET`, or `HUBSPOT_TOKEN` forces a dry
   run *regardless of step 2*, and the response names what is absent. A
   commercial email with no postal address is unlawful under CAN-SPAM, so the
   pipeline refuses rather than shipping one. HubSpot is the sole production
   audience source; opted-out, unsubscribed, bounced, and duplicate contacts are
   removed before dispatch.

`EMAIL_MAX_RECIPIENTS` (default 500) caps any single run.
The From header is fixed as `GolfRaw <contact@golfraw.com>`; `golfraw.com` must
be verified in Resend.

## Deliverability and the law

- One message per recipient. Never a shared `To` or `BCC`: that leaks every
  subscriber's address to every other subscriber and cannot carry a per-person
  unsubscribe link.
- `List-Unsubscribe` and `List-Unsubscribe-Post: List-Unsubscribe=One-Click` on
  every message. Gmail and Yahoo require these from bulk senders; without them
  the unsubscribe surfaces as "report spam" instead.
- Unsubscribe tokens are HMAC-signed, so a link only works for the address it
  was issued for and the list cannot be enumerated. **No expiry** — a link dug
  out of a six-month-old email must still work.
- Unsubscribing is immediate on both GET and POST. No confirmation step, no
  winback. Rotating `UNSUBSCRIBE_SECRET` invalidates every old link, so treat it
  as permanent.
- Real `text/plain` alternative on every message, not a stub.

## Why template B is not personalised

It cannot be. Every number the tools produce — bag, range sessions, scorecards,
picks — lives in the reader's own IndexedDB and **never reaches a server**. The
locker makes zero network calls, and every tool page says so in those words.

A "your tendencies this week" email would require uploading all of it, which
would make that promise false. So template B is a practice note that rotates
through four pieces and says plainly that we do not have the reader's numbers.

Changing this is a product decision with a real trust cost, not a feature.

## Schedule

Vercel calls `/api/cron/weekly?template=field` every Monday at 09:00 UTC
(`0 9 * * 1`). Authenticated manual calls may request `?template=practice`.

## Reviewing the templates without deploying

    node scripts/preview_email.js

Writes both templates as `.html` and `.txt` to `.email-preview/` (gitignored).
No credentials, no network, nothing sent.

## The "Golf Vibe" theme layer (`apply_theme.py`)

The site's colour, type and motion live in one global layer rather than in
the per-page inline shells:

- `public/theme-golf.css` — palette tokens (re-pointing every shell
  generation's custom properties to the championship-green system), Plus
  Jakarta Sans headlines over an Inter body with Arial metric-matched
  fallbacks (no CLS on swap), brand wordmark, header elevation, card/button
  motion, scroll-reveal styles. Loaded after each page's inline CSS so it wins.
- `public/theme-golf.js` — header `gr-scrolled` toggle and IntersectionObserver
  reveals. Progressive enhancement only.
- `public/fonts/inter-var.woff2`, `plus-jakarta-sans-var.woff2` — self-hosted (SIL OFL), latin subsets.

`python3 scripts/apply_theme.py` injects the managed `<!-- THEME:START/END -->`
block before `</head>` on every page, rewrites every colour literal the
pre-theme shells hardcoded onto the token scale (the `LITERALS` table: brand
red → green accent, warning red → amber, and since v8 the old greys, greens and
paper tints → slate/green), strips the header badge and Method-card numbers,
and marks the header search link as an icon button. Idempotent;
`--check` reports without writing. **Bump `THEME_VER`** whenever the CSS or JS
changes — `.css`/`.js` are served with an immutable one-year cache.

The palette (v8) is Tailwind-aligned: slate-900 `#0f172a` ink and dark
surfaces, green-800 `#166534` brand, green-700 `#15803d` interactive, slate-50
`#f8fafc` ground, slate-200/300 hairlines, amber-700 `#b45309` caution, and
amber-500 `#f59e0b` as the Golf Raw Pro accent (overrides for the `.gr-pro-*`
classes live at the end of `theme-golf.css`, prefixed with `html` so they
out-rank the styles `pro.js` injects). Three more stylesheets consume the same
tokens and carry their own cache versions:

- `public/tool-premium.css?v=3` — the tools' shared presentation layer
  (`PREMIUM_LINK` in the four builders, `schema_normalizer.py`, and the
  contract test `tests/premium-tools-ui.test.js`). Its header/nav rules were
  removed in v3: the theme owns the header on every page.
- `public/tool-cta.css?v=2` — in-article tool CTAs (`tool_cta.py`).
- `lib/locker/*.js?v=8` — the Locker drawer's injected CSS uses the palette
  too, so a palette change bumps `VER` in `wire_locker.py` (which also
  rewrites the article pages that carry the drawer).

Typography (v9) is three layers from two self-hosted variable fonts: Plus
Jakarta Sans for headlines and big numbers, Inter for reading text, and Inter
600 uppercase with `.05em` tracking and tabular figures as the meta layer
(bylines, dates, badges, scores, table heads). `apply_theme.py` re-points every
shell's `'IBM Plex Mono', monospace` stack to `var(--gr-meta)` and strips the
Plex preload, so no page requests a third font file. The scale lives in
`html:root`: `--gr-h1` `clamp(2rem, 4vw + 1rem, 3.25rem)`, `--gr-h2`
`clamp(1.5rem, 2.5vw + .75rem, 2.25rem)`, `--gr-h3`, `--gr-lead` 1.125rem,
`--gr-body` 1rem at 1.65 line-height, `--gr-meta-size` .6875rem; the article
measure is 72ch. Fallback faces are Arial metric-matched so a font swap is
CLS-free. Google Fonts is deliberately not used (no preconnect needed).

Favicons and the schema logo are installed by `python3 scripts/apply_icons.py`
(idempotent): it replaces every icon/apple-touch/manifest/theme-color line with
the Google Search set (48/32/16px PNGs, 180px Apple icon, `site.webmanifest`
with the 192/512px icons) and re-points each JSON-LD publisher `logo` to
`/icon-512.png` at the object level. The brand PNGs are served from the site
root (`/favicon-48x48.png`, `/apple-touch-icon.png`, `/icon-192.png`,
`/icon-512.png`, `/logo.png`; the `/public` copies are the originals), and
`vercel.json` rewrites `/favicon.ico` onto the 48px PNG for clients that never
read the markup. Run it after any page rebuild that regenerates a head from an
old template.

One brand spelling, `GolfRaw`, is enforced by `python3 scripts/apply_brand.py`
(idempotent). Google's Site Names system picks a name from the homepage
`WebSite` markup, `og:site_name`, the `<title>` and headings, and falls back to
the bare domain when they disagree; this site had carried GOLFRAW, GolfRaw,
Golf Raw and RawGolf side by side. The pass rewrites visible text and head
metadata outside `<script>`/`<style>`, edits JSON-LD at the object level
(publisher `GolfRaw`, author `GolfRaw Editorial`, product `GolfRaw Pro`), keeps
the legacy spellings as `alternateName` on the `WebSite` and `#organization`
nodes only, sets `og:site_name` and adds `application-name`. The generators
(`article_schema.py`, `schema_normalizer.py`, `sync_site.py`, `tool_inventory.py`,
the builders) and `articles.json` emit the same spelling, so the pass is a
guard rather than a dependency. Pipeline order after any rebuild: builder,
`wire_locker.py`, `apply_theme.py`, `apply_icons.py`, `apply_brand.py`.

Google Search Console ownership uses the HTML-tag method on the homepage
(`<meta name="google-site-verification" content="vOoo-…" />`, token in
`GOOGLE_SITE_VERIFICATION` in `fix_seo_audit.py`). The tag sits inside that
script's managed metadata block on `index.html`: a repair strips any stray copy
and re-emits exactly one, validation fails if it is missing or altered, and
`tests/test_site_verification.py` guards all of it. Never delete it by hand;
if the token ever changes, change the constant and the test together.

The eight hand-written tools (`tools-bag-audit`, `gimme-audit`,
`handicap-detector`, `plays-like`, `round-autopsy`, `settle-up-calculator`,
`tee-box-check`, `tilt-meter`) keep their layout CSS in two inline `<style>`
blocks ahead of the THEME block. They were stripped by an early JSON-LD
normalizer pass (commit 4e7a274) and restored from its parent; the current
`_replace_all_json_ld` preserves anything between schema blocks.

To restore the original design: `git checkout backup/original-version`, or
remove the THEME block and revert the literal rewrites from that branch.

## Generated tools share one shell extractor (`tool_shell.py`)

`build_standing_order.py`, `build_tendency_engine.py` and `build_field_reader.py`
lift their head, header, footer and behaviour scripts from `tools-bag-audit.html`
through `tool_shell.shell_parts()`. It finds each part by marker, never by line
number, and strips the managed LOCKER/THEME/TOOL-EVENTS blocks (the wiring
scripts re-add them). After any rebuild run, in order: the builder,
`wire_locker.py`, `wire_tool_events.py`, `apply_theme.py`. The builders import
from both `scripts/` and the repo root, so run them as
`PYTHONPATH=.:scripts python3 scripts/build_<tool>.py`.

## Golf Raw Pro: launch-monitor import (`lib/pro/lm-import.js`)

The Standing Order can ingest a CSV export from TrackMan, Foresight, Garmin,
FlightScope, Rapsodo, SkyTrak or any file with a club column and a carry column.
The engine is a standalone UMD module (no network code): delimiter sniffing,
RFC 4180 tokenizing, preamble/units-row/summary-row detection, heuristic column
mapping the reader can override, club-name normalisation to the tool's own
list, metres→yards conversion against the profile unit, and an optional mishit
filter. It emits the same `{name, shots[]}` records the keypad produces, so all
statistics and the bag sync are unchanged.

- Test: `node scripts/test_lm_import.js` (synthetic exports shaped like each
  vendor's real headers plus the edge cases).
- **Bump `LM_VER`** in `build_standing_order.py` whenever the module changes
  (immutable `.js` cache), then rebuild, wire, theme.

## Golf Raw Pro: coach & fitter report (`lib/pro/report.js`, `build_coach_report.py`)

`tools-coach-report.html` is generated by `build_coach_report.py` (same shell
extractor; run the builder, then `wire_locker.py`, `wire_tool_events.py`, then `apply_theme.py`). The
engine builds one model from the Locker — active bag, a range session, completed
scorecards — using the exact thresholds of the tools that own each number, and
renders it as a one-page document. Export is the browser's own print-to-PDF
(`@page` A4, a body-level print clone), and the share link carries the whole
model base64url-encoded in the URL fragment, which browsers never send to a
server. Test: `node scripts/test_report.js`. **Bump `REPORT_VER`** in the
builder whenever `report.js` changes.

## Golf Raw Pro: Stripe entitlement (`api/_lib/pro.js`, `lib/pro/pro.js`)

Stateless paywall. Stripe is the record of who paid; a signed token in the
reader's Locker (`meta` store, key `pro.pass`; localStorage fallback) is the
proof they carry. No user table, no sessions, no cookies.

Endpoints (Vercel functions, zero dependencies, Stripe over plain `fetch`):

| Route | Does |
|---|---|
| `GET /api/pro-config` | `{enabled, restoreByEmail, plans[]}` — plans are read from Stripe Prices, never hardcoded. `enabled:false` until configured. |
| `POST /api/create-checkout-session` | `{priceId}` → Stripe Checkout URL. Only `PRO_PRICE_IDS` accepted; same-site origin required. |
| `GET /api/pro-claim?session_id=` / `?restore=` | Paid session or restore token → entitlement token (Stripe consulted every time). |
| `POST /api/pro-verify` | Signature + expiry check. |
| `POST /api/pro-refresh` | Near expiry: re-reads the subscription's period end from Stripe and re-mints. |
| `POST /api/pro-restore` | `{email}` → emails a 30-day restore link (needs Resend). Same response whether or not the address is known. |
| `POST /api/stripe-webhook` | Verifies `Stripe-Signature` when a raw body is available AND re-fetches the event by id; on a paid Pro checkout sends the welcome/restore mail. Not load-bearing for entitlement. |

Client states: **preview** (config says disabled, or the API is unreachable —
fails *open*, badge "free in preview"), **gated** (on sale, no valid pass:
dimmed panel + cover + modal), **pro** (valid pass; verified with the server
when online, trusted until expiry when offline). Gating is a convenience for
honest readers, not a security boundary: the Pro outputs are built on the
device.

To switch Pro on: create the Prices in Stripe, then set `STRIPE_SECRET_KEY`,
`PRO_PRICE_IDS`, `PRO_ENTITLEMENT_SECRET` (and optionally
`STRIPE_WEBHOOK_SECRET`, `RESEND_API_KEY`) in the Vercel project — see the
header of `api/_lib/pro.js`. Nothing else changes; the two Pro panels gate
themselves on the next load. Pages: `/pro-thanks` (Stripe success URL, claims
and stores the pass; bookmarkable) and `/pro-restore` (restore link target +
email form), both noindex, generated by `build_pro_pages.py`.

Tests: `node scripts/test_pro_api.js` (45 checks, mocked Stripe) and
`node scripts/test_pro_client.js` (state machine). **Bump `PRO_VER`** in the
three builders whenever `lib/pro/pro.js` changes; **bump `VER`** in
`wire_locker.py` whenever `lib/locker/*` changes.

## Tool events (`lib/analytics/tool-events.js`, `wire_tool_events.py`)

One shared layer records what golfers do with the tools, never what they type.
It rides on the existing GA4 tag (`G-PMECW4VW66`), adds no cookies, and pushes
to `window.dataLayer` through an allowlist: six live events
(`tool_viewed`, `tool_started`, `tool_completed`, `result_shared`,
`related_tool_clicked`, `tool_error`), fixed parameter keys, and values that are
registry ids or short lowercase enums. Numbers and free text cannot pass, so a
score, handicap, yardage, name, stake or result can never be sent even by
mistake. `round_logged`, `pro_*` and `review_*` are reserved: `track()` refuses
them until the feature that fires them ships and moves them into `EVENTS`.

`wire_tool_events.py` injects the loader into every tool page as a managed
`<!-- TOOL-EVENTS:START/END -->` block just ahead of the LOCKER block
(`--check` reports drift). **Bump `VER`** there whenever `tool-events.js`
changes (immutable `.js` cache). The helper's tool registry mirrors
`tool_inventory.py`; `tests/test_tool_events.py` fails if they drift.

Page wiring is per tool, because each tool starts and finishes differently:

- `data-gr-inputs` on the input panel: a trusted edit or button press inside it
  is the start (`data-gr-inputs="import"` keeps the import mode, as on the Coach
  Report, whose data comes from other tools).
- `data-gr-run` on a run button inside that panel; `data-gr-ignore` on reset,
  clear and navigation controls that are not a start.
- `data-gr-mode="sample"` on sample-data buttons, so demo runs are recorded as
  `input_mode=sample` and never inflate real completions. Add `data-gr-saved`
  where the tool saves what the button loads (Bag Audit, Tilt Meter, Gimme
  Audit): the helper then keeps one local flag, `gr_track_sample:<tool_id>`, so
  a Run after a reload still counts as sample. The first real edit clears it;
  it is never sent.
- `data-gr-placement` on containers holding links to other tools.
- `GRTrack.completed()` on the valid-result path only (the hand-written tools
  call it just before `RawGolf.save`), and `GRTrack.shared(method)` where a
  copy, download, share or print is known to have succeeded (`rawgolf-tools.js`
  reports downloads and native shares itself).

Starts and completions count once per input mode per page view, so recalculating,
live re-renders and Save-reruns are not new completions. A share only counts
after a completion in the same view. On `localhost` events carry
`debug_mode` for GA4 DebugView; `localStorage.gr_track_debug = '1'` does the
same on production. `GRTrack.events()` returns what the page sent.

Tests: `node tests/tool-events.test.js` (the privacy guard and dedupe rules,
run against a stub page) and `python3 -m unittest tests.test_tool_events`
(wiring on all 14 pages, allowed call arguments, the Gimme → Handicap chain).
The measurement plan is in `docs/tool-events-measurement.md`.

## The Distance Check (`lib/distance/club-distance.js`, `build_club_distance.py`)

`tools-club-distance-calculator.html` is generated by `build_club_distance.py`
(same shell extractor; run the builder, then `wire_locker.py`,
`wire_tool_events.py`, `apply_theme.py`, `apply_icons.py`, `apply_brand.py`).
The model is a standalone UMD module with no network code: one anchor (driver
carry, 7-iron carry, driver swing speed or a handicap band) becomes a carry
range for 13 clubs, a best-strike range and a confidence label, plus a Tee It
Forward course-length range. It works in yards and mph; the page converts to
metres and km/h at the edges. Every coefficient is cited in the module header
(USGA/R&A 2023 recreational study, TrackMan 2024 tour averages, the 2011 Tee It
Forward chart).

- Tests: `node tests/club-distance.test.js` (input validation, a sweep of every
  accepted input, the published anchors) and
  `python3 -m unittest tests.test_club_distance_page` (metadata, schema,
  handoffs, and the static example table matched against the model).
- **Bump `MODEL_VER`** in the builder whenever `club-distance.js` changes
  (immutable `.js` cache), then rebuild. The "three golfers" example table is
  static HTML in the builder; the page test fails if it drifts from the model,
  so update both together.
- Analytics: `GRTrack.completed({ anchor_type })` sends which kind of number the
  golfer started from, never the number, the band or any output.


## The Settle Up V2 (`lib/games/settle-core.js`, `lib/games/settle-up.js`)

`tools-settle-up-calculator.html` is hand-written; its maths is two UMD modules
tested in Node (`node tests/settle-up.test.js`, and the page contract
`python3 -m unittest tests.test_settle_up_page`).

- **settle-core.js**: money as whole minor units (cents or hundredths of a
  point; currency is presentation only), stroke allocation by stroke index
  (Rules of Handicapping Appendix E, plus handicaps give back from SI 18,
  nine-hole rounds rank the nine), and `settle()`: the fewest possible
  payments (the largest number of zero-sum sub-groups, then largest debtor
  pays largest creditor inside each). Nobody both pays and receives.
- **settle-up.js**: skins (outright low wins; carryovers on or off; carried
  skins after the last hole are lost or go to a named playoff winner; optional
  birdie double; net strokes full or off the low), Nassau (match play, every
  pair, front/back/18, net at 100% of the difference; presses off, automatic
  at 2 down on the latest bet of each nine and the 18, or entered by hand) and
  closest to the pin on par 3s. Every rule is an input; `validate()` names the
  exact player and hole for any problem.
- Nothing about a round is put in a URL. Shares are plain text (the page opens
  the share sheet itself so line breaks survive). Analytics gets
  `game_type` and `scoring_mode` enums only.
- Saved state lives in this browser (`golfraw_settleup_round`,
  `golfraw_settleup_group`, format `v: 2`); the page still reads the V1 format.
- **Bump `version`** in a module and its `?v=` on the page together.
- Wolf is deliberately not in V2: its scoring has no agreed standard.

## Ads and consent (`lib/ads/tool-ads.js`, `wire_ads.py`)

Decisions, placement map, measurement plan and the activation steps live in
`docs/monetization-m1.md`. The engineering rules:

- `wire_ads.py` is the one wiring script for ads and consent. Run it after
  any builder, with `wire_locker.py` and `wire_tool_events.py`; `--check`
  reports drift. It does three things:
  - puts the `CONSENT-MODE` block before gtag.js on every GA4 page: defaults
    denied for the EEA, UK and Switzerland (32 ISO codes), granted elsewhere;
  - adds a Pro check to the article Auto ads loader, and to the two guide
    builders that embed it;
  - puts the `TOOL-ADS` block on every tool page in
    `tool_inventory.tracked_pages()`, replacing the inline loader.
- `TOOL-ADS` sits directly before `TOOL-EVENTS`. That block sits before
  `LOCKER`, which sits before `</body>`, so none of the three scripts moves
  another's block. `tool_shell.py` strips both new blocks, as it does the
  others.
- Tool pages never carry a static AdSense bootstrap, an `ins.adsbygoogle`, or
  `window.__gr_ads=true`. The module loads adsbygoogle.js once, only after a
  result, only when the `UNITS`, `AUTO_ADS_EXCLUDED` and `PAGES` switches allow
  it, and never with a live Pro pass.
- Slots are `data-gr-ad="after_result"` inside the result container, after its
  last action, and `data-gr-ad="lower"` before the FAQ with
  `data-gr-ad-when="#<result id>"`. Both start `hidden`.
- Never put a slot inside a `data-gr-inputs` panel, a form, a table, a
  scorecard entry or who-pays-whom. `tests/test_tool_ads.py` enforces it.
- Unit ids are real AdSense ids (ten digits) or empty; never invent one.
  Set since M1.1: `8457096514` (after_result), `1432433875` (lower), on the
  four `PAGES` pilots. Readers get them only once `AUTO_ADS_EXCLUDED` is
  `true`, and that needs a QA check showing no Auto ads on every pilot. Add a
  page to `PAGES` only after it is excluded in AdSense too. QA browsers set
  localStorage `gr_adtest=1` for test ads; that also skips the
  `AUTO_ADS_EXCLUDED` hold. Test with the tab in the foreground.
  Bump `VER` in `wire_ads.py` and `version` in the module together.
- Tests: `node tests/tool-ads.test.js` (the module in a fake browser) and
  `python3 -m unittest tests.test_tool_ads`. For a local look with a stub,
  set localStorage `gr_ads_test` to
  `{"units":{"after_result":"1111111111","lower":"2222222222"},"autoAdsExcluded":true,"adsSrc":"/tests/fixtures/adsbygoogle-stub.js"}`
  on localhost. The live domain ignores it.

## The Round Card (`lib/round/round-card.js`, `build_round_card.py`)

`tools-scorecard-analyzer.html` is generated (edit the builder, then run the
usual chain: builder, `wire_locker.py`, `wire_tool_events.py`,
`apply_theme.py`). The analysis is one UMD module tested in Node
(`node tests/round-card.test.js`, which also runs the real Locker in a
sandbox) plus the page contract (`python3 -m unittest tests.test_round_card_page`).

- **Input**: par and score on every hole, 9 or 18 holes. Optional putts and
  penalty strokes. Greens in regulation are derived (score - putts <= par - 2,
  unknown with 0 putts), never asked. Fairways are deliberately not collected:
  fairway rate barely moves with handicap and costly tee misses show up as
  penalties. In detail mode an empty penalty box on a hole with putts is
  stored as 0; a saved card with no penalty anywhere (a Tendency Engine card)
  keeps them unknown.
- **Blow-up**: double bogey or worse; when the typical hole (median to par,
  rounded down) is already a double, triple or worse. The result states the
  rule it used. Each blow-up is tagged from the optional stats: penalty,
  three putts or more, two or more extra shots to reach the green.
- **Findings**: at most three, from the card only, no handicap benchmarks, no
  strokes gained, no "tilt" (TheGrint found play after a blow-up is no worse).
  Confidence: strong when the stat covers >= 90% of holes, some >= 60%, unused
  below. The one focus is whichever of penalty strokes, putts beyond two or
  extra shots to the green cost most (>= 3 strokes on 18, >= 2 on 9, no tie);
  approach and damage control are only ever "some evidence".
- **Storage**: rounds live in the Locker's `scorecards` store beside the
  Tendency Engine's, so it is one history. The card being typed also lives in
  `localStorage` (`golfraw_roundcard_draft`); a blocked storage still leaves a
  working card. A card started in the Round Autopsy
  (`golfraw_autopsy_round`) can be opened once, on request.
- **Scorecard record, schema v2** (Locker `ScorecardSchema`; v1 is the
  Tendency Engine's card and still reads):

  ```
  { id: 'card-…',            // Locker uid, made on this device
    v: 2,                    // 1 = Tendency Engine card, 2 = Round Card
    course: '',              // up to 80 chars, never leaves the device
    playedAt, createdAt, updatedAt,   // ms; playedAt is local noon of the date played
    holes: [ { par: 3-6, score: 1-15|null, putts: 0-6|null, pen: 0-6|null,
               fir: 'hit'|'left'|'right'|null,          // Tendency Engine only
               app: 'hit'|'miss'|'short'|'long'|'left'|'right'|null } ],  // 9 or 18
    summary: { holes, gross, par, toPar, blowups, blowupToPar,
               putts|null, pen|null, gir|null, detail: 'quick'|'detailed' } | null }
  ```

  `null` always means "not recorded". `summary` is recomputed from the holes on
  every save and never trusted over them. A valid round is 9 or 18 holes, all
  scored. `listCompletedScorecards()` still returns 18-hole cards only, because
  the Tendency Engine and the Coach Report average per 18 holes; a finished
  9-hole card is no longer mistaken for a Tendency Engine draft.
- **Export / import**: `golfraw.rounds` v1 JSON (and CSV, one row per hole, for
  spreadsheets). Import reads that or a whole Locker backup, keeps only valid
  rounds, and adds new ids or newer copies. Nothing is uploaded.
- **Habit data** for a later multi-round review is derived, not stored:
  `habit(cards)` gives valid rounds, dates played and the first logged date.
  The page only says how many rounds are saved; nothing is sold.
- Analytics: `tool_completed` carries `round_length` (`nine`|`eighteen`) and
  `detail_mode` (`quick`|`detailed`) only. Never a score, course, date, hole,
  history count or summary.
- **Legacy**: The Round Autopsy left the hub (`LEGACY_TOOLS` in
  `tool_inventory.py`), stays live and tracked, and points here; so does the
  Tilt Meter, which stays listed. Neither is redirected: both had near-zero
  search value (Search Console, Mar-Sep 2026: 14 and 95 impressions), and a
  301 waits on an explicit decision.
- **Bump `MODEL_VER`** in the builder with any change to `round-card.js`.

## Units: yards or metres across the distance tools (`lib/distance/units.js`)

The Distance Check, Plays Like, Tee Box and Bag Audit run one model each, in
one canonical unit per quantity: yards, feet, °F and mph. Pages convert what
the golfer types into those units at full precision, run the model once, and
round only the numbers they show. `units.js` holds the exact conversions
(0.9144 m/yd, 0.3048 m/ft, 1.609344 km/h per mph), inward-rounded input
limits, and `field()`, which keeps the exact value behind a number input so
yards -> metres -> yards returns what was typed. No separate metric logic,
no separate URLs.

- **The preference** is the Locker profile's existing `units` field
  (`yards` | `meters`), the one the drawer, The Standing Order and the Coach
  Report already read. `GolfrawUnits.setDistance()` writes it through
  `GolfrawLocker.setUnits()`, which converts stored bag carries and range
  shots (one decimal, never accumulating) instead of relabelling them. The
  drawer goes through `setUnits` too. First visit: yards. Nothing reaches a
  URL or the analytics layer.
- **Temperature and wind** (Plays Like only) are not in the profile. They
  default from the browser language (°F only for the US; mph for the US and
  UK) and are saved in Plays Like's own state.
- **Storage stays canonical**: Plays Like and Tee Box save yards/°F/feet/mph
  (the format they always used), Bag Audit's own key saves yards, and the
  Locker bridge writes the bag in the profile's units, reading the profile in
  the same step as the write.
- Bag Audit's switch styles sit in a `<!-- UNITS:START/END -->` block that
  `tool_shell.py` strips, so the generated tools do not inherit them.
- `wire_locker.py` now also refreshes the Locker `?v=` inside the Locker
  blocks on articles and hubs, so a `VER` bump reaches every page.
- Tests: `node tests/units.test.js` (conversions, rounding rules,
  repeated-switch drift, imperial-vs-metric equivalence for all four tools,
  Distance Check vs Tee Box), `node tests/locker-units.test.js`, and
  `python3 -m unittest tests.test_distance_units_pages`. **Bump `version`**
  in `units.js` (and every page's `?v=`) when it changes.

## Plays Like and Tee Box models (`lib/distance/plays-like.js`, `lib/distance/tee-box.js`)

Both pages are hand-written (no builder); their maths lives in these two UMD
modules so it can be tested in Node. Each module header cites its sources and
names the places where GolfRaw simplifies beyond them.

- **Plays Like:** altitude 1.16% per 1,000 ft (Titleist), full from 100 yards
  and fading to none at 50; air temperature 0.75% per 10°F from 70°F
  (Titleist); wind 1 yd/mph into it and half downwind (Rice/Broadie, PING),
  applied at 150 yards and scaled with the shot; elevation a yard for a yard;
  humidity 0. Each effect is worked out alone and added, and the rounded
  breakdown always sums to the rounded total.
- **Tee Box:** needs `club-distance.js` loaded first. It reads the Tee It
  Forward chart and the USGA carry-to-total fit from that module, so it and
  The Distance Check always agree. Stroke cost uses the USGA Course Rating
  length formulas (1 per 220 yds scratch, 1 per 160 bogey), placed by score.
- Tests: `node tests/plays-like.test.js`, `node tests/tee-box.test.js`, and
  `python3 -m unittest tests.test_playslike_teebox_method` (sources, rules
  note, static numbers against the models, unchanged title and H1).
- **Bump `version`** in a module whenever it changes, and the matching
  `?v=` on the page (the page test fails if they differ). A change to
  `club-distance.js` also means bumping `MODEL_VER` in `build_club_distance.py`.
