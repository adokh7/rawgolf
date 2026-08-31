import json, re

with open('news-2026-tour-championship-tee-times-round-4.html', 'r') as f:
    html = f.read()

# 1. Header & Metadata
title = "Hovland on What Makes Scheffler Successful, in 8 Words | GOLFRAW"
description = "Asked if Scheffler amazes him, the man he'd just lost to said no. His actual explanation is duller and far more useful than any mental-game theory."
canonical_url = "https://www.golfraw.com/news-2026-hovland-on-what-makes-scheffler-successful"
image_asset = "/public/hovland-on-what-makes-scheffler-successful-2026.webp"

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
          <a href="/">RAWGOLF</a> / <a href="/pga-tour">PGA TOUR</a> / <span>HOVLAND ON SCHEFFLER</span>
        </nav>"""
html = re.sub(r'<nav class="crumbs".*?</nav>', new_vis_bc, html, flags=re.DOTALL)

html = re.sub(r'<h1 class="headline">.*?</h1>', f'<h1 class="headline">Hovland on What Makes Scheffler Successful, in 8 Words</h1>', html, flags=re.DOTALL)
html = re.sub(r'<p class="standfirst">.*?</p>', f'<p class="standfirst">{description}</p>', html, flags=re.DOTALL)

hero_html = """<figure class="lead-img">
       <img src="/public/hovland-on-what-makes-scheffler-successful-2026.webp" alt="Viktor Hovland speaking to media after finishing solo second to Scottie Scheffler at the 2026 Tour Championship at East Lake." width="1200" height="675" style="aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:8px;">
     </figure>
     <figcaption>VIKTOR HOVLAND OFFERED A REFRESHINGLY CANDID ASSESSMENT OF SCOTTIE SCHEFFLER'S DOMINANCE AFTER FINISHING RUNNER-UP AT EAST LAKE. PHOTO: RAWGOLF</figcaption>"""
html = re.sub(r'<figure class="lead-img">.*?</figcaption>\s*</figure>', hero_html, html, flags=re.DOTALL)
html = re.sub(r'<figure class="lead-img">.*?</figcaption>', hero_html, html, flags=re.DOTALL)
if '<figure class="lead-img">' in html and '<figcaption>' in html:
    html = re.sub(r'<figure class="lead-img">.*?</figure>\s*<figcaption>.*?</figcaption>', hero_html, html, flags=re.DOTALL)

