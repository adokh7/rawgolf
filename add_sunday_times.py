import json

with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "canonical": "/news-2026-tour-championship-sunday-tee-times-round-4",
  "alias_of": "",
  "slug": "news-2026-tour-championship-sunday-tee-times-round-4",
  "url": "/news-2026-tour-championship-sunday-tee-times-round-4",
  "title": "2026 Tour Championship Sunday Tee Times: Everything Moved | GOLFRAW",
  "excerpt": "The whole draw shifted about an hour earlier and the pairings were rebuilt. Full Round 4 tee sheet, TV windows, and the mismatch nobody has flagged.",
  "category": ["TOURNAMENTS", "PGA TOUR", "NEWS"],
  "date": "2026-08-30",
  "image": "/public/2026-tour-championship-sunday-tee-times-round-4.webp",
  "keywords": "Tour Championship Sunday Tee Times, Viktor Hovland, Ryan Gerard, East Lake, PGA Tour",
  "category_source": "override",
  "section": "TOURNAMENTS"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)
