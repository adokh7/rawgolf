import re

with open("article-template.html", "r") as f:
    template = f.read()

# Replace title
template = re.sub(
    r'<title>.*?</title>', 
    '<title>Scheffler and McIlroy Together, on ESPN, Thursday | GolfRaw</title>', 
    template
)

# Replace meta description
template = re.sub(
    r'<meta name="description" content="[^"]*">', 
    '<meta name="description" content="Scheffler and McIlroy are paired for two rounds in ESPN\'s morning window. ESPN hasn\'t shown the Tour Championship since 2006 — the year before the FedExCup.">', 
    template
)

# Make sure robots is exactly correct
template = re.sub(
    r'<meta name="robots" content="[^"]*">', 
    '<meta name="robots" content="index, follow, max-image-preview:large">', 
    template
)

# Open Graph tags
template = re.sub(
    r'<meta property="og:title" content="[^"]*">', 
    '<meta property="og:title" content="Scheffler and McIlroy Together, on ESPN, Thursday | GolfRaw">', 
    template
)
template = re.sub(
    r'<meta property="og:description" content="[^"]*">', 
    '<meta property="og:description" content="Scheffler and McIlroy are paired for two rounds in ESPN\'s morning window. ESPN hasn\'t shown the Tour Championship since 2006 — the year before the FedExCup.">', 
    template
)
template = re.sub(
    r'<meta property="og:url" content="[^"]*">', 
    '<meta property="og:url" content="https://www.golfraw.com/news-2026-espn-pga-tour-playoffs-coverage-fedex-st-jude">', 
    template
)
template = re.sub(
    r'<link rel="canonical" href="[^"]*">', 
    '<link rel="canonical" href="https://www.golfraw.com/news-2026-espn-pga-tour-playoffs-coverage-fedex-st-jude">', 
    template
)
template = re.sub(
    r'<meta property="og:image" content="[^"]*">', 
    '<meta property="og:image" content="https://www.golfraw.com/public/espn-pga-tour-playoffs-fedex-st-jude-2026.webp">', 
    template
)
template = re.sub(
    r'<meta name="twitter:title" content="[^"]*">', 
    '<meta name="twitter:title" content="Scheffler and McIlroy Together, on ESPN, Thursday | GolfRaw">', 
    template
)
template = re.sub(
    r'<meta name="twitter:description" content="[^"]*">', 
    '<meta name="twitter:description" content="Scheffler and McIlroy are paired for two rounds in ESPN\'s morning window. ESPN hasn\'t shown the Tour Championship since 2006 — the year before the FedExCup.">', 
    template
)
template = re.sub(
    r'<meta name="twitter:image" content="[^"]*">', 
    '<meta name="twitter:image" content="https://www.golfraw.com/public/espn-pga-tour-playoffs-fedex-st-jude-2026.webp">', 
    template
)

