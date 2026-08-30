import json

with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "canonical": "/news-2026-hovland-leads-tour-championship-final-day",
  "alias_of": "",
  "slug": "news-2026-hovland-leads-tour-championship-final-day",
  "url": "/news-2026-hovland-leads-tour-championship-final-day",
  "title": "Hovland Leads the Tour Championship by One Into Sunday | GOLFRAW",
  "excerpt": "He closed with six putts from 7 feet or longer to lead by one. Scheffler's three back, McIlroy shot 63, and nobody agrees on Sunday's tee times.",
  "category": ["TOURNAMENTS", "PGA TOUR", "NEWS"],
  "date": "2026-08-30",
  "image": "/public/hovland-leads-tour-championship-final-day-2026.webp",
  "keywords": "Viktor Hovland, Tour Championship Final Round, Scottie Scheffler, Rory McIlroy 63, Ryan Gerard, East Lake",
  "category_source": "override",
  "section": "TOURNAMENTS"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)
