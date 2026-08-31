import json, re

with open('news-2026-scheffler-brandel-chamblee.html', 'r') as f:
    html = f.read()

# 1. Header & Metadata
title = "The End of LIV Golf? What a Bankruptcy Would Really Mean | GOLFRAW"
description = "Chapter 11 isn't liquidation. It's the vehicle for handing the league to players at about a third of the purses. What's verified, what isn't."
canonical_url = "https://www.golfraw.com/news-2026-the-end-of-liv-golf-bankruptcy"
image_asset = "/public/the-end-of-liv-golf-bankruptcy-2026.webp"

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
          <a href="/">RAWGOLF</a> / <a href="/news">NEWS</a> / <a href="/liv-golf">LIV GOLF</a> / <span>THE END OF LIV GOLF EXPLAINED</span>
        </nav>"""
html = re.sub(r'<nav class="crumbs".*?</nav>', new_vis_bc, html, flags=re.DOTALL)

html = re.sub(r'<h1.*?>.*?</h1>', f'<h1>The End of LIV Golf? What a Bankruptcy Would Really Mean</h1>', html, flags=re.DOTALL, count=1)
html = re.sub(r'<p class="standfirst">.*?</p>', f'<p class="standfirst">{description}</p>', html, flags=re.DOTALL)
html = re.sub(r'<span class="cat">.*?</span>', '<span class="cat">LIV GOLF • NEWS ANALYSIS</span>', html, count=1)

hero_html = """<figure class="lead-img">
          <img src="/public/the-end-of-liv-golf-bankruptcy-2026.webp" alt="LIV Golf tournament branding and signage at a venue amid Chapter 11 bankruptcy reports and purse cuts." width="1200" height="675" style="aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:8px;">
          <figcaption>A REPORTED CHAPTER 11 FILING RESTRUCTURES LIV GOLF INTO A SLIMMED-DOWN, PLAYER-OWNED LEAGUE WITH SIGNIFICANTLY REDUCED PURSES. PHOTO: RAWGOLF</figcaption>
        </figure>"""
html = re.sub(r'<figure class="lead-img">.*?</figure>', hero_html, html, flags=re.DOTALL)


new_body = """<div class="article-body">
          <div class="key-takeaways" style="background:#f4f4f4;padding:20px;margin-bottom:30px;border-left:4px solid var(--flag);">
            <h3>Key Takeaways</h3>
            <ul style="margin-top:10px;">
              <li><b>Chapter 11 Is Not Liquidation:</b> LIV Golf is reportedly preparing to file for Chapter 11 in New Jersey, which is a restructuring maneuver designed to shed debt, not an immediate shutdown of the league.</li>
              <li><b>The Purse Collapse:</b> The reported LIV 2.0 structure will slice tournament purses by roughly 60%, dropping from $30M to around $10M total.</li>
              <li><b>No Easy Way Back:</b> With the PGA Tour's Returning Member Program window closed since February 2026, most current LIV players have no immediate path back to the traditional ecosystem.</li>
            </ul>
          </div>

          <h2>LIV Golf 1.0 vs LIV 2.0 Projection</h2>
          <div class="table-container" style="overflow-x:auto;">
            <table class="data-table" style="width:100%;border-collapse:collapse;margin-bottom:30px;font-family: 'IBM Plex Mono', monospace; font-size: 0.9rem;">
              <thead>
                <tr style="border-bottom: 2px solid var(--ink); text-align: left;">
                  <th style="padding: 10px 5px;">Metric</th>
                  <th style="padding: 10px 5px;">LIV 1.0 (2022-2026)</th>
                  <th style="padding: 10px 5px;">LIV 2.0 Projected</th>
                </tr>
              </thead>
              <tbody>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">Regular Event Purses</td><td style="padding: 10px 5px;">~$30M</td><td style="padding: 10px 5px;">~$10M (~40% of previous levels)</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">Financial Backing</td><td style="padding: 10px 5px;">$5B+ cumulative PIF equity</td><td style="padding: 10px 5px;"><$100M DIP bankruptcy loan</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">League Governance</td><td style="padding: 10px 5px;">100% PIF control</td><td style="padding: 10px 5px;">Player majority equity ownership</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">Player Compensation</td><td style="padding: 10px 5px;">Guaranteed multi-year contracts</td><td style="padding: 10px 5px;">Equity + "Cents on the dollar" settlements</td>
                </tr>
                <tr>
                  <td style="padding: 10px 5px;">Schedule Scale</td><td style="padding: 10px 5px;">14 closed events</td><td style="padding: 10px 5px;">~10 global events with open-tour allowances</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h2>Auditing the Reports</h2>
          <p>For weeks, rumor and speculation have dominated the professional golf landscape regarding the financial viability of LIV Golf. Recently, the Financial Times and Reuters broke the news that the Saudi-backed league is preparing a Chapter 11 bankruptcy filing in a New Jersey federal court, potentially as early as the week of September 7th.</p>
          <p>It's crucial to clarify what this means. Chapter 11 is not Chapter 7 liquidation. The courts are not auctioning off team logos and shotgun shells. Instead, it is a strategic restructuring maneuver designed to legally shed billions in guaranteed contract debt. As of publication, LIV Golf has not issued an official comment confirming the filing.</p>

          <h2>Ian Poulter's Warning and Tax Assets</h2>
          <p>The cracks in the foundation were visible before the reports surfaced. Ian Poulter's widely discussed warning—that the league had just four weeks to find $300 million to meet its September 1 payroll deadline—was the first public indicator of acute liquidity issues.</p>
          <p>But how does a league with $5 billion in net operating losses survive a restructuring? For private equity firms like BC Partners, who are reportedly negotiating to finance the reorganization, those massive losses aren't a failure; they are a tax asset. By acquiring the league, they can use those accumulated losses to offset future tax liabilities across their broader portfolio, making the acquisition viable even if the golf product itself remains unprofitable.</p>

          <h2>The $30M to $10M Purse Collapse</h2>
          <p>The most tangible change for fans and players in the projected "LIV 2.0" is the collapse of the prize money. Front Office Sports and Golf.com have reported that the restructuring demands a massive reduction in operating expenditures.</p>
          <p>Regular event purses are expected to plummet by roughly 60%, dropping from $30 million (individual plus team payouts) to approximately $10 million. This fundamentally alters the value proposition of the league. Without the massive, guaranteed payouts, the field strength is highly susceptible to dilution. Will elite players continue to travel globally for a fraction of the original purses?</p>

          <h2>Player Exit Disparities: DeChambeau vs Rahm</h2>
          <p>The bankruptcy restructuring creates a chaotic legal environment for the players, exposing stark disparities based on contract timelines. Bryson DeChambeau, whose original contract expires at the end of the 2026 season, is largely free to navigate the open market (though his options remain limited).</p>
          <p>Jon Rahm, however, is in a drastically different position. Having signed a massive, long-term deal just a few years ago, Rahm now finds himself listed as an unsecured creditor in a bankruptcy proceeding. His future earnings are trapped in the restructuring, forcing him into <a href="/news-2026-liv-golf-settlement-offers-bankruptcy">fraught settlement negotiations</a> where he may only recover cents on the dollar.</p>

          <h2>The Closed PGA Tour Route</h2>
          <p>For LIV players looking for an exit strategy, the door to the PGA Tour appears firmly shut. The Tour's Returning Member Program—a highly regulated window that allowed defectors to reapply—officially closed on February 2, 2026. Only Brooks Koepka successfully navigated the penalty structure to return.</p>
          <p>PGA Tour executive Brian Rolapp recently issued a statement confirming that there are "no plans to reopen" the program. The Tour is moving forward with its own consolidated, high-revenue model, leaving the vast majority of the LIV roster stranded in the newly restructured, lower-paying LIV 2.0 ecosystem.</p>

          <h2>Debunking 5 Viral Bankruptcy Myths</h2>
          <ul>
            <li><i>Myth 1: LIV Golf is shutting down immediately.</i> False. Chapter 11 is a reorganization to shed debt, not an immediate liquidation (Chapter 7). The league plans to operate a 2027 season.</li>
            <li><i>Myth 2: The PGA Tour engineered the bankruptcy.</i> False. LIV's financial insolvency is a direct result of the PIF withdrawing future capital guarantees due to the league's failure to generate revenue.</li>
            <li><i>Myth 3: Players can just return to the PGA Tour now.</i> False. The Returning Member Program closed in February 2026, and the Tour has explicitly stated it will not reopen.</li>
            <li><i>Myth 4: Players will get all their guaranteed money.</i> False. As unsecured creditors, players with long-term deals will likely settle for a fraction of their owed cash in exchange for league equity.</li>
            <li><i>Myth 5: Saudi Arabia ran out of money.</i> False. The PIF manages nearly a trillion dollars in assets; they simply chose to stop throwing unlimited capital into an asset with a massive negative burn rate.</li>
          </ul>

          <h2>The Raw Verdict</h2>
          <p>The reported Chapter 11 filing marks the definitive end of the "disruptor" era in professional golf. LIV Golf 1.0 was built on the premise of unlimited, consequence-free capital. LIV 2.0 will be forced to operate under the harsh realities of a private equity balance sheet. The league will likely survive, but the days of $25 million purses and nine-figure guaranteed contracts are officially over.</p>
          
          <div class="faq-section">
            <h2>Frequently Asked Questions</h2>
            
            <h3>Is LIV Golf shutting down?</h3>
            <p>No. The reported Chapter 11 bankruptcy filing is a legal mechanism to reorganize the league's debt and contracts, not a liquidation. LIV Golf is projecting a modified 2027 season.</p>
            
            <h3>Will LIV Golf players return to the PGA Tour?</h3>
            <p>For the vast majority of players, the answer is no. The PGA Tour's window for returning members closed in February 2026, and executives have confirmed there are no plans to reopen it.</p>
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
          <a class="rel-card" href="/news-2026-scott-oneil-linkedin-post-liv-golf">
            <div class="cat">LIV GOLF</div>
            <h3>Scott O'Neil's LinkedIn Post on LIV Golf 1.0, Fact-Checked</h3>
            <div class="d">MON 31 AUG · GOLFRAW</div>
          </a>
          <a class="rel-card" href="/news-2026-liv-golf-settlement-offers-bankruptcy">
            <div class="cat">LIV GOLF</div>
            <h3>LIV Golf Settlement Offers: Cents on the Dollar, Explained</h3>
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
      "@id": "https://www.golfraw.com/news-2026-the-end-of-liv-golf-bankruptcy#article",
      "headline": "The End of LIV Golf? What a Bankruptcy Would Really Mean | GOLFRAW",
      "name": "The End of LIV Golf? What a Bankruptcy Would Really Mean | GOLFRAW",
      "description": "Chapter 11 isn't liquidation. It's the vehicle for handing the league to players at about a third of the purses. What's verified, what isn't.",
      "articleSection": "News",
      "keywords": "LIV Golf, Chapter 11, Bankruptcy, PIF, Golf Restructuring, PGA Tour",
      "datePublished": "2026-08-31T17:00:00+02:00",
      "dateModified": "2026-08-31T17:00:00+02:00",
      "inLanguage": "en",
      "image": {
        "@type": "ImageObject",
        "url": "https://www.golfraw.com/public/the-end-of-liv-golf-bankruptcy-2026.webp",
        "contentUrl": "https://www.golfraw.com/public/the-end-of-liv-golf-bankruptcy-2026.webp",
        "width": 1200,
        "height": 675,
        "caption": "A reported Chapter 11 filing restructures LIV Golf into a slimmed-down, player-owned league with significantly reduced purses."
      },
      "author": {"@id": "https://www.golfraw.com/about#editorial"},
      "publisher": {"@id": "https://www.golfraw.com#organization"}
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://www.golfraw.com/news-2026-the-end-of-liv-golf-bankruptcy#breadcrumb",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.golfraw.com/"},
        {"@type": "ListItem", "position": 2, "name": "News", "item": "https://www.golfraw.com/news"},
        {"@type": "ListItem", "position": 3, "name": "LIV Golf", "item": "https://www.golfraw.com/liv-golf"},
        {"@type": "ListItem", "position": 4, "name": "The End of LIV Golf Explained", "item": "https://www.golfraw.com/news-2026-the-end-of-liv-golf-bankruptcy"}
      ]
    },
    {"@type": "Person", "@id": "https://www.golfraw.com/about#editorial", "name": "GOLFRAW Editorial", "url": "https://www.golfraw.com/about"},
    {"@type": "Organization", "@id": "https://www.golfraw.com#organization", "name": "GOLFRAW", "url": "https://www.golfraw.com/"},
    {
      "@type": "FAQPage",
      "@id": "https://www.golfraw.com/news-2026-the-end-of-liv-golf-bankruptcy#faq",
      "mainEntity": [
        {"@type": "Question", "name": "Is LIV Golf shutting down?", "acceptedAnswer": {"@type": "Answer", "text": "No. The reported Chapter 11 bankruptcy filing is a legal mechanism to reorganize the league's debt and contracts, not a liquidation. LIV Golf is projecting a modified 2027 season."}},
        {"@type": "Question", "name": "Will LIV Golf players return to the PGA Tour?", "acceptedAnswer": {"@type": "Answer", "text": "For the vast majority of players, the answer is no. The PGA Tour's window for returning members closed in February 2026, and executives have confirmed there are no plans to reopen it."}}
      ]
    }
  ]
}
</script>"""

html = re.sub(r'<script type="application/ld\+json">.*?</script>', json_ld, html, flags=re.DOTALL)

with open('news-2026-the-end-of-liv-golf-bankruptcy.html', 'w') as f:
    f.write(html)
