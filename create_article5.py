import json

template_path = "article-template.html"
with open(template_path, "r") as f:
    template = f.read()

# Replace head metadata
template = template.replace(
    "<title>Oakmont US Open Setup: How the USGA Broke the | GOLFRAW</title>",
    "<title>He Shot 59. It Only Got Him Into a Playoff. | GolfRaw</title>"
)
template = template.replace(
    '<meta name="description" content="Average score 74.8, stimp at 15. We walked Oakmont&#x27;s US Open setup with two tour caddies to find out which pins cross the line — and who secretly loves it.">',
    '<meta name="description" content="Frankie Harris shot 12-under 59 to win the Pinnacle Bank Championship — but Docherty birdied his last three to force extra holes. Only nine have done it.">'
)
template = template.replace(
    '<link rel="canonical" href="https://www.golfraw.com/article-template">',
    '<link rel="canonical" href="https://www.golfraw.com/news-2026-pinnacle-bank-championship-frankie-harris-59">'
)
template = template.replace(
    '<meta property="og:title" content="Oakmont US Open Setup: How the USGA Broke the | GOLFRAW">',
    '<meta property="og:title" content="He Shot 59. It Only Got Him Into a Playoff. | GolfRaw">'
)
template = template.replace(
    '<meta property="og:description" content="Average score 74.8, stimp at 15. We walked Oakmont&#x27;s US Open setup with two tour caddies to find out which pins cross the line — and who secretly loves it.">',
    '<meta property="og:description" content="Frankie Harris shot 12-under 59 to win the Pinnacle Bank Championship — but Docherty birdied his last three to force extra holes. Only nine have done it.">'
)
template = template.replace(
    '<meta property="og:url" content="https://www.golfraw.com/article-template">',
    '<meta property="og:url" content="https://www.golfraw.com/news-2026-pinnacle-bank-championship-frankie-harris-59">'
)
template = template.replace(
    '<meta property="og:image" content="https://www.golfraw.com/public/raw-golf-practice.webp">',
    '<meta property="og:image" content="https://www.golfraw.com/public/frankie-harris-59-pinnacle-bank-championship-2026.webp">'
)
template = template.replace(
    '<meta name="twitter:title" content="Oakmont US Open Setup: How the USGA Broke the | GOLFRAW">',
    '<meta name="twitter:title" content="He Shot 59. It Only Got Him Into a Playoff. | GolfRaw">'
)
template = template.replace(
    '<meta name="twitter:description" content="Average score 74.8, stimp at 15. We walked Oakmont&#x27;s US Open setup with two tour caddies to find out which pins cross the line — and who secretly loves it.">',
    '<meta name="twitter:description" content="Frankie Harris shot 12-under 59 to win the Pinnacle Bank Championship — but Docherty birdied his last three to force extra holes. Only nine have done it.">'
)
template = template.replace(
    '<meta name="twitter:image" content="https://www.golfraw.com/public/raw-golf-practice.webp">',
    '<meta name="twitter:image" content="https://www.golfraw.com/public/frankie-harris-59-pinnacle-bank-championship-2026.webp">'
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
    '"headline": "He Shot 59. It Only Got Him Into a Playoff.",'
)
template = template.replace(
    '"description": "Average score 74.8, greens at 15 on the stimp. Two tour caddies walked us through the US Open setup built to break the field.",',
    '"description": "Frankie Harris shot 12-under 59 to win the Pinnacle Bank Championship — but Docherty birdied his last three to force extra holes. Only nine have done it.",'
)
template = template.replace(
    '"https://www.golfraw.com/public/img/oakmont-2026-setup-og.jpg"',
    '"https://www.golfraw.com/public/frankie-harris-59-pinnacle-bank-championship-2026.webp"'
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
    '"mainEntityOfPage": "https://www.golfraw.com/news-2026-pinnacle-bank-championship-frankie-harris-59"'
)

