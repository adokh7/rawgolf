#!/usr/bin/env python3
"""Keep the site consistent with articles.json (the single source of truth).

  python3 scripts/sync_site.py --check    # report drift, exit 1 if any (use in CI)
  python3 scripts/sync_site.py            # rebuild all grids, search, and sitemap

Regenerates: the latest-article feed in index.html; news.html, liv-golf.html,
             pga-tour.html, guides.html, tournaments.html, search.html grids;
             sitemap.xml; and feed.xml.
"""
import sys, os, re, json, html as html_mod, hashlib

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

# Keep the homepage useful as a crawl hub without turning it into a complete
# archive. Priority URLs are guaranteed a slot even when they fall outside the
# newest 15 by date (for example, a newly promoted evergreen guide).
HOMEPAGE_ARTICLE_LIMIT = 15
HOMEPAGE_PRIORITY_URLS = (
    '/news-2026-7-wood-vs-3-iron-australian-golfers',
    '/news-2026-golf-club-distances-guide',
)
HOMEPAGE_START = '<!-- START HOMEPAGE ARTICLE FEED -->'
HOMEPAGE_END = '<!-- END HOMEPAGE ARTICLE FEED -->'

# Every publishable root-level non-article page. Keeping these here ensures the
# sitemap agrees with the indexable canonicals applied by fix_seo_audit.py.
# article-template.html is intentionally omitted because it is a development
# scaffold, not a public destination.
STATIC = ['/', '/news', '/guides', '/liv-golf', '/pga-tour', '/tournaments',
          '/vault', '/ratings', '/tools', '/analysis', '/about', '/contact',
          '/corrections', '/full-board', '/manifesto', '/past-issues',
          '/privacy', '/ratings-manual', '/search', '/terms', '/the-card']

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


def homepage_articles(articles):
    """Return 15 newest articles while guaranteeing priority crawl targets.

    Sorting by normalized date avoids the mixed human/ISO date formats that
    previously scrambled the sitemap. Priority stories replace the oldest
    non-priority cards, so the visible feed remains capped at 15.
    """
    ordered = sorted(articles, key=lambda a: iso_date(get_date(a)), reverse=True)
    selected = ordered[:HOMEPAGE_ARTICLE_LIMIT]
    by_url = {get_url(a): a for a in articles}

    for priority_url in HOMEPAGE_PRIORITY_URLS:
        priority = by_url.get(priority_url)
        if not priority or priority in selected:
            continue
        replace_at = next(
            (i for i in range(len(selected) - 1, -1, -1)
             if get_url(selected[i]) not in HOMEPAGE_PRIORITY_URLS),
            None,
        )
        if replace_at is not None:
            selected[replace_at] = priority

    return selected


# ---------------------------------------------------------------------------
# Grid injection
# ---------------------------------------------------------------------------

NEWS_GRID_INDENT = '        '
NEWS_GRID_CLOSE_INDENT = '      '


def write_if_changed(path, text):
    """Write only when the content actually differs.

    Every generated file goes through here so a no-op sync leaves the tree
    completely untouched — no rewrites, no mtime churn. Returns True if the
    file was written.
    """
    if os.path.exists(path) and open(path, encoding='utf-8').read() == text:
        return False
    open(path, 'w', encoding='utf-8').write(text)
    return True


