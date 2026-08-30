with open("news-2026-tour-championship-final-round-hovland-leads.html", "r") as f:
    html = f.read()

import re

# Update tee times
html = html.replace('<tr><td>Scottie Scheffler</td><td>-12</td><td>66</td><td>2:45 PM</td></tr>', '<tr><td>Scottie Scheffler</td><td>-12</td><td>66</td><td>2:27 PM</td></tr>')
html = html.replace('<tr><td>Brad Gotterup</td><td>-12</td><td>68</td><td>2:45 PM</td></tr>', '<tr><td>Brad Gotterup</td><td>-12</td><td>68</td><td>2:37 PM</td></tr>')
html = html.replace('<tr><td>Adam Scott</td><td>-12</td><td>65</td><td>2:35 PM</td></tr>', '<tr><td>Adam Scott</td><td>-12</td><td>65</td><td>2:27 PM</td></tr>')
html = html.replace('<tr><td>Ludvig Åberg</td><td>-12</td><td>66</td><td>2:35 PM</td></tr>', '<tr><td>Ludvig Åberg</td><td>-12</td><td>66</td><td>2:16 PM</td></tr>')
html = html.replace('<tr><td>Rory McIlroy</td><td>-10</td><td>63</td><td>2:15 PM</td></tr>', '<tr><td>Rory McIlroy</td><td>-10</td><td>63</td><td>2:16 PM</td></tr>')
html = html.replace('<tr><td>Cameron Young</td><td>-10</td><td>68</td><td>2:15 PM</td></tr>', '<tr><td>Cameron Young</td><td>-10</td><td>68</td><td>2:37 PM</td></tr>')

with open("news-2026-tour-championship-final-round-hovland-leads.html", "w") as f:
    f.write(html)
