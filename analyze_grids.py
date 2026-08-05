import re
from bs4 import BeautifulSoup
import os

files = ['news.html', 'guides.html', 'liv-golf.html', 'pga-tour.html', 'tournaments.html']
for file in files:
    if os.path.exists(file):
        with open(file, 'r') as f:
            soup = BeautifulSoup(f, 'html.parser')
            grids = soup.find_all(class_=['news-grid', 'guide-grid'])
            print(f"--- {file} ---")
            for grid in grids:
                links = grid.find_all('a', href=True)
                hrefs = set(link['href'] for link in links if not link['href'].startswith('#') and 'author' not in link['href'])
                for h in hrefs:
                    print(h)