def inject_news_grid(page_file, articles):
    """Replace the <div class="news-grid">...</div> block before NEWSLETTER.

    Idempotent: running this twice must produce byte-identical output. The
    previous version anchored at the tag itself rather than the start of its
    indentation, so it prepended a further eight spaces on every run —
    news.html had reached 168 — and its trailing '\\n\\n' stacked one more
    blank line each time.
    """
    path = os.path.join(ROOT, page_file)
    src = open(path, encoding='utf-8').read()

    # Match the leading whitespace too, so the tag is re-indented rather than
    # pushed a further NEWS_GRID_INDENT to the right on every run.
    opening = re.search(r'[ \t]*<div class="news-grid">', src)
    if not opening:
        print(f"  WARNING: no news-grid found in {page_file}")
        return False
    start = opening.start()

    # Find the NEWSLETTER marker that comes after the grid
    newsletter_idx = src.index('<!-- START NEWSLETTER SECTION -->')

    # Walk backwards from newsletter to find the closing </div> of the grid
    grid_end = src.rfind('</div>', start, newsletter_idx)
    if grid_end == -1:
        print(f"  WARNING: couldn't find grid close in {page_file}")
        return False
    end = grid_end + len('</div>')
    # Swallow the blank lines that follow, so the '\n\n' below replaces them
    # instead of adding one more each run.
    end = re.compile(r'(?:[ \t]*\r?\n)*').match(src, end).end()

    cards = '\n'.join(news_card(a) for a in articles)
    new_grid = (f'{NEWS_GRID_INDENT}<div class="news-grid">\n{cards}\n'
                f'{NEWS_GRID_CLOSE_INDENT}</div>\n\n')

    write_if_changed(path, src[:start] + new_grid + src[end:])
    return True


GUIDE_GRID_INDENT = '      '
GUIDE_GRID_CLOSE = '</div><!-- /.guide-grid -->'

# Matches the grid's closing </div> together with EVERY marker comment that
# follows it, so repeated runs collapse back to a single marker instead of
# stacking one more each time.
GUIDE_GRID_CLOSE_RE = re.compile(
    r'</div>[ \t]*(?:<!--\s*/?\.?\s*guide-grid\s*-->[ \t]*)+')


def inject_guide_grid(page_file, articles):
    """Replace the <div class="guide-grid">...</div> block before NEWSLETTER.

    Idempotent: running this twice must produce byte-identical output.

    The previous version was not. Its closing-marker regex was
    `</div><!-- [./]?guide-grid -->`, and `[./]?` matches at most one
    character, so it could never match the two in `/.guide-grid`. That match
    silently failed on every run, fell through to a bare `</div>` search that
    stopped short of the existing marker comments, and so preserved all of
    them while appending one more — and re-indented the opening tag by four
    extra spaces each time. Three pages had accumulated 17-18 stray comments.
    """
    path = os.path.join(ROOT, page_file)
    src = open(path, encoding='utf-8').read()

    opening = re.search(r'[ \t]*<div class="guide-grid">', src)
    if not opening:
        print(f"  WARNING: no guide-grid found in {page_file}")
        return False
    start = opening.start()

    m = GUIDE_GRID_CLOSE_RE.search(src, start)
    if m:
        end = m.end()
    else:
        newsletter_idx = src.index('<!-- START NEWSLETTER SECTION -->')
        end = src.rfind('</div>', start, newsletter_idx) + len('</div>')

    cards = '\n'.join(guide_card(a) for a in articles)
    # Indentation is fixed rather than copied from the file, so a previously
    # over-indented tag is corrected instead of preserved.
    new_grid = (f'{GUIDE_GRID_INDENT}<div class="guide-grid">\n{cards}\n'
                f'{GUIDE_GRID_INDENT}{GUIDE_GRID_CLOSE}')

    write_if_changed(path, src[:start] + new_grid + src[end:])
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

    write_if_changed(path, src[:start_idx] + new_block + src[end_idx:])
    return True


def inject_homepage_feed(articles):
    """Replace the marked homepage feed with direct, crawlable HTML anchors."""
    path = os.path.join(ROOT, 'index.html')
    src = open(path, encoding='utf-8').read()
    if HOMEPAGE_START not in src or HOMEPAGE_END not in src:
        print('  WARNING: homepage article-feed markers are missing')
        return False

    start = src.index(HOMEPAGE_START)
    end = src.index(HOMEPAGE_END, start) + len(HOMEPAGE_END)
    cards = '\n'.join(news_card(a) for a in homepage_articles(articles))
    block = (f'{HOMEPAGE_START}\n'
             f'      <div class="news-grid reveal">\n{cards}\n'
             f'      </div>\n'
             f'      {HOMEPAGE_END}')
    return write_if_changed(path, src[:start] + block + src[end:])


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



def tool_pages():
    """Every individual /tools-* page on disk, sorted.

    The tools are standalone HTML and deliberately absent from articles.json,
    which is why they never reached the sitemap. Globbing keeps them in step
    automatically instead of relying on someone remembering a list.
    """
    import glob
    return sorted(
        os.path.basename(p)[:-5]
        for p in glob.glob(os.path.join(ROOT, 'tools-*.html'))
    )


