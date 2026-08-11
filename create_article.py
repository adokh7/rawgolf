import json

template_path = "article-template.html"
with open(template_path, "r") as f:
    template = f.read()

# Replace head metadata
template = template.replace(
    "<title>Oakmont US Open Setup: How the USGA Broke the | GOLFRAW</title>",
    "<title>The Tournament the Tour Demoted Is the Hardest One | GolfRaw</title>"
)
template = template.replace(
    '<meta name="description" content="Average score 74.8, stimp at 15. We walked Oakmont&#x27;s US Open setup with two tour caddies to find out which pins cross the line — and who secretly loves it.">',
    '<meta name="description" content="Detroit gave up three 61s. Sedgefield gave up 36 rounds under 66. TPC Southwind is the same par and the hardest of the three — and it\'s being relegated.">'
)
template = template.replace(
    '<link rel="canonical" href="https://www.golfraw.com/article-template">',
    '<link rel="canonical" href="https://www.golfraw.com/news-2026-fedex-st-jude-championship-tpc-southwind-demotion">'
)
template = template.replace(
    '<meta property="og:title" content="Oakmont US Open Setup: How the USGA Broke the | GOLFRAW">',
    '<meta property="og:title" content="The Tournament the Tour Demoted Is the Hardest One | GolfRaw">'
)
template = template.replace(
    '<meta property="og:description" content="Average score 74.8, stimp at 15. We walked Oakmont&#x27;s US Open setup with two tour caddies to find out which pins cross the line — and who secretly loves it.">',
    '<meta property="og:description" content="Detroit gave up three 61s. Sedgefield gave up 36 rounds under 66. TPC Southwind is the same par and the hardest of the three — and it\'s being relegated.">'
)
template = template.replace(
    '<meta property="og:url" content="https://www.golfraw.com/article-template">',
    '<meta property="og:url" content="https://www.golfraw.com/news-2026-fedex-st-jude-championship-tpc-southwind-demotion">'
)
template = template.replace(
    '<meta property="og:image" content="https://www.golfraw.com/public/raw-golf-practice.webp">',
    '<meta property="og:image" content="https://www.golfraw.com/public/tpc-southwind-fedex-st-jude-championship-2026.webp">'
)
template = template.replace(
    '<meta name="twitter:title" content="Oakmont US Open Setup: How the USGA Broke the | GOLFRAW">',
    '<meta name="twitter:title" content="The Tournament the Tour Demoted Is the Hardest One | GolfRaw">'
)
template = template.replace(
    '<meta name="twitter:description" content="Average score 74.8, stimp at 15. We walked Oakmont&#x27;s US Open setup with two tour caddies to find out which pins cross the line — and who secretly loves it.">',
    '<meta name="twitter:description" content="Detroit gave up three 61s. Sedgefield gave up 36 rounds under 66. TPC Southwind is the same par and the hardest of the three — and it\'s being relegated.">'
)
template = template.replace(
    '<meta name="twitter:image" content="https://www.golfraw.com/public/raw-golf-practice.webp">',
    '<meta name="twitter:image" content="https://www.golfraw.com/public/tpc-southwind-fedex-st-jude-championship-2026.webp">'
)
template = template.replace(
    '<meta property="article:published_time" content="2026-06-13T07:30:00+02:00" />',
    '<meta property="article:published_time" content="2026-08-11T12:00:00+02:00" />'
)
template = template.replace(
    '<meta property="article:modified_time" content="2026-06-13T09:42:00+02:00">',
    '<meta property="article:modified_time" content="2026-08-11T12:00:00+02:00">'
)

# JSON-LD Schema Replace
template = template.replace(
    '"headline": "Oakmont Is Eating the Field Alive — and the USGA Planned It That Way",',
    '"headline": "The Tournament the Tour Demoted Is the Hardest One",'
)
template = template.replace(
    '"description": "Average score 74.8, greens at 15 on the stimp. Two tour caddies walked us through the US Open setup built to break the field.",',
    '"description": "Detroit gave up three 61s. Sedgefield gave up 36 rounds under 66. TPC Southwind is the same par and the hardest of the three — and it\'s being relegated.",'
)
template = template.replace(
    '"https://www.golfraw.com/public/img/oakmont-2026-setup-og.jpg"',
    '"https://www.golfraw.com/public/tpc-southwind-fedex-st-jude-championship-2026.webp"'
)
template = template.replace(
    '"datePublished": "2026-06-13T07:30:00+02:00",',
    '"datePublished": "2026-08-11T12:00:00+02:00",'
)
template = template.replace(
    '"dateModified": "2026-06-13T09:42:00+02:00",',
    '"dateModified": "2026-08-11T12:00:00+02:00",'
)
template = template.replace(
    '"mainEntityOfPage": "https://www.golfraw.com/article-template"',
    '"mainEntityOfPage": "https://www.golfraw.com/news-2026-fedex-st-jude-championship-tpc-southwind-demotion"'
)

# Replace the article content completely
article_start_tag = "<article>"
article_end_tag = "</article>"

