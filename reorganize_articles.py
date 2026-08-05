import re
import os

with open('search.html', 'r', encoding='utf-8') as f:
    search_html = f.read()

bad_entries = """  {
    title: "LIV Golf's Bankruptcy Story Has One Source | GOLFRAW",
    url: "/news-2026-liv-golf-bankruptcy-what-is-confirmed.html",
    date: "2026-08-02",
    tags: ["LIV Golf", "PIF", "Scott O'Neil", "Bankruptcy", "Jon Rahm", "Golf News", "GOLFRAW"]
  },
  {
    title: "Three 61s in Three Days at Detroit Golf Club | GOLFRAW",
    url: "/news-2026-detroit-golf-club-restoration-verdict.html",
    date: "2026-08-02",
    tags: ["Davis Riley", "Detroit Golf Club", "Rocket Classic", "PGA Tour", "Course Renovation", "Golf News", "GOLFRAW"]
  },

  {
    title: "She's Never Held a 54-Hole Major Lead. Now She Leads by 3. | GOLFRAW",
    url: "/yealimi-noh-royal-lytham-lead.html",
    date: "2026-08-02",
    tags: ["Yealimi Noh", "Haeran Ryu", "Nelly Korda", "Charley Hull", "AIG Women's Open", "Royal Lytham", "Golf News", "GOLFRAW"]
  },"""

good_entries = """  {t:"LIV Golf's Bankruptcy Story Has One Source | GOLFRAW", l:"/news-2026-liv-golf-bankruptcy-what-is-confirmed", img:"/public/liv-golf-staff-terminations-2026.webp", cat:"LIV Golf", date:"AUG 02 2026", author:"GOLFRAW Editorial", x:"LIV Golf's bankruptcy story has one source.", k:"LIV Golf, PIF, Scott O'Neil, Bankruptcy, Jon Rahm, Golf News, GOLFRAW"},
  {t:"Three 61s in Three Days at Detroit Golf Club | GOLFRAW", l:"/news-2026-detroit-golf-club-restoration-verdict", img:"/public/rocket-classic-2026-detroit-golf-club-renovation.webp", cat:"PGA Tour", date:"AUG 02 2026", author:"GOLFRAW Editorial", x:"Three 61s in three days at Detroit Golf Club.", k:"Davis Riley, Detroit Golf Club, Rocket Classic, PGA Tour, Course Renovation, Golf News, GOLFRAW"},
  {t:"She's Never Held a 54-Hole Major Lead. Now She Leads by 3. | GOLFRAW", l:"/yealimi-noh-royal-lytham-lead", img:"/public/aig-womens-open-2026-tee-times-lytham.webp", cat:"PGA Tour", date:"AUG 02 2026", author:"GOLFRAW Editorial", x:"Yealimi Noh leads by 3.", k:"Yealimi Noh, Haeran Ryu, Nelly Korda, Charley Hull, AIG Women's Open, Royal Lytham, Golf News, GOLFRAW"},"""

search_html = search_html.replace(bad_entries, good_entries)

