import re

with open("article-template.html", "r") as f:
    template = f.read()

# Replace title
template = re.sub(
    r'<title>.*?</title>', 
    '<title>The Best Woman in College Golf Gets an Invitation | GolfRaw</title>', 
    template
)

# Replace meta description
template = re.sub(
    r'<meta name="description" content="[^"]*">', 
    '<meta name="description" content="Megha Ganne won the Inkster Award and makes her LPGA debut in Portland. Men\'s college golf\'s top finishers get Tour cards. Hers gets one sponsor invite.">', 
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
    '<meta property="og:title" content="The Best Woman in College Golf Gets an Invitation | GolfRaw">', 
    template
)
template = re.sub(
    r'<meta property="og:description" content="[^"]*">', 
    '<meta property="og:description" content="Megha Ganne won the Inkster Award and makes her LPGA debut in Portland. Men\'s college golf\'s top finishers get Tour cards. Hers gets one sponsor invite.">', 
    template
)
template = re.sub(
    r'<meta property="og:url" content="[^"]*">', 
    '<meta property="og:url" content="https://www.golfraw.com/news-2026-megha-ganne-lpga-debut-inkster-award">', 
    template
)
template = re.sub(
    r'<link rel="canonical" href="[^"]*">', 
    '<link rel="canonical" href="https://www.golfraw.com/news-2026-megha-ganne-lpga-debut-inkster-award">', 
    template
)
template = re.sub(
    r'<meta property="og:image" content="[^"]*">', 
    '<meta property="og:image" content="https://www.golfraw.com/public/megha-ganne-lpga-debut-inkster-award-2026.webp">', 
    template
)
template = re.sub(
    r'<meta name="twitter:title" content="[^"]*">', 
    '<meta name="twitter:title" content="The Best Woman in College Golf Gets an Invitation | GolfRaw">', 
    template
)
template = re.sub(
    r'<meta name="twitter:description" content="[^"]*">', 
    '<meta name="twitter:description" content="Megha Ganne won the Inkster Award and makes her LPGA debut in Portland. Men\'s college golf\'s top finishers get Tour cards. Hers gets one sponsor invite.">', 
    template
)
template = re.sub(
    r'<meta name="twitter:image" content="[^"]*">', 
    '<meta name="twitter:image" content="https://www.golfraw.com/public/megha-ganne-lpga-debut-inkster-award-2026.webp">', 
    template
)

# Generate new article content
article_content = """
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/#pga-tour">LPGA Tour</a> / <span>News</span>
        </nav>

        <header class="article-head">
          <span class="cat">LPGA Tour · News</span>
          <h1>The Best Man in College Golf Gets a PGA Tour Card. The Best Woman Gets an Invitation.</h1>
          <p class="standfirst">Megha Ganne makes her regular-season LPGA Tour debut as a professional this week at the Standard Portland Classic via a sponsor invitation awarded for winning the Juli Inkster Award. While men's collegiate standouts like <a href="/news-2026-pinnacle-bank-championship-frankie-harris-59">Frankie Harris</a> and <a href="/news-2026-jackson-koivun-tpc-southwind-fedex-st-jude">Jackson Koivun</a> transition directly onto top-tier men's tours via PGA Tour University, top women's college graduates earn Epson Tour status alongside isolated sponsor exemptions.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>AUG 12 2026</b></span>
          </div>
        </header>
        
        <figure class="lead-img" style="border:none;">
          <img src="/public/megha-ganne-lpga-debut-inkster-award-2026.webp" alt="Megha Ganne LPGA Debut Inkster Award 2026" />
        </figure>
        <figcaption>PHOTO: GETTY IMAGES / RAWGOLF</figcaption>

        <div class="article-body">
          <div class="meta-callout" style="border-left: 4px solid #10b981; padding-left: 12px; margin: 16px 0;">
            <strong>Collegiate Golf & Tour Pathways:</strong> August 12, 2026 | Megha Ganne LPGA Debut & Inkster Award
          </div>

          <h2>An Exceptional Collegiate and Amateur Record</h2>
          <p>Ganne brings a decorated amateur resume to the professional ranks. At age 17, she shared the first-round lead at the 2021 U.S. Women's Open at The Olympic Club and finished tied 14th as low amateur. Her Stanford career includes:</p>

          <ul>
            <li><strong>NCAA Championships:</strong> Two national team titles (2024 and 2026), clinching the deciding point in 2026.</li>
            <li><strong>Augusta National Women's Amateur:</strong> Shot a tournament-record 63 in 2025.</li>
            <li><strong>U.S. Women's Amateur:</strong> Captured the 2025 title at Bandon Dunes.</li>
          </ul>

          <h2>What the Inkster Award Provides</h2>
          <p>Presented by Workday, the Inkster Award recognizes the highest-ranked Division I female golfer in her final year of eligibility. It provides three primary benefits:</p>

          <ul>
            <li>A sponsor invitation to the $2 million Standard Portland Classic at Columbia Edgewater Country Club.</li>
            <li>$50,000 to the Juli Inkster Foundation to cover professional transition and travel expenses.</li>
            <li>A two-day mentorship retreat with Hall of Famer Juli Inkster in Northern California.</li>
          </ul>

          <h2>PGA Tour University vs. LPGA Pathway Structure</h2>
          <p>The disparity between men's and women's collegiate transition systems reflects broader commercial differences rather than intentional policy. PGA Tour University awards direct status on the PGA Tour or Korn Ferry Tour to its top 10 finishers. Conversely, the LPGA's collegiate pipeline relies on developmental Epson Tour status complemented by individual award exemptions.</p>

          <div class="faq-section" style="background:#F3F4F0; padding:20px; border:2px solid var(--ink); margin: 34px 0;">
            <h2>Frequently Asked Questions</h2>

            <h3>Who is Megha Ganne?</h3>
            <p>Megha Ganne is a former Stanford All-American, 2025 U.S. Women's Amateur champion, and winner of the 2026 Inkster Award who made her professional debut in 2026.</p>

            <h3>What is the Inkster Award?</h3>
            <p>An annual award recognizing the top Division I senior female college golfer, granting an LPGA sponsor exemption, $50,000 in travel support, and a mentorship retreat with Juli Inkster.</p>

            <h3>What tour does Megha Ganne play on?</h3>
            <p>She plays on the Epson Tour, the official developmental tour of the LPGA, having earned status through the collegiate pathway.</p>

            <h3>Where is Ganne making her regular-season LPGA debut?</h3>
            <p>At the Standard Portland Classic held at Columbia Edgewater Country Club in Portland, Oregon.</p>
          </div>

          <h2>The Raw Take</h2>
          <p>Ganne's transition highlights structural differences between men's and women's professional pathways. While PGA Tour University offers immediate access to premier tournaments, the Inkster Award provides vital exposure and financial backing as Ganne begins her professional career on the Epson Tour.</p>

          <nav class="tag-row" aria-label="Article tags">
            <a href="#">LPGA Tour</a>
            <a href="#">Megha Ganne</a>
            <a href="#">Collegiate Golf</a>
            <a href="#">Epson Tour</a>
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

with open("news-2026-megha-ganne-lpga-debut-inkster-award.html", "w") as f:
    f.write(template)

print("Created news-2026-megha-ganne-lpga-debut-inkster-award.html")
