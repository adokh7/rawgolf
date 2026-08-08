import json

file_path = "articles.json"
with open(file_path, "r") as f:
    data = json.load(f)

new_article = {
    "url": "/news-2026-liv-golf-investor-bc-partners-dechambeau",
    "title": "The Mystery Investor Has a Name. It Lends Money to Bryson DeChambeau's Agency.",
    "category": "LIV GOLF",
    "date": "2026-08-08",
    "image": "/public/liv-golf-bc-partners-dechambeau.webp",
    "snippet": "Bloomberg and the FT name BC Partners as LIV's investor \u2014 a lender to Bryson DeChambeau's agency. And LIV quietly lost its feeder tour to the PGA Tour.",
    "keywords": "liv golf investor bc partners, liv golf funding 2027, liv golf asian tour, liv golf 2.0 schedule, bryson dechambeau liv contract",
    "canonical": "/news-2026-liv-golf-investor-bc-partners-dechambeau",
    "alias_of": "",
    "slug": "news-2026-liv-golf-investor-bc-partners-dechambeau",
    "excerpt": "Bloomberg and the FT name BC Partners as LIV's investor \u2014 a lender to Bryson DeChambeau's agency. And LIV quietly lost its feeder tour to the PGA Tour."
}

data["articles"].insert(0, new_article)
data["count"] = len(data["articles"])

with open(file_path, "w") as f:
    json.dump(data, f, indent=2)

