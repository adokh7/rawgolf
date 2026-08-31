import json, re

with open('news-2026-tour-championship-tee-times-round-4.html', 'r') as f:
    html = f.read()

# 1. Header & Metadata
title = "Scottie Scheffler's Final Press Conference Answer of 2026 | GOLFRAW"
description = "No existential monologue this time. Wind, fighting back, and travelling with his wife and two sons. Why the boring version tells you more."
canonical_url = "https://www.golfraw.com/news-2026-scottie-scheffler-final-press-conference-answer"
image_asset = "/public/scottie-scheffler-final-press-conference-answer-2026.webp"

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
          <a href="/">RAWGOLF</a> / <a href="/pga-tour">PGA TOUR</a> / <span>SCHEFFLER FINAL PRESS CONFERENCE</span>
        </nav>"""
html = re.sub(r'<nav class="crumbs".*?</nav>', new_vis_bc, html, flags=re.DOTALL)

html = re.sub(r'<h1 class="headline">.*?</h1>', f'<h1 class="headline">Scottie Scheffler\'s Final Press Conference Answer of 2026</h1>', html, flags=re.DOTALL)
html = re.sub(r'<p class="standfirst">.*?</p>', f'<p class="standfirst">{description}</p>', html, flags=re.DOTALL)
html = re.sub(r'<span class="cat">.*?</span>', '<span class="cat">PGA TOUR · NEWS</span>', html)

hero_html = """<figure class="lead-img">
       <img src="/public/scottie-scheffler-final-press-conference-answer-2026.webp" alt="Scottie Scheffler at the media center press conference podium after winning the 2026 Tour Championship." width="1200" height="675" style="aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:8px;">
     </figure>
     <figcaption>SCOTTIE SCHEFFLER CLOSED OUT HIS HISTORIC 2026 CAMPAIGN WITH A REFRESHINGLY GROUNDED PRESS CONFERENCE FOCUSING ON CONDITIONS, RESILIENCE, AND FAMILY. PHOTO: RAWGOLF</figcaption>"""
html = re.sub(r'<figure class="lead-img">.*?</figcaption>\s*</figure>', hero_html, html, flags=re.DOTALL)
html = re.sub(r'<figure class="lead-img">.*?</figcaption>', hero_html, html, flags=re.DOTALL)
if '<figure class="lead-img">' in html and '<figcaption>' in html:
    html = re.sub(r'<figure class="lead-img">.*?</figure>\s*<figcaption>.*?</figcaption>', hero_html, html, flags=re.DOTALL)

new_body = """<div class="article-body">
          <div class="takeaways-box" style="background:#f4f4f4;padding:20px;margin-bottom:30px;border-left:4px solid var(--flag);">
            <h3>Key Takeaways</h3>
            <ul style="margin-top:10px;">
              <li><b>Grounded Reality:</b> Scheffler's final remarks of 2026 focused on the brutal course conditions and his growing family, contrasting sharply with his existential 2025 monologues.</li>
              <li><b>"Fighting Back":</b> He highlighted his resilience—specifically grinding out top finishes after over-par opening rounds earlier in the season—as his proudest achievement.</li>
              <li><b>Statistical Anomaly:</b> Scheffler closed a historic season capturing 3 wins, 13 top-5 finishes, and the all-time career money list record at over $130.39 million.</li>
            </ul>
          </div>

          <h2>2026 Season Statistical Breakdown</h2>
          <div class="table-container" style="overflow-x:auto;">
            <table style="width:100%; border-collapse: collapse; font-family: 'IBM Plex Mono', monospace; font-size: 0.9rem;">
              <thead>
                <tr style="border-bottom: 2px solid var(--ink); text-align: left;">
                  <th style="padding: 10px 5px;">Metric</th>
                  <th style="padding: 10px 5px;">Total</th>
                  <th style="padding: 10px 5px;">Notes</th>
                </tr>
              </thead>
              <tbody>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">Wins</td><td style="padding: 10px 5px;">3</td><td style="padding: 10px 5px;">Including Tour Championship (FedExCup)</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">Runner-Up Finishes</td><td style="padding: 10px 5px;">5</td><td style="padding: 10px 5px;">2 losses occurred in playoffs</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">Top-5 Finishes</td><td style="padding: 10px 5px;">13</td><td style="padding: 10px 5px;">Per CBS's Trevor Immelman tracking</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">Top-25 Finishes</td><td style="padding: 10px 5px;">17 of 18</td><td style="padding: 10px 5px;">Incredible consistency metric</td>
                </tr>
                <tr>
                  <td style="padding: 10px 5px;">Single-Season Earnings</td><td style="padding: 10px 5px;">$30M+</td><td style="padding: 10px 5px;">Career: $130,390,661 — 1st All-Time</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h2>The Opening Statements: Conditions and Resilience</h2>
          <p>When Scottie Scheffler sat down in the East Lake media center as the 2026 FedExCup Champion, the golf world braced for a sweeping soliloquy. Instead, he delivered a clinical breakdown of the golf course. He addressed the unusual Atlanta winds, the baked-out firmness of the layout, and his late birdie surge on a brutal Sunday where only 14 of 29 players managed to break par.</p>
          <p>It was a profoundly boring opening statement, but it perfectly summarized why he is currently unbeatable. While the media sought grand narratives, <a href="/scottie-scheffler-swing-explained">Scheffler's mind was still processing trajectory control and green firmness</a>.</p>

          <h2>"Proud of Fighting Back"</h2>
          <p>When pressed on his most significant accomplishment of the year, Scheffler didn't point to the massive $10 million payout or the three trophies. He pointed to Thursday afternoons.</p>
          <p>"I'm most proud of fighting back," Scheffler said. He specifically referenced grinding through over-par opening rounds at the WM Phoenix Open, the Genesis Invitational, and the U.S. Open. In all three instances, he battled back through the cutline to secure podium finishes. That relentless refusal to punt a bad week is the true architecture of his historic season.</p>

          <h2>Weekend Anatomy: Erasing Hovland</h2>
          <p>The resilience he spoke of was on full display during the weekend at East Lake. Scheffler recorded just two bogeys over his final 36 holes. On Sunday, facing a three-shot deficit to Viktor Hovland on the first tee, Scheffler methodically wiped it out by the 5th hole. He closed with a cold-blooded 66 to beat Hovland by three shots.</p>
          <p>As <a href="/news-2026-hovland-on-what-makes-scheffler-successful">Hovland noted earlier in the week</a>, there is no magic to it. He simply refuses to make mistakes when the pressure redlines.</p>

          <h2>The Closing Answer: Family Over Everything</h2>
          <p>The starkest contrast of the press conference came at the very end. Flashback to Portrush in 2025, where Scheffler famously delivered an existential monologue about his faith, stating that "sport is not where to seek ultimate satisfaction." It was heavy, introspective, and widely dissected.</p>
          <p>His final answer of 2026 was drastically different. Asked what comes next, Scheffler smiled. "Traveling with my wife Meredith and my two boys," he said. He spoke about the logistics of car seats, the chaos of packing, and the relief of returning home. The existential weight of 2025 has been replaced by the settled, grounded reality of fatherhood. He isn't searching for satisfaction anymore; he already has it.</p>

          <h2>Debunking 4 Season-Long Narratives</h2>
          <ul>
            <li><i>Myth 1: Scheffler struggles from behind.</i> False. His weekend performance at East Lake, wiping out a 3-shot deficit, proves his elite closing ability.</li>
            <li><i>Myth 2: His putting is a fatal flaw.</i> False. While streaky, his ball-striking metrics completely insulate his scorecard from average putting weeks.</li>
            <li><i>Myth 3: The money record is inflated by signature events.</i> False. While purses are larger, <a href="/news-2026-tiger-woods-career-money-list-record">surpassing Tiger Woods' career earnings</a> in a fraction of the time requires an unprecedented win rate.</li>
            <li><i>Myth 4: He is exhausted by the pressure.</i> False. His grounded press conference demeanor indicates a player completely insulated from external media pressure.</li>
          </ul>

          <div class="verdict-box" style="margin-top: 30px; padding: 20px; background-color: #111; color: #fff; border-left: 4px solid var(--flag);">
            <h3 style="color: #fff;">The Raw Verdict</h3>
            <p>Scottie Scheffler's 2026 season was a masterclass in suffocating consistency. His final press conference proved that the most dominant player in golf is also the most emotionally stable. He has built a life that makes golf secondary, which ironically makes him impossible to beat.</p>
          </div>
          
          <div class="faq-section" style="margin-top: 40px;">
            <h2>Frequently Asked Questions</h2>
            
            <h3 style="font-size:1.1rem; margin-top:20px;">What did Scottie Scheffler say in his final 2026 press conference?</h3>
            <p>Scheffler focused on the difficulty of the course conditions, his pride in fighting back from poor opening rounds throughout the year, and his excitement to travel home with his wife and two sons.</p>
            
            <h3 style="font-size:1.1rem; margin-top:20px;">How much money did Scottie Scheffler make in 2026?</h3>
            <p>Scheffler earned over $30 million in official prize money during the 2026 season, elevating his career total past $130.39 million to become the highest-earning player in PGA Tour history.</p>
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
      "@id": "https://www.golfraw.com/news-2026-scottie-scheffler-final-press-conference-answer#article",
      "headline": "Scottie Scheffler's Final Press Conference Answer of 2026 | GOLFRAW",
      "name": "Scottie Scheffler's Final Press Conference Answer of 2026 | GOLFRAW",
      "description": "No existential monologue this time. Wind, fighting back, and travelling with his wife and two sons. Why the boring version tells you more.",
      "articleSection": "News",
      "keywords": "Scottie Scheffler, PGA Tour, Tour Championship, FedExCup, Golf Interview",
      "datePublished": "2026-08-31T17:00:00+02:00",
      "dateModified": "2026-08-31T17:00:00+02:00",
      "inLanguage": "en",
      "image": {
        "@type": "ImageObject",
        "url": "https://www.golfraw.com/public/scottie-scheffler-final-press-conference-answer-2026.webp",
        "contentUrl": "https://www.golfraw.com/public/scottie-scheffler-final-press-conference-answer-2026.webp",
        "width": 1200,
        "height": 675,
        "caption": "Scottie Scheffler at the media center press conference podium after winning the 2026 Tour Championship."
      },
      "author": {"@id": "https://www.golfraw.com/about#editorial"},
      "publisher": {"@id": "https://www.golfraw.com#organization"}
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://www.golfraw.com/news-2026-scottie-scheffler-final-press-conference-answer#breadcrumb",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.golfraw.com/"},
        {"@type": "ListItem", "position": 2, "name": "PGA Tour", "item": "https://www.golfraw.com/pga-tour"},
        {"@type": "ListItem", "position": 3, "name": "Scheffler Final Press Conference", "item": "https://www.golfraw.com/news-2026-scottie-scheffler-final-press-conference-answer"}
      ]
    },
    {"@type": "Person", "@id": "https://www.golfraw.com/about#editorial", "name": "GOLFRAW Editorial", "url": "https://www.golfraw.com/about"},
    {"@type": "Organization", "@id": "https://www.golfraw.com#organization", "name": "GOLFRAW", "url": "https://www.golfraw.com/"},
    {
      "@type": "FAQPage",
      "@id": "https://www.golfraw.com/news-2026-scottie-scheffler-final-press-conference-answer#faq",
      "mainEntity": [
        {"@type": "Question", "name": "What did Scottie Scheffler say in his final 2026 press conference?", "acceptedAnswer": {"@type": "Answer", "text": "Scheffler focused on the difficulty of the course conditions, his pride in fighting back from poor opening rounds throughout the year, and his excitement to travel home with his wife and two sons."}},
        {"@type": "Question", "name": "How much money did Scottie Scheffler make in 2026?", "acceptedAnswer": {"@type": "Answer", "text": "Scheffler earned over $30 million in official prize money during the 2026 season, elevating his career total past $130.39 million to become the highest-earning player in PGA Tour history."}}
      ]
    }
  ]
}
</script>"""

html = re.sub(r'<script type="application/ld\+json">.*?</script>', json_ld, html, flags=re.DOTALL)

with open('news-2026-scottie-scheffler-final-press-conference-answer.html', 'w') as f:
    f.write(html)
