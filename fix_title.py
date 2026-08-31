import re

with open('news-2026-scottie-scheffler-final-press-conference-answer.html', 'r') as f:
    html = f.read()

# Fix h1
new_h1 = "<h1>Scottie Scheffler's Final Press Conference Answer of the Season</h1>"
html = re.sub(r'<h1>2026 Tour Championship Tee Times: Round 4 at East Lake</h1>', new_h1, html)

# Fix standfirst
new_standfirst = '<p class="standfirst">He\'d just won $10 million, a second FedEx Cup, and passed Tiger Woods on the all-time money list. Then he spent his last answers of the year talking about wind and about travelling with his kids.</p>'
html = re.sub(r'<p class="standfirst">.*?</p>', new_standfirst, html)

# Fix category badge
html = re.sub(r'<span class="cat">PGA TOUR · NEWS</span>', '<span class="cat">PGA TOUR • SEASON RETROSPECTIVE</span>', html)

# Fix figure caption and ensure image is correct (it should be the v2 image from before!)
hero_html = """<figure class="lead-img">
          <img src="/public/scottie-scheffler-final-press-conference-answer-2026-v2.webp" alt="Scottie Scheffler at the media center press conference podium after winning the 2026 Tour Championship." width="1200" height="675" style="aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:8px;">
          <figcaption>SCOTTIE SCHEFFLER REFLECTED ON HIS HISTORIC 2026 SEASON WITH A GROUNDED PRESS CONFERENCE AT EAST LAKE. PHOTO: RAWGOLF</figcaption>
        </figure>"""
html = re.sub(r'<figure class="lead-img">.*?</figure>', hero_html, html, flags=re.DOTALL)

with open('news-2026-scottie-scheffler-final-press-conference-answer.html', 'w') as f:
    f.write(html)