# Generate new article content
article_content = """
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/#pga-tour">PGA Tour</a> / <span>News</span>
        </nav>

        <header class="article-head">
          <span class="cat">PGA Tour · News</span>
          <h1>ESPN Last Showed the Tour Championship in 2006. It's Back the Year the Whole Thing Went Up in the Air.</h1>
          <p class="standfirst">World No. 1 Scottie Scheffler and Rory McIlroy headline the opening two rounds of the FedEx St. Jude Championship together inside ESPN's Thursday morning broadcast window. Markings ESPN's first live linear return to the Tour Championship since 2006—before the FedExCup era even existed—the network expands into a playoff format facing major structural shifts after 2027.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>AUG 12 2026</b></span>
          </div>
        </header>
        
        <figure class="lead-img" style="border:none;">
          <img src="/public/espn-pga-tour-playoffs-fedex-st-jude-2026.webp" alt="ESPN PGA Tour Playoffs Coverage FedEx St Jude 2026" />
        </figure>
        <figcaption>PHOTO: GETTY IMAGES / RAWGOLF</figcaption>

        <div class="article-body">
          <div class="meta-callout" style="border-left: 4px solid #10b981; padding-left: 12px; margin: 16px 0;">
            <strong>Broadcast & Playoffs Analysis:</strong> August 12, 2026 | ESPN Broadcast Rights & TPC Southwind Setup
          </div>

          <h2>ESPN Linear Coverage and PGA Tour Live Streaming Scale</h2>
          <p>ESPN will broadcast 12 hours of main linear morning coverage across all three playoff events: the FedEx St. Jude Championship (Aug 13–14), BMW Championship (Aug 20–21), and Tour Championship (Aug 27–28). Enhanced broadcasts feature drone cameras, player audio, and 3D modeling from PGA Tour Studios.</p>

          <p>Simultaneously, PGA Tour Live on the ESPN App delivers over 100 hours across four concurrent streams (Main Feed, Marquee Group, Featured Groups, and Featured Holes).</p>

          <h2>Key Marquee Groupings for Memphis</h2>
          <ul>
            <li><strong>ESPN Thursday Morning:</strong> Scottie Scheffler with Rory McIlroy; Tommy Fleetwood with Jordan Spieth; Tom Kim with Ludvig Åberg.</li>
            <li><strong>ESPN Friday Morning:</strong> Wyndham Clark with Matt Fitzpatrick; Michael Brennan with Justin Rose; Chris Gotterup with Min Woo Lee.</li>
            <li><strong>Golf Channel Thursday Afternoon:</strong> Cameron Young with Collin Morikawa; Xander Schauffele with Sam Burns; Ryan Fox with Adam Scott.</li>
          </ul>

          <h2>TPC Southwind Course Difficulty: Par-70 Analysis</h2>
          <p>Playing at 7,288 yards to a par 70, TPC Southwind represents one of the tour's sternest scoring tests despite being shorter than recent venues. Comparing recent winning scores across identical par-70 layouts highlights Southwind's structural rigor:</p>

          <ul>
            <li><strong>Sedgefield Country Club (7,131 yards):</strong> Michael Brennan won at 22-under par (258 strokes).</li>
            <li><strong>Detroit Golf Club (7,328 yards):</strong> Michael Thorbjornsen won at 18-under par (262 strokes).</li>
            <li><strong>TPC Southwind (7,288 yards):</strong> Justin Rose won in 2025 at 16-under par (264 strokes).</li>
          </ul>

          <h2>High Stakes and $20 Million Purse</h2>
          <p>With 69 players competing across four rounds with no cut, $20 million is on the line with $3.6 million going to the winner. Quadrupled FedExCup playoff points offer dramatic standing shifts, as the top 50 after Sunday secure places in all eight 2027 Signature Events and advance to the BMW Championship.</p>

          <p>Regarding historical records, Scottie Scheffler arrives seeking his second overall FedExCup title after securing his first in 2024.</p>

          <div class="faq-section" style="background:#F3F4F0; padding:20px; border:2px solid var(--ink); margin: 34px 0;">
            <h2>Frequently Asked Questions</h2>

            <h3>When is ESPN broadcasting the FedEx St. Jude Championship?</h3>
            <p>ESPN broadcasts live linear coverage from 9:00 AM to 11:00 AM ET on Thursday, August 13 and Friday, August 14.</p>

            <h3>Who is Scottie Scheffler paired with for the first two rounds?</h3>
            <p>Scheffler is paired alongside Rory McIlroy for Thursday and Friday morning rounds in Memphis.</p>

            <h3>What is the purse and course setup at TPC Southwind?</h3>
            <p>The tournament features a $20 million purse ($3.6M winner's share) played at TPC Southwind (7,288 yards, Par 70).</p>

            <h3>How many FedExCup titles has Scottie Scheffler won?</h3>
            <p>Scottie Scheffler has won one FedExCup title, capturing the season-long championship in 2024.</p>
          </div>

          <h2>The Raw Take</h2>
          <p>ESPN's expanded production investment reflects high confidence in golf's broadcast numbers, even as the PGA Tour prepares for schedule restructures in 2028. TPC Southwind remains an uncompromising venue where narrow Zoysia fairways and water hazards test precision over distance.</p>

          <nav class="tag-row" aria-label="Article tags">
            <a href="#">PGA Tour</a>
            <a href="#">FedExCup Playoffs</a>
            <a href="#">ESPN</a>
            <a href="#">Scottie Scheffler</a>
            <a href="#">Rory McIlroy</a>
          </nav>
        </div>
"""

# Replace the `<article>` content
template = re.sub(
    r'<article>.*?</article>', 
    '<article>\n' + article_content + '\n      </article>', 
    template,
    flags=re.DOTALL
)

with open("news-2026-espn-pga-tour-playoffs-coverage-fedex-st-jude.html", "w") as f:
    f.write(template)

print("Created news-2026-espn-pga-tour-playoffs-coverage-fedex-st-jude.html")
