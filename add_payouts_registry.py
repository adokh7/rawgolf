import json

with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "canonical": "/news-2026-tour-championship-points-and-payouts",
  "alias_of": "",
  "slug": "news-2026-tour-championship-points-and-payouts",
  "url": "/news-2026-tour-championship-points-and-payouts",
  "title": "Tour Championship Points and Payouts: All 29 Checks | GOLFRAW",
  "excerpt": "Scheffler took $10M, seven men split $11.95M, and $355,000 went nowhere. Full table, plus the figure two official pages disagree on.",
  "category": ["PGA TOUR", "TOURNAMENTS", "NEWS"],
  "date": "2026-08-31",
  "image": "/public/tour-championship-points-and-payouts-2026.webp",
  "keywords": "Tour Championship Payouts, FedExCup Prize Money, Scottie Scheffler, PGA Tour Earnings, East Lake",
  "category_source": "override",
  "section": "PGA TOUR"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)
