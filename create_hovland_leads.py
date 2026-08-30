import json, re

with open('article-template.html', 'r') as f:
    html = f.read()

# 1. Header & Metadata
title = "Hovland Leads the Tour Championship by One Into Sunday | GOLFRAW"
description = "He closed with six putts from 7 feet or longer to lead by one. Scheffler's three back, McIlroy shot 63, and nobody agrees on Sunday's tee times."
canonical_url = "https://www.golfraw.com/news-2026-hovland-leads-tour-championship-final-day"
image_asset = "/public/hovland-leads-tour-championship-final-day-2026.webp"

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
html = html.replace('<div class="wrap page-grid">', '<div class="wrap page-grid" style="padding-top: 40px;">')

hero_html = """
        <figure class="lead-img">
          <img src="/public/hovland-leads-tour-championship-final-day-2026.webp" alt="Viktor Hovland reading a birdie putt on the 17th green at East Lake during Round 3 of the 2026 Tour Championship." width="1200" height="675" style="aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:8px;">
          <figcaption>VIKTOR HOVLAND HOLDS A ONE-SHOT LEAD OVER RYAN GERARD AFTER CLOSING WITH SIX STRAIGHT PUTTS FROM SEVEN FEET OR LONGER. PHOTO: RAWGOLF</figcaption>
        </figure>
"""
if '<figure class="lead-img">' in html:
    html = re.sub(r'<figure class="lead-img">.*?</figure>', hero_html, html, flags=re.DOTALL)
else:
    html = html.replace('</header>', '</header>\n' + hero_html)

new_vis_bc = """<nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/news">News</a> / <a href="/tournaments">Tournaments</a> / <span>Hovland Leads Tour Championship Final Day</span>
        </nav>"""
html = re.sub(r'<nav class="crumbs".*?</nav>', new_vis_bc, html, flags=re.DOTALL)

html = re.sub(r'<h1 class="headline">.*?</h1>', '<h1 class="headline">Hovland Leads the Tour Championship by One Into Sunday</h1>', html, flags=re.DOTALL)
html = re.sub(r'<h2 class="subhead">.*?</h2>', '<h2 class="subhead">He closed with six putts from 7 feet or longer to lead by one. Scheffler\'s three back, McIlroy shot 63, and nobody agrees on Sunday\'s tee times.</h2>', html, flags=re.DOTALL)

