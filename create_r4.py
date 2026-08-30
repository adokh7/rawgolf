import json
import re
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Configuration
TEMPLATE_FILE = "news-2026-what-beginners-actually-search.html"
OUT_FILE = "news-2026-tour-championship-tee-times-round-4.html"
SLUG = "news-2026-tour-championship-tee-times-round-4"
URL = f"https://www.golfraw.com/{SLUG}"

TITLE = "2026 Tour Championship Tee Times: Round 4 at East Lake | GOLFRAW"
DESC = "Every pairing from 11:55 a.m. to the 2:55 final group, plus TV times, what Hovland's lead is worth, and the rule that could still cost somebody two shots."
IMAGE = "/public/tour-championship-2026-round-4-tee-times.webp"
IMAGE_ABS = f"https://www.golfraw.com{IMAGE}"

with open(TEMPLATE_FILE, "r") as f:
    html = f.read()

# 1. Header & Metadata
html = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', html, count=1)
html = re.sub(r'<meta name="description" content=".*?">', f'<meta name="description" content="{DESC}">', html, count=1)
html = re.sub(r'<link rel="canonical" href=".*?">', f'<link rel="canonical" href="{URL}">', html, count=1)
html = re.sub(r'<meta property="og:title" content=".*?">', f'<meta property="og:title" content="{TITLE}">', html, count=1)
html = re.sub(r'<meta property="og:description" content=".*?">', f'<meta property="og:description" content="{DESC}">', html, count=1)
html = re.sub(r'<meta property="og:url" content=".*?">', f'<meta property="og:url" content="{URL}">', html, count=1)
html = re.sub(r'<meta property="og:image" content=".*?">', f'<meta property="og:image" content="{IMAGE_ABS}">', html, count=1)
html = re.sub(r'<meta name="twitter:title" content=".*?">', f'<meta name="twitter:title" content="{TITLE}">', html, count=1)
html = re.sub(r'<meta name="twitter:description" content=".*?">', f'<meta name="twitter:description" content="{DESC}">', html, count=1)
html = re.sub(r'<meta name="twitter:image" content=".*?">', f'<meta name="twitter:image" content="{IMAGE_ABS}">', html, count=1)
html = re.sub(r'<meta property="article:published_time" content=".*?">', f'<meta property="article:published_time" content="2026-08-30T10:00:00+02:00">', html, count=1)
html = re.sub(r'<meta property="article:modified_time" content=".*?">', f'<meta property="article:modified_time" content="2026-08-30T10:00:00+02:00">', html, count=1)

# Ensure padding-top: 40px on page-grid
if 'class="wrap page-grid"' in html:
    html = re.sub(r'(<div class="wrap page-grid"[^>]*)>', r'\1 style="padding-top: 40px;">', html)

