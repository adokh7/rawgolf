import re

with open('/Users/adnan/Desktop/golf/article-template.html', 'r') as f:
    template = f.read()

# Meta replacements
template = re.sub(r'<title>.*?</title>', '<title>Lowest Round in LET History Friday. Four-Putt Sunday. | GolfRaw</title>', template)
template = re.sub(r'<meta name="description"\s*content=".*?">', '<meta name="description"\n    content="Charley Hull shot 62 to equal the lowest round in Ladies European Tour history, then four-putted the 17th while leading. Anna Huang, 17, eagled the last.">', template)
template = re.sub(r'<link rel="canonical" href=".*?">', '<link rel="canonical" href="https://www.golfraw.com/news-2026-charley-hull-four-putt-anna-huang-pif-london">', template)
template = re.sub(r'<meta property="og:title" content=".*?" />', '<meta property="og:title" content="Lowest Round in LET History Friday. Four-Putt Sunday. | GolfRaw" />', template)
template = re.sub(r'<meta property="og:description" content=".*?" />', '<meta property="og:description" content="Charley Hull shot 62 to equal the lowest round in Ladies European Tour history, then four-putted the 17th while leading. Anna Huang, 17, eagled the last." />', template)
template = re.sub(r'<meta property="og:url" content=".*?" />', '<meta property="og:url" content="https://www.golfraw.com/news-2026-charley-hull-four-putt-anna-huang-pif-london" />', template)
template = re.sub(r'<meta property="og:image" content=".*?">', '<meta property="og:image" content="https://www.golfraw.com/public/charley-hull-four-putt-pif-london.webp">', template)
template = re.sub(r'<meta name="twitter:title" content=".*?">', '<meta name="twitter:title" content="Lowest Round in LET History Friday. Four-Putt Sunday. | GolfRaw">', template)
template = re.sub(r'<meta name="twitter:description"\s*content=".*?">', '<meta name="twitter:description"\n    content="Charley Hull shot 62 to equal the lowest round in Ladies European Tour history, then four-putted the 17th while leading. Anna Huang, 17, eagled the last.">', template)
template = re.sub(r'<meta name="twitter:image" content=".*?">', '<meta name="twitter:image" content="https://www.golfraw.com/public/charley-hull-four-putt-pif-london.webp">', template)
template = re.sub(r'<meta property="article:published_time" content=".*?" />', '<meta property="article:published_time" content="2026-08-09T07:30:00+02:00" />', template)
template = re.sub(r'<meta property="article:section" content=".*?">', '<meta property="article:section" content="WOMEN\'S GOLF">', template)

