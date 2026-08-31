import json

with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "canonical": "/news-2026-liv-golf-settlement-offers-bankruptcy",
  "alias_of": "",
  "slug": "news-2026-liv-golf-settlement-offers-bankruptcy",
  "url": "/news-2026-liv-golf-settlement-offers-bankruptcy",
  "title": "LIV Golf Settlement Offers: Cents on the Dollar, Explained | GOLFRAW",
  "excerpt": "Take a fraction now and join a smaller league, or hold out and queue as an unsecured creditor. What the offers say, and who's waiting on the answer.",
  "category": ["LIV GOLF", "TOURNAMENTS", "NEWS"],
  "date": "2026-08-31",
  "image": "/public/liv-golf-settlement-offers-bankruptcy-2026.webp",
  "keywords": "LIV Golf Settlement, Chapter 11 Bankruptcy, PIF, Golf Contracts, Jon Rahm",
  "category_source": "override",
  "section": "LIV GOLF"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)
