#!/usr/bin/env python3
"""Apply (or check) the "Golf Vibe" theme layer across every HTML page.

Two things happen, both idempotent:

1. A managed block is inserted before </head>: preloads for the Inter and
   Plus Jakarta Sans variable
   fonts, the theme stylesheet, a one-line inline script that marks the
   document as JS-capable (so scroll reveals can hide below-the-fold content
   without ever hiding it from no-JS readers or crawlers) with a 2.5s
   fallback that forces everything visible, and the deferred behaviour script.
   Re-running replaces the block rather than stacking it.

2. Red colour literals that live outside the token system (inline style
   attributes, script strings, SVG strokes) are rewritten. Brand red becomes
   the green accent; red that meant "warning" becomes amber, so meaning is
   preserved while the palette is purged.

vercel.json serves .css/.js with a one-year immutable cache, so THEME_VER must
be bumped whenever theme-golf.css or theme-golf.js changes.
"""
import glob, io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THEME_VER = '5'
START, END = '<!-- THEME:START -->', '<!-- THEME:END -->'

BLOCK = f"""{START}
  <link rel="preload" href="/public/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/public/fonts/plus-jakarta-sans-var.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/public/theme-golf.css?v={THEME_VER}">
  <script>document.documentElement.classList.add('gr-js');setTimeout(function(){{document.documentElement.classList.add('gr-reveal-all')}},2500)</script>
  <script src="/public/theme-golf.js?v={THEME_VER}" defer></script>
{END}
"""

GREEN, AMBER = '#1F7A45', '#A85F06'
GREEN_RGBA, AMBER_RGBA = 'rgba(31,122,69', 'rgba(168,95,6'

# (pattern, replacement, flags). Order matters: specific cases first.
LITERALS = [
    # form error message colour is a warning, keep it semantic
    (r"style\.color\s*=\s*'#cc0000'", "style.color = '%s'" % AMBER, re.I),
    # newsletter block + any other inline red = brand accent
    (r'#cc0000', GREEN, re.I),
    # status cells like "Cancelled" / "Ending" = negative
    (r'#ef4444', AMBER, re.I),
    # light red on dark stat panels = light amber
    (r'#ff9486', '#F2C078', re.I),
    # the brand token definition itself
    (r'(--flag\s*:\s*)#e03e2d', r'\g<1>' + GREEN, re.I),
    # every remaining bare red literal is a swatch, marker or warning
    (r'#e03e2d', AMBER, re.I),
]


def apply(path, check=False):
    s = io.open(path, encoding='utf-8').read()
    orig = s
    if '</head>' not in s:
        return None
    s = re.sub(re.escape(START) + r'.*?' + re.escape(END) + r'\n?', '', s, flags=re.S)
    s = s.replace('</head>', BLOCK + '</head>', 1)
    for pat, rep, fl in LITERALS:
        s = re.sub(pat, rep, s, flags=fl)
    # ---- markup refinements (idempotent) ----
    # the wordmark stands alone: no header badge
    s = re.sub(r'\s*<span class="tag">NO PR REWRITES</span>', '', s)
    # the Method card is a data box, not a numbered list
    s = re.sub(r'\s*<span class="evidence-no">\d+</span>', '', s)
    # header search is an icon button; the text stays for screen readers
    s = re.sub(r'<a href="/search">(?:🔍\s*)?Search</a>',
               '<a href="/search" class="nav-search" aria-label="Search">Search</a>', s)
    # ---- editorial numbering purge ----
    # section index numbers ("04 Swing Analysis"), story catalog badges
    # ("A-12"), footer document codes ("P-01") and hub ordinals ("HUB 01 ·").
    # Patterns are shaped so genuine figures in <span class="n"> (stat cells,
    # percentages, section signs) are never touched.
    s = re.sub(r'\s*<span class="idx">[A-Z0-9]{1,3}</span>\s*', '', s)   # "04", "REL", "SEE" 
    s = re.sub(r'\s*<span class="n">[A-Z]-\d{2}</span>\s*', '', s)
    s = re.sub(r'<span class="fc-n">[A-Z]-\d{2}</span>', '', s)
    s = re.sub(r'(<span class="hub-no">)HUB\s+\d+\s*[·•-]\s*', r'\1', s)
    # Raw Guides: a balanced two-column grid instead of a forced single column
    s = s.replace('<div class="news-grid reveal" style="grid-template-columns: 1fr;">',
                  '<div class="news-grid guides-grid reveal">')
    # rgba red: warning banner in the handicap tool is amber, the rest is brand
    rgba_to = AMBER_RGBA if os.path.basename(path) == 'tools-handicap-detector.html' else GREEN_RGBA
    s = re.sub(r'rgba\(\s*224\s*,\s*62\s*,\s*45', rgba_to, s)
    if s != orig and not check:
        io.open(path, 'w', encoding='utf-8').write(s)
    return s != orig


def main():
    check = '--check' in sys.argv
    files = sorted(glob.glob(os.path.join(ROOT, '*.html')))
    changed = skipped = 0
    for p in files:
        r = apply(p, check)
        if r is None: skipped += 1
        elif r: changed += 1
    print('  %s %d page(s); %d unchanged; %d without </head> skipped'
          % ('would change' if check else 'themed', changed, len(files) - changed - skipped, skipped))
    return 0


if __name__ == '__main__':
    sys.exit(main())
