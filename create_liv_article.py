import re
from bs4 import BeautifulSoup
import json
import os
import datetime

# 1. CREATE HTML FILE
with open('news-2026-solheim-cup-big-names-missing.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Update Metadata
soup.title.string = "Players Get Equity \"Instead of Cash,\" Says LIV CEO | GolfRaw"
soup.find('meta', {'name': 'description'})['content'] = "LIV Golf says players will become majority owners. Its CEO then said the equity comes \"instead of cash.\" What that actually means for the league."
soup.find('link', {'rel': 'canonical'})['href'] = "https://www.golfraw.com/news-2026-liv-players-get-equity-instead-of-cash"

# Open Graph
soup.find('meta', {'property': 'og:title'})['content'] = "Players Get Equity \"Instead of Cash,\" Says LIV CEO | GolfRaw"
soup.find('meta', {'property': 'og:description'})['content'] = "LIV Golf says players will become majority owners. Its CEO then said the equity comes \"instead of cash.\" What that actually means for the league."
soup.find('meta', {'property': 'og:url'})['content'] = "https://www.golfraw.com/news-2026-liv-players-get-equity-instead-of-cash"
soup.find('meta', {'property': 'og:image'})['content'] = "https://www.golfraw.com/public/liv-golf-equity-instead-of-cash.webp"
soup.find('meta', {'property': 'og:image:alt'})['content'] = "Players Get Equity Instead of Cash, Says LIV CEO"
soup.find('meta', {'property': 'article:section'})['content'] = "LIV Golf"
soup.find('meta', {'property': 'article:tag'})['content'] = "liv golf, scott oneil, jon rahm, equity, bankruptcy, instead of cash"

# Twitter Card
soup.find('meta', {'name': 'twitter:title'})['content'] = "Players Get Equity \"Instead of Cash,\" Says LIV CEO | GolfRaw"
soup.find('meta', {'name': 'twitter:description'})['content'] = "LIV Golf says players will become majority owners. Its CEO then said the equity comes \"instead of cash.\" What that actually means for the league."
soup.find('meta', {'name': 'twitter:image'})['content'] = "https://www.golfraw.com/public/liv-golf-equity-instead-of-cash.webp"

# Structured Data
script_tag = soup.find('script', type='application/ld+json')
ld = json.loads(script_tag.string)
ld['headline'] = "Players Get Equity \"Instead of Cash,\" Says LIV CEO"
ld['description'] = "LIV Golf says players will become majority owners. Its CEO then said the equity comes \"instead of cash.\" What that actually means for the league."
ld['image'] = ["https://www.golfraw.com/public/liv-golf-equity-instead-of-cash.webp"]
ld['mainEntityOfPage'] = "https://www.golfraw.com/news-2026-liv-players-get-equity-instead-of-cash"
script_tag.string = "\n" + json.dumps(ld, indent=2) + "\n"

# Article Content
article_html = """
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="news">Latest News</a> / <span>LIV Golf</span>
        </nav>

        <header class="article-head">
          <span class="cat">NEWS · LIV GOLF</span>
          <h1>Players Get Equity "Instead of Cash," Says LIV CEO</h1>
          <p class="standfirst">Yesterday, LIV Golf announced that a new lead investor would make its players the majority equity owners of the league. Within hours, CEO Scott O'Neil clarified exactly what that mechanism is: equity "instead of cash." It reframes the entire announcement from an athlete-empowerment story into a massive debt restructuring.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>AUG 06 2026</b></span>
          </div>
        </header>

        <img src="/public/liv-golf-equity-instead-of-cash.webp" alt="LIV Golf Equity Instead of Cash" style="width: 100%; border-radius: 4px; margin-bottom: 40px;">

        <div class="article-body">
<h2>The Question Answered Out Loud</h2>
<p>In our previous coverage of Wednesday's announcement, the biggest unresolved question was whether the "majority equity" for players was a windfall arriving on top of what they were owed, or a way of converting an unpayable debt into paper.</p>

<p>We know now. O'Neil answered it himself at the Bedminster press conference, in comments carried by the AP.</p>

<p>He said many players came to LIV because it was a good opportunity to make money, and that this second bite at the apple is equity <em>instead of</em> cash.</p>

<p>Instead of. Not alongside. LIV reportedly still owes its players, Jon Rahm included, sums running into nine figures. The equity offer appears to be the primary mechanism by which a league carrying hundreds of millions in debt stops owing hundreds of millions in debt.</p>

<p>That could still be a very good deal for the players. A majority stake in a functioning league that survives is worth more than a cleared check from a league that folds. But it is fundamentally a debt restructuring wearing the language of empowerment. Anyone reading "players will own the league" as pure good news is reading the press release rather than the CEO's follow-up.</p>

<h2>The $250M Phantom Headline</h2>
<p>The gap between what was announced and what is being reported continues to widen. Bleacher Report originally headlined the announcement as LIV securing a "$250M investment"—a figure nowhere in O'Neil's statement.</p>

<p>It has since worsened. Their headline still states LIV "Secures $250M Investment." Yet, their own body text now attributes $250–300 million to Sportico and the New York Post as the <em>target</em> LIV was seeking.</p>

<p>The piece states in paragraph two that the figure is a fundraising target, but states in the headline that the money is secured. The article corrects its own headline, but the headline is what everyone sees and shares on social media.</p>

<h2>What LIV 2.0 Actually Looks Like</h2>
<p>The financial realities of the surviving league are coming into sharper focus. Multiple reports confirm that purses are facing a severe haircut.</p>

<p>The 2026 individual purse was $20 million, with $4 million paid to the winner. The proposed $10 million purse for 2027 would cut that amount by about half.</p>

<p>That is a cut of about half in prize money for the players holding the new equity.</p>

<h2>Michigan Cancelled, and a Lesson from 2022</h2>
<p>LIV Golf New York will serve as the penultimate individual event of the season, but the finale is in jeopardy. Multiple outlets now describe the Michigan team championship as reportedly cancelled, noting that preparations at the venue never actually started. While not officially confirmed dead by LIV, the weight of reporting has shifted heavily toward cancellation.</p>

<p>And for historical context: "players as owners" is not a new idea at LIV. It is just the second attempt. At launch in 2022, principal players on each team were reported to receive a 25% ownership cut of their franchises. That initial equity offer did not prevent the current financial squeeze.</p>

<div class="faq-section" style="background:var(--white); border:2px solid var(--ink); padding:24px; margin:32px 0;">
  <h2 style="margin-top:0;">Frequently Asked Questions</h2>

  <h3 style="font-size:18px; margin-top:16px;">What did Scott O'Neil mean by equity "instead of cash"?</h3>
  <p>LIV CEO Scott O'Neil clarified that the new structure making players majority owners will provide equity instead of cash payouts. This strongly indicates the move is a debt restructuring strategy to settle the hundreds of millions reportedly still owed to players.</p>

  <h3 style="font-size:18px; margin-top:16px;">Did LIV Golf secure a $250 million investment?</h3>
  <p>No investment figure has been officially confirmed or disclosed. Headlines claiming $250 million are quoting a previously reported fundraising target originating from outlets like Sportico, not a secured commitment.</p>

  <h3 style="font-size:18px; margin-top:16px;">Are LIV Golf prize purses being cut?</h3>
  <p>Yes. Reports indicate that tournament purses will drop from roughly $25–30 million down to approximately $10 million per event in the restructured league.</p>

  <h3 style="font-size:18px; margin-top:16px;">Is the LIV Golf Michigan Team Championship cancelled?</h3>
  <p>While LIV has not issued a formal cancellation, multiple outlets report the event is effectively cancelled, noting that on-site venue preparations never began.</p>
</div>

<h2>The Raw Take</h2>
<p>When an executive tells you exactly what they are doing, it is usually wise to listen to them rather than the press release.</p>

<p>"Equity instead of cash" is the most honest sentence spoken about LIV Golf's finances all year. It turns a magical story about athlete empowerment into a standard corporate restructuring. The players are trading IOUs for stock in the company that owes them. We will find out in September if the market thinks that stock is worth holding.</p>
          <div class="tag-row">
            <a href="search">LIV Golf</a>
            <a href="search">Equity</a>
            <a href="search">GOLFRAW</a>
          </div>
        </div>
"""

new_article = BeautifulSoup(article_html, 'html.parser')
soup.article.replace_with(new_article)

final_html = "<!DOCTYPE html>\n" + str(soup)
with open('news-2026-liv-players-get-equity-instead-of-cash.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

# 2. UPDATE ARTICLES.JSON
with open('articles.json', 'r', encoding='utf-8') as f:
    articles_data = json.load(f)

new_json_obj = {
    "canonical": "/news-2026-liv-players-get-equity-instead-of-cash",
    "alias_of": "",
    "slug": "news-2026-liv-players-get-equity-instead-of-cash",
    "url": "/news-2026-liv-players-get-equity-instead-of-cash",
    "title": "Players Get Equity 'Instead of Cash,' Says LIV CEO",
    "excerpt": "LIV Golf says players will become majority owners. Its CEO then said the equity comes 'instead of cash.' What that actually means for the league.",
    "category": "LIV GOLF",
    "date": "2026-08-06",
    "image": "/public/liv-golf-equity-instead-of-cash.webp",
    "category_source": "manual",
    "section": "LIV GOLF"
}
articles_data['articles'].insert(0, new_json_obj)
articles_data['count'] += 1

with open('articles.json', 'w', encoding='utf-8') as f:
    json.dump(articles_data, f, indent=2, ensure_ascii=False)
    f.write('\n')

# 3. UPDATE SEARCH.HTML
with open('search.html', 'r', encoding='utf-8') as f:
    search_html = f.read()

new_entry = """  {t:"Players Get Equity 'Instead of Cash,' Says LIV CEO", l:"/news-2026-liv-players-get-equity-instead-of-cash", img:"/public/liv-golf-equity-instead-of-cash.webp", cat:"LIV GOLF", date:"AUG 06 2026", author:"GOLFRAW Editorial", x:"LIV Golf says players will become majority owners. Its CEO then said the equity comes 'instead of cash.' What that actually means for the league.", k:"liv golf, scott oneil, jon rahm, equity, bankruptcy, instead of cash"},
"""
search_html = search_html.replace('const ARTICLES = [', 'const ARTICLES = [\n' + new_entry)
with open('search.html', 'w', encoding='utf-8') as f:
    f.write(search_html)

# 4. UPDATE NEWS.HTML and LIV-GOLF.HTML
# Read the first grid in news.html and insert the new card
card_html = f'''        <article class="news">
          <a href="/news-2026-liv-players-get-equity-instead-of-cash" style="display:block; margin-bottom:16px;">
            <img src="/public/liv-golf-equity-instead-of-cash.webp" alt="Players Get Equity 'Instead of Cash,' Says LIV CEO" style="width: 100%; border-radius: 4px;" loading="lazy">
          </a>
          <div class="cat" style="display:flex;align-items:center;gap:8px;">
            <span>LIV GOLF</span>
          </div>
          <h3><a href="/news-2026-liv-players-get-equity-instead-of-cash">Players Get Equity 'Instead of Cash,' Says LIV CEO</a></h3>
          <p>LIV Golf says players will become majority owners. Its CEO then said the equity comes 'instead of cash.' What that actually means for the league.</p>
          <div class="meta"><span>BY GOLFRAW Editorial</span><span class="mono">AUG 06 2026</span></div>
        </article>
'''

for filepath in ['news.html', 'liv-golf.html']:
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    html = html.replace('<div class="news-grid">\n', '<div class="news-grid">\n' + card_html)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
