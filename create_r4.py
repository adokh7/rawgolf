import json, re

with open('article-template.html', 'r') as f:
    html = f.read()

# 1. Header & Metadata
title = "Tour Championship Final Round: Hovland Leads by One | GOLFRAW"
description = "Hovland leads by one at 15 under, Scheffler's three back, McIlroy shot 63. Every number that matters before the final round of the season."
canonical_url = "https://www.golfraw.com/news-2026-tour-championship-final-round-hovland-leads"
image_asset = "/public/tour-championship-final-round-hovland-leads-2026.webp"

html = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', html)
html = re.sub(r'<meta name="description" content=".*?">', f'<meta name="description" content="{description}">', html)
html = re.sub(r'<link rel="canonical" href=".*?">', f'<link rel="canonical" href="{canonical_url}">', html)
html = re.sub(r'<meta property="og:title" content=".*?">', f'<meta property="og:title" content="{title}">', html)
html = re.sub(r'<meta property="og:description" content=".*?">', f'<meta property="og:description" content="{description}">', html)
html = re.sub(r'<meta property="og:url" content=".*?">', f'<meta property="og:url" content="{canonical_url}">', html)
html = re.sub(r'<meta property="og:image" content=".*?">', f'<meta property="og:image" content="https://www.golfraw.com{image_asset}">', html)
html = re.sub(r'<meta name="twitter:title" content=".*?">', f'<meta name="twitter:title" content="{title}">', html)
html = re.sub(r'<meta name="twitter:description" content=".*?">', f'<meta name="twitter:description" content="{description}">', html)
html = re.sub(r'<meta name="twitter:image" content=".*?">', f'<meta name="twitter:image" content="https://www.golfraw.com{image_asset}">', html)

# 2. Layout & Header Spacing Protection
# Replace main page-grid padding
# Find <main class="wrap page-grid"> and add style="padding-top: 40px;"
html = html.replace('<main class="wrap page-grid">', '<main class="wrap page-grid" style="padding-top: 40px;">')

# Insert the hero right below the byline
# In article-template.html, byline is usually something like <div class="byline">...</div></header>
hero_html = """
        <figure class="lead-img">
          <img src="/public/tour-championship-final-round-hovland-leads-2026.webp" alt="Viktor Hovland celebrating a birdie putt on the 17th green at East Lake during Round 3 of the 2026 Tour Championship." width="1200" height="675" style="aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:8px;">
          <figcaption>VIKTOR HOVLAND HOLDS A ONE-SHOT ADVANTAGE HEADING INTO SUNDAY AT EAST LAKE WITH ALL 29 PLAYERS UNDER PAR. PHOTO: RAWGOLF</figcaption>
        </figure>
"""
# find </header> and insert after it
if '<figure class="lead-img">' in html:
    # replace existing
    html = re.sub(r'<figure class="lead-img">.*?</figure>', hero_html, html, flags=re.DOTALL)
else:
    html = html.replace('</header>', '</header>\n' + hero_html)

# Let's replace the visual breadcrumbs
new_vis_bc = """<nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/news">News</a> / <a href="/tournaments">Tournaments</a> / <span>Tour Championship Final Round</span>
        </nav>"""
html = re.sub(r'<nav class="crumbs".*?</nav>', new_vis_bc, html, flags=re.DOTALL)

# Header H1
html = re.sub(r'<h1 class="headline">.*?</h1>', '<h1 class="headline">Tour Championship Final Round: Hovland Leads by One</h1>', html, flags=re.DOTALL)
html = re.sub(r'<h2 class="subhead">.*?</h2>', '<h2 class="subhead">Hovland leads by one at 15 under, Scheffler’s three back, McIlroy shot 63. Every number that matters before the final round of the season.</h2>', html, flags=re.DOTALL)