articles = []
lines = search_html.split('\n')
for i, line in enumerate(lines):
    if line.strip().startswith('{t:'):
        t_m = re.search(r't:"(.*?)"', line)
        t = t_m.group(1) if t_m else ""
        
        l_m = re.search(r'l:"(.*?)"', line)
        l = l_m.group(1) if l_m else ""
        
        img_m = re.search(r'img:"(.*?)"', line)
        img = img_m.group(1) if img_m else ""
        
        cat_m = re.search(r'cat:"(.*?)"', line)
        cat = cat_m.group(1) if cat_m else ""
        
        date_m = re.search(r'date:"(.*?)"', line)
        date = date_m.group(1) if date_m else ""
        
        author_m = re.search(r'author:"(.*?)"', line)
        author = author_m.group(1) if author_m else ""
        
        x_m = re.search(r'x:"(.*?)"', line)
        x = x_m.group(1) if x_m else ""
        
        k_m = re.search(r'k:"(.*?)"', line)
        k = k_m.group(1) if k_m else ""
        
        if l.endswith('.html'):
            l = l[:-5]
        if not l.startswith('/'):
            l = '/' + l
            
        l_path = l
        guides = ['/news-2026-what-beginners-actually-search', '/news-2026-golf-deals-means-travel', '/what-to-wear-to-topgolf', '/golf-majors-guide', '/how-far-lpga-players-drive', '/swing-speed-guide', '/golf-swing-analysis-apps', '/what-is-topgolf', '/topgolf-first-timers', '/golf-clubs-for-beginners', '/what-does-lpga-stand-for', '/raw-golf-mindset']
        liv = ['/news-2026-liv-golf-secures-lead-investor', '/news-2026-cam-smith-liv-door-closed', '/news-2026-liv-golf-bankruptcy-what-is-confirmed', '/news-2026-liv-golf-staff-terminations', '/news-2026-liv-golf-250m-investment-rescue', '/news-2026-nick-faldo-liv-golf-comments', '/news-2026-lucas-herbert-liv-uk-record-asterisk', '/news-2026-lucas-herbert-liv-golf-uk-record-win', '/news-2026-lucas-herbert-liv-golf-uk-61', '/news-2026-thomas-pieters-q-school-liv-golf', '/news-2026-jon-rahm-liv-golf-investment-drama', '/news-2026-liv-golf-michigan-martin-kaymer']
        
        is_liv = False
        for liv_path in liv:
            if l_path == liv_path:
                is_liv = True
        if 'liv golf' in t.lower() or 'liv golf' in k.lower():
            is_liv = True
            
        is_guide = False
        for guide_path in guides:
            if l_path == guide_path:
                is_guide = True
        if 'guide' in cat.lower() or 'guides' in cat.lower():
            is_guide = True

        if is_guide:
            new_cat = "GUIDES"
        elif is_liv:
            new_cat = "LIV GOLF"
        else:
            new_cat = "PGA TOUR"
        
        new_line = re.sub(r'cat:".*?"', f'cat:"{new_cat}"', line)
        new_line = re.sub(r'l:".*?"', f'l:"{l}"', new_line)
        lines[i] = new_line
        
        articles.append({'t': t, 'l': l, 'img': img, 'cat': new_cat, 'date': date, 'author': author, 'x': x})

search_html = '\n'.join(lines)
with open('search.html', 'w', encoding='utf-8') as f:
    f.write(search_html)

def generate_news_card(a):
    return f'''        <article class="news">
          <a href="{a['l']}" style="display:block; margin-bottom:16px;">
            <img src="{a['img']}" alt="{a['t']}" style="width: 100%; border-radius: 4px;" loading="lazy">
          </a>
          <div class="cat" style="display:flex;align-items:center;gap:8px;">
            <span>{a['cat']}</span>
          </div>
          <h3><a href="{a['l']}">{a['t']}</a></h3>
          <p>{a['x']}</p>
          <div class="meta"><span>BY {a['author']}</span><span class="mono">{a['date']}</span></div>
        </article>'''

def generate_guide_card(a):
    return f'''        <a class="guide-card" href="{a['l']}">
          <img width="1672" height="941" src="{a['img']}" alt="{a['t']}" class="card-thumb" loading="lazy">
          <div class="card-body">
            <div class="badge-row">
              <span class="badge badge-red">{a['cat']}</span>
              <span class="badge badge-green">New</span>
            </div>
            <h3>{a['t']}</h3>
            <p>{a['x']}</p>
            <div class="card-meta">
              <span class="author">BY {a['author']} | {a['date']}</span>
              <span class="card-cta">Read Guide →</span>
            </div>
          </div>
        </a>'''

def replace_grid(filepath, articles_subset, card_generator, grid_class):
    if not os.path.exists(filepath): return
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    start_str = f'<div class="{grid_class}">'
    start_idx = html.find(start_str)
    if start_idx == -1: return
    start_idx += len(start_str)
    
    depth = 1
    i = start_idx
    while i < len(html) and depth > 0:
        if html[i:i+4] == '<div':
            depth += 1
            i += 4
        elif html[i:i+5] == '</div':
            depth -= 1
            i += 5
        else:
            i += 1
    
    end_idx = i - 5 
    
    cards_html = "\n" + "\n\n".join(card_generator(a) for a in articles_subset) + "\n      "
    
    new_html = html[:start_idx] + cards_html + html[end_idx:]
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_html)

replace_grid('news.html', articles, generate_news_card, 'news-grid')
guides_articles = [a for a in articles if a['cat'] == 'GUIDES']
replace_grid('guides.html', guides_articles, generate_guide_card, 'guide-grid')
liv_articles = [a for a in articles if a['cat'] == 'LIV GOLF']
replace_grid('liv-golf.html', liv_articles, generate_news_card, 'news-grid')
pga_articles = [a for a in articles if a['cat'] == 'PGA TOUR']
replace_grid('pga-tour.html', pga_articles, generate_guide_card, 'guide-grid')
replace_grid('tournaments.html', pga_articles, generate_guide_card, 'guide-grid')