new_body = """<div class="article-body">
          <div class="takeaways">
            <h3 style="margin-top:0;">Key Takeaways</h3>
            <ul>
              <li><b>Viktor Hovland (-15)</b> survived a shaky swing by making his last six putts from outside seven feet.</li>
              <li><b>Ryan Gerard (-14)</b> shot a bogey-free 66 in his first Tour Championship final group.</li>
              <li><b>Scottie Scheffler (-12)</b> sits three back despite playing through the aftereffects of hand, foot, and mouth disease.</li>
              <li><b>Rory McIlroy (-10)</b> fired a career-low 63 at East Lake, gaining 3 strokes putting.</li>
              <li><b>The Tee Time Mystery</b>: Competing published tee sheets show either a 1:50 PM or 2:55 PM start for the final group.</li>
            </ul>
          </div>

          <h2>Leaderboard & Chasers Comparison</h2>
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>Player</th>
                  <th>Score</th>
                  <th>Round 3</th>
                  <th>To Par</th>
                </tr>
              </thead>
              <tbody>
                <tr><td>Viktor Hovland</td><td>-15</td><td>66</td><td>-4</td></tr>
                <tr><td>Ryan Gerard</td><td>-14</td><td>66</td><td>-4</td></tr>
                <tr><td>Scottie Scheffler</td><td>-12</td><td>66</td><td>-4</td></tr>
                <tr><td>Brad Gotterup</td><td>-12</td><td>68</td><td>-2</td></tr>
                <tr><td>Adam Scott</td><td>-12</td><td>65</td><td>-5</td></tr>
                <tr><td>Ludvig Åberg</td><td>-12</td><td>66</td><td>-4</td></tr>
                <tr><td>Rory McIlroy</td><td>-10</td><td>63</td><td>-7</td></tr>
                <tr><td>Cameron Young</td><td>-10</td><td>68</td><td>-2</td></tr>
              </tbody>
            </table>
          </div>

          <h2>Hovland’s Clutch Putting Finish</h2>
          <p><a href="/news-2026-hovland-tie-for-lead-tour-championship">After hitting 12 of 14 fairways on Friday to claim a share of the lead</a>, Viktor Hovland spent Saturday fighting his swing. He missed a crucial bunker save at the 4th, but what saved his round—and the outright 54-hole lead—was his putter. He closed his round by holing six consecutive putts from 7 feet or longer, including four clutch birdies and two essential pars to card a 66 and reach 15 under.</p>

          <h2>Ryan Gerard's Overlooked Performance</h2>
          <p>Playing in the final group of the Tour Championship for the first time, 27-year-old Ryan Gerard looked anything but overwhelmed. He delivered a flawless, bogey-free 66, matching Hovland shot-for-shot for most of the back nine and securing his spot in Sunday's final pairing at 14 under.</p>

          <h2>The 12-Under Chasing Pack</h2>
          <p>Scottie Scheffler arrived at East Lake dealing with the lingering effects of hand, foot, and mouth disease, but it hasn't broken him. He shot a bogey-free 66 to reach 12 under. Ludvig Åberg finished his round with three straight birdies to join the tie at 12 under, alongside Adam Scott, who shot 65, and Brad Gotterup.</p>

          <h2>McIlroy's 63: A Complete Reversal</h2>
          <p>Rory McIlroy produced the round of the day, tying his lowest career score at East Lake with a 63. He poured in nine birdies and completely reversed his putting woes, gaining over 3 strokes on the greens (SG: Putting). He now sits tied with Cameron Young (who <a href="/news-2026-cameron-young-new-putter-62-tour-championship">shot 62 earlier in the week</a>) at 10 under par.</p>

          <h2>The Conflicting Tee Sheets Mystery</h2>
          <p>There is currently total disagreement over when the final round will begin. The official Golf Channel broadcast draw shows an 11:55 AM start, with the leaders teeing off at 2:55 PM. However, Golf.com and other outlets published a revised draw indicating a 10:50 AM start with a 1:50 PM final pairing, presumably due to weather concerns. Check the <a href="/news-2026-tour-championship-tee-times-round-4">Sunday Tee Times</a> page for updates.</p>

          <h2>Financial Stakes & The Field's Vulnerability</h2>
          <p>This year’s winner takes home $10 million from an official $40 million purse. This is a sharp contrast from the $18 million FedExCup bonus pool awarded in 2023 under the previous staggered-start format. And with all 29 players under par on an accessible East Lake setup, a 62 or 63 from the chasing pack is a highly realistic threat.</p>

          <h2>Fact-Checking Final Round Myths</h2>
          <ul>
            <li><i>Myth 1: The leader always wins at East Lake.</i> False. Without the staggered start advantage, a one-shot lead is nothing.</li>
            <li><i>Myth 2: You can't come from five back.</i> False. Rory McIlroy erased a six-shot deficit in 2022.</li>
            <li><i>Myth 3: The course gets impossible on Sunday.</i> False. Soft conditions mean scoring will remain low, and all 29 players are already under par.</li>
            <li><i>Myth 4: Experience dominates.</i> False. Gerard and Åberg are contending in real time against veterans.</li>
          </ul>

          <div class="verdict-box">
            <h3>The Raw Verdict</h3>
            <p>Hovland’s putter bailed him out on Saturday, but relying on 10-footers for par is not a sustainable Sunday strategy with Scheffler and McIlroy lurking. He needs his Friday ball-striking to return if he wants to win $10 million.</p>
          </div>
          
          <section class="sources" aria-labelledby="faq-label">
            <h2 id="faq-label" style="font-size: 1.25rem; font-family: 'IBM Plex Mono', monospace; text-transform: uppercase;">FAQ</h2>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">Who leads the Tour Championship heading into Sunday?</h3>
              <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">Viktor Hovland leads by one shot at 15 under par over Ryan Gerard.</p>
              </div>
            </div>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">What is the winner's prize at the 2026 Tour Championship?</h3>
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
              <li><a href="/news-2026-tour-championship-tee-times-round-4">Sunday Tee Times</a>. Full Round 4 pairings and start times.</li>
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

html = re.sub(r'<div class="article-body">.*?</main>', new_body + '\n</article>\n</main>', html, flags=re.DOTALL)

json_ld = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "NewsArticle",
      "@id": "https://www.golfraw.com/news-2026-hovland-leads-tour-championship-final-day#article",
      "headline": "Hovland Leads the Tour Championship by One Into Sunday | GOLFRAW",
      "name": "Hovland Leads the Tour Championship by One Into Sunday | GOLFRAW",
      "description": "He closed with six putts from 7 feet or longer to lead by one. Scheffler's three back, McIlroy shot 63, and nobody agrees on Sunday's tee times.",
      "articleSection": "Tournaments",
      "keywords": "Viktor Hovland, Tour Championship Final Round, Scottie Scheffler, Rory McIlroy 63, Ryan Gerard, East Lake",
      "datePublished": "2026-08-30T10:00:00+02:00",
      "dateModified": "2026-08-30T10:00:00+02:00",
      "inLanguage": "en",
      "image": {
        "@type": "ImageObject",
        "url": "https://www.golfraw.com/public/hovland-leads-tour-championship-final-day-2026.webp",
        "contentUrl": "https://www.golfraw.com/public/hovland-leads-tour-championship-final-day-2026.webp",
        "width": 1200,
        "height": 675,
        "caption": "Viktor Hovland reading a birdie putt on the 17th green at East Lake during Round 3 of the 2026 Tour Championship."
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
      "@id": "https://www.golfraw.com/news-2026-hovland-leads-tour-championship-final-day#breadcrumb",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.golfraw.com/"},
        {"@type": "ListItem", "position": 2, "name": "News", "item": "https://www.golfraw.com/news"},
        {"@type": "ListItem", "position": 3, "name": "Hovland Leads Tour Championship Final Day", "item": "https://www.golfraw.com/news-2026-hovland-leads-tour-championship-final-day"}
      ]
    },
    {"@type": "Person", "@id": "https://www.golfraw.com/about#editorial", "name": "GOLFRAW Editorial", "url": "https://www.golfraw.com/about"},
    {"@type": "Organization", "@id": "https://www.golfraw.com#organization", "name": "GOLFRAW", "url": "https://www.golfraw.com/"},
    {
      "@type": "FAQPage",
      "@id": "https://www.golfraw.com/news-2026-hovland-leads-tour-championship-final-day#faq",
      "mainEntity": [
        {"@type": "Question", "name": "Who leads the Tour Championship heading into Sunday?", "acceptedAnswer": {"@type": "Answer", "text": "Viktor Hovland leads by one shot at 15 under par over Ryan Gerard."}},
        {"@type": "Question", "name": "What is the winner's prize at the 2026 Tour Championship?", "acceptedAnswer": {"@type": "Answer", "text": "The winner receives $10 million from the official $40 million purse and a 5-year PGA Tour exemption."}}
      ]
    }
  ]
}
</script>"""

if '<script type="application/ld+json">' in html:
    html = re.sub(r'<script type="application/ld\+json">.*?</script>', json_ld, html, flags=re.DOTALL)
else:
    html = html.replace('</head>', json_ld + '\n</head>')

with open('news-2026-hovland-leads-tour-championship-final-day.html', 'w') as f:
    f.write(html)
