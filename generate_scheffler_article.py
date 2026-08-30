import re
from scripts.fix_template_metadata import finalize_html

with open('/Users/adnan/Desktop/golf/article-template.html', 'r') as f:
    template = f.read()

# Meta replacements
template = re.sub(r'<title>.*?</title>', '<title>No, Scheffler Isn\'t at a Disadvantage at East Lake | GolfRaw</title>', template)
template = re.sub(r'<meta name="description"\s*content=".*?">', '<meta name="description"\n    content="The FedExCup leader no longer starts 10 under at the Tour Championship. That isn\'t a disadvantage — it\'s no advantage. Why the difference matters in 2026.">', template)
template = re.sub(r'<link rel="canonical" href=".*?">', '<link rel="canonical" href="https://www.golfraw.com/news-2026-scheffler-tour-championship-fedexcup-format-east-lake">', template)
template = re.sub(r'<meta property="og:title" content=".*?" />', '<meta property="og:title" content="No, Scheffler Isn\'t at a Disadvantage at East Lake | GolfRaw" />', template)
template = re.sub(r'<meta property="og:description" content=".*?" />', '<meta property="og:description" content="The FedExCup leader no longer starts 10 under at the Tour Championship. That isn\'t a disadvantage — it\'s no advantage. Why the difference matters in 2026." />', template)
template = re.sub(r'<meta property="og:url" content=".*?" />', '<meta property="og:url" content="https://www.golfraw.com/news-2026-scheffler-tour-championship-fedexcup-format-east-lake" />', template)
template = re.sub(r'<meta property="og:image" content=".*?">', '<meta property="og:image" content="https://www.golfraw.com/public/scheffler-tour-championship-fedexcup-east-lake.webp">', template)
template = re.sub(r'<meta name="twitter:title" content=".*?">', '<meta name="twitter:title" content="No, Scheffler Isn\'t at a Disadvantage at East Lake | GolfRaw">', template)
template = re.sub(r'<meta name="twitter:description"\s*content=".*?">', '<meta name="twitter:description"\n    content="The FedExCup leader no longer starts 10 under at the Tour Championship. That isn\'t a disadvantage — it\'s no advantage. Why the difference matters in 2026.">', template)
template = re.sub(r'<meta name="twitter:image" content=".*?">', '<meta name="twitter:image" content="https://www.golfraw.com/public/scheffler-tour-championship-fedexcup-east-lake.webp">', template)
template = re.sub(r'<meta property="article:published_time" content=".*?" />', '<meta property="article:published_time" content="2026-08-09T07:30:00+02:00" />', template)
template = re.sub(r'<meta property="article:section" content=".*?">', '<meta property="article:section" content="PGA TOUR">', template)

# Indexing Guardrail
template = re.sub(r'<meta name="robots" content=".*?"\s*>', '<meta name="robots" content="index, follow, max-image-preview:large">', template)

