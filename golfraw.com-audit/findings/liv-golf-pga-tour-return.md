# Article SEO audit: LIV Golf players return to PGA Tour

**URL:** `/liv-golf-pga-tour-return`  
**Audit date:** 26 August 2026  
**Scope:** Static HTML, source index, generated hubs, sitemap, RSS and supplied research handoff.

## Result

The article is publishable from a technical, on-page, content and structured-data perspective. The page is server-rendered HTML with one H1, seven question-form H2 sections, a 154-character meta description, a clean canonical and a complete JSON-LD graph. The target query appears in the title, H1, first 100 words and a question H2.

The focused content review scored content quality at **86/100**, E-E-A-T at **74/100** and AI citation readiness at **92/100**. The main E-E-A-T limitation is the supplied author credential gap, which is disclosed on the page.

## Evidence checked

- `articles.json` contains the article and routes it to the LIV GOLF section.
- `index.html`, `news.html`, `liv-golf.html`, `search.html`, `sitemap.xml` and `feed.xml` expose the new URL.
- The page has one `NewsArticle`, one `WebPage`, one `BreadcrumbList`, one `Organization`, one `WebSite` and one `FAQPage` node.
- The five visible FAQ pairs match the five JSON-LD questions and answers exactly.
- The supplied research constraints are visible in the article: BC Partners Credit remains unconfirmed, the BBC URL returned HTTP 403 and is excluded, CNN was read through licensed syndication, and no Reddit or forum evidence is presented.
- The 49.5 percent purse reduction is shown as arithmetic from the published Indianapolis figures.
- The article has seven HTTPS source links and three contextual internal links.
- The hero is a WebP with explicit dimensions, responsive `srcset`/`sizes`, and high fetch priority. Both wide tables sit in touch-scrollable, keyboard-focusable regions.

## Quality and AEO checks

- Answer-first paragraphs follow every question section.
- A scannable takeaway block, eligibility table, purse table, timeline, criteria list, verification block and FAQ section support extraction and mobile scanning.
- Four short definition sentences and more than five standalone quotable facts are present.
- Sentence-length spread meets the humanization target, with short and long sentences mixed through the article.
- No em dashes, semicolon-led prose, placeholder text or unsupported Wikidata/sameAs values remain in the article.

## Remaining notes

1. The hero source is a 1024x1024 archive image. HTML, Open Graph and JSON-LD now declare the same square dimensions. A purpose-built 1200x675 crop would improve social previews when an approved asset is available.
2. RSS uses the article's publication date because `articles.json` stores dates without times. The new item is aligned manually to the page's 15:53 UTC publication timestamp.
3. FAQPage remains useful for semantic and answer-engine context. Google FAQ rich-result visibility is not an expected benefit for a general publisher page.
4. A local HTTP server and live host request were unavailable in the sandbox during this pass, so no Lighthouse, CrUX, GSC or production status code was claimed here. The existing site-wide audit contains those limitations and broader findings.

## Status

**PASS — ready for editorial review and normal publication checks.**
