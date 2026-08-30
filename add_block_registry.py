import json

with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "canonical": "/news-2026-michael-block-lead-ally-challenge",
  "alias_of": "",
  "slug": "news-2026-michael-block-lead-ally-challenge",
  "url": "/news-2026-michael-block-lead-ally-challenge",
  "title": "Michael Block's 2-Shot Lead at the Ally Challenge Explained | GOLFRAW",
  "excerpt": "He eagled the first, made five birdies, dropped nothing, and leads by two. But the number he's actually chasing isn't first place. Here's what it is.",
  "category": ["TOURNAMENTS", "CHAMPIONS TOUR", "NEWS"],
  "date": "2026-08-30",
  "image": "/public/michael-block-lead-ally-challenge-2026.webp",
  "keywords": "Michael Block, Ally Challenge, Champions Tour, Warwick Hills, Steven Alker, Charles Schwab Cup",
  "category_source": "override",
  "section": "TOURNAMENTS"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)
