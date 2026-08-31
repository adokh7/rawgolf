import json

with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "canonical": "/news-2026-scheffler-brandel-chamblee",
  "alias_of": "",
  "slug": "news-2026-scheffler-brandel-chamblee",
  "url": "/news-2026-scheffler-brandel-chamblee",
  "title": "Scheffler and Brandel Chamblee: The Full 2026 Arc | GOLFRAW",
  "excerpt": "In April he didn't recognise Scheffler's swing. In August he called him miles ahead. Both takes were right, and the record proves it.",
  "category": ["PGA TOUR", "TOURNAMENTS", "NEWS"],
  "date": "2026-08-31",
  "image": "/public/scheffler-brandel-chamblee-2026.webp",
  "keywords": "Scottie Scheffler, Brandel Chamblee, Golf Channel, PGA Tour, Golf Media",
  "category_source": "override",
  "section": "PGA TOUR"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)
