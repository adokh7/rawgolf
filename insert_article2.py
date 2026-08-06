import sys

pga_snippet = """
        <a class="guide-card" href="/news-2026-memphis-championship-series-fedexcup">
          <img width="1672" height="941" src="/public/memphis-championship-series-fedexcup.webp" alt="The Bigger Story Isn't Memphis. It's Whether the FedExCup Survives." class="card-thumb" loading="lazy">
          <div class="card-body">
            <div class="badge-row">
              <span class="badge badge-red">PGA TOUR</span>
              <span class="badge badge-green">New</span>
            </div>
            <h3>The Bigger Story Isn't Memphis. It's Whether the FedExCup Survives.</h3>
            <p>Memphis loses top-tier status in 2028. But FedEx's deal covers the points race and postseason too, and it expires in 2027. What that really puts at risk.</p>
            <div class="card-meta">
              <span class="author">BY GOLFRAW Editorial | AUG 06 2026</span>
            </div>
          </div>
        </a>"""

with open('pga-tour.html', 'r') as f:
    content = f.read()
target = '<div class="guide-grid">'
if target in content:
    content = content.replace(target, target + pga_snippet, 1)
    with open('pga-tour.html', 'w') as f:
        f.write(content)
    print("Updated pga-tour.html")

search_snippet = """  {t:"The Bigger Story Isn't Memphis. It's Whether the FedExCup Survives.", l:"/news-2026-memphis-championship-series-fedexcup", img:"/public/memphis-championship-series-fedexcup.webp", cat:"PGA TOUR", date:"AUG 06 2026", author:"GOLFRAW Editorial", x:"Memphis loses top-tier status in 2028. But FedEx's deal covers the points race and postseason too, and it expires in 2027. What that really puts at risk.", k:"fedex st jude championship 2028, pga tour championship series, memphis pga tour, fedexcup ending, challenger series, tpc southwind"},
"""

with open('search.html', 'r') as f:
    content = f.read()
target = 'const articles = [\n'
if target in content:
    content = content.replace(target, target + search_snippet, 1)
    with open('search.html', 'w') as f:
        f.write(content)
    print("Updated search.html")
