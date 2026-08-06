import sys

snippet = """
        <article class="news">
          <a href="/news-2026-memphis-championship-series-fedexcup" style="display:block; margin-bottom:16px;">
            <img src="/public/memphis-championship-series-fedexcup.webp" alt="The Bigger Story Isn't Memphis. It's Whether the FedExCup Survives." style="width: 100%; border-radius: 4px;" loading="lazy">
          </a>
          <div class="cat" style="display:flex;align-items:center;gap:8px;">
            <span style="background:var(--fairway);">PGA TOUR</span>
          </div>
          <h3><a href="/news-2026-memphis-championship-series-fedexcup">The Bigger Story Isn't Memphis. It's Whether the FedExCup Survives.</a></h3>
          <p>Memphis loses top-tier status in 2028. But FedEx's deal covers the points race and postseason too, and it expires in 2027. What that really puts at risk.</p>
          <div class="meta"><span>BY GOLFRAW Editorial</span><span class="mono">AUG 06 2026</span></div>
        </article>"""

files_to_update = ['news.html', 'pga-tour.html', 'search.html']

for filename in files_to_update:
    try:
        with open(filename, 'r') as f:
            content = f.read()
        
        target = '<div class="news-grid">'
        if target in content:
            new_content = content.replace(target, target + snippet, 1)
            with open(filename, 'w') as f:
                f.write(new_content)
            print(f"Updated {filename}")
        else:
            print(f"Could not find target in {filename}")
    except Exception as e:
        print(f"Error on {filename}: {e}")
