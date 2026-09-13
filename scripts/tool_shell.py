"""Marker-based extraction of the shared tool-page shell.

The generated tools (Standing Order, Tendency Engine, Field Reader) lift their
head, header, footer and behaviour scripts from tools-bag-audit.html. The
builders used to slice that file by line number, which silently broke the
moment wire_locker.py and apply_theme.py injected their managed blocks into
the shell: every rebuild would have produced a page with no </head>, no <body>
and no tool CSS. Markers do not drift; line numbers do.

The managed LOCKER and THEME blocks are stripped from every part on purpose.
The wiring scripts are idempotent and re-inject them after a rebuild, so a
builder must never bake a stale copy in.
"""
import io
import re

MANAGED = re.compile(r'\s*<!-- (LOCKER|THEME):START -->.*?<!-- \1:END -->\n?', re.S)


def _between(text, start_pat, end_pat, inclusive_end=True, label=''):
    a = re.search(start_pat, text)
    if not a:
        raise RuntimeError('shell marker not found: %s (%s)' % (start_pat, label))
    b = re.search(end_pat, text[a.start():])
    if not b:
        raise RuntimeError('shell end marker not found: %s (%s)' % (end_pat, label))
    end = a.start() + (b.end() if inclusive_end else b.start())
    return text[a.start():end]


def shell_parts(shell_path):
    src = io.open(shell_path, encoding='utf-8').read()
    src = MANAGED.sub('\n', src)

    head_top = src[:src.index('  <!-- ============ STRUCTURED DATA')].rstrip('\n')
    head_tail = _between(src, r'<!-- ============ FONTS', r'</head>', label='head_tail')
    # add_breadcrumbs.py appends the shell's OWN BreadcrumbList before </head>;
    # every generated tool declares its own, so the Bag Audit's must not leak.
    head_tail = re.sub(r'\s*<script type="application/ld\+json">\s*\{[^<]*?"@type":\s*"BreadcrumbList"[^<]*?</script>\n?', '\n', head_tail, flags=re.S)
    body_open = _between(src, r'<body[^>]*>', r'</header>', label='body_open')
    footer = _between(src, r'  <footer\b', r'</footer>', label='footer')

    # First inline script after the footer is the burger / mobile-nav behaviour.
    after_footer = src[src.index('</footer>'):]
    # The NAV behaviour is one IIFE at the top of the shell's tool script, not a
    # script of its own, so lift the IIFE and wrap it: the rest of that script
    # is the Bag Audit's own logic and must never ride along.
    nav_iife = _between(after_footer, r'/\* =+ NAV =+ \*/', r'\n    \}\)\(\);', label='nav_script')
    nav_script = '  <script>\n    ' + nav_iife + '\n  </script>'
    gtag = '  ' + _between(after_footer, r'<script>\n\s*window\.dataLayer', r'</script>', label='gtag')

    return {
        'head_top': head_top,
        'head_tail': head_tail,
        'body_open': body_open,
        'footer': footer,
        'nav_script': nav_script,   # complete <script>…</script> block
        'gtag': gtag,               # complete <script>…</script> block
    }
