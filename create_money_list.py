import json, re

with open('article-template.html', 'r') as f:
    html = f.read()

# 1. Header & Metadata
title = "Tiger Woods' Career Money List Record May Fall Today | GOLFRAW"
description = "Scheffler needs solo 13th, McIlroy needs solo 4th. One outlet already declared it done a week ago. Here's what's actually verified and what isn't."
canonical_url = "https://www.golfraw.com/news-2026-tiger-woods-career-money-list-record"
image_asset = "/public/tiger-woods-career-money-list-record.webp"

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
          <img src="/public/tiger-woods-career-money-list-record.webp" alt="Scottie Scheffler on the practice range at East Lake chasing Tiger Woods' all-time PGA Tour career money list record." width="1200" height="675" style="aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:8px;">
          <figcaption>SCOTTIE SCHEFFLER ENTERS THE TOUR CHAMPIONSHIP FINAL ROUND JUST $609,000 AWAY FROM ECLIPSING TIGER WOODS' ALL-TIME PGA TOUR CAREER MONEY RECORD. PHOTO: RAWGOLF</figcaption>
        </figure>
"""
if '<figure class="lead-img">' in html:
    html = re.sub(r'<figure class="lead-img">.*?</figure>', hero_html, html, flags=re.DOTALL)
else:
    html = html.replace('</header>', '</header>\n' + hero_html)

new_vis_bc = """<nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/pga-tour">PGA Tour</a> / <span>Tiger Woods Career Money Record</span>
        </nav>"""
html = re.sub(r'<nav class="crumbs".*?</nav>', new_vis_bc, html, flags=re.DOTALL)

html = re.sub(r'<h1 class="headline">.*?</h1>', '<h1 class="headline">Tiger Woods\' Career Money List Record May Fall Today</h1>', html, flags=re.DOTALL)
html = re.sub(r'<h2 class="subhead">.*?</h2>', '<h2 class="subhead">Scheffler needs solo 13th, McIlroy needs solo 4th. One outlet already declared it done a week ago. Here\'s what\'s actually verified and what isn\'t.</h2>', html, flags=re.DOTALL)

new_body = """<div class="article-body">
          <div class="takeaways">
            <h3 style="margin-top:0;">Key Takeaways</h3>
            <ul>
              <li><b>The Record:</b> Tiger Woods holds the official PGA Tour career money record at $120,999,166, a mark he has held uninterrupted since 2000.</li>
              <li><b>The Chasers:</b> Scottie Scheffler trails by $609,000 (needs solo 13th today). Rory McIlroy trails by ~$3.2M (needs solo 4th today).</li>
              <li><b>The Confusion:</b> Discrepancies in media reporting prematurely crowned Scheffler last week. However, official tour metrics verify he is still short of Woods' historic number.</li>
              <li><b>The Inflation:</b> Sam Snead won 82 times and earned $620K in his career. Scheffler is on the verge of breaking the all-time record with just 21 victories.</li>
            </ul>
          </div>

          <h2>Career Money List Thresholds & Stats</h2>
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>Player</th>
                  <th>Career Earnings</th>
                  <th>Starts</th>
                  <th>PGA Tour Wins</th>
                  <th>Threshold Needed Today</th>
                </tr>
              </thead>
              <tbody>
                <tr><td><b>Tiger Woods</b></td><td>$120,999,166</td><td>378</td><td>82</td><td><i>Current Record Holder</i></td></tr>
                <tr><td><b>Scottie Scheffler</b></td><td>$120,390,661</td><td><168</td><td>21</td><td>Solo 13th ($625,000)</td></tr>
                <tr><td><b>Rory McIlroy</b></td><td>~$117,800,000</td><td>>240</td><td>26</td><td>Solo 4th ($3,150,000)</td></tr>
                <tr><td><b>Sam Snead</b></td><td>$620,126</td><td>N/A</td><td>82</td><td><i>Historic Benchmark</i></td></tr>
              </tbody>
            </table>
          </div>

          <h2>The $609K Sunday Threshold</h2>
          <p>Heading into the final round of the Tour Championship, the math is staggering. Scottie Scheffler needs just $608,506 to eclipse Tiger Woods on the official career money list. Entering <a href="/news-2026-tour-championship-sunday-tee-times-round-4">Sunday's revised tee times</a>, Scheffler sits in a tie for third, well within the safety margin. If he finishes in solo 13th place or better (worth roughly $625,000), he claims the all-time record. Meanwhile, Rory McIlroy, starting tied for seventh, needs a massive surge to solo fourth to claim the record for himself.</p>

          <h2>The Media Discrepancy Breakdown</h2>
          <p>If you feel like you already read about this record falling, you aren't crazy. Following the BMW Championship last week, Yahoo Sports published a widely circulated piece claiming Scheffler had officially broken the record. This was premature. Yahoo had incorrectly tabulated unofficial money (likely FedExCup bonuses from prior years) into Scheffler's official career total. Golf Channel and the PGA Tour subsequently confirmed the verified official money math stands precisely at $120,390,661 for Scheffler, keeping Woods at the top.</p>

          <h2>McIlroy’s Shifting Reporting</h2>
          <p>Further clouding the record watch is Rory McIlroy's total. Different major outlets currently report discrepancies in McIlroy’s career earnings ranging from $117.2M to $118.1M. These variations stem from inconsistencies in how European Tour co-sanctioned events and early-career WGC payouts are retroactively calculated in official PGA Tour ledgers.</p>

          <h2>What the Official Money List Ignores</h2>
          <p>It is crucial to understand what "Official Career Earnings" actually means. It completely excludes bonus pools. If you factor in the $23 million FedExCup bonus pool and the $10 million Comcast Business Tour Top 10 regular-season bonus that Scheffler has already secured this year alone, his actual bank account has long surpassed Woods'. However, the official metric strictly tracks tournament purse payouts.</p>

          <h2>Historical Purse Inflation: Snead vs Woods vs Scheffler</h2>
          <p>The pace of modern purses renders historical comparisons absurd. Sam Snead amassed 82 PGA Tour victories and earned a career total of $620,126. Tiger Woods matched those 82 victories and pushed his earnings to $120.9 million—a staggering 195:1 ratio over Snead. Now, <a href="/news-2026-pga-tour-winners-2026">fueled by the Signature Event era</a>, Scheffler is poised to surpass Woods' financial total in fewer than 168 career starts with only 21 victories. The era of the $20 million purse has entirely rewritten the record books.</p>

          <h2>Debunking 4 Money List Misconceptions</h2>
          <ul>
            <li><i>Myth 1: Scheffler already broke the record at the BMW Championship.</i> False. Media reporting errors confused unofficial bonus money with official tournament payouts.</li>
            <li><i>Myth 2: Tiger's earnings include his massive FedExCup bonuses.</i> False. Official career money strictly excludes all season-long bonus pools for all players.</li>
            <li><i>Myth 3: Tiger earned more internationally than on the PGA Tour.</i> False. While Tiger commanded massive appearance fees globally, his $120.9M official PGA Tour total represents the vast majority of his competitive on-course earnings.</li>
            <li><i>Myth 4: The Tour Championship payout is completely unofficial.</i> False. <a href="/every-shot-tiger-woods-80th-win-2018">Unlike the 2018 format</a>, the 2026 Tour Championship awards official money ($10M to the winner) separate from the bonus structure.</li>
          </ul>

          <div class="verdict-box">
            <h3>The Raw Verdict</h3>
            <p>Scheffler will inevitably break the record, quite possibly this afternoon. While it highlights the astronomical rise in modern purses rather than a direct comparison of dominance to Woods, achieving $121 million in under 170 starts is a financial feat that defies comprehension.</p>
          </div>
          
          <section class="sources" aria-labelledby="faq-label">
            <h2 id="faq-label" style="font-size: 1.25rem; font-family: 'IBM Plex Mono', monospace; text-transform: uppercase;">FAQ</h2>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">Who has the highest career earnings on the PGA Tour?</h3>
              <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">Tiger Woods currently holds the official PGA Tour career earnings record with $120,999,166, though Scottie Scheffler is less than $1 million behind.</p>
              </div>
            </div>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">Do FedExCup bonuses count toward career earnings?</h3>
              <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">No. The official PGA Tour career money list only tracks official tournament purse payouts, excluding season-long bonus pools like the FedExCup.</p>
              </div>
            </div>
          </section>

          <section class="sources" aria-labelledby="sources-label">
            <p class="section-label" id="sources-label">Sources</p>
            <ol>
              <li><a href="/pga-tour">GOLFRAW: PGA Tour Coverage</a>. Full season archives and statistics.</li>
              <li><a href="/news-2026-tour-championship-sunday-tee-times-round-4">Sunday Tee Times</a>. Tracking Scheffler and McIlroy's final round progression.</li>
              <li><a href="/news-2026-pga-tour-winners-2026">2026 PGA Tour Winners</a>. The complete breakdown of the modern Signature Event purse structure.</li>
              <li><a href="/every-shot-tiger-woods-80th-win-2018">Tiger Woods' 80th Win</a>. Understanding the historical context of Tiger's earnings dominance.</li>
            </ol>
          </section>

          <div class="provenance">
            <p><strong>Article history.</strong> Published <time datetime="2026-08-30T17:00:00+02:00">30 August 2026 at 17:00 CEST</time>.</p>
            <p><strong>Corrections.</strong> None at publication. <a href="/corrections">Corrections policy</a>.</p>
            <p><strong>Last updated.</strong> <time datetime="2026-08-30T17:00:00+02:00">30 August 2026 at 17:00 CEST</time>.</p>
          </div>

          <aside class="related" aria-label="Related GolfRaw reporting">
            <p class="section-label" style="color:#b8d2c5">Keep reading</p>
            <ul>
              <li><a href="/news-2026-tour-championship-sunday-tee-times-round-4">Tour Championship Sunday Pressure</a></li>
              <li><a href="/every-shot-tiger-woods-80th-win-2018">Tiger Woods 80th Win Retrospective</a></li>
              <li><a href="/news-2026-pga-tour-winners-2026">2026 PGA Tour Season Audit</a></li>
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
      "@id": "https://www.golfraw.com/news-2026-tiger-woods-career-money-list-record#article",
      "headline": "Tiger Woods' Career Money List Record May Fall Today | GOLFRAW",
      "name": "Tiger Woods' Career Money List Record May Fall Today | GOLFRAW",
      "description": "Scheffler needs solo 13th, McIlroy needs solo 4th. One outlet already declared it done a week ago. Here's what's actually verified and what isn't.",
      "articleSection": "PGA Tour",
      "keywords": "Tiger Woods, Scottie Scheffler, Rory McIlroy, PGA Tour Career Money List, Tour Championship",
      "datePublished": "2026-08-30T17:00:00+02:00",
      "dateModified": "2026-08-30T17:00:00+02:00",
      "inLanguage": "en",
      "image": {
        "@type": "ImageObject",
        "url": "https://www.golfraw.com/public/tiger-woods-career-money-list-record.webp",
        "contentUrl": "https://www.golfraw.com/public/tiger-woods-career-money-list-record.webp",
        "width": 1200,
        "height": 675,
        "caption": "Scottie Scheffler on the practice range at East Lake chasing Tiger Woods' all-time PGA Tour career money list record."
      },
      "author": {"@id": "https://www.golfraw.com/about#editorial"},
      "publisher": {"@id": "https://www.golfraw.com#organization"},
      "about": [
        {"@type": "Thing", "name": "PGA Tour"},
        {"@type": "Thing", "name": "Tiger Woods"}
      ]
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://www.golfraw.com/news-2026-tiger-woods-career-money-list-record#breadcrumb",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.golfraw.com/"},
        {"@type": "ListItem", "position": 2, "name": "PGA Tour", "item": "https://www.golfraw.com/pga-tour"},
        {"@type": "ListItem", "position": 3, "name": "Tiger Woods Career Money Record", "item": "https://www.golfraw.com/news-2026-tiger-woods-career-money-list-record"}
      ]
    },
    {"@type": "Person", "@id": "https://www.golfraw.com/about#editorial", "name": "GOLFRAW Editorial", "url": "https://www.golfraw.com/about"},
    {"@type": "Organization", "@id": "https://www.golfraw.com#organization", "name": "GOLFRAW", "url": "https://www.golfraw.com/"},
    {
      "@type": "FAQPage",
      "@id": "https://www.golfraw.com/news-2026-tiger-woods-career-money-list-record#faq",
      "mainEntity": [
        {"@type": "Question", "name": "Who has the highest career earnings on the PGA Tour?", "acceptedAnswer": {"@type": "Answer", "text": "Tiger Woods currently holds the official PGA Tour career earnings record with $120,999,166, though Scottie Scheffler is less than $1 million behind."}},
        {"@type": "Question", "name": "Do FedExCup bonuses count toward career earnings?", "acceptedAnswer": {"@type": "Answer", "text": "No. The official PGA Tour career money list only tracks official tournament purse payouts, excluding season-long bonus pools like the FedExCup."}}
      ]
    }
  ]
}
</script>"""

if '<script type="application/ld+json">' in html:
    html = re.sub(r'<script type="application/ld\+json">.*?</script>', json_ld, html, flags=re.DOTALL)
else:
    html = html.replace('</head>', json_ld + '\n</head>')

with open('news-2026-tiger-woods-career-money-list-record.html', 'w') as f:
    f.write(html)
