import re

with open('/Users/adnan/Desktop/golf/article-template.html', 'r') as f:
    template = f.read()

# Meta replacements
template = re.sub(r'<title>.*?</title>', '<title>Eighth in Iron Play, 116th in Putting: The Brutal Math Behind Brooks Koepka\'s Wyndham Stand | GolfRaw</title>', template)
template = re.sub(r'<meta name="description"\s*content=".*?">', '<meta name="description"\n    content="Koepka is 8th on Tour in approach play and 116th in putting. He withdrew from Detroit with a hand injury. Now he needs a massive week at Sedgefield.">', template)
template = re.sub(r'<link rel="canonical" href=".*?">', '<link rel="canonical" href="https://www.golfraw.com/news-2026-brooks-koepka-wyndham-putting-stat-injury">', template)
template = re.sub(r'<meta property="og:title" content=".*?" />', '<meta property="og:title" content="Eighth in Iron Play, 116th in Putting: The Brutal Math Behind Brooks Koepka\'s Wyndham Stand" />', template)
template = re.sub(r'<meta property="og:description" content=".*?" />', '<meta property="og:description" content="Koepka is 8th on Tour in approach play and 116th in putting. He withdrew from Detroit with a hand injury. Now he needs a massive week at Sedgefield." />', template)
template = re.sub(r'<meta property="og:url" content=".*?" />', '<meta property="og:url" content="https://www.golfraw.com/news-2026-brooks-koepka-wyndham-putting-stat-injury" />', template)
template = re.sub(r'<meta property="og:image" content=".*?">', '<meta property="og:image" content="https://www.golfraw.com/public/brooks-koepka-wyndham-putting-pga-tour.webp">', template)
template = re.sub(r'<meta name="twitter:title" content=".*?">', '<meta name="twitter:title" content="Eighth in Iron Play, 116th in Putting: The Brutal Math Behind Brooks Koepka\'s Wyndham Stand">', template)
template = re.sub(r'<meta name="twitter:description"\s*content=".*?">', '<meta name="twitter:description"\n    content="Koepka is 8th on Tour in approach play and 116th in putting. He withdrew from Detroit with a hand injury. Now he needs a massive week at Sedgefield.">', template)
template = re.sub(r'<meta name="twitter:image" content=".*?">', '<meta name="twitter:image" content="https://www.golfraw.com/public/brooks-koepka-wyndham-putting-pga-tour.webp">', template)
template = re.sub(r'<meta property="article:published_time" content=".*?" />', '<meta property="article:published_time" content="2026-08-09T07:30:00+02:00" />', template)