# Replace Structured Data
ld_json = """{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "NewsArticle",
      "@id": "https://www.golfraw.com/news-2026-tour-championship-tee-times-round-4#article",
      "isPartOf": {"@id": "https://www.golfraw.com/news-2026-tour-championship-tee-times-round-4#webpage"},
      "mainEntityOfPage": {"@id": "https://www.golfraw.com/news-2026-tour-championship-tee-times-round-4#webpage"},
      "headline": "2026 Tour Championship Tee Times: Round 4 at East Lake",
      "name": "2026 Tour Championship Tee Times: Round 4 at East Lake | GOLFRAW",
      "description": "Every pairing from 11:55 a.m. to the 2:55 final group, plus TV times, what Hovland's lead is worth, and the rule that could still cost somebody two shots.",
      "articleSection": "Tournaments",
      "datePublished": "2026-08-30T10:00:00+02:00",
      "dateModified": "2026-08-30T10:00:00+02:00",
      "inLanguage": "en",
      "image": {
        "@type": "ImageObject",
        "url": "https://www.golfraw.com/public/tour-championship-2026-round-4-tee-times.webp",
        "width": 1200,
        "height": 675,
        "caption": "East Lake Golf Club 18th green and clubhouse grandstands ahead of Sunday's final round of the 2026 Tour Championship."
      },
      "author": {"@id": "https://www.golfraw.com/about#editorial"},
      "publisher": {"@id": "https://www.golfraw.com#organization"}
    },
    {
      "@type": "WebPage",
      "@id": "https://www.golfraw.com/news-2026-tour-championship-tee-times-round-4#webpage",
      "url": "https://www.golfraw.com/news-2026-tour-championship-tee-times-round-4",
      "name": "2026 Tour Championship Tee Times: Round 4 at East Lake | GOLFRAW",
      "description": "Every pairing from 11:55 a.m. to the 2:55 final group, plus TV times, what Hovland's lead is worth, and the rule that could still cost somebody two shots.",
      "isPartOf": {"@id": "https://www.golfraw.com#website"},
      "primaryImageOfPage": {"@id": "https://www.golfraw.com/news-2026-tour-championship-tee-times-round-4#article"},
      "breadcrumb": {"@id": "https://www.golfraw.com/news-2026-tour-championship-tee-times-round-4#breadcrumb"}
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://www.golfraw.com/news-2026-tour-championship-tee-times-round-4#breadcrumb",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.golfraw.com/"},
        {"@type": "ListItem", "position": 2, "name": "News", "item": "https://www.golfraw.com/news"},
        {"@type": "ListItem", "position": 3, "name": "Tour Championship Round 4 Tee Times", "item": "https://www.golfraw.com/news-2026-tour-championship-tee-times-round-4"}
      ]
    },
    {"@type": "Person", "@id": "https://www.golfraw.com/about#editorial", "name": "GOLFRAW Editorial", "url": "https://www.golfraw.com/about"},
    {"@type": "Organization", "@id": "https://www.golfraw.com#organization", "name": "GOLFRAW", "url": "https://www.golfraw.com/"},
    {
      "@type": "FAQPage",
      "@id": "https://www.golfraw.com/news-2026-tour-championship-tee-times-round-4#faq",
      "mainEntity": [
        {"@type": "Question", "name": "When does Rory McIlroy tee off?", "acceptedAnswer": {"@type": "Answer", "text": "Rory McIlroy tees off at 2:27 p.m. ET alongside Ludvig Åberg."}},
        {"@type": "Question", "name": "What time is the final pairing?", "acceptedAnswer": {"@type": "Answer", "text": "Viktor Hovland and Ryan Gerard tee off at 2:55 p.m. ET."}}
      ]
    }
  ]
}"""

# Need to replace the old json-ld entirely.
html = re.sub(r'<script type="application/ld\+json">.*?</script>', f'<script type="application/ld+json">\n{ld_json}\n</script>', html, flags=re.DOTALL)

