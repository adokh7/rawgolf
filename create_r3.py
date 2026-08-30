import json, re

with open('article-template.html', 'r') as f:
    html = f.read()

# 1. Header & Metadata
title = "Tour Championship Round 3: Hovland's 65 and Every Score | GOLFRAW"
description = "Nineteen players began Saturday within five shots and it ended with a one-shot lead. Full Round 3 draw, results, and the Sunday sheet nobody agrees on."
canonical_url = "https://www.golfraw.com/news-2026-tour-championship-round-3-tee-times-leaderboard"
image_asset = "/public/tour-championship-2026-round-3-tee-times-leaderboard.webp"

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
          <img src="/public/tour-championship-2026-round-3-tee-times-leaderboard.webp" alt="The first tee and tournament scoreboard at East Lake during Moving Day Round 3 of the 2026 Tour Championship." width="1200" height="675" style="aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:8px;">
          <figcaption>VIKTOR HOVLAND HOLDS A ONE-SHOT LEAD AFTER SATURDAY'S THIRD ROUND AT EAST LAKE AS ALL 29 PLAYERS REMAIN UNDER PAR. PHOTO: RAWGOLF</figcaption>
        </figure>
"""
if '<figure class="lead-img">' in html:
    html = re.sub(r'<figure class="lead-img">.*?</figure>', hero_html, html, flags=re.DOTALL)
else:
    html = html.replace('</header>', '</header>\n' + hero_html)

new_vis_bc = """<nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/news">News</a> / <a href="/tournaments">Tournaments</a> / <span>Tour Championship Round 3 Recap</span>
        </nav>"""
html = re.sub(r'<nav class="crumbs".*?</nav>', new_vis_bc, html, flags=re.DOTALL)

html = re.sub(r'<h1 class="headline">.*?</h1>', '<h1 class="headline">Tour Championship Round 3: Hovland\'s 65 and Every Score</h1>', html, flags=re.DOTALL)
html = re.sub(r'<h2 class="subhead">.*?</h2>', '<h2 class="subhead">Nineteen players began Saturday within five shots and it ended with a one-shot lead. Full Round 3 draw, results, and the Sunday sheet nobody agrees on.</h2>', html, flags=re.DOTALL)

new_body = """<div class="article-body">
          <div class="takeaways">
            <h3 style="margin-top:0;">Key Takeaways</h3>
            <ul>
              <li><b>Viktor Hovland</b> fired a 65, holing six putts outside 7 feet down the stretch to secure a one-shot 54-hole lead at 15 under.</li>
              <li><b>Rory McIlroy</b> delivered the round of the day with a 63 (9 birdies), erasing his putting struggles by gaining over 3 strokes on the greens.</li>
              <li><b>Ryan Gerard</b> posted a bogey-free 66 in the final group, remaining just one shot back at 14 under.</li>
              <li><b>All 29 players</b> remain under par, turning East Lake into an uncharacteristic birdie sprint.</li>
              <li><b>The Tee Sheet Discrepancy</b>: Sunday's official draw is currently disputed between published sources, hinting at early weather revisions.</li>
            </ul>
          </div>

          <h2>The Pre-Round Chaos</h2>
          <p>Saturday began with a highly condensed leaderboard: 19 players were positioned within five shots of the lead. The level-start format guaranteed an aggressive Moving Day, and East Lake's softer conditions delivered an outright birdie race.</p>

          <h2>Full Round 3 Tee Times</h2>
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>Tee Time (ET)</th>
                  <th>Players</th>
                </tr>
              </thead>
              <tbody>
                <tr><td>11:55 AM</td><td>Robert MacIntyre</td></tr>
                <tr><td>12:05 PM</td><td>Keegan Bradley, Tom Hoge</td></tr>
                <tr><td>12:15 PM</td><td>Christiaan Bezuidenhout, Brian Harman</td></tr>
                <tr><td>12:25 PM</td><td>Tony Finau, Russell Henley</td></tr>
                <tr><td>12:35 PM</td><td>Justin Thomas, Byeong Hun An</td></tr>
                <tr><td>12:45 PM</td><td>Corey Conners, Sungjae Im</td></tr>
                <tr><td>12:55 PM</td><td>Aaron Rai, Shane Lowry</td></tr>
                <tr><td>1:05 PM</td><td>Justin Rose, Sepp Straka</td></tr>
                <tr><td>1:15 PM</td><td>Hideki Matsuyama, Patrick Cantlay</td></tr>
                <tr><td>2:05 PM</td><td>Xander Schauffele, Billy Horschel</td></tr>
                <tr><td>2:16 PM</td><td>Rory McIlroy, Ludvig Åberg</td></tr>
                <tr><td>2:27 PM</td><td>Adam Scott, Scottie Scheffler</td></tr>
                <tr><td>2:37 PM</td><td>Chris Gotterup, Cameron Young</td></tr>
                <tr><td colspan="2"><i>18-minute gap</i></td></tr>
                <tr><td>2:55 PM</td><td>Ryan Gerard, Viktor Hovland</td></tr>
              </tbody>
            </table>
          </div>

          <h2>Round 3 Breakdown: Hovland & Gerard Hold Firm</h2>
          <p>Viktor Hovland fought his swing early but was bailed out by exceptional clutch putting. He closed by holing six consecutive putts from 7+ feet—including crucial par saves and birdies at 13, 14, and 17—to post a 65 and reach 15 under. Right beside him, 27-year-old Ryan Gerard remained unflappable, shooting a bogey-free 66 to sit at 14 under. Meanwhile, Ludvig Åberg birdied his final three holes to join the chase.</p>

          <h2>Rory McIlroy's Historic 63</h2>
          <p>McIlroy produced the round of the day, a 63 featuring nine birdies. It ties his lowest career round at East Lake. The difference? A massive putting turnaround, where he gained over +3 strokes on the greens, completely erasing the struggles that plagued his first two days.</p>

          <h2>Saturday Broadcast Schedule</h2>
          <p>The Round 3 broadcast began on PGA Tour Live at 12:15 PM ET, moving to Golf Channel from 1:00 PM to 3:00 PM ET, and concluding on CBS from 3:00 PM to 7:00 PM ET. Early streaming coverage remains restricted for marquee groups until the main network windows.</p>

          <h2>The Sunday Tee Sheet Discrepancy</h2>
          <p>As Round 3 concluded, a bizarre discrepancy emerged regarding Sunday's final round. The Golf Channel republished the Saturday draw (an 11:55 AM start, with the final group at 2:55 PM). Conversely, Golf.com and other outlets released an early weather-revised draw beginning at 10:50 AM with leaders off at 1:50 PM. Check our <a href="/news-2026-tour-championship-final-round-hovland-leads">final round preview</a> for the latest updates on when play actually begins.</p>

          <h2>Financial and Historical Stakes</h2>
          <p>This is a $40 million official purse event with a $10 million winner’s check. This starkly contrasts Hovland's 2023 victory, where he claimed an $18 million FedExCup bonus pool payout under the heavily criticized staggered-starts format.</p>

          <h2>Fact-Checking 4 Moving Day Myths</h2>
          <ul>
            <li><i>Myth 1: Hovland is pulling away.</i> False. A one-shot lead on a soft golf course with 19 players within striking distance is volatile.</li>
            <li><i>Myth 2: McIlroy's 63 was pure ball-striking.</i> False. While his irons were elite, his flatstick (+3 SG: Putting) drove the score.</li>
            <li><i>Myth 3: East Lake is playing like a par 72.</i> False. It's a par 70, but soft conditions have effectively neutered its defenses, keeping all 29 players under par.</li>
            <li><i>Myth 4: Starting strokes dictated this leaderboard.</i> False. This is a level-start 72-hole stroke play event; the scoreboard reflects pure golf played this week.</li>
          </ul>

          <div class="verdict-box">
            <h3>The Raw Verdict</h3>
            <p>Saturday proved that no lead is safe. With McIlroy discovering his putter and Gerard refusing to fade, Hovland cannot afford to spray his driver on Sunday. The $10 million check will require another 65.</p>
          </div>
          
          <section class="sources" aria-labelledby="faq-label">
            <h2 id="faq-label" style="font-size: 1.25rem; font-family: 'IBM Plex Mono', monospace; text-transform: uppercase;">FAQ</h2>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">Who leads after Round 3 of the Tour Championship?</h3>
              <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">Viktor Hovland leads by one shot at 15 under par after shooting a 65.</p>
              </div>
            </div>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">What did Rory McIlroy shoot in Round 3?</h3>
              <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">Rory McIlroy shot a 63 with 9 birdies, tying his career-low round at East Lake.</p>
              </div>
            </div>
          </section>

          <section class="sources" aria-labelledby="sources-label">
            <p class="section-label" id="sources-label">Sources</p>
            <ol>
              <li><a href="/news">GOLFRAW: Latest News</a>. The live reporting index for current tournament updates.</li>
              <li><a href="/tournaments">GOLFRAW: Tournament coverage</a>. East Lake leaderboard and event context.</li>
              <li><a href="/news-2026-tour-championship-tee-times-round-4">Sunday Tee Times</a>. The official (and disputed) Round 4 pairings.</li>
              <li><a href="/news-2026-cameron-young-new-putter-62-tour-championship">Cameron Young's 62</a>. Context on low rounds at East Lake this week.</li>
              <li><a href="/news-2026-tour-championship-final-round-hovland-leads">Final Round Preview</a>. Detailed Sunday analysis of the chasing pack.</li>
            </ol>
          </section>

          <div class="provenance">
            <p><strong>Article history.</strong> Published <time datetime="2026-08-30T14:00:00+02:00">30 August 2026 at 14:00 CEST</time>.</p>
            <p><strong>Corrections.</strong> None at publication. <a href="/corrections">Corrections policy</a>.</p>
            <p><strong>Last updated.</strong> <time datetime="2026-08-30T14:00:00+02:00">30 August 2026 at 14:00 CEST</time>.</p>
          </div>

          <aside class="related" aria-label="Related GolfRaw reporting">
            <p class="section-label" style="color:#b8d2c5">Keep reading</p>
            <ul>
              <li><a href="/news-2026-tour-championship-tee-times-round-4">Sunday Tee Times</a></li>
              <li><a href="/news-2026-cameron-young-new-putter-62-tour-championship">Cameron Young shoots 62</a></li>
              <li><a href="/news-2026-tour-championship-final-round-hovland-leads">Hovland Leads: Final Round Preview</a></li>
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
      "@id": "https://www.golfraw.com/news-2026-tour-championship-round-3-tee-times-leaderboard#article",
      "headline": "Tour Championship Round 3: Hovland's 65 and Every Score | GOLFRAW",
      "name": "Tour Championship Round 3: Hovland's 65 and Every Score | GOLFRAW",
      "description": "Nineteen players began Saturday within five shots and it ended with a one-shot lead. Full Round 3 draw, results, and the Sunday sheet nobody agrees on.",
      "articleSection": "Tournaments",
      "keywords": "Tour Championship Round 3, Viktor Hovland, Rory McIlroy 63, East Lake Leaderboard, PGA Tour",
      "datePublished": "2026-08-30T14:00:00+02:00",
      "dateModified": "2026-08-30T14:00:00+02:00",
      "inLanguage": "en",
      "image": {
        "@type": "ImageObject",
        "url": "https://www.golfraw.com/public/tour-championship-2026-round-3-tee-times-leaderboard.webp",
        "contentUrl": "https://www.golfraw.com/public/tour-championship-2026-round-3-tee-times-leaderboard.webp",
        "width": 1200,
        "height": 675,
        "caption": "The first tee and tournament scoreboard at East Lake during Moving Day Round 3 of the 2026 Tour Championship."
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
      "@id": "https://www.golfraw.com/news-2026-tour-championship-round-3-tee-times-leaderboard#breadcrumb",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.golfraw.com/"},
        {"@type": "ListItem", "position": 2, "name": "News", "item": "https://www.golfraw.com/news"},
        {"@type": "ListItem", "position": 3, "name": "Tour Championship Round 3 Recap", "item": "https://www.golfraw.com/news-2026-tour-championship-round-3-tee-times-leaderboard"}
      ]
    },
    {"@type": "Person", "@id": "https://www.golfraw.com/about#editorial", "name": "GOLFRAW Editorial", "url": "https://www.golfraw.com/about"},
    {"@type": "Organization", "@id": "https://www.golfraw.com#organization", "name": "GOLFRAW", "url": "https://www.golfraw.com/"},
    {
      "@type": "FAQPage",
      "@id": "https://www.golfraw.com/news-2026-tour-championship-round-3-tee-times-leaderboard#faq",
      "mainEntity": [
        {"@type": "Question", "name": "Who leads after Round 3 of the Tour Championship?", "acceptedAnswer": {"@type": "Answer", "text": "Viktor Hovland leads by one shot at 15 under par after shooting a 65."}},
        {"@type": "Question", "name": "What did Rory McIlroy shoot in Round 3?", "acceptedAnswer": {"@type": "Answer", "text": "Rory McIlroy shot a 63 with 9 birdies, tying his career-low round at East Lake."}}
      ]
    }
  ]
}
</script>"""

if '<script type="application/ld+json">' in html:
    html = re.sub(r'<script type="application/ld\+json">.*?</script>', json_ld, html, flags=re.DOTALL)
else:
    html = html.replace('</head>', json_ld + '\n</head>')

with open('news-2026-tour-championship-round-3-tee-times-leaderboard.html', 'w') as f:
    f.write(html)
