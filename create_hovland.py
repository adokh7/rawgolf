import json, re
from scripts.article_header import (
    finalize_article_template_metadata,
    replace_article_header,
)

with open('article-template.html', 'r') as f:
    html = f.read()

# 1. Header & Metadata
title = "Hovland's One-Shot Lead Came From Six Straight Putts | GOLFRAW"
description = "Six putts from seven feet or longer built it. Scheffler, Scott, Åberg and Gotterup are three back, McIlroy shot 63, and last place is 3 under."
canonical_url = "https://www.golfraw.com/news-2026-hovland-one-shot-lead-tour-championship"
image_asset = "/public/hovland-one-shot-lead-tour-championship-2026.webp"

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
          <img src="/public/hovland-one-shot-lead-tour-championship-2026.webp" alt="Viktor Hovland putting on the 15th peninsula green at East Lake during the third round of the 2026 Tour Championship." width="1200" height="675" style="aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:8px;">
          <figcaption>VIKTOR HOVLAND HOLDS A ONE-SHOT LEAD AT EAST LAKE HEADING INTO SUNDAY AFTER CLOSING WITH SIX CONSECUTIVE PUTTS FROM SEVEN FEET OR LONGER. PHOTO: RAWGOLF</figcaption>
        </figure>
"""
if '<figure class="lead-img">' in html:
    html = re.sub(r'<figure class="lead-img">.*?</figure>', hero_html, html, flags=re.DOTALL)
else:
    html = html.replace('</header>', '</header>\n' + hero_html)

new_vis_bc = """<nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/news">News</a> / <a href="/tournaments">Tournaments</a> / <span>Hovland One-Shot Lead</span>
        </nav>"""
html = re.sub(r'<nav class="crumbs".*?</nav>', new_vis_bc, html, flags=re.DOTALL)

html = replace_article_header(
    html,
    "Hovland's One-Shot Lead Came From Six Straight Putts",
    description,
)

new_body = """<div class="article-body">
          <div class="takeaways">
            <h3 style="margin-top:0;">Key Takeaways</h3>
            <ul>
              <li><b>Viktor Hovland (-15)</b> saved his round with a phenomenal putting clinic on the final six holes.</li>
              <li><b>Rory McIlroy (-10)</b> vaulted up the board with a 63, tying his career low at East Lake.</li>
              <li><b>Scottie Scheffler (-12)</b> sits three back, battling putter frustration but looming ominously.</li>
              <li><b>A Historic Birdie Fest:</b> The entire 29-player field is under par, with last place sitting at -3.</li>
            </ul>
          </div>

          <h2>Leaderboard Standings</h2>
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>Player</th>
                  <th>Total</th>
                  <th>Round 3</th>
                  <th>Key Stat</th>
                </tr>
              </thead>
              <tbody>
                <tr><td>Viktor Hovland</td><td>-15</td><td>66</td><td>6 putts > 7ft on final 6 holes</td></tr>
                <tr><td>Ryan Gerard</td><td>-14</td><td>66</td><td>Bogey-free Round 3</td></tr>
                <tr><td>Scottie Scheffler</td><td>-12</td><td>66</td><td>Bogey-free, missed several 8-12ft putts</td></tr>
                <tr><td>Brad Gotterup</td><td>-12</td><td>68</td><td>-2 on Saturday</td></tr>
                <tr><td>Adam Scott</td><td>-12</td><td>65</td><td>45 years old</td></tr>
                <tr><td>Ludvig Åberg</td><td>-12</td><td>65</td><td>3 straight birdies to finish</td></tr>
                <tr><td>Rory McIlroy</td><td>-10</td><td>63</td><td>+3.0 SG: Putting</td></tr>
                <tr><td>Cameron Young</td><td>-10</td><td>68</td><td>Double bogey on 10th hole</td></tr>
              </tbody>
            </table>
          </div>

          <h2>The Six-Putt Survival Clinic</h2>
          <p>Viktor Hovland’s ball-striking was flawless on Friday, but Saturday was a grind. He sprayed his driver early and missed a crucial bunker save on the 4th hole. However, he constructed a one-shot lead entirely with his flatstick on the back nine. Starting on the 13th, Hovland poured in an 11-foot birdie, an 18-foot par save on 14, an 11-foot birdie on the peninsula 15th, a 7-foot par save on 16, and back-to-back 8-foot birdies on 17 and 18. Six consecutive putts from outside seven feet sealed a 66.</p>

          <h2>The 12-Under Chasing Pack</h2>
          <p>Scottie Scheffler sits three shots back at 12 under par. Despite a bogey-free 66, he looked visibly frustrated on the greens, missing multiple 8-to-12-foot birdie opportunities. A win on Sunday wouldn't just secure the FedExCup; it would propel Scheffler past a major career earnings milestone set by Tiger Woods. Joining him at 12 under are Chris Gotterup (who, combined with Scheffler, accounts for five PGA Tour titles in <a href="/news-2026-pga-tour-winners-2026">the 2026 season</a>), Ludvig Åberg following a 65, and Adam Scott, who continues to defy his 45 years of age.</p>

          <h2>McIlroy’s 63 and the Unprecedented Scoring</h2>
          <p>Rory McIlroy shot the round of the day, a 63 featuring nine birdies. It vaulted him to 10 under par. The score highlighted a bizarre reality at East Lake following Andrew Green's post-2023 course restoration and this week's soft conditions: scoring is entirely undefended. The leaderboard is historically congested, with the player in dead last place sitting at 3 under par.</p>

          <h2>Cameron Young’s Stalled Momentum</h2>
          <p>After a <a href="/news-2026-cameron-young-new-putter-62-tour-championship">blistering 62 on Friday</a>, Cameron Young struggled to maintain his surge. His momentum came to a crashing halt with a double bogey on the 10th hole, leading to a 68 that dropped him into a tie with McIlroy at 10 under par.</p>

          <h2>Financial and FedExCup Stakes</h2>
          <p>Unlike previous years with staggered starts padding an $18 million bonus pool, the 2026 Tour Championship returns to official money. The winner receives a staggering $10 million from the $40 million purse and a five-year PGA Tour exemption.</p>

          <h2>Debunking 4 Moving Day Myths</h2>
          <ul>
            <li><i>Myth 1: A one-shot lead is secure at East Lake.</i> False. With the entire field under par, a one-shot lead is meaningless.</li>
            <li><i>Myth 2: Scheffler's putter is broken again.</i> False. He didn't make everything, but a bogey-free 66 requires solid scrambling.</li>
            <li><i>Myth 3: The course is playing harder after the restoration.</i> False. Last place is 3 under par; the course is completely vulnerable.</li>
            <li><i>Myth 4: Cameron Young is out of it.</i> False. Five shots back on a course yielding 62s and 63s means he is very much alive.</li>
          </ul>

          <div class="verdict-box">
            <h3>The Raw Verdict</h3>
            <p>Hovland’s putting display was heroic, but it’s not a repeatable formula. If he doesn't find his driver on Sunday, Scheffler or McIlroy will run him down on a golf course that is practically begging players to shoot 64.</p>
          </div>
          
          <section class="sources" aria-labelledby="faq-label">
            <h2 id="faq-label" style="font-size: 1.25rem; font-family: 'IBM Plex Mono', monospace; text-transform: uppercase;">FAQ</h2>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">How many consecutive putts did Viktor Hovland make to close his round?</h3>
              <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">Viktor Hovland made six consecutive putts from seven feet or longer on his final six holes.</p>
              </div>
            </div>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">What is the score of the last place player at the Tour Championship?</h3>
              <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">The player in last place is currently 3 under par.</p>
              </div>
            </div>
          </section>

          <section class="sources" aria-labelledby="sources-label">
            <p class="section-label" id="sources-label">Sources</p>
            <ol>
              <li><a href="/news">GOLFRAW: Latest News</a>. The live reporting index for current tournament updates.</li>
              <li><a href="/news-2026-pga-tour-winners-2026">2026 PGA Tour Winners</a>. Full season archives and statistics.</li>
              <li><a href="/news-2026-tour-championship-tee-times-round-4">Sunday Tee Times</a>. Final round pairings for the 2026 finale.</li>
              <li><a href="/news-2026-cameron-young-new-putter-62-tour-championship">Cameron Young shoots 62</a>. A look at the Valero Texas Open winner's late-season form.</li>
            </ol>
          </section>

          <div class="provenance">
            <p><strong>Article history.</strong> Published <time datetime="2026-08-30T15:00:00+02:00">30 August 2026 at 15:00 CEST</time>.</p>
            <p><strong>Corrections.</strong> None at publication. <a href="/corrections">Corrections policy</a>.</p>
            <p><strong>Last updated.</strong> <time datetime="2026-08-30T15:00:00+02:00">30 August 2026 at 15:00 CEST</time>.</p>
          </div>

          <aside class="related" aria-label="Related GolfRaw reporting">
            <p class="section-label" style="color:#b8d2c5">Keep reading</p>
            <ul>
              <li><a href="/news-2026-pga-tour-winners-2026">2026 PGA Tour Winners Recap</a></li>
              <li><a href="/news-2026-tour-championship-tee-times-round-4">Tour Championship Sunday Tee Times</a></li>
              <li><a href="/news-2026-cameron-young-new-putter-62-tour-championship">Cameron Young's 62 at East Lake</a></li>
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
      "@id": "https://www.golfraw.com/news-2026-hovland-one-shot-lead-tour-championship#article",
      "headline": "Hovland's One-Shot Lead Came From Six Straight Putts | GOLFRAW",
      "name": "Hovland's One-Shot Lead Came From Six Straight Putts | GOLFRAW",
      "description": "Six putts from seven feet or longer built it. Scheffler, Scott, Åberg and Gotterup are three back, McIlroy shot 63, and last place is 3 under.",
      "articleSection": "Tournaments",
      "keywords": "Viktor Hovland, Tour Championship, Scottie Scheffler, Rory McIlroy 63, East Lake, PGA Tour",
      "datePublished": "2026-08-30T15:00:00+02:00",
      "dateModified": "2026-08-30T15:00:00+02:00",
      "inLanguage": "en",
      "image": {
        "@type": "ImageObject",
        "url": "https://www.golfraw.com/public/hovland-one-shot-lead-tour-championship-2026.webp",
        "contentUrl": "https://www.golfraw.com/public/hovland-one-shot-lead-tour-championship-2026.webp",
        "width": 1200,
        "height": 675,
        "caption": "Viktor Hovland putting on the 15th peninsula green at East Lake during the third round of the 2026 Tour Championship."
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
      "@id": "https://www.golfraw.com/news-2026-hovland-one-shot-lead-tour-championship#breadcrumb",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.golfraw.com/"},
        {"@type": "ListItem", "position": 2, "name": "News", "item": "https://www.golfraw.com/news"},
        {"@type": "ListItem", "position": 3, "name": "Hovland One-Shot Lead", "item": "https://www.golfraw.com/news-2026-hovland-one-shot-lead-tour-championship"}
      ]
    },
    {"@type": "Person", "@id": "https://www.golfraw.com/about#editorial", "name": "GOLFRAW Editorial", "url": "https://www.golfraw.com/about"},
    {"@type": "Organization", "@id": "https://www.golfraw.com#organization", "name": "GOLFRAW", "url": "https://www.golfraw.com/"},
    {
      "@type": "FAQPage",
      "@id": "https://www.golfraw.com/news-2026-hovland-one-shot-lead-tour-championship#faq",
      "mainEntity": [
        {"@type": "Question", "name": "How many consecutive putts did Viktor Hovland make to close his round?", "acceptedAnswer": {"@type": "Answer", "text": "Viktor Hovland made six consecutive putts from seven feet or longer on his final six holes."}},
        {"@type": "Question", "name": "What is the score of the last place player at the Tour Championship?", "acceptedAnswer": {"@type": "Answer", "text": "The player in last place is currently 3 under par."}}
      ]
    }
  ]
}
</script>"""

if '<script type="application/ld+json">' in html:
    html = re.sub(r'<script type="application/ld\+json">.*?</script>', json_ld, html, flags=re.DOTALL)
else:
    html = html.replace('</head>', json_ld + '\n</head>')

html = finalize_article_template_metadata(html)

with open('news-2026-hovland-one-shot-lead-tour-championship.html', 'w') as f:
    f.write(html)
