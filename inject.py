import re
from datetime import datetime

article_card = """        <article class="news">
          <a href="/news-2026-jon-rahm-liv-money-owed" style="display:block; margin-bottom:16px;">
            <img src="/news-2026-jon-rahm-liv-money-owed.webp" alt="Jon Rahm's LIV Money: What He's Owed and Who Gets Paid | GOLFRAW" style="width: 100%; border-radius: 4px;" decoding="async" width="1536" height="1024" loading="lazy">
          </a>
          <div class="cat" style="display:flex;align-items:center;gap:8px;">
            <span>LIV GOLF, MONEY, NEWS</span>
          </div>
          <h3><a href="/news-2026-jon-rahm-liv-money-owed">Jon Rahm's LIV Money: What He's Owed and Who Gets Paid | GOLFRAW</a></h3>
          <p>Three outlets give three different figures for what he's owed. The bigger question is where a player ranks when the bankruptcy queue forms.</p>
          <div class="meta"><span>BY GOLFRAW Editorial</span><span class="mono">2026-09-01</span></div>
        </article>
"""

def insert_after(file_path, marker, text):
    with open(file_path, 'r') as f:
        content = f.read()
    if marker in content:
        content = content.replace(marker, marker + '\n' + text, 1)
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Updated {file_path}")
    else:
        print(f"Marker not found in {file_path}")

insert_after('index.html', '<div class="news-grid reveal">', article_card)
insert_after('news.html', '<div class="news-grid">', article_card)
insert_after('liv-golf.html', '<div class="news-grid">', article_card)

sitemap_entry = """  <url>
    <loc>https://www.golfraw.com/news-2026-jon-rahm-liv-money-owed</loc>
    <lastmod>2026-09-01</lastmod>
    <changefreq>never</changefreq>
  </url>
"""

with open('sitemap.xml', 'r') as f:
    sitemap = f.read()
sitemap = sitemap.replace('</urlset>', sitemap_entry + '</urlset>')
with open('sitemap.xml', 'w') as f:
    f.write(sitemap)
print("Updated sitemap.xml")

feed_entry = """    <item>
      <title>Jon Rahm's LIV Money: What He's Owed and Who Gets Paid | GOLFRAW</title>
      <link>https://www.golfraw.com/news-2026-jon-rahm-liv-money-owed</link>
      <guid isPermaLink="true">https://www.golfraw.com/news-2026-jon-rahm-liv-money-owed</guid>
      <pubDate>Tue, 01 Sep 2026 21:30:00 +0200</pubDate>
      <category>LIV GOLF, MONEY, NEWS</category>
      <description>Three outlets give three different figures for what he's owed. The bigger question is where a player ranks when the bankruptcy queue forms.</description>
      <enclosure url="https://www.golfraw.com/news-2026-jon-rahm-liv-money-owed.webp" length="100000" type="image/webp"/>
    </item>
"""
insert_after('feed.xml', '<atom:link rel="hub" href="https://pubsubhubbub.superfeedr.com/"/>', feed_entry)

