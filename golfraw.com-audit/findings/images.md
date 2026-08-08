# Images — 70/100

## What works

- Every image on all 227 pages has alt text — zero exceptions
- 221 of 227 assets are WebP
- Explicit width and height on card images, which protects CLS
- loading=lazy on grid thumbnails

## Findings

## [High] Oversized and unoptimised assets

56 files over 400 KB across a 77.5 MB public directory, including two raw AI exports with spaces in their filenames.

**Fix:** Batch re-encode, rename the two AI exports to clean slugs, and audit whether the 2.5 MB webm earns its place.

