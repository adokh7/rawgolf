# GolfRaw — Prioritised Action Plan

Health Score 74/100. Ordered by impact per unit of effort.

## Phase 1: Critical Fixes (Today)

- [ ] Point pga-tour.html rel=canonical and og:url at /pga-tour
- [ ] Remove or defer the 2.5 MB homepage video
- [ ] Compress the 10 largest images

## Phase 2: High-Impact Improvements (Weeks 2-3)

- [ ] Batch-compress the remaining 46 oversized images and rename the two AI exports
- [ ] Add BreadcrumbList JSON-LD to article and tool templates
- [ ] Add the 5 missing security headers to vercel.json
- [ ] Trim the 40 longest title tags on the highest-traffic articles

## Phase 3: Content & Authority (Month 2)

- [ ] Introduce an outbound-citation habit: 2-3 primary sources per article
- [ ] Extend FAQ schema from the tools to article templates
- [ ] Publish /llms.txt
- [ ] Submit the sitemap in Search Console — the 9 tool pages have never been crawled

## Phase 4: Monitoring & Iteration (Ongoing)

- [ ] Run scripts/sync_site.py --check in CI to catch registry and doc drift
- [ ] Watch Core Web Vitals in Search Console for real LCP once images are fixed
- [ ] Re-audit after the image work lands

## All findings by severity

| Severity | Category | Finding |
|---|---|---|
| Critical | Technical SEO | pga-tour.html canonicalises itself to /tournaments |
| Critical | Performance (CWV) | Homepage ships roughly 5 MB |
| High | Content Quality | Almost no outbound citation |
| High | Performance (CWV) | 56 images exceed 400 KB |
| High | Images | Oversized and unoptimised assets |
| Medium | Technical SEO | Five security headers absent |
| Medium | Content Quality | FAQ schema on only 10% of content |
| Medium | On-Page SEO | 154 title tags exceed 60 characters |
| Medium | Schema / Structured Data | BreadcrumbList on 1 page of 227 |
| Medium | AI Search Readiness | No llms.txt |
| Medium | AI Search Readiness | Citability limited by absent sourcing |
| Low | Technical SEO | Two-hop redirect from the http apex |
| Low | On-Page SEO | 68 meta descriptions exceed 160 characters |
| Low | On-Page SEO | ratings.html has two H1 elements |
| Low | Schema / Structured Data | No ImageObject on article schema |
| Info | Performance (CWV) | No field data available |
