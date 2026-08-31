import json, re

with open('news-2026-scottie-scheffler-final-press-conference-answer.html', 'r') as f:
    html = f.read()

# 1. Header & Metadata
title = "Scott O'Neil's LinkedIn Post on LIV Golf 1.0, Fact-Checked | GOLFRAW"
description = "Players as majority owners, five continents, a billion homes. Every claim checked against what LIV actually did in 2026, including the purse cut."
canonical_url = "https://www.golfraw.com/news-2026-scott-oneil-linkedin-post-liv-golf"
image_asset = "/public/scott-oneil-linkedin-post-liv-golf-2026.webp"

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

new_vis_bc = """<nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RAWGOLF</a> / <a href="/news">NEWS</a> / <a href="/liv-golf">LIV GOLF</a> / <span>SCOTT O'NEIL LINKEDIN AUDIT</span>
        </nav>"""
html = re.sub(r'<nav class="crumbs".*?</nav>', new_vis_bc, html, flags=re.DOTALL)

html = re.sub(r'<h1.*?>.*?</h1>', f'<h1>Scott O\'Neil\'s LinkedIn Post on LIV Golf 1.0, Fact-Checked</h1>', html, flags=re.DOTALL, count=1)
html = re.sub(r'<p class="standfirst">.*?</p>', f'<p class="standfirst">{description}</p>', html, flags=re.DOTALL)
html = re.sub(r'<span class="cat">.*?</span>', '<span class="cat">LIV GOLF • NEWS</span>', html, count=1)

hero_html = """<figure class="lead-img">
          <img src="/public/scott-oneil-linkedin-post-liv-golf-2026.webp" alt="LIV Golf CEO Scott O'Neil speaking about the league's transition to LIV 2.0 amid Chapter 11 bankruptcy reports." width="1200" height="675" style="aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:8px;">
          <figcaption>LIV GOLF CEO SCOTT O'NEIL FRAMED THE LEAGUE'S FUTURE AROUND PLAYER EQUITY, BUT HIS LINKEDIN REFLECTION SKIPPED CRITICAL REVENUE AND PURSE CUTS. PHOTO: RAWGOLF</figcaption>
        </figure>"""
html = re.sub(r'<figure class="lead-img">.*?</figure>', hero_html, html, flags=re.DOTALL)

