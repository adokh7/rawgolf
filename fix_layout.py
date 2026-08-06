import re
from bs4 import BeautifulSoup

filepath = 'news-2026-wyndham-fedexcup-bubble-koivun.html'
with open(filepath, 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

main = soup.find('main')

# Build new clean layout container
new_layout = BeautifulSoup("""
<div class="wrap" style="max-width: 800px; margin: 0 auto; padding: 40px 20px;">
</div>
""", 'html.parser').div

# Extract the existing elements
nav = soup.find('nav', class_='crumbs')
header = soup.find('header', class_='article-head')
img = main.find('img', alt="Jackson Koivun at Wyndham Championship")
if not img:
    # try looking for any img with the source
    img = main.find('img')
body = soup.find('div', class_='article-body')

# Assemble the new single column layout
new_layout.append(nav)
new_layout.append(header)
if img:
    img['style'] = "width: 100%; max-width: 100%; border-radius: 4px; margin: 24px 0 40px;"
    new_layout.append(img)
new_layout.append(body)

# Replace the old broken grid with the new single column layout
old_wrap = main.find('div', class_='wrap page-grid')
old_wrap.replace_with(new_layout)

# Also ensure max-width of article-body and standfirst are 100% or unset so they fill the 800px container
# Since we are overriding styles, we can just inject a quick style tag inside main
style_tag = soup.new_tag("style")
style_tag.string = ".article-body, .standfirst { max-width: 100% !important; }"
main.insert(0, style_tag)

final_html = "<!DOCTYPE html>\n" + str(soup)
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(final_html)

