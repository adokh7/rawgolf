# GolfRaw indexing and technical SEO audit

Audit date: 2026-08-13
Production origin: `https://www.golfraw.com`

## Executive diagnosis

The recent articles are technically crawlable and indexable. The production
site is not blocking Googlebot, the sitemap contains the correct clean URLs,
and the named article URLs return direct HTTP 200 responses with matching
self-canonicals.

The primary pipeline defect was use of Google's Indexing API for ordinary
`NewsArticle` pages. Google restricts that API to pages containing
`JobPosting`, or `BroadcastEvent` embedded in a `VideoObject`. An HTTP 200 from
`urlNotifications:publish` confirms notification receipt; it does not make a
normal article eligible for the API and does not prove indexing. Metadata
lookups for the two named articles returned HTTP 404 `NOT_FOUND` despite the
old script reporting their earlier publish calls as `200 OK`.

The Search Console API is also disabled for Google Cloud project
`843856762072`. A read-only property/index inspection request returned HTTP 403
`accessNotConfigured`. This does not block Googlebot, but it prevents the
pipeline from checking Google's real coverage state and helped the false
success message go unnoticed.

A separate deployment misconfiguration was also confirmed. This workspace was
linked to Vercel project `golf` (`prj_hJQ1yyDxcumXKOBgUFAltlxaQcO2`), while
`www.golfraw.com` belongs to project `rawgolf`
(`prj_bW4iQwYFEw3s7EJ9rzBChI1sV7xX`). The old pipeline could report a successful
production deployment on the `golf` project while the real custom domain kept
serving the previous build. GitHub pushes had masked this by triggering the
separate `rawgolf` project. The workspace is now linked to `rawgolf`, and
deployment `dpl_8VYScQqviLUvDLJMumDxr6fZFrpk` is live on
`https://www.golfraw.com`.

The Search Console UI's "Indexing request rejected" message is not explained
by a crawl/indexability defect found on the site. Google's documentation says
URL Inspection requests can fail silently when the property's request quota is
exceeded. The remaining likely causes are that separate UI quota or a temporary
Search Console service error. Repeated requests do not accelerate crawling.

Official references:

- https://developers.google.com/search/apis/indexing-api/v3/using-api
- https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl
- https://support.google.com/webmasters/answer/10351509

## Verified production results

- Crawled all 247 sitemap URLs with a Googlebot smartphone user agent.
- 247/247 returned direct HTTP 200 responses.
- Zero sitemap redirects and zero redirect loops.
- Zero `X-Robots-Tag` headers.
- Every sitemap HTML response used the exact expected self-canonical.
- Every sitemap HTML response used `index, follow, max-image-preview:large`.
- Largest HTML response was 215,880 bytes, well below Google's 2 MB HTML fetch
  limit.
- `robots.txt`, `sitemap.xml`, the IndexNow key file, and both named articles
  returned HTTP 200.
- `.html` article URLs returned a single 308 redirect to the clean URL.
- HTTP and non-www requests resolved to the HTTPS www canonical without loops.

Named article checks:

- `/news-2026-7-wood-vs-3-iron-australian-golfers`: HTTP 200, exact clean
  canonical, index/follow, present in sitemap.
- `/news-2026-liv-golf-michigan-team-championship-cancelled`: HTTP 200, exact
  clean canonical, index/follow, present in sitemap.

## Local metadata and sitemap results

- Scanned 249 root HTML files.
- 249/249 contain exactly one robots meta directive with the required value.
- Zero `noindex` or `nofollow` directives.
- Zero dirty sitemap URLs, `.html` sitemap URLs, brackets, spaces, duplicates,
  or invalid `<lastmod>` values.
- All 217 active registry articles are present in `sitemap.xml`.
- The only duplicate local canonical belongs to the legacy
  `what-beginners-actually-search.html` alias, which is intentionally excluded
  from the sitemap and permanently redirected by Vercel.

## Code defects fixed

### `scripts/fast_index.py`

- Stops sending normal editorial pages to Google's restricted Indexing API.
- Checks JSON-LD and permits that API only for eligible job or livestream
  pages.
- Describes Google API HTTP 200 accurately as notification acceptance, not an
  indexing result.
- Normalizes `.html` inputs to clean URLs.
- Rejects query strings, fragments, brackets, whitespace, backslashes, foreign
  hosts, and non-canonical schemes.
- Retains `.fast-index-pending.json` if WebSub, IndexNow, URL validation, or an
  eligible Google API delivery fails.
- Clears the queue only after successful delivery.
- Returns a nonzero process status on failure so deployment automation can see
  it.

### `scripts/sync_site.py`

- Detects both new and edited articles using SHA-256 fingerprints of registry
  metadata and HTML content.
- Migrates the old URL-only state without resubmitting the full archive.
- Merges pending changes instead of overwriting them.
- Rejects dirty registry URLs during validation.

### `vercel.json`

- Removed the unnecessary SPA catch-all rewrite to `/index.html`.
- Kept Vercel's native `cleanUrls` behavior for the static multi-page site.
- Added explicit `trailingSlash: false` canonicalization.
- Added the official Vercel JSON schema declaration.

### Vercel project binding

- Relinked the local workspace from project `golf` to the `rawgolf` project
  that owns `golfraw.com`.
- Verified the final deployment is `Ready`, targets production, and is aliased
  directly to `www.golfraw.com` and `golfraw.com`.
- Verified both clean article URLs return HTTP 200, `.html` and trailing-slash
  variants return one 308 to the clean URL, and unknown paths return 404.

### HTML metadata

`scripts/fix_seo_audit.py` repaired and normalized managed metadata on 15
recent pages. A subsequent read-only audit passed all 249 HTML files for title,
description, indexability, canonical/social parity, and required tags.

## External Search Console configuration still required

Enable `searchconsole.googleapis.com` for Google Cloud project `843856762072`,
then make sure the service account in `service_account.json` is an owner or full
user of the `sc-domain:golfraw.com` Search Console property. This enables
read-only URL Inspection diagnostics; it does not itself force indexing.

After enabling the API, use URL Inspection to review `coverageState`,
`pageFetchState`, `robotsTxtState`, `indexingState`, `userCanonical`, and
`googleCanonical`. For ordinary articles, rely on the sitemap, internal links,
and crawl quality rather than the restricted Indexing API.
