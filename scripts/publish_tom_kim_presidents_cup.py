#!/usr/bin/env python3
"""Publish the Tom Kim Presidents Cup record story through GolfRaw's static article path.

Same pipeline as publish_lpga_earnings.py: fill article-template.html, insert
the registry record, then `python3 scripts/sync_site.py` rebuilds the feeds,
hubs, sitemap and search index from that record.
"""

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
SLUG = "tom-kim-presidents-cup-record-medinah"
OUTPUT = ROOT / f"{SLUG}.html"
REGISTRY = ROOT / "articles.json"
TEMPLATE = ROOT / "article-template.html"

TITLE = "Tom Kim Presidents Cup Record: 3-5-1 and a Rematch Waiting"
DESCRIPTION = (
    "What Tom Kim said in 2024, what he walked back, his 3-5-1 Presidents Cup record, "
    "and why the Schauffele-Cantlay rematch at Medinah matters more than the boos."
)
CANONICAL = f"https://www.golfraw.com/{SLUG}"
H1 = "Tom Kim Is 3-5-1 at the Presidents Cup. The Villain Label Doesn't Fit the Record."
STANDFIRST = (
    "He said US players cursed at him at Royal Montreal, took most of it back the next "
    "morning, and has won 3, lost 5 and halved 1 across two Presidents Cups. This week he "
    "arrives at Medinah on the best form of his career, and the two Americans everyone "
    "links to the 2024 story are both on Brandt Snedeker's team."
)
DATE = "2026-09-23"
# News articles carry the full publication time: the Google News sitemap and
# feed.xml read it, and the standard sitemap keeps the date part as lastmod.
DATETIME = "2026-09-23T16:45:00+02:00"
# The owner uploads images by hand; this one is committed at
# public/images/<name>.webp. Vercel serves the repo root (outputDirectory "."),
# so that file is /public/images/<name>.webp. The bare /images/ prefix only
# works for heroes that also have a copy in the root images/ folder, which
# this one does not (checked live: /images/... 404, /public/images/... 200).
# The size is the file's own; the image pass re-reads it.
HERO = "/public/images/tom-kim-presidents-cup-medinah.webp"
HERO_ALT = "Tom Kim of the International Team during a Presidents Cup match"
HERO_W, HERO_H = 1536, 1024

REGISTRY_RECORD = {
    "canonical": f"/{SLUG}",
    "alias_of": "",
    "slug": SLUG,
    "url": f"/{SLUG}",
    "title": TITLE,
    "excerpt": DESCRIPTION,
    "category": ["PGA TOUR", "PRESIDENTS CUP", "PRO GOLF"],
    "date": DATE,
    "image": HERO,
    "keywords": (
        "Tom Kim Presidents Cup record, Tom Kim Presidents Cup, Tom Kim cursing 2024 Royal Montreal, "
        "Presidents Cup 2026 Medinah, Tom Kim Schauffele Cantlay, Tom Kim villain, International Team"
    ),
    "category_source": "editorial",
    # PGA TOUR is the primary section (a player's record, tour news); the
    # other values are supporting taxonomy for cards, search and links.
    "section": "PGA TOUR",
}


ARTICLE_CSS = """
  <style id="tom-kim-article">
    .article-body a{text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:3px}
    .article-body a:hover{color:var(--flag)}
    .table-container{overflow-x:auto;margin:26px 0 12px;border:2px solid var(--ink);background:var(--white)}
    .table-container table{width:100%;min-width:320px;border-collapse:collapse;font-size:15px;line-height:1.4}
    .table-container th,.table-container td{padding:13px 14px;border-bottom:1px solid #cbd5e1;text-align:left;vertical-align:top}
    .table-container th{background:var(--ink);color:#fff;font-family:var(--gr-meta,Inter,system-ui,sans-serif);font-size:10px;letter-spacing:.1em;text-transform:uppercase}
    .table-container tbody th{background:var(--white);color:var(--ink);font-family:inherit;font-size:15px;letter-spacing:0;text-transform:none;font-weight:700}
    .table-container tr:last-child td,.table-container tr:last-child th{border-bottom:0}
    .table-container tr.total th,.table-container tr.total td{background:#f1f5f9;font-weight:700}
    .table-note{margin:0 0 30px;font-size:12px;color:var(--grey)}
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
    @media(max-width:700px){.sources,.verdict-box{padding:20px}.table-container{margin-left:-2px;margin-right:-2px}}
  </style>
"""


