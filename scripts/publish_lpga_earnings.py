#!/usr/bin/env python3
"""Publish the LPGA earnings data story through GolfRaw's static article path."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

try:
    from scripts.article_header import finalize_article_template_metadata, replace_article_header
except ModuleNotFoundError:  # direct execution from the scripts directory
    from article_header import finalize_article_template_metadata, replace_article_header


ROOT = Path(__file__).resolve().parents[1]
SLUG = "how-much-do-lpga-players-make"
OUTPUT = ROOT / f"{SLUG}.html"
REGISTRY = ROOT / "articles.json"
TEMPLATE = ROOT / "article-template.html"

TITLE = "How Much Do LPGA Players Make? Korda $6.2M, Median $205K"
DESCRIPTION = (
    "How much do LPGA players make? Nelly Korda has $6.2M, but the median player has "
    "$205,066. See prize money, caddie costs and what salary searches miss."
)
CANONICAL = f"https://www.golfraw.com/{SLUG}"
H1 = "Nelly Korda Has $6.2 Million. The Median LPGA Pro Has $205,066."
STANDFIRST = (
    "A typical LPGA Tour player has earned about $205,000 in prize money in 2026. "
    "That's the median on the LPGA's official money list through the FM Championship "
    "on 30 August, covering 190 players. Nelly Korda has $6,220,214. Only 26 players "
    "have reached $1 million."
)
HERO = "/public/lpga-tour-players-prize-money-earnings.webp"
HERO_ALT = "LPGA Tour golfer and caddie walking down the fairway during an official tournament round"
CADDIE_IMAGE = "/public/lpga-caddie-cost-weekly-fees.webp"
CADDIE_ALT = "LPGA caddie reviewing yardage book beside a staff golf bag on the practice green"

REGISTRY_RECORD = {
    "canonical": f"/{SLUG}",
    "alias_of": "",
    "slug": SLUG,
    "url": f"/{SLUG}",
    "title": TITLE,
    "excerpt": DESCRIPTION,
    "category": ["LPGA TOUR", "WOMEN'S GOLF", "PRO GOLF", "MONEY", "NEWS"],
    "date": "2026-09-21",
    "image": HERO,
    "keywords": (
        "how much do LPGA players make, LPGA average salary, LPGA player earnings, "
        "LPGA prize money 2026, median LPGA earnings, Nelly Korda earnings"
    ),
    "category_source": "editorial",
    # LPGA TOUR is the primary section; the other values are supporting
    # taxonomy used by cards, search and contextual links.
    "section": "LPGA TOUR",
}


ARTICLE_CSS = """
  <style id="lpga-earnings-article">
    .article-body a{text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:3px}
    .article-body a:hover{color:var(--flag)}
    .takeaways{margin:34px 0;padding:24px 26px;background:var(--white);border:2px solid var(--ink);border-top:4px solid var(--flag)}
    .takeaways h2,.takeaways h3{margin:0 0 12px;padding:0;border:0;font-size:18px;text-transform:uppercase}
    .takeaways p{margin:0}
    .table-container{overflow-x:auto;margin:26px 0 34px;border:2px solid var(--ink);background:var(--white)}
    .table-container table{width:100%;min-width:680px;border-collapse:collapse;font-size:15px;line-height:1.4}
    .table-container th,.table-container td{padding:13px 14px;border-bottom:1px solid #cbd5e1;text-align:left;vertical-align:top}
    .table-container th{background:var(--ink);color:#fff;font-family:var(--gr-meta,Inter,system-ui,sans-serif);font-size:10px;letter-spacing:.1em;text-transform:uppercase}
    .table-container tr:last-child td{border-bottom:0}
    .caddie-figure{margin:30px 0 34px;padding:12px;background:var(--white);border:2px solid var(--ink)}
    .caddie-figure img{width:100%;height:auto;aspect-ratio:1672 / 941;object-fit:cover}
    .caddie-figure figcaption{margin:10px 4px 2px;padding:0}
    .verdict-box{margin:42px 0 34px;padding:26px;background:var(--ink);color:#fff;border-top:4px solid var(--flag)}
    .verdict-box h2{margin:0 0 12px;padding:0;border:0;color:#fff}
    .verdict-box p:last-child{margin-bottom:0}
    .sources{margin:42px 0 0;padding:24px 26px;background:var(--white);border:1px solid #cbd5e1}
    .sources h2{margin:0 0 14px;padding:0;border:0;font-size:20px}
    .sources ol{margin:0;padding-left:20px;font-size:15px}
    .sources li{margin:0 0 12px}
    .provenance{margin-top:28px;padding-top:24px;border-top:1px solid #94a3b8;color:var(--grey);font-size:15px}
    .provenance p{margin:0 0 12px}
    .sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
    @media(max-width:700px){.takeaways,.sources{padding:20px}.table-container{margin-left:-2px;margin-right:-2px}.caddie-figure{margin-left:0;margin-right:0}}
  </style>
"""


ARTICLE_SCHEMA = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": "Article",
            "@id": f"{CANONICAL}#article",
            "headline": H1,
            "description": DESCRIPTION,
            "articleSection": "LPGA Tour",
            "keywords": REGISTRY_RECORD["keywords"],
            "inLanguage": "en",
            "image": {
                "@type": "ImageObject",
                "url": f"https://www.golfraw.com{HERO}",
                "contentUrl": f"https://www.golfraw.com{HERO}",
                "width": 1672,
                "height": 941,
                "caption": HERO_ALT,
            },
            "datePublished": "2026-09-21",
            "dateModified": "2026-09-21",
            "author": {
                "@type": "Organization",
                "@id": "https://www.golfraw.com/about#editorial",
                "name": "GolfRaw Editorial",
                "url": "https://www.golfraw.com/about",
            },
            "publisher": {"@id": "https://www.golfraw.com#organization"},
            "mainEntityOfPage": CANONICAL,
        },
        {
            "@type": "Organization",
            "@id": "https://www.golfraw.com#organization",
            "name": "GolfRaw",
            "url": "https://www.golfraw.com/",
            "logo": {
                "@type": "ImageObject",
                "url": "https://www.golfraw.com/icon-512.png",
                "width": 512,
                "height": 512,
            },
        },
        {
            "@type": "BreadcrumbList",
            "@id": f"{CANONICAL}#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.golfraw.com/"},
                {"@type": "ListItem", "position": 2, "name": "LPGA Tour", "item": "https://www.golfraw.com/lpga-tour"},
                {"@type": "ListItem", "position": 3, "name": H1, "item": CANONICAL},
            ],
        },
    ],
}


def replace_meta(source: str, pattern: str, value: str, *, attribute: str = "content") -> str:
    escaped = html.escape(value, quote=True)
    regex = re.compile(
        rf'(<meta\s+{attribute}=["\']{re.escape(pattern)}["\']\s+content=["\'])[^"\']*(["\'])',
        re.I,
    )
    updated, count = regex.subn(rf"\g<1>{escaped}\g<2>", source, count=1)
    if count != 1:
        raise ValueError(f"missing metadata field: {pattern}")
    return updated


def ensure_registry() -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    articles = data.setdefault("articles", [])
    existing = next((item for item in articles if item.get("slug") == SLUG), None)
    if existing is None:
        articles.insert(0, REGISTRY_RECORD)
    else:
        existing.update(REGISTRY_RECORD)
    categories = data.setdefault("categories", [])
    for value in REGISTRY_RECORD["category"]:
        if value not in categories:
            categories.append(value)
    data["categories"] = sorted(set(categories), key=lambda value: value.casefold())
    sections = data.setdefault("sections", [])
    if REGISTRY_RECORD["section"] not in sections:
        sections.append(REGISTRY_RECORD["section"])
    data["sections"] = sorted(set(sections), key=lambda value: value.casefold())
    REGISTRY.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build() -> None:
    ensure_registry()
    source = TEMPLATE.read_text(encoding="utf-8")
    source = replace_meta(source, "description", DESCRIPTION, attribute="name")
    source = re.sub(r"<title>.*?</title>", f"<title>{html.escape(TITLE)}</title>", source, count=1, flags=re.I | re.S)
    source = re.sub(r'(<link\s+rel=["\']canonical["\']\s+href=["\'])[^"\']*(["\'])', rf"\g<1>{CANONICAL}\g<2>", source, count=1, flags=re.I)
    source = replace_meta(source, "og:title", TITLE, attribute="property")
    source = replace_meta(source, "og:description", DESCRIPTION, attribute="property")
    source = replace_meta(source, "og:url", CANONICAL, attribute="property")
    source = replace_meta(source, "og:image", f"https://www.golfraw.com{HERO}", attribute="property")
    source = replace_meta(source, "og:image:width", "1672", attribute="property")
    source = replace_meta(source, "og:image:height", "941", attribute="property")
    source = replace_meta(source, "twitter:title", TITLE, attribute="name")
    source = replace_meta(source, "twitter:description", DESCRIPTION, attribute="name")
    source = replace_meta(source, "twitter:image", f"https://www.golfraw.com{HERO}", attribute="name")
    source = replace_meta(source, "robots", "index, follow, max-image-preview:large", attribute="name")
    source = replace_meta(source, "og:image:alt", HERO_ALT, attribute="property")
    source = replace_meta(source, "article:published_time", "2026-09-21", attribute="property")
    source = replace_meta(source, "article:modified_time", "2026-09-21", attribute="property")
    source = replace_meta(source, "article:section", "LPGA Tour", attribute="property")
    source = re.sub(
        r'(<meta\s+property=["\']article:author["\']\s+content=["\'])[^"\']*(["\'])',
        r"\g<1>GolfRaw Editorial\g<2>",
        source,
        count=1,
        flags=re.I,
    )
    source = replace_article_header(source, H1, STANDFIRST)
    source = re.sub(
        r'<nav class="crumbs".*?</nav>',
        '<nav class="crumbs" aria-label="Breadcrumb">\n'
        '          <a href="/">GolfRaw</a> / <a href="/lpga-tour">LPGA Tour</a> / '
        '<span>LPGA Player Earnings</span>\n        </nav>',
        source,
        count=1,
        flags=re.I | re.S,
    )
    source = re.sub(
        r'<span class="cat">.*?</span>',
        '<span class="cat">LPGA Tour · Earnings</span>',
        source,
        count=1,
        flags=re.I | re.S,
    )
    source = re.sub(
        r'<div class="byline">.*?</div>',
        '<div class="byline">\n'
        '            <span>BY <b><a href="/about">GolfRaw Editorial</a></b></span>\n'
        '            <span>PUBLISHED <b>MON 21 SEP 2026</b></span>\n'
        '            <span class="live-upd">UPDATED 21 SEP 2026</span>\n'
        '            <span><b>11 MIN READ</b></span>\n'
        '          </div>',
        source,
        count=1,
        flags=re.I | re.S,
    )
    source = re.sub(
        r'<figure class="lead-img">.*?</figure>',
        f'''<figure class="lead-img">
          <img src="{HERO}" alt="{html.escape(HERO_ALT, quote=True)}" width="1672" height="941" fetchpriority="high" decoding="async">
          <figcaption>LPGA TOUR MONEY LIST DATA THROUGH THE FM CHAMPIONSHIP. PHOTO: GOLFRAW</figcaption>
        </figure>''',
        source,
        count=1,
        flags=re.I | re.S,
    )

    body = f'''<div class="article-body">
          <p><b>THE SHORT ANSWER:</b> A typical LPGA Tour player has earned about $205,000 in prize money in 2026. That's the median on the LPGA's official money list through the FM Championship on 30 August, covering 190 players. Nelly Korda has $6,220,214. Only 26 players have reached $1 million.</p>

          <p>And $205,000 isn't what lands in anyone's bank account. The caddie gets paid first, win or lose, and the math on that is further down.</p>

          <div class="takeaways" role="note" aria-label="Methodology">
            <h3>Methodology</h3>
            <p>GolfRaw pulled the LPGA's official money list on 21 September 2026 and calculated the median, averages and shares ourselves. Official money counts LPGA members only. It excludes unofficial events such as the Solheim Cup and all sponsorship income.</p>
          </div>

          <h2>LPGA Money List 2026: The Numbers That Matter</h2>
          <p>Twenty-two official events are done and nine are left. The last one is the CME Group Tour Championship on 22 November. The 2025 column shows how a full season ended up.</p>

          <div class="table-container">
            <table>
              <caption class="sr-only">LPGA official money list comparison for 2026 and 2025</caption>
              <thead><tr><th scope="col">Metric</th><th scope="col">2026 through FM Championship</th><th scope="col">2025 full season</th></tr></thead>
              <tbody>
                <tr><th scope="row">Players with official money</th><td>190</td><td>182</td></tr>
                <tr><th scope="row">Total official money</th><td>$91,826,137</td><td>$111,417,097</td></tr>
                <tr><th scope="row">Money leader</th><td>Nelly Korda, $6,220,214</td><td>Jeeno Thitikul, $7,578,330</td></tr>
                <tr><th scope="row">Median player</th><td>$205,066</td><td>$268,163</td></tr>
                <tr><th scope="row">Average (mean)</th><td>$483,295</td><td>$612,182</td></tr>
                <tr><th scope="row">Players at $1M or more</th><td>26</td><td>43</td></tr>
                <tr><th scope="row">Players under $100K</th><td>67</td><td>51</td></tr>
                <tr><th scope="row">100th on the list</th><td>$186,062 (Mimi Rhodes)</td><td>$225,562</td></tr>
              </tbody>
            </table>
          </div>
          <p class="mono" style="font-size:11px;color:var(--grey);">SOURCE: LPGA official money, 2026 and 2025 seasons, accessed 21 SEP 2026. Totals, median, mean and counts calculated by GolfRaw.</p>

          <h2>Why Average LPGA Earnings Figures Mislead</h2>
          <p>The 2026 average is $483,295. Sounds decent. It's also more than double the median, and a gap that wide means a few names are dragging the average up.</p>
          <p>Korda alone has 6.8% of every official dollar paid to LPGA members this season, by our count. The top 10 have $28.5 million between them, close to a third of the whole pot. Now go to the other end. The bottom 95 players, half the tour, have $7.16 million combined. One golfer is less than a million short of half the membership put together.</p>
          <p>The real middle of the tour is Sophia Schubert and Chiara Tamburlini, 95th and 96th, three dollars apart. Sixty-seven players are still under $100,000. That's more than a third of the list, with two months of golf left to fix it.</p>

          <h2>How Did Nelly Korda Make $6.2 Million?</h2>
          <p>Mostly in two weeks. Korda won the Chevron Championship in April for $1,350,000, <a href="https://www.nbcsports.com/golf/news/2026-chevron-championship-payout-for-nelly-korda-and-field">NBC Sports reported</a>, then took the U.S. Women's Open at Riviera in June for $2,500,000 from a record $12.5 million purse, per <a href="https://www.golfchannel.com/lpga/news/us-womens-open-2026-prize-money-full-list">Golf Channel</a>. Add those up and you get $3.85 million. Sixty-two percent of her season came from two majors.</p>
          <p>Money at the top of the women's game comes in big chunks like that. The CME winner collects $4 million, and our math says that single cheque beats every player's 2026 total so far except Korda's and Haeran Ryu's $4,521,414.</p>
          <p>Prize money is also the smaller part of what a star makes. Sportico estimated Korda earned $13.8 million in 2025, with $2.8 million on the course and $11 million from sponsors, according to Skratch's report on the list. Jeeno Thitikul was at $10.1 million. Sponsor money exists further down the rankings too, but nobody publishes it, and it never shows up on the money list.</p>

          <h2>How Much Did LPGA Players Make in 2025?</h2>
          <p>A finished season is the better yardstick. The LPGA's final 2025 list has 182 members splitting $111.4 million in official money. The median player made $268,163. Forty-three cleared $1 million. Fifty-one never got to $100,000.</p>
          <p>Golf Monthly put the 2025 average at $701,098. That lines up with the reported $131.6 million total purse divided by 182, not with the money members actually earned. Run the LPGA's own list and the average drops to $612,182.</p>
          <p>That leaves about $20 million unaccounted for, and nobody publishes the breakdown. Our best read is non-members cashing at LPGA events, plus unofficial events. You can watch it happen this year. Shiho Kuwaki won the AIG Women's Open on 2 August and isn't on the LPGA's 2026 official money list at all.</p>
          <p>Next time a broadcast shows a huge season purse number, remember it's what the tournaments pay out. LPGA members bank less than that.</p>

          <h2>How Much Does an LPGA Caddie Cost?</h2>
          <figure class="caddie-figure">
            <img src="{CADDIE_IMAGE}" alt="{html.escape(CADDIE_ALT, quote=True)}" width="1672" height="941" loading="lazy" decoding="async">
            <figcaption>THE BAG COSTS MONEY BEFORE THE PLAYER HITS A SHOT. PHOTO: GOLFRAW</figcaption>
          </figure>
          <p>A lot. Caddies are required, and The Boston Globe reported in August 2026 that fees run $1,700 to $2,500 a week plus 8 to 10 percent of winnings. Entry fees are generally $200 for members. The Globe called the weekly bill "a few thousand dollars, paid out of pocket, before tee time."</p>
          <p>This is a GolfRaw example, not a real player's books. Take the 2026 median of $205,066, 20 starts and an 8% caddie cut:</p>
          <ul>
            <li>Weekly caddie fees: $34,000 to $50,000</li>
            <li>8% of winnings: $16,405</li>
            <li>Entry fees: $4,000</li>
          </ul>
          <p>That's $54,405 to $70,405 spent. Roughly $135,000 to $150,000 is left, and that's before flights, hotels, a coach or the tax bill. Caddie deals are private, so treat that as the least a player could be paying.</p>
          <p>A missed cut still costs a full week. Whether it pays depends on the event. The Chevron and the U.S. Women's Open gave $10,000 to pros who missed the cut. The FM Championship offered $1,000, plus hotel rooms, flight vouchers and rental cars, the Globe reported. We couldn't find out how many other stops do anything similar.</p>
          <p>LPGA commissioner Craig Kessler told the Globe: "Forever, golf has been a meritocracy. But I'm proud of the efforts we put forward to take care of all of our athletes, regardless of where they finish on the leaderboard." We'd give the FM credit for that. But plenty of players near the bottom of the list still spend more some weeks than they win.</p>

          <h2>Do LPGA Players Get a Salary?</h2>
          <p>No. LPGA Tour players get paid through prize money, and some of them add sponsorship. Holding a tour card doesn't come with a base wage.</p>
          <p>So be careful with "LPGA average salary" results. ZipRecruiter's "PGA LPGA salary" page says $44,778 a year as of September 2026, but it's built from golf-industry jobs like shop staff and teaching pros. It's accurate pay for a different job. The LPGA also has a teaching and club professional division, which muddles things more. See <a href="/what-does-lpga-stand-for">what LPGA stands for</a> if you want the organizational context.</p>
          <p>Earnings don't even decide who keeps a card. Full status goes to the top 100 in Race to the CME Globe points after The Annika. As The Golf News Net put it after the 2025 cutoff: "Ranking on the money list doesn't matter."</p>

          <h2>LPGA vs PGA Tour Prize Money</h2>
          <p>In 2025 the PGA Tour paid $550.4 million across 46 events, and its 236 players on the official money list averaged $2,335,280, according to Golf Monthly. On the LPGA's own list the average was $612,182. So the average man made about 3.8 times more.</p>
          <p>Scottie Scheffler won $27.7 million in official money in 2025. That's roughly a quarter of what the entire LPGA membership earned on the course that year. Purses depend on sponsors and TV deals, and so does pay. Scores have nothing to do with it.</p>
          <p>In team golf the gap is even starker. Read our breakdown of <a href="/solheim-cup-prize-money-ryder-cup-500k">Solheim Cup prize money</a> for the other side of the comparison.</p>

          <div class="verdict-box">
            <h2>The Raw Verdict</h2>
            <p>When someone asks how much LPGA players make, give them the median: about $205,000 in 2026 prize money so far, before a caddie who costs up to $2,500 a week. Korda's $6.2 million is real. So is the $132 million season purse. Both describe a couple of dozen players, not the tour.</p>
            <p>We think the median is the fairer number to quote, and the one we'll keep updating on this page. For most of the field, tour golf works like a small business. The good weeks pay for the bad ones, and nobody's on salary.</p>
          </div>
          <p>Keep two dates in mind. The Annika on 15 November decides who keeps a card, no matter how much anyone has banked. A week later the CME's $4 million first prize can reshuffle the top of the money list in a single afternoon.</p>
          <p>Want the on-course numbers instead? Start with <a href="/how-far-lpga-players-drive">how far LPGA players drive</a>.</p>

          <section class="sources" aria-labelledby="sources-label">
            <h2 id="sources-label">Sources</h2>
            <ol>
              <li><a href="https://www.lpga.com/tournaments/results">LPGA</a>, Official Money / Finishes, 2026 and 2025 seasons, accessed 21 September 2026.</li>
              <li>The Boston Globe (Emma Healy), “For women golfers, life on the fringes can be rough,” 23 August 2026.</li>
              <li><a href="https://www.golfchannel.com/lpga/news/us-womens-open-2026-prize-money-full-list">Golf Channel</a>, “U.S. Women's Open 2026 prize money,” 7 June 2026.</li>
              <li><a href="https://www.nbcsports.com/golf/news/2026-chevron-championship-payout-for-nelly-korda-and-field">NBC Sports</a>, “2026 Chevron Championship payout,” April 2026.</li>
              <li>Golf Monthly, “How Much Money Did The Average LPGA Tour Pro Make In 2025?” and “What Did The Average PGA Tour Pro Earn In 2025?”</li>
              <li>Skratch, Sportico, Sportcal, The Golf News Net, ZipRecruiter and Wikipedia, as cited in the relevant sections above.</li>
            </ol>
          </section>

          <div class="provenance">
            <p><strong>How we reported this.</strong> GolfRaw used the LPGA's official money lists as the primary dataset, then calculated the median, mean, thresholds and shares. Private costs and sponsorship estimates are labeled as reported or illustrative.</p>
            <p><strong>Author.</strong> <a href="/about">GolfRaw Editorial</a>.</p>
            <p><strong>Published.</strong> <time datetime="2026-09-21">21 September 2026</time>.</p>
            <p><strong>Last updated.</strong> <time datetime="2026-09-21">21 September 2026</time>. <a href="/corrections">Corrections policy</a>.</p>
          </div>

          <nav class="tag-row" aria-label="Article tags">
            <a href="/lpga-tour">LPGA Tour</a><a href="/what-does-lpga-stand-for">LPGA</a><a href="/how-far-lpga-players-drive">Women's golf</a><a href="/solheim-cup-prize-money-ryder-cup-500k">Prize money</a>
          </nav>
        </div>'''
    body_start = source.index('<div class="article-body">')
    article_end = source.index('      </article>', body_start)
    source = source[:body_start] + body + "\n" + source[article_end:]

    aside_start = source.index('      <aside class="article-aside"')
    aside_end = source.index('      </aside>', aside_start) + len('      </aside>')
    aside = '''      <aside class="article-aside" aria-label="Related LPGA coverage">
        <div class="aside-box">
          <div class="ab-head">More LPGA reporting</div>
          <a class="aside-item" href="/what-does-lpga-stand-for"><span class="mono">LPGA EXPLAINER</span>What does LPGA stand for?</a>
          <a class="aside-item" href="/how-far-lpga-players-drive"><span class="mono">TOUR DATA</span>How far do LPGA players drive?</a>
          <a class="aside-item" href="/solheim-cup-prize-money-ryder-cup-500k"><span class="mono">TEAM GOLF</span>Solheim Cup prize money explained</a>
        </div>
      </aside>'''
    source = source[:aside_start] + aside + source[aside_end:]

    related_marker = '    <!-- ============ RELATED ============ -->'
    related_start = source.index(related_marker)
    related_end = source.index('  <!-- START NEWSLETTER SECTION -->', related_start)
    related = '''    <!-- ============ RELATED ============ -->
    <section class="related" aria-labelledby="related-heading">
      <div class="wrap">
        <h2 id="related-heading">Keep Reading <span class="idx">/ LPGA</span></h2>
        <div class="rel-grid">
          <a class="rel-card" href="/what-does-lpga-stand-for"><div class="cat">LPGA Explainer</div><h3>What Does LPGA Stand For?</h3><div class="d">ORGANIZATION · GOLFRAW</div></a>
          <a class="rel-card" href="/how-far-lpga-players-drive"><div class="cat">Tour Data</div><h3>How Far Do LPGA Players Drive the Ball?</h3><div class="d">DISTANCE · GOLFRAW</div></a>
          <a class="rel-card" href="/solheim-cup-prize-money-ryder-cup-500k"><div class="cat">Team Golf</div><h3>Solheim Cup Prize Money: $0, and the Ryder Cup's $500K</h3><div class="d">PRIZE MONEY · GOLFRAW</div></a>
        </div>
      </div>
    </section>

'''
    source = source[:related_start] + related + source[related_end:]

    source = source.replace('</head>', ARTICLE_CSS + '\n</head>', 1)
    source = source.replace(
        '<!-- ============ STRUCTURED DATA (NewsArticle) ============ -->',
        '<!-- ============ STRUCTURED DATA (Article) ============ -->',
        1,
    )
    source = re.sub(
        r'<script type="application/ld\+json">.*?</script>',
        '<script type="application/ld+json">\n' + json.dumps(ARTICLE_SCHEMA, ensure_ascii=False, indent=2) + '\n</script>',
        source,
        count=1,
        flags=re.I | re.S,
    )
    source = finalize_article_template_metadata(source, OUTPUT)
    source = "\n".join(line.rstrip() for line in source.splitlines()) + "\n"
    OUTPUT.write_text(source, encoding="utf-8")
    print(f"published {OUTPUT}")


if __name__ == "__main__":
    build()
