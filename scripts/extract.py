"""Shared metadata extraction for the GolfRaw article registry."""
import re, os, json

UTIL = {'index','search','news','guides','liv-golf','pga-tour','tournaments','analysis','vault',
'ratings','tools','about','contact','privacy','terms','corrections','manifesto','past-issues',
'article-template','full-board','the-card','ratings-manual'}
# match-play, strokes-gained and swing-guide are content pages, not utility chrome.

def meta(s, key, attr='name'):
    """Read a meta tag regardless of attribute order (both orders occur in this repo)."""
    k = re.escape(key)
    for pat in (r'<meta\s+%s="%s"\s+content="([^"]*)"' % (attr, k),
                r'<meta\s+content="([^"]*)"\s+%s="%s"' % (attr, k)):
        m = re.search(pat, s)
        if m:
            return m.group(1).strip()
    return ''

def unescape(t):
    for a,b in [('&amp;','&'),('&quot;','"'),('&#39;',"'"),('&lt;','<'),('&gt;','>'),('&nbsp;',' ')]:
        t = t.replace(a,b)
    return t.strip()

def slugs(root='.'):
    d = {f[:-5] for f in os.listdir(root) if f.endswith('.html')}
    return sorted(d - UTIL - {x for x in d if x.startswith('tools-')})

def categories(root='.'):
    """Authoritative category map from the live search index."""
    s = open(os.path.join(root,'search.html'), encoding='utf-8').read()
    out = {}
    for l, c in re.findall(r'l:"([^"]+)".*?cat:"([^"]*)"', s):
        out[l.lstrip('/')] = c.split('·')[-1].strip().upper()
    return out

def extract(slug, root='.', catmap=None):
    s = open(os.path.join(root, slug + '.html'), encoding='utf-8').read()
    title = meta(s,'og:title','property') or (re.search(r'<title>([^<]*)</title>', s) or [None,''])[1]
    title = unescape(re.sub(r'\s*[|—]\s*(GOLFRAW|GolfRaw|Raw Take).*$', '', title))
    img = meta(s,'og:image','property')
    if img.startswith('http'): img = '/' + img.split('/',3)[-1] if '//' in img else img
    if not img:
        m = re.search(r'<img[^>]+src="(/public/[^"]+\.webp)"', s)
        img = m.group(1) if m else ''
    date = meta(s,'article:published_time','property') or meta(s,'article:modified_time','property')
    canon = ''
    m = re.search(r'<link[^>]*rel="canonical"[^>]*>', s)
    if m:
        c = re.search(r'href="([^"]*)"', m.group(0))
        if c:
            canon = c.group(1).replace('https://www.golfraw.com', '')
    return {
        'canonical': canon,
        'alias_of': canon.lstrip('/') if canon and canon.lstrip('/') != slug else '',
        'slug': slug,
        'url': '/' + slug,
        'title': title,
        'excerpt': unescape(meta(s,'description') or meta(s,'og:description','property')),
        'category': (catmap or {}).get(slug,''),
        'date': date[:10] if date else '',
        'image': img,
    }
