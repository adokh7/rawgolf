#!/usr/bin/env python3
"""Keep the site consistent with articles.json (the single source of truth).

  python3 scripts/sync_site.py --check    # report drift, exit 1 if any (use in CI)
  python3 scripts/sync_site.py            # report drift AND regenerate sitemap.xml

Grids and search.html are *checked*, not overwritten, so hand-curated ordering,
hero blocks and per-entry keywords survive. Anything missing is reported so it
can be placed deliberately.
"""
import sys, os, re, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECTION_PAGE = {'GUIDES':'guides.html','LIV GOLF':'liv-golf.html',
                'PGA TOUR':'pga-tour.html','TOURNAMENTS':'tournaments.html'}
STATIC = ['/', '/news', '/guides', '/liv-golf', '/pga-tour', '/tournaments',
          '/vault', '/ratings', '/tools', '/analysis', '/about', '/contact']

def load():
    d = json.load(open(os.path.join(ROOT,'articles.json'), encoding='utf-8'))
    return [a for a in d['articles'] if not a.get('alias_of')]

def links(page):
    s = open(os.path.join(ROOT,page), encoding='utf-8').read()
    return {h.lstrip('/').split('#')[0].split('?')[0] for h in re.findall(r'href="([^"]+)"', s)}

def search_index():
    s = open(os.path.join(ROOT,'search.html'), encoding='utf-8').read()
    i = s.index('const ARTICLES = [')
    return {m.lstrip('/') for m in re.findall(r'l:"([^"]+)"', s[i:s.index('\n];', i)])}

def check(arts):
    problems = []
    news, idx = links('news.html'), search_index()
    for a in arts:
        if a['slug'] not in news:
            problems.append(('news.html missing', a['slug']))
        if a['slug'] not in idx:
            problems.append(('search.html missing', a['slug']))
        page = SECTION_PAGE.get(a['section'])
        if page and a['slug'] not in links(page):
            problems.append((f'{page} missing', a['slug']))
        img = a['image'].split('?')[0]
        if not img or not os.path.exists(os.path.join(ROOT, img.lstrip('/'))):
            problems.append(('image missing', f"{a['slug']} -> {a['image']}"))
        if not os.path.exists(os.path.join(ROOT, a['slug'] + '.html')):
            problems.append(('page missing', a['slug']))
    known = {a['slug'] for a in arts}
    for ghost in idx - known:
        problems.append(('search.html has unknown entry', ghost))
    # cross-contamination between the two PGA pages
    overlap = links('pga-tour.html') & links('tournaments.html') & known
    for o in sorted(overlap):
        problems.append(('on both pga-tour and tournaments', o))
    return problems

def write_sitemap(arts):
    base = 'https://www.golfraw.com'
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">', '']
    out += [f'  <url>\n    <loc>{base}/</loc>\n    <changefreq>daily</changefreq>'
            f'\n    <priority>1.0</priority>\n  </url>']
    for u in STATIC[1:]:
        out.append(f'  <url>\n    <loc>{base}{u}</loc>\n    <changefreq>daily</changefreq>'
                   f'\n    <priority>0.8</priority>\n  </url>')
    for a in sorted(arts, key=lambda x: x['date'], reverse=True):
        out.append(f'  <url>\n    <loc>{base}{a["url"]}</loc>\n    <lastmod>{a["date"]}</lastmod>'
                   f'\n    <priority>0.9</priority>\n  </url>')
    out += ['</urlset>', '']
    open(os.path.join(ROOT,'sitemap.xml'),'w',encoding='utf-8').write('\n'.join(out))
    return len(arts) + len(STATIC)

if __name__ == '__main__':
    arts = load()
    probs = check(arts)
    print(f"registry: {len(arts)} articles")
    if probs:
        print(f"DRIFT: {len(probs)} problem(s)")
        for kind, what in probs[:40]:
            print(f"   [{kind}] {what}")
    else:
        print("DRIFT: none — grids, search and images all consistent")
    if '--check' in sys.argv:
        sys.exit(1 if probs else 0)
    n = write_sitemap(arts)
    print(f"sitemap.xml regenerated: {n} URLs")
