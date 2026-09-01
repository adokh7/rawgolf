import re

with open('news-2026-jon-rahm-liv-money-owed.html', 'r') as f:
    html = f.read()

html = re.sub(r'<h1>.*?</h1>', "<h1>Jon Rahm's LIV Money: What He's Owed and Who Gets Paid</h1>", html, count=1, flags=re.DOTALL)
html = re.sub(r'<p class="standfirst">.*?</p>', '<p class="standfirst">Three outlets give three different figures for what he\'s owed. The bigger question is where a player ranks when the bankruptcy queue forms.</p>', html, count=1, flags=re.DOTALL)

new_img = """<figure class="lead-img">
          <img src="/news-2026-jon-rahm-liv-money-owed.webp" width="1200" height="675" alt="Jon Rahm LIV Golf unpaid contract money and creditor ranking 2026 season" fetchpriority="high">
          <figcaption>Jon Rahm LIV Golf unpaid contract money and creditor ranking 2026 season — GOLFRAW</figcaption>
        </figure>"""

html = re.sub(r'<figure class="lead-img">.*?</figure>', new_img, html, count=1, flags=re.DOTALL)

with open('news-2026-jon-rahm-liv-money-owed.html', 'w') as f:
    f.write(html)