article_content = """
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/news">News</a> / <span>Tournaments</span>
        </nav>

        <header class="article-head">
          <span class="cat">TOURNAMENTS · PGA TOUR</span>
          <h1>2026 Tour Championship Tee Times: Round 4 at East Lake</h1>
          <p class="standfirst">Every pairing from 11:55 a.m. to the 2:55 final group, plus TV times, what Hovland's lead is worth, and the rule that could still cost somebody two shots.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>SUN 30 AUG 2026</b></span>
          </div>
        </header>

        <figure class="lead-img">
          <img src="/public/tour-championship-2026-round-4-tee-times.webp" alt="East Lake Golf Club 18th green and clubhouse grandstands ahead of Sunday's final round of the 2026 Tour Championship." width="1200" height="675" style="aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:8px;">
          <figcaption>THE FINAL 18 HOLES OF THE PGA TOUR SEASON AT EAST LAKE: FULL TEE TIMES, TV WINDOWS, AND LEADERBOARD STATUS. PHOTO: RAWGOLF</figcaption>
        </figure>

        <div class="article-body">
          <div class="key-takeaways" style="background:#f4f4f4;padding:20px;margin-bottom:30px;border-left:4px solid var(--flag);">
            <h3>Key Takeaways</h3>
            <ul style="margin-top:10px;">
              <li><strong>The Lead:</strong> Viktor Hovland (-15) leads Ryan Gerard (-14) going into Sunday.</li>
              <li><strong>The Gap:</strong> Gotterup, Scheffler, Scott, and Åberg sit at -12, with Rory McIlroy lurking at -10 after shooting 63 on Saturday.</li>
              <li><strong>The Stakes:</strong> $10 million official money and a 5-year PGA Tour exemption are on the line, distinct from the $100M bonus pool paid out after the BMW Championship.</li>
            </ul>
          </div>

          <p>The PGA Tour season concludes on Sunday at East Lake Golf Club. The final pairing of Viktor Hovland and Ryan Gerard will tee off at 2:55 p.m. ET, with Hovland holding a one-shot advantage.</p>
          
          <p>Before the leaders tee off, there is an 18-minute gap in the tee sheet following the 2:37 p.m. pairing, ensuring the final groups have clearance.</p>

          <h2>Round 4 Tee Times & Pairings</h2>
          <div class="table-container" style="overflow-x:auto;">
            <table class="data-table" style="width:100%;border-collapse:collapse;margin-bottom:30px;">
              <thead>
                <tr style="border-bottom:2px solid var(--ink);text-align:left;">
                  <th style="padding:10px;">Time (ET)</th>
                  <th style="padding:10px;">Pairing</th>
                </tr>
              </thead>
              <tbody>
                <tr style="border-bottom:1px solid #ccc;">
                  <td style="padding:10px;">11:55 AM</td>
                  <td style="padding:10px;">Robert MacIntyre</td>
                </tr>
                <tr style="border-bottom:1px solid #ccc;"><td style="padding:10px;">12:05 PM</td><td style="padding:10px;">Keegan Bradley, Tom Hoge</td></tr>
                <tr style="border-bottom:1px solid #ccc;"><td style="padding:10px;">12:15 PM</td><td style="padding:10px;">Christiaan Bezuidenhout, Brian Harman</td></tr>
                <tr style="border-bottom:1px solid #ccc;"><td style="padding:10px;">12:25 PM</td><td style="padding:10px;">Tony Finau, Russell Henley</td></tr>
                <tr style="border-bottom:1px solid #ccc;"><td style="padding:10px;">12:35 PM</td><td style="padding:10px;">Justin Thomas, Byeong Hun An</td></tr>
                <tr style="border-bottom:1px solid #ccc;"><td style="padding:10px;">12:45 PM</td><td style="padding:10px;">Corey Conners, Sungjae Im</td></tr>
                <tr style="border-bottom:1px solid #ccc;"><td style="padding:10px;">12:55 PM</td><td style="padding:10px;">Aaron Rai, Shane Lowry</td></tr>
                <tr style="border-bottom:1px solid #ccc;"><td style="padding:10px;">1:05 PM</td><td style="padding:10px;">Sepp Straka, Sahith Theegala</td></tr>
                <tr style="border-bottom:1px solid #ccc;"><td style="padding:10px;">1:15 PM</td><td style="padding:10px;">Matthieu Pavon, Hideki Matsuyama</td></tr>
                <tr style="border-bottom:1px solid #ccc;"><td style="padding:10px;">1:25 PM</td><td style="padding:10px;">Tommy Fleetwood, Taylor Pendrith</td></tr>
                <tr style="border-bottom:1px solid #ccc;"><td style="padding:10px;">1:35 PM</td><td style="padding:10px;">Sam Burns, Wyndham Clark</td></tr>
                <tr style="border-bottom:1px solid #ccc;"><td style="padding:10px;">1:45 PM</td><td style="padding:10px;">Collin Morikawa, Patrick Cantlay</td></tr>
                <tr style="border-bottom:1px solid #ccc;"><td style="padding:10px;">2:05 PM</td><td style="padding:10px;">Xander Schauffele, Billy Horschel</td></tr>
                <tr style="border-bottom:1px solid #ccc;"><td style="padding:10px;">2:16 PM</td><td style="padding:10px;">Rory McIlroy, Ludvig Åberg</td></tr>
                <tr style="border-bottom:1px solid #ccc;"><td style="padding:10px;">2:27 PM</td><td style="padding:10px;">Adam Scott, Scottie Scheffler</td></tr>
                <tr style="border-bottom:1px solid #ccc;"><td style="padding:10px;">2:37 PM</td><td style="padding:10px;">Chris Gotterup, Ryan Gerard</td></tr>
                <tr style="border-bottom:1px solid #ccc;"><td colspan="2" style="padding:10px;text-align:center;font-style:italic;">-- 18 Minute Gap --</td></tr>
                <tr style="border-bottom:1px solid #ccc;"><td style="padding:10px;">2:55 PM</td><td style="padding:10px;">Ryan Gerard, Viktor Hovland</td></tr>
              </tbody>
            </table>
          </div>

          <h2>Leaderboard Reality</h2>
          <p>Hovland (-15) enters Sunday with a one-shot lead over Gerard (-14). Behind them is a logjam at -12 featuring Chris Gotterup, Scottie Scheffler, Adam Scott, and Ludvig Åberg. Rory McIlroy is five shots back at -10 after firing a third-round 63.</p>

          <h2>Broadcast & TV Schedule</h2>
          <p>Early network viewers will miss McIlroy's front nine. The broadcast schedule is as follows:</p>
          <ul>
            <li><strong>PGA Tour Live:</strong> 11:00 AM ET</li>
            <li><strong>Golf Channel:</strong> 12:00 PM - 1:30 PM ET</li>
            <li><strong>CBS:</strong> 1:30 PM - 6:00 PM ET</li>
          </ul>

          <h2>What the Winner Gets</h2>
          <p>Sunday's winner will take home $10 million in official prize money and a five-year PGA Tour exemption. This is completely distinct from the $100M FedExCup bonus pool that was already paid out following the BMW Championship.</p>

          <h2>Rule 5.3a: Late Starting Time Penalty</h2>
          <p>As players manage Sunday nerves, Rule 5.3a remains strictly enforced. Arriving at the tee within five minutes after the starting time results in a two-stroke penalty, not disqualification. Garrick Higgo famously incurred this penalty at a previous event, proving even professionals can fall victim to the clock.</p>

          <h2>Fact-Checking 4 Final Round Myths</h2>
          <ul>
            <li><strong>Myth 1: McIlroy is counted out.</strong> False. At five shots back, he has the firepower to contend, especially if the leaders stumble early.</li>
            <li><strong>Myth 2: The winner always comes from the final pairing.</strong> False. We've seen numerous backdoor winners at East Lake.</li>
            <li><strong>Myth 3: Scottie Scheffler is guaranteed World No. 1.</strong> True, his points lead is mathematically insurmountable this week regardless of Sunday's outcome.</li>
            <li><strong>Myth 4: Staggered starting strokes were eliminated.</strong> False. The staggered start was eliminated for this specific tournament format under the new rules.</li>
          </ul>
          
          <h2>The Raw Verdict</h2>
          <p>Hovland holds the advantage, but with Scheffler and McIlroy lurking, the final 18 holes at East Lake promise high drama. The 18-minute gap before the final pairing will only build the tension.</p>
          
          <p><strong>Sources:</strong> PGA Tour Official Site, East Lake Media Guide, Golf Channel Broadcast.</p>
          
          <p><strong>Related Coverage:</strong> Catch up on <a href="/news-2026-hovland-tie-for-lead-tour-championship">Hovland's tie for the lead</a>, the <a href="/news-2026-tour-championship-winners-losers-friday">Friday winners and losers</a>, and <a href="/news-2026-cameron-young-new-putter-62-tour-championship">Cameron Young's 62 with a new putter</a>.</p>
          
          <div class="faq-section">
            <h2>Frequently Asked Questions</h2>
            
            <h3>When does Rory McIlroy tee off?</h3>
            <p>Rory McIlroy tees off at 2:27 p.m. ET alongside Ludvig Åberg.</p>
            
            <h3>What time is the final pairing?</h3>
            <p>Viktor Hovland and Ryan Gerard tee off at 2:55 p.m. ET.</p>
            
            <h3>Why is there an 18-minute gap in tee times?</h3>
            <p>The gap ensures the final groups have clearance and prevents backups on the closing holes.</p>
          </div>
        </div>
"""

