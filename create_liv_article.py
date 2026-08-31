import json, re

with open('news-2026-tour-championship-tee-times-round-4.html', 'r') as f:
    html = f.read()

# 1. Header & Metadata
title = "LIV Golf Bankruptcy: What Chapter 11 Would Actually Do | GOLFRAW"
description = "A Chapter 11 filing isn't the league shutting down. It's the vehicle for handing it to the players. What's verified, what isn't, and who gets paid last."
canonical_url = "https://www.golfraw.com/news-2026-liv-golf-bankruptcy-chapter-11-explained"
image_asset = "/public/liv-golf-bankruptcy-chapter-11-explained-2026.webp"

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
          <a href="/">RAWGOLF</a> / <a href="/news">NEWS</a> / <a href="/liv-golf">LIV GOLF</a> / <span>CHAPTER 11 EXPLAINED</span>
        </nav>"""
html = re.sub(r'<nav class="crumbs".*?</nav>', new_vis_bc, html, flags=re.DOTALL)

html = re.sub(r'<h1 class="headline">.*?</h1>', f'<h1 class="headline">LIV Golf Bankruptcy: What Chapter 11 Would Actually Do</h1>', html, flags=re.DOTALL)
html = re.sub(r'<p class="standfirst">.*?</p>', f'<p class="standfirst">{description}</p>', html, flags=re.DOTALL)
html = re.sub(r'<span class="cat">.*?</span>', '<span class="cat">NEWS · LIV GOLF</span>', html)

hero_html = """<figure class="lead-img">
       <img src="/public/liv-golf-bankruptcy-chapter-11-explained-2026.webp" alt="A LIV Golf branded tee marker at an empty tournament venue amid reports of a Chapter 11 bankruptcy filing." width="1200" height="675" style="aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:8px;">
     </figure>
     <figcaption>A REPORTED CHAPTER 11 BANKRUPTCY FILING WOULD ACT AS THE LEGAL MECHANISM TO RESTRUCTURE LIV GOLF AND TRANSFER EQUITY TO PLAYERS. PHOTO: RAWGOLF</figcaption>"""
html = re.sub(r'<figure class="lead-img">.*?</figcaption>\s*</figure>', hero_html, html, flags=re.DOTALL)
html = re.sub(r'<figure class="lead-img">.*?</figcaption>', hero_html, html, flags=re.DOTALL)
if '<figure class="lead-img">' in html and '<figcaption>' in html:
    html = re.sub(r'<figure class="lead-img">.*?</figure>\s*<figcaption>.*?</figcaption>', hero_html, html, flags=re.DOTALL)

new_body = """<div class="article-body">
          <div class="takeaways-box" style="background:#f4f4f4;padding:20px;margin-bottom:30px;border-left:4px solid var(--flag);">
            <h3>Key Takeaways</h3>
            <ul style="margin-top:10px;">
              <li><b>Not a Liquidation:</b> A potential Chapter 11 filing is a restructuring maneuver designed to hand the league over to the players, not a Chapter 7 liquidation.</li>
              <li><b>The Unsecured Creditor Trap:</b> Players refusing settlements will join vendors as unsecured creditors, waiting in line behind PIF's DIP financing.</li>
              <li><b>LIV 2.0 Vision:</b> The new equity-driven cooperative model aims for ~10 global events, open tour cross-participation, and resolving ongoing DP World Tour/PGA Tour sanction conflicts.</li>
            </ul>
          </div>

          <h2>LIV Golf Restructuring vs Original Structure</h2>
          <div class="table-container" style="overflow-x:auto;">
            <table style="width:100%; border-collapse: collapse; font-family: 'IBM Plex Mono', monospace; font-size: 0.9rem;">
              <thead>
                <tr style="border-bottom: 2px solid var(--ink); text-align: left;">
                  <th style="padding: 10px 5px;">Metric</th>
                  <th style="padding: 10px 5px;">Original Structure (2022-2026)</th>
                  <th style="padding: 10px 5px;">Post-Bankruptcy "LIV 2.0"</th>
                </tr>
              </thead>
              <tbody>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">Funding Source</td><td style="padding: 10px 5px;">Cumulative PIF Funding ($5B+)</td><td style="padding: 10px 5px;">Debtor-in-Possession Loan (&lt;$100M)</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">Player Compensation</td><td style="padding: 10px 5px;">Guaranteed multi-year cash contracts</td><td style="padding: 10px 5px;">"Cents on the dollar" settlement + Equity</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">Schedule & Freedom</td><td style="padding: 10px 5px;">14 closed, mandatory events</td><td style="padding: 10px 5px;">~10 global events + open tour cross-participation</td>
                </tr>
                <tr>
                  <td style="padding: 10px 5px;">Corporate Governance</td><td style="padding: 10px 5px;">PIF-operated, top-down league</td><td style="padding: 10px 5px;">Player-controlled equity cooperative</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h2>Auditing the Chapter 11 Reports</h2>
          <p>Recent reports from the Financial Times and Reuters indicate LIV Golf is preparing a Chapter 11 bankruptcy filing in a New Jersey federal court, potentially as early as the week of September 7. Currently unverified with no official comments from LIV executives or PIF representatives, the filing is widely misunderstood. It is crucial to separate the headlines from the legal reality: this is not a shutdown.</p>
          <p>A Chapter 11 bankruptcy is a corporate restructuring mechanism. In LIV's case, it serves as the legal vehicle to formally sever the original, unsustainable financial structure backed by $5 billion from the Public Investment Fund (PIF) and transition the entity into a player-owned cooperative.</p>

          <h2>The Player Dilemma & Unsecured Creditor Trap</h2>
          <p>The impending filing forces LIV’s roster into a brutal legal dilemma. The guaranteed multi-year contracts that lured players away from the PGA Tour are about to be shredded in bankruptcy court. Players essentially have three options:</p>
          <ol>
            <li><b>Settle and Join LIV 2.0:</b> Accept a "cents on the dollar" cash settlement for their remaining contracts in exchange for equity in the newly restructured league.</li>
            <li><b>Settle and Exit:</b> Take the reduced settlement payout and leave the ecosystem entirely, attempting to return to legacy tours.</li>
            <li><b>Reject and Sue:</b> Refuse the settlement and fight it out in court. This is the "Unsecured Creditor Trap." By suing, players join aggrieved vendors at the back of the line, waiting behind PIF, who will likely secure priority status through Debtor-in-Possession (DIP) financing.</li>
          </ol>

          <h2>Inside "LIV 2.0" and the Sanction Standoff</h2>
          <p>If the restructuring succeeds, "LIV 2.0" aims to operate roughly 10 global events with a significantly reduced overhead. The ultimate goal of this player-owned equity model is freedom—specifically, open tour cross-participation. However, this vision immediately collides with the ongoing DP World Tour sanction threats and the PGA Tour's strict returning restrictions.</p>
          <p>As <a href="/scottie-scheffler-swing-explained">Scottie Scheffler continues his historic dominance</a> on the PGA Tour, the window for LIV stars to return remains fraught. PGA Tour executives, including Brian Rolapp, have maintained a hardline stance. For players like Brooks Koepka, the legal restructuring of LIV might be their only path to renegotiating access to legacy tour events without crippling fines.</p>

          <h2>Operational Reality: Layoffs and Lawsuits</h2>
          <p>The writing has been on the wall for weeks. According to a recent report by Joel Beall of Golf Digest, comprehensive staff layoffs are scheduled to conclude by the first week of September. Additionally, several vendor lawsuits over unpaid production and app development fees have already hit the docket.</p>
          <p>The macro timeline reveals the unsustainable burn rate: PIF sank over $5 billion into the project since 2022. Following the April 2026 funding cliff and the disastrous $300 million loss associated with the Asian Tour partnership termination, the original financial model was entirely exhausted.</p>

          <h2>Fact-Checking 5 Widespread Bankruptcy Myths</h2>
          <ul>
            <li><i>Myth 1: LIV Golf is liquidating and shutting down completely.</i> False. It is a Chapter 11 restructuring, not a Chapter 7 liquidation.</li>
            <li><i>Myth 2: Players will get all the remaining money on their contracts.</i> False. Contracts will be restructured; players will be offered reduced settlements and equity.</li>
            <li><i>Myth 3: The PGA Tour orchestrated the bankruptcy.</i> False. This is a direct result of PIF cutting off the funding pipeline due to massive burn rates.</li>
            <li><i>Myth 4: PIF will lose everything they invested.</i> False. By providing DIP financing, PIF maintains significant leverage and priority debt status during the restructuring.</li>
            <li><i>Myth 5: LIV players can immediately rejoin the PGA Tour.</i> False. PGA Tour returning restrictions and fines remain firmly in place, complicating any mass exodus.</li>
          </ul>

          <div class="verdict-box" style="margin-top: 30px; padding: 20px; background-color: #111; color: #fff; border-left: 4px solid var(--flag);">
            <h3 style="color: #fff;">The Raw Verdict</h3>
            <p>The restructuring hinges entirely on Jon Rahm's contract leverage. If the highest-paid player accepts an equity settlement, the rest of the roster will likely follow into LIV 2.0. If Rahm fights it, the unsecured creditor queue will become a legal bloodbath.</p>
          </div>
          
          <div class="faq-section" style="margin-top: 40px;">
            <h2>Frequently Asked Questions</h2>
            
            <h3 style="font-size:1.1rem; margin-top:20px;">What happens to LIV Golf player contracts in Chapter 11?</h3>
            <p>Player contracts are treated as unsecured debt. Players will likely be offered a reduced cash settlement combined with equity in the newly restructured league.</p>
            
            <h3 style="font-size:1.1rem; margin-top:20px;">Will LIV Golf tournaments still happen in 2027?</h3>
            <p>If the restructuring is successful, LIV 2.0 plans to operate a reduced schedule of approximately 10 global events.</p>
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
          <a class="rel-card" href="/news-2026-pga-tour-winners-2026">
            <div class="cat">PGA TOUR</div>
            <h3>2026 PGA Tour Champions Directory</h3>
            <div class="d">MON 31 AUG · GOLFRAW</div>
          </a>
          <a class="rel-card" href="/news-2026-tour-championship-points-and-payouts">
            <div class="cat">TOURNAMENTS</div>
            <h3>Tour Championship Points and Payouts</h3>
            <div class="d">MON 31 AUG · GOLFRAW</div>
          </a>
          <a class="rel-card" href="/scottie-scheffler-swing-explained">
            <div class="cat">GUIDES</div>
            <h3>Scottie Scheffler's Swing Explained</h3>
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
      "@id": "https://www.golfraw.com/news-2026-liv-golf-bankruptcy-chapter-11-explained#article",
      "headline": "LIV Golf Bankruptcy: What Chapter 11 Would Actually Do | GOLFRAW",
      "name": "LIV Golf Bankruptcy: What Chapter 11 Would Actually Do | GOLFRAW",
      "description": "A Chapter 11 filing isn't the league shutting down. It's the vehicle for handing it to the players. What's verified, what isn't, and who gets paid last.",
      "articleSection": "News",
      "keywords": "LIV Golf, Chapter 11 Bankruptcy, PIF Funding, PGA Tour, Golf Business",
      "datePublished": "2026-08-31T17:00:00+02:00",
      "dateModified": "2026-08-31T17:00:00+02:00",
      "inLanguage": "en",
      "image": {
        "@type": "ImageObject",
        "url": "https://www.golfraw.com/public/liv-golf-bankruptcy-chapter-11-explained-2026.webp",
        "contentUrl": "https://www.golfraw.com/public/liv-golf-bankruptcy-chapter-11-explained-2026.webp",
        "width": 1200,
        "height": 675,
        "caption": "A LIV Golf branded tee marker at an empty tournament venue amid reports of a Chapter 11 bankruptcy filing."
      },
      "author": {"@id": "https://www.golfraw.com/about#editorial"},
      "publisher": {"@id": "https://www.golfraw.com#organization"}
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://www.golfraw.com/news-2026-liv-golf-bankruptcy-chapter-11-explained#breadcrumb",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.golfraw.com/"},
        {"@type": "ListItem", "position": 2, "name": "News", "item": "https://www.golfraw.com/news"},
        {"@type": "ListItem", "position": 3, "name": "LIV Golf", "item": "https://www.golfraw.com/liv-golf"},
        {"@type": "ListItem", "position": 4, "name": "LIV Golf Bankruptcy Explained", "item": "https://www.golfraw.com/news-2026-liv-golf-bankruptcy-chapter-11-explained"}
      ]
    },
    {"@type": "Person", "@id": "https://www.golfraw.com/about#editorial", "name": "GOLFRAW Editorial", "url": "https://www.golfraw.com/about"},
    {"@type": "Organization", "@id": "https://www.golfraw.com#organization", "name": "GOLFRAW", "url": "https://www.golfraw.com/"},
    {
      "@type": "FAQPage",
      "@id": "https://www.golfraw.com/news-2026-liv-golf-bankruptcy-chapter-11-explained#faq",
      "mainEntity": [
        {"@type": "Question", "name": "What happens to LIV Golf player contracts in Chapter 11?", "acceptedAnswer": {"@type": "Answer", "text": "Player contracts are treated as unsecured debt. Players will likely be offered a reduced cash settlement combined with equity in the newly restructured league."}},
        {"@type": "Question", "name": "Will LIV Golf tournaments still happen in 2027?", "acceptedAnswer": {"@type": "Answer", "text": "If the restructuring is successful, LIV 2.0 plans to operate a reduced schedule of approximately 10 global events."}}
      ]
    }
  ]
}
</script>"""

html = re.sub(r'<script type="application/ld\+json">.*?</script>', json_ld, html, flags=re.DOTALL)

with open('news-2026-liv-golf-bankruptcy-chapter-11-explained.html', 'w') as f:
    f.write(html)