def write_sitemap(arts):
    base = 'https://www.golfraw.com'
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">', '']
    out += [f'  <url>\n    <loc>{base}/</loc>\n    <changefreq>daily</changefreq>'
            f'\n    <priority>1.0</priority>\n  </url>']
    for u in STATIC[1:]:
        out.append(f'  <url>\n    <loc>{base}{u}</loc>\n    <changefreq>daily</changefreq>'
                   f'\n    <priority>0.8</priority>\n  </url>')
    # Individual tool pages. These were missing entirely — only /tools was
    # listed — so none of the calculators were being crawled. Discovered from
    # disk rather than hardcoded, so a new tool is indexed the moment it ships.
    # They carry no published date, so <lastmod> is omitted rather than faked.
    for slug in tool_pages():
        out.append(f'  <url>\n    <loc>{base}/{slug}</loc>\n    <changefreq>monthly</changefreq>'
                   f'\n    <priority>0.8</priority>\n  </url>')
    # Sort on the normalised date too — mixing 'AUG 07 2026' with '2026-08-07'
    # sorts lexicographically and scrambles the order.
    for a in sorted(arts, key=lambda x: iso_date(x.get('date')), reverse=True):
        d = iso_date(a.get('date'))
        lastmod = f'\n    <lastmod>{d}</lastmod>' if d else ''
        out.append(f'  <url>\n    <loc>{base}{a["url"]}</loc>{lastmod}'
                   f'\n    <priority>0.9</priority>\n  </url>')
    out += ['</urlset>', '']
    write_if_changed(os.path.join(ROOT, 'sitemap.xml'), '\n'.join(out))
    return len(arts) + len(STATIC) + len(tool_pages())



# ---------------------------------------------------------------------------
# RSS feed (WebSub-enabled)
# ---------------------------------------------------------------------------

FEED_PATH  = 'feed.xml'
FEED_URL   = 'https://www.golfraw.com/feed.xml'
FEED_ITEMS = 40
WEBSUB_HUBS = [
    'https://pubsubhubbub.appspot.com/',
    'https://pubsubhubbub.superfeedr.com/',
]


def rfc822(iso):
    """RFC-822 date for RSS. Falls back to now when the date is unparseable."""
    import datetime, email.utils
    d = iso_date(iso)
    if d:
        try:
            y, m, day = (int(x) for x in d.split('-'))
            dt = datetime.datetime(y, m, day, 9, 0, 0, tzinfo=datetime.timezone.utc)
            return email.utils.format_datetime(dt)
        except ValueError:
            pass
    return email.utils.format_datetime(datetime.datetime.now(datetime.timezone.utc))


def write_feed(arts):
    """Write feed.xml — the newest FEED_ITEMS articles, with WebSub hub links.

    The <atom:link rel="hub"> elements are what make this feed pushable: a hub
    only accepts a publish ping for a feed that advertises it. rel="self" is
    equally required — the hub uses it to identify the topic being published.
    """
    base = 'https://www.golfraw.com'
    items = sorted(arts, key=lambda a: iso_date(get_date(a)), reverse=True)[:FEED_ITEMS]
    # Derived from the newest item, NOT wall-clock time: a clock-based value
    # rewrites feed.xml on every sync and dirties the tree even when nothing
    # changed, which defeats write_if_changed.
    now = rfc822(get_date(items[0])) if items else rfc822('')

    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" '
           'xmlns:content="http://purl.org/rss/1.0/modules/content/">',
           '  <channel>',
           '    <title>GOLFRAW</title>',
           f'    <link>{base}/</link>',
           '    <description>Golf news without the press-release language. '
           'Evidence first, opinion labeled.</description>',
           '    <language>en</language>',
           f'    <lastBuildDate>{now}</lastBuildDate>',
           f'    <atom:link rel="self" href="{FEED_URL}" type="application/rss+xml"/>']
    for hub in WEBSUB_HUBS:
        out.append(f'    <atom:link rel="hub" href="{hub}"/>')
    for a in items:
        url = base + get_url(a)
        img = get_image(a).split('?')[0]
        out += ['    <item>',
                f'      <title>{esc(get_title(a))}</title>',
                f'      <link>{url}</link>',
                f'      <guid isPermaLink="true">{url}</guid>',
                f'      <pubDate>{rfc822(get_date(a))}</pubDate>',
                f'      <category>{esc(get_category(a))}</category>',
                f'      <description>{esc(get_excerpt(a))}</description>']
        if img:
            out.append(f'      <enclosure url="{base}{img}" type="image/webp"/>')
        out.append('    </item>')
    out += ['  </channel>', '</rss>', '']
    write_if_changed(os.path.join(ROOT, FEED_PATH), '\n'.join(out))
    return len(items)



