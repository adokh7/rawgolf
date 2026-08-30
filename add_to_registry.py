import json

with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "canonical": "/news-2026-tour-championship-final-round-hovland-leads",
  "alias_of": "",
  "slug": "news-2026-tour-championship-final-round-hovland-leads",
  "url": "/news-2026-tour-championship-final-round-hovland-leads",
  "title": "Tour Championship Final Round: Hovland Leads by One | GOLFRAW",
  "excerpt": "Hovland leads by one at 15 under, Scheffler's three back, McIlroy shot 63. Every number that matters before the final round of the season.",
  "category": ["TOURNAMENTS", "PGA TOUR", "NEWS"],
  "date": "2026-08-30",
  "image": "/public/tour-championship-final-round-hovland-leads-2026.webp",
  "keywords": "Viktor Hovland, Tour Championship Final Round, Scottie Scheffler, Rory McIlroy 63, East Lake",
  "category_source": "override",
  "section": "TOURNAMENTS"
}

# Add at Position #1 (index 0)
data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)
