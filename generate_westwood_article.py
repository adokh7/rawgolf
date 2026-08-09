import re

with open('/Users/adnan/Desktop/golf/article-template.html', 'r') as f:
    template = f.read()

# Meta replacements
template = re.sub(r'<title>.*?</title>', '<title>At 53, He Says He\'s Playing a Different Course | GolfRaw</title>', template)
template = re.sub(r'<meta name="description"\s*content=".*?">', '<meta name="description"\n    content="Westwood is 53, third and four back at Bedminster — on a 7,651-yard course where, in his own words, he\'s playing a different golf course to everyone else.">', template)
template = re.sub(r'<link rel="canonical" href=".*?">', '<link rel="canonical" href="https://www.golfraw.com/news-2026-lee-westwood-liv-golf-bedminster-different-course">', template)
template = re.sub(r'<meta property="og:title" content=".*?" />', '<meta property="og:title" content="At 53, He Says He\'s Playing a Different Course | GolfRaw" />', template)
template = re.sub(r'<meta property="og:description" content=".*?" />', '<meta property="og:description" content="Westwood is 53, third and four back at Bedminster — on a 7,651-yard course where, in his own words, he\'s playing a different golf course to everyone else." />', template)
template = re.sub(r'<meta property="og:url" content=".*?" />', '<meta property="og:url" content="https://www.golfraw.com/news-2026-lee-westwood-liv-golf-bedminster-different-course" />', template)
template = re.sub(r'<meta property="og:image" content=".*?">', '<meta property="og:image" content="https://www.golfraw.com/public/lee-westwood-liv-golf-bedminster-53.webp">', template)
template = re.sub(r'<meta name="twitter:title" content=".*?">', '<meta name="twitter:title" content="At 53, He Says He\'s Playing a Different Course | GolfRaw">', template)
template = re.sub(r'<meta name="twitter:description"\s*content=".*?">', '<meta name="twitter:description"\n    content="Westwood is 53, third and four back at Bedminster — on a 7,651-yard course where, in his own words, he\'s playing a different golf course to everyone else.">', template)
template = re.sub(r'<meta name="twitter:image" content=".*?">', '<meta name="twitter:image" content="https://www.golfraw.com/public/lee-westwood-liv-golf-bedminster-53.webp">', template)
template = re.sub(r'<meta property="article:published_time" content=".*?" />', '<meta property="article:published_time" content="2026-08-09T07:30:00+02:00" />', template)
template = re.sub(r'<meta property="article:section" content=".*?">', '<meta property="article:section" content="LIV GOLF">', template)

# Indexing Guardrail
template = re.sub(r'<meta name="robots" content=".*?"\s*>', '<meta name="robots" content="index, follow, max-image-preview:large">', template)

