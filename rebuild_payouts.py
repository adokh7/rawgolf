import json, re

with open('news-2026-tour-championship-tee-times-round-4.html', 'r') as f:
    html = f.read()

# 1. Header & Metadata
title = "Tour Championship Points and Payouts: All 29 Checks | GOLFRAW"
description = "Scheffler took $10M, seven men split $11.95M, and $355,000 went nowhere. Full table, plus the figure two official pages disagree on."
canonical_url = "https://www.golfraw.com/news-2026-tour-championship-points-and-payouts"
image_asset = "/public/tour-championship-points-and-payouts-2026.webp"

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

# Fix padding offset requirement if needed:
html = html.replace('<div class="wrap page-grid" style="padding-top: 40px;">', '<div class="wrap page-grid" style="padding-top: 48px;">')
if '<div class="wrap page-grid">' in html:
    html = html.replace('<div class="wrap page-grid">', '<div class="wrap page-grid" style="padding-top: 48px;">')


new_vis_bc = """<nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RAWGOLF</a> / <a href="/news">NEWS</a> / <a href="/tournaments">TOURNAMENTS</a> / <span>PGA TOUR</span>
        </nav>"""
html = re.sub(r'<nav class="crumbs".*?</nav>', new_vis_bc, html, flags=re.DOTALL)

html = re.sub(r'<h1 class="headline">.*?</h1>', '<h1 class="headline">Tour Championship Points and Payouts: All 29 Checks</h1>', html, flags=re.DOTALL)
html = re.sub(r'<p class="standfirst">.*?</p>', f'<p class="standfirst">{description}</p>', html, flags=re.DOTALL)

hero_html = """<figure class="lead-img">
    <img src="/public/tour-championship-points-and-payouts-2026.webp" alt="Scottie Scheffler holding the FedExCup trophy on the 18th green at East Lake after winning the 2026 Tour Championship." width="1200" height="675" style="aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:8px;">
  </figure>
  <figcaption>SCOTTIE SCHEFFLER COLLECTS $10 MILLION AND PASSES TIGER WOODS ON THE ALL-TIME MONEY LIST AFTER WINNING THE 2026 TOUR CHAMPIONSHIP. PHOTO: RAWGOLF</figcaption>"""
html = re.sub(r'<figure class="lead-img">.*?</figcaption>\s*</figure>', hero_html, html, flags=re.DOTALL)
html = re.sub(r'<figure class="lead-img">.*?</figcaption>', hero_html, html, flags=re.DOTALL)
# One more try in case figcaption was outside figure in the previous html
if '<figure class="lead-img">' in html and '<figcaption>' in html:
    html = re.sub(r'<figure class="lead-img">.*?</figure>\s*<figcaption>.*?</figcaption>', hero_html, html, flags=re.DOTALL)

