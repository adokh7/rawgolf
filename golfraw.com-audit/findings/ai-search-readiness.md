# AI Search Readiness — 68/100

## What works

- No AI crawler is blocked — GPTBot, ClaudeBot, PerplexityBot and CCBot all permitted
- Direct-answer blocks on tool pages are well suited to extraction
- Clean semantic HTML with no JS-rendering dependency
- Strong entity signals via NewsMediaOrganization and consistent bylines

## Findings

## [Medium] No llms.txt

The site publishes no /llms.txt, so AI crawlers get no curated guide to the highest-value content.

**Fix:** Publish /llms.txt listing the tools, pillar guides and section hubs. Note that Google Search ignores it; this targets other answer engines.

## [Medium] Citability limited by absent sourcing

AI answer engines preferentially cite material that itself cites sources. At 2 of 196 pages, the site reads as assertion rather than reporting.

**Fix:** Same fix as the E-E-A-T finding — outbound links to primary sources.

