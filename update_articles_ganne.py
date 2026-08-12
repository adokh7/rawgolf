import json

with open('articles.json', 'r') as f:
    data = json.load(f)

new_entry = {
  "url": "/news-2026-megha-ganne-lpga-debut-inkster-award",
  "title": "The Best Man in College Golf Gets a PGA Tour Card. The Best Woman Gets an Invitation.",
  "category": "LPGA TOUR",
  "date": "AUG 12 2026",
  "image": "/public/megha-ganne-lpga-debut-inkster-award-2026.webp",
  "snippet": "Megha Ganne won the Inkster Award and makes her LPGA debut in Portland. Men's college golf's top finishers get Tour cards. Hers gets one sponsor invite.",
  "keywords": "megha ganne, inkster award, megha ganne lpga debut, standard portland classic 2026, epson tour, lpga collegiate advancement pathway, pga tour university vs lpga"
}

data['articles'].insert(0, new_entry)

with open('articles.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Updated articles.json")
