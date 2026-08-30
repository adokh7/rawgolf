import json

with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "canonical": "/news-2026-michael-block-leads-ally-challenge-final-round",
  "alias_of": "",
  "slug": "news-2026-michael-block-leads-ally-challenge-final-round",
  "url": "/news-2026-michael-block-leads-ally-challenge-final-round",
  "title": "Michael Block Leads the Ally Challenge Into Sunday by Two | GOLFRAW",
  "excerpt": "He's in on an invitation, his son is on the bag, and he opened Saturday with an eagle. What Block actually needs from Sunday, and it isn't the trophy.",
  "category": ["TOURNAMENTS", "CHAMPIONS TOUR", "NEWS"],
  "date": "2026-08-30",
  "image": "/public/michael-block-leads-ally-challenge-final-round-2026.webp",
  "keywords": "Michael Block, Ally Challenge, Champions Tour, Warwick Hills, Steven Alker, Charles Schwab Cup",
  "category_source": "override",
  "section": "TOURNAMENTS"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)
