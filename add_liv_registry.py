import json

with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "canonical": "/news-2026-liv-golf-bankruptcy-chapter-11-explained",
  "alias_of": "",
  "slug": "news-2026-liv-golf-bankruptcy-chapter-11-explained",
  "url": "/news-2026-liv-golf-bankruptcy-chapter-11-explained",
  "title": "LIV Golf Bankruptcy: What Chapter 11 Would Actually Do | GOLFRAW",
  "excerpt": "A Chapter 11 filing isn't the league shutting down. It's the vehicle for handing it to the players. What's verified, what isn't, and who gets paid last.",
  "category": ["LIV GOLF", "TOURNAMENTS", "NEWS"],
  "date": "2026-08-31",
  "image": "/public/liv-golf-bankruptcy-chapter-11-explained-2026.webp",
  "keywords": "LIV Golf, Chapter 11 Bankruptcy, PIF Funding, PGA Tour, Golf Business",
  "category_source": "override",
  "section": "LIV GOLF"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)
