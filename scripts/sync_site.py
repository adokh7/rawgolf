#!/usr/bin/env python3
"""Keep the site consistent with articles.json (the single source of truth).

  python3 scripts/sync_site.py --check    # report drift, exit 1 if any (use in CI)
  python3 scripts/sync_site.py            # rebuild all grids, search, and sitemap

Regenerates: news.html, liv-golf.html, pga-tour.html, guides.html,
             tournaments.html, search.html grids, and sitemap.xml.
"""
import sys, os, re, json, html as html_mod

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Maps article "section" (or "category") to the category page file
SECTION_PAGE = {
    'GUIDES':      'guides.html',
    'LIV GOLF':    'liv-golf.html',
    'PGA TOUR':    'pga-tour.html',
    'TOURNAMENTS': 'tournaments.html',
}

# Pages that use the news-grid card format (article.news)
NEWS_GRID_PAGES = {'news.html', 'liv-golf.html'}

# Pages that use the guide-grid card format (a.guide-card)
GUIDE_GRID_PAGES = {'pga-tour.html', 'guides.html', 'tournaments.html'}

STATIC = ['/', '/news', '/guides', '/liv-golf', '/pga-tour', '/tournaments',
          '/vault', '/ratings', '/tools', '/analysis', '/about', '/contact']

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load():
    d = json.load(open(os.path.join(ROOT, 'articles.json'), encoding='utf-8'))
    return [a for a in d['articles'] if not a.get('alias_of')]


def esc(s):
    """HTML-escape a string for safe insertion."""
    return html_mod.escape(s, quote=True)


def get_title(a):
    return a.get('title', '')


def get_excerpt(a):
    return a.get('snippet') or a.get('excerpt') or ''


def get_date(a):
    return a.get('date', '')


def get_url(a):
    return a.get('url', '')


def get_image(a):
    return a.get('image', '')


def get_category(a):
    return a.get('category', '')


def get_section(a):
    """Return the section for routing. Falls back to category."""
    return a.get('section') or a.get('category') or ''


def get_keywords(a):
    return a.get('keywords', '')


# ---------------------------------------------------------------------------
# Card generators
# ---------------------------------------------------------------------------

def news_card(a):
    """Generate an <article class="news"> card for news.html / liv-golf.html."""
    return f'''        <article class="news">
          <a href="{esc(get_url(a))}" style="display:block; margin-bottom:16px;">
            <img src="{esc(get_image(a))}" alt="{esc(get_title(a))}" style="width: 100%; border-radius: 4px;" loading="lazy">
          </a>
          <div class="cat" style="display:flex;align-items:center;gap:8px;">
            <span>{esc(get_category(a))}</span>
          </div>
          <h3><a href="{esc(get_url(a))}">{esc(get_title(a))}</a></h3>
          <p>{esc(get_excerpt(a))}</p>
          <div class="meta"><span>BY GOLFRAW Editorial</span><span class="mono">{esc(get_date(a))}</span></div>
        </article>'''


def guide_card(a):
    """Generate an <a class="guide-card"> card for pga-tour/guides/tournaments."""
    return f'''        <a class="guide-card" href="{esc(get_url(a))}">
          <img width="1672" height="941" src="{esc(get_image(a))}" alt="{esc(get_title(a))}" class="card-thumb" loading="lazy">
          <div class="card-body">
            <div class="badge-row"><span class="badge badge-red">{esc(get_category(a))}</span></div>
            <h3>{esc(get_title(a))}</h3>
            <p>{esc(get_excerpt(a))}</p>
            <div class="card-meta">
              <span class="author">GOLFRAW Editorial · {esc(get_date(a))}</span>
              <span class="card-cta">Read →</span>
            </div>
          </div>
        </a>'''


def search_entry(a):
    """Generate a JS object literal for the search index."""
    def js_esc(s):
        return s.replace('\\', '\\\\').replace('"', '\\"')
    return (f'  {{t:"{js_esc(get_title(a))}", '
            f'l:"{js_esc(get_url(a))}", '
            f'img:"{js_esc(get_image(a))}", '
            f'cat:"{js_esc(get_category(a))}", '
            f'date:"{js_esc(get_date(a))}", '
            f'author:"GOLFRAW Editorial", '
            f'x:"{js_esc(get_excerpt(a))}", '
            f'k:"{js_esc(get_keywords(a))}"}}')


# ---------------------------------------------------------------------------
# Grid injection
# ---------------------------------------------------------------------------

