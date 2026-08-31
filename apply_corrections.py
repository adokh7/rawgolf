import json, re

# Update articles.json
with open("articles.json", "r") as f:
    data = json.load(f)

for article in data["articles"]:
    if article["slug"] == "news-2026-scottie-scheffler-final-press-conference-answer":
        article["image"] = "/public/scheffler-presser-eastlake-2026.webp"

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)


# Update HTML
with open('news-2026-scottie-scheffler-final-press-conference-answer.html', 'r') as f:
    html = f.read()

# Update image path in meta tags
html = re.sub(r'/public/scottie-scheffler-final-press-conference-answer-2026-v2.webp', '/public/scheffler-presser-eastlake-2026.webp', html)
html = re.sub(r'/public/scottie-scheffler-final-press-conference-answer-2026.webp', '/public/scheffler-presser-eastlake-2026.webp', html)

# Ensure Category Badge
html = re.sub(r'<span class="cat">.*?</span>', '<span class="cat">PGA TOUR • SEASON RETROSPECTIVE</span>', html, count=1)

# Ensure H1
html = re.sub(r'<h1>.*?</h1>', '<h1>Scottie Scheffler\'s Final Press Conference Answer of the Season</h1>', html, count=1)

# Ensure Subtitle
html = re.sub(r'<p class="standfirst">.*?</p>', '<p class="standfirst">He\'d just won $10 million, a second FedEx Cup, and passed Tiger Woods on the all-time money list. Then he spent his last answers of the year talking about wind and about travelling with his kids.</p>', html, count=1)

# Update Hero Figure
hero_html = """<figure class="lead-img">
          <img src="/public/scheffler-presser-eastlake-2026.webp" alt="Scottie Scheffler speaking at the media center press conference podium after winning the 2026 Tour Championship." width="1200" height="675" style="aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:8px;">
          <figcaption>SCOTTIE SCHEFFLER REFLECTED ON HIS 2026 SEASON WITH A GROUNDED PRESS CONFERENCE AT EAST LAKE. PHOTO: RAWGOLF</figcaption>
        </figure>"""
html = re.sub(r'<figure class="lead-img">.*?</figure>', hero_html, html, flags=re.DOTALL)

with open('news-2026-scottie-scheffler-final-press-conference-answer.html', 'w') as f:
    f.write(html)
