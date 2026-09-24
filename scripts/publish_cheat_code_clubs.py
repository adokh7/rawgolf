#!/usr/bin/env python3
"""Publish GolfRaw's "3 clubs that feel like a cheat code" equipment guide.

Same pipeline as publish_3wood_vs_3hybrid.py: fill article-template.html,
insert the registry record, then `python3 scripts/sync_site.py` rebuilds the
homepage feed, guides hub, search index, feed and sitemap from that record.
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
SLUG = "clubs-that-feel-like-a-cheat-code"
OUTPUT = ROOT / f"{SLUG}.html"
REGISTRY = ROOT / "articles.json"
TEMPLATE = ROOT / "article-template.html"

TITLE = "3 Clubs That Feel Like a Cheat Code (the Data Backs 2) | GolfRaw"
DESCRIPTION = (
    "A 7-wood, a hybrid and a chipper. Tracking data from millions of amateur rounds "
    "shows two of them lower scores. The third comes with a catch."
)
CANONICAL = f"https://www.golfraw.com/{SLUG}"
H1 = "3 Clubs That Feel Like a Cheat Code on the Course"
STANDFIRST = DESCRIPTION
DATE = "2026-09-24"
DATETIME = "2026-09-24T15:55:00+02:00"
# The owner uploads images by hand to public/images/, served as /public/images/.
# The file was not on disk when this was written, so the standard hero size
# is set here; the image pass rewrites width/height from the file once it lands.
HERO = "/public/images/clubs-that-feel-like-a-cheat-code.webp"
HERO_ALT = "The three golf clubs that feel like a cheat code: 7-wood, hybrid and chipper"
HERO_W, HERO_H = 1536, 1024
READING_TIME = "7 min read"

REGISTRY_RECORD = {
    "canonical": f"/{SLUG}",
    "alias_of": "",
    "slug": SLUG,
    "url": f"/{SLUG}",
    "title": TITLE,
    "excerpt": DESCRIPTION,
    "category": ["GUIDES", "EQUIPMENT", "CLUB FITTING"],
    "date": DATE,
    "image": HERO,
    "keywords": (
        "clubs that feel like a cheat code, easiest golf clubs to hit, 7 wood vs hybrid, "
        "hybrid vs long iron, is a chipper legal, 7 wood distance by handicap, "
        "easiest club for high handicappers, golf chipper, Scheffler 7 wood"
    ),
    "category_source": "editorial",
    "section": "GUIDES",
    "reading_time": READING_TIME,
}

# Visible FAQ and the FAQPage node are built from one list so they can never
# drift apart (tests/test_phase8_schema.py compares the two on articles).
FAQ = [
    (
        "What is the easiest golf club to hit for beginners?",
        "For most beginners, a hybrid or a 7-wood is easier to hit than a long iron. Arccos data from more than 200 million shots found the 4-hybrid hit more greens than the 4-iron in every handicap bracket. The wider sole and lower center of gravity get the ball airborne without perfect contact.",
    ),
    (
        "Is a 7-wood better than a hybrid?",
        "It depends on how you miss. A 7-wood usually launches higher and lands softer, which helps on firm greens and if you struggle to get the ball up. A hybrid is shorter, easier to control from rough and more versatile around greens. Many amateurs carry both.",
    ),
    (
        "Can you use a chipper in a tournament?",
        "Yes, if it conforms. It must have one striking face and a round grip, because Equipment Rule 2.1a says a putter can't have more than 10 degrees of loft. Two-sided chippers are non-conforming. Using one in a round means disqualification under Rule 4.1a.",
    ),
    (
        "How far should an average golfer hit a 7-wood?",
        "Shot Scope data reported by MyGolfSpy puts a 15-handicap's 7-wood carry at 180 to 195 yards and a 25-handicap at 165 to 180. A scratch golfer carries it 215 to 225. Loft is typically 20 to 23 degrees, with 21 the most common.",
    ),
]


ARTICLE_CSS = """
  <style id="cheat-code-clubs-article">
    .article-body a{text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:3px}
    .article-body a:hover{color:var(--flag)}
    .article-body a:focus-visible,.tag-row a:focus-visible,.aside-item:focus-visible,.rel-card:focus-visible{outline:3px solid var(--flag);outline-offset:3px}
    .takeaways{margin:34px 0;padding:24px 26px;background:var(--white);border:2px solid var(--ink);border-top:4px solid var(--flag)}
    .takeaways h2{margin:0 0 12px;padding:0;border:0;font-size:18px;text-transform:uppercase}
    .takeaways p{margin:0 0 12px}
    .takeaways p:last-child{margin-bottom:0}
    .table-container{overflow-x:auto;margin:26px 0 12px;border:2px solid var(--ink);background:var(--white)}
    .table-container table{width:100%;min-width:320px;border-collapse:collapse;font-size:15px;line-height:1.4}
    .table-container th,.table-container td{padding:13px 14px;border-bottom:1px solid #cbd5e1;text-align:left;vertical-align:top}
    .table-container th{background:var(--ink);color:#fff;font-family:var(--gr-meta,Inter,system-ui,sans-serif);font-size:10px;letter-spacing:.1em;text-transform:uppercase}
    .table-container tbody th{background:var(--white);color:var(--ink);font-family:inherit;font-size:15px;letter-spacing:0;text-transform:none;font-weight:700}
    .table-container tr:last-child td,.table-container tr:last-child th{border-bottom:0}
    .table-note{margin:0 0 30px;font-size:12px;color:var(--grey)}
    .faq-block h3{margin:22px 0 8px}
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
    @media(max-width:700px){.takeaways,.sources,.verdict-box{padding:20px}.table-container{margin-left:-2px;margin-right:-2px}}
    @media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.rel-card,.aside-item{transition:none}}
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
            "articleSection": "Guides",
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
                {"@type": "ListItem", "position": 2, "name": "Guides", "item": "https://www.golfraw.com/guides"},
                {"@type": "ListItem", "position": 3, "name": H1, "item": CANONICAL},
            ],
        },
        {
            "@type": "FAQPage",
            "@id": f"{CANONICAL}#faq",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": question,
                    "acceptedAnswer": {"@type": "Answer", "text": answer},
                }
                for question, answer in FAQ
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