new_article = """<article>
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/tournaments">Tournaments</a> / <span>LET Tour</span>
        </nav>

        <header class="article-head">
          <span class="cat">WOMEN'S GOLF · PIF LONDON</span>
          <h1>She Shot the Lowest Round in Tour History on Friday. On Sunday She Four-Putted.</h1>
          <p class="standfirst">Charley Hull stood on the 17th tee at Centurion Club on Sunday with a one-shot lead, three birdies in her previous four holes, and a roaring home crowd. Minutes later, a four-putt double bogey erased two shots and handed victory away.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>AUG 09 2026</b></span>
          </div>
        </header>

        <div class="meta-callout" style="border-left: 4px solid #10b981; padding-left: 12px; margin: 16px 0;">
          <strong>LET Tour Dynamics:</strong> August 9, 2026 | Tournament Standings & Solheim Cup Readiness
        </div>

        <figure class="lead-img">
          <img src="/public/charley-hull-four-putt-pif-london.webp" alt="Charley Hull Four Putt Centurion Club Anna Huang" />
        </figure>

        <div class="article-body">
          <h2>From Record-Setting Brilliance to Sunday Heartbreak</h2>
          <p>Hull opened her tournament with an uninspiring 74 before putting on a ball-striking clinic on Friday. Her second-round 62—featuring an eagle and nine birdies in a bogey-free performance—broke the Centurion Club course record set by Georgia Hall in 2021 and tied the all-time Ladies European Tour record alongside Haeran Ryu, Jessica Korda, Alison Lee, and Karrie Webb.</p>

          <p>She followed up with a 67 on Saturday to sit three shots behind 17-year-old Anna Huang heading into the final round. Hull stormed back on Sunday's back nine with three birdies in a four-hole stretch, taking the outright lead at 16 under. Then came the fateful 17th green, where four putts derailed her march toward a first professional victory on English soil.</p>

          <h2>Anna Huang's Historic Distinction</h2>
          <p>While attention focused on Hull's green-side misstep, 17-year-old Canadian phenom Anna Huang delivered a legendary finish. Leading from round one, Huang answered Hull's rally by making an eagle on the par-5 18th hole—her fourth eagle on that exact hole in four days—to finish at 22 under par and claim the $300,000 top prize.</p>

          <p>The victory makes Huang the youngest player in Ladies European Tour history to reach four career titles, showcasing poise well beyond her years when playing in front of partisan crowds backing her opponent.</p>

          <h2>The Anatomy of a Four-Putt and What Amateur Golfers Can Learn</h2>
          <p>A four-putt rarely stems from four faulty strokes in a row. It typically originates with aggressive distance control on the initial long putt, followed by defensive acceleration on the second, leaving a tense short putt hit under emotional strain.</p>

          <ul>
            <li><strong>Distance Control First:</strong> On putts outside 30 feet, treat a 3-foot circle around the cup as your primary target rather than trying to force the ball into the back of the cup.</li>
            <li><strong>Reset After a Poor First Stroke:</strong> When a lag putt goes wrong, take extra time to reset your breath and routine before attempting the second stroke to avoid reactive rushing.</li>
          </ul>

          <h2>Solheim Cup Outlook for Team Europe</h2>
          <p>Hull's finish arrives at a critical juncture as she prepares for her eighth Solheim Cup appearance at Bernardus Golf in the Netherlands this September. Managing back and ankle lingering issues throughout the year, Hull now gets a needed week off to recalibrate her putting setup before joining European Captain Anna Nordqvist's squad.</p>

          <div class="faq-section">
            <h2>Frequently Asked Questions</h2>

            <h3>Who won the 2026 PIF London Championship?</h3>
            <p>17-year-old Anna Huang won the tournament at 22 under par after making an eagle on the 18th hole, securing her fourth Ladies European Tour title.</p>

            <h3>What happened to Charley Hull on the 17th hole?</h3>
            <p>Holding a one-shot lead, Hull four-putted the 17th green for a double bogey, falling two shots behind Huang with one hole remaining.</p>

            <h3>What was Charley Hull's course record score at Centurion Club?</h3>
            <p>Hull shot an 11-under 62 in the second round, breaking the course record and matching the lowest round in LET history.</p>

            <h3>Is Charley Hull qualified for the 2026 Solheim Cup?</h3>
            <p>Yes, Hull qualified automatically for Team Europe, which will compete at Bernardus Golf in September 2026.</p>
          </div>

          <h2>The Raw Take</h2>
          <p>Golf logic can be merciless: an 11-under 62 on Friday counts for no more than four putts on Sunday. Charley Hull showed the highest ceiling in women's golf this week, but her upcoming Solheim Cup campaign will depend entirely on how quickly she can stabilize distance control on lag putts when the pressure reaches its peak.</p>

          <nav class="tag-row" aria-label="Article tags">
            <a href="#">Charley Hull</a>
            <a href="#">Anna Huang</a>
            <a href="#">LET Tour</a>
            <a href="#">Women's Golf</a>
          </nav>
        </div>
      </article>"""

template = re.sub(r'<article>.*?</article>', new_article, template, flags=re.DOTALL)

with open('/Users/adnan/Desktop/golf/news-2026-charley-hull-four-putt-anna-huang-pif-london.html', 'w') as f:
    f.write(template)

print("Article generated.")
