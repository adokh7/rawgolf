import json

with open('articles.json', 'r') as f:
    data = json.load(f)

new_article = {
  "canonical": "/news-2026-memphis-championship-series-fedexcup",
  "alias_of": "",
  "slug": "news-2026-memphis-championship-series-fedexcup",
  "url": "/news-2026-memphis-championship-series-fedexcup",
  "title": "The Bigger Story Isn't Memphis. It's Whether the FedExCup Survives.",
  "excerpt": "Memphis loses top-tier status in 2028. But FedEx's deal covers the points race and postseason too, and it expires in 2027. What that really puts at risk.",
  "category": "PGA TOUR",
  "date": "2026-08-06",
  "image": "/public/memphis-championship-series-fedexcup.webp",
  "category_source": "manual",
  "section": "PGA TOUR",
  "keywords": "fedex st jude championship 2028, pga tour championship series, memphis pga tour, fedexcup ending, challenger series, tpc southwind"
}

data['articles'].insert(0, new_article)

with open('articles.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Updated articles.json")
