import json, re

with open('article-template.html', 'r') as f:
    html = f.read()

# 1. Header & Metadata
title = "PGA Tour Winners 2026: 28 Names, 35 Events, One Left | GOLFRAW"
description = "Every winner from the Sony Open to the BMW, the three men who won three times, and why the best player in the world isn't one of them."
canonical_url = "https://www.golfraw.com/news-2026-pga-tour-winners-2026"
image_asset = "/public/pga-tour-winners-2026-season-recap.webp"

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
          <img src="/public/pga-tour-winners-2026-season-recap.webp" alt="PGA Tour trophy presentation on the 18th green celebrating a 2026 tournament champion." width="1200" height="675" style="aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:8px;">
          <figcaption>TWENTY-EIGHT DIFFERENT PLAYERS CAPTURED PGA TOUR TITLES ACROSS 35 EVENTS IN 2026 HEADING INTO THE TOUR CHAMPIONSHIP FINALE. PHOTO: RAWGOLF</figcaption>
        </figure>
"""
if '<figure class="lead-img">' in html:
    html = re.sub(r'<figure class="lead-img">.*?</figure>', hero_html, html, flags=re.DOTALL)
else:
    html = html.replace('</header>', '</header>\n' + hero_html)

# Breadcrumbs targeting "PGA Tour" specifically as requested
new_vis_bc = """<nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/pga-tour">PGA Tour</a> / <span>PGA Tour Winners 2026</span>
        </nav>"""
html = re.sub(r'<nav class="crumbs".*?</nav>', new_vis_bc, html, flags=re.DOTALL)

html = re.sub(r'<h1 class="headline">.*?</h1>', '<h1 class="headline">PGA Tour Winners 2026: 28 Names, 35 Events, One Left</h1>', html, flags=re.DOTALL)
html = re.sub(r'<h2 class="subhead">.*?</h2>', '<h2 class="subhead">Every winner from the Sony Open to the BMW, the three men who won three times, and why the best player in the world isn\'t one of them.</h2>', html, flags=re.DOTALL)

new_body = """<div class="article-body">
          <div class="takeaways">
            <h3 style="margin-top:0;">Key Takeaways</h3>
            <ul>
              <li><b>The Three-Win Club:</b> Wyndham Clark, Chris Gotterup, and Matt Fitzpatrick lead the Tour with three victories each.</li>
              <li><b>Scottie Scheffler's Paradox:</b> The World No. 1 has only two wins (zero majors) but enters East Lake atop the FedExCup standings for the fifth straight year.</li>
              <li><b>Major Shocks:</b> Aaron Rai captured the PGA Championship at Aronimink, highlighting a historic year for first-time major winners.</li>
              <li><b>New Blood:</b> Rising stars like Jacob Bridgeman (Riviera), Jackson Koivun, and Michael Thorbjornsen all secured breakthrough titles.</li>
              <li><b>Schedule Upheaval:</b> The Sentry at Kapalua was canceled, and Doral returned with the Cadillac Championship.</li>
            </ul>
          </div>

          <h2>The Complete 2026 PGA Tour Winners & Purses</h2>
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Tournament</th>
                  <th>Winner</th>
                  <th>Purse</th>
                </tr>
              </thead>
              <tbody>
                <tr><td>Jan 8-11</td><td>Sony Open in Hawaii</td><td>Chris Gotterup</td><td>$8.3M</td></tr>
                <tr><td>Jan 15-18</td><td>The American Express</td><td>Scottie Scheffler</td><td>$8.4M</td></tr>
                <tr><td>Jan 22-25</td><td>Farmers Insurance Open</td><td>Sahith Theegala</td><td>$9.0M</td></tr>
                <tr><td>Jan 29-Feb 1</td><td>AT&T Pebble Beach Pro-Am</td><td>Wyndham Clark</td><td>$20.0M</td></tr>
                <tr><td>Feb 5-8</td><td>WM Phoenix Open</td><td>Tom Kim</td><td>$8.8M</td></tr>
                <tr><td>Feb 12-15</td><td>The Genesis Invitational</td><td>Jacob Bridgeman</td><td>$20.0M</td></tr>
                <tr><td>Feb 19-22</td><td>Mexico Open at Vidanta</td><td>Michael Thorbjornsen</td><td>$8.1M</td></tr>
                <tr><td>Feb 26-Mar 1</td><td>The Cognizant Classic</td><td>Matt Fitzpatrick</td><td>$9.0M</td></tr>
                <tr><td>Mar 5-8</td><td>Cadillac Championship at Doral</td><td>Xander Schauffele</td><td>$20.0M</td></tr>
                <tr><td>Mar 12-15</td><td>THE PLAYERS Championship</td><td>Chris Gotterup</td><td>$25.0M</td></tr>
                <tr><td>Mar 19-22</td><td>Valspar Championship</td><td>Stefano Mazzoli</td><td>$8.4M</td></tr>
                <tr><td>Mar 26-29</td><td>Texas Children's Houston Open</td><td>Steven Fisk</td><td>$9.1M</td></tr>
                <tr><td>Apr 2-5</td><td>Valero Texas Open</td><td>Cameron Young</td><td>$9.2M</td></tr>
                <tr><td>Apr 9-12</td><td>Masters Tournament</td><td>Hideki Matsuyama</td><td>$20.0M</td></tr>
                <tr><td>Apr 16-19</td><td>RBC Heritage</td><td>Collin Morikawa</td><td>$20.0M</td></tr>
                <tr><td>Apr 23-26</td><td>Zurich Classic of New Orleans</td><td>Matt Fitzpatrick & Alex Fitzpatrick</td><td>$8.9M</td></tr>
                <tr><td>Apr 30-May 3</td><td>CJ CUP Byron Nelson</td><td>Michael Brennan</td><td>$9.5M</td></tr>
                <tr><td>May 7-10</td><td>Wells Fargo Championship</td><td>Kristoffer Reitan</td><td>$20.0M</td></tr>
                <tr><td>May 14-17</td><td>PGA Championship (Aronimink)</td><td>Aaron Rai</td><td>$18.5M</td></tr>
                <tr><td>May 21-24</td><td>Charles Schwab Challenge</td><td>Wyndham Clark</td><td>$8.7M</td></tr>
                <tr><td>May 28-31</td><td>RBC Canadian Open</td><td>Nick Taylor</td><td>$9.4M</td></tr>
                <tr><td>Jun 4-7</td><td>the Memorial Tournament</td><td>Viktor Hovland</td><td>$20.0M</td></tr>
                <tr><td>Jun 11-14</td><td>U.S. Open (Oakmont)</td><td>Patrick Cantlay</td><td>$21.5M</td></tr>
                <tr><td>Jun 18-21</td><td>Travelers Championship</td><td>Matt Fitzpatrick</td><td>$20.0M</td></tr>
                <tr><td>Jun 25-28</td><td>Rocket Mortgage Classic</td><td>Jackson Koivun</td><td>$8.8M</td></tr>
                <tr><td>Jul 2-5</td><td>John Deere Classic</td><td>Adam Scott</td><td>$8.0M</td></tr>
                <tr><td>Jul 9-12</td><td>Genesis Scottish Open</td><td>Tommy Fleetwood</td><td>$9.0M</td></tr>
                <tr><td>Jul 16-19</td><td>The Open Championship</td><td>Ludvig Åberg</td><td>$17.0M</td></tr>
                <tr><td>Jul 23-26</td><td>3M Open</td><td>Cameron Davis</td><td>$8.1M</td></tr>
                <tr><td>Jul 30-Aug 2</td><td>Wyndham Championship</td><td>Chris Gotterup</td><td>$7.9M</td></tr>
                <tr><td>Aug 6-9</td><td>FedEx St. Jude Championship</td><td>Scottie Scheffler</td><td>$20.0M</td></tr>
                <tr><td>Aug 13-16</td><td>BMW Championship</td><td>Wyndham Clark</td><td>$20.0M</td></tr>
              </tbody>
            </table>
          </div>

          <h2>The Three-Win Leaders</h2>
          <p>Wyndham Clark and Chris Gotterup firmly established themselves as the apex predators of the 2026 regular season, each claiming three solo titles. Matt Fitzpatrick also joins the three-win club, though his tally comes with a slight asterisk: his victory alongside brother Alex at the Zurich Classic team event technically counts toward his total, complementing his wins at the Cognizant Classic and Travelers Championship.</p>

          <h2>The Scottie Scheffler Dynamic</h2>
          <p>For the fifth consecutive year, Scottie Scheffler enters East Lake as the FedExCup leader. Yet, surprisingly, he only secured two victories (The American Express and FedEx St. Jude) and was entirely shut out of the major championships. His dominance remains rooted in terrifyingly consistent top-5 finishes rather than outright trophies.</p>

          <h2>First-Time and Cinderella Champions</h2>
          <p>The 2026 season was defined by monumental breakthroughs. Aaron Rai secured his place in history with a shocking PGA Championship victory at Aronimink. Meanwhile, the Signature Events saw massive upsets, none bigger than Jacob Bridgeman conquering Riviera. We also witnessed breakthrough wins from Kristoffer Reitan at Quail Hollow, and a wave of new talent claiming regular events, including Steven Fisk, Stefano Mazzoli, Jackson Koivun, Michael Thorbjornsen, and Michael Brennan.</p>

          <h2>Schedule Shifts and Cancellations</h2>
          <p>The season started on a somber note with the cancellation of The Sentry at Kapalua, forced off the calendar due to severe drought and local water disputes in Maui. The PGA Tour filled the void later in the spring with the introduction of the Cadillac Championship, marking a highly anticipated return to Doral.</p>

          <h2>Fact-Checking 4 Misleading Season Narratives</h2>
          <ul>
            <li><i>Myth 1: Signature Events killed underdog stories.</i> False. Bridgeman winning Riviera and Reitan taking Quail Hollow proved that elite fields don't guarantee chalk winners.</li>
            <li><i>Myth 2: Scheffler had a down year.</i> False. Entering the Tour Championship at No. 1 for the fifth straight year is unprecedented consistency, even without a major.</li>
            <li><i>Myth 3: The youth movement stalled.</i> False. Koivun, Thorbjornsen, and Brennan winning in the same season marks the strongest arrival of college talent since the Class of 2011.</li>
            <li><i>Myth 4: Team golf is irrelevant.</i> False. The Fitzpatricks winning the Zurich Classic was one of the most widely watched broadcasts of the spring.</li>
          </ul>

          <div class="verdict-box">
            <h3>The Raw Verdict</h3>
            <p>The 2026 season delivered the perfect mix of superstar validation and fresh blood. While Gotterup and Clark stole the headlines with three wins, the emergence of a new generation like Koivun and Bridgeman ensures the Tour's pipeline is healthier than ever.</p>
          </div>
          
          <section class="sources" aria-labelledby="faq-label">
            <h2 id="faq-label" style="font-size: 1.25rem; font-family: 'IBM Plex Mono', monospace; text-transform: uppercase;">FAQ</h2>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">Who had the most wins on the PGA Tour in 2026?</h3>
              <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">Wyndham Clark, Chris Gotterup, and Matt Fitzpatrick led the PGA Tour with three wins each in the 2026 season prior to the Tour Championship.</p>
              </div>
            </div>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">Did Scottie Scheffler win a major in 2026?</h3>
              <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">No, despite entering the Tour Championship as the FedExCup leader for the fifth consecutive year, Scottie Scheffler did not win a major in 2026.</p>
              </div>
            </div>
          </section>

          <section class="sources" aria-labelledby="sources-label">
            <p class="section-label" id="sources-label">Sources</p>
            <ol>
              <li><a href="/pga-tour">GOLFRAW: PGA Tour Coverage</a>. Full season archives and statistics.</li>
              <li><a href="/news-2026-tour-championship-final-round-hovland-leads">Tour Championship Final Round Preview</a>. How the season concludes at East Lake.</li>
              <li><a href="/news-2026-tour-championship-tee-times-round-4">Sunday Tee Times</a>. Final round pairings for the 2026 finale.</li>
              <li><a href="/news-2026-cameron-young-new-putter-62-tour-championship">Cameron Young shoots 62</a>. A look at the Valero Texas Open winner's late-season form.</li>
            </ol>
          </section>

          <div class="provenance">
            <p><strong>Article history.</strong> Published <time datetime="2026-08-30T15:00:00+02:00">30 August 2026 at 15:00 CEST</time>.</p>
            <p><strong>Corrections.</strong> None at publication. <a href="/corrections">Corrections policy</a>.</p>
            <p><strong>Last updated.</strong> <time datetime="2026-08-30T15:00:00+02:00">30 August 2026 at 15:00 CEST</time>.</p>
          </div>

          <aside class="related" aria-label="Related GolfRaw reporting">
            <p class="section-label" style="color:#b8d2c5">Keep reading</p>
            <ul>
              <li><a href="/news-2026-tour-championship-final-round-hovland-leads">Tour Championship Final Round Preview</a></li>
              <li><a href="/news-2026-tour-championship-tee-times-round-4">Tour Championship Sunday Tee Times</a></li>
              <li><a href="/news-2026-cameron-young-new-putter-62-tour-championship">Cameron Young's 62 at East Lake</a></li>
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
      "@id": "https://www.golfraw.com/news-2026-pga-tour-winners-2026#article",
      "headline": "PGA Tour Winners 2026: 28 Names, 35 Events, One Left | GOLFRAW",
      "name": "PGA Tour Winners 2026: 28 Names, 35 Events, One Left | GOLFRAW",
      "description": "Every winner from the Sony Open to the BMW, the three men who won three times, and why the best player in the world isn't one of them.",
      "articleSection": "PGA Tour",
      "keywords": "PGA Tour Winners 2026, Chris Gotterup, Wyndham Clark, Scottie Scheffler, Aaron Rai, Tour Championship",
      "datePublished": "2026-08-30T15:00:00+02:00",
      "dateModified": "2026-08-30T15:00:00+02:00",
      "inLanguage": "en",
      "image": {
        "@type": "ImageObject",
        "url": "https://www.golfraw.com/public/pga-tour-winners-2026-season-recap.webp",
        "contentUrl": "https://www.golfraw.com/public/pga-tour-winners-2026-season-recap.webp",
        "width": 1200,
        "height": 675,
        "caption": "PGA Tour trophy presentation on the 18th green celebrating a 2026 tournament champion."
      },
      "author": {"@id": "https://www.golfraw.com/about#editorial"},
      "publisher": {"@id": "https://www.golfraw.com#organization"},
      "about": [
        {"@type": "Thing", "name": "PGA Tour"},
        {"@type": "Thing", "name": "Scottie Scheffler"}
      ]
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://www.golfraw.com/news-2026-pga-tour-winners-2026#breadcrumb",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.golfraw.com/"},
        {"@type": "ListItem", "position": 2, "name": "PGA Tour", "item": "https://www.golfraw.com/pga-tour"},
        {"@type": "ListItem", "position": 3, "name": "PGA Tour Winners 2026", "item": "https://www.golfraw.com/news-2026-pga-tour-winners-2026"}
      ]
    },
    {"@type": "Person", "@id": "https://www.golfraw.com/about#editorial", "name": "GOLFRAW Editorial", "url": "https://www.golfraw.com/about"},
    {"@type": "Organization", "@id": "https://www.golfraw.com#organization", "name": "GOLFRAW", "url": "https://www.golfraw.com/"},
    {
      "@type": "FAQPage",
      "@id": "https://www.golfraw.com/news-2026-pga-tour-winners-2026#faq",
      "mainEntity": [
        {"@type": "Question", "name": "Who had the most wins on the PGA Tour in 2026?", "acceptedAnswer": {"@type": "Answer", "text": "Wyndham Clark, Chris Gotterup, and Matt Fitzpatrick led the PGA Tour with three wins each in the 2026 season prior to the Tour Championship."}},
        {"@type": "Question", "name": "Did Scottie Scheffler win a major in 2026?", "acceptedAnswer": {"@type": "Answer", "text": "No, despite entering the Tour Championship as the FedExCup leader for the fifth consecutive year, Scottie Scheffler did not win a major in 2026."}}
      ]
    }
  ]
}
</script>"""

if '<script type="application/ld+json">' in html:
    html = re.sub(r'<script type="application/ld\+json">.*?</script>', json_ld, html, flags=re.DOTALL)
else:
    html = html.replace('</head>', json_ld + '\n</head>')

with open('news-2026-pga-tour-winners-2026.html', 'w') as f:
    f.write(html)