SEEN_PATH    = '.fast-index-seen.json'
PENDING_PATH = '.fast-index-pending.json'


def article_fingerprint(article):
    """Hash registry metadata plus the published HTML source for change detection."""
    url = get_url(article)
    slug = article.get('slug') or url.lstrip('/')
    page_path = os.path.join(ROOT, slug + '.html')
    stable = {
        'url': url,
        'title': get_title(article),
        'excerpt': get_excerpt(article),
        'date': get_date(article),
        'image': get_image(article),
        'category': get_category(article),
        'section': get_section(article),
        'keywords': get_keywords(article),
    }
    digest = hashlib.sha256(
        json.dumps(stable, sort_keys=True, ensure_ascii=False).encode('utf-8'))
    try:
        with open(page_path, 'rb') as page:
            for chunk in iter(lambda: page.read(1024 * 1024), b''):
                digest.update(chunk)
    except OSError:
        # validate() reports the missing page separately. Retaining a stable
        # marker here still lets record_changed() complete and preserve state.
        digest.update(b'\0MISSING_PAGE')
    return digest.hexdigest()


def record_changed(arts, changed_hubs=()):
    """Diff URLs and content fingerprints, then queue new or changed pages.

    Older state files contain only ``urls``. That format is migrated without
    blasting the archive: existing pages become the fingerprint baseline and
    only genuinely new URLs are queued during the migration run.
    """
    seen_p = os.path.join(ROOT, SEEN_PATH)
    state = {}
    current = sorted({get_url(a) for a in arts if get_url(a)})
    fingerprints = {get_url(a): article_fingerprint(a) for a in arts if get_url(a)}
    try:
        state = json.load(open(seen_p, encoding='utf-8'))
        seen = set(state.get('urls', []))
    except (OSError, ValueError):
        seen = set()
    previous_fingerprints = state.get('fingerprints', {})
    if not isinstance(previous_fingerprints, dict):
        previous_fingerprints = {}

    current_set = set(current)
    new = current_set - seen
    changed_existing = {
        url for url in current_set & seen
        if previous_fingerprints and previous_fingerprints.get(url) != fingerprints[url]
    }
    changed = sorted(new | changed_existing | set(changed_hubs))

    first_run = not seen
    if first_run:
        changed = []                  # never blast the archive on the first run

    pend_p = os.path.join(ROOT, PENDING_PATH)
    if changed:
        prev = []
        try:
            prev = json.load(open(pend_p, encoding='utf-8')).get('urls', [])
        except (OSError, ValueError):
            pass
        merged = sorted(set(prev) | set(changed))
        json.dump({'urls': merged}, open(pend_p, 'w', encoding='utf-8'), indent=1)
    json.dump({'urls': current, 'fingerprints': fingerprints},
              open(seen_p, 'w', encoding='utf-8'), indent=1)
    return changed, first_run


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

README = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'README.md')