new_article = """<article>
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/liv-golf">LIV Golf</a> / <span>Bedminster</span>
        </nav>

        <header class="article-head">
          <span class="cat">LIV GOLF · BEDMINSTER</span>
          <h1>At 53, Lee Westwood Says He's Playing a Different Golf Course. He's Right, and He's Third.</h1>
          <p class="standfirst">Lee Westwood goes into the final round of LIV Golf New York in third place, four shots behind Joaquín Niemann at Trump National Bedminster. At fifty-three years old, he gave a technical answer about distance that cuts to the core of age, length, and elite performance.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>AUG 09 2026</b></span>
          </div>
        </header>

        <div class="meta-callout" style="border-left: 4px solid #10b981; padding-left: 12px; margin: 16px 0;">
          <strong>LIV Golf Bedminster Dynamics:</strong> August 9, 2026 | Leaderboard & Strategic Breakdown
        </div>

        <figure class="lead-img">
          <img src="/public/lee-westwood-liv-golf-bedminster-53.webp" alt="Lee Westwood LIV Golf Bedminster 53 Years Old" />
        </figure>

        <div class="article-body">
          <h2>The Numbers at Bedminster</h2>
          <p>Joaquín Niemann leads at 14 under par through three rounds. Harold Varner III sits second at 12 under, with Westwood occupying solo third at 10 under par.</p>

          <p>Trump National Bedminster measures 7,651 yards this week—the second-longest course LIV Golf has featured all season, lengthened by more than 125 yards since 2023 with new back tees on the 9th, 13th, and 16th holes. Westwood enters the final day ranked 28th in LIV's individual season standings, while Niemann sits fifth behind Jon Rahm, Bryson DeChambeau, Lucas Herbert, and Tyrrell Hatton.</p>

          <h2>Why "A Different Golf Course" Is the Exact Description</h2>
          <p>Distance loss changes strategy before it alters the score. On a 480-yard par four:</p>

          <ul>
            <li><strong>Long Hitter (300-yard carry):</strong> Leaves 180 yards into the green—a 7-iron or 8-iron allowing an aggressive line into the pin.</li>
            <li><strong>Westwood (265-yard carry):</strong> Leaves 215 yards into the green—a hybrid or long iron landing hot and holding firm greens with difficulty.</li>
          </ul>

          <p>Across 18 holes at 7,651 yards, Westwood is forced to execute a sequence of high-difficulty approach shots where par represents a strong result, whereas younger bombers are grinding for birdies with short wedges.</p>

          <h2>Historical Context: Winning in Your Fifties</h2>
          <p>Winning a major professional event in your fifties remains exceptionally rare across modern golf:</p>

          <ul>
            <li><strong>Sam Snead:</strong> Oldest PGA Tour winner (52 years old, set in 1965).</li>
            <li><strong>Miguel Ángel Jiménez:</strong> Oldest DP World Tour winner (50 years old).</li>
            <li><strong>Lee Westwood:</strong> 53 years old, seeking his first LIV Golf title after 44 career professional victories.</li>
          </ul>

          <p>When asked about those historical benchmarks, Westwood dismissed the numbers, noting that at 53 his primary goal is remaining in physical condition to compete alongside stars like Rahm, DeChambeau, and Hatton.</p>

          <h2>Practical Lessons for Amateur Golfers</h2>
          <p>Westwood's technical diagnosis offers direct lessons for everyday players:</p>

          <ul>
            <li><strong>Play the Right Tees:</strong> If your carry distance is under 220 yards, playing 7,000+ yard courses tests endurance rather than skill. Moving up tee boxes preserves scoring and enjoyment.</li>
            <li><strong>Process Over Expectations:</strong> Rather than setting rigid target scores, focusing entirely on full preparation and execution per shot removes mental burden.</li>
          </ul>

          <div class="faq-section">
            <h2>Frequently Asked Questions</h2>

            <h3>Where does Lee Westwood stand at LIV Golf New York?</h3>
            <p>Westwood is in third place at 10 under par after three rounds, four shots behind leader Joaquín Niemann (14 under) and two behind Harold Varner III (12 under).</p>

            <h3>How long is Trump National Bedminster?</h3>
            <p>The course measures 7,651 yards (par 71), making it the second-longest venue on LIV Golf's 2026 schedule.</p>

            <h3>Who is the oldest winner in professional golf history?</h3>
            <p>Sam Snead holds the PGA Tour record at age 52, while Miguel Ángel Jiménez holds the DP World Tour record at age 50.</p>

            <h3>Has Lee Westwood won on the LIV Golf circuit?</h3>
            <p>No, Westwood has not won an individual LIV Golf title since joining the league.</p>
          </div>

          <h2>The Raw Take</h2>
          <p>Four shots behind Joaquín Niemann is a formidable gap entering Sunday. Yet sitting third at 10 under on a 7,651-yard layout at age 53 proves that Lee Westwood's tactical mastery and ball-striking precision remain elite, even while playing a demonstrably longer golf course than his competitors.</p>

          <nav class="tag-row" aria-label="Article tags">
            <a href="#">Lee Westwood</a>
            <a href="#">LIV Golf</a>
            <a href="#">Bedminster</a>
            <a href="#">Golf Strategy</a>
          </nav>
        </div>
      </article>"""

template = re.sub(r'<article>.*?</article>', new_article, template, flags=re.DOTALL)

with open('/Users/adnan/Desktop/golf/news-2026-lee-westwood-liv-golf-bedminster-different-course.html', 'w') as f:
    f.write(template)

print("Article generated.")
