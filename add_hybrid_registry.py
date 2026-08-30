import json

with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "canonical": "/why-pros-are-ditching-hybrids",
  "alias_of": "",
  "slug": "why-pros-are-ditching-hybrids",
  "url": "/why-pros-are-ditching-hybrids",
  "title": "Why Pros Are Ditching Hybrids, and Why You Shouldn't | GOLFRAW",
  "excerpt": "Hybrid use in the PGA Tour top 100 fell from 32% to 13%. On the LPGA it's 70%. The 15 mph gap explains both, and one man won a major with one.",
  "category": ["GUIDES", "GEAR", "PGA TOUR"],
  "date": "2026-08-30",
  "image": "/public/why-pros-are-ditching-hybrids-analysis.webp",
  "keywords": "Hybrids, 7-wood, PGA Tour Gear, Golf Equipment, Amateur Golf Data, Arccos Data",
  "category_source": "override",
  "section": "GUIDES"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)