ARTICLE_SCHEMA = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": "NewsArticle",
            "@id": f"{CANONICAL}#article",
            "headline": H1,
            "description": DESCRIPTION,
            "articleSection": "PGA Tour",
            "keywords": REGISTRY_RECORD["keywords"],
            "inLanguage": "en",
            "image": {
                "@type": "ImageObject",
                "url": f"https://www.golfraw.com{HERO}",
                "contentUrl": f"https://www.golfraw.com{HERO}",
                "width": HERO_W,
                "height": HERO_H,
                "caption": HERO_ALT,
            },
            "datePublished": DATETIME,
            "dateModified": DATETIME,
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
                {"@type": "ListItem", "position": 2, "name": "PGA Tour", "item": "https://www.golfraw.com/pga-tour"},
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


BODY = '''<div class="article-body">
          <p>Tom Kim tees it up at Medinah this week as the International player the Americans reportedly like least, two years after he said US players cursed at him at Royal Montreal. He took most of that back the next morning. His Presidents Cup record across 2022 and 2024 is 3 wins, 5 losses and 1 half. He also arrives playing the best golf of his career, and the two Americans everyone links to the 2024 story, Xander Schauffele and Patrick Cantlay, are both on Brandt Snedeker's team.</p>
          <p>That last part is the bit worth your attention. Kim has faced that pairing twice in this event and split the results. More on that below.</p>

          <h2>What Tom Kim actually said in 2024</h2>
          <p>The story is shorter than its reputation.</p>
          <p>Saturday 28 September 2024. Kim and Si Woo Kim lose a foursomes match 1 down to Schauffele and Cantlay at Royal Montreal, per Golf Monthly. Afterwards Kim tells reporters he heard US players cursing at his side during the match. Golf Digest quoted him: "I just don't think there's a need to look at someone and curse at them." He didn't name anyone. He did say Schauffele, Cantlay and their caddies were not the ones involved, according to Golf Monthly, and Golf Channel's Rex Hoggard reported the moment came on the 11th hole and involved some members of the US contingent.</p>
          <p>Schauffele's answer the same day, per Golf Digest: "I felt like Pat and I, we treated the Kims with the utmost respect...I have no clue if anyone was doing any of that."</p>
          <p>Sunday 29 September 2024. Before singles, Kim went to find US captain Jim Furyk and Schauffele to clear the air, NBC Sports reported. "I didn't mean it to go in such a negative way," he said. The US won the cup that afternoon 18.5&ndash;11.5.</p>
          <p>So the whole thing lasted under 24 hours, named nobody, and was walked back by the person who said it. Who cursed, and what they said, has never been established publicly. Two years on, it still hasn't.</p>

          <h2>Tom Kim's Presidents Cup record</h2>
          <p>Here's the part the villain framing skips. Kim has never had a winning week in this event.</p>
          <div class="table-container">
            <table>
              <caption class="sr-only">Tom Kim's Presidents Cup record by year</caption>
              <thead><tr><th scope="col">Year</th><th scope="col">Venue</th><th scope="col">Record (W-L-H)</th><th scope="col">Result</th></tr></thead>
              <tbody>
                <tr><th scope="row">2022</th><td>Quail Hollow</td><td>2-3-0</td><td>US won 17.5&ndash;12.5</td></tr>
                <tr><th scope="row">2024</th><td>Royal Montreal</td><td>1-2-1</td><td>US won 18.5&ndash;11.5</td></tr>
                <tr class="total"><th scope="row">Career</th><td>&mdash;</td><td>3-5-1</td><td>0 team wins</td></tr>
              </tbody>
            </table>
          </div>
          <p class="table-note mono">RECORDS FROM THE 2022 AND 2024 PRESIDENTS CUP RESULTS; THE 2024 LINE ALSO APPEARS IN GOLF DIGEST'S 22 SEPT 2026 COLUMN.</p>
          <p>The 2022 week is why people remember him. On the Saturday at Quail Hollow he and K.H. Lee beat Scottie Scheffler and Sam Burns 2&amp;1 in foursomes, then he and Si Woo Kim beat Cantlay and Schauffele in four-ball, with Kim hitting a 2-iron to 10 feet on the 18th and holing the winning birdie, as CBS Sports reported at the time. The celebrations were loud. That was a 20-year-old rookie taking two points off the best team in the world in one day.</p>
          <p>Then the numbers ran out. Three losses that same week, and a 1-2-1 in Montreal while Schauffele and Cantlay each went 4-1-0. If Kim were really the player who torments the Americans, the record would show it. It shows a good player on a team that keeps losing by six points or more.</p>

          <h2>Why 2026 is different</h2>
          <p>Kim qualified for this team on points. Nobody had to spend a pick on him.</p>
          <p>He'd gone almost three years without a win before July. Then he shot a closing 64 to win the Genesis Scottish Open at 20 under, two clear of Min Woo Lee, on 12 July 2026, his first PGA Tour win in roughly 1,010 days, according to the PGA Tour's own recap. He called his approach on the final hole "one of the best shots I've hit in my career so far." Earlier in the summer he finished third at the U.S. Open.</p>
          <p>Golf Channel's Brentley Romine ranked him sixth of all 24 players at Medinah on 20 September, citing his form since the Scottish Open. That's an outside opinion, not a stat, but it matches the results. This is the first Presidents Cup where Kim shows up as one of the Internationals' best players rather than their loudest one.</p>

          <h2>The Schauffele and Cantlay rematch</h2>
          <p>Snedeker used two of his six captain's picks on Schauffele and Cantlay, alongside Chris Gotterup, Justin Thomas, Jacob Bridgeman and Jackson Koivun. So the pair Kim beat in 2022 and lost to in 2024 are in the building. By our count that's 1-1 head to head over two Presidents Cups.</p>
          <p>Whether you get a third instalment depends on the captains. Thursday is five four-ball matches, Friday is five foursomes, Saturday splits four and four, and Sunday is 12 singles, per CBS Sports. Thirty points are on the table and 15.5 wins the cup. Geoff Ogilvy has paired the two Kims before. If he does it again and Snedeker sends Cantlay and Schauffele out against them, you'll know within an hour of the pairings dropping. For the side of the draw Ogilvy is working with, see our piece on <a href="/presidents-cup-captain-liv-golf-restrictions-international-team">the International captain and the LIV players he cannot pick</a>.</p>
          <p>Our view: that match would be the one to watch this week, not because of any grudge but because it's the best test of whether Kim's 2026 form travels into match play against the Americans' most reliable pairing.</p>

          <h2>What Kim said at Medinah this week</h2>
          <p>Golf Digest's Joel Beall wrote on 22 September that US players privately considered Kim's Montreal behaviour "bush league and annoying as hell." That's Golf Digest's account of unnamed sources, and no American has said anything like it on the record this week that we could find.</p>
          <p>Kim, speaking on Tuesday as reported by Golf Digest, sounded like someone who expects the reception and doesn't mind it: "Going to be a little bit different than the last one obviously playing on U.S. soil. Sure we're going to hear a lot of boos." He added: "I think you just got to enjoy it as much as you can. Team golf is so special. The more years I play on the PGA Tour the more I realize how special these events are."</p>
          <p>The Americans have won 13 of the previous 15 Presidents Cups and 10 in a row, per CBS Sports. The Internationals don't need a pantomime villain. They need points, and Kim is one of the few players on their side currently producing them.</p>

          <div class="verdict-box">
            <h2>The Raw Verdict</h2>
            <p>The villain label is a television storyline built on one vague comment that its author retracted within a day. Treating it as proof of bad character isn't fair to Kim, and treating him as some proven American-killer isn't fair to the scoreboard. He's 3-5-1.</p>
            <p>What matters at Medinah is simpler. Kim is playing well for the first time in a Presidents Cup year, and the Internationals are 0-for-10 since 2005. If Ogilvy pairs him with Si Woo Kim on Thursday and the Americans answer with Cantlay and Schauffele, watch that match. It'll tell you more about this week than any boo from the gallery.</p>
          </div>
          <p>Want the money side of team golf? <a href="/solheim-cup-prize-money-ryder-cup-500k">Solheim Cup players aren't paid</a>, and the Ryder Cup's $500K is the exception.</p>
          <p>Add Golf Raw as a preferred source in Google to see our Presidents Cup coverage in Top Stories.</p>

          <section class="sources" aria-labelledby="sources-label">
            <h2 id="sources-label">Sources</h2>
            <ol>
              <li>Golf Digest (Joel Beall), &ldquo;Presidents Cup 2026: Tom Kim is the agitator this event desperately needs,&rdquo; 22 September 2026.</li>
              <li>PGA Tour, &ldquo;International Team Captain Geoff Ogilvy announces six picks for 2026 Presidents Cup,&rdquo; 1 September 2026.</li>
              <li>PGA Tour, &ldquo;Presidents Cup: How to watch, live scores, tee times, TV times,&rdquo; 22 September 2026.</li>
              <li>PGA Tour, Genesis Scottish Open final-round recap, 12 July 2026.</li>
              <li>Golf Channel (staff), &ldquo;2026 Presidents Cup: Full International Team roster,&rdquo; 22 September 2026.</li>
              <li>Golf Channel (Brentley Romine), &ldquo;Ranking all 24 Presidents Cup competitors at Medinah,&rdquo; 20 September 2026.</li>
              <li>Yahoo Sports (Ryan Young), &ldquo;Brandt Snedeker, Geoff Ogilvy make captain's picks,&rdquo; 1 September 2026.</li>
              <li>CBS Sports (Robby Kalland), &ldquo;2026 Presidents Cup format and schedule,&rdquo; 22 September 2026.</li>
              <li>CBS Sports (Kyle Porter), &ldquo;2022 Presidents Cup: Tom Kim emerges as breakout star,&rdquo; 24 September 2022.</li>
              <li>Golf Digest (Joel Beall), &ldquo;Tom Kim accuses Americans of poor sportsmanship, being cursed at,&rdquo; 28 September 2024.</li>
              <li>Golf Monthly (Jonny Leighfield), &ldquo;&lsquo;I Could Hear Some Players Cursing At Us&rsquo;,&rdquo; 29 September 2024.</li>
              <li>NBC Sports (Brentley Romine), &ldquo;Tom Kim seeks out Americans to clear air,&rdquo; 29 September 2024.</li>
              <li>Presidents Cup results, 2022 and 2024, cross-checked 23 September 2026.</li>
            </ol>
          </section>

          <div class="provenance">
            <p><strong>How we reported this.</strong> GolfRaw was not at Medinah. Quotes and match details come from the reports listed above; the 3-5-1 record was compiled from the official 2022 and 2024 Presidents Cup results and cross-checked against Golf Digest's 22 September 2026 column.</p>
            <p><strong>Author.</strong> <a href="/about">GolfRaw Editorial</a>.</p>
            <p><strong>Published.</strong> <time datetime="2026-09-23">23 September 2026</time>.</p>
            <p><strong>Last updated.</strong> <time datetime="2026-09-23">23 September 2026</time>. <a href="/corrections">Corrections policy</a>.</p>
          </div>

          <nav class="tag-row" aria-label="Article tags">
            <a href="/pga-tour">PGA Tour</a><a href="/news-2026-us-presidents-cup-team-standings">Presidents Cup</a><a href="/presidents-cup-captain-liv-golf-restrictions-international-team">International Team</a><a href="/solheim-cup-prize-money-ryder-cup-500k">Team golf</a>
          </nav>
        </div>'''