def faq_html() -> str:
    items = []
    for question, answer in FAQ:
        items.append(
            f"            <h3>{html.escape(question)}</h3>\n"
            f"            <p>{html.escape(answer)}</p>"
        )
    return "\n".join(items)


BODY = f'''<div class="article-body">
          <p>Be honest. How many times did you hit your 4-iron onto the green last season? If you're a 20-handicap, Shot Scope's 2026 data says you hit the green from 175 yards 8% of the time with a long iron. Switch to a hybrid and that number becomes 14%. You didn't take a lesson for that. You changed one club.</p>

          <div class="takeaways" role="note" aria-label="Quick answer">
            <h2>Quick answer</h2>
            <p>The three clubs that feel like a cheat code are a 7-wood, a hybrid in place of your long irons, and a chipper. Amateur tracking data backs the first two. They launch higher, land softer and hit more greens. The chipper helps some golfers, but the independent test we found gave it only a one-inch edge.</p>
            <p>The chipper is the one that looks most like cheating and does the least. We'll get to why.</p>
          </div>

          <p class="mono" style="font-size:12px;color:var(--grey);">BUILT ON: ARCCOS SHOT-TRACKING DATA, SHOT SCOPE DATA (VIA MYGOLFSPY AND GOLF MONTHLY), MYGOLFSPY'S PING CHIPR TEST, THE R&amp;A/USGA RULES OF GOLF AND EQUIPMENT RULES, AND GOLF.COM'S REPORTING ON SCOTTIE SCHEFFLER'S 7-WOOD. GOLF RAW DID NOT TEST ANY OF THESE CLUBS.</p>

          <h2>Why some clubs feel like a cheat code</h2>
          <p>Most amateurs don't have a speed problem with their long clubs. They have a height problem. A 4-iron needs speed and a clean strike to get airborne, and a thin one runs along the ground.</p>
          <p>The clubs on this list solve that with design, not skill. A low center of gravity, a wider sole and more loft let the club get the ball up for you. That's the whole trick, and it's legal.</p>

          <h2>Cheat code #1: the 7-wood</h2>
          <p>Scottie Scheffler won the 2025 PGA Championship with a 7-wood in the bag. According to GOLF.com, he used a TaylorMade Qi35 7-wood bent to 20 degrees. It launched 1.5 degrees higher than his 3-iron, spun 1,500 rpm more, and carried 240 yards.</p>
          <p>His reason was simple. "You have to be able to land the ball up on the green. You can't really run it up," Scheffler told GOLF.com. He hit it into the par-5 10th on Sunday, and that set up the birdie that put him in the lead for good.</p>
          <p>You're not hitting it 240. You don't need to. MyGolfSpy puts the typical 7-wood loft at 20 to 23 degrees, with 21 the most common. Its Shot Scope carry data looks like this:</p>
          <div class="table-container">
            <table>
              <caption class="sr-only">Typical 7-wood carry distance by handicap</caption>
              <thead><tr><th scope="col">Handicap</th><th scope="col">Typical 7-wood carry</th></tr></thead>
              <tbody>
                <tr><th scope="row">Scratch</th><td>215&ndash;225 yards</td></tr>
                <tr><th scope="row">5</th><td>200&ndash;210 yards</td></tr>
                <tr><th scope="row">15</th><td>180&ndash;195 yards</td></tr>
                <tr><th scope="row">25</th><td>165&ndash;180 yards</td></tr>
              </tbody>
            </table>
          </div>
          <p class="table-note mono">SOURCE: SHOT SCOPE DATA VIA MYGOLFSPY, MAY 2025.</p>
          <p>Look at the 15-handicap row. That's 180 to 195 yards of carry from a club most people find easier to hit than a 3-wood. The ball comes down steep enough to stop, so you're not hoping for a lucky bounce onto the front of the green.</p>
          <p>Who should carry one? Anyone who can't get a 3-wood airborne off the fairway, and plenty of people who can. If your 3-wood only leaves the bag on the tee, a 7-wood is probably the more useful club.</p>

          <h2>Cheat code #2: a hybrid instead of your long irons</h2>
          <p>This one has the best data behind it. Arccos looked at more than 200 million shots across 3.8 million rounds and compared the 4-iron with the 4-hybrid, in a study it published in 2020. The 4-hybrid hit more greens in regulation in every handicap bracket. And Arccos said: "Every handicap bracket saw a lower score when using the 4-hybrid off the tee."</p>
          <p>Shot Scope's newer 2026 numbers, reported by Golf Monthly, show the same pattern from 175 yards:</p>
          <div class="table-container">
            <table>
              <caption class="sr-only">Greens in regulation from 175 yards with a hybrid versus a long iron, by handicap</caption>
              <thead><tr><th scope="col">Handicap</th><th scope="col">GIR with hybrid</th><th scope="col">GIR with long iron</th></tr></thead>
              <tbody>
                <tr><th scope="row">20</th><td>14%</td><td>8%</td></tr>
                <tr><th scope="row">15</th><td>18%</td><td>14%</td></tr>
                <tr><th scope="row">10</th><td>25%</td><td>22%</td></tr>
                <tr><th scope="row">5</th><td>33%</td><td>31%</td></tr>
                <tr><th scope="row">Scratch</th><td>44%</td><td>46%</td></tr>
              </tbody>
            </table>
          </div>
          <p class="table-note mono">SOURCE: SHOT SCOPE 2026 DATA VIA GOLF MONTHLY, MAY 2026.</p>
          <p>The 20-handicap goes from 8% to 14%, almost double the greens. Only scratch players do better with the iron. Arccos found something similar at the top end: 0&ndash;5 handicaps hit 46.2% of fairways with a 4-iron off the tee against 43.5% with the hybrid. So good players do have a real reason to keep a long iron. If you're not one of them, that reason doesn't apply to you.</p>
          <p>Our view: if you're above a 10 and still carrying a 4-iron, it's costing you shots. Ask to swap it for a hybrid next time you're in a shop and hit them side by side. You'll see the difference in ball flight within a few swings.</p>

          <h2>Cheat code #3: the chipper (with a catch)</h2>
          <p>A chipper looks like a putter and has the loft of a mid-iron. You swing it with a putting stroke. The Ping ChipR has 38.5 degrees of loft and a putter-length 35-inch shaft, according to MyGolfSpy. Golf Monthly lists the Odyssey chipper at about 37 degrees.</p>
          <p>Here's the catch. When MyGolfSpy tested the ChipR in 2022 against seven golfers' own clubs, handicaps 1.0 to 15.0, it won on the fringe. But 55% of testers got closer with it, and the average gain was one inch. From the rough, fewer testers benefited. From a bunker it made cleaner contact but didn't get high enough to hold the green.</p>
          <p>That's the honest picture. The chipper feels like cheating because it takes the chunk out of the shot, and for someone with the chipping yips, that's worth a lot. For everyone else, one inch isn't a cheat code.</p>

          <h2>Is a chipper legal? Common myths about these clubs</h2>
          <p>Every one of these myths gets repeated on range and forum threads. The numbers don't back any of them.</p>
          <ul>
            <li><b>Myth: chippers are illegal.</b> Wrong for most models. The R&amp;A and USGA Equipment Rules allow one striking face on any club except a putter (Rule 2.4d). A chipper isn't a putter, because a putter can't have more than 10 degrees of loft (Rule 2.1a). That means it also needs a round grip (Rule 2.3b). A one-sided chipper with a round grip is fine. A two-faced chipper is not, and using a non-conforming club means disqualification under Rule 4.1a.</li>
            <li><b>Myth: hybrids are for seniors and beginners.</b> The Arccos data showed lower scores with the hybrid off the tee in every handicap bracket. Shot Scope showed more greens hit from 175 yards for every amateur group down to a 5-handicap. That's most golfers alive.</li>
            <li><b>Myth: good players hit long irons, not lofted woods.</b> The world No. 1 won a major with a 7-wood because a 3-iron couldn't stop on firm greens. Scheffler's 7-wood data is more useful to you than any macho rule about what belongs in a bag.</li>
            <li><b>Myth: a chipper will fix your short game.</b> A one-inch average gain on the fringe isn't a fix. Your short-game problem is probably distance control. Shot Scope's data, via MyGolfSpy, puts the average 25-handicap at 22 feet from the hole after short-game shots and the scratch golfer at 11. A different club won't close that 11-foot gap. Practice will.</li>
          </ul>

          <h2>How do you fit these clubs in a 14-club bag?</h2>
          <p>Rule 4.1b caps you at 14 clubs. Carry a 15th in stroke play and it costs two strokes for every hole where you broke the rule, up to four strokes a round. In match play you lose a hole for each breach, to a maximum of two.</p>
          <p>So something has to go. The easy swaps:</p>
          <ul>
            <li><b>7-wood</b> replaces the 3-wood you only hit off tees, or your 3-hybrid if they fly the same distance.</li>
            <li><b>Hybrid</b> replaces the 4-iron, then maybe the 5-iron.</li>
            <li><b>Chipper</b> replaces the lob wedge you're scared of anyway.</li>
          </ul>
          <p>Before you drop anything, hit the new club and the old one side by side on a launch monitor or a range with flags. If the carry distances overlap by less than 10 yards, you've got two clubs doing one job. <a href="/tools-bag-audit">The Bag Audit</a> will show you the gaps in your set from the carry numbers you already know.</p>

          <section class="faq-block" aria-labelledby="faq-label">
            <h2 id="faq-label">Frequently asked questions</h2>
{faq_html()}
          </section>

          <div class="verdict-box">
            <h2>The Raw Verdict</h2>
            <p>If you only change one club this year, make it the hybrid. It has the most data, it's cheap to try, and it helps nearly everyone who isn't a scratch player. The 7-wood comes a close second, and you won't find a better answer to firm greens and long par 3s.</p>
            <p>The chipper is the one we'd think twice about. It's legal and it works for golfers who freeze over a wedge. But the only independent test we found gave it one inch. Buy it for peace of mind, not because you think it'll save you shots.</p>
          </div>

          <section class="sources" aria-labelledby="sources-label">
            <h2 id="sources-label">Sources</h2>
            <ol>
              <li>Arccos, 4-iron versus 4-hybrid study across more than 200 million shots and 3.8 million rounds, published 2020.</li>
              <li>Shot Scope 2026 data on greens in regulation from 175 yards by handicap, as reported by Golf Monthly, May 2026.</li>
              <li>Shot Scope carry-distance and short-game proximity data, as reported by MyGolfSpy, May 2025.</li>
              <li>MyGolfSpy, Ping ChipR test with seven golfers (handicaps 1.0 to 15.0), 2022.</li>
              <li>GOLF.com, Scottie Scheffler's TaylorMade Qi35 7-wood at the 2025 PGA Championship.</li>
              <li>The R&amp;A and USGA, Rules of Golf (Rules 4.1a and 4.1b) and Equipment Rules (2.1a, 2.3b, 2.4d).</li>
            </ol>
          </section>

          <div class="provenance">
            <p><strong>How we reported this.</strong> GolfRaw did not test any of these clubs. Every number comes from the tracking data and tests listed above, and the rules citations are to the current R&amp;A and USGA texts. Where we give an opinion, it is marked as our view.</p>
            <p><strong>Author.</strong> <a href="/about">GolfRaw Editorial</a>.</p>
            <p><strong>Published.</strong> <time datetime="2026-09-24">24 September 2026</time>.</p>
            <p><strong>Last updated.</strong> <time datetime="2026-09-24">24 September 2026</time>. <a href="/corrections">Corrections policy</a>.</p>
          </div>

          <nav class="tag-row" aria-label="Article tags">
            <a href="/guides">Guides</a><a href="/3-wood-vs-3-hybrid">Fairway woods</a><a href="/why-pros-are-ditching-hybrids">Hybrids</a><a href="/tools-bag-audit">Bag gapping</a>
          </nav>
        </div>'''

