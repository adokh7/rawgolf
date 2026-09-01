import json

with open('articles.json', 'r') as f:
    data = json.load(f)

new_article = {
    "canonical": "/news-2026-jon-rahm-liv-money-owed",
    "alias_of": "",
    "slug": "news-2026-jon-rahm-liv-money-owed",
    "url": "/news-2026-jon-rahm-liv-money-owed",
    "title": "Jon Rahm's LIV Money: What He's Owed and Who Gets Paid | GOLFRAW",
    "excerpt": "Three outlets give three different figures for what he's owed. The bigger question is where a player ranks when the bankruptcy queue forms.",
    "category": ["LIV GOLF", "MONEY", "NEWS"],
    "date": "2026-09-01",
    "image": "/news-2026-jon-rahm-liv-money-owed.webp",
    "keywords": "LIV GOLF, MONEY, NEWS, Jon Rahm",
    "category_source": "override",
    "section": "LIV GOLF"
}

data['articles'].insert(0, new_article)
data['count'] += 1

with open('articles.json', 'w') as f:
    json.dump(data, f, indent=2)
