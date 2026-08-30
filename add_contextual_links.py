with open("news-2026-tour-championship-final-round-hovland-leads.html", "r") as f:
    html = f.read()

# Sunday tee times
html = html.replace('Sunday will not be a survival test', 'Sunday will not be a survival test (check the <a href="/news-2026-tour-championship-tee-times-round-4">Sunday Tee Times</a>)')

# Cameron Young's 62
html = html.replace('tied with Cameron Young.', 'tied with Cameron Young (who <a href="/news-2026-cameron-young-new-putter-62-tour-championship">shot a 62 in Round 3</a>).')

# Hovland's R2 co-lead
html = html.replace('Viktor Hovland took control of the Tour Championship late on Saturday.', '<a href="/news-2026-hovland-tie-for-lead-tour-championship">Following his strong Round 2 where he co-led</a>, Viktor Hovland took control of the Tour Championship late on Saturday.')

with open("news-2026-tour-championship-final-round-hovland-leads.html", "w") as f:
    f.write(html)
