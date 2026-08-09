import json
import os

filepath = "/Users/adnan/Desktop/golf/articles.json"
with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

new_article = {
  "url": "/news-2026-michigan-golf-tournaments-rocket-classic-liv-cancelled",
  "title": "Michigan Had Two Elite Golf Tournaments This Year. Soon It May Have None.",
  "category": "PGA TOUR",
  "date": "AUG 09 2026",
  "image": "/public/michigan-golf-tournaments-rocket-classic-liv.webp",
  "snippet": "The Rocket Classic is gone and LIV's Michigan finale is reportedly cancelled — four weeks apart, for entirely different reasons. What Detroit actually lost.",
  "keywords": "liv golf michigan team championship cancelled, rocket classic ending, the cardinal saint johns golf, michigan pga tour 2027, liv golf michigan 2026"
}

# Add at the VERY TOP of the array
data["articles"].insert(0, new_article)

# Update the count
data["count"] = len(data["articles"])

with open(filepath, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
