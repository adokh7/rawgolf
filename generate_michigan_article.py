import re
from scripts.fix_template_metadata import finalize_html

with open('/Users/adnan/Desktop/golf/article-template.html', 'r') as f:
    template = f.read()

# Meta replacements
template = re.sub(r'<title>.*?</title>', '<title>Michigan Pro Golf Faces an Uncertain Future in 2027 | GolfRaw</title>', template)
template = re.sub(r'<meta name="description"\s*content=".*?">', '<meta name="description"\n    content="Michigan could lose three men\'s pro golf events before 2027. See the latest on the Rocket Classic, LIV Golf, Ally Challenge and LPGA stops.">', template)
template = re.sub(r'<link rel="canonical" href=".*?">', '<link rel="canonical" href="https://www.golfraw.com/news-2026-michigan-golf-tournaments-rocket-classic-liv-cancelled">', template)
template = re.sub(r'<meta property="og:title" content=".*?" />', '<meta property="og:title" content="Michigan Pro Golf Faces an Uncertain Future in 2027 | GolfRaw" />', template)
template = re.sub(r'<meta property="og:description" content=".*?" />', '<meta property="og:description" content="Michigan could lose three men\'s pro golf events before 2027. See the latest on the Rocket Classic, LIV Golf, Ally Challenge and LPGA stops." />', template)
template = re.sub(r'<meta property="og:url" content=".*?" />', '<meta property="og:url" content="https://www.golfraw.com/news-2026-michigan-golf-tournaments-rocket-classic-liv-cancelled" />', template)
template = re.sub(r'<meta property="og:image" content=".*?">', '<meta property="og:image" content="https://www.golfraw.com/public/michigan-pro-golf-2027-uncertain-future.webp">', template)
template = re.sub(r'<meta name="twitter:title" content=".*?">', '<meta name="twitter:title" content="Michigan Pro Golf Faces an Uncertain Future in 2027 | GolfRaw">', template)
template = re.sub(r'<meta name="twitter:description"\s*content=".*?">', '<meta name="twitter:description"\n    content="Michigan could lose three men\'s pro golf events before 2027. See the latest on the Rocket Classic, LIV Golf, Ally Challenge and LPGA stops.">', template)
template = re.sub(r'<meta name="twitter:image" content=".*?">', '<meta name="twitter:image" content="https://www.golfraw.com/public/michigan-pro-golf-2027-uncertain-future.webp">', template)
template = re.sub(r'<meta property="article:published_time" content=".*?" />', '<meta property="article:published_time" content="2026-08-09T07:30:00+02:00" />', template)

