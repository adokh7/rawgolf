import json, re

with open('news-2026-tour-championship-tee-times-round-4.html', 'r') as f:
    html = f.read()

# 1. Header & Metadata
title = "LIV Golf Settlement Offers: Cents on the Dollar, Explained | GOLFRAW"
description = "Take a fraction now and join a smaller league, or hold out and queue as an unsecured creditor. What the offers say, and who's waiting on the answer."
canonical_url = "https://www.golfraw.com/news-2026-liv-golf-settlement-offers-bankruptcy"
image_asset = "/public/liv-golf-settlement-offers-bankruptcy-2026.webp"

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
          <a href="/">RAWGOLF</a> / <a href="/news">NEWS</a> / <a href="/liv-golf">LIV GOLF</a> / <span>SETTLEMENT OFFERS</span>
        </nav>"""
html = re.sub(r'<nav class="crumbs".*?</nav>', new_vis_bc, html, flags=re.DOTALL)

html = re.sub(r'<h1 class="headline">.*?</h1>', f'<h1 class="headline">LIV Golf Settlement Offers: Cents on the Dollar, Explained</h1>', html, flags=re.DOTALL)
html = re.sub(r'<p class="standfirst">.*?</p>', f'<p class="standfirst">{description}</p>', html, flags=re.DOTALL)
html = re.sub(r'<span class="cat">.*?</span>', '<span class="cat">NEWS · LIV GOLF</span>', html)

hero_html = """<figure class="lead-img">
       <img src="/public/liv-golf-settlement-offers-bankruptcy-2026.webp" alt="A LIV Golf team logo and tournament branding at a venue amid settlement offers and Chapter 11 restructuring talks." width="1200" height="675" style="aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:8px;">
     </figure>
     <figcaption>LIV GOLF PLAYERS WITH GUARANTEED CONTRACTS PAST 2026 FACE SETTLEMENT OFFERS REPORTEDLY WORTH CENTS ON THE DOLLAR AHEAD OF A POTENTIAL CHAPTER 11 FILING. PHOTO: RAWGOLF</figcaption>"""
html = re.sub(r'<figure class="lead-img">.*?</figcaption>\s*</figure>', hero_html, html, flags=re.DOTALL)
html = re.sub(r'<figure class="lead-img">.*?</figcaption>', hero_html, html, flags=re.DOTALL)
if '<figure class="lead-img">' in html and '<figcaption>' in html:
    html = re.sub(r'<figure class="lead-img">.*?</figure>\s*<figcaption>.*?</figcaption>', hero_html, html, flags=re.DOTALL)

new_body = """<div class="article-body">
          <div class="takeaways-box" style="background:#f4f4f4;padding:20px;margin-bottom:30px;border-left:4px solid var(--flag);">
            <h3>Key Takeaways</h3>
            <ul style="margin-top:10px;">
              <li><b>Fractional Buyouts:</b> Players with guaranteed contracts extending past 2026 are being offered "cents on the dollar" cash buyouts ahead of a Chapter 11 filing.</li>
              <li><b>The Equity Play:</b> To offset the massive cash haircuts, LIV 2.0 is offering players equity in the newly restructured league.</li>
              <li><b>BC Partners Lurking:</b> Private capital firm BC Partners is exploring an investment, contingent on LIV wiping out player debt and preserving massive Net Operating Losses (NOLs).</li>
            </ul>
          </div>

          <h2>Player Options & Financial Restructuring Matrix</h2>
          <div class="table-container" style="overflow-x:auto;">
            <table style="width:100%; border-collapse: collapse; font-family: 'IBM Plex Mono', monospace; font-size: 0.9rem;">
              <thead>
                <tr style="border-bottom: 2px solid var(--ink); text-align: left;">
                  <th style="padding: 10px 5px;">Choice</th>
                  <th style="padding: 10px 5px;">Compensation Structure</th>
                  <th style="padding: 10px 5px;">Playing Status Outcome</th>
                </tr>
              </thead>
              <tbody>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;"><b>Door 1 (Settle & Stay)</b></td><td style="padding: 10px 5px;">Reduced cash settlement + Equity/Shares in LIV 2.0</td><td style="padding: 10px 5px;">Participate in ~10 global events; open tour cross-participation (if allowed)</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;"><b>Door 2 (Settle & Leave)</b></td><td style="padding: 10px 5px;">"Cents on the dollar" cash buyout</td><td style="padding: 10px 5px;">Free agent; immediate exit (PGA/DP World Tour status heavily restricted)</td>
                </tr>
                <tr>
                  <td style="padding: 10px 5px;"><b>Door 3 (Reject & Fight)</b></td><td style="padding: 10px 5px;">Unsecured creditor claim for full contract value</td><td style="padding: 10px 5px;">Queued behind PIF's DIP loan in bankruptcy court; massive legal fees</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h2>The Settlement Terms: Equity Over Cash</h2>
          <p>As <a href="/news-2026-liv-golf-bankruptcy-chapter-11-explained">details of the impending Chapter 11 restructuring emerge</a>, the stark financial reality for LIV Golf's roster has come into focus. The primary leverage point of the restructuring is erasing billions in guaranteed contract liabilities extending past 2026.</p>
          <p>The settlement offers currently circulating among player agents represent a massive cash haircut—widely described as "cents on the dollar." In exchange for tearing up the guaranteed PIF cash, players are being offered equity in "LIV 2.0," a restructured, player-owned cooperative entity. It is a high-risk gamble: swapping guaranteed sovereign wealth money for shares in an unproven, newly bankrupt golf league.</p>

          <h2>The Unsecured Creditor Reality</h2>
          <p>Players who refuse the fractional settlement face a grim legal reality known as the Unsecured Creditor Trap. In a Chapter 11 restructuring, debt hierarchy is absolute. The Public Investment Fund (PIF) is expected to provide Debtor-in-Possession (DIP) financing—reportedly under $100 million—to keep the lights on during the bankruptcy process.</p>
          <p>By law, DIP financing receives super-priority status. If a player rejects the settlement and sues for their full contract value, they join unpaid app developers, hospitality vendors, and production crews at the back of the line as unsecured creditors, waiting for whatever scraps remain after PIF is made whole.</p>

          <h2>The Hidden Player: BC Partners and Tax Assets</h2>
          <p>The restructuring isn't just about dumping player contracts; it's about making the entity investable. Private capital firm BC Partners is reportedly examining an equity-like investment in LIV 2.0. However, their involvement is strictly contingent on two factors:</p>
          <ol>
            <li>Wiping the balance sheet clean of the guaranteed player contract debt.</li>
            <li>Preserving LIV's massive Net Operating Losses (NOLs). After burning through $5 billion, LIV possesses staggering NOL tax assets that could be highly lucrative for a private equity partner, provided the restructuring is handled correctly under Section 382 of the Internal Revenue Code.</li>
          </ol>

          <h2>Pre-Filing Cutbacks: Canceled Events and Lawsuits</h2>
          <p>The financial distress is already visible operationally. LIV recently canceled the highly promoted 2026 Michigan Team Championship. Furthermore, following Joel Beall's reporting in Golf Digest, sweeping staff terminations are effectively concluding by the first week of September.</p>
          <p>Vendor lawsuits are piling up, providing a preview of the unsecured creditor queue. Most notably, a $992,000 lawsuit regarding unpaid app development fees was recently filed, underscoring the severe liquidity crisis gripping the original corporate entity.</p>

          <h2>The Blocked Exits</h2>
          <p>Players considering "Door 2" (taking the cash buyout and leaving) face a harsh professional reality. The PGA Tour Returning Member Program remains heavily restricted. Executives like Brian Rolapp have maintained strict sanction policies, and the window for high-profile returns (like the rumors surrounding Brooks Koepka earlier this year) appears to be closed. DP World Tour fines and suspensions also remain in full effect, leaving exiting players effectively stateless in professional golf.</p>

          <h2>Fact-Checking 5 Common Misconceptions</h2>
          <ul>
            <li><i>Myth 1: Players will eventually get 100% of their contracts.</i> False. In bankruptcy, unsecured contract debt is almost never paid out in full.</li>
            <li><i>Myth 2: Equity in LIV 2.0 guarantees future wealth.</i> False. Equity is only valuable if the restructured league becomes profitable or is sold, which remains highly speculative.</li>
            <li><i>Myth 3: The PGA Tour must accept players back if LIV goes bankrupt.</i> False. The PGA Tour operates as an independent entity and enforces its own disciplinary guidelines for unauthorized events.</li>
            <li><i>Myth 4: PIF is walking away entirely.</i> False. By providing DIP financing, PIF maintains ultimate leverage and priority control over the bankruptcy process.</li>
            <li><i>Myth 5: All players received the exact same settlement offer.</i> False. Settlements are reportedly tiered based on remaining contract length, initial signing bonuses, and player leverage (e.g., Jon Rahm).</li>
          </ul>

          <div class="verdict-box" style="margin-top: 30px; padding: 20px; background-color: #111; color: #fff; border-left: 4px solid var(--flag);">
            <h3 style="color: #fff;">The Raw Verdict</h3>
            <p>The entire Chapter 11 maneuver hinges on Jon Rahm. If the highest-paid asset accepts the fractional cash and equity settlement, the rest of the locker room will likely fold. If Rahm weaponizes his contract and fights, the bankruptcy court will become the most expensive battleground in golf history.</p>
          </div>
          
          <div class="faq-section" style="margin-top: 40px;">
            <h2>Frequently Asked Questions</h2>
            
            <h3 style="font-size:1.1rem; margin-top:20px;">What happens if a LIV Golf player refuses the settlement offer?</h3>
            <p>If a player refuses the settlement, their contract is treated as unsecured debt in the bankruptcy filing. They must sue in court and wait behind secured creditors, like PIF, for any potential payout.</p>
            
            <h3 style="font-size:1.1rem; margin-top:20px;">Can LIV Golf players return to the PGA Tour?</h3>
            <p>Currently, LIV players face strict returning guidelines, massive fines, and suspensions enforced by both the PGA Tour and the DP World Tour, complicating any potential return.</p>
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
          <a class="rel-card" href="/news-2026-liv-golf-bankruptcy-chapter-11-explained">
            <div class="cat">LIV GOLF</div>
            <h3>LIV Golf Bankruptcy: What Chapter 11 Would Actually Do</h3>
            <div class="d">MON 31 AUG · GOLFRAW</div>
          </a>
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
      "@id": "https://www.golfraw.com/news-2026-liv-golf-settlement-offers-bankruptcy#article",
      "headline": "LIV Golf Settlement Offers: Cents on the Dollar, Explained | GOLFRAW",
      "name": "LIV Golf Settlement Offers: Cents on the Dollar, Explained | GOLFRAW",
      "description": "Take a fraction now and join a smaller league, or hold out and queue as an unsecured creditor. What the offers say, and who's waiting on the answer.",
      "articleSection": "News",
      "keywords": "LIV Golf Settlement, Chapter 11 Bankruptcy, PIF, Golf Contracts, Jon Rahm",
      "datePublished": "2026-08-31T17:00:00+02:00",
      "dateModified": "2026-08-31T17:00:00+02:00",
      "inLanguage": "en",
      "image": {
        "@type": "ImageObject",
        "url": "https://www.golfraw.com/public/liv-golf-settlement-offers-bankruptcy-2026.webp",
        "contentUrl": "https://www.golfraw.com/public/liv-golf-settlement-offers-bankruptcy-2026.webp",
        "width": 1200,
        "height": 675,
        "caption": "LIV Golf players face settlement offers worth cents on the dollar ahead of a potential Chapter 11 filing."
      },
      "author": {"@id": "https://www.golfraw.com/about#editorial"},
      "publisher": {"@id": "https://www.golfraw.com#organization"}
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://www.golfraw.com/news-2026-liv-golf-settlement-offers-bankruptcy#breadcrumb",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.golfraw.com/"},
        {"@type": "ListItem", "position": 2, "name": "News", "item": "https://www.golfraw.com/news"},
        {"@type": "ListItem", "position": 3, "name": "LIV Golf", "item": "https://www.golfraw.com/liv-golf"},
        {"@type": "ListItem", "position": 4, "name": "LIV Settlement Offers Explained", "item": "https://www.golfraw.com/news-2026-liv-golf-settlement-offers-bankruptcy"}
      ]
    },
    {"@type": "Person", "@id": "https://www.golfraw.com/about#editorial", "name": "GOLFRAW Editorial", "url": "https://www.golfraw.com/about"},
    {"@type": "Organization", "@id": "https://www.golfraw.com#organization", "name": "GOLFRAW", "url": "https://www.golfraw.com/"},
    {
      "@type": "FAQPage",
      "@id": "https://www.golfraw.com/news-2026-liv-golf-settlement-offers-bankruptcy#faq",
      "mainEntity": [
        {"@type": "Question", "name": "What happens if a LIV Golf player refuses the settlement offer?", "acceptedAnswer": {"@type": "Answer", "text": "If a player refuses the settlement, their contract is treated as unsecured debt in the bankruptcy filing. They must sue in court and wait behind secured creditors, like PIF, for any potential payout."}},
        {"@type": "Question", "name": "Can LIV Golf players return to the PGA Tour?", "acceptedAnswer": {"@type": "Answer", "text": "Currently, LIV players face strict returning guidelines, massive fines, and suspensions enforced by both the PGA Tour and the DP World Tour, complicating any potential return."}}
      ]
    }
  ]
}
</script>"""

html = re.sub(r'<script type="application/ld\+json">.*?</script>', json_ld, html, flags=re.DOTALL)

with open('news-2026-liv-golf-settlement-offers-bankruptcy.html', 'w') as f:
    f.write(html)
