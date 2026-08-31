import json

with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "canonical": "/news-2026-the-end-of-liv-golf-bankruptcy",
  "alias_of": "",
  "slug": "news-2026-the-end-of-liv-golf-bankruptcy",
  "url": "/news-2026-the-end-of-liv-golf-bankruptcy",
  "title": "The End of LIV Golf? What a Bankruptcy Would Really Mean | GOLFRAW",
  "excerpt": "Chapter 11 isn't liquidation. It's the vehicle for handing the league to players at about a third of the purses. What's verified, what isn't.",
  "category": ["LIV GOLF", "TOURNAMENTS", "NEWS"],
  "date": "2026-08-31",
  "image": "/public/the-end-of-liv-golf-bankruptcy-2026.webp",
  "keywords": "LIV Golf, Chapter 11, Bankruptcy, PIF, Golf Restructuring, PGA Tour",
  "category_source": "override",
  "section": "LIV GOLF"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)
