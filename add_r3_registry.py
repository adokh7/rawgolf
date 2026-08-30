import json

with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "canonical": "/news-2026-tour-championship-round-3-tee-times-leaderboard",
  "alias_of": "",
  "slug": "news-2026-tour-championship-round-3-tee-times-leaderboard",
  "url": "/news-2026-tour-championship-round-3-tee-times-leaderboard",
  "title": "Tour Championship Round 3: Hovland's 65 and Every Score | GOLFRAW",
  "excerpt": "Nineteen players began Saturday within five shots and it ended with a one-shot lead. Full Round 3 draw, results, and the Sunday sheet nobody agrees on.",
  "category": ["TOURNAMENTS", "PGA TOUR", "NEWS"],
  "date": "2026-08-30",
  "image": "/public/tour-championship-2026-round-3-tee-times-leaderboard.webp",
  "keywords": "Tour Championship Round 3, Viktor Hovland, Rory McIlroy 63, East Lake Leaderboard, PGA Tour",
  "category_source": "override",
  "section": "TOURNAMENTS"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)
