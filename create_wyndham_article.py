import re
from bs4 import BeautifulSoup
import json
import os

# 1. CREATE HTML FILE
with open('news-2026-solheim-cup-big-names-missing.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Update Metadata
soup.title.string = "Wyndham Championship Bubble: Koivun Leads by 12 Points | GolfRaw"
soup.find('meta', {'name': 'description'})['content'] = "Jackson Koivun enters the 2026 Wyndham Championship holding the 70th FedExCup spot by just 12 points. What Sedgefield's positional layout means for the playoff bubble."
soup.find('link', {'rel': 'canonical'})['href'] = "https://www.golfraw.com/news-2026-wyndham-fedexcup-bubble-koivun"

# Open Graph
soup.find('meta', {'property': 'og:title'})['content'] = "Wyndham Championship Bubble: Koivun Leads by 12 Points | GolfRaw"
soup.find('meta', {'property': 'og:description'})['content'] = "Jackson Koivun enters the 2026 Wyndham Championship holding the 70th FedExCup spot by just 12 points. What Sedgefield's positional layout means for the playoff bubble."
soup.find('meta', {'property': 'og:url'})['content'] = "https://www.golfraw.com/news-2026-wyndham-fedexcup-bubble-koivun"
soup.find('meta', {'property': 'og:image'})['content'] = "https://www.golfraw.com/public/wyndham-fedexcup-bubble-koivun.webp"
soup.find('meta', {'property': 'og:image:alt'})['content'] = "Jackson Koivun at Wyndham Championship"
soup.find('meta', {'property': 'article:section'})['content'] = "PGA Tour"
soup.find('meta', {'property': 'article:tag'})['content'] = "wyndham championship, jackson koivun, fedexcup bubble, mac meissner, keegan bradley, pga tour, sedgefield"

# Twitter Card
soup.find('meta', {'name': 'twitter:title'})['content'] = "Wyndham Championship Bubble: Koivun Leads by 12 Points | GolfRaw"
soup.find('meta', {'name': 'twitter:description'})['content'] = "Jackson Koivun enters the 2026 Wyndham Championship holding the 70th FedExCup spot by just 12 points. What Sedgefield's positional layout means for the playoff bubble."
soup.find('meta', {'name': 'twitter:image'})['content'] = "https://www.golfraw.com/public/wyndham-fedexcup-bubble-koivun.webp"

# Structured Data
script_tag = soup.find('script', type='application/ld+json')
ld = json.loads(script_tag.string)
ld['headline'] = "A Razor-Thin Bubble at Sedgefield: 12 Points Decide a Rookie's Fate"
ld['description'] = "Jackson Koivun enters the 2026 Wyndham Championship holding the 70th FedExCup spot by just 12 points. What Sedgefield's positional layout means for the playoff bubble."
ld['image'] = ["https://www.golfraw.com/public/wyndham-fedexcup-bubble-koivun.webp"]
ld['mainEntityOfPage'] = "https://www.golfraw.com/news-2026-wyndham-fedexcup-bubble-koivun"
script_tag.string = "\n" + json.dumps(ld, indent=2) + "\n"

# Article Content
article_html = """
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="news">Latest News</a> / <span>PGA Tour</span>
        </nav>

        <header class="article-head">
          <span class="cat">NEWS · PGA TOUR</span>
          <h1>A Razor-Thin Bubble at Sedgefield: 12 Points Decide a Rookie's Fate</h1>
          <p class="standfirst">Round one of the 2026 Wyndham Championship begins today with an $8.5 million purse on the line, but the real stakes are measured in FedExCup points. For 21-year-old phenom Jackson Koivun, a 12-point margin is the only thing standing between his rookie season continuing into the playoffs or ending abruptly in North Carolina.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>AUG 06 2026</b></span>
          </div>
        </header>

        <img src="/public/wyndham-fedexcup-bubble-koivun.webp" alt="Jackson Koivun at Wyndham Championship" style="width: 100%; border-radius: 4px; margin-bottom: 40px;">

        <div class="article-body">
<div class="meta-callout" style="border-left: 4px solid #10b981; padding-left: 12px; margin: 16px 0;">
  <strong>Tournament Update:</strong> August 6, 2026 | First Round, Sedgefield Country Club
</div>

<h2>Let's Be Honest About the Drama</h2>
<p>The previews will tell you the whole week is a knife fight. It isn't, quite — the top 59 players in the standings are already mathematically safe. They cannot be caught. That is exactly why only three players from the world's top 20 turned up in Greensboro this week.</p>

<p>But where the tension does exist, it is sharper than the broad previews suggest.</p>

<p>Jackson Koivun sits 70th in the FedExCup standings, exactly 12 points ahead of the man in 71st (Mac Meissner) and 18 points ahead of the man in 72nd (Keegan Bradley). Twelve points. A single good round moves the needle more than that.</p>

<p>He is 21 years old. He won the 3M Open just two weeks ago, staring down Scottie Scheffler to do it, but failed to build any points cushion in Detroit. Andrew Putnam and Johnny Keefer are right behind him after missing the cut there, with veterans Jason Day and Bradley lurking in the same neighborhood.</p>

<p>There are about eleven spots genuinely in play this week, and the final boundary is currently being decided by a margin thinner than a single birdie.</p>

<h2>The Local Angle and a Positional Defense</h2>
<p>There is a detail that makes Koivun's defense of that 70th spot highly compelling: he tied for fifth at this exact tournament last year as an amateur. The player whose entire season hangs on this week is at the one course on Tour where he has already proved he can contend.</p>

<p>He will have to do it on a layout that neutralizes modern power. Sedgefield is a positional golf course. Betting analysts and course evaluators agree that the driver comes out less often here than usual, and reading the Bermuda greens is the true competitive edge.</p>

<p>That is a course defended by its surfaces and conditioning rather than raw yardage — which is the entire point of Sedgefield. It favors precision iron players and elite putters, setting the stage for a volatile leaderboard where anyone can catch fire.</p>

<h2>The Presidents Cup Paradox</h2>
<p>Koivun's precarious position on the bubble contrasts wildly with how he is viewed by the sport's leadership. On Tuesday, U.S. Presidents Cup captain Brandt Snedeker played a practice round with Koivun and publicly called him a "generational player."</p>

<p>Koivun is now actively in the Presidents Cup conversation while simultaneously sitting directly on the FedExCup playoff cutline. It is a strange, uniquely high-pressure pair of things for a 21-year-old rookie to be balancing at once.</p>

<h2>What They're Playing For</h2>
<p>Beyond the playoff spots, the winner at Sedgefield will take home $1.53 million from an $8.5 million overall purse. That 18 percent winner's share is standard for the Tour, but for the players ranked 60th to 80th, the prize money is entirely secondary to the points.</p>

<p>For those guys, Friday's cutline and Sunday's back nine are about survival. Twelve points.</p>

<div class="faq-section" style="background:var(--white); border:2px solid var(--ink); padding:24px; margin:32px 0;">
  <h2 style="margin-top:0;">Frequently Asked Questions</h2>

  <h3 style="font-size:18px; margin-top:16px;">What is the purse for the 2026 Wyndham Championship?</h3>
  <p>The total purse for the 2026 Wyndham Championship is $8.5 million, with the winner taking home exactly 18 percent of the total, or $1.53 million.</p>

  <h3 style="font-size:18px; margin-top:16px;">How close is the FedExCup bubble at Wyndham?</h3>
  <p>Entering the week, Jackson Koivun holds the 70th and final playoff spot by a razor-thin margin. He is just 12 points ahead of Mac Meissner (71st) and 18 points ahead of Keegan Bradley (72nd).</p>

  <h3 style="font-size:18px; margin-top:16px;">Has Jackson Koivun played Sedgefield before?</h3>
  <p>Yes. Koivun finished tied for fifth (T5) at the Wyndham Championship last year while still competing as an amateur.</p>

  <h3 style="font-size:18px; margin-top:16px;">What kind of course is Sedgefield Country Club?</h3>
  <p>Sedgefield is considered a positional layout. Players use their drivers less frequently than at typical Tour stops, placing a premium on approach play and putting on its Bermuda grass greens.</p>
</div>

<h2>The Raw Take</h2>
<p>We spend all year analyzing 7,500-yard bomber tracks and designated event payouts, but the best drama in golf is often a 21-year-old trying to protect a 12-point lead on a par-70 course where the driver stays in the bag.</p>

<p>The top 59 guys are safe. They are already booking flights to Memphis. For the dozen guys below them, Sedgefield is a knife fight where every missed 10-footer on a Bermuda green could mean the end of the season.</p>
          <div class="tag-row">
            <a href="search">Wyndham Championship</a>
            <a href="search">Jackson Koivun</a>
            <a href="search">PGA Tour</a>
          </div>
        </div>
"""

new_article = BeautifulSoup(article_html, 'html.parser')
soup.article.replace_with(new_article)

final_html = "<!DOCTYPE html>\n" + str(soup)
with open('news-2026-wyndham-fedexcup-bubble-koivun.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

# 2. UPDATE ARTICLES.JSON
with open('articles.json', 'r', encoding='utf-8') as f:
    articles_data = json.load(f)

new_json_obj = {
    "canonical": "/news-2026-wyndham-fedexcup-bubble-koivun",
    "alias_of": "",
    "slug": "news-2026-wyndham-fedexcup-bubble-koivun",
    "url": "/news-2026-wyndham-fedexcup-bubble-koivun",
    "title": "A Razor-Thin Bubble at Sedgefield: 12 Points Decide a Rookie's Fate",
    "excerpt": "Jackson Koivun enters the 2026 Wyndham Championship holding the 70th FedExCup spot by just 12 points. What Sedgefield's positional layout means for the playoff bubble.",
    "category": "PGA TOUR",
    "date": "2026-08-06",
    "image": "/public/wyndham-fedexcup-bubble-koivun.webp",
    "category_source": "manual",
    "section": "PGA TOUR"
}
articles_data['articles'].insert(0, new_json_obj)
articles_data['count'] += 1

with open('articles.json', 'w', encoding='utf-8') as f:
    json.dump(articles_data, f, indent=2, ensure_ascii=False)
    f.write('\n')

# 3. UPDATE SEARCH.HTML
with open('search.html', 'r', encoding='utf-8') as f:
    search_html = f.read()

new_entry = """  {t:"A Razor-Thin Bubble at Sedgefield: 12 Points Decide a Rookie's Fate", l:"/news-2026-wyndham-fedexcup-bubble-koivun", img:"/public/wyndham-fedexcup-bubble-koivun.webp", cat:"PGA TOUR", date:"AUG 06 2026", author:"GOLFRAW Editorial", x:"Jackson Koivun enters the 2026 Wyndham Championship holding the 70th FedExCup spot by just 12 points. What Sedgefield's positional layout means for the playoff bubble.", k:"wyndham championship, jackson koivun, fedexcup bubble, mac meissner, keegan bradley, pga tour, sedgefield"},
"""
search_html = search_html.replace('const ARTICLES = [', 'const ARTICLES = [\n' + new_entry)
with open('search.html', 'w', encoding='utf-8') as f:
    f.write(search_html)

# 4. UPDATE NEWS.HTML
card_html_news = f'''        <article class="news">
          <a href="/news-2026-wyndham-fedexcup-bubble-koivun" style="display:block; margin-bottom:16px;">
            <img src="/public/wyndham-fedexcup-bubble-koivun.webp" alt="A Razor-Thin Bubble at Sedgefield: 12 Points Decide a Rookie's Fate" style="width: 100%; border-radius: 4px;" loading="lazy">
          </a>
          <div class="cat" style="display:flex;align-items:center;gap:8px;">
            <span style="background:var(--fairway);">PGA TOUR</span>
          </div>
          <h3><a href="/news-2026-wyndham-fedexcup-bubble-koivun">A Razor-Thin Bubble at Sedgefield: 12 Points Decide a Rookie's Fate</a></h3>
          <p>Jackson Koivun enters the 2026 Wyndham Championship holding the 70th FedExCup spot by just 12 points. What Sedgefield's positional layout means for the playoff bubble.</p>
          <div class="meta"><span>BY GOLFRAW Editorial</span><span class="mono">AUG 06 2026</span></div>
        </article>
'''
with open('news.html', 'r', encoding='utf-8') as f:
    html_news = f.read()
html_news = html_news.replace('<div class="news-grid">\n', '<div class="news-grid">\n' + card_html_news)
with open('news.html', 'w', encoding='utf-8') as f:
    f.write(html_news)

# 5. UPDATE PGA-TOUR.HTML
card_html_pga = f'''        <a class="guide-card" href="/news-2026-wyndham-fedexcup-bubble-koivun">
          <img width="1672" height="941" src="/public/wyndham-fedexcup-bubble-koivun.webp" alt="A Razor-Thin Bubble at Sedgefield: 12 Points Decide a Rookie's Fate" class="card-thumb" loading="lazy">
          <div class="card-body">
            <div class="badge-row">
              <span class="badge badge-red">PGA TOUR</span>
              <span class="badge badge-green">New</span>
            </div>
            <h3>A Razor-Thin Bubble at Sedgefield: 12 Points Decide a Rookie's Fate</h3>
            <p>Jackson Koivun enters the 2026 Wyndham Championship holding the 70th FedExCup spot by just 12 points. What Sedgefield's positional layout means for the playoff bubble.</p>
            <div class="card-meta">
              <span class="author">BY GOLFRAW Editorial | AUG 06 2026</span>
            </div>
          </div>
        </a>
'''
with open('pga-tour.html', 'r', encoding='utf-8') as f:
    html_pga = f.read()
html_pga = html_pga.replace('<div class="guide-grid">\n', '<div class="guide-grid">\n' + card_html_pga)
with open('pga-tour.html', 'w', encoding='utf-8') as f:
    f.write(html_pga)

