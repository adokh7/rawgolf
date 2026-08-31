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
          <img src="/public/tour-championship-points-and-payouts-2026.webp" alt="Scottie Scheffler holding the FedExCup trophy at East Lake" width="1200" height="675" style="aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:8px;">
          <figcaption>SCOTTIE SCHEFFLER COLLECTS $10 MILLION AND PASSES TIGER WOODS ON THE ALL-TIME MONEY LIST. PHOTO: RAWGOLF</figcaption>
        </figure>"""
html = re.sub(r'<figure class="lead-img">.*?</figcaption>\s*</figure>', hero_html, html, flags=re.DOTALL)
html = re.sub(r'<figure class="lead-img">.*?</figcaption>', hero_html, html, flags=re.DOTALL)
if '<figure class="lead-img">' in html and '<figcaption>' in html:
    html = re.sub(r'<figure class="lead-img">.*?</figure>\s*<figcaption>.*?</figcaption>', hero_html, html, flags=re.DOTALL)

new_body = """<div class="article-body">
          <div class="takeaways-box" style="background:#f4f4f4;padding:20px;margin-bottom:30px;border-left:4px solid var(--flag);">
            <h3>Key Takeaways</h3>
            <ul style="margin-top:10px;">
              <li><b>The Winner:</b> Scottie Scheffler captured the $10 million top prize, locking up his 22nd career win and 2nd FedExCup.</li>
              <li><b>The Record:</b> Scheffler officially surpassed Tiger Woods' all-time career money list record by banking his $10 million payout.</li>
              <li><b>Zero Points Awarded:</b> No FedExCup points are awarded at East Lake; the 72-hole winner simply claims the Cup.</li>
              <li><b>The Seven-Way Tie:</b> The seven players tied for 4th pooled their combined potential payouts and split exactly $1,707,142.86 each.</li>
            </ul>
          </div>

          <h2>Complete 29-Player Official Payout Table</h2>
          <div class="table-container" style="overflow-x:auto;">
            <table style="width:100%; border-collapse: collapse; font-family: 'IBM Plex Mono', monospace; font-size: 0.9rem;">
              <thead>
                <tr style="border-bottom: 2px solid var(--ink); text-align: left;">
                  <th style="padding: 10px 5px;">Pos</th>
                  <th style="padding: 10px 5px;">Player</th>
                  <th style="padding: 10px 5px;">Score</th>
                  <th style="padding: 10px 5px; text-align: right;">Official Payout</th>
                </tr>
              </thead>
              <tbody>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">1</td><td style="padding: 10px 5px;"><b>Scottie Scheffler</b></td><td style="padding: 10px 5px;">264 (-16)</td><td style="padding: 10px 5px; text-align: right;">$10,000,000</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">2</td><td style="padding: 10px 5px;">Viktor Hovland</td><td style="padding: 10px 5px;">267 (-13)</td><td style="padding: 10px 5px; text-align: right;">$5,000,000</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">3</td><td style="padding: 10px 5px;">Ryan Gerard</td><td style="padding: 10px 5px;">268 (-12)</td><td style="padding: 10px 5px; text-align: right;">$3,705,000</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">T4</td><td style="padding: 10px 5px;">A. Fitzpatrick, J. Bridgeman, M.W. Lee, R. Henley, R. McIlroy, C. Gotterup, L. Åberg</td><td style="padding: 10px 5px;">269 (-11)</td><td style="padding: 10px 5px; text-align: right;">$1,707,142.86</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">T11</td><td style="padding: 10px 5px;">Tommy Fleetwood, Cameron Young, Adam Scott</td><td style="padding: 10px 5px;">270 (-10)</td><td style="padding: 10px 5px; text-align: right;">$660,000</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">T14</td><td style="padding: 10px 5px;">Xander Schauffele, Tom Kim, Collin Morikawa, Si Woo Kim</td><td style="padding: 10px 5px;">271 (-9)</td><td style="padding: 10px 5px; text-align: right;">$536,250</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">T18</td><td style="padding: 10px 5px;">Akshay Bhatia, Justin Rose, Sam Burns</td><td style="padding: 10px 5px;">273 (-7)</td><td style="padding: 10px 5px; text-align: right;">$460,000</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">T21</td><td style="padding: 10px 5px;">Patrick Cantlay, Hideki Matsuyama, Matt Fitzpatrick, Wyndham Clark</td><td style="padding: 10px 5px;">275 (-5)</td><td style="padding: 10px 5px; text-align: right;">$408,750</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">25</td><td style="padding: 10px 5px;">Kristoffer Reitan</td><td style="padding: 10px 5px;">277 (-3)</td><td style="padding: 10px 5px; text-align: right;">$380,000</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">26</td><td style="padding: 10px 5px;">Ryan Fox</td><td style="padding: 10px 5px;">278 (-2)</td><td style="padding: 10px 5px; text-align: right;">$375,000</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">27</td><td style="padding: 10px 5px;">Alex Smalley</td><td style="padding: 10px 5px;">279 (-1)</td><td style="padding: 10px 5px; text-align: right;">$370,000</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">28</td><td style="padding: 10px 5px;">Robert MacIntyre</td><td style="padding: 10px 5px;">280 (E)</td><td style="padding: 10px 5px; text-align: right;">$365,000</td>
                </tr>
                <tr>
                  <td style="padding: 10px 5px;">29</td><td style="padding: 10px 5px;">Gary Woodland</td><td style="padding: 10px 5px;">282 (+2)</td><td style="padding: 10px 5px; text-align: right;">$360,000</td>
                </tr>
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

          <div class="verdict-box" style="margin-top: 30px; padding: 20px; background-color: #111; color: #fff; border-left: 4px solid var(--flag);">
            <h3 style="color: #fff;">The Raw Verdict</h3>
            <p>Scheffler's dominance is unquestioned, but the real story of the payout sheet is the congestion at T4. A seven-way tie siphoning money from elite finishers perfectly encapsulates the unforgiving, cutthroat math of the PGA Tour playoffs.</p>
          </div>
          
          <div class="faq-section" style="margin-top: 40px;">
            <h2>Frequently Asked Questions</h2>
            
            <h3 style="font-size:1.1rem; margin-top:20px;">How much did Scottie Scheffler win at the 2026 Tour Championship?</h3>
            <p>Scottie Scheffler won $10,000,000 in official prize money for his victory at the Tour Championship.</p>
            
            <h3 style="font-size:1.1rem; margin-top:20px;">Did Scottie Scheffler pass Tiger Woods on the all-time money list?</h3>
            <p>Yes. With his $10 million victory, Scheffler's official career earnings reached $130,390,661, surpassing Tiger Woods' record of $120,999,166.</p>
          </div>
        </div>
