import json

with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "canonical": "/news-2026-tiger-woods-career-money-list-record",
  "alias_of": "",
  "slug": "news-2026-tiger-woods-career-money-list-record",
  "url": "/news-2026-tiger-woods-career-money-list-record",
  "title": "Tiger Woods' Career Money List Record May Fall Today | GOLFRAW",
  "excerpt": "Scheffler needs solo 13th, McIlroy needs solo 4th. One outlet already declared it done a week ago. Here's what's actually verified and what isn't.",
  "category": ["PGA TOUR", "TOURNAMENTS", "NEWS"],
  "date": "2026-08-30",
  "image": "/public/tiger-woods-career-money-list-record.webp",
  "keywords": "Tiger Woods, Scottie Scheffler, Rory McIlroy, PGA Tour Career Money List, Tour Championship",
  "category_source": "override",
  "section": "PGA TOUR"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)
