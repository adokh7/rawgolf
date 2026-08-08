# Technical SEO — 72/100

## What works

- HTTPS with HSTS (max-age 63072000)
- Single canonical host, apex and http both 308 to https://www
- robots.txt correct, declares sitemap, images explicitly crawlable
- sitemap.xml valid, 216 URLs, every one returns 200
- Clean URLs via cleanUrls, no .html exposed anywhere
- 5,696 internal links, zero broken
- Genuine 404 for unknown paths

## Findings

## [Critical] pga-tour.html canonicalises itself to /tournaments

pga-tour.html carries rel=canonical and og:url pointing at https://www.golfraw.com/tournaments. The page holds 92 PGA Tour articles and is linked from the main nav on all 227 pages, but it instructs Google to treat it as a duplicate of a different page. Left in place, /pga-tour drops out of the index and its link equity consolidates onto /tournaments. Introduced when the two pages were split apart; title, description and h1 were updated but the canonical was not.

**Fix:** Point both rel=canonical and og:url at https://www.golfraw.com/pga-tour.

## [Medium] Five security headers absent

Only strict-transport-security is set. x-content-type-options, x-frame-options, content-security-policy, referrer-policy and permissions-policy are all missing.

**Fix:** Add a headers block to vercel.json. Not a direct ranking factor, but part of Google's page-experience signals and trivially cheap here.

## [Low] Two-hop redirect from the http apex

http://golfraw.com/x redirects to https://golfraw.com/x and then to https://www.golfraw.com/x — two hops, both 308.

**Fix:** Collapse to a single hop straight to https://www. Minor crawl-budget saving.