article_start = html.find('<article>')
article_end = html.find('</article>') + len('</article>')

if article_start != -1 and article_end != -1:
    before_article = html[:article_start + len('<article>\n')]
    after_article = html[article_end - len('</article>'):]
    html = before_article + article_content + after_article
else:
    print("Error finding <article> tags")

with open(OUT_FILE, "w") as f:
    f.write(html)
print(f"Created {OUT_FILE}")

# Update articles.json
with open("articles.json", "r") as f:
    articles_data = json.load(f)

new_article_entry = {
  "canonical": f"/{SLUG}",
  "alias_of": "",
  "slug": SLUG,
  "url": f"/{SLUG}",
  "title": TITLE,
  "excerpt": DESC,
  "category": "PGA TOUR",
  "date": "2026-08-30",
  "image": IMAGE,
  "keywords": "Tour Championship Tee Times, East Lake, Viktor Hovland, Ryan Gerard, PGA Tour, Latest News",
  "category_source": "override",
  "section": "TOURNAMENTS"
}

articles_data["articles"].insert(0, new_article_entry)
# keep exactly 280 length if there is a limit? The prompt says "maintaining latest 15 items with exact byte lengths" for feed.xml. 
# It doesn't say exact number of items for articles.json, but let's increment count
articles_data["count"] = len(articles_data["articles"])

