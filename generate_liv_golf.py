with open('news.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('<title>Latest Golf News — Unfiltered Tour Coverage | GOLFRAW</title>', '<title>LIV Golf News | GOLFRAW</title>')
html = html.replace('<h1>Latest News</h1>', '<h1>LIV Golf</h1>')
html = html.replace('<p>Golf news without the press-release language. Every story is what it is.</p>', '<p>Unfiltered coverage of LIV Golf. Real analysis, no PR rewrites.</p>')
html = html.replace('RAWGOLF · SECTION 02', 'RAWGOLF · CATEGORY')
html = html.replace('canonical" href="https://www.golfraw.com/news', 'canonical" href="https://www.golfraw.com/liv-golf')

with open('liv-golf.html', 'w', encoding='utf-8') as f:
    f.write(html)
