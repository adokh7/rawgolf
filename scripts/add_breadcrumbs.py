#!/usr/bin/env python3
"""Inject a valid BreadcrumbList into every content page that lacks one.

Idempotent: pages already carrying a BreadcrumbList anywhere are skipped, so
hand-built breadcrumbs (the newer articles, four tools) are never disturbed.
The trail is Home -> section hub -> page for routable sections, and
Home -> News -> page for sections with no hub of their own. Each block is a
standalone <script type="application/ld+json"> appended just before </head>.
"""
import html as _html
import io, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://www.golfraw.com'

# Only these sections have hub pages (mirrors SECTION_PAGE in sync_site.py).
HUB = {
    'GUIDES':      ('Guides', '/guides'),
    'LIV GOLF':    ('LIV Golf', '/liv-golf'),
    'PGA TOUR':    ('PGA Tour', '/pga-tour'),
    'TOURNAMENTS': ('Tournaments', '/tournaments'),
}

TOOLS = ('Tools', '/tools')


def block(trail):
    items = [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + u}
             for i, (n, u) in enumerate(trail)]
    d = {'@context': 'https://schema.org', '@type': 'BreadcrumbList',
         'itemListElement': items}
    return ('  <script type="application/ld+json">\n'
            + json.dumps(d, indent=2, ensure_ascii=False) + '\n  </script>\n')


def inject(path, trail):
    s = io.open(path, encoding='utf-8').read()
    if 'BreadcrumbList' in s:
        return False
    i = s.find('</head>')
    if i == -1:
        print('  !! no </head> in', os.path.basename(path)); return False
    s = s[:i] + block(trail) + s[i:]
    io.open(path, 'w', encoding='utf-8').write(s)
    return True


def main():
    reg = json.load(io.open(os.path.join(ROOT, 'articles.json'), encoding='utf-8'))
    done = skipped = 0
    for a in reg['articles']:
        if a.get('alias_of'):
            continue
        path = os.path.join(ROOT, a['slug'] + '.html')
        if not os.path.exists(path):
            continue
        sec = a.get('section') or ''
        mid = HUB.get(sec, ('News', '/news'))
        trail = [('Home', '/'), mid, (a['title'], a['canonical'])]
        if inject(path, trail):
            done += 1
        else:
            skipped += 1
    # tool pages without breadcrumbs
    import glob, re
    for path in sorted(glob.glob(os.path.join(ROOT, 'tools-*.html'))):
        s = io.open(path, encoding='utf-8').read()
        if 'BreadcrumbList' in s:
            skipped += 1; continue
        m = re.search(r'<title>([^<|]+)', s)
        # <title> text arrives entity-encoded; JSON-LD wants plain text.
        name = _html.unescape(m.group(1).strip()) if m else os.path.basename(path)[:-5]
        slug = '/' + os.path.basename(path)[:-5]
        if inject(path, [('Home', '/'), TOOLS, (name, slug)]):
            done += 1
    print('  injected: %d | already had one: %d' % (done, skipped))
    return 0


if __name__ == '__main__':
    sys.exit(main())
