import json, re

with open('article-template.html', 'r') as f:
    html = f.read()

# 1. Header & Metadata
title = "Michael Block's 2-Shot Lead at the Ally Challenge Explained | GOLFRAW"
description = "He eagled the first, made five birdies, dropped nothing, and leads by two. But the number he's actually chasing isn't first place. Here's what it is."
canonical_url = "https://www.golfraw.com/news-2026-michael-block-lead-ally-challenge"
image_asset = "/public/michael-block-lead-ally-challenge-2026.webp"

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
          <img src="/public/michael-block-lead-ally-challenge-2026.webp" alt="Michael Block playing his approach shot during his bogey-free 65 at the 2026 Ally Challenge at Warwick Hills." width="1200" height="675" style="aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:8px;">
          <figcaption>MICHAEL BLOCK HOLDS A TWO-SHOT LEAD AT WARWICK HILLS AFTER A BOGEY-FREE 65, CHASING A CRUCIAL TOP-10 FINISH FOR PLAYOFF ELIGIBILITY. PHOTO: RAWGOLF</figcaption>
        </figure>
"""
if '<figure class="lead-img">' in html:
    html = re.sub(r'<figure class="lead-img">.*?</figure>', hero_html, html, flags=re.DOTALL)
else:
    html = html.replace('</header>', '</header>\n' + hero_html)

new_vis_bc = """<nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/news">News</a> / <a href="/tournaments">Tournaments</a> / <span>Michael Block Ally Challenge Lead</span>
        </nav>"""
html = re.sub(r'<nav class="crumbs".*?</nav>', new_vis_bc, html, flags=re.DOTALL)

html = re.sub(r'<h1 class="headline">.*?</h1>', '<h1 class="headline">Michael Block\'s 2-Shot Lead at the Ally Challenge Explained</h1>', html, flags=re.DOTALL)
html = re.sub(r'<h2 class="subhead">.*?</h2>', '<h2 class="subhead">He eagled the first, made five birdies, dropped nothing, and leads by two. But the number he\'s actually chasing isn\'t first place. Here\'s what it is.</h2>', html, flags=re.DOTALL)

new_body = """<div class="article-body">
          <div class="takeaways">
            <h3 style="margin-top:0;">Key Takeaways</h3>
            <ul>
              <li><b>Michael Block (-13)</b> fired a bogey-free 65 to take a two-shot lead heading into Sunday at Warwick Hills.</li>
              <li><b>The True Incentive:</b> A top-10 finish is the priority. It secures an exemption into the Sanford International, completing his 7th start to qualify for the Charles Schwab Cup playoffs.</li>
              <li><b>Steven Alker (-11)</b> matched the 65 and sits two shots back, fresh off a recent victory.</li>
              <li><b>Rules Warning:</b> Caddie alignment penalties (Rule 10.2b(4)) are a persistent threat, especially with Block having his son Ethan on the bag.</li>
            </ul>
          </div>

          <h2>Ally Challenge Round 2 Leaderboard</h2>
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>Player</th>
                  <th>Total</th>
                  <th>Round 2 Score</th>
                </tr>
              </thead>
              <tbody>
                <tr><td>Michael Block</td><td>-13</td><td>65</td></tr>
                <tr><td>Steven Alker</td><td>-11</td><td>65</td></tr>
                <tr><td>Padraig Harrington</td><td>-10</td><td>69</td></tr>
                <tr><td>Ricardo Gonzalez</td><td>-9</td><td>68</td></tr>
                <tr><td>Vaughn Taylor</td><td>-9</td><td>67</td></tr>
                <tr><td>Thongchai Jaidee</td><td>-8</td><td>69</td></tr>
                <tr><td>Angel Cabrera</td><td>-8</td><td>68</td></tr>
                <tr><td>Michael Campbell</td><td>-8</td><td>70</td></tr>
                <tr><td>Greg Chalmers</td><td>-8</td><td>66</td></tr>
              </tbody>
            </table>
          </div>

          <h2>The Saturday Bogey-Free Masterclass</h2>
          <p>Michael Block set the tone immediately on Saturday, dropping an eagle on the 563-yard par-5 1st hole. From there, it was a clinic in course management. He added five birdies and surrendered zero bogeys, carding a 65 to reach 13 under par. His iron play was dialled in, reminiscent of the form that made him a viral sensation.</p>

          <h2>The Top-10 Chain Reaction (The True Incentive)</h2>
          <p>While winning the $330,000 first-place prize is the obvious goal, Block is playing for a much more complex math equation. He is currently chasing the "Top-10 Chain Reaction" for playoff eligibility.</p>
          <p>If Block finishes in the top 10 on Sunday, he earns an automatic exemption into the upcoming Sanford International. Playing the Sanford International would mark his 7th start of the season. Hitting the 7-start threshold is the mandatory requirement for players to be officially listed on the Charles Schwab Cup money list. If he gets on that list, he qualifies for the playoffs—which conveniently includes a hometown event at Norwood Hills in St. Louis. For Block, Sunday is about survival just as much as it is about a trophy.</p>

          <h2>The Chasing Pack and Purses</h2>
          <p>Steven Alker, one of the most dominant forces on the Champions Tour, is breathing down Block's neck. Alker matched Block's bogey-free 65 and sits at 11 under. Just behind them is Padraig Harrington at 10 under, followed by a congested pack of 10 players within five shots of the lead. The field is competing for a $2.2 million purse.</p>

          <h2>Course Yardage Clarification</h2>
          <p>Earlier in the week, multiple outlets erroneously reported Warwick Hills as playing to 7,112 yards. The official setup, confirmed by ESPN and AP, is a par 72 playing at 7,085 yards. The slightly shorter yardage favors precise iron players like Block over pure bombers.</p>

          <h2>Rules Audit: Rule 10.2b(4)</h2>
          <p>With his son Ethan on the bag, Block must be hyper-vigilant regarding Rule 10.2b(4) (Caddies lining up players behind the ball). The rule stipulates a two-shot penalty if a caddie stands in the restricted area on the extension of the line of play behind the player once the player begins taking a stance. We've seen this penalty casually ruin rounds on the Champions Tour, and familial comfort on the bag can sometimes lead to relaxed positioning.</p>

          <h2>Debunking 4 Media Misconceptions</h2>
          <ul>
            <li><i>Myth 1: Block is only here on a sponsor exemption.</i> False. He earned his way into this field via his recent strong play and qualifying categories.</li>
            <li><i>Myth 2: First place is the only thing that matters.</i> False. A top-10 finish is arguably just as valuable for his long-term playoff status. (If you're curious about <a href="/how-long-do-golf-tournaments-last">how long tournament grinds like this last</a>, they test endurance as much as skill).</li>
            <li><i>Myth 3: Warwick Hills is a bomber's paradise.</i> False. At 7,085 yards, it's a second-shot golf course that rewards precision, perfectly suiting Block's game.</li>
            <li><i>Myth 4: The Champions Tour lacks depth.</i> False. Look at the leaderboard: Harrington, Cabrera, Campbell. Major champions are lurking everywhere.</li>
          </ul>

          <div class="verdict-box">
            <h3>The Raw Verdict</h3>
            <p>Block has the game to win, but the pressure of the Top-10 exemption might cause him to play conservatively if Alker makes an early charge. If Block is tied for the lead on the 15th tee, he plays for the win. If he's two shots back, expect him to protect his top-10 status at all costs.</p>
          </div>
          
          <section class="sources" aria-labelledby="faq-label">
            <h2 id="faq-label" style="font-size: 1.25rem; font-family: 'IBM Plex Mono', monospace; text-transform: uppercase;">FAQ</h2>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">Why does Michael Block need a top-10 finish at the Ally Challenge?</h3>
              <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">A top-10 finish earns him an exemption into the Sanford International, which would be his 7th start of the season. 7 starts are required to officially qualify for the Charles Schwab Cup playoffs.</p>
              </div>
            </div>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">What did Michael Block shoot in the second round of the Ally Challenge?</h3>
              <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">Michael Block shot a bogey-free 65, including an eagle on the 1st hole and five birdies.</p>
              </div>
            </div>
          </section>

          <section class="sources" aria-labelledby="sources-label">
            <p class="section-label" id="sources-label">Sources</p>
            <ol>
              <li><a href="/news">GOLFRAW: Latest News</a>. The live reporting index for current tournament updates.</li>
              <li><a href="/tournaments">GOLFRAW: Tournament coverage</a>. Historical context and current leaderboards.</li>
              <li><a href="/how-long-do-golf-tournaments-last">How Long Do Golf Tournaments Last?</a> Understanding the weekend grind.</li>
            </ol>
          </section>

          <div class="provenance">
            <p><strong>Article history.</strong> Published <time datetime="2026-08-30T15:30:00+02:00">30 August 2026 at 15:30 CEST</time>.</p>
            <p><strong>Corrections.</strong> None at publication. <a href="/corrections">Corrections policy</a>.</p>
            <p><strong>Last updated.</strong> <time datetime="2026-08-30T15:30:00+02:00">30 August 2026 at 15:30 CEST</time>.</p>
          </div>

          <aside class="related" aria-label="Related GolfRaw reporting">
            <p class="section-label" style="color:#b8d2c5">Keep reading</p>
            <ul>
              <li><a href="/news-2026-tour-championship-tee-times-round-4">Tour Championship Sunday Tee Times</a></li>
              <li><a href="/how-long-do-golf-tournaments-last">Tournament Formats Guide</a></li>
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
      "@id": "https://www.golfraw.com/news-2026-michael-block-lead-ally-challenge#article",
      "headline": "Michael Block's 2-Shot Lead at the Ally Challenge Explained | GOLFRAW",
      "name": "Michael Block's 2-Shot Lead at the Ally Challenge Explained | GOLFRAW",
      "description": "He eagled the first, made five birdies, dropped nothing, and leads by two. But the number he's actually chasing isn't first place. Here's what it is.",
      "articleSection": "Tournaments",
      "keywords": "Michael Block, Ally Challenge, Champions Tour, Warwick Hills, Steven Alker, Charles Schwab Cup",
      "datePublished": "2026-08-30T15:30:00+02:00",
      "dateModified": "2026-08-30T15:30:00+02:00",
      "inLanguage": "en",
      "image": {
        "@type": "ImageObject",
        "url": "https://www.golfraw.com/public/michael-block-lead-ally-challenge-2026.webp",
        "contentUrl": "https://www.golfraw.com/public/michael-block-lead-ally-challenge-2026.webp",
        "width": 1200,
        "height": 675,
        "caption": "Michael Block playing his approach shot during his bogey-free 65 at the 2026 Ally Challenge at Warwick Hills."
      },
      "author": {"@id": "https://www.golfraw.com/about#editorial"},
      "publisher": {"@id": "https://www.golfraw.com#organization"},
      "about": [
        {"@type": "Thing", "name": "Ally Challenge"},
        {"@type": "Thing", "name": "Michael Block"}
      ]
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://www.golfraw.com/news-2026-michael-block-lead-ally-challenge#breadcrumb",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.golfraw.com/"},
        {"@type": "ListItem", "position": 2, "name": "News", "item": "https://www.golfraw.com/news"},
        {"@type": "ListItem", "position": 3, "name": "Michael Block Ally Challenge Lead", "item": "https://www.golfraw.com/news-2026-michael-block-lead-ally-challenge"}
      ]
    },
    {"@type": "Person", "@id": "https://www.golfraw.com/about#editorial", "name": "GOLFRAW Editorial", "url": "https://www.golfraw.com/about"},
    {"@type": "Organization", "@id": "https://www.golfraw.com#organization", "name": "GOLFRAW", "url": "https://www.golfraw.com/"},
    {
      "@type": "FAQPage",
      "@id": "https://www.golfraw.com/news-2026-michael-block-lead-ally-challenge#faq",
      "mainEntity": [
        {"@type": "Question", "name": "Why does Michael Block need a top-10 finish at the Ally Challenge?", "acceptedAnswer": {"@type": "Answer", "text": "A top-10 finish earns him an exemption into the Sanford International, which would be his 7th start of the season. 7 starts are required to officially qualify for the Charles Schwab Cup playoffs."}},
        {"@type": "Question", "name": "What did Michael Block shoot in the second round of the Ally Challenge?", "acceptedAnswer": {"@type": "Answer", "text": "Michael Block shot a bogey-free 65, including an eagle on the 1st hole and five birdies."}}
      ]
    }
  ]
}
</script>"""

if '<script type="application/ld+json">' in html:
    html = re.sub(r'<script type="application/ld\+json">.*?</script>', json_ld, html, flags=re.DOTALL)
else:
    html = html.replace('</head>', json_ld + '\n</head>')

with open('news-2026-michael-block-lead-ally-challenge.html', 'w') as f:
    f.write(html)
