# GolfRaw — Full SEO Audit

**Health Score: 74/100**  
**Site type:** Independent digital publisher — golf news, evergreen guides and free client-side tools (Publisher / Media, not local or e-commerce)  
**Scope:** 227 pages analysed locally, live verification against production, 216 sitemap URLs status-checked  
**Date:** 2026-08-08

> Tooling note: this skill's helper scripts (`render_page.py`, `google_auth.py`, `backlinks_auth.py`, `google_report.py`) are not installed, and the PageSpeed Insights API returned a quota error. So there is **no Lighthouse score, no CrUX field data, no GSC/GA4 data and no backlink profile** in this audit. Performance findings are lab proxies measured directly. Everything else is first-hand evidence.

## Top findings

1. pga-tour.html declares rel=canonical and og:url pointing at /tournaments, telling Google the 92-article PGA Tour hub is a duplicate and should be de-indexed
2. Homepage ships ~5 MB (2.4 MB images + 2.5 MB autoplaying video) — the single biggest ranking and UX drag
3. 56 images exceed 400 KB; two unoptimised AI exports at 1.7 MB and 1.4 MB
4. BreadcrumbList schema on 1 of 227 pages, forfeiting breadcrumb rich results sitewide
5. Only 2 of 196 content pages cite an external source, a weak E-E-A-T signal for a news publisher

## Quick wins

1. Fix the pga-tour canonical and og:url (one-line change, restores a 92-article hub to the index)
2. Compress the 56 oversized images and drop or lazy-load the 2.5 MB homepage video
3. Add BreadcrumbList JSON-LD to article and tool templates
4. Add the 5 missing security headers via vercel.json
5. Publish /llms.txt to guide AI crawlers

## Category scores

| Category | Score | Weight |
|---|---|---|
| Technical SEO | 72/100 | 22% |
| Content Quality | 84/100 | 23% |
| On-Page SEO | 76/100 | 20% |
| Schema / Structured Data | 80/100 | 10% |
| Performance (CWV) | 55/100 | 10% |
| AI Search Readiness | 68/100 | 10% |
| Images | 70/100 | 5% |

## Technical SEO — 72/100

**What works**

- HTTPS with HSTS (max-age 63072000)
- Single canonical host, apex and http both 308 to https://www
- robots.txt correct, declares sitemap, images explicitly crawlable
- sitemap.xml valid, 216 URLs, every one returns 200
- Clean URLs via cleanUrls, no .html exposed anywhere
- 5,696 internal links, zero broken
- Genuine 404 for unknown paths

**Findings**

### [Critical] pga-tour.html canonicalises itself to /tournaments

pga-tour.html carries rel=canonical and og:url pointing at https://www.golfraw.com/tournaments. The page holds 92 PGA Tour articles and is linked from the main nav on all 227 pages, but it instructs Google to treat it as a duplicate of a different page. Left in place, /pga-tour drops out of the index and its link equity consolidates onto /tournaments. Introduced when the two pages were split apart; title, description and h1 were updated but the canonical was not.

**Fix:** Point both rel=canonical and og:url at https://www.golfraw.com/pga-tour.

### [Medium] Five security headers absent

Only strict-transport-security is set. x-content-type-options, x-frame-options, content-security-policy, referrer-policy and permissions-policy are all missing.

**Fix:** Add a headers block to vercel.json. Not a direct ranking factor, but part of Google's page-experience signals and trivially cheap here.

### [Low] Two-hop redirect from the http apex

http://golfraw.com/x redirects to https://golfraw.com/x and then to https://www.golfraw.com/x — two hops, both 308.

**Fix:** Collapse to a single hop straight to https://www. Minor crawl-budget saving.


## Content Quality — 84/100

**What works**

- Median 1,430 words per content page; zero thin pages under 300 words
- 100% of 196 content pages carry an author byline and published date
- 93% carry a modified date
- Full trust-page set live: about, contact, privacy, terms, corrections, manifesto, ratings-manual
- Distinctive editorial voice, genuinely differentiated from syndicated golf coverage

**Findings**

### [High] Almost no outbound citation

Only 2 of 196 content pages link to an external source. For a publisher making factual claims about tours, purses and results, unsourced assertion is a weak trustworthiness signal for both Google and AI answer engines, which prefer citable, corroborated material.

**Fix:** Link the primary source when citing a figure — tour sites, official releases, governing-body pages. Two or three per article is enough.

### [Medium] FAQ schema on only 10% of content

