import json

file_path = "articles.json"
with open(file_path, "r") as f:
    data = json.load(f)

new_article = {
  "url": "/news-2026-jason-day-wyndham-streak-ended",
  "title": "Jason Day's Streak Ended on a Friday in Greensboro",
  "category": "PGA TOUR",
  "date": "AUG 08 2026",
  "image": "/public/jason-day-wyndham-streak-ended.webp",
  "snippet": "Jason Day missed the cut at Sedgefield and ended 18 consecutive FedExCup Playoffs appearances. Bradley and Finau survived on the number. Who needs what now.",
  "keywords": "jason day fedexcup streak, wyndham championship cut line, keegan bradley playoffs, tony finau fedexcup, wyndham championship leaderboard",
  "canonical": "/news-2026-jason-day-wyndham-streak-ended",
  "alias_of": "",
  "slug": "news-2026-jason-day-wyndham-streak-ended",
  "excerpt": "Jason Day missed the cut at Sedgefield and ended 18 consecutive FedExCup Playoffs appearances. Bradley and Finau survived on the number. Who needs what now."
}

data["articles"].insert(0, new_article)
data["count"] = len(data["articles"])

with open(file_path, "w") as f:
    json.dump(data, f, indent=2)

