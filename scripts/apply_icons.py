#!/usr/bin/env python3
"""Install the GolfRaw favicon set on every page (Google Search favicon guidelines).

Idempotent. For each HTML page:
  * removes every existing <link rel="icon"|"alternate icon"|"apple-touch-icon"|"manifest">
    and <meta name="theme-color"> line,
  * inserts the canonical ICON_BLOCK right after the viewport meta (or before </head>),
  * repoints every Organization/publisher logo ImageObject in JSON-LD from the old
    1254px favicon to /public/icon-512.png (object-level: parse, edit, re-dump).

The PNGs are served from the site root (copies of the /public originals);
vercel.json rewrites /favicon.ico onto the 48px PNG.

    python3 scripts/apply_icons.py [--check]
"""
import io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://www.golfraw.com'
LOGO_URL = SITE + '/icon-512.png'
LOGO_SIZE = 512
OLD_LOGOS = {SITE + '/public/favicon-192.webp', SITE + '/public/favicon-192.png',
             SITE + '/public/icon-512.png', '/public/favicon-192.webp', '/public/favicon-192.png'}

ICON_BLOCK = '''  <link rel="icon" type="image/png" sizes="48x48" href="/favicon-48x48.png">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">
  <meta name="theme-color" content="#166534">
'''

# attribute order varies between shell generations (rel first or href first)
OLD_LINE = re.compile(
    r'[ \t]*<link\b[^>]*\brel="(?:icon|alternate icon|apple-touch-icon|manifest|shortcut icon)"[^>]*>[ \t]*\n?'
    r'|[ \t]*<meta\b[^>]*\bname="theme-color"[^>]*>[ \t]*\n?', re.I)
VIEWPORT = re.compile(r'([ \t]*<meta\s+name="viewport"[^>]*>[ \t]*\n)', re.I)
JSON_LD = re.compile(r'(<script\b[^>]*type\s*=\s*["\']application/ld\+json["\'][^>]*>)(.*?)(</script\s*>)', re.S | re.I)


def fix_logo(node, changed):
    if isinstance(node, dict):
        for key, val in node.items():
            if key == 'logo' and isinstance(val, dict) and val.get('url') in OLD_LOGOS:
                val['url'] = LOGO_URL
                val['width'] = LOGO_SIZE
                val['height'] = LOGO_SIZE
                changed.append(1)
            elif key == 'logo' and isinstance(val, str) and val in OLD_LOGOS:
                node[key] = {'@type': 'ImageObject', 'url': LOGO_URL, 'width': LOGO_SIZE, 'height': LOGO_SIZE}
                changed.append(1)
            else:
                fix_logo(val, changed)
    elif isinstance(node, list):
        for item in node:
            fix_logo(item, changed)


def apply(path, check=False):
    s = io.open(path, encoding='utf-8').read()
    if '</head>' not in s:
        return None
    orig = s
    # ---- head icons ----
    s = OLD_LINE.sub('', s)
    if VIEWPORT.search(s):
        s = VIEWPORT.sub(lambda m: m.group(1) + ICON_BLOCK, s, count=1)
    else:
        s = s.replace('</head>', ICON_BLOCK + '</head>', 1)

    # ---- schema logo, object level ----
    def repl(m):
        try:
            doc = json.loads(m.group(2))
        except ValueError:
            return m.group(0)
        changed = []
        fix_logo(doc, changed)
        if not changed:
            return m.group(0)
        body = json.dumps(doc, indent=2, ensure_ascii=False).replace('</script>', '<\\/script>')
        return m.group(1) + '\n' + body + '\n  ' + m.group(3)   # same framing as schema_normalizer
    s = JSON_LD.sub(repl, s)

    if s != orig and not check:
        io.open(path, 'w', encoding='utf-8').write(s)
    return s != orig


def main():
    check = '--check' in sys.argv
    changed = same = 0
    for name in sorted(os.listdir(ROOT)):
        if not name.endswith('.html'):
            continue
        r = apply(os.path.join(ROOT, name), check)
        if r is None:
            continue
        if r:
            changed += 1
        else:
            same += 1
    print('  icons: %d page(s) %s; %d unchanged' % (changed, 'would change' if check else 'updated', same))


if __name__ == '__main__':
    main()
