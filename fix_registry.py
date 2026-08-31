import json

with open("articles.json", "r") as f:
    data = json.load(f)

# Find the article
for article in data["articles"]:
    if article["slug"] == "news-2026-scottie-scheffler-final-press-conference-answer":
        article["title"] = "Scottie Scheffler's Final Press Conference Answer of the Season"
        article["excerpt"] = "He'd just won $10 million, a second FedEx Cup, and passed Tiger Woods on the all-time money list. Then he spent his last answers of the year talking about wind and about travelling with his kids."

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)
