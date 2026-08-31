import json, re

with open('news-2026-tour-championship-tee-times-round-4.html', 'r') as f:
    html = f.read()

# 1. Header & Metadata
title = "Scottie Scheffler's Swing: The Foot Slide Is a Symptom | GOLFRAW"
description = "Most of the famous foot slide happens after the ball has gone. What's actually producing 1.694 strokes gained tee to green is duller and copyable."
canonical_url = "https://www.golfraw.com/scottie-scheffler-swing-explained"
image_asset = "/public/scottie-scheffler-swing-explained.webp"

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
          <a href="/">RAWGOLF</a> / <a href="/guides">GUIDES</a> / <span>SCHEFFLER SWING EXPLAINED</span>
        </nav>"""
html = re.sub(r'<nav class="crumbs".*?</nav>', new_vis_bc, html, flags=re.DOTALL)

html = re.sub(r'<h1 class="headline">.*?</h1>', f'<h1 class="headline">Scottie Scheffler\'s Swing: The Foot Slide Is a Symptom</h1>', html, flags=re.DOTALL)
html = re.sub(r'<p class="standfirst">.*?</p>', f'<p class="standfirst">{description}</p>', html, flags=re.DOTALL)
html = re.sub(r'<span class="cat">.*?</span>', '<span class="cat">GUIDES · SWING MECHANICS</span>', html)

hero_html = """<figure class="lead-img">
       <img src="/public/scottie-scheffler-swing-explained.webp" alt="Scottie Scheffler demonstrating his dynamic golf swing follow-through with trail foot slide on the driving range." width="1200" height="675" style="aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:8px;">
     </figure>
     <figcaption>SCOTTIE SCHEFFLER'S TRADEMARK FOOT SLIDE OCCURS AFTER IMPACT AS A DIRECT REACTION TO ENORMOUS VERTICAL GROUND FORCES. PHOTO: RAWGOLF</figcaption>"""
html = re.sub(r'<figure class="lead-img">.*?</figcaption>\s*</figure>', hero_html, html, flags=re.DOTALL)
html = re.sub(r'<figure class="lead-img">.*?</figcaption>', hero_html, html, flags=re.DOTALL)
if '<figure class="lead-img">' in html and '<figcaption>' in html:
    html = re.sub(r'<figure class="lead-img">.*?</figure>\s*<figcaption>.*?</figcaption>', hero_html, html, flags=re.DOTALL)