new_body = """<div class="article-body">
          <div class="key-takeaways" style="background:#f4f4f4;padding:20px;margin-bottom:30px;border-left:4px solid var(--flag);">
            <h3>Key Takeaways</h3>
            <ul style="margin-top:10px;">
              <li><b>The Winner:</b> Scottie Scheffler captured the $10 million top prize, locking up his 22nd career win and 2nd FedExCup.</li>
              <li><b>The Record:</b> Scheffler officially surpassed Tiger Woods' all-time career money list record by banking his $10 million payout.</li>
              <li><b>Zero Points Awarded:</b> No FedExCup points are awarded at East Lake; the 72-hole winner simply claims the Cup.</li>
              <li><b>The Seven-Way Tie:</b> The seven players tied for 4th pooled their combined potential payouts and split exactly $1,707,142.86 each.</li>
            </ul>
          </div>

          <h2>Complete 29-Player Official Payout Table</h2>
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>Position</th>
                  <th>Player</th>
                  <th>Score</th>
                  <th>Official Payout</th>
                </tr>
              </thead>
              <tbody>
                <tr><td>1</td><td><b>Scottie Scheffler</b></td><td>-16 (264)</td><td>$10,000,000</td></tr>
                <tr><td>2</td><td>Viktor Hovland</td><td>-13 (267)</td><td>$5,000,000</td></tr>
                <tr><td>3</td><td>Ryan Gerard</td><td>-12 (268)</td><td>$3,705,000</td></tr>
                <tr><td>T4</td><td>A. Fitzpatrick</td><td>-11 (269)</td><td>$1,707,142.86</td></tr>
                <tr><td>T4</td><td>Jacob Bridgeman</td><td>-11 (269)</td><td>$1,707,142.86</td></tr>
                <tr><td>T4</td><td>Min Woo Lee</td><td>-11 (269)</td><td>$1,707,142.86</td></tr>
                <tr><td>T4</td><td>Russell Henley</td><td>-11 (269)</td><td>$1,707,142.86</td></tr>
                <tr><td>T4</td><td>Rory McIlroy</td><td>-11 (269)</td><td>$1,707,142.86</td></tr>
                <tr><td>T4</td><td>Chris Gotterup</td><td>-11 (269)</td><td>$1,707,142.86</td></tr>
                <tr><td>T4</td><td>Ludvig Åberg</td><td>-11 (269)</td><td>$1,707,142.86</td></tr>
                <tr><td>T11</td><td>Tommy Fleetwood</td><td>-10 (270)</td><td>$660,000</td></tr>
                <tr><td>T11</td><td>Cameron Young</td><td>-10 (270)</td><td>$660,000</td></tr>
                <tr><td>T11</td><td>Adam Scott</td><td>-10 (270)</td><td>$660,000</td></tr>
                <tr><td>T14</td><td>Xander Schauffele</td><td>-9 (271)</td><td>$536,250</td></tr>
                <tr><td>T14</td><td>Tom Kim</td><td>-9 (271)</td><td>$536,250</td></tr>
                <tr><td>T14</td><td>Collin Morikawa</td><td>-9 (271)</td><td>$536,250</td></tr>
                <tr><td>T14</td><td>Si Woo Kim</td><td>-9 (271)</td><td>$536,250</td></tr>
                <tr><td>T18</td><td>Akshay Bhatia</td><td>-7 (273)</td><td>$460,000</td></tr>
                <tr><td>T18</td><td>Justin Rose</td><td>-7 (273)</td><td>$460,000</td></tr>
                <tr><td>T18</td><td>Sam Burns</td><td>-7 (273)</td><td>$460,000</td></tr>
                <tr><td>T21</td><td>Patrick Cantlay</td><td>-5 (275)</td><td>$408,750</td></tr>
                <tr><td>T21</td><td>Hideki Matsuyama</td><td>-5 (275)</td><td>$408,750</td></tr>
                <tr><td>T21</td><td>Matt Fitzpatrick</td><td>-5 (275)</td><td>$408,750</td></tr>
                <tr><td>T21</td><td>Wyndham Clark</td><td>-5 (275)</td><td>$408,750</td></tr>
                <tr><td>25</td><td>Kristoffer Reitan</td><td>-3 (277)</td><td>$380,000</td></tr>
                <tr><td>26</td><td>Ryan Fox</td><td>-2 (278)</td><td>$375,000</td></tr>
                <tr><td>27</td><td>Alex Smalley</td><td>-1 (279)</td><td>$370,000</td></tr>
                <tr><td>28</td><td>Robert MacIntyre</td><td>E (280)</td><td>$365,000</td></tr>
                <tr><td>29</td><td>Gary Woodland</td><td>+2 (282)</td><td>$360,000</td></tr>
              </tbody>
            </table>
          </div>

          <h2>Why Zero FedExCup Points Are Awarded</h2>
          <p>Despite being the crowning event of the playoffs, the Tour Championship awards exactly zero FedExCup points. Under the staggered-strokes format, the points math completely freezes following the BMW Championship. The objective at East Lake is brutally simple: win the 72-hole stroke play event, and you are immediately crowned the FedExCup Champion.</p>

          <h2>The T4 Tie Pooling Arithmetic</h2>
          <p>The most devastating financial blow of the day occurred in the massive seven-way tie for fourth place. The designated payouts for positions 4 through 10 totaled $11,950,000. Under PGA Tour distribution rules, that entire sum was pooled and divided evenly among the seven players. The result? Each player took home $1,707,142.86. For a player like Rory McIlroy, <a href="/news-2026-tour-championship-sunday-tee-times-round-4">who entered the day hoping for a solo 4th place finish</a> (worth roughly $3.2 million), slipping into this tie cost him nearly $1.5 million.</p>

          <h2>The Third-Place Discrepancy & Missing $355K</h2>
          <p>An audit of the official PGA Tour payout logs reveals a bizarre discrepancy. The pre-tournament purse projection allocated $3,750,000 for third place. However, Ryan Gerard’s official third-place check cleared for $3,705,000. Furthermore, with J.J. Spaun's withdrawal reducing the field to 29 players, the total purse distributed was $39,645,000—leaving the pre-allocated $355,000 for 30th place completely unallocated and retained by the Tour.</p>

          <h2>Scheffler's Historic Financial Milestone</h2>
          <p>Scottie Scheffler didn't just win the tournament; he completely re-wrote the record books. <a href="/news-2026-tiger-woods-career-money-list-record">As projected earlier this week</a>, the $10 million winner’s check pushed Scheffler's official career earnings to an astronomical $130,390,661. By passing Tiger Woods' long-standing mark of $120,999,166, Scheffler officially becomes the highest-earning player in PGA Tour history. He accomplished this feat while securing his 22nd career victory and claiming his second FedExCup title.</p>

          <h2>Debunking 4 Common Payout Myths</h2>
          <ul>
            <li><i>Myth 1: Tour Championship money doesn't count as official earnings.</i> False. Unlike prior years where bonus pools muddied the waters, the 2026 Tour Championship awards official purse money separate from the Comcast bonus pool.</li>
            <li><i>Myth 2: FedExCup points are quadrupled at East Lake.</i> False. Points are frozen; there are no points awarded during the final event.</li>
            <li><i>Myth 3: The 30th place money goes to charity if someone withdraws.</i> False. Unallocated purse funds resulting from a WD (like Spaun's) are retained by the PGA Tour.</li>
            <li><i>Myth 4: Ties are broken by final round score for payouts.</i> False. All ties in professional golf pool the money for the designated slots and divide it equally among the tied players.</li>
          </ul>

          <div class="verdict-box">
            <h3>The Raw Verdict</h3>
            <p>Scheffler's dominance is unquestioned, but the real story of the payout sheet is the congestion at T4. A seven-way tie siphoning money from elite finishers perfectly encapsulates the unforgiving, cutthroat math of the PGA Tour playoffs.</p>
          </div>
          
          <section class="sources" aria-labelledby="faq-label">
            <h2 id="faq-label" style="font-size: 1.25rem; font-family: 'IBM Plex Mono', monospace; text-transform: uppercase;">FAQ</h2>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">How much did Scottie Scheffler win at the 2026 Tour Championship?</h3>
              <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">Scottie Scheffler won $10,000,000 in official prize money for his victory at the Tour Championship.</p>
              </div>
            </div>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">Did Scottie Scheffler pass Tiger Woods on the all-time money list?</h3>
              <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">Yes. With his $10 million victory, Scheffler's official career earnings reached $130,390,661, surpassing Tiger Woods' record of $120,999,166.</p>
              </div>
            </div>
          </section>

          <section class="sources" aria-labelledby="sources-label">
            <p class="section-label" id="sources-label">Sources</p>
            <ol>
              <li><a href="/news">GOLFRAW: Latest News</a>. The live reporting index for tournament updates.</li>
              <li><a href="/news-2026-tiger-woods-career-money-list-record">Tiger Woods Career Money Record</a>. Contextualizing Scheffler's historic financial milestone.</li>
              <li><a href="/news-2026-pga-tour-winners-2026">2026 PGA Tour Winners</a>. The complete breakdown of the season's champions.</li>
            </ol>
          </section>

          <div class="provenance">
            <p><strong>Article history.</strong> Published <time datetime="2026-08-31T17:00:00+02:00">31 August 2026 at 17:00 CEST</time>.</p>
            <p><strong>Corrections.</strong> None at publication. <a href="/corrections">Corrections policy</a>.</p>
            <p><strong>Last updated.</strong> <time datetime="2026-08-31T17:00:00+02:00">31 August 2026 at 17:00 CEST</time>.</p>
          </div>

          <aside class="related" aria-label="Related GolfRaw reporting">
            <p class="section-label" style="color:#b8d2c5">Keep reading</p>
            <ul>
              <li><a href="/news-2026-tiger-woods-career-money-list-record">The Fall of Tiger's Money Record</a></li>
              <li><a href="/news-2026-tour-championship-sunday-tee-times-round-4">Tour Championship Sunday Tension</a></li>
              <li><a href="/news-2026-pga-tour-winners-2026">2026 PGA Tour Champions Directory</a></li>
            </ul>
          </aside>
        </div>"""

