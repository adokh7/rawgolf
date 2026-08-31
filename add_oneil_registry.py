import json

with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "canonical": "/news-2026-scott-oneil-linkedin-post-liv-golf",
  "alias_of": "",
  "slug": "news-2026-scott-oneil-linkedin-post-liv-golf",
  "url": "/news-2026-scott-oneil-linkedin-post-liv-golf",
  "title": "Scott O'Neil's LinkedIn Post on LIV Golf 1.0, Fact-Checked | GOLFRAW",
  "excerpt": "Players as majority owners, five continents, a billion homes. Every claim checked against what LIV actually did in 2026, including the purse cut.",
  "category": ["LIV GOLF", "TOURNAMENTS", "NEWS"],
  "date": "2026-08-31",
  "image": "/public/scott-oneil-linkedin-post-liv-golf-2026.webp",
  "keywords": "Scott O'Neil, LIV Golf, Chapter 11, LIV 2.0, Golf Business, Fact Check",
  "category_source": "override",
  "section": "LIV GOLF"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)
