import json, re

with open('article-template.html', 'r') as f:
    html = f.read()

# 1. Header & Metadata
title = "2026 Tour Championship Sunday Tee Times: Everything Moved | GOLFRAW"
description = "The whole draw shifted about an hour earlier and the pairings were rebuilt. Full Round 4 tee sheet, TV windows, and the mismatch nobody has flagged."
canonical_url = "https://www.golfraw.com/news-2026-tour-championship-sunday-tee-times-round-4"
image_asset = "/public/2026-tour-championship-sunday-tee-times-round-4.webp"

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
          <img src="/public/2026-tour-championship-sunday-tee-times-round-4.webp" alt="Starter board and 1st tee at East Lake Golf Club showing the revised Sunday tee times for the 2026 Tour Championship final round." width="1200" height="675" style="aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:8px;">
          <figcaption>SUNDAY TEE TIMES AT EAST LAKE MOVED ROUGHLY AN HOUR EARLIER WITH VIKTOR HOVLAND AND RYAN GERARD TEEING OFF AT 1:50 P.M. ET. PHOTO: RAWGOLF</figcaption>
        </figure>
"""
if '<figure class="lead-img">' in html:
    html = re.sub(r'<figure class="lead-img">.*?</figure>', hero_html, html, flags=re.DOTALL)
else:
    html = html.replace('</header>', '</header>\n' + hero_html)

new_vis_bc = """<nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/news">News</a> / <a href="/tournaments">Tournaments</a> / <span>Revised Sunday Tee Times</span>
        </nav>"""
html = re.sub(r'<nav class="crumbs".*?</nav>', new_vis_bc, html, flags=re.DOTALL)

html = re.sub(r'<h1 class="headline">.*?</h1>', '<h1 class="headline">2026 Tour Championship Sunday Tee Times: Everything Moved</h1>', html, flags=re.DOTALL)
html = re.sub(r'<h2 class="subhead">.*?</h2>', '<h2 class="subhead">The whole draw shifted about an hour earlier and the pairings were rebuilt. Full Round 4 tee sheet, TV windows, and the mismatch nobody has flagged.</h2>', html, flags=re.DOTALL)

new_body = """<div class="article-body">
          <div class="takeaways">
            <h3 style="margin-top:0;">Key Takeaways</h3>
            <ul>
              <li><b>Tee Times Shifted:</b> Due to weather considerations, the final round draw has moved up roughly one hour. <b>Viktor Hovland</b> and <b>Ryan Gerard</b> tee off at <b>1:50 p.m. ET</b>.</li>
              <li><b>Broadcast Mismatch:</b> Play starts at 10:50 a.m. ET, but Golf Channel coverage doesn't begin until noon, leaving early play exclusive to ESPN+ streaming.</li>
              <li><b>Tight Leaderboard:</b> Hovland (-15) leads by one over Gerard (-14), followed by a massive four-way tie at 12 under par.</li>
              <li><b>Rules Audit (Rule 5.4):</b> The revised times are strictly enforced. Playing in the wrong group or missing the new start time triggers immediate penalties or disqualification.</li>
            </ul>
          </div>

          <h2>Revised Sunday Tee Times (Round 4)</h2>
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>Tee Time (ET)</th>
                  <th>Players</th>
                </tr>
              </thead>
              <tbody>
                <tr><td>10:50 a.m.</td><td>Alex Smalley</td></tr>
                <tr><td>11:02 a.m.</td><td>Patrick Cantlay, Kristoffer Reitan</td></tr>
                <tr><td>11:14 a.m.</td><td>Robert MacIntyre, Hideki Matsuyama</td></tr>
                <tr><td>11:26 a.m.</td><td>Akshay Bhatia, Gary Woodland</td></tr>
                <tr><td>11:38 a.m.</td><td>Ryan Fox, Xander Schauffele</td></tr>
                <tr><td>11:56 a.m.</td><td>Tom Kim, Collin Morikawa</td></tr>
                <tr><td>12:08 p.m.</td><td>Tommy Fleetwood, Alex Fitzpatrick</td></tr>
                <tr><td>12:20 p.m.</td><td>Matt Fitzpatrick, Wyndham Clark</td></tr>
                <tr><td>12:32 p.m.</td><td>Si Woo Kim, Justin Rose</td></tr>
                <tr><td>12:44 p.m.</td><td>Jacob Bridgeman, Sam Burns</td></tr>
                <tr><td>1:02 p.m.</td><td>Min Woo Lee, Russell Henley</td></tr>
                <tr><td>1:14 p.m.</td><td>Rory McIlroy, Cameron Young</td></tr>
                <tr><td>1:26 p.m.</td><td>Scottie Scheffler, Chris Gotterup</td></tr>
                <tr><td>1:38 p.m.</td><td>Adam Scott, Ludvig Åberg</td></tr>
                <tr><td>1:50 p.m.</td><td>Viktor Hovland, Ryan Gerard</td></tr>
              </tbody>
            </table>
          </div>

          <h2>The Broadcast Mismatch</h2>
          <p>The PGA Tour was forced to pull the draw forward due to incoming weather threats, but the television networks did not completely adjust. While the first ball goes in the air at 10:50 a.m. ET, the Golf Channel broadcast doesn't begin until 12:00 p.m. ET (CBS picks up at 1:30 p.m. ET). This creates a 70-minute dead zone for traditional cable viewers, meaning early action is entirely relegated to PGA Tour Live on ESPN+ (which begins streaming at 11:00 a.m. ET).</p>

          <h2>Leaderboard Context & Featured Parings</h2>
          <p><a href="/news-2026-tour-championship-final-round-hovland-leads">As we analyzed following Round 3</a>, Viktor Hovland holds a precarious one-shot lead at 15 under over Ryan Gerard (-14). Just behind them is a massive 4-way tie at 12 under, comprising Scottie Scheffler, Chris Gotterup, Adam Scott, and Ludvig Åberg. Further back, but highly dangerous, are Rory McIlroy and <a href="/news-2026-cameron-young-new-putter-62-tour-championship">Cameron Young</a> at 10 under.</p>
          <p>The chase pairings to watch are McIlroy and Young at 1:14 p.m., followed closely by the powerhouse pairing of Adam Scott and Ludvig Åberg at 1:38 p.m. ET.</p>

          <h2>Rules Audit: Missing the Revised Time</h2>
          <p>With an abruptly altered schedule, players must be hyper-vigilant. Under <b>Rule 5.3a</b>, a player who arrives at the starting area within five minutes after their new starting time receives a two-stroke penalty. Arriving later than that results in disqualification. Furthermore, <b>Rule 5.4</b> dictates that a player must play in their assigned group; teeing off in the wrong pairing results in instant disqualification.</p>

          <h2>Debunking 4 Final Round Misconceptions</h2>
          <ul>
            <li><i>Myth 1: The leaders tee off at 2:55 p.m. ET.</i> False. That was the unadjusted schedule; the final group is now off at 1:50 p.m. ET.</li>
            <li><i>Myth 2: TV coverage captures the whole round.</i> False. The first hour of play is streaming only due to the broadcast mismatch.</li>
            <li><i>Myth 3: Three players are tied for third.</i> False. There is a four-way tie at 12 under par (Scheffler, Gotterup, Scott, Åberg).</li>
            <li><i>Myth 4: A one-shot lead on Sunday is a cushion.</i> False. With a soft golf course yielding 62s and 63s, a one-shot lead is essentially a tied golf tournament.</li>
          </ul>

          <div class="verdict-box">
            <h3>The Raw Verdict</h3>
            <p>The condensed schedule favors the chasers. With TV coverage disjointed and weather looming, the pressure will mount quickly. Hovland must hold off an elite pack that will be throwing darts from the 10:50 a.m. start.</p>
          </div>
          
          <section class="sources" aria-labelledby="faq-label">
            <h2 id="faq-label" style="font-size: 1.25rem; font-family: 'IBM Plex Mono', monospace; text-transform: uppercase;">FAQ</h2>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">What time does the final pairing tee off on Sunday at the Tour Championship?</h3>
              <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">Viktor Hovland and Ryan Gerard tee off at 1:50 p.m. ET.</p>
              </div>
            </div>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">How can I watch the early Sunday coverage of the Tour Championship?</h3>
              <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">Early coverage begins at 11:00 a.m. ET exclusively on ESPN+ (PGA Tour Live), before Golf Channel coverage begins at noon ET.</p>
              </div>
            </div>
          </section>

          <section class="sources" aria-labelledby="sources-label">
            <p class="section-label" id="sources-label">Sources</p>
            <ol>
              <li><a href="/news">GOLFRAW: Latest News</a>. The live reporting index for current tournament updates.</li>
              <li><a href="/news-2026-pga-tour-winners-2026">2026 PGA Tour Winners</a>. Full season archives and statistics.</li>
              <li><a href="/news-2026-tour-championship-final-round-hovland-leads">Hovland's Final Round Preview</a>. Tactical breakdown of the 54-hole leader.</li>
              <li><a href="/news-2026-cameron-young-new-putter-62-tour-championship">Cameron Young's 62</a>. A look at the firepower in the 1:14 p.m. group.</li>
            </ol>
          </section>

          <div class="provenance">
            <p><strong>Article history.</strong> Published <time datetime="2026-08-30T16:00:00+02:00">30 August 2026 at 16:00 CEST</time>.</p>
            <p><strong>Corrections.</strong> None at publication. <a href="/corrections">Corrections policy</a>.</p>
            <p><strong>Last updated.</strong> <time datetime="2026-08-30T16:00:00+02:00">30 August 2026 at 16:00 CEST</time>.</p>
          </div>

          <aside class="related" aria-label="Related GolfRaw reporting">
            <p class="section-label" style="color:#b8d2c5">Keep reading</p>
            <ul>
              <li><a href="/news-2026-tour-championship-final-round-hovland-leads">Hovland's Final Round Lead Analysis</a></li>
              <li><a href="/news-2026-pga-tour-winners-2026">2026 PGA Tour Winners Recap</a></li>
              <li><a href="/news-2026-cameron-young-new-putter-62-tour-championship">Cameron Young shoots 62</a></li>
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
      "@id": "https://www.golfraw.com/news-2026-tour-championship-sunday-tee-times-round-4#article",
      "headline": "2026 Tour Championship Sunday Tee Times: Everything Moved | GOLFRAW",
      "name": "2026 Tour Championship Sunday Tee Times: Everything Moved | GOLFRAW",
      "description": "The whole draw shifted about an hour earlier and the pairings were rebuilt. Full Round 4 tee sheet, TV windows, and the mismatch nobody has flagged.",
      "articleSection": "Tournaments",
      "keywords": "Tour Championship Sunday Tee Times, Viktor Hovland, Ryan Gerard, East Lake, PGA Tour",
      "datePublished": "2026-08-30T16:00:00+02:00",
      "dateModified": "2026-08-30T16:00:00+02:00",
      "inLanguage": "en",
      "image": {
        "@type": "ImageObject",
        "url": "https://www.golfraw.com/public/2026-tour-championship-sunday-tee-times-round-4.webp",
        "contentUrl": "https://www.golfraw.com/public/2026-tour-championship-sunday-tee-times-round-4.webp",
        "width": 1200,
        "height": 675,
        "caption": "Starter board and 1st tee at East Lake Golf Club showing the revised Sunday tee times for the 2026 Tour Championship final round."
      },
      "author": {"@id": "https://www.golfraw.com/about#editorial"},
      "publisher": {"@id": "https://www.golfraw.com#organization"},
      "about": [
        {"@type": "Thing", "name": "Tour Championship"}
      ]
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://www.golfraw.com/news-2026-tour-championship-sunday-tee-times-round-4#breadcrumb",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.golfraw.com/"},
        {"@type": "ListItem", "position": 2, "name": "News", "item": "https://www.golfraw.com/news"},
        {"@type": "ListItem", "position": 3, "name": "Revised Sunday Tee Times", "item": "https://www.golfraw.com/news-2026-tour-championship-sunday-tee-times-round-4"}
      ]
    },
    {"@type": "Person", "@id": "https://www.golfraw.com/about#editorial", "name": "GOLFRAW Editorial", "url": "https://www.golfraw.com/about"},
    {"@type": "Organization", "@id": "https://www.golfraw.com#organization", "name": "GOLFRAW", "url": "https://www.golfraw.com/"},
    {
      "@type": "FAQPage",
      "@id": "https://www.golfraw.com/news-2026-tour-championship-sunday-tee-times-round-4#faq",
      "mainEntity": [
        {"@type": "Question", "name": "What time does the final pairing tee off on Sunday at the Tour Championship?", "acceptedAnswer": {"@type": "Answer", "text": "Viktor Hovland and Ryan Gerard tee off at 1:50 p.m. ET."}},
        {"@type": "Question", "name": "How can I watch the early Sunday coverage of the Tour Championship?", "acceptedAnswer": {"@type": "Answer", "text": "Early coverage begins at 11:00 a.m. ET exclusively on ESPN+ (PGA Tour Live), before Golf Channel coverage begins at noon ET."}}
      ]
    }
  ]
}
</script>"""

if '<script type="application/ld+json">' in html:
    html = re.sub(r'<script type="application/ld\+json">.*?</script>', json_ld, html, flags=re.DOTALL)
else:
    html = html.replace('</head>', json_ld + '\n</head>')

with open('news-2026-tour-championship-sunday-tee-times-round-4.html', 'w') as f:
    f.write(html)
