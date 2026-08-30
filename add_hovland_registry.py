import json

with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "canonical": "/news-2026-hovland-one-shot-lead-tour-championship",
  "alias_of": "",
  "slug": "news-2026-hovland-one-shot-lead-tour-championship",
  "url": "/news-2026-hovland-one-shot-lead-tour-championship",
  "title": "Hovland's One-Shot Lead Came From Six Straight Putts | GOLFRAW",
  "excerpt": "Six putts from seven feet or longer built it. Scheffler, Scott, Åberg and Gotterup are three back, McIlroy shot 63, and last place is 3 under.",
  "category": ["TOURNAMENTS", "PGA TOUR", "NEWS"],
  "date": "2026-08-30",
  "image": "/public/hovland-one-shot-lead-tour-championship-2026.webp",
  "keywords": "Viktor Hovland, Tour Championship, Scottie Scheffler, Rory McIlroy 63, East Lake, PGA Tour",
  "category_source": "override",
  "section": "TOURNAMENTS"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)