new_article_content = """<article>
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/#tournaments">Tournaments</a> / <span>FedExCup Playoffs 2026</span>
        </nav>

        <header class="article-head">
          <span class="cat">Tournaments · PGA Tour</span>
          <h1>The Tournament the Tour Just Demoted Is the Hardest One of the Three</h1>
          <p class="standfirst">Across three consecutive weeks of par-70 layouts, the PGA Tour arrives at TPC Southwind in Memphis (7,233 yards). Detroit Golf Club gave up three 61s, and Sedgefield surrendered thirty-six rounds under 66 on Thursday alone. TPC Southwind is by far the most difficult test of the three—and it is the exact tournament the Tour confirmed five days ago will not be part of its top-tier Championship Series when the schedule restructures in 2028.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>TUE 11 AUG 2026</b></span>
            <span><b>3 MIN READ</b></span>
          </div>
        </header>

        <div class="meta-callout" style="border-left: 4px solid #10b981; padding-left: 12px; margin: 16px 0;">
          <strong>FedExCup Playoffs Stage 1:</strong> August 11, 2026 | TPC Southwind Course Breakdown & Field Preview
        </div>

        <figure class="lead-img">
            <img src="/public/tpc-southwind-fedex-st-jude-championship-2026.webp" alt="TPC Southwind FedEx St Jude Championship 2026" />
        </figure>
        <figcaption>TPC SOUTHWIND DEFENDS ITSELF WITH ZOYSIA FAIRWAYS AND WATER HAZARDS ON 11 HOLES.</figcaption>

        <div class="article-body">
          <h2>What Makes TPC Southwind So Difficult</h2>
          <p>Unlike longer venues, Southwind's defense relies on demanding ball-striking architecture rather than raw yardage:</p>

          <ul>
            <li><strong>Seven Par-Fours Over 450 Yards:</strong> On a par-70 course with only two par fives, players face long irons on approach shots instead of short scoring wedges.</li>
            <li><strong>Water on 11 Holes:</strong> Strategic water hazards penalize off-target drives directly.</li>
            <li><strong>Zoysia Fairways & Bermuda Rough:</strong> Dense, grabby Zoysia paired with thick Bermuda rough severely limits clubhead speed on missed fairways.</li>
          </ul>

          <h2>What Is at Stake in Memphis</h2>
          <p>The field features 69 players (Daniel Berger, ranked 60th, opted not to enter) with no 36-hole cut. Points are quadrupled compared to regular season events, creating massive leaderboard volatility across $20 million in prize money.</p>

          <p>Advancing into the Top 50 after Sunday secures entry into the BMW Championship at Bellerive and guarantees spots in all eight 2027 Signature Events. Reaching the Top 30 after the BMW Championship earns a two-year Tour exemption and a spot at the 2027 Masters.</p>

          <h2>Scheffler, McIlroy, and Key Contenders</h2>
          <p>Scottie Scheffler leads the FedExCup standings following a remarkably consistent season featuring one win, five runner-up finishes, and eleven top-fives. Under the updated playoff format, all thirty finalists now begin at even par at East Lake, removing previous handicap strokes.</p>

          <p>Rory McIlroy makes his return to TPC Southwind after skipping the event last season, while Hideki Matsuyama brings the strongest course history in the field—highlighted by his 2024 victory. 2025 champion Justin Rose and Sam Burns (ranked second on Tour in par-4 scoring at 3.95) also represent serious threats.</p>

          <div class="faq-section">
            <h2>Frequently Asked Questions</h2>

            <h3>When is the 2026 FedEx St. Jude Championship?</h3>
            <p>The tournament takes place August 13–16 at TPC Southwind in Memphis, Tennessee, serving as the opening event of the FedExCup Playoffs.</p>

            <h3>How many players are competing at TPC Southwind?</h3>
            <p>69 players are in the field. Daniel Berger (ranked 60th) chose not to enter, and there is no 36-hole cut.</p>

            <h3>Is Memphis losing its PGA Tour playoff event?</h3>
            <p>The PGA Tour confirmed TPC Southwind will not feature in the top-tier Championship Series starting in 2028, though it remains under consideration for the second-tier Challenger Series.</p>

            <h3>What are the qualifications for the next playoff leg?</h3>
            <p>The top 50 in FedExCup points after Sunday advance to the BMW Championship and qualify for all 2027 Signature Events.</p>
          </div>

          <h2>The Raw Take</h2>
          <p>TPC Southwind represents pure championship golf where accuracy off the tee and long-iron control dictate survival. While commercial restructuring and August heat in Tennessee have reshaped its future status, Southwind remains the sternest physical test of the Tour's late-summer swing.</p>
        </div>
      </article>"""

start_idx = template.find(article_start_tag)
end_idx = template.find(article_end_tag) + len(article_end_tag)

new_html = template[:start_idx] + new_article_content + template[end_idx:]

with open("news-2026-fedex-st-jude-championship-tpc-southwind-demotion.html", "w") as f:
    f.write(new_html)

print("Created news-2026-fedex-st-jude-championship-tpc-southwind-demotion.html")

# Update articles.json
with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "url": "/news-2026-fedex-st-jude-championship-tpc-southwind-demotion",
  "title": "The Tournament the Tour Demoted Is the Hardest One",
  "category": "PGA TOUR",
  "date": "AUG 11 2026",
  "image": "/public/tpc-southwind-fedex-st-jude-championship-2026.webp",
  "snippet": "Detroit gave up three 61s. Sedgefield gave up 36 rounds under 66. TPC Southwind is the same par and the hardest of the three — and it's being relegated.",
  "keywords": "fedex st jude championship 2026, tpc southwind course, fedexcup playoffs field, fedex st jude purse, scottie scheffler fedexcup"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)

print("Updated articles.json")