# Let's extract the article body and replace it
new_body = """<div class="article-body">
          <div class="takeaways">
            <h3 style="margin-top:0;">Key Takeaways</h3>
            <ul>
              <li><b>Viktor Hovland (-15)</b> seized the 54-hole lead with a birdie-birdie finish, shooting 66.</li>
              <li><b>Ryan Gerard (-14)</b> matched him shot-for-shot until the 18th hole.</li>
              <li><b>Scottie Scheffler (-12)</b> sits three back after a bogey-free 66.</li>
              <li><b>Rory McIlroy (-10)</b> posted a career-low 63 at East Lake, gaining 3 strokes putting.</li>
              <li><b>All 29 players are under par</b>, turning this into a pure birdie sprint on an accessible course.</li>
            </ul>
          </div>

          <h2>How Hovland Seized the Lead</h2>
          <p>Viktor Hovland took control of the Tour Championship late on Saturday. He buried a crucial 12-footer on the 13th, matched Ryan Gerard with a clutch putt on the 14th, and delivered a birdie-birdie finish to card a 66 and reach 15 under par.</p>

          <h2>Ryan Gerard's Breakthrough</h2>
          <p>At 27 years old, playing in his first Tour Championship, Ryan Gerard has refused to blink. He stayed tied with Hovland for most of the back nine before slipping one back at the finish, sitting alone in second at 14 under.</p>

          <h2>The 12-Under Chasing Pack</h2>
          <p>Scottie Scheffler delivered exactly what he needed: a bogey-free 66 to reach 12 under, firmly in the mix. Ludvig Åberg closed with three straight birdies to join him. Adam Scott, at 45 years old, fired a 65 to enter the final round three shots back alongside Brad Gotterup.</p>

          <h2>McIlroy's 63: The Turnaround</h2>
          <p>Rory McIlroy produced the round of the day, tying his lowest career score at East Lake with a 63. He poured in nine birdies and completely reversed his putting woes, gaining over 3 strokes on the greens to reach 10 under, tied with Cameron Young.</p>

          <h2>The Stat That Matters</h2>
          <p>East Lake is yielding numbers. For the first time all week, <b>all 29 players in the field are under par</b>. There has been zero attrition. Sunday will not be a survival test; it will be a pure birdie race.</p>

          <h2>Broadcast Times and the Prize</h2>
          <p>Early coverage streams on ESPN+ and Peacock. Golf Channel picks up the broadcast from noon to 1:30 PM ET, leading into the main CBS broadcast from 1:30 PM to 6:00 PM ET. At stake is a $10 million winner's check from the official $40 million purse and a five-year PGA Tour exemption.</p>

          <h2>Debunking Final Round Myths</h2>
          <ul>
            <li><i>Myth 1: The leader always wins at East Lake.</i> The history of the staggered start is short, and leads have evaporated here before.</li>
            <li><i>Myth 2: You can't come from five back.</i> Tell that to Rory McIlroy in 2022.</li>
            <li><i>Myth 3: The course gets impossible on Sunday.</i> Soft conditions mean scoring will remain low.</li>
            <li><i>Myth 4: Experience dominates.</i> Gerard and Åberg are disproving this in real time.</li>
          </ul>

          <div class="verdict-box">
            <h3>The Raw Verdict</h3>
            <p>Hovland is in the driver's seat, but Scheffler lurking at 12 under is the real threat. If Hovland's driver behaves, he wins. If he misses fairways early, the 12-under pack will swallow him.</p>
          </div>
          
          <section class="sources" aria-labelledby="faq-label">
            <h2 id="faq-label" style="font-size: 1.25rem; font-family: 'IBM Plex Mono', monospace; text-transform: uppercase;">FAQ</h2>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">Who leads the Tour Championship?</h3>
              <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">Viktor Hovland leads at 15 under par heading into the final round.</p>
              </div>
            </div>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">What is the winner's prize?</h3>
              <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">The winner receives $10 million from the official $40 million purse and a 5-year PGA Tour exemption.</p>
              </div>
            </div>
          </section>

          <section class="sources" aria-labelledby="sources-label">
            <p class="section-label" id="sources-label">Sources</p>
            <ol>
              <li><a href="/news">GOLFRAW: Latest News</a>. The live reporting index for current tournament updates.</li>
              <li><a href="/tournaments">GOLFRAW: Tournament coverage</a>. East Lake leaderboard and event context.</li>
              <li><a href="/news-2026-tour-championship-tee-times-round-4">Sunday Tee Times</a>. Full Round 4 pairings and starting times.</li>
              <li><a href="/news-2026-cameron-young-new-putter-62-tour-championship">Cameron Young's 62</a>. Analysis of his putter change and low round.</li>
              <li><a href="/news-2026-hovland-tie-for-lead-tour-championship">Hovland's Round 2</a>. Context on his 12-of-14 fairways performance.</li>
            </ol>
          </section>

          <div class="provenance">
            <p><strong>Article history.</strong> Published <time datetime="2026-08-30T10:00:00+02:00">30 August 2026 at 10:00 CEST</time>.</p>
            <p><strong>Corrections.</strong> None at publication. <a href="/corrections">Corrections policy</a>.</p>
            <p><strong>Last updated.</strong> <time datetime="2026-08-30T10:00:00+02:00">30 August 2026 at 10:00 CEST</time>.</p>
          </div>

          <aside class="related" aria-label="Related GolfRaw reporting">
            <p class="section-label" style="color:#b8d2c5">Keep reading</p>
            <ul>
              <li><a href="/news-2026-tour-championship-tee-times-round-4">Sunday Tee Times</a></li>
              <li><a href="/news-2026-cameron-young-new-putter-62-tour-championship">Cameron Young shoots 62</a></li>
              <li><a href="/news-2026-hovland-tie-for-lead-tour-championship">Hovland's Round 2</a></li>
            </ul>
          </aside>

        </div>
"""

