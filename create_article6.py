import json
import os

template_path = "article-template.html"
with open(template_path, "r") as f:
    template = f.read()

# Replace head metadata
template = template.replace(
    "<title>Oakmont US Open Setup: How the USGA Broke the | GOLFRAW</title>",
    "<title>He Won at 25 Under. This Week Is the Opposite. | GolfRaw</title>"
)
template = template.replace(
    '<meta name="description" content="Average score 74.8, stimp at 15. We walked Oakmont&#x27;s US Open setup with two tour caddies to find out which pins cross the line — and who secretly loves it.">',
    '<meta name="description" content="Koivun won the 3M Open at 25 under. TPC Southwind has seven par 4s over 450 yards and water on 11 holes. The first real test of a 21-year-old\'s season.">'
)
template = template.replace(
    '<link rel="canonical" href="https://www.golfraw.com/article-template">',
    '<link rel="canonical" href="https://www.golfraw.com/news-2026-jackson-koivun-tpc-southwind-fedex-st-jude">'
)
template = template.replace(
    '<meta property="og:title" content="Oakmont US Open Setup: How the USGA Broke the | GOLFRAW">',
    '<meta property="og:title" content="He Won at 25 Under. This Week Is the Opposite. | GolfRaw">'
)
template = template.replace(
    '<meta property="og:description" content="Average score 74.8, stimp at 15. We walked Oakmont&#x27;s US Open setup with two tour caddies to find out which pins cross the line — and who secretly loves it.">',
    '<meta property="og:description" content="Koivun won the 3M Open at 25 under. TPC Southwind has seven par 4s over 450 yards and water on 11 holes. The first real test of a 21-year-old\'s season.">'
)
template = template.replace(
    '<meta property="og:url" content="https://www.golfraw.com/article-template">',
    '<meta property="og:url" content="https://www.golfraw.com/news-2026-jackson-koivun-tpc-southwind-fedex-st-jude">'
)
template = template.replace(
    '<meta property="og:image" content="https://www.golfraw.com/public/raw-golf-practice.webp">',
    '<meta property="og:image" content="https://www.golfraw.com/public/jackson-koivun-tpc-southwind-2026.webp">'
)
template = template.replace(
    '<meta name="twitter:title" content="Oakmont US Open Setup: How the USGA Broke the | GOLFRAW">',
    '<meta name="twitter:title" content="He Won at 25 Under. This Week Is the Opposite. | GolfRaw">'
)
template = template.replace(
    '<meta name="twitter:description" content="Average score 74.8, stimp at 15. We walked Oakmont&#x27;s US Open setup with two tour caddies to find out which pins cross the line — and who secretly loves it.">',
    '<meta name="twitter:description" content="Koivun won the 3M Open at 25 under. TPC Southwind has seven par 4s over 450 yards and water on 11 holes. The first real test of a 21-year-old\'s season.">'
)
template = template.replace(
    '<meta name="twitter:image" content="https://www.golfraw.com/public/raw-golf-practice.webp">',
    '<meta name="twitter:image" content="https://www.golfraw.com/public/jackson-koivun-tpc-southwind-2026.webp">'
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
    '"headline": "He Won at 25 Under. This Week Is the Opposite.",'
)
template = template.replace(
    '"description": "Average score 74.8, greens at 15 on the stimp. Two tour caddies walked us through the US Open setup built to break the field.",',
    '"description": "Koivun won the 3M Open at 25 under. TPC Southwind has seven par 4s over 450 yards and water on 11 holes. The first real test of a 21-year-old\'s season.",'
)
template = template.replace(
    '"https://www.golfraw.com/public/img/oakmont-2026-setup-og.jpg"',
    '"https://www.golfraw.com/public/jackson-koivun-tpc-southwind-2026.webp"'
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
    '"mainEntityOfPage": "https://www.golfraw.com/news-2026-jackson-koivun-tpc-southwind-fedex-st-jude"'
)

