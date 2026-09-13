#!/usr/bin/env python3
"""One brand spelling everywhere: GolfRaw.

Google's Site Names system chooses a name from the homepage WebSite markup,
og:site_name, the <title> and headings, and falls back to the bare domain when
those disagree. This site carried GOLFRAW, GolfRaw, Golf Raw and RawGolf side
by side. This pass (idempotent) rewrites every page so that:

  * visible text and head metadata (outside <script>/<style>) use "GolfRaw"
    ("GolfRaw Editorial", "GolfRaw Pro" for the entities that carry a suffix);
  * every JSON-LD string value that names the brand uses the same spelling,
    edited at the object level, with the legacy spellings kept as alternateName
    on WebSite and Organization nodes so Google can reconcile old citations;
  * og:site_name is "GolfRaw" and an application-name meta is present.

    python3 scripts/apply_brand.py [--check]
"""
import io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND = 'GolfRaw'
LEGACY = ['GOLFRAW', 'Golf Raw']

# order matters: multi-word entities first, then bare tokens
TOKENS = [
    ('GOLFRAW EDITORIAL STAFF', 'GolfRaw Editorial Staff'),
    ('GOLFRAW Editorial Staff', 'GolfRaw Editorial Staff'),
    ('Golf Raw Editorial Staff', 'GolfRaw Editorial Staff'),
    ('Golf Raw Editorial Board', 'GolfRaw Editorial Board'),
    ('GOLFRAW EDITORIAL', 'GolfRaw Editorial'),
    ('GOLFRAW Editorial', 'GolfRaw Editorial'),
    ('Golf Raw Editorial', 'GolfRaw Editorial'),
    ('Golf Raw Pro', 'GolfRaw Pro'),
    ('GOLFRAW PRO', 'GolfRaw Pro'),
    ('GOLF RAW', BRAND),
    ('GOLFRAW', BRAND),
    ('Golf Raw', BRAND),
    ('RawGolf', BRAND),
    ('RAWGOLF', BRAND),
    ('Raw Golf', BRAND),
]
_B = r'(?<![A-Za-z0-9_-])%s(?![A-Za-z0-9_-])'
TOKEN_RES = [(re.compile(_B % re.escape(a)), b) for a, b in TOKENS]
URL_KEYS = {'@id', '@type', '@context', 'url', 'contentUrl', 'urlTemplate', 'target', 'sameAs',
            'thumbnailUrl', 'embedUrl', 'item', 'mainEntityOfPage', 'image', 'logo'}
SPLIT = re.compile(r'(<script\b.*?</script>|<style\b.*?</style>)', re.S | re.I)
JSON_LD = re.compile(r'(<script\b[^>]*type\s*=\s*["\']application/ld\+json["\'][^>]*>)(.*?)(</script\s*>)', re.S | re.I)


def fix_text(s):
    for rx, rep in TOKEN_RES:
        s = rx.sub(rep, s)
    return s


def fix_node(node, key=None):
    if isinstance(node, dict):
        for k, v in list(node.items()):
            node[k] = fix_node(v, k)
        t = node.get('@type')
        types = {t} if isinstance(t, str) else set(t or [])
        # the site-level publisher entity is the brand itself; "Editorial" is an alias
        if str(node.get('@id', '')).endswith('#organization') and node.get('name') in (BRAND + ' Editorial', 'GOLFRAW Editorial'):
            node['name'] = BRAND
            node['alternateName'] = list(node.get('alternateName') or []) + [BRAND + ' Editorial']
        site_entity = 'WebSite' in types or str(node.get('@id', '')).endswith('#organization')
        if not site_entity and types & {'Organization', 'NewsMediaOrganization'} and node.get('alternateName') == LEGACY:
            del node['alternateName']   # nested publisher references stay minimal (matches the generators)
        if site_entity and types & {'WebSite', 'Organization', 'NewsMediaOrganization'} and node.get('name') == BRAND:
            alt = node.get('alternateName')
            alt = [alt] if isinstance(alt, str) else list(alt or [])
            seen, clean = set(), []
            for a in alt + LEGACY:
                if a == BRAND or a in seen:
                    continue
                seen.add(a); clean.append(a)
            node['alternateName'] = clean
        return node
    if isinstance(node, list):
        return [fix_node(x, key) for x in node]
    if key == 'alternateName':
        return node   # legacy spellings are kept verbatim so Google can reconcile them
    if isinstance(node, str) and key not in URL_KEYS and not node.startswith(('http://', 'https://', '/')):
        return fix_text(node)
    return node


def apply(path, check=False):
    s = io.open(path, encoding='utf-8').read()
    if '</head>' not in s:
        return None
    orig = s
    # ---- text and head metadata, skipping scripts and styles ----
    parts = SPLIT.split(s)
    parts = [p if SPLIT.fullmatch(p) else fix_text(p) for p in parts]
    s = ''.join(parts)
    # ---- JSON-LD, object level ----
    def repl(m):
        try:
            doc = json.loads(m.group(2))
        except ValueError:
            return m.group(0)
        new = fix_node(doc)
        body = json.dumps(new, indent=2, ensure_ascii=False).replace('</script>', '<\\/script>')
        if json.dumps(doc, sort_keys=True) == json.dumps(json.loads(m.group(2)), sort_keys=True) and body.strip() == m.group(2).strip():
            return m.group(0)
        return m.group(1) + '\n' + body + '\n  ' + m.group(3)
    s = JSON_LD.sub(repl, s)
    # ---- site name metadata ----
    s = re.sub(r'<meta property="og:site_name" content="[^"]*">', '<meta property="og:site_name" content="%s">' % BRAND, s)
    if 'name="application-name"' not in s:
        if '<meta property="og:site_name"' in s:
            s = s.replace('<meta property="og:site_name" content="%s">' % BRAND,
                          '<meta property="og:site_name" content="%s">\n  <meta name="application-name" content="%s">' % (BRAND, BRAND), 1)
        else:
            s = s.replace('</head>', '  <meta property="og:site_name" content="%s">\n  <meta name="application-name" content="%s">\n</head>' % (BRAND, BRAND), 1)
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
        changed += bool(r); same += (not r)
    print('  brand: %d page(s) %s; %d unchanged' % (changed, 'would change' if check else 'updated', same))


if __name__ == '__main__':
    main()
