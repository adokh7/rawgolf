import json

with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "canonical": "/scottie-scheffler-swing-explained",
  "alias_of": "",
  "slug": "scottie-scheffler-swing-explained",
  "url": "/scottie-scheffler-swing-explained",
  "title": "Scottie Scheffler's Swing: The Foot Slide Is a Symptom | GOLFRAW",
  "excerpt": "Most of the famous foot slide happens after the ball has gone. What's actually producing 1.694 strokes gained tee to green is duller and copyable.",
  "category": ["GUIDES", "PGA TOUR", "SWING MECHANICS"],
  "date": "2026-08-31",
  "image": "/public/scottie-scheffler-swing-explained.webp",
  "keywords": "Scottie Scheffler, Swing Analysis, Golf Mechanics, PGA Tour, Foot Slide",
  "category_source": "override",
  "section": "GUIDES"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)