# Replace body
html = re.sub(r'<div class="article-body">.*?</main>', new_body + '\n</article>\n</main>', html, flags=re.DOTALL)

# JSON-LD Schema
json_ld = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "NewsArticle",
      "@id": "https://www.golfraw.com/news-2026-tour-championship-final-round-hovland-leads#article",
      "headline": "Tour Championship Final Round: Hovland Leads by One | GOLFRAW",
      "name": "Tour Championship Final Round: Hovland Leads by One | GOLFRAW",
      "description": "Hovland leads by one at 15 under, Scheffler's three back, McIlroy shot 63. Every number that matters before the final round of the season.",
      "articleSection": "Tournaments",
      "keywords": "Viktor Hovland, Tour Championship Final Round, Scottie Scheffler, Rory McIlroy 63, East Lake",
      "datePublished": "2026-08-30T10:00:00+02:00",
      "dateModified": "2026-08-30T10:00:00+02:00",
      "inLanguage": "en",
      "image": {
        "@type": "ImageObject",
        "url": "https://www.golfraw.com/public/tour-championship-final-round-hovland-leads-2026.webp",
        "contentUrl": "https://www.golfraw.com/public/tour-championship-final-round-hovland-leads-2026.webp",
        "width": 1200,
        "height": 675,
        "caption": "Viktor Hovland celebrating a birdie putt on the 17th green at East Lake during Round 3 of the 2026 Tour Championship."
      },
      "author": {"@id": "https://www.golfraw.com/about#editorial"},
      "publisher": {"@id": "https://www.golfraw.com#organization"},
      "about": [
        {"@type": "Thing", "name": "Tour Championship"},
        {"@type": "Thing", "name": "Viktor Hovland"}
      ]
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://www.golfraw.com/news-2026-tour-championship-final-round-hovland-leads#breadcrumb",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.golfraw.com/"},
        {"@type": "ListItem", "position": 2, "name": "News", "item": "https://www.golfraw.com/news"},
        {"@type": "ListItem", "position": 3, "name": "Tour Championship Final Round Hovland Leads", "item": "https://www.golfraw.com/news-2026-tour-championship-final-round-hovland-leads"}
      ]
    },
    {"@type": "Person", "@id": "https://www.golfraw.com/about#editorial", "name": "GOLFRAW Editorial", "url": "https://www.golfraw.com/about"},
    {"@type": "Organization", "@id": "https://www.golfraw.com#organization", "name": "GOLFRAW", "url": "https://www.golfraw.com/"},
    {
      "@type": "FAQPage",
      "@id": "https://www.golfraw.com/news-2026-tour-championship-final-round-hovland-leads#faq",
      "mainEntity": [
        {"@type": "Question", "name": "Who leads the Tour Championship?", "acceptedAnswer": {"@type": "Answer", "text": "Viktor Hovland leads at 15 under par heading into the final round."}},
        {"@type": "Question", "name": "What is the winner's prize?", "acceptedAnswer": {"@type": "Answer", "text": "The winner receives $10 million from the official $40 million purse and a 5-year PGA Tour exemption."}}
      ]
    }
  ]
}
</script>"""

# Find the end of <head> or replace existing ld+json
if '<script type="application/ld+json">' in html:
    html = re.sub(r'<script type="application/ld\+json">.*?</script>', json_ld, html, flags=re.DOTALL)
else:
    html = html.replace('</head>', json_ld + '\n</head>')

with open('news-2026-tour-championship-final-round-hovland-leads.html', 'w') as f:
    f.write(html)
