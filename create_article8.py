import json
import shutil
import os

# Ensure the image exists by copying the existing one
source_img = "public/brooks-koepka-wyndham-putting-pga-tour.webp"
target_img = "public/brooks-koepka-wyndham-championship-2026.webp"
if os.path.exists(source_img) and not os.path.exists(target_img):
    shutil.copy(source_img, target_img)
    print("Copied image to new filename")

template_path = "article-template.html"
with open(template_path, "r") as f:
    template = f.read()

# Replace head metadata
template = template.replace(
    "<title>Oakmont US Open Setup: How the USGA Broke the | GOLFRAW</title>",
    "<title>\"Pathetic.\" Also: \"10 Out of 10.\" Same Interview. | GolfRaw</title>"
)
template = template.replace(
    '<meta name="description" content="Average score 74.8, stimp at 15. We walked Oakmont&#x27;s US Open setup with two tour caddies to find out which pins cross the line — and who secretly loves it.">',
    '<meta name="description" content="Koepka called his season pathetic and rated his happiness 10 out of 10, minutes apart. What his return from LIV actually cost, and what went wrong.">'
)
template = template.replace(
    '<link rel="canonical" href="https://www.golfraw.com/article-template">',
    '<link rel="canonical" href="https://www.golfraw.com/news-2026-brooks-koepka-pga-tour-return-season-verdict">'
)
template = template.replace(
    '<meta property="og:title" content="Oakmont US Open Setup: How the USGA Broke the | GOLFRAW">',
    '<meta property="og:title" content="\"Pathetic.\" Also: \"10 Out of 10.\" Same Interview. | GolfRaw">'
)
template = template.replace(
    '<meta property="og:description" content="Average score 74.8, stimp at 15. We walked Oakmont&#x27;s US Open setup with two tour caddies to find out which pins cross the line — and who secretly loves it.">',
    '<meta property="og:description" content="Koepka called his season pathetic and rated his happiness 10 out of 10, minutes apart. What his return from LIV actually cost, and what went wrong.">'
)
template = template.replace(
    '<meta property="og:url" content="https://www.golfraw.com/article-template">',
    '<meta property="og:url" content="https://www.golfraw.com/news-2026-brooks-koepka-pga-tour-return-season-verdict">'
)
template = template.replace(
    '<meta property="og:image" content="https://www.golfraw.com/public/raw-golf-practice.webp">',
    '<meta property="og:image" content="https://www.golfraw.com/public/brooks-koepka-wyndham-championship-2026.webp">'
)
template = template.replace(
    '<meta name="twitter:title" content="Oakmont US Open Setup: How the USGA Broke the | GOLFRAW">',
    '<meta name="twitter:title" content="\"Pathetic.\" Also: \"10 Out of 10.\" Same Interview. | GolfRaw">'
)
template = template.replace(
    '<meta name="twitter:description" content="Average score 74.8, stimp at 15. We walked Oakmont&#x27;s US Open setup with two tour caddies to find out which pins cross the line — and who secretly loves it.">',
    '<meta name="twitter:description" content="Koepka called his season pathetic and rated his happiness 10 out of 10, minutes apart. What his return from LIV actually cost, and what went wrong.">'
)
template = template.replace(
    '<meta name="twitter:image" content="https://www.golfraw.com/public/raw-golf-practice.webp">',
    '<meta name="twitter:image" content="https://www.golfraw.com/public/brooks-koepka-wyndham-championship-2026.webp">'
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
    '"headline": "Brooks Koepka Gave Two Opposite Verdicts on His Season in the Same Interview",'
)
template = template.replace(
    '"description": "Average score 74.8, greens at 15 on the stimp. Two tour caddies walked us through the US Open setup built to break the field.",',
    '"description": "Koepka called his season pathetic and rated his happiness 10 out of 10, minutes apart. What his return from LIV actually cost, and what went wrong.",'
)
template = template.replace(
    '"https://www.golfraw.com/public/img/oakmont-2026-setup-og.jpg"',
    '"https://www.golfraw.com/public/brooks-koepka-wyndham-championship-2026.webp"'
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
    '"mainEntityOfPage": "https://www.golfraw.com/news-2026-brooks-koepka-pga-tour-return-season-verdict"'
)