html = re.sub(r'<div class="article-body">.*?</div>\s*</article>', new_body + '\n</article>', html, flags=re.DOTALL)

json_ld = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "NewsArticle",
      "@id": "https://www.golfraw.com/news-2026-tour-championship-points-and-payouts#article",
      "headline": "Tour Championship Points and Payouts: All 29 Checks | GOLFRAW",
      "name": "Tour Championship Points and Payouts: All 29 Checks | GOLFRAW",
      "description": "Scheffler took $10M, seven men split $11.95M, and $355,000 went nowhere. Full table, plus the figure two official pages disagree on.",
      "articleSection": "Tournaments",
      "keywords": "Tour Championship Payouts, FedExCup Prize Money, Scottie Scheffler, PGA Tour Earnings, East Lake",
      "datePublished": "2026-08-31T17:00:00+02:00",
      "dateModified": "2026-08-31T17:00:00+02:00",
      "inLanguage": "en",
      "image": {
        "@type": "ImageObject",
        "url": "https://www.golfraw.com/public/tour-championship-points-and-payouts-2026.webp",
        "contentUrl": "https://www.golfraw.com/public/tour-championship-points-and-payouts-2026.webp",
        "width": 1200,
        "height": 675,
        "caption": "Scottie Scheffler holding the FedExCup trophy on the 18th green at East Lake after winning the 2026 Tour Championship."
      },
      "author": {"@id": "https://www.golfraw.com/about#editorial"},
      "publisher": {"@id": "https://www.golfraw.com#organization"},
      "about": [
        {"@type": "Thing", "name": "Tour Championship"},
        {"@type": "Thing", "name": "Scottie Scheffler"}
      ]
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://www.golfraw.com/news-2026-tour-championship-points-and-payouts#breadcrumb",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.golfraw.com/"},
        {"@type": "ListItem", "position": 2, "name": "PGA Tour", "item": "https://www.golfraw.com/pga-tour"},
        {"@type": "ListItem", "position": 3, "name": "Tour Championship Points and Payouts", "item": "https://www.golfraw.com/news-2026-tour-championship-points-and-payouts"}
      ]
    },
    {"@type": "Person", "@id": "https://www.golfraw.com/about#editorial", "name": "GOLFRAW Editorial", "url": "https://www.golfraw.com/about"},
    {"@type": "Organization", "@id": "https://www.golfraw.com#organization", "name": "GOLFRAW", "url": "https://www.golfraw.com/"},
    {
      "@type": "FAQPage",
      "@id": "https://www.golfraw.com/news-2026-tour-championship-points-and-payouts#faq",
      "mainEntity": [
        {"@type": "Question", "name": "How much did Scottie Scheffler win at the 2026 Tour Championship?", "acceptedAnswer": {"@type": "Answer", "text": "Scottie Scheffler won $10,000,000 in official prize money for his victory at the Tour Championship."}},
        {"@type": "Question", "name": "Did Scottie Scheffler pass Tiger Woods on the all-time money list?", "acceptedAnswer": {"@type": "Answer", "text": "Yes. With his $10 million victory, Scheffler's official career earnings reached $130,390,661, surpassing Tiger Woods' record of $120,999,166."}}
      ]
    }
  ]
}
</script>"""

html = re.sub(r'<script type="application/ld\+json">.*?</script>', json_ld, html, flags=re.DOTALL)

with open('news-2026-tour-championship-points-and-payouts.html', 'w') as f:
    f.write(html)
