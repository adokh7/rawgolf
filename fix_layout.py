from bs4 import BeautifulSoup

with open('/Users/adnan/Desktop/golf/news-2026-wyndham-championship-brennan-fedexcup-bubble-resolution.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Move meta-callout before lead-img
meta_callout = soup.find('div', class_='meta-callout')
lead_img = soup.find('figure', class_='lead-img')

if meta_callout and lead_img:
    # Remove meta_callout from its current position
    meta_callout.extract()
    # Insert it right before lead_img
    lead_img.insert_before(meta_callout)

with open('/Users/adnan/Desktop/golf/news-2026-wyndham-championship-brennan-fedexcup-bubble-resolution.html', 'w', encoding='utf-8') as f:
    f.write("<!DOCTYPE html>\n" + str(soup))