new_body = """<div class="article-body">
          <div class="takeaways-box" style="background:#f4f4f4;padding:20px;margin-bottom:30px;border-left:4px solid var(--flag);">
            <h3>Key Takeaways</h3>
            <ul style="margin-top:10px;">
              <li><b>The Quote:</b> Asked to explain Scheffler's dominance, Viktor Hovland summarized it simply: "He's just good, and he played good every day."</li>
              <li><b>Physical over Mental:</b> Hovland dismissed abstract mental-game theories, pointing directly to ball flight predictability and avoiding two-way misses.</li>
              <li><b>The Leaderboard Check:</b> Contrary to the "unbothered" narrative, Scheffler constantly monitors leaderboards to dictate his aggression, a tactic confirmed by Jack Nicklaus.</li>
            </ul>
          </div>

          <h2>Scheffler's 2026 Season Dominance Summary</h2>
          <div class="table-container" style="overflow-x:auto;">
            <table style="width:100%; border-collapse: collapse; font-family: 'IBM Plex Mono', monospace; font-size: 0.9rem;">
              <thead>
                <tr style="border-bottom: 2px solid var(--ink); text-align: left;">
                  <th style="padding: 10px 5px;">Metric</th>
                  <th style="padding: 10px 5px;">Result</th>
                  <th style="padding: 10px 5px;">Notable Events</th>
                </tr>
              </thead>
              <tbody>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">Wins</td><td style="padding: 10px 5px;">3</td><td style="padding: 10px 5px;">Tour Championship (FedExCup)</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">Runner-Ups</td><td style="padding: 10px 5px;">5</td><td style="padding: 10px 5px;">Two occurred during FedExCup Playoffs</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">Thirds</td><td style="padding: 10px 5px;">2</td><td style="padding: 10px 5px;">-</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">Fourths</td><td style="padding: 10px 5px;">3</td><td style="padding: 10px 5px;">-</td>
                </tr>
                <tr>
                  <td style="padding: 10px 5px;">Earnings</td><td style="padding: 10px 5px;">$30M+ (2026)</td><td style="padding: 10px 5px;">$130.39M Career (All-time Record)</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h2>"He's Just Good"</h2>
          <p>When you finish a brutal 72 holes trailing the best player on the planet by three shots, the media expects poetry. They want psychological breakdowns. They want to know what invisible aura Scottie Scheffler carries inside the ropes. Viktor Hovland, standing outside the East Lake clubhouse after collecting $5 million for second place, opted for blunt force trauma instead.</p>
          <p>Asked if Scheffler's relentless consistency amazed him, Hovland didn't hesitate: "No. He's just good, and he played good every day."</p>
          <p>It sounds dismissive. It isn't. Hovland’s eight-word answer cuts through the bloated sports psychology industry to state the fundamental truth of professional golf: Scheffler plays with the profound, freeing knowledge that his baseline is simply higher than everyone else's.</p>

          <h2>Rejecting the Mental Game Narrative</h2>
          <p>Golf media loves to diagnose missed cuts as "mental blocks" and attribute dominant runs to "superior focus." Hovland's assessment rejects this entirely. When a player is struggling, it is rarely because they aren't trying hard enough or lack psychological fortitude. It is almost always a physical reality: a two-way miss.</p>
          <p>If you don't know whether your driver is going to over-cut into the right rough or double-cross into the left trees, no amount of deep breathing will save your scorecard. Scheffler's "mental toughness" is actually a byproduct of physical predictability. He knows exactly where the clubface is, and more importantly, he knows exactly which way the ball is going to curve before he even starts the downswing.</p>

          <h2>Scheffler's Leaderboard Reality</h2>
          <p>One of the most pervasive myths surrounding Scheffler is that he operates in a bubble, oblivious to the tournament around him. The reality is the exact opposite. Scheffler is an aggressive leaderboard watcher.</p>
          <p>Jack Nicklaus famously revealed in 2025 that Scheffler constantly tracks the board. He uses that data to dictate his strategy. You don't try to force a birdie on the 18th hole at East Lake unless you know exactly how many strokes you can afford to lose. Scheffler isn't blindly swinging free; he is operating with ruthless, calculated awareness of the mathematics.</p>

          <h2>Debunking 4 Common Myths</h2>
          <ul>
            <li><i>Myth 1: Scheffler ignores the leaderboard to stay calm.</i> False. He actively monitors it to dictate his course management and risk tolerance.</li>
            <li><i>Myth 2: Hovland lost because he cracked under pressure.</i> False. Hovland shot a bogey-free back nine; he simply ran out of holes to catch a player who made zero mistakes.</li>
            <li><i>Myth 3: Scheffler's swing speed is his biggest advantage.</i> False. While fast, his true edge is ball flight predictability and face control.</li>
            <li><i>Myth 4: The mental game is more important than mechanics.</i> False. As Hovland pointed out, elite mechanics and predictable misses build the foundation for a strong mental game.</li>
          </ul>

          <div class="verdict-box" style="margin-top: 30px; padding: 20px; background-color: #111; color: #fff; border-left: 4px solid var(--flag);">
            <h3 style="color: #fff;">The Raw Verdict</h3>
            <p>We want greatness to be complicated so we can sell books about it. Hovland's brutal honesty reminds us that sometimes, the secret to dominating the PGA Tour is exactly what it looks like: hitting the center of the clubface with an open or shut face intentionally, over and over again, until everyone else breaks.</p>
          </div>
          
          <div class="faq-section" style="margin-top: 40px;">
            <h2>Frequently Asked Questions</h2>
            
            <h3 style="font-size:1.1rem; margin-top:20px;">What did Viktor Hovland say about Scottie Scheffler?</h3>
            <p>When asked if Scheffler's play amazed him, Hovland responded, "No. He's just good, and he played good every day."</p>
            
            <h3 style="font-size:1.1rem; margin-top:20px;">Does Scottie Scheffler look at the leaderboard?</h3>
            <p>Yes. Despite his calm demeanor, Scheffler frequently checks the leaderboard to manage his strategy, a fact confirmed by Jack Nicklaus.</p>
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
          <a class="rel-card" href="/news-2026-tour-championship-points-and-payouts">
            <div class="cat">TOURNAMENTS</div>
            <h3>Tour Championship Points and Payouts: All 29 Checks</h3>
            <div class="d">MON 31 AUG · GOLFRAW</div>
          </a>
          <a class="rel-card" href="/news-2026-tiger-woods-career-money-list-record">
            <div class="cat">PGA TOUR</div>
            <h3>The Fall of Tiger's Money Record</h3>
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
      "@id": "https://www.golfraw.com/news-2026-hovland-on-what-makes-scheffler-successful#article",
      "headline": "Hovland on What Makes Scheffler Successful, in 8 Words | GOLFRAW",
      "name": "Hovland on What Makes Scheffler Successful, in 8 Words | GOLFRAW",
      "description": "Asked if Scheffler amazes him, the man he'd just lost to said no. His actual explanation is duller and far more useful than any mental-game theory.",
      "articleSection": "Tournaments",
      "keywords": "Viktor Hovland, Scottie Scheffler, Tour Championship, Golf Mental Game, PGA Tour",
      "datePublished": "2026-08-31T17:00:00+02:00",
      "dateModified": "2026-08-31T17:00:00+02:00",
      "inLanguage": "en",
      "image": {
        "@type": "ImageObject",
        "url": "https://www.golfraw.com/public/hovland-on-what-makes-scheffler-successful-2026.webp",
        "contentUrl": "https://www.golfraw.com/public/hovland-on-what-makes-scheffler-successful-2026.webp",
        "width": 1200,
        "height": 675,
        "caption": "Viktor Hovland speaking to media after finishing solo second to Scottie Scheffler at the 2026 Tour Championship at East Lake."
      },
      "author": {"@id": "https://www.golfraw.com/about#editorial"},
      "publisher": {"@id": "https://www.golfraw.com#organization"},
      "about": [
        {"@type": "Person", "name": "Viktor Hovland"},
        {"@type": "Person", "name": "Scottie Scheffler"}
      ]
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://www.golfraw.com/news-2026-hovland-on-what-makes-scheffler-successful#breadcrumb",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.golfraw.com/"},
        {"@type": "ListItem", "position": 2, "name": "PGA Tour", "item": "https://www.golfraw.com/pga-tour"},
        {"@type": "ListItem", "position": 3, "name": "Hovland on Scheffler's Success", "item": "https://www.golfraw.com/news-2026-hovland-on-what-makes-scheffler-successful"}
      ]
    },
    {"@type": "Person", "@id": "https://www.golfraw.com/about#editorial", "name": "GOLFRAW Editorial", "url": "https://www.golfraw.com/about"},
    {"@type": "Organization", "@id": "https://www.golfraw.com#organization", "name": "GOLFRAW", "url": "https://www.golfraw.com/"},
    {
      "@type": "FAQPage",
      "@id": "https://www.golfraw.com/news-2026-hovland-on-what-makes-scheffler-successful#faq",
      "mainEntity": [
        {"@type": "Question", "name": "What did Viktor Hovland say about Scottie Scheffler?", "acceptedAnswer": {"@type": "Answer", "text": "When asked if Scheffler's play amazed him, Hovland responded, 'No. He's just good, and he played good every day.'"}},
        {"@type": "Question", "name": "Does Scottie Scheffler look at the leaderboard?", "acceptedAnswer": {"@type": "Answer", "text": "Yes. Despite his calm demeanor, Scheffler frequently checks the leaderboard to manage his strategy, a fact confirmed by Jack Nicklaus."}}
      ]
    }
  ]
}
</script>"""

html = re.sub(r'<script type="application/ld\+json">.*?</script>', json_ld, html, flags=re.DOTALL)

with open('news-2026-hovland-on-what-makes-scheffler-successful.html', 'w') as f:
    f.write(html)