ASIDE = '''      <aside class="article-aside" aria-label="Related equipment guides">
        <div class="aside-box">
          <div class="ab-head">More on what goes in the bag</div>
          <a class="aside-item" href="/tools-bag-audit"><span class="mono">FREE TOOL</span>The Bag Audit: find the gaps and overlaps in your set</a>
          <a class="aside-item" href="/3-wood-vs-3-hybrid"><span class="mono">EQUIPMENT</span>3-Wood vs 3-Hybrid: which one belongs in your bag</a>
          <a class="aside-item" href="/why-pros-are-ditching-hybrids"><span class="mono">EQUIPMENT</span>Why pros are ditching hybrids, and why you shouldn't</a>
        </div>
      </aside>'''

RELATED = '''    <!-- ============ RELATED ============ -->
    <section class="related" aria-labelledby="related-heading">
      <div class="wrap">
        <h2 id="related-heading">Keep Reading <span class="idx">/ Equipment</span></h2>
        <div class="rel-grid">
          <a class="rel-card" href="/3-wood-vs-3-hybrid"><div class="cat">Equipment</div><h3>3-Wood vs 3-Hybrid: Distance, Forgiveness and Which One Belongs in Your Bag</h3><div class="d">CLUB FITTING · GOLFRAW</div></a>
          <a class="rel-card" href="/why-pros-are-ditching-hybrids"><div class="cat">Equipment</div><h3>Why Pros Are Ditching Hybrids, and Why You Shouldn't</h3><div class="d">GEAR · GOLFRAW</div></a>
          <a class="rel-card" href="/srixon-zxi-irons-review"><div class="cat">Equipment</div><h3>Srixon ZXi Irons Review: Which 2026 Set Fits?</h3><div class="d">REVIEW · GOLFRAW</div></a>
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
    source = replace_meta(source, "article:section", "Guides", attribute="property")
    source = re.sub(
        r'(<meta\s+property=["\']article:author["\']\s+content=["\'])[^"\']*(["\'])',
        r"\g<1>GolfRaw Editorial\g<2>", source, count=1, flags=re.I,
    )
    source = replace_article_header(source, H1, STANDFIRST)
    source = re.sub(
        r'<nav class="crumbs".*?</nav>',
        '<nav class="crumbs" aria-label="Breadcrumb">\n'
        '          <a href="/">GolfRaw</a> / <a href="/guides">Guides</a> / '
        '<span>Cheat Code Clubs</span>\n        </nav>',
        source, count=1, flags=re.I | re.S,
    )
    source = re.sub(
        r'<span class="cat">.*?</span>',
        '<span class="cat">Guides · Equipment</span>',
        source, count=1, flags=re.I | re.S,
    )
    source = re.sub(
        r'<div class="byline">.*?</div>',
        '<div class="byline">\n'
        '            <span>BY <b><a href="/about">GolfRaw Editorial</a></b></span>\n'
        '            <span>PUBLISHED <b>THU 24 SEP 2026</b></span>\n'
        '            <span class="live-upd">UPDATED 24 SEP 2026</span>\n'
        f'            <span><b>{READING_TIME.upper()}</b></span>\n'
        '          </div>',
        source, count=1, flags=re.I | re.S,
    )
    source = re.sub(
        r'<figure class="lead-img">.*?</figure>',
        f'''<figure class="lead-img">
          <img src="{HERO}" alt="{html.escape(HERO_ALT, quote=True)}" width="{HERO_W}" height="{HERO_H}" fetchpriority="high" decoding="async">
          <figcaption>A 7-WOOD, A HYBRID AND A CHIPPER. THE DATA BACKS TWO OF THEM.</figcaption>
        </figure>''',
        source, count=1, flags=re.I | re.S,
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
    source = source.replace(
        '<!-- ============ STRUCTURED DATA (NewsArticle) ============ -->',
        '<!-- ============ STRUCTURED DATA (Article + FAQPage) ============ -->', 1,
    )
    source = re.sub(
        r'<script type="application/ld\+json">.*?</script>',
        '<script type="application/ld+json">\n' + json.dumps(ARTICLE_SCHEMA, ensure_ascii=False, indent=2) + '\n</script>',
        source, count=1, flags=re.I | re.S,
    )
    source = finalize_article_template_metadata(source, OUTPUT)
    source = "\n".join(line.rstrip() for line in source.splitlines()) + "\n"
    OUTPUT.write_text(source, encoding="utf-8")
    print(f"published {OUTPUT}")


if __name__ == "__main__":
    build()
