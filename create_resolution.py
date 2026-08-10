import json
from bs4 import BeautifulSoup

# 1. Create HTML file
with open('/Users/adnan/Desktop/golf/article-template.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

soup.title.string = "One Player In, One Out. The Rest Ran Out of Season. | GolfRaw"
soup.find('meta', {'name': 'description'})['content'] = "Michael Brennan won and jumped to 47th. Steven Fisk missed the cut and fell to 71st. Koepka, Day, Bradley and Finau are all out. The final FedExCup 70."
soup.find('link', {'rel': 'canonical'})['href'] = "https://www.golfraw.com/news-2026-wyndham-championship-brennan-fedexcup-bubble-resolution"

soup.find('meta', {'property': 'og:title'})['content'] = "One Player In, One Out. The Rest Ran Out of Season."
soup.find('meta', {'property': 'og:description'})['content'] = "Michael Brennan won and jumped to 47th. Steven Fisk missed the cut and fell to 71st. Koepka, Day, Bradley and Finau are all out. The final FedExCup 70."
soup.find('meta', {'property': 'og:url'})['content'] = "https://www.golfraw.com/news-2026-wyndham-championship-brennan-fedexcup-bubble-resolution"
soup.find('meta', {'property': 'og:image'})['content'] = "https://www.golfraw.com/public/michael-brennan-wyndham-championship-2026.webp"
soup.find('meta', {'property': 'og:image:alt'})['content'] = "Michael Brennan Wyndham Championship Winner 2026"
soup.find('meta', {'property': 'article:section'})['content'] = "PGA Tour"
soup.find('meta', {'property': 'article:tag'})['content'] = "fedexcup playoffs 2026 field, who made the fedexcup playoffs, jackson koivun bubble, brooks koepka fedexcup, jason day playoff streak, fedex st jude championship field"

soup.find('meta', {'name': 'twitter:title'})['content'] = "One Player In, One Out. The Rest Ran Out of Season."
soup.find('meta', {'name': 'twitter:description'})['content'] = "Michael Brennan won and jumped to 47th. Steven Fisk missed the cut and fell to 71st. Koepka, Day, Bradley and Finau are all out. The final FedExCup 70."
soup.find('meta', {'name': 'twitter:image'})['content'] = "https://www.golfraw.com/public/michael-brennan-wyndham-championship-2026.webp"

script_tag = soup.find('script', type='application/ld+json')
ld = json.loads(script_tag.string)
ld['headline'] = "One Player Got In. One Player Got Out. Everybody Else Just Ran Out of Season."
ld['description'] = "Michael Brennan won and jumped to 47th. Steven Fisk missed the cut and fell to 71st. Koepka, Day, Bradley and Finau are all out. The final FedExCup 70."
ld['image'] = ["https://www.golfraw.com/public/michael-brennan-wyndham-championship-2026.webp"]
ld['mainEntityOfPage'] = "https://www.golfraw.com/news-2026-wyndham-championship-brennan-fedexcup-bubble-resolution"
script_tag.string = "\n" + json.dumps(ld, indent=2) + "\n"

# Verify robots meta
robots_meta = soup.find('meta', {'name': 'robots'})
if robots_meta:
    robots_meta['content'] = "index, follow, max-image-preview:large"
else:
    new_tag = soup.new_tag("meta", attrs={"name": "robots", "content": "index, follow, max-image-preview:large"})
    soup.head.append(new_tag)

article_html = """
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/news">Latest News</a> / <span>PGA Tour</span>
        </nav>

        <header class="article-head">
          <span class="cat">PGA TOUR</span>
          <h1>One Player Got In. One Player Got Out. Everybody Else Just Ran Out of Season.</h1>
          <p class="standfirst">Michael Brennan won the Wyndham Championship by three shots on Sunday and moved from 105th in the FedExCup standings to 47th. He is the only player in the entire field who played his way into the playoffs. Steven Fisk began the week 69th, missed the cut at Sedgefield, and finished 71st. He is the only player who fell out.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>AUG 10 2026</b></span>
          </div>
        </header>

        <figure class="lead-img">
          <img src="/public/michael-brennan-wyndham-championship-2026.webp" alt="Michael Brennan Wyndham Championship Winner 2026" />
        </figure>

        <div class="article-body">
          <div class="meta-callout" style="border-left: 4px solid #10b981; padding-left: 12px; margin: 16px 0;">
            <strong>FedExCup Playoffs Resolution:</strong> August 10, 2026 | Wyndham Championship Final Standings
          </div>

          <h2>Koivun Held the Bubble and Didn't Know It Until the Last Putt</h2>
          <p>Jackson Koivun arrived in Greensboro 70th—the last man in—and left in exactly the same position. The 21-year-old from Auburn turned professional after finishing tied 23rd as an amateur at the U.S. Open. He has reached the FedExCup Playoffs in just five starts as a professional.</p>

          <p>His week was a masterclass in doing enough: making the cut by two shots, firing a Saturday 66 to climb into the top fifteen, then carding a 71 on Sunday while keeping a close eye on the leaderboard. Had Beau Hossler won the tournament, Koivun would have been bumped out; Hossler's failure to convert left Koivun holding the final postseason ticket.</p>

          <h2>What Happened to the Big Names on the Bubble</h2>
          <p>The final regular season week proved ruthless for established Tour veterans whose streaks and playoff plans were cut short:</p>

          <ul>
            <li><strong>Brooks Koepka (86th):</strong> Needed a solo fourth; missed the postseason in his first year back from LIV Golf after surrendering bonus grants and withdrawing from Detroit with a hand injury.</li>
            <li><strong>Jason Day (75th):</strong> Missed the cut after shooting 73 on Friday, ending a 19-consecutive-season playoff streak—the longest active run on Tour.</li>
            <li><strong>Keegan Bradley (73rd):</strong> Made the cut on the number but fell short of the needed T38 finish, ending his 15-year playoff streak.</li>
            <li><strong>Tony Finau (89th):</strong> Needed a T3 finish to extend his 11-year postseason run, but couldn't secure the result required.</li>
          </ul>

          <h2>Michael Brennan's Sudden Ascent</h2>
          <p>Needing at least a top-two finish to crash the top 70, 24-year-old Michael Brennan won outright by three strokes. The victory represents his second PGA Tour title, following his 2025 Bank of Utah Championship win on a sponsor invitation. Coming off a second-place finish at the Rocket Classic eight days ago, Brennan jumped 58 spots directly into 47th position.</p>

          <h2>What Reaching the Top 70 Actually Secures</h2>
          <p>Advancing into the FedExCup Playoffs provides substantial long-term status:</p>

          <ul>
            <li><strong>Top 70:</strong> Guarantees full PGA Tour membership and entry into the Players Championship for 2027.</li>
            <li><strong>Top 50 (after Memphis):</strong> Qualifies players for all eight elevated Signature Events in 2027.</li>
            <li><strong>Top 30 (after BMW):</strong> Earns a two-year Tour exemption plus spots at the Masters and U.S. Open.</li>
          </ul>

          <h2>Looking Ahead to Memphis and Beyond</h2>
          <p>The playoffs kick off at the FedEx St. Jude Championship at TPC Southwind in Memphis (August 13–16) with 69 players competing after Daniel Berger (ranked 60th) opted not to enter. The postseason continues at the BMW Championship at Bellerive Country Club (August 20–23) for the Top 50, concluding at the Tour Championship at East Lake in Atlanta (August 27–30) for the final Top 30.</p>

          <div class="faq-section" style="background:var(--white); border:2px solid var(--ink); padding:24px; margin:32px 0;">
            <h2 style="margin-top:0;">Frequently Asked Questions</h2>

            <h3 style="font-size:18px; margin-top:16px;">Who made the 2026 FedExCup Playoffs?</h3>
            <p>The top 70 players in FedExCup points following the Wyndham Championship qualified. Michael Brennan was the lone player to crash the field (jumping from 105th to 47th), while Steven Fisk was the only player dropped (falling from 69th to 71st).</p>

            <h3 style="font-size:18px; margin-top:16px;">Who was the FedExCup bubble boy at 70th?</h3>
            <p>Jackson Koivun held 70th position through all four rounds, securing the final spot in just his fifth start as a professional.</p>

            <h3 style="font-size:18px; margin-top:16px;">Did Brooks Koepka make the FedExCup Playoffs?</h3>
            <p>No, Koepka finished outside the top 70 and will not participate in the 2026 postseason.</p>

            <h3 style="font-size:18px; margin-top:16px;">Whose long playoff streaks came to an end at Sedgefield?</h3>
            <p>Jason Day (19 straight seasons), Keegan Bradley (15 straight seasons), and Tony Finau (11 straight seasons) all missed the top 70 cutoff.</p>
          </div>

          <h2>The Raw Take</h2>
          <p>Marginal shifts dictate entire PGA Tour seasons. While four veterans with 54 combined playoff appearances watched their runs end on Friday and Sunday, a 24-year-old winner and a 21-year-old rookie captured the narrative. In elite professional golf, executing precisely to the requirement is often the most critical skill on the card.</p>
          
          <div class="tag-row" style="margin-top: 32px;">
            <a href="/search">FedExCup Playoffs</a>
            <a href="/search">Michael Brennan</a>
            <a href="/search">Jackson Koivun</a>
            <a href="/search">PGA Tour</a>
          </div>
        </div>
"""

new_article = BeautifulSoup(article_html, 'html.parser')
soup.article.replace_with(new_article)

final_html = "<!DOCTYPE html>\n" + str(soup)
with open('/Users/adnan/Desktop/golf/news-2026-wyndham-championship-brennan-fedexcup-bubble-resolution.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

# Update articles.json
with open('/Users/adnan/Desktop/golf/articles.json', 'r', encoding='utf-8') as f:
    articles_data = json.load(f)

new_json_obj = {
    "url": "/news-2026-wyndham-championship-brennan-fedexcup-bubble-resolution",
    "title": "One Player In, One Out. The Rest Ran Out of Season.",
    "category": "PGA TOUR",
    "date": "AUG 10 2026",
    "image": "/public/michael-brennan-wyndham-championship-2026.webp",
    "snippet": "Michael Brennan won and jumped to 47th. Steven Fisk missed the cut and fell to 71st. Koepka, Day, Bradley and Finau are all out. The final FedExCup 70.",
    "keywords": "fedexcup playoffs 2026 field, who made the fedexcup playoffs, jackson koivun bubble, brooks koepka fedexcup, jason day playoff streak, fedex st jude championship field"
}

articles_data['articles'].insert(0, new_json_obj)
articles_data['count'] += 1

with open('/Users/adnan/Desktop/golf/articles.json', 'w', encoding='utf-8') as f:
    json.dump(articles_data, f, indent=2, ensure_ascii=False)
    f.write('\n')
