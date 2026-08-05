import re
from bs4 import BeautifulSoup
import json
import os

with open('news-2026-golf-deals-means-travel.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Update Metadata
soup.title.string = "7-Wood vs 3-Iron: What Aussie Golfers Actually Search | GolfRaw"
soup.find('meta', {'name': 'description'})['content'] = "Australians search for a 7-wood three times more than a 3-iron. The loft numbers, the one downside nobody mentions, and why the club has three names."
soup.find('link', {'rel': 'canonical'})['href'] = "https://www.golfraw.com/news-2026-7-wood-vs-3-iron-australian-golfers"

# Open Graph
soup.find('meta', {'property': 'og:title'})['content'] = "7-Wood vs 3-Iron: What Aussie Golfers Actually Search | GolfRaw"
soup.find('meta', {'property': 'og:description'})['content'] = "Australians search for a 7-wood three times more than a 3-iron. The loft numbers, the one downside nobody mentions, and why the club has three names."
soup.find('meta', {'property': 'og:url'})['content'] = "https://www.golfraw.com/news-2026-7-wood-vs-3-iron-australian-golfers"
soup.find('meta', {'property': 'og:image'})['content'] = "https://www.golfraw.com/public/7-wood-vs-3-iron-australian-golfers.webp"
soup.find('meta', {'property': 'og:image:alt'})['content'] = "Australians Search for a 7-Wood Three Times More Than a 3-Iron. The Bag Setup Rules Haven't Caught Up."
soup.find('meta', {'property': 'article:section'})['content'] = "Guides"
soup.find('meta', {'property': 'article:tag'})['content'] = "Golf Clubs, 7 Wood"

# Twitter Card
soup.find('meta', {'name': 'twitter:title'})['content'] = "7-Wood vs 3-Iron: What Aussie Golfers Actually Search | GolfRaw"
soup.find('meta', {'name': 'twitter:description'})['content'] = "Australians search for a 7-wood three times more than a 3-iron. The loft numbers, the one downside nobody mentions, and why the club has three names."
soup.find('meta', {'name': 'twitter:image'})['content'] = "https://www.golfraw.com/public/7-wood-vs-3-iron-australian-golfers.webp"

# Structured Data
script_tag = soup.find('script', type='application/ld+json')
ld = json.loads(script_tag.string)
ld['headline'] = "Australians Search for a 7-Wood Three Times More Than a 3-Iron. The Bag Setup Rules Haven't Caught Up."
ld['description'] = "Australians search for a 7-wood three times more than a 3-iron. The loft numbers, the one downside nobody mentions, and why the club has three names."
ld['image'] = ["https://www.golfraw.com/public/7-wood-vs-3-iron-australian-golfers.webp"]
ld['mainEntityOfPage'] = "https://www.golfraw.com/news-2026-7-wood-vs-3-iron-australian-golfers"
script_tag.string = "\n" + json.dumps(ld, indent=2) + "\n"

# Article Content
article_html = """
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="guides">Guides</a> / <span>Equipment</span>
        </nav>

        <header class="article-head">
          <span class="cat">GUIDES</span>
          <h1>Australians Search for a 7-Wood Three Times More Than a 3-Iron. The Bag Setup Rules Haven't Caught Up.</h1>
          <p class="standfirst">Pull up what Australian golfers actually type into Google and something obvious falls out: "Golf club 7 wood" gets roughly 880 searches a month, while "Golf club 3 iron" gets about 260. Add up all high-lofted woods (5, 7, 9, 11) and searches reach ~1,550/mo, dwarfing long irons (1, 2, 3) at ~640/mo. Here is what the data, the physics, and the 2026 Masters champion reveal about modern club selection.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>AUG 05 2026</b></span>
          </div>
        </header>

        <img src="/public/7-wood-vs-3-iron-australian-golfers.webp" alt="7 Wood vs 3 Iron" style="width: 100%; border-radius: 4px; margin-bottom: 40px;">

        <div class="article-body">
<div class="meta-callout" style="border-left: 4px solid #10b981; padding-left: 12px; margin: 16px 0;">
  <strong>Verified & Updated:</strong> August 5, 2026 | Australian Search Keyword Dataset & Golf Australia Participation Data
</div>

<h2>The Clubs Have Three Names and That's the Giveaway</h2>
<p>Here's the detail that made me look twice: the same category of club shows up in Australian search under three different words. Utility club. Rescue club. Recovery club. All three are real search terms with real volume.</p>

<p>Utility. Rescue. Recovery.</p>

<p>Nobody needed three euphemisms for a sand wedge. These names exist because the club's actual selling point — it's easier to hit than the thing a proper golfer is supposed to use — isn't something anyone wants printed on the sole.</p>

<p>Worth noting: "utility club golf" carries the highest cost-per-click in the entire dataset I looked at, on very modest volume. Somebody is paying well above the odds to reach people asking that question.</p>

<h2>What the Club Actually Does</h2>
<p>A 7-wood typically carries 20 to 23 degrees of loft, most commonly 21. That slots it into the fairway wood progression: 15 degrees for a 3-wood, 18 for a 5-wood, 21 for a 7-wood.</p>

<p>That loft is roughly what you'd find on a 3-iron or 4-iron, depending on the set. Which is exactly the point — same loft, completely different club.</p>

<p>Marty Jertson, VP of Fit and Innovation at PING, describes the mechanism plainly: fairway woods spin more, peak higher, and come down at a steeper angle. That's not marketing, it's geometry. A wide sole and a low centre of gravity get the ball up; a thin-faced long iron demands you do that work yourself with a perfect strike.</p>

<p>The practical version: on a long par 3 with trouble short, a 4-iron might need one of your best swings of the day just to carry it and hold the green. A well-fitted 7-wood covers similar ground and lands softer, stopping instead of releasing through the back.</p>

<p>Carry distances typically land somewhere in the 180 to 200 yard range, though swing speed and strike quality move that figure more than the club itself.</p>

<h2>The Permission Slip</h2>
<p>If you want evidence that this isn't a beginner's compromise, it's not hard to find.</p>

<p>Rory McIlroy won the 2026 Masters in April carrying a 21-degree Ping G430 Max 7-wood. Not in the bag as a novelty—in the bag of the man who won the tournament.</p>

<p>One widely syndicated article claims 40 of the 91 players in that field carried a 7-wood. I went looking to verify that specific number and couldn't confirm it independently — it appears in one piece of reporting and its syndicated copies. The field size of 91 checks out, and McIlroy's club checks out. Treat the 40 as one outlet's count rather than an established fact.</p>

<p>The direction it points is corroborated regardless. High-lofted woods have gone from a club associated with slower swing speeds to something you see in elite bags.</p>

<h2>Now the Part Almost Nobody Tells You</h2>
<p>The 7-wood is not a universal upgrade, and I found exactly one source willing to say so — a retailer that sells them.</p>

<p>If you have a genuinely fast swing, the extra height and spin can work against you. The ball balloons. Into an Australian coastal breeze, that's not a soft landing, it's a shot that goes nowhere and comes back at you.</p>

<p>The long iron still wins in wind, because a low flight is the whole reason it exists. If you play links-style courses, exposed layouts, or anywhere the wind is a permanent feature rather than an occasional inconvenience, the calculation genuinely changes.</p>

<p>The honest version is this: for most recreational golfers, a high-lofted wood is easier to hit than the long iron it replaces. For a minority with fast swings playing in wind, it isn't. Which of those you are is a fitting question, and the search data suggests Australians already know it — "club golf fitting" and "golf club fitting near me" carry costs-per-click roughly ten times the equipment terms around them.</p>

<h2>Who This Is Actually For</h2>
<p>Golf Australia's own participation report, published in December 2025, contains a number worth sitting with.</p>

<p>More than four million Australian Australia adults played golf in 2024/25. Of those, 1.8 million play on-course golf regularly without belonging to a club. Around a quarter of a million of them play at least once a month.</p>

<p>Social memberships have been growing at roughly 10.7% a year over five years, against 2.8% for traditional club membership. Golf Australia published these figures while launching its own flexible handicap product, so read them with that in mind — but the shape of it holds.</p>

<p>That 1.8 million is the group being ignored by most equipment content. They're not carrying a 3-iron because a club captain expects it. They have no captain. There is genuinely nothing stopping them putting whatever works in the bag, and the search data suggests they've figured that out well ahead of the advice.</p>

<h2>One More Thing the Data Showed</h2>
<p>The question "what are golf club distances" gets around 480 searches a month on Google in Australia.</p>

<p>The same question on TikTok gets around 22,200.</p>

<p>That's a factor of roughly 46, and it reframes what this content should look like. Australians aren't reading about club distances. They're watching them. A distance chart buried in an article is the wrong format for where the question is actually being asked.</p>

<h2>What I'd Actually Do</h2>
<ol>
  <li><strong>Count what you don't use:</strong> If you have a 3-iron or 4-iron and can't remember the last three times you hit one well, that's your answer.</li>
  <li><strong>Get on a launch monitor before buying:</strong> The whole argument rests on your launch and descent angle. Guessing defeats the point, and fitting is the one part worth paying for.</li>
  <li><strong>Check your wind before your ego:</strong> Exposed coastal course in a permanent breeze? The long iron case is real. Sheltered parkland? It isn't.</li>
  <li><strong>Buy it used first:</strong> Searches for used and second-hand clubs in Australia run well ahead of searches for full new sets (~7,500/mo combined for used vs. 5,400 for sets). Test the concept for a fraction of the cost.</li>
</ol>

<h2>Honest Caveats</h2>
<p>The search figures are rounded bands from a single keyword tool, so the ratios here are directional, not exact. I found no Australian sales data to confirm that search interest converts into purchases, and no peer-reviewed research on amateur club selection exists that I could locate.</p>

<p>One thing worth flagging about this corner of the internet: researching this, I found a page ranking well with three named golf "experts" and their quotes, hosted on the website of a roof truss manufacturer. I couldn't verify that any of those three people exist. If you read something confident about club selection, check whose site it's on.</p>

<div class="faq-section" style="background:var(--white); border:2px solid var(--ink); padding:24px; margin:32px 0;">
  <h2 style="margin-top:0;">Frequently Asked Questions</h2>

  <h3 style="font-size:18px; margin-top:16px;">What club does a 7-wood replace?</h3>
  <p>Usually a 3-iron or 4-iron. Iron lofts vary between manufacturers and modern sets feature stronger lofts, so the exact replacement depends on your specific iron set configuration.</p>

  <h3 style="font-size:18px; margin-top:16px;">Is a 7-wood easier to hit than a 3-iron?</h3>
  <p>For most recreational golfers, yes. The wider sole and lower center of gravity launch the ball higher with less demand on perfect strike quality. The exception is golfers with very fast swing speeds, where extra spin can cause shots to balloon in the wind.</p>

  <h3 style="font-size:18px; margin-top:16px;">What loft is a 7-wood?</h3>
  <p>Typically 20 to 23 degrees, most commonly 21 degrees. That fits the fairway wood progression of 15° (3-wood), 18° (5-wood), and 21° (7-wood).</p>

  <h3 style="font-size:18px; margin-top:16px;">How far does a 7-wood carry?</h3>
  <p>Commonly cited carry distance is 180 to 200 yards, though actual distance depends heavily on individual swing speed and strike quality.</p>

  <h3 style="font-size:18px; margin-top:16px;">What is a utility or rescue club?</h3>
  <p>Different names for clubs designed to replace hard-to-hit long irons — usually hybrids or high-lofted fairway woods. The multiple terms reflect marketing efforts to offer easy-to-hit alternatives without ego barriers.</p>

  <h3 style="font-size:18px; margin-top:16px;">Do professional golfers use 7-woods?</h3>
  <p>Yes. Rory McIlroy won the 2026 Masters carrying a 21-degree Ping G430 Max 7-wood.</p>
</div>

<h2>The Raw Take</h2>
<p>Golf presents itself as a game of tradition, where carrying a 3-iron is treated as a badge of honor. But the search data shows Australian golfers are moving past that pretense.</p>

<p>When high-lofted woods draw more than three times the search interest of long irons, and when the world's best player wins Augusta with a 21-degree 7-wood in his bag, the debate is effectively over. Put whatever gets the ball in the air in your bag, and leave the long irons for the windiest coastal days.</p>
          <div class="tag-row">
            <a href="search">7 Wood</a>
            <a href="search">3 Iron</a>
            <a href="search">GOLFRAW</a>
          </div>
        </div>
"""

new_article = BeautifulSoup(article_html, 'html.parser')
soup.article.replace_with(new_article)

# Fix doctype and html tags which bs4 sometimes strips or formats weirdly
final_html = "<!DOCTYPE html>\n" + str(soup)

with open('news-2026-7-wood-vs-3-iron-australian-golfers.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

# Add to search.html
with open('search.html', 'r', encoding='utf-8') as f:
    search_html = f.read()

new_entry = """  {t:"Australians Search for a 7-Wood Three Times More Than a 3-Iron. The Bag Setup Rules Haven't Caught Up.", l:"/news-2026-7-wood-vs-3-iron-australian-golfers", img:"/public/7-wood-vs-3-iron-australian-golfers.webp", cat:"GUIDES", date:"AUG 05 2026", author:"GOLFRAW Editorial", x:"Australians search for a 7-wood three times more than a 3-iron. The loft numbers, the one downside nobody mentions, and why the club has three names.", k:"7 wood, 3 iron, golf club, Australia, GOLFRAW"},
"""
# insert before the closing bracket
search_html = search_html.replace('];', new_entry + '];')
# wait, there's no bracket semicolon, just bracket in search.html at line 301
search_html = search_html.replace(']', new_entry + ']')

with open('search.html', 'w', encoding='utf-8') as f:
    f.write(search_html)