new_article = """<article>
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/pga-tour">PGA Tour</a> / <span>FedExCup</span>
        </nav>

        <header class="article-head">
          <span class="cat">PGA TOUR · TOUR CHAMPIONSHIP</span>
          <h1>Scheffler Isn't at a Disadvantage at the Tour Championship. He Just Has No Advantage.</h1>
          <p class="standfirst">There is a recurring argument that Scottie Scheffler will be at a distinct disadvantage at East Lake if he arrives as the FedExCup points leader. He won't be. He will have zero advantage—and that distinction is the entire point.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>AUG 09 2026</b></span>
          </div>
        </header>

        <div class="meta-callout" style="border-left: 4px solid #10b981; padding-left: 12px; margin: 16px 0;">
          <strong>FedExCup Format Analysis:</strong> August 9, 2026 | Tournament Rules & Playoff Dynamics
        </div>

        <figure class="lead-img">
          <img src="/public/scheffler-tour-championship-fedexcup-east-lake.webp" alt="Scottie Scheffler Tour Championship FedExCup East Lake Format" />
        </figure>

        <div class="article-body">
          <p>Under the staggered starting strokes format utilized previously, the points leader teed off on Thursday at 10 under par. Second place began at 8 under, scaling down to even par for the lower tier of the 30-man field. That system has been scrapped. All 30 players now tee off at level par, playing 72 holes of traditional stroke play where the lowest score claims both the Tour Championship and the FedExCup title.</p>

          <p>Scheffler does not lose ground relative to the field; he simply loses the 10-shot head start the previous rules provided for regular-season consistency. Nobody starts ahead of him. He no longer starts ahead of everyone else.</p>

          <h2>What the Old System Accomplished—and Why It Ended</h2>
          <p>The staggered start ran from 2019 through 2024. Its core objective was protecting season-long dominance: a player who won multiple times across nine months couldn't lose the overarching trophy due to one cold week in Atlanta.</p>

          <p>However, broadcast audiences widely disliked the handicap setup. Leaderboards felt disconnected from daily tournament play, with competitors shooting identical 68s but occupying vastly different tournament positions. When the PGA Tour shifted back to flat 72-hole stroke play, Scheffler himself voiced support, noting that equal footing on a demanding layout remains the purest way to crown a champion.</p>

          <h2>Nine Months of Golf to Earn a Tee Time</h2>
          <p>Under the current rules, points reset after the first two playoff stops (the FedEx St. Jude Championship and BMW Championship). Thirty players arrive at East Lake starting from scratch.</p>

          <ul>
            <li><strong>The Season's Reward:</strong> Nine months of consistent play earns access into the exclusive 30-man field.</li>
            <li><strong>The Playoff Reality:</strong> The season title is decided entirely by a single 72-hole shootout.</li>
          </ul>

          <p>Rory McIlroy, a three-time FedExCup champion, noted during the transition that while he favored giving the season's top performer an advantage, starting everyone at level par creates an undeniable clean slate.</p>

          <h2>Why the Debate Is Amplified in 2026</h2>
          <p>The debate lands with extra force this season due to Scheffler's specific statistical profile. Amassing double-digit top-five finishes and leading the FedExCup standings through steady contention, he exemplifies the exact consistency the old format rewarded.</p>

          <p>Under a level-par format, a player who contended weekly all summer enters Thursday with the exact same standing as someone who qualified via a late July victory. Whether that represents a flaws-and-all shootout or an unfair reset depends on whether you view the FedExCup as an Order of Merit or a playoff bracket.</p>

          <div class="faq-section">
            <h2>Frequently Asked Questions</h2>

            <h3>Does the FedExCup leader get starting strokes at the Tour Championship?</h3>
            <p>No. Starting strokes were eliminated. All 30 qualified players begin the Tour Championship at level par in a standard 72-hole stroke-play tournament.</p>

            <h3>Why were Tour Championship starting strokes removed?</h3>
            <p>The staggered handicap format was removed to simplify the leaderboard for fans and ensure the player shooting the lowest 72-hole score wins the event.</p>

            <h3>How do players qualify for the Tour Championship in 2026?</h3>
            <p>The top 70 in FedExCup points enter the FedEx St. Jude Championship, the top 50 advance to the BMW Championship, and the top 30 reach East Lake for the Tour Championship.</p>

            <h3>Has Scottie Scheffler won the FedExCup?</h3>
            <p>Yes, Scheffler secured his first FedExCup title at East Lake in 2024.</p>
          </div>

          <h2>The Raw Take</h2>
          <p>Golf has struggled for two decades to blend a season-long points race with a dramatic playoff finale. Equalizing the field at East Lake prioritizes clear television drama over season-long credit. Scheffler isn't playing at a handicap—he is playing the exact same game as 29 other golfers, where four good days decide the trophy.</p>

          <nav class="tag-row" aria-label="Article tags">
            <a href="#">Scottie Scheffler</a>
            <a href="#">Tour Championship</a>
            <a href="#">FedExCup</a>
            <a href="#">PGA Tour</a>
          </nav>
        </div>
      </article>"""

template = re.sub(r'<article>.*?</article>', new_article, template, flags=re.DOTALL)

template = finalize_html(
    template,
    '/Users/adnan/Desktop/golf/news-2026-scheffler-tour-championship-fedexcup-format-east-lake.html',
    force=True,
)

with open('/Users/adnan/Desktop/golf/news-2026-scheffler-tour-championship-fedexcup-format-east-lake.html', 'w') as f:
    f.write(template)

print("Article generated.")
