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
THEME_VER = '10'
START, END = '<!-- THEME:START -->', '<!-- THEME:END -->'

BLOCK = f"""{START}
  <link rel="preload" href="/public/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/public/fonts/plus-jakarta-sans-var.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/public/theme-golf.css?v={THEME_VER}">
  <script>document.documentElement.classList.add('gr-js');setTimeout(function(){{document.documentElement.classList.add('gr-reveal-all')}},2500)</script>
  <script src="/public/theme-golf.js?v={THEME_VER}" defer></script>
{END}
"""

LOGO_MARKUP = ('<a href="/" class="logo" aria-label="GolfRaw home">'
               '<img src="/logo.png" alt="GolfRaw" width="500" height="109" decoding="async" fetchpriority="high"></a>')

GREEN, AMBER, LIGHT_AMBER = '#147a3b', '#b45309', '#fcd34d'
GREEN_RGBA, AMBER_RGBA = 'rgba(20,122,59', 'rgba(180,83,9'

# (pattern, replacement, flags). Order matters: specific cases first.
LITERALS = [
    # form error message colour is a warning, keep it semantic
    (r"style\.color\s*=\s*'#cc0000'", "style.color = '%s'" % AMBER, re.I),
    # newsletter block + any other inline red = brand accent
    (r'#cc0000', GREEN, re.I),
    # status cells like "Cancelled" / "Ending" = negative
    (r'#ef4444', AMBER, re.I),
    # light red on dark stat panels = light amber
    (r'#ff9486', LIGHT_AMBER, re.I),
    # the brand token definition itself
    (r'(--flag\s*:\s*)#e03e2d', r'\g<1>' + GREEN, re.I),
    # every remaining bare red literal is a swatch, marker or warning
    (r'#e03e2d', AMBER, re.I),
    # v8 palette: the previous theme's literals move to the slate/green scale
    (r'#1F7A45', GREEN, re.I),
    (r'#A85F06', AMBER, re.I),
    (r'#F2C078', LIGHT_AMBER, re.I),
    # v8 palette: every literal the pre-theme shells hardcoded, mapped onto the slate/green scale
    (r'#F3F4F0(?![0-9a-f])', '#f8fafc', re.I),
    (r'#101511(?![0-9a-f])', '#0f172a', re.I),
    (r'#181c1a(?![0-9a-f])', '#0f172a', re.I),
    (r'#5B665E(?![0-9a-f])', '#475569', re.I),
    (r'#626a66(?![0-9a-f])', '#475569', re.I),
    (r'#8b958d(?![0-9a-f])', '#94a3b8', re.I),
    (r'#14402A(?![0-9a-f])', '#166534', re.I),
    (r'#0f392b(?![0-9a-f])', '#166534', re.I),
    (r'#0B2418(?![0-9a-f])', '#0f172a', re.I),
    (r'#0a2a20(?![0-9a-f])', '#0f172a', re.I),
    (r'#DADDD4(?![0-9a-f])', '#e2e8f0', re.I),
    (r'#D7DAD2(?![0-9a-f])', '#e2e8f0', re.I),
    (r'#e4e4e1(?![0-9a-f])', '#e2e8f0', re.I),
    (r'#d3d5d1(?![0-9a-f])', '#cbd5e1', re.I),
    (r'#9CC9AE(?![0-9a-f])', '#cbd5e1', re.I),
    (r'#CFE3D6(?![0-9a-f])', '#cbd5e1', re.I),
    (r'#b9d2c2(?![0-9a-f])', '#cbd5e1', re.I),
    (r'#b8d2c5(?![0-9a-f])', '#cbd5e1', re.I),
    (r'#c8d2c9(?![0-9a-f])', '#cbd5e1', re.I),
    (r'#6FDB9A(?![0-9a-f])', '#86efac', re.I),
    (r'#9fe6b8(?![0-9a-f])', '#86efac', re.I),
    (r'#f0c674(?![0-9a-f])', '#fbbf24', re.I),
    (r'#a8aea3(?![0-9a-f])', '#94a3b8', re.I),
    (r'#9aa59d(?![0-9a-f])', '#94a3b8', re.I),
    (r'#344139(?![0-9a-f])', '#475569', re.I),
    (r'#f0a79f(?![0-9a-f])', '#fcd34d', re.I),
    (r'#e7f0eb(?![0-9a-f])', '#f0fdf4', re.I),
    (r'#e7f6ee(?![0-9a-f])', '#f0fdf4', re.I),
    (r'#1a221b(?![0-9a-f])', '#1e293b', re.I),
    (r'#2e8b67(?![0-9a-f])', GREEN, re.I),
    # v9: the interactive green darkens one step so it clears 4.8:1 on the canvas
    (r'#15803d(?![0-9a-f])', GREEN, re.I),
    (r'#b43b31(?![0-9a-f])', '#b45309', re.I),
    (r'#fff0ed(?![0-9a-f])', '#fffbeb', re.I),
    (r'#fff4dd(?![0-9a-f])', '#fffbeb', re.I),
    (r'#fff6f4(?![0-9a-f])', '#fffbeb', re.I),
    (r'#111(?![0-9a-f])', '#0f172a', re.I),
    (r'#101010(?![0-9a-f])', '#0f172a', re.I),
    # v9 typography: the shells' mono metadata stacks become the Inter meta layer
    (r'''['"]IBM Plex Mono['"]\s*,\s*(?:ui-monospace\s*,\s*)?monospace''', 'var(--gr-meta, Inter, system-ui, sans-serif)', 0),
    # the shells' Archivo body stacks: the theme renders Inter, so the face must not be requested
    (r'''['"]Archivo['"]\s*,\s*(?:system-ui\s*,\s*)?sans-serif''', 'var(--gr-sans, Inter, system-ui, sans-serif)', 0),
    (r'#aaa(?![0-9a-f])', '#94a3b8', re.I),
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
    # the header home link carries the official wordmark image (text wordmark -> /logo.png)
    s = re.sub(r'<a\b[^>]*\bclass="logo"[^>]*>\s*(?:Golf|GOLF)\s*<span[^>]*>\s*(?:Raw|RAW)\s*</span>\s*</a>',
               LOGO_MARKUP, s)
    # intrinsic dimensions on the wordmark image (500x109); CSS sets the rendered height
    s = re.sub(r'<img src="/logo.png" alt="GolfRaw" width="\d+" height="\d+"', '<img src="/logo.png" alt="GolfRaw" width="500" height="109"', s)
    # the mono face is no longer used by any rule, so its preload is dead weight
    s = re.sub(r'\s*<link rel="preload" href="/public/fonts/ibm-plex-mono-[^"]*" as="font" type="font/woff2" crossorigin>', '', s)
    s = re.sub(r'\s*<link rel="preload" href="/public/fonts/archivo-var\.woff2" as="font" type="font/woff2" crossorigin>', '', s)
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
    # v7 rgba literals written by the previous palette
    s = re.sub(r'rgba\(\s*31\s*,\s*122\s*,\s*69', GREEN_RGBA, s)
    s = re.sub(r'rgba\(\s*168\s*,\s*95\s*,\s*6\b', AMBER_RGBA, s)
    s = re.sub(r'rgba\(\s*21\s*,\s*128\s*,\s*61', GREEN_RGBA, s)
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