ASIDE = '''      <aside class="article-aside" aria-label="Related Presidents Cup coverage">
        <div class="aside-box">
          <div class="ab-head">More Presidents Cup</div>
          <a class="aside-item" href="/news-2026-us-presidents-cup-team-standings"><span class="mono">US TEAM</span>2026 U.S. Presidents Cup team standings: Scheffler and Young secure automatic spots</a>
          <a class="aside-item" href="/presidents-cup-captain-liv-golf-restrictions-international-team"><span class="mono">INTERNATIONALS</span>Presidents Cup captain: LIV Golf bans hurt the International Team</a>
          <a class="aside-item" href="/news-2026-trump-honorary-chairman-presidents-cup-2026"><span class="mono">MEDINAH</span>Trump named honorary chairman of the Presidents Cup again</a>
        </div>
      </aside>'''

RELATED = '''    <!-- ============ RELATED ============ -->
    <section class="related" aria-labelledby="related-heading">
      <div class="wrap">
        <h2 id="related-heading">Keep Reading <span class="idx">/ Presidents Cup</span></h2>
        <div class="rel-grid">
          <a class="rel-card" href="/news-2026-us-presidents-cup-team-standings"><div class="cat">US Team</div><h3>2026 U.S. Presidents Cup Team Standings: Scheffler and Young Secure Automatic Spots</h3><div class="d">PGA TOUR · GOLFRAW</div></a>
          <a class="rel-card" href="/presidents-cup-captain-liv-golf-restrictions-international-team"><div class="cat">International Team</div><h3>Presidents Cup Captain: LIV Golf Bans Hurt the International Team</h3><div class="d">TOURNAMENTS · GOLFRAW</div></a>
          <a class="rel-card" href="/solheim-cup-prize-money-ryder-cup-500k"><div class="cat">Team Golf</div><h3>Solheim Cup Prize Money: $0, and the Ryder Cup's $500K</h3><div class="d">PRIZE MONEY · GOLFRAW</div></a>
        </div>
      </div>
    </section>

'''


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
    source = replace_meta(source, "og:image:width", str(HERO_W), attribute="property")
    source = replace_meta(source, "og:image:height", str(HERO_H), attribute="property")
    source = replace_meta(source, "twitter:title", TITLE, attribute="name")
    source = replace_meta(source, "twitter:description", DESCRIPTION, attribute="name")
    source = replace_meta(source, "twitter:image", f"https://www.golfraw.com{HERO}", attribute="name")
    source = replace_meta(source, "robots", "index, follow, max-image-preview:large", attribute="name")
    source = replace_meta(source, "og:image:alt", HERO_ALT, attribute="property")
    source = replace_meta(source, "article:published_time", DATETIME, attribute="property")
    source = replace_meta(source, "article:modified_time", DATETIME, attribute="property")
    source = replace_meta(source, "article:section", "PGA Tour", attribute="property")
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
        '          <a href="/">GolfRaw</a> / <a href="/pga-tour">PGA Tour</a> / '
        '<span>Tom Kim</span>\n        </nav>',
        source,
        count=1,
        flags=re.I | re.S,
    )
    source = re.sub(
        r'<span class="cat">.*?</span>',
        '<span class="cat">Pro Golf · Presidents Cup</span>',
        source,
        count=1,
        flags=re.I | re.S,
    )
    source = re.sub(
        r'<div class="byline">.*?</div>',
        '<div class="byline">\n'
        '            <span>BY <b><a href="/about">GolfRaw Editorial</a></b></span>\n'
        '            <span>PUBLISHED <b>WED 23 SEP 2026</b></span>\n'
        '            <span class="live-upd">UPDATED 23 SEP 2026</span>\n'
        '            <span><b>6 MIN READ</b></span>\n'
        '          </div>',
        source,
        count=1,
        flags=re.I | re.S,
    )
    source = re.sub(
        r'<figure class="lead-img">.*?</figure>',
        f'''<figure class="lead-img">
          <img src="{HERO}" alt="{html.escape(HERO_ALT, quote=True)}" width="{HERO_W}" height="{HERO_H}" fetchpriority="high" decoding="async">
          <figcaption>{html.escape(HERO_ALT.upper())}.</figcaption>
        </figure>''',
        source,
        count=1,
        flags=re.I | re.S,
    )

    body_start = source.index('<div class="article-body">')
    article_end = source.index('      </article>', body_start)
    source = source[:body_start] + BODY + "\n" + source[article_end:]

    aside_start = source.index('      <aside class="article-aside"')
    aside_end = source.index('      </aside>', aside_start) + len('      </aside>')
    source = source[:aside_start] + ASIDE + source[aside_end:]

    related_marker = '    <!-- ============ RELATED ============ -->'
    related_start = source.index(related_marker)
    related_end = source.index('  <!-- START NEWSLETTER SECTION -->', related_start)
    source = source[:related_start] + RELATED + source[related_end:]

    source = source.replace('</head>', ARTICLE_CSS + '\n</head>', 1)
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
