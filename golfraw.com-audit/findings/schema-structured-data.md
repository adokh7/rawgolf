# Schema / Structured Data — 80/100

## What works

- 244 JSON-LD blocks and zero parse errors
- NewsArticle on 163 pages, Article on 31 more
- FAQPage on 23, WebApplication on all 9 tools, NewsMediaOrganization and WebSite present

## Findings

## [Medium] BreadcrumbList on 1 page of 227

Only the newest tool carries breadcrumb markup. The site has a clean two-level hierarchy that would qualify for breadcrumb rich results across every article and tool.

**Fix:** Add BreadcrumbList to the article and tool templates: Home > Section > Page.

## [Low] No ImageObject on article schema

NewsArticle blocks reference images as bare URLs rather than ImageObject with dimensions.

**Fix:** Upgrade to ImageObject with width and height to strengthen rich-result eligibility.