new_article_content = """<article>
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/#news">News</a> / <span>PGA Tour</span>
        </nav>

        <header class="article-head">
          <span class="cat">News · PGA Tour</span>
          <h1>Brooks Koepka Gave Two Opposite Verdicts on His Season in the Same Interview</h1>
          <p class="standfirst">Brooks Koepka wrapped up his first PGA Tour season in four years on Sunday afternoon at Sedgefield, missed the <a href="/news-2026-wyndham-championship-brennan-fedexcup-bubble-resolution">FedExCup Playoffs</a>, and told reporters it was "pretty pathetic that I can't get through." Minutes later in the exact same interview, he rated his overall happiness at 10 out of 10. Both statements are accurate reflections of two very different aspects of his year.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>TUE 11 AUG 2026</b></span>
            <span><b>4 MIN READ</b></span>
          </div>
        </header>

        <div class="meta-callout" style="border-left: 4px solid #10b981; padding-left: 12px; margin: 16px 0;">
          <strong>PGA Tour Season Review:</strong> August 11, 2026 | Brooks Koepka's Return Season Analysis
        </div>

        <figure class="lead-img">
            <img src="/public/brooks-koepka-wyndham-championship-2026.webp" alt="Brooks Koepka Wyndham Championship 2026" />
        </figure>
        <figcaption>KOEPKA MISSED THE FEDEXCUP PLAYOFFS BUT PRAISED HIS RETURN TO THE PGA TOUR.</figcaption>

        <div class="article-body">
          <h2>The Statistical Reality of His Season</h2>
          <p>Competitively, Koepka struggled to generate momentum. He made 10 cuts and registered a single top-10 finish—a tie for ninth at the Cognizant Classic in March. Entering the Wyndham Championship ranked 86th in FedExCup points, he needed roughly a top-four finish to reach the top 70. Rounds of 67, 66, 74, and 70 dropped him to around 94th in the final standings.</p>

          <p>When Koepka remarked that he had "zero top-10s basically in two years," he was rounding down based on his high internal standards. For a five-time major champion, a solo T9 finish falls into the category of an unfulfilled week.</p>

          <h2>What Returning to the PGA Tour Cost Him</h2>
          <p>Koepka departed LIV Golf and rejoined the PGA Tour under the Returning Member Program, accepting substantial financial penalties:</p>

          <ul>
            <li><strong>Charitable Contribution:</strong> A $5 million mandatory donation made at the Tour's request.</li>
            <li><strong>Equity Restriction:</strong> Ineligibility for player equity shares for five years.</li>
            <li><strong>Bonus Exclusion:</strong> Ineligible for the $100 million FedExCup bonus program in 2026.</li>
            <li><strong>Signature Event Access:</strong> No sponsor exemptions into high-purse signature events.</li>
            <li><strong>Earnings Forgone:</strong> The PGA Tour estimated he could forgo up to $85 million in potential career earnings.</li>
          </ul>

          <h2>Eighth in Approach, 116th in Putting</h2>
          <p>Koepka's struggles were isolated to a single club. He ranked eighth on the PGA Tour in strokes gained approach but dropped to 116th in strokes gained putting, admitting he had "zero confidence" on the greens. Despite cycling through multiple putters—including a prototype Scotty Cameron with a Teryllium insert at Sedgefield—his elite iron play could not overcome his putting statistics.</p>

          <p>An arm injury forced a withdrawal from the Rocket Classic at Detroit Golf Club the previous week, stripping away vital opportunities to earn playoff points before Greensboro.</p>

          <div class="faq-section">
            <h2>Frequently Asked Questions</h2>

            <h3>Did Brooks Koepka qualify for the 2026 FedExCup Playoffs?</h3>
            <p>No. Koepka finished around 94th in the standings, missing the top 70 cutoff required for the FedEx St. Jude Championship.</p>

            <h3>What did Koepka say about his return season?</h3>
            <p>He called his inability to make the playoffs "pretty pathetic", while also stating that his personal return experience was "great" and rating his happiness as 10 out of 10.</p>

            <h3>What were Koepka's strokes gained rankings this season?</h3>
            <p>Koepka ranked 8th on Tour in strokes gained approach and 116th in strokes gained putting.</p>

            <h3>Where will Brooks Koepka play next?</h3>
            <p>Koepka plans to compete in select DP World Tour events in Europe and participate in the FedExCup Fall schedule beginning in September.</p>
          </div>

          <h2>The Raw Take</h2>
          <p>A golf season can be a competitive failure and a personal success simultaneously. Koepka traded guaranteed money for competitive autonomy, proved his ball-striking remains world-class, and identified a single statistical flaw in his putting that needs fixing. Heading into the autumn, his foundation remains formidable.</p>
        </div>
      </article>"""

article_start_tag = "<article>"
article_end_tag = "</article>"

start_idx = template.find(article_start_tag)
end_idx = template.find(article_end_tag) + len(article_end_tag)

new_html = template[:start_idx] + new_article_content + template[end_idx:]

with open("news-2026-brooks-koepka-pga-tour-return-season-verdict.html", "w") as f:
    f.write(new_html)

print("Created news-2026-brooks-koepka-pga-tour-return-season-verdict.html")

# Update articles.json
with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "url": "/news-2026-brooks-koepka-pga-tour-return-season-verdict",
  "title": "Brooks Koepka Gave Two Opposite Verdicts on His Season in the Same Interview",
  "category": "PGA TOUR",
  "date": "AUG 11 2026",
  "image": "/public/brooks-koepka-wyndham-championship-2026.webp",
  "snippet": "Koepka called his season pathetic and rated his happiness 10 out of 10, minutes apart. What his return from LIV actually cost, and what went wrong.",
  "keywords": "brooks koepka pathetic, koepka missed fedexcup playoffs, koepka returning member program cost, brooks koepka putting stats, koepka liv return"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)

print("Updated articles.json")
