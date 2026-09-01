import json, re
from scripts.article_header import (
    finalize_article_template_metadata,
    replace_article_header,
)

with open('article-template.html', 'r') as f:
    html = f.read()

# 1. Header & Metadata
title = "Why Pros Are Ditching Hybrids, and Why You Shouldn't | GOLFRAW"
description = "Hybrid use in the PGA Tour top 100 fell from 32% to 13%. On the LPGA it's 70%. The 15 mph gap explains both, and one man won a major with one."
canonical_url = "https://www.golfraw.com/why-pros-are-ditching-hybrids"
image_asset = "/public/why-pros-are-ditching-hybrids-analysis.webp"

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
          <img src="/public/why-pros-are-ditching-hybrids-analysis.webp" alt="A tour staff golf bag with high-lofted fairway woods and utility irons next to a hybrid at address." width="1200" height="675" style="aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:8px;">
          <figcaption>WHILE PGA TOUR USAGE DROPPED TO 13%, HYBRIDS REMAIN AT 70% ON THE LPGA AND 74% ON PGA TOUR CHAMPIONS DUE TO SWING SPEED DYNAMICS. PHOTO: RAWGOLF</figcaption>
        </figure>
"""
if '<figure class="lead-img">' in html:
    html = re.sub(r'<figure class="lead-img">.*?</figure>', hero_html, html, flags=re.DOTALL)
else:
    html = html.replace('</header>', '</header>\n' + hero_html)

new_vis_bc = """<nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/guides">Guides</a> / <span>Why Pros Are Ditching Hybrids</span>
        </nav>"""
html = re.sub(r'<nav class="crumbs".*?</nav>', new_vis_bc, html, flags=re.DOTALL)

html = replace_article_header(
    html,
    "Why Pros Are Ditching Hybrids, and Why You Shouldn't",
    description,
)

new_body = """<div class="article-body">
          <div class="takeaways">
            <h3 style="margin-top:0;">Key Takeaways</h3>
            <ul>
              <li><b>The PGA Tour Exodus:</b> Only 13 of the top 100 PGA Tour players regularly bag a hybrid, down drastically from 2010.</li>
              <li><b>Speed Dictates Gear:</b> At 102+ mph clubhead speeds, hybrids produce severe hooks. At 87 mph (average LPGA and amateur), they produce high, straight ball flights.</li>
              <li><b>The Replacements:</b> Elite pros are replacing hybrids with 7-woods, 9-woods, Callaway Apex UWs, and Utility Irons.</li>
              <li><b>Amateur Data:</b> Arccos data analyzing over 200 million shots proves hybrids beat 4-irons in GIR percentages for every amateur bracket except scratch golfers.</li>
            </ul>
          </div>

          <h2>Tour vs Amateur Hybrid & Long-Iron Data Comparison</h2>
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>Metric</th>
                  <th>PGA Tour</th>
                  <th>LPGA / Champions Tour</th>
                  <th>Mid-Handicap Amateurs (10-15)</th>
                </tr>
              </thead>
              <tbody>
                <tr><td><b>Avg. Swing Speed (Iron)</b></td><td>102 mph</td><td>~87 mph</td><td>~85 mph</td></tr>
                <tr><td><b>Hybrid Adoption Rate</b></td><td>13%</td><td>70% - 74%</td><td>High (>75%)</td></tr>
                <tr><td><b>Long Iron GIR (>175/200 yds)</b></td><td>Elite control</td><td>Lower stopping power</td><td>Very Poor</td></tr>
                <tr><td><b>Primary Replacement</b></td><td>7-wood, Apex UW, Utility Iron</td><td>Hybrids, 7-woods</td><td>Hybrids</td></tr>
              </tbody>
            </table>
          </div>

          <h2>How Far Hybrid Usage Has Fallen on the PGA Tour</h2>
          <p>If you attended a PGA Tour event in 2010, you would regularly see 130 to 140 hybrids in the field. Today, they are a dying breed on the men's circuit. Current equipment audits reveal that only 13 of the top 100 players in the world consistently bag a hybrid. The usage rate has plummeted from roughly 40% a decade ago down to just 13%.</p>

          <h2>What Is Replacing Them?</h2>
          <p>Nature abhors a vacuum, and the 225-yard gap in a PGA Tour bag has been filled by three distinct clubs:</p>
          <ul>
            <li><b>High-Lofted Fairway Woods (7-woods, 9-woods):</b> Players like Ludvig Åberg, Patrick Cantlay, Max Homa, and Tyrrell Hatton have fully embraced the 7-wood. Tommy Fleetwood and Adam Scott occasionally deploy 9-woods. These clubs launch higher, spin more, and land softer than hybrids.</li>
            <li><b>The Hybrid-Wood Tweener:</b> The Callaway Apex UW is heavily favored by Xander Schauffele and Akshay Bhatia. It offers wood-like launch with hybrid-like versatility without the severe draw bias.</li>
            <li><b>Utility Irons:</b> Gary Woodland and Min Woo Lee prefer driving irons for piercing ball flights in windy conditions, relying on their immense swing speeds to generate adequate launch.</li>
          </ul>

          <h2>Why Pros Moved Away: The High-Speed Hook</h2>
          <p>The death of the hybrid on the PGA Tour comes down to clubhead speed and center of gravity. Hybrids feature deep, low, and heel-biased weighting designed to help amateurs launch the ball and fight slices. When a tour pro swings a hybrid at 102 mph, that same weighting causes the clubface to snap shut, producing a violent, uncontrollable hook.</p>
          <p>Furthermore, hybrids lack workability. Xander Schauffele famously <a href="/news-2026-pga-tour-winners-2026">swapped out his equipment ahead of his Open Championship victory at Royal Troon</a>, opting for clubs he could reliably fade—a shot shape that is notoriously difficult to execute with a modern hybrid at tour speeds.</p>

          <h2>What the 200M Shot Amateur Data Proves</h2>
          <p>While the PGA Tour avoids them, amateurs absolutely shouldn't. Arccos Golf and Shot Scope data analyzing over 200 million golf shots reveals a brutal truth: unless you are a scratch golfer, you should not be hitting a 4-iron. Across all mid-to-high handicap brackets (5-20), hybrids unequivocally outperform long irons in both total distance and Greens in Regulation (GIR) percentages. The 15 mph swing speed gap between a Tour pro and a 12-handicap perfectly utilizes the hybrid's heel-weighting to straighten out natural slices and elevate the ball.</p>
          <p>Before you copy a tour pro's setup, run your own numbers through our <a href="/tools/bag-audit">Bag Audit Tool</a> to see where your gaps lie.</p>

          <h2>Rules Audit: Rule 4.1b (The 14-Club Limit)</h2>
          <p>When swapping between long irons, hybrids, and 7-woods to dial in yardages, players must rigidly adhere to <b>Rule 4.1b</b>. A player must not start a round with more than 14 clubs. The penalty for exceeding this limit is severe: two penalty strokes for each hole where a breach occurred, with a maximum penalty of four strokes per round.</p>

          <h2>Fact-Checking 5 Common Equipment Myths</h2>
          <ul>
            <li><i>Myth 1: No one wins majors with hybrids anymore.</i> False. Aaron Rai won the 2026 PGA Championship at Aronimink bagging a Titleist GT2 24° hybrid.</li>
            <li><i>Myth 2: 7-woods are only for seniors.</i> False. The hardest swingers on the PGA Tour (like Cantlay and Åberg) use them to stop the ball on firm greens.</li>
            <li><i>Myth 3: Scratch golfers shouldn't use hybrids.</i> False. While the cutoff for hybrid advantage peaks around scratch, many + handicaps successfully bag them; Russell Henley won the Charles Schwab Challenge using one.</li>
            <li><i>Myth 4: A 3-iron and a 3-hybrid go the same distance.</i> False. Even with identical lofts, the longer shaft and hotter face of a hybrid typically produce 10-15 more yards.</li>
            <li><i>Myth 5: Hybrids are hook machines for everyone.</i> False. They are hook machines at 100+ mph; at 85 mph, they are slice-correcting lifesavers.</li>
          </ul>

          <div class="verdict-box">
            <h3>The Raw Verdict</h3>
            <p>Don't let PGA Tour trends ruin your scorecard. The 7-wood is a brilliant club, but for the average amateur swinging 85 mph, the hybrid remains the ultimate cheat code for long approach shots.</p>
          </div>
          
          <section class="sources" aria-labelledby="faq-label">
            <h2 id="faq-label" style="font-size: 1.25rem; font-family: 'IBM Plex Mono', monospace; text-transform: uppercase;">FAQ</h2>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">Why do PGA Tour pros hook hybrids?</h3>
              <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">Hybrids are built with a heel-biased center of gravity to help amateurs fight slices. When swung at tour speeds (100+ mph), this weighting causes the clubface to close rapidly, resulting in severe hooks.</p>
              </div>
            </div>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">Should a mid-handicap amateur use a 4-iron or a hybrid?</h3>
              <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">Data shows that mid-to-high handicap amateurs hit hybrids significantly higher, straighter, and with a better Greens in Regulation percentage than a 4-iron.</p>
              </div>
            </div>
          </section>

          <section class="sources" aria-labelledby="sources-label">
            <p class="section-label" id="sources-label">Sources</p>
            <ol>
              <li><a href="/guides">GOLFRAW: Guides</a>. Equipment, technique, and strategic analysis.</li>
              <li><a href="/tools/bag-audit">Bag Audit Tool</a>. Evaluate your own gapping and hybrid needs.</li>
              <li><a href="/news-2026-pga-tour-winners-2026">2026 PGA Tour Winners</a>. Examining the bags of this season's champions.</li>
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
              <li><a href="/tools/bag-audit">Interactive Bag Audit Tool</a></li>
              <li><a href="/news-2026-pga-tour-winners-2026">2026 PGA Tour Winners Gear Breakdown</a></li>
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
      "@type": "Article",
      "@id": "https://www.golfraw.com/why-pros-are-ditching-hybrids#article",
      "headline": "Why Pros Are Ditching Hybrids, and Why You Shouldn't | GOLFRAW",
      "name": "Why Pros Are Ditching Hybrids, and Why You Shouldn't | GOLFRAW",
      "description": "Hybrid use in the PGA Tour top 100 fell from 32% to 13%. On the LPGA it's 70%. The 15 mph gap explains both, and one man won a major with one.",
      "articleSection": "Guides",
      "keywords": "Hybrids, 7-wood, PGA Tour Gear, Golf Equipment, Amateur Golf Data, Arccos Data",
      "datePublished": "2026-08-30T17:00:00+02:00",
      "dateModified": "2026-08-30T17:00:00+02:00",
      "inLanguage": "en",
      "image": {
        "@type": "ImageObject",
        "url": "https://www.golfraw.com/public/why-pros-are-ditching-hybrids-analysis.webp",
        "contentUrl": "https://www.golfraw.com/public/why-pros-are-ditching-hybrids-analysis.webp",
        "width": 1200,
        "height": 675,
        "caption": "A tour staff golf bag with high-lofted fairway woods and utility irons next to a hybrid at address."
      },
      "author": {"@id": "https://www.golfraw.com/about#editorial"},
      "publisher": {"@id": "https://www.golfraw.com#organization"},
      "about": [
        {"@type": "Thing", "name": "Golf Equipment"}
      ]
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://www.golfraw.com/why-pros-are-ditching-hybrids#breadcrumb",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.golfraw.com/"},
        {"@type": "ListItem", "position": 2, "name": "Guides", "item": "https://www.golfraw.com/guides"},
        {"@type": "ListItem", "position": 3, "name": "Why Pros Are Ditching Hybrids", "item": "https://www.golfraw.com/why-pros-are-ditching-hybrids"}
      ]
    },
    {"@type": "Person", "@id": "https://www.golfraw.com/about#editorial", "name": "GOLFRAW Editorial", "url": "https://www.golfraw.com/about"},
    {"@type": "Organization", "@id": "https://www.golfraw.com#organization", "name": "GOLFRAW", "url": "https://www.golfraw.com/"},
    {
      "@type": "FAQPage",
      "@id": "https://www.golfraw.com/why-pros-are-ditching-hybrids#faq",
      "mainEntity": [
        {"@type": "Question", "name": "Why do PGA Tour pros hook hybrids?", "acceptedAnswer": {"@type": "Answer", "text": "Hybrids are built with a heel-biased center of gravity to help amateurs fight slices. When swung at tour speeds (100+ mph), this weighting causes the clubface to close rapidly, resulting in severe hooks."}},
        {"@type": "Question", "name": "Should a mid-handicap amateur use a 4-iron or a hybrid?", "acceptedAnswer": {"@type": "Answer", "text": "Data shows that mid-to-high handicap amateurs hit hybrids significantly higher, straighter, and with a better Greens in Regulation percentage than a 4-iron."}}
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

with open('why-pros-are-ditching-hybrids.html', 'w') as f:
    f.write(html)
