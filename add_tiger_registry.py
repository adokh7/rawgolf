import json

with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "canonical": "/every-shot-tiger-woods-80th-win-2018",
  "alias_of": "",
  "slug": "news-every-shot-tiger-woods-80th-win-2018",
  "url": "/news-every-shot-tiger-woods-80th-win-2018",
  "title": "Every Shot From Tiger Woods' 80th Win: What to Watch For | GOLFRAW",
  "excerpt": "He shot 71 on Sunday, made three bogeys, and won by two. What the full broadcast shows that the highlight reel cuts, and the trophy he didn't take home.",
  "category": ["TOURNAMENTS", "PGA TOUR", "HISTORY"],
  "date": "2026-08-30",
  "image": "/public/every-shot-tiger-woods-80th-win-2018.webp",
  "keywords": "Tiger Woods 80th Win, 2018 Tour Championship, East Lake, FedExCup, PGA Tour History",
  "category_source": "override",
  "section": "HISTORY"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)