def generated_files():
    """Every file this script rewrites, derived from the real constants.

    Anything listed here is regenerated in whole or in part from articles.json,
    so hand-edits to generated regions are destroyed on the next sync.
    """
    return {'index.html', 'news.html', 'search.html', 'sitemap.xml', 'feed.xml'} | set(SECTION_PAGE.values())


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
        url = a.get('url', '')
        if (not url.startswith('/') or url.endswith('/') or url.endswith('.html') or
                any(char in url for char in '[]?#') or re.search(r'\s', url)):
            problems.append(('dirty article URL', repr(url)))
        slug = a.get('slug') or a['url'].lstrip('/')
        img = a.get('image', '').split('?')[0]
        if not img or not os.path.exists(os.path.join(ROOT, img.lstrip('/'))):
            problems.append(('image missing', f"{slug} -> {img}"))
        if not os.path.exists(os.path.join(ROOT, slug + '.html')):
            problems.append(('page missing', slug))
    return problems


def direct_anchor_urls(page_file):
    """Return literal href values from server-rendered anchor elements."""
    path = os.path.join(ROOT, page_file)
    try:
        src = open(path, encoding='utf-8').read()
    except OSError:
        return set()
    return set(re.findall(r'<a\b[^>]*\bhref=["\']([^"\']+)["\']', src, re.I))


def validate_internal_links(arts):
    """Require complete direct-anchor coverage on homepage and category hubs."""
    problems = []
    registry_urls = {get_url(a) for a in arts}
    for priority_url in HOMEPAGE_PRIORITY_URLS:
        if priority_url not in registry_urls:
            problems.append(('homepage priority URL absent from registry', priority_url))

    homepage_urls = direct_anchor_urls('index.html')
    selected = homepage_articles(arts)
    for article in selected:
        if get_url(article) not in homepage_urls:
            problems.append(('homepage article link missing', get_url(article)))

    news_urls = direct_anchor_urls('news.html')
    for article in arts:
        if get_url(article) not in news_urls:
            problems.append(('news hub article link missing', get_url(article)))

    for section, page_file in SECTION_PAGE.items():
        hub_urls = direct_anchor_urls(page_file)
        for article in arts:
            if get_section(article) == section and get_url(article) not in hub_urls:
                problems.append((f'{page_file} article link missing', get_url(article)))
    return problems


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    arts = load()
    print(f"registry: {len(arts)} articles")

    # Validate files exist, and that README.md still describes reality
    # A normal sync repairs generated-link drift before checking it below.
    # --check is read-only, so it must include internal-link drift up front.
    probs = validate(arts) + check_readme()
    if '--check' in sys.argv:
        probs += validate_internal_links(arts)
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

    # 0. index.html — 15 newest direct links, with priority crawl targets
    homepage_changed = inject_homepage_feed(arts)
    print(f"  index.html homepage feed rebuilt: {len(homepage_articles(arts))} articles")

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

    # 5. feed.xml — WebSub hubs are declared here, which is what makes the
    #    hub ping in step 6 acceptable to the hub at all.
    n = write_feed(arts)
    print(f"  feed.xml regenerated: {n} items")

    # 6. Fast indexing. Deliberately NOT fired by default: sync runs before
    #    the deploy, so a ping now would make the hub fetch the *old* live
    #    feed and find nothing new. The changed URLs are recorded instead, and
    #    `python3 scripts/fast_index.py` sends them once the deploy is live.
    changed, first_run = record_changed(arts, ['/'] if homepage_changed else [])
    if first_run:
        print("  fast-index: baseline recorded (no ping on first run)")
    elif changed:
        print(f"  fast-index: {len(changed)} new or changed URL(s) queued")
        for u in changed[:5]:
            print(f"      {u}")
        if len(changed) > 5:
            print(f"      ... +{len(changed)-5} more")
    else:
        print("  fast-index: no new URLs")

    link_problems = validate_internal_links(arts)
    if link_problems:
        print(f"  INTERNAL LINK VALIDATION: {len(link_problems)} problem(s)")
        for kind, what in link_problems[:40]:
            print(f"      [{kind}] {what}")
        sys.exit(1)
    print("  internal links: homepage and all category hubs complete")

    if '--notify' in sys.argv or os.environ.get('FAST_INDEX') == '1':
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        try:
            import fast_index
            print()
            fast_index.notify()
        except Exception as e:                 # indexing must never fail a sync
            print(f"  fast-index: skipped ({type(e).__name__}: {e})")
    elif changed:
        print("  -> run `python3 scripts/fast_index.py` AFTER deploying")

    print()
    print("SYNC COMPLETE")
