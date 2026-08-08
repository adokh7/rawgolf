# Performance (CWV) — 55/100

## What works

- Served over HTTP/2 from Vercel's CDN with cache HIT
- WebP throughout, lazy loading on grid images
- HTML compresses well — /news is 194 KB raw but 32 KB over the wire

## Findings

## [Critical] Homepage ships roughly 5 MB

Measured live: 11 image requests totalling 2,448 KB plus a single 2,529 KB video, against 20 KB of HTML. Load completes at 3.5s with TTFB at 1,091ms. On mobile connections this is the dominant obstacle to a good LCP.

**Fix:** Drop the homepage video or load it behind an interaction; compress hero images to under 200 KB and serve responsive srcset.

## [High] 56 images exceed 400 KB

public/ totals 77.5 MB. The worst offenders are a 1.7 MB PNG and a 1.4 MB WebP, both with raw AI-export filenames, plus multiple article heroes near 1 MB.

**Fix:** Re-encode at quality 78-82 and cap hero width at 1600px. Most of these should land under 200 KB.

## [Info] No field data available

PageSpeed Insights returned a quota error and the browser did not expose paint timing, so LCP, INP and CLS could not be measured directly. Figures above are lab proxies.

**Fix:** Check Core Web Vitals in Search Console, which has field data this audit could not reach.

