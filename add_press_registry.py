import json

with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "canonical": "/news-2026-scottie-scheffler-final-press-conference-answer",
  "alias_of": "",
  "slug": "news-2026-scottie-scheffler-final-press-conference-answer",
  "url": "/news-2026-scottie-scheffler-final-press-conference-answer",
  "title": "Scottie Scheffler's Final Press Conference Answer of 2026 | GOLFRAW",
  "excerpt": "No existential monologue this time. Wind, fighting back, and travelling with his wife and two sons. Why the boring version tells you more.",
  "category": ["PGA TOUR", "TOURNAMENTS", "NEWS"],
  "date": "2026-08-31",
  "image": "/public/scottie-scheffler-final-press-conference-answer-2026.webp",
  "keywords": "Scottie Scheffler, PGA Tour, Tour Championship, FedExCup, Golf Interview",
  "category_source": "override",
  "section": "PGA TOUR"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)
