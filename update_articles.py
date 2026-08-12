import json

with open('articles.json', 'r') as f:
    data = json.load(f)

new_entry = {
  "url": "/news-2026-lexi-thompson-pregnant-baby-daughter-lpga",
  "title": "Lexi Thompson Is Expecting a Daughter. She's the Fourth Name in Two Years.",
  "category": "LPGA TOUR",
  "date": "AUG 11 2026",
  "image": "/public/lexi-thompson-pregnant-baby-daughter-2026.webp",
  "snippet": "Lexi Thompson and Max Provost are expecting a baby girl in February 2027. Why the coverage of pregnancy in women's golf has changed — and what still hasn't.",
  "keywords": "lexi thompson pregnant, lexi thompson baby, lexi thompson husband, is lexi thompson retired, lexi thompson 2026 season, lpga maternity policy"
}

data['articles'].insert(0, new_entry)

with open('articles.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Updated articles.json")
