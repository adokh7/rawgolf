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

MONTHS = {'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04', 'MAY': '05', 'JUN': '06',
          'JUL': '07', 'AUG': '08', 'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'}


def iso_date(value):
    """Return a strict W3C YYYY-MM-DD date, or '' if it cannot be determined.

    The registry's `date` field doubles as human-readable card text, so it can
    arrive as either '2026-08-07' or 'AUG 07 2026'. <lastmod> must never carry
    the latter — Search Console rejects the whole sitemap as an invalid date.
    Returning '' lets the caller omit <lastmod> entirely, which is valid,
    rather than emit something malformed.
    """
    d = (value or '').strip()
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', d):
        return d
    m = re.fullmatch(r'([A-Za-z]{3})\s+(\d{1,2})\s+(\d{4})', d)      # AUG 07 2026
    if m and m.group(1).upper() in MONTHS:
        return f'{m.group(3)}-{MONTHS[m.group(1).upper()]}-{int(m.group(2)):02d}'
    m = re.fullmatch(r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})', d)      # 07 AUG 2026
    if m and m.group(2).upper() in MONTHS:
        return f'{m.group(3)}-{MONTHS[m.group(2).upper()]}-{int(m.group(1)):02d}'
    if re.match(r'\d{4}-\d{2}-\d{2}', d):                            # ISO + time
        return d[:10]
    return ''


def write_sitemap(arts):
    base = 'https://www.golfraw.com'
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">', '']
    out += [f'  <url>\n    <loc>{base}/</loc>\n    <changefreq>daily</changefreq>'
            f'\n    <priority>1.0</priority>\n  </url>']
    for u in STATIC[1:]:
        out.append(f'  <url>\n    <loc>{base}{u}</loc>\n    <changefreq>daily</changefreq>'
                   f'\n    <priority>0.8</priority>\n  </url>')
    # Sort on the normalised date too — mixing 'AUG 07 2026' with '2026-08-07'
    # sorts lexicographically and scrambles the order.
    for a in sorted(arts, key=lambda x: iso_date(x.get('date')), reverse=True):
        d = iso_date(a.get('date'))
        lastmod = f'\n    <lastmod>{d}</lastmod>' if d else ''
        out.append(f'  <url>\n    <loc>{base}{a["url"]}</loc>{lastmod}'
                   f'\n    <priority>0.9</priority>\n  </url>')
    out += ['</urlset>', '']
    open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write('\n'.join(out))
    return len(arts) + len(STATIC)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

README = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'README.md')


def generated_files():
    """Every file this script rewrites, derived from the real constants.

    Anything listed here is regenerated wholesale from articles.json, so a
    hand-edit to it is destroyed on the next sync.
    """
    return {'news.html', 'search.html', 'sitemap.xml'} | set(SECTION_PAGE.values())


def documented_files(text):
    """The generated-file list the README advertises, and its safe-to-edit list.

    The 'edit articles.json, never search.html' rule is only useful while it
    names the right files. The README already went stale once — it claimed the
    grids were never regenerated, months after they were — and that mismatch is
    what cost 63 keyword sets. So the doc is asserted against the code.
    """
    generated, safe = set(), set()
    m = re.search(r'regenerates these files wholesale.*?\n\n(.*?)\n\n', text, re.S)
    if m:
        generated = set(re.findall(r'`([\w./-]+\.(?:html|xml))`', m.group(1)))
    m = re.search(r'Safe to edit by hand:(.*?)(?:\n\n|\Z)', text, re.S)
    if m:
        safe = set(re.findall(r'`([\w./-]+\.(?:html|xml))`', m.group(1)))
    return generated, safe


def check_readme():
    """Fail if README.md misdescribes which files are generated."""
    problems = []
    if not os.path.exists(README):
        return [('README missing', 'scripts/README.md')]
    text = open(README, encoding='utf-8').read()
    actual = generated_files()
    documented, safe = documented_files(text)
    if not documented:
        return [('README generated-file table not found',
                 "expected a table after 'regenerates these files wholesale'")]
    for f in sorted(actual - documented):
        problems.append(('README missing generated file',
                         f'{f} is regenerated but not documented'))
    for f in sorted(documented - actual):
        problems.append(('README lists a non-generated file',
                         f'{f} is documented as generated but is not'))
    for f in sorted(safe & actual):
        problems.append(('README calls a generated file safe to edit',
                         f'{f} is regenerated — hand-edits are destroyed'))
    return problems


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

    # Validate files exist, and that README.md still describes reality
    probs = validate(arts) + check_readme()
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