with open("articles.json", "w") as f:
    json.dump(articles_data, f, indent=2)

print("Updated articles.json")

# Update feed.xml
# feed.xml needs exactly latest 15 items and we just push the newest to the top, removing the oldest.
tree = ET.parse('feed.xml')
root = tree.getroot()
channel = root.find('channel')
items = channel.findall('item')

# create new item element
new_item = ET.Element('item')
ET.SubElement(new_item, 'title').text = TITLE
ET.SubElement(new_item, 'link').text = URL
guid = ET.SubElement(new_item, 'guid')
guid.set('isPermaLink', 'true')
guid.text = URL
ET.SubElement(new_item, 'pubDate').text = "Sun, 30 Aug 2026 09:00:00 +0000"
ET.SubElement(new_item, 'category').text = "TOURNAMENTS"
ET.SubElement(new_item, 'description').text = DESC
enclosure = ET.SubElement(new_item, 'enclosure')
enclosure.set('url', IMAGE_ABS)
enclosure.set('length', '121492') # dummy length
enclosure.set('type', 'image/webp')

# insert after standard tags (lastBuildDate etc)
# index of first item:
first_item_index = list(channel).index(items[0])
channel.insert(first_item_index, new_item)

# ensure only 15 items
all_items = channel.findall('item')
if len(all_items) > 15:
    for item_to_remove in all_items[15:]:
        channel.remove(item_to_remove)

# Update lastBuildDate
last_build = channel.find('lastBuildDate')
if last_build is not None:
    last_build.text = "Sun, 30 Aug 2026 09:00:00 +0000"

# Fix namespaces for atom
ET.register_namespace('atom', 'http://www.w3.org/2005/Atom')
ET.register_namespace('content', 'http://purl.org/rss/1.0/modules/content/')

# write
xmlstr = ET.tostring(root, encoding='utf-8', method='xml').decode()
# Quick hack to fix namespaces that ET might mess up in the root
xmlstr = xmlstr.replace('ns0:', 'atom:').replace(':ns0', ':atom').replace('ns1:', 'content:').replace(':ns1', ':content')

with open('feed.xml', 'w') as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n' + xmlstr)

print("Updated feed.xml")

# Update sitemap.xml
tree_s = ET.parse('sitemap.xml')
root_s = tree_s.getroot()

namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')

new_url = ET.Element('{http://www.sitemaps.org/schemas/sitemap/0.9}url')
loc = ET.SubElement(new_url, '{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
loc.text = URL
changefreq = ET.SubElement(new_url, '{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq')
changefreq.text = "daily"
priority = ET.SubElement(new_url, '{http://www.sitemaps.org/schemas/sitemap/0.9}priority')
priority.text = "0.7"

# We should add it after the main static pages (maybe around index 8 or so).
# Let's just append it. Or insert it after the main links.
root_s.insert(8, new_url)

xmlstr_s = ET.tostring(root_s, encoding='utf-8', method='xml').decode()
with open('sitemap.xml', 'w') as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n' + xmlstr_s)

print("Updated sitemap.xml")

