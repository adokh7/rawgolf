import json

with open('articles.json', 'r') as f:
    data = json.load(f)

new_entry = {
  "url": "/news-2026-espn-pga-tour-playoffs-coverage-fedex-st-jude",
  "title": "ESPN Last Showed the Tour Championship in 2006. It's Back the Year the Whole Thing Went Up in the Air.",
  "category": "PGA TOUR",
  "date": "AUG 12 2026",
  "image": "/public/espn-pga-tour-playoffs-fedex-st-jude-2026.webp",
  "snippet": "Scheffler and McIlroy are paired for two rounds in ESPN's morning window. ESPN hasn't shown the Tour Championship since 2006 — the year before the FedExCup.",
  "keywords": "fedex st jude featured groups, how to watch fedex st jude championship, scheffler mcilroy pairing, espn pga tour playoffs coverage, tpc southwind course"
}

data['articles'].insert(0, new_entry)

with open('articles.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Updated articles.json")
