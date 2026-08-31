import json, re

with open('news-2026-scottie-scheffler-final-press-conference-answer.html', 'r') as f:
    html = f.read()

# 1. Header & Metadata
title = "Scheffler and Brandel Chamblee: The Full 2026 Arc | GOLFRAW"
description = "In April he didn't recognise Scheffler's swing. In August he called him miles ahead. Both takes were right, and the record proves it."
canonical_url = "https://www.golfraw.com/news-2026-scheffler-brandel-chamblee"
image_asset = "/public/scheffler-brandel-chamblee-2026.webp"

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
          <a href="/">RAWGOLF</a> / <a href="/pga-tour">PGA TOUR</a> / <span>SCHEFFLER & BRANDEL CHAMBLEE ARC</span>
        </nav>"""
html = re.sub(r'<nav class="crumbs".*?</nav>', new_vis_bc, html, flags=re.DOTALL)

html = re.sub(r'<h1.*?>.*?</h1>', f'<h1>Scheffler and Brandel Chamblee: The Full 2026 Arc</h1>', html, flags=re.DOTALL, count=1)
html = re.sub(r'<p class="standfirst">.*?</p>', f'<p class="standfirst">{description}</p>', html, flags=re.DOTALL)
html = re.sub(r'<span class="cat">.*?</span>', '<span class="cat">PGA TOUR • MEDIA ANALYSIS</span>', html, count=1)

hero_html = """<figure class="lead-img">
          <img src="/public/scheffler-brandel-chamblee-2026.webp" alt="Scottie Scheffler and Brandel Chamblee on the Golf Central set after the 2026 Tour Championship." width="1200" height="675" style="aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:8px;">
          <figcaption>SCOTTIE SCHEFFLER JOINED BRANDEL CHAMBLEE ON GOLF CENTRAL POSTGAME AFTER WINNING THE 2026 TOUR CHAMPIONSHIP, CAPPING A SEASON-LONG NARRATIVE ARC. PHOTO: RAWGOLF</figcaption>
        </figure>"""
html = re.sub(r'<figure class="lead-img">.*?</figure>', hero_html, html, flags=re.DOTALL)


new_body = """<div class="article-body">
          <div class="key-takeaways" style="background:#f4f4f4;padding:20px;margin-bottom:30px;border-left:4px solid var(--flag);">
            <h3>Key Takeaways</h3>
            <ul style="margin-top:10px;">
              <li><b>The Spring Critique Was Real:</b> Chamblee accurately diagnosed Scheffler's actual eight-month winless slump and open clubface mechanics during the Florida swing.</li>
              <li><b>The Summer Reversal:</b> By August, Chamblee used statistical evidence to declare Scheffler "miles ahead," proving his analysis tracks data, not personal bias.</li>
              <li><b>The Live Sit-Down:</b> Scheffler joining Chamblee on the Golf Central set at East Lake effectively debunked social media narratives of a feud between the two.</li>
            </ul>
          </div>

          <h2>Chamblee's 2026 Scheffler Timeline</h2>
          <div class="table-container" style="overflow-x:auto;">
            <table class="data-table" style="width:100%;border-collapse:collapse;margin-bottom:30px;font-family: 'IBM Plex Mono', monospace; font-size: 0.9rem;">
              <thead>
                <tr style="border-bottom: 2px solid var(--ink); text-align: left;">
                  <th style="padding: 10px 5px;">Timeframe</th>
                  <th style="padding: 10px 5px;">Chamblee's Take</th>
                  <th style="padding: 10px 5px;">The Reality</th>
                </tr>
              </thead>
              <tbody>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">April (Masters/Spring)</td><td style="padding: 10px 5px;">"Don't recognize this swing"</td><td style="padding: 10px 5px;">Scheffler missed top 10s at Riviera & Bay Hill, battling open face mechanics.</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">May (PGA Championship)</td><td style="padding: 10px 5px;">"Worst golf in years"</td><td style="padding: 10px 5px;">Scheffler endured a legitimate winless drought from January to August.</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">June (POTY Debate)</td><td style="padding: 10px 5px;">"Brilliantly consistent"</td><td style="padding: 10px 5px;">Chamblee compared his top-10 consistency to Nelly Korda but noted the 1-win barrier.</td>
                </tr>
                <tr>
                  <td style="padding: 10px 5px;">August (Playoffs)</td><td style="padding: 10px 5px;">"Scottie is miles ahead"</td><td style="padding: 10px 5px;">Wins St. Jude & East Lake, sweeps POTY debate, sets money record.</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h2>Verifying the Postgame Interview</h2>
          <p>The defining image of the 2026 PGA Tour season might just be Scottie Scheffler sitting across from Brandel Chamblee on the Golf Central postgame set at East Lake. The sit-down, hosted by Rich Lerner, was highly anticipated following a season where Chamblee's critical analysis of Scheffler's game frequently went viral on social media.</p>
          <p>During the broadcast, Scheffler answered questions thoroughly and respectfully. Social media rumors quickly circulated that Scheffler called Chamblee a "walking encyclopedia" as a subtle jab, but <a href="/news-2026-scottie-scheffler-final-press-conference-answer">a transcript of Scheffler's final press conference</a> and the broadcast tape confirms no such interaction occurred. It was a professional, data-driven conversation between the sport's best player and its most prominent analyst.</p>

          <h2>The Spring Critique vs Reality</h2>
          <p>To understand the magnitude of Chamblee's August praise, one must revisit his April critiques. During the Masters and the Florida swing, Chamblee stated he "didn't recognize this swing," pointing to a slightly more open clubface and erratic iron play.</p>
          <p>Golf Twitter framed this as personal animosity, but reality supported Chamblee's thesis. Scheffler was in the midst of a very real, very uncharacteristic winless drought stretching from January to August. As explored in our deep dive into <a href="/scottie-scheffler-swing-explained">Scheffler's swing mechanics</a>, the symptoms Chamblee highlighted on the Golf Channel monitor were mathematically present in Scheffler's strokes-gained approach data during that window.</p>

          <h2>The Player of the Year Turn</h2>
          <p>By June, as Scheffler began piling up top-5 finishes without securing trophies, Chamblee adjusted his stance based on the incoming data. He called Scheffler "brilliantly consistent" and drew parallels to Nelly Korda's dominance on the LPGA Tour.</p>
          <p>However, Chamblee correctly noted the historical barrier: you cannot win Player of the Year with only one victory. He laid out the exact mathematical path Scheffler needed to take in the FedExCup Playoffs to overtake the field. It wasn't hate; it was a roadmap.</p>

          <h2>How Sunday Sealed the Argument</h2>
          <p>When Scheffler closed with a cold-blooded 66 on Sunday at East Lake—recording just two bogeys over the weekend—he didn't just win $10 million and pass Tiger Woods on the all-time money list ($130.39 million). He broke the final mathematical barrier of the 2026 season.</p>
          <p>As <a href="/news-2026-hovland-on-what-makes-scheffler-successful">Viktor Hovland noted</a>, there is no magic to Scheffler's game; it's just relentless. Chamblee echoed this sentiment on Sunday night, declaring that "Scottie is miles ahead" of the rest of the professional golf ecosystem. The arc was complete: the analyst who highlighted the slump in the spring was the first to crown him in the summer.</p>

          <h2>Debunking 5 Viral Media Misconceptions</h2>
          <ul>
            <li><i>Myth 1: Chamblee hates Scheffler.</i> False. Chamblee's analysis is strictly tethered to TrackMan data and swing mechanics.</li>
            <li><i>Myth 2: Scheffler refused to go on Golf Channel.</i> False. He sat down with Chamblee and Lerner immediately following his Tour Championship victory.</li>
            <li><i>Myth 3: Scheffler was playing great in April.</i> False. By his own historic standards, his strokes-gained approach numbers dipped significantly during the spring.</li>
            <li><i>Myth 4: Chamblee said Scheffler couldn't win POTY.</i> False. He said he couldn't win it <i>with only one victory</i>, which was historically accurate.</li>
            <li><i>Myth 5: Scheffler insulted Chamblee on air.</i> False. The interview was entirely cordial and focused on course conditions and family.</li>
          </ul>

          <h2>The Raw Verdict</h2>
          <p>The supposed feud between Scottie Scheffler and Brandel Chamblee was entirely manufactured by social media aggregation accounts. Chamblee did his job in April by identifying mechanical flaws during a slump, and he did his job in August by contextualizing one of the greatest closing stretches in PGA Tour history. The data shifted, and the analysis shifted with it.</p>
          
          <div class="faq-section">
            <h2>Frequently Asked Questions</h2>
            
            <h3>Did Scottie Scheffler and Brandel Chamblee have a feud in 2026?</h3>
            <p>No. Social media framed Chamblee's critical swing analysis in April as a feud, but Scheffler's cordial postgame interview with Chamblee at East Lake proved it was purely a professional dynamic.</p>
            
            <h3>What did Brandel Chamblee say about Scottie Scheffler's swing?</h3>
            <p>In April, Chamblee criticized an open clubface that led to a slump in approach play. By August, after Scheffler fixed the issue and dominated the playoffs, Chamblee declared him "miles ahead" of the field.</p>
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
          <a class="rel-card" href="/news-2026-scottie-scheffler-final-press-conference-answer">
            <div class="cat">PGA TOUR</div>
            <h3>Scottie Scheffler's Final Press Conference Answer</h3>
            <div class="d">MON 31 AUG · GOLFRAW</div>
          </a>
          <a class="rel-card" href="/scottie-scheffler-swing-explained">
            <div class="cat">GUIDES</div>
            <h3>Scottie Scheffler's Swing Explained</h3>
            <div class="d">MON 31 AUG · GOLFRAW</div>
          </a>
          <a class="rel-card" href="/news-2026-hovland-on-what-makes-scheffler-successful">
            <div class="cat">PGA TOUR</div>
            <h3>Hovland on What Makes Scheffler Successful, in 8 Words</h3>
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
      "@id": "https://www.golfraw.com/news-2026-scheffler-brandel-chamblee#article",
      "headline": "Scheffler and Brandel Chamblee: The Full 2026 Arc | GOLFRAW",
      "name": "Scheffler and Brandel Chamblee: The Full 2026 Arc | GOLFRAW",
      "description": "In April he didn't recognise Scheffler's swing. In August he called him miles ahead. Both takes were right, and the record proves it.",
      "articleSection": "News",
      "keywords": "Scottie Scheffler, Brandel Chamblee, Golf Channel, PGA Tour, Golf Media",
      "datePublished": "2026-08-31T17:00:00+02:00",
      "dateModified": "2026-08-31T17:00:00+02:00",
      "inLanguage": "en",
      "image": {
        "@type": "ImageObject",
        "url": "https://www.golfraw.com/public/scheffler-brandel-chamblee-2026.webp",
        "contentUrl": "https://www.golfraw.com/public/scheffler-brandel-chamblee-2026.webp",
        "width": 1200,
        "height": 675,
        "caption": "Scottie Scheffler joined Brandel Chamblee on Golf Central Postgame after winning the 2026 Tour Championship."
      },
      "author": {"@id": "https://www.golfraw.com/about#editorial"},
      "publisher": {"@id": "https://www.golfraw.com#organization"}
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://www.golfraw.com/news-2026-scheffler-brandel-chamblee#breadcrumb",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.golfraw.com/"},
        {"@type": "ListItem", "position": 2, "name": "PGA Tour", "item": "https://www.golfraw.com/pga-tour"},
        {"@type": "ListItem", "position": 3, "name": "Scheffler & Brandel Chamblee Arc", "item": "https://www.golfraw.com/news-2026-scheffler-brandel-chamblee"}
      ]
    },
    {"@type": "Person", "@id": "https://www.golfraw.com/about#editorial", "name": "GOLFRAW Editorial", "url": "https://www.golfraw.com/about"},
    {"@type": "Organization", "@id": "https://www.golfraw.com#organization", "name": "GOLFRAW", "url": "https://www.golfraw.com/"},
    {
      "@type": "FAQPage",
      "@id": "https://www.golfraw.com/news-2026-scheffler-brandel-chamblee#faq",
      "mainEntity": [
        {"@type": "Question", "name": "Did Scottie Scheffler and Brandel Chamblee have a feud in 2026?", "acceptedAnswer": {"@type": "Answer", "text": "No. Social media framed Chamblee's critical swing analysis in April as a feud, but Scheffler's cordial postgame interview with Chamblee at East Lake proved it was purely a professional dynamic."}},
        {"@type": "Question", "name": "What did Brandel Chamblee say about Scottie Scheffler's swing?", "acceptedAnswer": {"@type": "Answer", "text": "In April, Chamblee criticized an open clubface that led to a slump in approach play. By August, after Scheffler fixed the issue and dominated the playoffs, Chamblee declared him 'miles ahead' of the field."}}
      ]
    }
  ]
}
</script>"""

html = re.sub(r'<script type="application/ld\+json">.*?</script>', json_ld, html, flags=re.DOTALL)

with open('news-2026-scheffler-brandel-chamblee.html', 'w') as f:
    f.write(html)