# Article content replacement
new_article = """<article>
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/#pga-tour">PGA Tour</a> / <span>FedExCup Playoffs</span>
        </nav>

        <header class="article-head">
          <span class="cat">PGA Tour · Wyndham</span>
          <h1>Eighth in Iron Play, 116th in Putting: The Brutal Math Behind Brooks Koepka's Wyndham Stand</h1>
          <p class="standfirst">Brooks Koepka arrived at Sedgefield Country Club needing something close to a miracle to save his FedExCup season. The strange part is that his golf isn't broken — only one specific, maddening part of it.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>AUG 09 2026</b></span>
          </div>
        </header>

        <div class="meta-callout" style="border-left: 4px solid #10b981; padding-left: 12px; margin: 16px 0;">
          <strong>PGA Tour Dynamics:</strong> August 9, 2026 | FedExCup Playoff Bubble & Player Diagnostics
        </div>

        <figure class="lead-img">
          <img src="/public/brooks-koepka-wyndham-putting-pga-tour.webp" alt="Brooks Koepka Wyndham Championship Putting Injury" />
        </figure>

        <div class="article-body">
          <p>Most coverage of Koepka’s 2026 PGA Tour campaign frames it as a classic narrative of decline: brief flashes of major-championship form buried under long stretches of irrelevance. But that framing misses a critical factor that reframes his entire posture entering the Wyndham Championship.</p>

          <h2>The Injury That Shifted the Bubble</h2>
          <p>Koepka arrived at the Rocket Classic in Detroit ranked 84th in FedExCup points and subsequently withdrew, struggling with a hand injury. That withdrawal cost him a vital week of points he had no way of making up, dropping him to 86th entering Greensboro.</p>

          <p>The math at Sedgefield is unforgiving: he needs a solo fourth-place finish or better simply to climb into the top 70 and extend his season. The withdrawal didn't just cost him points; it altered field dynamics across the Tour. Players like Lanto Griffin and Justin Lower gained starts off that single opening in Detroit and Greensboro — proving once again that in late-summer tour golf, one player's bad month is another's career lifeline.</p>

          <h2>Eighth in Irons, 116th on the Greens</h2>
          <p>The most revealing detail of Koepka’s season isn't a decline in physical power or ball-striking capability. It is a single stark statistical contrast:</p>

          <ul>
            <li><strong>Strokes Gained: Approach the Green:</strong> 8th on the PGA Tour</li>
            <li><strong>Strokes Gained: Putting:</strong> 116th on the PGA Tour</li>
          </ul>

          <p>Eighth in the world at hitting iron shots. A hundred and sixteenth at holing putts. That is not a man who has lost his swing; it’s a player carrying one flat-stick weakness into the one week he couldn't afford it.</p>

          <p>Koepka has cycled through putters repeatedly throughout the season. He arrived at Sedgefield pulling another change out of the bag: a prototype Scotty Cameron Phantom 3 equipped with a Teryllium insert — the exact insert configuration he relied upon during his major championship runs. Every club golfer recognizes the pattern: when the ball-striking is pristine but the card won't reflect it, you start searching for answers at the grip end of the putter.</p>

          <h2>What's Really at Stake at Sedgefield</h2>
          <p>Entering the weekend rounds five shots off the lead before early Saturday bogeys stalled his momentum, Koepka faces a cliff far steeper than missing three playoff events.</p>

          <p>Under the terms of his Returning Member agreement, Koepka cannot receive sponsor exemptions into Signature Events next season. To play in the Tour’s marquee $20M purse events in 2027, he must finish inside the top 50 in FedExCup points this season. That means simply scraping into the top 70 at Wyndham isn't enough — he needs to go deep into the playoffs once he gets there.</p>

          <p>Sunday in Greensboro isn't merely about extending a 2026 schedule. It's about whether his entire 2027 campaign will look like this one.</p>

          <div class="faq-section">
            <h2>Frequently Asked Questions</h2>

            <h3>Why did Brooks Koepka withdraw from the Rocket Classic?</h3>
            <p>Koepka withdrew from the Detroit event due to a hand injury, which dropped him from 84th to 86th in the FedExCup standings heading into the Wyndham Championship.</p>

            <h3>What does Koepka need at the Wyndham Championship to make the playoffs?</h3>
            <p>He needs a solo fourth-place finish or better at Sedgefield to break into the top 70 and qualify for the FedExCup Playoffs.</p>

            <h3>What putter is Koepka using at Sedgefield?</h3>
            <p>He put a prototype Scotty Cameron Phantom 3 with a Teryllium insert into play, mirroring the insert technology he used during his major victories.</p>

            <h3>How do Koepka's 2026 PGA Tour stats compare?</h3>
            <p>Koepka ranks 8th on Tour in Strokes Gained: Approach the Green, but struggles at 116th in Strokes Gained: Putting.</p>
          </div>

          <h2>The Raw Take</h2>
          <p>Koepka’s dilemma is the ultimate reality check for modern tour golf. Being the eighth-best iron player on the planet used to guarantee you a comfortable Sunday anywhere. In 2026, paired with the 116th-ranked putter and a bad hand in July, it leaves a five-time major champion grinding at Sedgefield just to secure a job for next season's Signature Events.</p>

          <nav class="tag-row" aria-label="Article tags">
            <a href="#">Brooks Koepka</a>
            <a href="#">Wyndham Championship</a>
            <a href="#">FedExCup Playoffs</a>
            <a href="#">PGA Tour</a>
          </nav>
        </div>
      </article>"""

# Using regex to replace the <article>...</article> section
template = re.sub(r'<article>.*?</article>', new_article, template, flags=re.DOTALL)

with open('/Users/adnan/Desktop/golf/news-2026-brooks-koepka-wyndham-putting-stat-injury.html', 'w') as f:
    f.write(template)

print("Article generated.")
