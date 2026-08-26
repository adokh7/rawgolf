#!/usr/bin/env python3
"""Build articles.json — the single source of truth for GolfRaw articles.

Metadata comes from each article's own <head> (og:title, description,
article:published_time, og:image); category comes from the live search index,
with a keyword fallback for articles not yet indexed.
"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract import slugs, categories, extract

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Keyword fallback, only used when the search index has no category yet.
RULES = [
    ('LIV GOLF', r'\bliv\b|greg-norman|cam-smith|pieters-q-school'),
    ('GUIDES',   r'guide|how-to|how-far|what-is|what-does|what-to-wear|beginner|drills|'
                 r'swing|grip|distances|strokes-gained|witb|fitting|search|deals|topgolf|'
                 r'majors|mindset|explained|winners-list|rules'),
    ('PGA TOUR', r'.'),
]

# Within PGA TOUR, split event/major/venue coverage (tournaments.html) from
# tour news, results and players (pga-tour.html).
MAJOR = (r'us-open|the-open|open-championship|birkdale|masters|pga-championship|evian|'
         r'aig-womens-open|womens-open|lytham|solheim|ryder-cup|kpmg|shinnecock|sahalee|'
         r'major|course-guide|course-history|scorecard|yardage|setup|renovation|restoration|'
         r'renaissance-club|teugega|donald-ross|venue|tour-championship-odds-even-par')

def section(a):
    """Which category page owns this article."""
    if a['category'] != 'PGA TOUR':
        return a['category']
    return 'TOURNAMENTS' if re.search(MAJOR, a['slug']) else 'PGA TOUR'

# Explicit category overrides where the search-index tag is wrong.
# swing-guide is evergreen swing instruction, not tour news; it already sits
# on guides.html, so PGA TOUR left it cross-listed on two category pages.
OVERRIDES = {
    # Evergreen swing, drill and instructional content. These are how-to and
    # explainer pieces, not tour reporting, so PGA TOUR stays strictly news,
    # bubble updates and tournament results. analysis.html still curates the
    # swing collection from these — it is a section, not a category page.
    'swing-guide': 'GUIDES',
    'fix-over-the-top': 'GUIDES',
    'golf-swing-drills': 'GUIDES',
    'scottie-scheffler-footwork': 'GUIDES',
    'scheffler-swing': 'GUIDES',
    'scheffler-witb': 'GUIDES',
    'strokes-gained': 'GUIDES',
    'amateur-tournament-guide': 'GUIDES',
}

def fallback(slug, title):
    hay = (slug + ' ' + title).lower()
    for cat, pat in RULES:
        if re.search(pat, hay):
            return cat
    return 'PGA TOUR'

def existing_keywords():
    """Collect hand-written search keywords so a rebuild never destroys them.

    No article carries <meta name="keywords">, so these cannot be re-derived
    from the HTML. The only sources are the current registry and the current
    search index, both of which are hand-maintained. Registry wins on conflict.
    """
    kw = {}
    search = os.path.join(ROOT, 'search.html')
    if os.path.exists(search):
        s = open(search, encoding='utf-8').read()
        i = s.find('const ARTICLES = [')
        if i >= 0:
            for entry in re.findall(r'\{t:.*?\},', s[i:s.find('\n];', i)], re.S):
                slug = re.search(r'l:"([^"]+)"', entry)
                keys = re.search(r'k:"([^"]*)"', entry)
                if slug and keys and keys.group(1).strip():
                    kw[slug.group(1).lstrip('/')] = keys.group(1)
    reg = os.path.join(ROOT, 'articles.json')
    if os.path.exists(reg):
        try:
            for a in json.load(open(reg, encoding='utf-8'))['articles']:
                slug = a.get('slug') or a.get('url', '').lstrip('/')
                if slug and a.get('keywords', '').strip():
                    kw[slug] = a['keywords']
        except (ValueError, KeyError):
            pass
    return kw


def build():
    catmap = categories(ROOT)
    keywords = existing_keywords()
    arts, gaps = [], []
    for s in slugs(ROOT):
        a = extract(s, ROOT, catmap)
        a['keywords'] = keywords.get(s, '')
        if not a['category']:
            a['category'] = fallback(s, a['title'])
            a['category_source'] = 'keyword-fallback'
        else:
            a['category_source'] = 'search-index'
        missing = [k for k in ('title','excerpt','date','image') if not a[k]]
        if missing:
            gaps.append((s, missing))
        if a['slug'] in OVERRIDES:
            a['category'] = OVERRIDES[a['slug']]
            a['category_source'] = 'override'
        a['section'] = section(a)
        arts.append(a)
    arts.sort(key=lambda a: (a['date'] or '0000-00-00', a['slug']), reverse=True)
    return arts, gaps

if __name__ == '__main__':
    arts, gaps = build()
    out = {
        'generated': '2026-08-05',
        'count': len(arts),
        'categories': sorted({a['category'] for a in arts}),
        'sections': sorted({a['section'] for a in arts}),
        'articles': arts,
    }
    with open(os.path.join(ROOT, 'articles.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(f"articles.json: {len(arts)} articles")
    print(f"   keywords preserved: {sum(1 for a in arts if a['keywords'])}")
    from collections import Counter
    for c, n in Counter(a['category'] for a in arts).most_common():
        print(f"   {c:<10} {n}")
    print(f"\nfallback-categorised: {sum(1 for a in arts if a['category_source']=='keyword-fallback')}")
    print(f"INCOMPLETE METADATA: {len(gaps)}")
    for s, m in gaps[:20]:
        print(f"   {s}: missing {','.join(m)}")