new_body = """<div class="article-body">
          <div class="takeaways-box" style="background:#f4f4f4;padding:20px;margin-bottom:30px;border-left:4px solid var(--flag);">
            <h3>Key Takeaways</h3>
            <ul style="margin-top:10px;">
              <li><b>The Famous Slide is a Reaction:</b> Scheffler's chaotic footwork primarily happens after the ball has already been struck; it's a symptom, not the engine.</li>
              <li><b>Vertical Force Generation:</b> His swing is powered by immense vertical ground forces, utilizing the ground to create explosive rotation without sacrificing face control.</li>
              <li><b>Boring Fundamentals:</b> His daily practice routine focuses on grip, posture, and alignment sticks, building a bulletproof foundation before any technical swing mechanics.</li>
            </ul>
          </div>

          <h2>Scheffler's 2026 PGA Tour Dominance</h2>
          <div class="table-container" style="overflow-x:auto;">
            <table style="width:100%; border-collapse: collapse; font-family: 'IBM Plex Mono', monospace; font-size: 0.9rem;">
              <thead>
                <tr style="border-bottom: 2px solid var(--ink); text-align: left;">
                  <th style="padding: 10px 5px;">Metric</th>
                  <th style="padding: 10px 5px;">Performance</th>
                  <th style="padding: 10px 5px;">Tour Rank</th>
                </tr>
              </thead>
              <tbody>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">SG: Total</td><td style="padding: 10px 5px;">2.374</td><td style="padding: 10px 5px;">1st</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">SG: Tee-to-Green</td><td style="padding: 10px 5px;">1.694</td><td style="padding: 10px 5px;">1st</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">Greens in Regulation (GIR)</td><td style="padding: 10px 5px;">72.9%</td><td style="padding: 10px 5px;">1st</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">Scrambling</td><td style="padding: 10px 5px;">67.5%</td><td style="padding: 10px 5px;">1st</td>
                </tr>
                <tr style="border-bottom: 1px solid #ddd;">
                  <td style="padding: 10px 5px;">Scoring Average</td><td style="padding: 10px 5px;">67.9</td><td style="padding: 10px 5px;">1st</td>
                </tr>
                <tr>
                  <td style="padding: 10px 5px;">SG: Putting</td><td style="padding: 10px 5px;">+0.680</td><td style="padding: 10px 5px;">3rd</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h2>The Foot Slide Unpacked: A Body Release</h2>
          <p>Every amateur golfer who watches Scottie Scheffler asks the same question: "How does he hit it so well with that swing?" The fixation is always on his chaotic lower body, particularly the violent slip and slide of his trail foot during the follow-through.</p>
          <p>But the foot slide isn't what makes him the best ball striker on the planet. It is merely a symptom. The critical phase of the swing—from the start of the downswing through impact—is incredibly stable. The frantic movement of his feet occurs almost entirely after the ball has left the clubface. It's a "body release" mechanism, allowing his joints to safely absorb and dissipate the enormous rotational and vertical forces he generates.</p>

          <h2>The 3 Preceding Engine Moves</h2>
          <p>The real engine of Scheffler's swing operates much earlier in the sequence:</p>
          <ol>
            <li><b>Early Pressure Shift:</b> Scheffler begins moving pressure toward his lead target side before his backswing is even finished, creating a dynamic transition.</li>
            <li><b>Aggressive Torso and Hip Rotation:</b> He clears his hips exceptionally well, creating massive space for his arms to swing down on a neutral path.</li>
            <li><b>Vertical Ground Push:</b> This is the crucial factor. Scheffler pushes aggressively up from the ground, which unweights his trail foot (causing the slide) and lifts his lead heel. This vertical force translates directly into clubhead speed.</li>
          </ol>

          <h2>Why Amateurs Should NOT Copy the Footwork</h2>
          <p>If you're an amateur searching for more distance, deliberately sliding your right foot across the tee box is not the answer. Scheffler’s long-time coach, Randy Smith, has noted that whenever they attempted to quiet Scheffler's footwork, he lost significant distance and trajectory control. The slide works for him because his unique biomechanics demand it.</p>
          <p>Attempting to artificially manufacture the slide without producing the necessary ground forces will only lead to disastrous contact and potential injury. Prominent swing instructors like Jonathan Yarwood have explicitly warned that amateurs attempting to mimic Scheffler's extreme lateral shear forces run a high risk of severe ankle and knee injuries.</p>

          <h2>What Scheffler Actually Trains Daily</h2>
          <p>The most important takeaway for amateurs isn't Scheffler's follow-through; it's his preparation. What <a href="/news-2026-hovland-on-what-makes-scheffler-successful">makes him so relentlessly consistent</a> isn't an obscure biomechanical secret, but a monotonous dedication to fundamentals.</p>
          <p>Every single day, Scheffler and Randy Smith begin practice by obsessing over grip, posture, and alignment. Scheffler utilizes alignment sticks for almost every shot on the range. He builds a flawless, repeatable baseline setup before taking a single full swing. His elite ball striking is built on the most boring fundamentals in golf.</p>

          <h2>Fact-Checking 4 Common Swing Myths</h2>
          <ul>
            <li><i>Myth 1: Scheffler hits it well despite his swing.</i> False. He hits it well because his swing sequence leading up to impact is biomechanically optimal.</li>
            <li><i>Myth 2: Amateurs should try to slide their foot like Scottie.</i> False. Attempting to copy the slide without the necessary vertical force is detrimental and dangerous.</li>
            <li><i>Myth 3: Scheffler's swing relies entirely on hand-eye coordination.</i> False. While his coordination is elite, his consistency is rooted in stable mechanics during the impact interval.</li>
            <li><i>Myth 4: You must have a textbook swing to win on Tour.</i> False. Function always supersedes aesthetics. The golf ball only cares about the clubface at impact, not how your feet look afterward.</li>
          </ul>

          <div class="verdict-box" style="margin-top: 30px; padding: 20px; background-color: #111; color: #fff; border-left: 4px solid var(--flag);">
            <h3 style="color: #fff;">The Raw Verdict</h3>
            <p>Ignore the chaotic footwork. The true genius of Scottie Scheffler's swing lies in his immaculate setup fundamentals and his ability to generate massive ground force while maintaining clubface control. It's a masterclass in function over form.</p>
          </div>
          
          <div class="faq-section" style="margin-top: 40px;">
            <h2>Frequently Asked Questions</h2>
            
            <h3 style="font-size:1.1rem; margin-top:20px;">Why does Scottie Scheffler slide his foot?</h3>
            <p>The foot slide is a biomechanical reaction to the massive vertical ground forces he generates during the downswing, allowing his body to release tension safely.</p>
            
            <h3 style="font-size:1.1rem; margin-top:20px;">Should I copy Scottie Scheffler's swing?</h3>
            <p>Amateurs should emulate his perfect setup, grip, and posture, but attempting to artificially copy his foot slide can lead to poor contact and injury.</p>
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
          <a class="rel-card" href="/news-2026-hovland-on-what-makes-scheffler-successful">
            <div class="cat">PGA TOUR</div>
            <h3>Hovland on What Makes Scheffler Successful, in 8 Words</h3>
            <div class="d">MON 31 AUG · GOLFRAW</div>
          </a>
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
      "@type": "Article",
      "@id": "https://www.golfraw.com/scottie-scheffler-swing-explained#article",
      "headline": "Scottie Scheffler's Swing: The Foot Slide Is a Symptom | GOLFRAW",
      "name": "Scottie Scheffler's Swing: The Foot Slide Is a Symptom | GOLFRAW",
      "description": "Most of the famous foot slide happens after the ball has gone. What's actually producing 1.694 strokes gained tee to green is duller and copyable.",
      "articleSection": "Guides",
      "keywords": "Scottie Scheffler, Swing Analysis, Golf Mechanics, PGA Tour, Foot Slide",
      "datePublished": "2026-08-31T17:00:00+02:00",
      "dateModified": "2026-08-31T17:00:00+02:00",
      "inLanguage": "en",
      "image": {
        "@type": "ImageObject",
        "url": "https://www.golfraw.com/public/scottie-scheffler-swing-explained.webp",
        "contentUrl": "https://www.golfraw.com/public/scottie-scheffler-swing-explained.webp",
        "width": 1200,
        "height": 675,
        "caption": "Scottie Scheffler demonstrating his dynamic golf swing follow-through with trail foot slide on the driving range."
      },
      "author": {"@id": "https://www.golfraw.com/about#editorial"},
      "publisher": {"@id": "https://www.golfraw.com#organization"},
      "about": [
        {"@type": "Person", "name": "Scottie Scheffler"}
      ]
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://www.golfraw.com/scottie-scheffler-swing-explained#breadcrumb",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.golfraw.com/"},
        {"@type": "ListItem", "position": 2, "name": "Guides", "item": "https://www.golfraw.com/guides"},
        {"@type": "ListItem", "position": 3, "name": "Scheffler Swing Explained", "item": "https://www.golfraw.com/scottie-scheffler-swing-explained"}
      ]
    },
    {"@type": "Person", "@id": "https://www.golfraw.com/about#editorial", "name": "GOLFRAW Editorial", "url": "https://www.golfraw.com/about"},
    {"@type": "Organization", "@id": "https://www.golfraw.com#organization", "name": "GOLFRAW", "url": "https://www.golfraw.com/"},
    {
      "@type": "FAQPage",
      "@id": "https://www.golfraw.com/scottie-scheffler-swing-explained#faq",
      "mainEntity": [
        {"@type": "Question", "name": "Why does Scottie Scheffler slide his foot?", "acceptedAnswer": {"@type": "Answer", "text": "The foot slide is a biomechanical reaction to the massive vertical ground forces he generates during the downswing, allowing his body to release tension safely."}},
        {"@type": "Question", "name": "Should I copy Scottie Scheffler's swing?", "acceptedAnswer": {"@type": "Answer", "text": "Amateurs should emulate his perfect setup, grip, and posture, but attempting to artificially copy his foot slide can lead to poor contact and injury."}}
      ]
    }
  ]
}
</script>"""

html = re.sub(r'<script type="application/ld\+json">.*?</script>', json_ld, html, flags=re.DOTALL)

with open('scottie-scheffler-swing-explained.html', 'w') as f:
    f.write(html)
