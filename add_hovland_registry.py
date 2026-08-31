import json

with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "canonical": "/news-2026-hovland-on-what-makes-scheffler-successful",
  "alias_of": "",
  "slug": "news-2026-hovland-on-what-makes-scheffler-successful",
  "url": "/news-2026-hovland-on-what-makes-scheffler-successful",
  "title": "Hovland on What Makes Scheffler Successful, in 8 Words | GOLFRAW",
  "excerpt": "Asked if Scheffler amazes him, the man he'd just lost to said no. His actual explanation is duller and far more useful than any mental-game theory.",
  "category": ["PGA TOUR", "TOURNAMENTS", "NEWS"],
  "date": "2026-08-31",
  "image": "/public/hovland-on-what-makes-scheffler-successful-2026.webp",
  "keywords": "Viktor Hovland, Scottie Scheffler, Tour Championship, Golf Mental Game, PGA Tour",
  "category_source": "override",
  "section": "PGA TOUR"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)