new_article_content = """<article>
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/#news">News</a> / <span>Korn Ferry Tour</span>
        </nav>

        <header class="article-head">
          <span class="cat">News · Korn Ferry Tour</span>
          <h1>He Shot 59 and It Only Got Him Into a Playoff</h1>
          <p class="standfirst">Frankie Harris holed an 18-foot birdie putt on the 18th green at The Club at Indian Creek for a 12-under 59—and it barely got him a playoff. Alistair Docherty birdied his final three holes, including a 53-footer at the 16th, to post 22 under par (262) and force extra holes before Harris secured his maiden Korn Ferry Tour title on the second playoff hole.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>TUE 11 AUG 2026</b></span>
            <span><b>3 MIN READ</b></span>
          </div>
        </header>

        <div class="meta-callout" style="border-left: 4px solid #10b981; padding-left: 12px; margin: 16px 0;">
          <strong>Korn Ferry Tour News:</strong> August 11, 2026 | Pinnacle Bank Championship Final Round
        </div>

        <figure class="lead-img">
            <img src="/public/frankie-harris-59-pinnacle-bank-championship-2026.webp" alt="Frankie Harris 59 Pinnacle Bank Championship 2026" />
        </figure>
        <figcaption>FRANKIE HARRIS BECOMES JUST THE NINTH GOLFER TO WIN WITH A FINAL-ROUND SUB-60 SCORE.</figcaption>

        <div class="article-body">
          <h2>Nine Golfers in History Have Shot Sub-60 and Won</h2>
          <p>Harris became just the ninth golfer worldwide to shoot a final-round sub-60 score and win the tournament. He joins an elite club that includes Bryson DeChambeau (58 at LIV Golf Greenbrier in 2023) and Jim Furyk (58 at the 2016 Travelers Championship).</p>

          <p>The round marked the 18th sub-60 score in Korn Ferry Tour history and the second in two weeks. Harris built his 59 through steady ball-striking and remarkable putting performance:</p>

          <ul>
            <li><strong>Front Nine (32):</strong> Four birdies and five pars.</li>
            <li><strong>Back Nine (27):</strong> Six birdies, an eagle, and two pars.</li>
            <li><strong>Putting Distance:</strong> Made over 153 feet of putts across 18 holes.</li>
          </ul>

          <h2>The Impact of PGA Tour University Class of 2026</h2>
          <p>Harris, 23, finished 9th in the PGA Tour University Class of 2026 after setting school scoring records at South Carolina. His victory highlights an extraordinary fortnight for the collegiate pathway program:</p>

          <ul>
            <li><strong>Michael Thorbjornsen (No. 1, 2024):</strong> Won the Rocket Classic in Detroit for his first PGA Tour title.</li>
            <li><strong>Jackson Koivun (2026):</strong> Won the 3M Open and clinched the final FedExCup playoff spot (70th).</li>
            <li><strong>Ben James (No. 1, 2026):</strong> Opened with a 62 at the Wyndham Championship.</li>
            <li><strong>Frankie Harris (No. 9, 2026):</strong> Fired a 59 to win in his sixth Korn Ferry Tour start.</li>
          </ul>

          <h2>Korn Ferry Points Standing and Future Outlook</h2>
          <p>The victory vault Harris to No. 29 on the Korn Ferry Tour points list, placing him nine spots outside the top 20 promotion cutoff for 2027 PGA Tour cards. Robby Shelton finished solo third at 19 under par, while Doc Redman finished fourth.</p>

          <div class="faq-section">
            <h2>Frequently Asked Questions</h2>

            <h3>Who won the 2026 Pinnacle Bank Championship?</h3>
            <p>Frankie Harris won his first Korn Ferry Tour title on the second playoff hole against Alistair Docherty after shooting a 12-under 59 in regulation.</p>

            <h3>How rare is shooting a sub-60 round in a final round to win?</h3>
            <p>Only nine golfers worldwide have shot below 60 in a tournament's final round and gone on to win the event.</p>

            <h3>How did Alistair Docherty force a playoff?</h3>
            <p>Docherty birdied his last three holes—highlighted by a 53-foot putt on the 16th—for a closing 64 to tie Harris at 22 under par (262).</p>

            <h3>Where does Frankie Harris stand on the Korn Ferry Tour points list?</h3>
            <p>The win moves Harris to No. 29 on the points list, approaching the top 20 threshold needed for automatic 2027 PGA Tour promotion.</p>
          </div>

          <h2>The Raw Take</h2>
          <p>A final-round 59 requires hot putting over a 12-hole stretch, but Docherty's heroic three-birdie finish to force extra holes proves how relentless modern professional golf has become. Harris's maiden win underlines the immediate impact PGA Tour University graduates are making across professional tours.</p>
        </div>
      </article>"""

article_start_tag = "<article>"
article_end_tag = "</article>"

start_idx = template.find(article_start_tag)
end_idx = template.find(article_end_tag) + len(article_end_tag)

new_html = template[:start_idx] + new_article_content + template[end_idx:]

with open("news-2026-pinnacle-bank-championship-frankie-harris-59.html", "w") as f:
    f.write(new_html)

print("Created news-2026-pinnacle-bank-championship-frankie-harris-59.html")

# Update articles.json
with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "url": "/news-2026-pinnacle-bank-championship-frankie-harris-59",
  "title": "He Shot 59 and It Only Got Him Into a Playoff",
  "category": "KORN FERRY TOUR",
  "date": "AUG 11 2026",
  "image": "/public/frankie-harris-59-pinnacle-bank-championship-2026.webp",
  "snippet": "Frankie Harris shot a 12-under 59 to win the Pinnacle Bank Championship — but Alistair Docherty birdied his last three to force extra holes.",
  "keywords": "frankie harris 59, pinnacle bank championship 2026, korn ferry tour 59, sub 60 rounds golf, pga tour university 2026, korn ferry tour points list"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)

print("Updated articles.json")
