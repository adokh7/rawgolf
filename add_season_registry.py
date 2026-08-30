import json

with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "canonical": "/news-2026-pga-tour-winners-2026",
  "alias_of": "",
  "slug": "news-2026-pga-tour-winners-2026",
  "url": "/news-2026-pga-tour-winners-2026",
  "title": "PGA Tour Winners 2026: 28 Names, 35 Events, One Left | GOLFRAW",
  "excerpt": "Every winner from the Sony Open to the BMW, the three men who won three times, and why the best player in the world isn't one of them.",
  "category": ["PGA TOUR", "TOURNAMENTS", "NEWS"],
  "date": "2026-08-30",
  "image": "/public/pga-tour-winners-2026-season-recap.webp",
  "keywords": "PGA Tour Winners 2026, Chris Gotterup, Wyndham Clark, Scottie Scheffler, Aaron Rai, Tour Championship",
  "category_source": "override",
  "section": "PGA TOUR"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)