def inject_news_grid(page_file, articles):
    """Replace the <div class="news-grid">...</div> block before NEWSLETTER."""
    path = os.path.join(ROOT, page_file)
    src = open(path, encoding='utf-8').read()

    # Find the news-grid opening tag
    grid_start_match = re.search(r'<div class="news-grid">', src)
    if not grid_start_match:
        print(f"  WARNING: no news-grid found in {page_file}")
        return False

    # Find the NEWSLETTER marker that comes after the grid
    newsletter_idx = src.index('<!-- START NEWSLETTER SECTION -->')

    # Walk backwards from newsletter to find the closing </div> of the grid
    # The grid is closed by </div> then some whitespace before the newsletter
    grid_end = src.rfind('</div>', grid_start_match.start(), newsletter_idx)
    if grid_end == -1:
        print(f"  WARNING: couldn't find grid close in {page_file}")
        return False

    # Build new grid
    cards = '\n'.join(news_card(a) for a in articles)
    new_grid = f'        <div class="news-grid">\n{cards}\n      </div>\n\n'

    new_src = src[:grid_start_match.start()] + new_grid + src[grid_end + len('</div>') + 1:]
    open(path, 'w', encoding='utf-8').write(new_src)
    return True


def inject_guide_grid(page_file, articles):
    """Replace the <div class="guide-grid">...</div> block before NEWSLETTER."""
    path = os.path.join(ROOT, page_file)
    src = open(path, encoding='utf-8').read()

    # Find the guide-grid opening tag
    grid_start_match = re.search(r'<div class="guide-grid">', src)
    if not grid_start_match:
        print(f"  WARNING: no guide-grid found in {page_file}")
        return False

    # Find the closing comment for guide-grid or NEWSLETTER section
    # Try to find a closing comment first
    close_comment = re.search(r'</div><!-- [./]?guide-grid -->', src[grid_start_match.start():])
    if close_comment:
        grid_end_abs = grid_start_match.start() + close_comment.end()
    else:
        # Fall back to finding the NEWSLETTER marker
        newsletter_idx = src.index('<!-- START NEWSLETTER SECTION -->')
        # Walk backwards to find the last </div> before newsletter
        # We need to find the </div> that closes the guide-grid, then the wrapping </div> for wrap
        grid_end_abs = src.rfind('</div>', grid_start_match.start(), newsletter_idx) + len('</div>')

    # Build new grid
    cards = '\n'.join(guide_card(a) for a in articles)
    new_grid = f'    <div class="guide-grid">\n{cards}\n      </div><!-- /.guide-grid -->'

    new_src = src[:grid_start_match.start()] + new_grid + src[grid_end_abs:]
    open(path, 'w', encoding='utf-8').write(new_src)
    return True


def inject_search_index(articles):
    """Replace the const ARTICLES = [...]; block in search.html."""
    path = os.path.join(ROOT, 'search.html')
    src = open(path, encoding='utf-8').read()

    start_marker = 'const ARTICLES = ['
    end_marker = '\n];'

    start_idx = src.index(start_marker)
    end_idx = src.index(end_marker, start_idx) + len(end_marker)

    entries = ',\n'.join(search_entry(a) for a in articles)
    new_block = f'const ARTICLES = [\n{entries}\n];'

    new_src = src[:start_idx] + new_block + src[end_idx:]
    open(path, 'w', encoding='utf-8').write(new_src)
    return True


# ---------------------------------------------------------------------------
# Sitemap
# ---------------------------------------------------------------------------

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
    open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write('\n'.join(out))
    return len(arts) + len(STATIC)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate(arts):
    """Check for missing files and images."""
    problems = []
    for a in arts:
        slug = a.get('slug') or a['url'].lstrip('/')
        img = a.get('image', '').split('?')[0]
        if not img or not os.path.exists(os.path.join(ROOT, img.lstrip('/'))):
            problems.append(('image missing', f"{slug} -> {img}"))
        if not os.path.exists(os.path.join(ROOT, slug + '.html')):
            problems.append(('page missing', slug))
    return problems


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    arts = load()
    print(f"registry: {len(arts)} articles")

    # Validate files exist
    probs = validate(arts)
    if probs:
        print(f"VALIDATION: {len(probs)} problem(s)")
        for kind, what in probs[:40]:
            print(f"   [{kind}] {what}")
    else:
        print("VALIDATION: all article files and images present")

    if '--check' in sys.argv:
        sys.exit(1 if probs else 0)

    # ---- Rebuild all grids ----
    print()

    # 1. news.html — ALL articles
    if inject_news_grid('news.html', arts):
        print(f"  news.html rebuilt: {len(arts)} articles")
    
    # 2. Category pages — filtered by section/category
    for section, page_file in SECTION_PAGE.items():
        filtered = [a for a in arts if get_section(a) == section]
        if page_file in NEWS_GRID_PAGES:
            if inject_news_grid(page_file, filtered):
                print(f"  {page_file} rebuilt: {len(filtered)} articles")
        elif page_file in GUIDE_GRID_PAGES:
            if inject_guide_grid(page_file, filtered):
                print(f"  {page_file} rebuilt: {len(filtered)} articles")

    # 3. search.html — ALL articles
    if inject_search_index(arts):
        print(f"  search.html rebuilt: {len(arts)} articles")

    # 4. sitemap.xml
    n = write_sitemap(arts)
    print(f"  sitemap.xml regenerated: {n} URLs")

    print()
    print("SYNC COMPLETE")
