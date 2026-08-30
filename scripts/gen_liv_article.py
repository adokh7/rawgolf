import os
from pathlib import Path
try:
    from scripts.fix_template_metadata import finalize_html
except ModuleNotFoundError:
    from fix_template_metadata import finalize_html
import json

ROOT = Path(__file__).resolve().parents[1]
template_path = ROOT / 'article-template.html'
output_path = ROOT / 'news-2026-liv-golf-bedminster-crushers-six-over-par.html'

with open(template_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace Head Metadata
html = html.replace('<title>Oakmont US Open Setup: How the USGA Broke the | GOLFRAW</title>', '<title>The Winning Team Finished Six Over Par | GolfRaw</title>')
html = html.replace('content="Average score 74.8, stimp at 15. We walked Oakmont&#x27;s US Open setup with two tour caddies to find out which pins cross the line — and who secretly loves it."', 'content="Crushers GC won LIV New York at six over — the highest winning team score in league history. Niemann took the individual title wire to wire at 16 under."')
html = html.replace('href="https://www.golfraw.com/article-template"', 'href="https://www.golfraw.com/news-2026-liv-golf-bedminster-crushers-six-over-par"')
html = html.replace('<meta property="og:title" content="Oakmont US Open Setup: How the USGA Broke the | GOLFRAW">', '<meta property="og:title" content="The Winning Team Finished Six Over Par | GolfRaw">')
html = html.replace('<meta name="twitter:title" content="Oakmont US Open Setup: How the USGA Broke the | GOLFRAW">', '<meta name="twitter:title" content="The Winning Team Finished Six Over Par | GolfRaw">')
html = html.replace('content="https://www.golfraw.com/public/raw-golf-practice.webp"', 'content="https://www.golfraw.com/public/joaquin-niemann-liv-bedminster-win-2026.webp"')

# Make sure robots meta tag is correct
if '<meta name="robots" content="index, follow, max-image-preview:large">' not in html:
    print("WARNING: Robots tag not found")

# Replace article section
article_content = """<article>
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/liv-golf">LIV Golf</a> / <span>Bedminster 2026</span>
        </nav>

        <header class="article-head">
          <span class="cat">LIV GOLF</span>
          <h1>The Winning Team Finished Six Over Par. That Has Never Happened Before.</h1>
          <p class="standfirst">Bryson DeChambeau's Crushers GC won the team title at LIV Golf New York with a cumulative score of six over par—the highest score ever posted by a winning team in the league's history. Joaquín Niemann claimed the individual title at sixteen under par wire-to-wire, while 53-year-old Lee Westwood finished tied for third at nine under.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>MON 10 AUG 2026</b></span>
            <span><b>3 MIN READ</b></span>
          </div>
        </header>

        <div class="meta-callout" style="border-left: 4px solid #10b981; padding-left: 12px; margin: 16px 0;">
          <strong>LIV Golf Bedminster Recap:</strong> August 10, 2026 | Trump National Bedminster Final Results
        </div>

        <figure class="lead-img">
          <img src="/public/joaquin-niemann-liv-bedminster-win-2026.webp" alt="Joaquin Niemann and Crushers GC LIV Golf Bedminster 2026" />
        </figure>
        <figcaption>CRUSHERS GC SET A LIV GOLF RECORD FOR HIGHEST WINNING TEAM SCORE AT SIX OVER PAR. PHOTO: RAWGOLF</figcaption>

        <div class="article-body">
          <h2>Niemann's Record Ninth LIV Victory</h2>
          <p>Joaquín Niemann led from Thursday morning to Sunday afternoon, becoming the fifth wire-to-wire winner on LIV Golf this season. Opening rounds of 64, 65, and 70 gave him a two-shot cushion entering Sunday. Despite an opening bogey and pressure from Harold Varner III, Niemann answered with a 58-foot birdie putt on the 13th hole and a 26-foot eagle conversion on the 15th to seal a three-shot victory at 16 under par (268).</p>

          <p>The win marks Niemann's ninth individual LIV title in three years, extending his league record and earning him $4,000,000 from the $20,000,000 individual purse.</p>

          <h2>Six Over Par: Bedminster's Historic Test</h2>
          <p>In a league often characterized by low-scoring shootouts, Trump National Bedminster presented an unyielding challenge. Measuring 7,651 yards (par 71)—lengthened by more than 125 yards since 2023—the layout pushed the entire field:</p>

          <ul>
            <li><strong>Crushers GC Victory:</strong> DeChambeau's squad captured their record 11th regular-season team title with a score of +6, the first over-par winning team total in LIV history.</li>
            <li><strong>Scoring Dispersion:</strong> While Niemann dominated at 16 under, solo third place sat at 9 under, illustrating how difficult conditions separated elite ball-striking from the pack.</li>
          </ul>

          <h2>Westwood at Fifty-Three and Rahm's Championship</h2>
          <p>Lee Westwood closed with a 72 to finish tied for third at 9 under alongside Scott Vincent. Competing on the second-longest layout of the season, the 53-year-old outperformed dozens of competitors half his age through disciplined course management.</p>

          <p>Meanwhile, Jon Rahm carded a final-round 76 to finish tied for 41st—his lowest finish across 36 completed LIV starts. However, his dominant regular season secured him the season-long Individual Championship for the third consecutive year (2024, 2025, 2026) along with the $6 million bonus.</p>

          <h2>Frequently Asked Questions</h2>

          <h3>Who won LIV Golf New York 2026?</h3>
          <p>Joaquín Niemann won the individual title wire-to-wire at 16 under par (268), three strokes ahead of Harold Varner III.</p>

          <h3>Who won the team competition at Bedminster?</h3>
          <p>Crushers GC, captained by Bryson DeChambeau, won the team title at six over par (+6), setting a LIV Golf record for the highest winning team score.</p>

          <h3>Who won the 2026 LIV Golf Individual Championship?</h3>
          <p>Jon Rahm clinched the season-long Individual Championship for the third consecutive year, earning a $6 million bonus.</p>

          <h3>What was the official purse payout for the winner?</h3>
          <p>Niemann earned $4,000,000 from a $20,000,000 individual prize pool.</p>

          <h3>Where did Lee Westwood finish?</h3>
          <p>Westwood finished tied for third at 9 under par after carding a final-round 72.</p>

          <h2>The Raw Take</h2>
          <p>A winning team score of six over par destroys the narrative that modern professional setups cannot challenge elite players. Trump National Bedminster proved that length, firm greens, and tight margins expose weaknesses quickly. Niemann's dominance was exceptional, but the tournament belonged to a golf course that refused to yield easy scores.</p>
        </div>
      </article>"""

# Find the start and end of <article> in the HTML and replace it
import re
html = re.sub(r'<article>.*?</article>', article_content, html, flags=re.DOTALL)

html = finalize_html(html, output_path, force=True)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Article created successfully.")