"""

html = re.sub(r'<div class="article-body">.*?</div>\s*</div>\s*</article>', new_body + '\n</article>', html, flags=re.DOTALL)
html = re.sub(r'<div class="article-body">.*?</article>', new_body + '\n</article>', html, flags=re.DOTALL)

# Replace the related grid
related_html = """
    <!-- ============ RELATED ============ -->
    <section class="related" aria-labelledby="related-heading">
      <div class="wrap">
        <h2 id="related-heading"><span class="idx">REL</span>Related Stories</h2>
        <div class="rel-grid">
          <a class="rel-card" href="/news-2026-tiger-woods-career-money-list-record">
            <div class="cat">PGA TOUR</div>
            <h3>The Fall of Tiger's Money Record</h3>
            <div class="d">SUN 30 AUG · GOLFRAW</div>
          </a>
          <a class="rel-card" href="/news-2026-tour-championship-sunday-tee-times-round-4">
            <div class="cat">TOURNAMENTS</div>
            <h3>Tour Championship Sunday Tension</h3>
            <div class="d">SUN 30 AUG · GOLFRAW</div>
          </a>
          <a class="rel-card" href="/news-2026-pga-tour-winners-2026">
            <div class="cat">PGA TOUR</div>
            <h3>2026 PGA Tour Champions Directory</h3>
            <div class="d">SAT 29 AUG · GOLFRAW</div>
          </a>
        </div>
      </div>
    </section>
"""

html = re.sub(r'<!-- ============ RELATED ============ -->.*?</section>', related_html, html, flags=re.DOTALL)


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
        "caption": "Scottie Scheffler holding the FedExCup trophy at East Lake"
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