new_article = """<article>
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/pga-tour">PGA Tour</a> / <span>Michigan</span>
        </nav>

        <header class="article-head">
          <span class="cat">PGA TOUR · MICHIGAN</span>
          <h1>Michigan Pro Golf Faces an Uncertain Future in 2027</h1>
          <p class="standfirst">Michigan hosted five prominent tour events in 2026 across the PGA Tour, PGA Tour Champions, LIV Golf, and LPGA Tour. By 2027, only two LPGA stops may have a secure place on the calendar if the LIV event falls through and the Ally Challenge cannot reach a new agreement.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>AUG 09 2026</b></span>
          </div>
        </header>

        <div class="meta-callout" style="border-left: 4px solid #10b981; padding-left: 12px; margin: 16px 0;">
          <strong>Michigan Golf Outlook:</strong> August 9, 2026 | State Tournament Calendar & Contract Status
        </div>

        <figure class="lead-img">
          <img src="/public/michigan-pro-golf-2027-uncertain-future.webp" alt="Michigan Pro Golf 2027 Calendar Uncertainty" />
        </figure>

        <div class="article-body">
          <h2>The Rocket Classic Has Ended After Eight Years</h2>
          <p>The Rocket Classic closed its eight-year run on August 2, when Michael Thorbjornsen shot a final-round 63 to finish at 18 under par, edging Xander Schauffele by two strokes for his first PGA Tour victory. Thorbjornsen won the final edition, completing a run at Detroit Golf Club that began in 2019.</p>

          <p>Rocket confirmed in June that the 2026 tournament would be its last, leaving Detroit without a PGA Tour date for 2027. While reports connect the decision to the rising costs of securing a top-tier position on the PGA Tour calendar, Rocket offered no official public explanation. The PGA Tour has expressed interest in returning to Metro Detroit, but a replacement event, venue, and title sponsor remain unannounced.</p>

          <h2>Is LIV Golf Michigan Still Happening?</h2>
          <p>On paper, yes. The official LIV Golf schedule still lists the Team Championship Michigan for August 27–30 at The Cardinal at Saint John's in Plymouth, with tickets remaining on sale. However, operational doubts persist.</p>

          <p>LIV Golf CEO Scott O'Neil announced on August 5 that the league had secured a lead investor expected to support operations into 2027, though he did not name the investor or disclose financial terms. Asked about the Michigan finale, O'Neil described the situation as "very fluid" with no firm updates. On-site visits to The Cardinal in early August documented no buildout for a major tournament setup, creating uncertainty for ticket holders and vendors alike.</p>

          <h2>The Ally Challenge Fighting for a 2027 Return</h2>
          <p>Michigan's next men's professional event is the Ally Challenge at Warwick Hills Golf & Country Club in Grand Blanc, scheduled for August 24–30 on the PGA Tour Champions circuit. This marks the final year of the tournament's current contract.</p>

          <p>Negotiations between tour officials and tournament management remain active. Organizers point to over $10 million in total charitable giving generated since 2018 alongside major fan draws like Keith Urban performing after the second round. However, an official contract extension for 2027 has not yet been finalized.</p>

          <h2>LPGA Tour Provides Clear Stability</h2>
          <p>In contrast to the men's events, Michigan's LPGA stops carry long-term security. The Dow Championship at Midland Country Club—won in 2026 by Yana Wilson and Gina Kim—holds a firm contract extension through 2029. Meanwhile, the Meijer LPGA Classic at Blythefield Country Club remains a staple of the summer schedule with no exit announced.</p>

          <div class="faq-section">
            <h2>Frequently Asked Questions</h2>

            <h3>Will the PGA Tour return to Detroit in 2027?</h3>
            <p>No. The Rocket Classic ended after the 2026 tournament, and its schedule slot has been assigned to a new event in Napa, California. The PGA Tour hopes to return to Metro Detroit in 2028 or later.</p>

            <h3>Is LIV Golf's Michigan Team Championship confirmed for 2026?</h3>
            <p>The event remains listed on LIV Golf's website for August 27–30 at The Cardinal in Plymouth, but tournament leadership described the status as "fluid" and no major buildout had begun by early August.</p>

            <h3>Will the Ally Challenge return to Warwick Hills in 2027?</h3>
            <p>Contract negotiations for the PGA Tour Champions event are ongoing, but no official extension beyond 2026 has been announced.</p>

            <h3>Which professional golf tournaments are secured in Michigan for 2027?</h3>
            <p>The Dow Championship is contracted through 2029, and the Meijer LPGA Classic remains established on the LPGA Tour calendar.</p>
          </div>

          <h2>The Raw Take</h2>
          <p>Michigan is witnessing how rapidly a premier golf market can reshape. While fan support and course conditions remain strong across Detroit and Grand Blanc, corporate sponsorship transitions and league restructures determine where professional tournaments land. For Michigan golf fans, the LPGA Tour currently offers the state's most reliable anchor.</p>

          <nav class="tag-row" aria-label="Article tags">
            <a href="#">Michigan</a>
            <a href="#">PGA Tour</a>
            <a href="#">LIV Golf</a>
            <a href="#">LPGA Tour</a>
          </nav>
        </div>
      </article>"""

template = re.sub(r'<article>.*?</article>', new_article, template, flags=re.DOTALL)

template = finalize_html(
    template,
    '/Users/adnan/Desktop/golf/news-2026-michigan-golf-tournaments-rocket-classic-liv-cancelled.html',
    force=True,
)

with open('/Users/adnan/Desktop/golf/news-2026-michigan-golf-tournaments-rocket-classic-liv-cancelled.html', 'w') as f:
    f.write(template)

print("Article generated.")
