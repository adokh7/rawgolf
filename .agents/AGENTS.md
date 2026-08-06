# Workspace Rules

## Article Generation Rules
When creating or formatting a new article, you MUST strictly clone the exact DOM structure from a known-good article (e.g. `news-2026-what-beginners-actually-search.html` or `article-template.html`). 
- Do NOT invent new CSS classes.
- Do NOT use side-by-side grids or flexboxes for text.
- Do NOT change the DOM hierarchy. 
- You must strictly perform content insertion ONLY into the existing HTML wrappers.
- The standard layout must have the `<main>` tag containing `<div class="wrap page-grid">`, followed by `<article>`, and include the standard `<aside class="article-aside">` sidebar.
