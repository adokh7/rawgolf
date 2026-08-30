from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
article_path = ROOT / 'news-2026-wyndham-championship-brennan-fedexcup-bubble-resolution.html'

html = article_path.read_text(encoding='utf-8')

soup = BeautifulSoup(html, 'html.parser')

# Move meta-callout before lead-img
meta_callout = soup.find('div', class_='meta-callout')
lead_img = soup.find('figure', class_='lead-img')

if meta_callout and lead_img:
    # Remove meta_callout from its current position
    meta_callout.extract()
    # Insert it right before lead_img
    lead_img.insert_before(meta_callout)

article_path.write_text("<!DOCTYPE html>\n" + str(soup), encoding='utf-8')
