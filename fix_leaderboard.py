import re
with open("news-2026-tour-championship-final-round-hovland-leads.html", "r") as f:
    html = f.read()

table_html = """
          <h2>Leaderboard Summary</h2>
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>Player</th>
                  <th>Score</th>
                  <th>Round 3</th>
                </tr>
              </thead>
              <tbody>
                <tr><td>Viktor Hovland</td><td>-15</td><td>66</td></tr>
                <tr><td>Ryan Gerard</td><td>-14</td><td>67</td></tr>
                <tr><td>Scottie Scheffler</td><td>-12</td><td>66</td></tr>
                <tr><td>Brad Gotterup</td><td>-12</td><td>68</td></tr>
                <tr><td>Adam Scott</td><td>-12</td><td>65</td></tr>
                <tr><td>Ludvig Åberg</td><td>-12</td><td>66</td></tr>
                <tr><td>Rory McIlroy</td><td>-10</td><td>63</td></tr>
                <tr><td>Cameron Young</td><td>-10</td><td>68</td></tr>
              </tbody>
            </table>
          </div>
"""

# Insert table after Key Takeaways
html = html.replace('</div>\n\n          <h2>How Hovland', '</div>\n' + table_html + '\n          <h2>How Hovland')

with open("news-2026-tour-championship-final-round-hovland-leads.html", "w") as f:
    f.write(html)