new_article_content = """<article>
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/#news">News</a> / <span>PGA Tour</span>
        </nav>

        <header class="article-head">
          <span class="cat">News · PGA Tour</span>
          <h1>Koivun Won at 25 Under. Southwind Is the Opposite of That.</h1>
          <p class="standfirst">Jackson Koivun's maiden PGA Tour victory at the 3M Open came at a staggering 25 under par, setting a tournament record at TPC Twin Cities and beating the world number one by three shots. This week at TPC Southwind for the FedEx St. Jude Championship, he faces a course with <a href="/news-2026-fedex-st-jude-championship-tpc-southwind-demotion">seven par fours over 450 yards</a>, water in play on eleven holes, and only two par fives.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>TUE 11 AUG 2026</b></span>
            <span><b>4 MIN READ</b></span>
          </div>
        </header>

        <div class="meta-callout" style="border-left: 4px solid #10b981; padding-left: 12px; margin: 16px 0;">
          <strong>FedExCup Playoff Player Focus:</strong> August 11, 2026 | Jackson Koivun at TPC Southwind
        </div>

        <figure class="lead-img">
            <img src="/public/jackson-koivun-tpc-southwind-2026.webp" alt="Jackson Koivun TPC Southwind FedEx St Jude 2026" />
        </figure>
        <figcaption>KOIVUN SECURED THE 70TH AND FINAL SPOT IN THE FEDEXCUP PLAYOFFS AT THE WYNDHAM CHAMPIONSHIP.</figcaption>

        <div class="article-body">
          <h2>How Koivun Clung to 70th in the Standings</h2>
          <p>Koivun opened with a 67 at the Wyndham Championship, posted a Saturday 66 to move into the top 15, and closed with a 71. He held 70th position—the final qualifying spot for the FedExCup Playoffs—by just 12 points, admitting afterwards that he closely monitored the live leaderboard throughout Sunday afternoon.</p>

          <h2>The NCAA Record-Setting Resume</h2>
          <p>While <a href="/news-2026-who-is-jackson-koivun-explained">we've covered his background in full elsewhere</a>, his collegiate credentials at Auburn remain historic: 11 individual victories, 56 weeks as world amateur number one, three consecutive SEC Player of the Year awards, and two sweeps of the Haskins, Hogan, and Nicklaus awards.</p>

          <p>After earning his PGA Tour card through the Accelerated program, he turned professional in June and won on Tour just 24 days later—becoming the youngest American to win a PGA Tour event by more than one shot in 94 years.</p>

          <h2>Why TPC Southwind Presents a Radically Different Examination</h2>
          <p>Winning at 25 under proves a player can capitalize on soft scoring conditions. Southwind offers no such comfort. Unlike Detroit Golf Club—which yielded <a href="/news-2026-fedex-st-jude-championship-tpc-southwind-demotion">three rounds of 61</a> in a single week—Southwind punishes minor errors with narrow Zoysia fairways, thick Bermuda rough, and punishing water hazards.</p>

          <h2>What Is at Stake in Memphis</h2>
          <p>Entering the week ranked 70th, Koivun needs to climb 20 spots to reach the Top 50, which guarantees entry into all eight 2027 Signature Events and the BMW Championship at Bellerive. Quadrupled playoff points provide a realistic path, but leave zero margin for error across four rounds with no cut.</p>

          <div class="faq-section">
            <h2>Frequently Asked Questions</h2>

            <h3>Is Jackson Koivun in the FedExCup Playoffs?</h3>
            <p>Yes. Koivun finished 70th in the FedExCup standings following the Wyndham Championship, securing the final spot for the FedEx St. Jude Championship.</p>

            <h3>What was Jackson Koivun's winning score at the 3M Open?</h3>
            <p>He won at 25-under 259, establishing a TPC Twin Cities tournament record and defeating Scottie Scheffler by three strokes.</p>

            <h3>What does Koivun need to accomplish at TPC Southwind?</h3>
            <p>He must advance into the top 50 in FedExCup points to qualify for the BMW Championship and all eight 2027 Signature Events.</p>

            <h3>What makes TPC Southwind difficult compared to TPC Twin Cities?</h3>
            <p>TPC Southwind features a par 70 setup with seven par 4s over 450 yards, only two par 5s, grabby Zoysia fairways, and water hazards on 11 holes.</p>
          </div>

          <h2>The Raw Take</h2>
          <p>Following up a 25-under victory with modest finishes in Detroit and Greensboro isn't a slump—it's the natural baseline of a 21-year-old rookie navigating tour life. TPC Southwind will provide the first true gauge of how Koivun handles a course designed to penalize inexperience rather than reward birdies.</p>
        </div>
      </article>"""

article_start_tag = "<article>"
article_end_tag = "</article>"

start_idx = template.find(article_start_tag)
end_idx = template.find(article_end_tag) + len(article_end_tag)

new_html = template[:start_idx] + new_article_content + template[end_idx:]

with open("news-2026-jackson-koivun-tpc-southwind-fedex-st-jude.html", "w") as f:
    f.write(new_html)

print("Created news-2026-jackson-koivun-tpc-southwind-fedex-st-jude.html")

# Update articles.json
with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "url": "/news-2026-jackson-koivun-tpc-southwind-fedex-st-jude",
  "title": "He Won at 25 Under. This Week Is the Opposite.",
  "category": "PGA TOUR",
  "date": "AUG 11 2026",
  "image": "/public/jackson-koivun-tpc-southwind-2026.webp",
  "snippet": "Koivun won the 3M Open at 25 under. TPC Southwind has seven par 4s over 450 yards and water on 11 holes. The first real test of a 21-year-old's season.",
  "keywords": "jackson koivun fedex st jude, koivun playoffs, tpc southwind course difficulty, jackson koivun 3m open, fedexcup top 50 signature events"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)

print("Updated articles.json")

# Update /news-2026-who-is-jackson-koivun-explained.html
file_to_update = "news-2026-who-is-jackson-koivun-explained.html"
if os.path.exists(file_to_update):
    with open(file_to_update, "r") as f:
        content = f.read()
    
    update_html = '<p><em>Update (August 2026): Read our breakdown of <a href="/news-2026-jackson-koivun-tpc-southwind-fedex-st-jude">Koivun\'s playoff test at TPC Southwind</a>.</em></p>'
    
    # insert it right before the last closing </div> that wraps the article body, 
    # or just before </article>
    if '<div class="faq-section">' in content:
        # let's place it before the faq section just to be safe or right before </article>
        # but the prompt says: near the end.
        pass
        
    # the easiest way is to place it before </article> but inside article-body if we can.
    article_body_end = content.rfind('</div>\n      </article>')
    if article_body_end != -1:
        new_content = content[:article_body_end] + update_html + '\n        </div>\n      </article>' + content[article_body_end+len('</div>\n      </article>'):]
        with open(file_to_update, "w") as f:
            f.write(new_content)
        print("Updated", file_to_update)
    else:
        # Try finding just </article>
        end_idx = content.rfind('</article>')
        if end_idx != -1:
            new_content = content[:end_idx] + update_html + '\n      </article>' + content[end_idx+len('</article>'):]
            with open(file_to_update, "w") as f:
                f.write(new_content)
            print("Updated", file_to_update)
        else:
            print("Could not find </article> tag in", file_to_update)
else:
    print(file_to_update, "does not exist")