20 of 196 content pages carry FAQPage markup despite the house style already answering direct questions in prose.

**Fix:** Extend the FAQ block pattern already used on the tools to article templates.


## On-Page SEO — 76/100

**What works**

- Zero missing titles, descriptions, H1s or canonicals across 227 pages
- Exactly one H1 per page on 226 of 227
- Strong internal linking, 5,696 links with none broken
- Only one orphan page, and it is a deliberate redirect alias

**Findings**

### [Medium] 154 title tags exceed 60 characters

68% of pages have titles long enough that Google will truncate them in the SERP, so the differentiating tail of the headline is often the part that gets cut.

**Fix:** Front-load the distinctive phrase and keep titles near 55-60 characters. Prioritise the highest-traffic articles rather than rewriting all 154.

### [Low] 68 meta descriptions exceed 160 characters

30% of descriptions will be truncated or rewritten by Google.

**Fix:** Trim to 150-160 characters, leading with the hook.

### [Low] ratings.html has two H1 elements

Ambiguous primary heading on one page.

**Fix:** Demote the second to h2.


## Schema / Structured Data — 80/100

**What works**

- 244 JSON-LD blocks and zero parse errors
- NewsArticle on 163 pages, Article on 31 more
- FAQPage on 23, WebApplication on all 9 tools, NewsMediaOrganization and WebSite present

**Findings**

### [Medium] BreadcrumbList on 1 page of 227

Only the newest tool carries breadcrumb markup. The site has a clean two-level hierarchy that would qualify for breadcrumb rich results across every article and tool.

**Fix:** Add BreadcrumbList to the article and tool templates: Home > Section > Page.

### [Low] No ImageObject on article schema

NewsArticle blocks reference images as bare URLs rather than ImageObject with dimensions.

**Fix:** Upgrade to ImageObject with width and height to strengthen rich-result eligibility.


## Performance (CWV) — 55/100

**What works**

- Served over HTTP/2 from Vercel's CDN with cache HIT
- WebP throughout, lazy loading on grid images
- HTML compresses well — /news is 194 KB raw but 32 KB over the wire

**Findings**

### [Critical] Homepage ships roughly 5 MB

Measured live: 11 image requests totalling 2,448 KB plus a single 2,529 KB video, against 20 KB of HTML. Load completes at 3.5s with TTFB at 1,091ms. On mobile connections this is the dominant obstacle to a good LCP.

**Fix:** Drop the homepage video or load it behind an interaction; compress hero images to under 200 KB and serve responsive srcset.

### [High] 56 images exceed 400 KB

public/ totals 77.5 MB. The worst offenders are a 1.7 MB PNG and a 1.4 MB WebP, both with raw AI-export filenames, plus multiple article heroes near 1 MB.

**Fix:** Re-encode at quality 78-82 and cap hero width at 1600px. Most of these should land under 200 KB.

### [Info] No field data available

PageSpeed Insights returned a quota error and the browser did not expose paint timing, so LCP, INP and CLS could not be measured directly. Figures above are lab proxies.

**Fix:** Check Core Web Vitals in Search Console, which has field data this audit could not reach.


## AI Search Readiness — 68/100

**What works**

- No AI crawler is blocked — GPTBot, ClaudeBot, PerplexityBot and CCBot all permitted
- Direct-answer blocks on tool pages are well suited to extraction
- Clean semantic HTML with no JS-rendering dependency
- Strong entity signals via NewsMediaOrganization and consistent bylines

**Findings**

### [Medium] No llms.txt

The site publishes no /llms.txt, so AI crawlers get no curated guide to the highest-value content.

**Fix:** Publish /llms.txt listing the tools, pillar guides and section hubs. Note that Google Search ignores it; this targets other answer engines.

### [Medium] Citability limited by absent sourcing

AI answer engines preferentially cite material that itself cites sources. At 2 of 196 pages, the site reads as assertion rather than reporting.

**Fix:** Same fix as the E-E-A-T finding — outbound links to primary sources.


## Images — 70/100

**What works**

- Every image on all 227 pages has alt text — zero exceptions
- 221 of 227 assets are WebP
- Explicit width and height on card images, which protects CLS
- loading=lazy on grid thumbnails

**Findings**

### [High] Oversized and unoptimised assets

56 files over 400 KB across a 77.5 MB public directory, including two raw AI exports with spaces in their filenames.

**Fix:** Batch re-encode, rename the two AI exports to clean slugs, and audit whether the 2.5 MB webm earns its place.