new_body = """<div class="article-body">
          <div class="key-takeaways" style="background:#f4f4f4;padding:20px;margin-bottom:30px;border-left:4px solid var(--flag);">
            <h3>Key Takeaways</h3>
            <ul style="margin-top:10px;">
              <li><b>Distribution vs. Viewership:</b> Claiming "1 billion homes reached" refers to technical broadcast availability across global networks, not verified active viewership ratings.</li>
              <li><b>Equity Over Cash:</b> Framing "players as majority equity holders" as a triumph omits the fact that this equity is replacing billions in guaranteed sovereign cash amid <a href="/news-2026-liv-golf-settlement-offers-bankruptcy">fractional settlement offers</a>.</li>
              <li><b>The 60% Cut:</b> While the post claims fans won't notice a difference in LIV 2.0, reporting indicates purses will be slashed to roughly 40% of their previous levels.</li>
            </ul>
          </div>

          <h2>Claims vs Reality Fact-Check Table</h2>
          <div class="table-container" style="overflow-x:auto;">
            <table class="data-table" style="width:100%;border-collapse:collapse;margin-bottom:30px;font-family: 'IBM Plex Mono', monospace; font-size: 0.9rem;">
              <thead>
                <tr style="border-bottom: 2px solid var(--ink); text-align: left;">
                  <th style="padding: 10px 5px;">O'Neil's LinkedIn Claim</th>
                  <th style="padding: 10px 5px;">The Reality</th>
                </tr>
              </thead>
              <tbody>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">"Reaching over 1 billion homes across 200 countries"</td><td style="padding: 10px 5px;">This measures broadcast <i>availability</i> (potential reach), not verified TV ratings or viewership.</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">"Players as majority equity holders is a sports first"</td><td style="padding: 10px 5px;">Equity is being given in lieu of guaranteed contracts via <a href="/news-2026-liv-golf-settlement-offers-bankruptcy">settlement offers of "cents on the dollar"</a>.</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">"Fans won't notice the difference in LIV 2.0"</td><td style="padding: 10px 5px;">Purses are projected to drop to ~40% of previous levels (a 60% cut) under the new model.</td>
                </tr>
                <tr>
                  <td style="padding: 10px 5px;">"Vibrant global season completion"</td><td style="padding: 10px 5px;">The 2026 season was cut short in Indianapolis, canceling the Team Championship and massive on-site parties.</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h2>Line-by-Line Breakdown: LinkedIn vs Reality</h2>
          <p>As LIV Golf navigates <a href="/news-2026-liv-golf-bankruptcy-chapter-11-explained">its reported Chapter 11 restructuring into "LIV 2.0"</a>, CEO Scott O'Neil took to LinkedIn to frame the transition as a historic pivot rather than a financial retreat. His post, which quickly circulated among golf industry professionals, painted a picture of a league voluntarily shifting into an innovative player-owned cooperative.</p>
          <p>However, when O'Neil's carefully curated executive statements are cross-referenced with recent bankruptcy reporting from the Financial Times and Reuters, the narrative splinters. The post is a masterclass in corporate repositioning—highlighting operational metrics while completely side-stepping the severe liquidity crisis that forced the restructuring.</p>

          <h2>The Distribution Metric Myth</h2>
          <p>One of the most prominent claims in O'Neil's post is the assertion that LIV Golf reached "over 1 billion homes across 200 countries." While technically accurate from a distribution standpoint, this metric is widely understood in the sports media industry as a vanity statistic.</p>
          <p>"Reach" simply means that the broadcast was technically available in a household (e.g., through an app or a bundled cable channel). It does not mean a billion people, or even a fraction of that, actually watched the broadcast. By conflating potential availability with active viewership, O'Neil masks the league's well-documented struggles to secure a competitive domestic television footprint.</p>

          <h2>Equity vs Debt: The Real Cost of "Ownership"</h2>
          <p>The core of O'Neil's optimism centers on the transition to a player-owned model, which he heralds as a "sports first." While true that active players owning the majority of a league is unprecedented, the context of <i>how</i> they acquired that equity is critical.</p>
          <p>This is not a reward for performance; it is a desperate financial maneuver. As detailed in the <a href="/news-2026-liv-golf-settlement-offers-bankruptcy">LIV Golf settlement offers breakdown</a>, players are being forced to accept equity in LIV 2.0 because the Public Investment Fund (PIF) is wiping out billions in guaranteed contract debt. Players are swapping bulletproof, sovereign-backed cash contracts for shares in an unproven, newly bankrupt golf league.</p>

          <h2>The Financial Reality: The 60% Purse Cut</h2>
          <p>O'Neil assured fans that they "won't notice the difference in LIV 2.0." From a purely visual standpoint—shotguns starts, team branding—he might be right. But inside the ropes, the financial reality will be drastically altered.</p>
          <p>According to reports from Golf.com, the new LIV 2.0 structure will see tournament purses slashed by roughly 60%, dropping to approximately 40% of their previous $25 million levels. This severe reduction is necessary to make the league viable for private capital firms like BC Partners, who refuse to underwrite the reckless spending of LIV 1.0.</p>

          <h2>The Silent Indianapolis Finale</h2>
          <p>The post concludes by praising the "vibrant global season completion." Yet, the reality on the ground in Indianapolis was starkly different. The 2026 season was abruptly truncated. The highly promoted Team Championship was canceled, and the massive on-site parties and concerts that defined LIV's brand were absent.</p>
          <p>Jon Rahm, who amassed $105.6 million in career LIV earnings, and Bryson DeChambeau concluded their seasons in an eerily subdued atmosphere at Chatham Hills, a quiet ending to what was supposed to be a disruptive global phenomenon.</p>

          <h2>Debunking 5 Viral Social Media Claims</h2>
          <ul>
            <li><i>Myth 1: LIV Golf was profitable in 2026.</i> False. The league was operating at a massive loss, leading to the reported Chapter 11 filing and PIF's withdrawal of future capital guarantees.</li>
            <li><i>Myth 2: 1 billion people watched LIV Golf.</i> False. The 1 billion figure represents potential technical reach, not active viewership metrics.</li>
            <li><i>Myth 3: The PGA Tour is buying LIV.</i> False. The PGA Tour continues to operate independently and has maintained strict returning member guidelines.</li>
            <li><i>Myth 4: Players wanted the equity model.</i> False. The equity model is being forced upon players as a replacement for their guaranteed cash contracts.</li>
            <li><i>Myth 5: LIV 2.0 will have the exact same prize money.</i> False. Purses are projected to face a 60% reduction.</li>
          </ul>

          <h2>The Raw Verdict</h2>
          <p>Scott O'Neil's LinkedIn post did exactly what an executive statement is designed to do: spin a crisis into an opportunity. While the concept of a player-owned league is fascinating, it was born out of financial insolvency, not innovation. The true test of LIV 2.0 won't be how it's framed on social media, but whether players are willing to tee it up for a fraction of what they were originally promised.</p>
          
          <div class="faq-section">
            <h2>Frequently Asked Questions</h2>
            
            <h3>What did Scott O'Neil say about LIV Golf's future?</h3>
            <p>O'Neil highlighted the transition to "LIV 2.0" as an innovative move to a player-owned equity model, emphasizing global reach while omitting details about contract buyouts and bankruptcy restructuring.</p>
            
            <h3>Is LIV Golf actually reaching 1 billion homes?</h3>
            <p>The "1 billion homes" metric refers to technical broadcast availability across global networks, not the number of people who actively watched the tournaments.</p>
          </div>
        </div>
"""

