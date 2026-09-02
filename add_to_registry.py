"""Historical registry helper for a route now permanently redirected.

The final-day story was consolidated into the canonical Tour Championship
article. Keep this helper safe to rerun so it cannot reintroduce the retired
route into the article registry.
"""

import json

REDIRECTED_ROUTE = "/news-2026-hovland-leads-tour-championship-final-day"

with open("articles.json", "r", encoding="utf-8") as f:
    data = json.load(f)

data["articles"] = [
    article for article in data["articles"]
    if article.get("url") != REDIRECTED_ROUTE
]

with open("articles.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