html = re.sub(r'<div class="article-body">.*?</div>\s*</article>', new_body + '\n</article>', html, flags=re.DOTALL)

related_html = """
    <!-- ============ RELATED ============ -->
    <section class="related" aria-labelledby="related-heading">
      <div class="wrap">
        <h2 id="related-heading"><span class="idx">REL</span>Related Stories</h2>
        <div class="rel-grid">
          <a class="rel-card" href="/news-2026-liv-golf-settlement-offers-bankruptcy">
            <div class="cat">LIV GOLF</div>
            <h3>LIV Golf Settlement Offers: Cents on the Dollar, Explained</h3>
            <div class="d">MON 31 AUG · GOLFRAW</div>
          </a>
          <a class="rel-card" href="/news-2026-liv-golf-bankruptcy-chapter-11-explained">
            <div class="cat">LIV GOLF</div>
            <h3>LIV Golf Bankruptcy: What Chapter 11 Would Actually Do</h3>
            <div class="d">MON 31 AUG · GOLFRAW</div>
          </a>
          <a class="rel-card" href="/news-2026-tour-championship-points-and-payouts">
            <div class="cat">TOURNAMENTS</div>
            <h3>Tour Championship Points and Payouts</h3>
            <div class="d">MON 31 AUG · GOLFRAW</div>
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
      "@id": "https://www.golfraw.com/news-2026-scott-oneil-linkedin-post-liv-golf#article",
      "headline": "Scott O'Neil's LinkedIn Post on LIV Golf 1.0, Fact-Checked | GOLFRAW",
      "name": "Scott O'Neil's LinkedIn Post on LIV Golf 1.0, Fact-Checked | GOLFRAW",
      "description": "Players as majority owners, five continents, a billion homes. Every claim checked against what LIV actually did in 2026, including the purse cut.",
      "articleSection": "News",
      "keywords": "Scott O'Neil, LIV Golf, Chapter 11, LIV 2.0, Golf Business, Fact Check",
      "datePublished": "2026-08-31T17:00:00+02:00",
      "dateModified": "2026-08-31T17:00:00+02:00",
      "inLanguage": "en",
      "image": {
        "@type": "ImageObject",
        "url": "https://www.golfraw.com/public/scott-oneil-linkedin-post-liv-golf-2026.webp",
        "contentUrl": "https://www.golfraw.com/public/scott-oneil-linkedin-post-liv-golf-2026.webp",
        "width": 1200,
        "height": 675,
        "caption": "LIV Golf CEO Scott O'Neil framed the league's future around player equity, but skipped critical revenue cuts."
      },
      "author": {"@id": "https://www.golfraw.com/about#editorial"},
      "publisher": {"@id": "https://www.golfraw.com#organization"}
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://www.golfraw.com/news-2026-scott-oneil-linkedin-post-liv-golf#breadcrumb",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.golfraw.com/"},
        {"@type": "ListItem", "position": 2, "name": "News", "item": "https://www.golfraw.com/news"},
        {"@type": "ListItem", "position": 3, "name": "LIV Golf", "item": "https://www.golfraw.com/liv-golf"},
        {"@type": "ListItem", "position": 4, "name": "Scott O'Neil LinkedIn Audit", "item": "https://www.golfraw.com/news-2026-scott-oneil-linkedin-post-liv-golf"}
      ]
    },
    {"@type": "Person", "@id": "https://www.golfraw.com/about#editorial", "name": "GOLFRAW Editorial", "url": "https://www.golfraw.com/about"},
    {"@type": "Organization", "@id": "https://www.golfraw.com#organization", "name": "GOLFRAW", "url": "https://www.golfraw.com/"},
    {
      "@type": "FAQPage",
      "@id": "https://www.golfraw.com/news-2026-scott-oneil-linkedin-post-liv-golf#faq",
      "mainEntity": [
        {"@type": "Question", "name": "What did Scott O'Neil say about LIV Golf's future?", "acceptedAnswer": {"@type": "Answer", "text": "O'Neil highlighted the transition to 'LIV 2.0' as an innovative move to a player-owned equity model, emphasizing global reach while omitting details about contract buyouts and bankruptcy restructuring."}},
        {"@type": "Question", "name": "Is LIV Golf actually reaching 1 billion homes?", "acceptedAnswer": {"@type": "Answer", "text": "The '1 billion homes' metric refers to technical broadcast availability across global networks, not the number of people who actively watched the tournaments."}}
      ]
    }
  ]
}
</script>"""

html = re.sub(r'<script type="application/ld\+json">.*?</script>', json_ld, html, flags=re.DOTALL)

with open('news-2026-scott-oneil-linkedin-post-liv-golf.html', 'w') as f:
    f.write(html)
