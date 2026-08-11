import json

with open("/Users/adnan/Desktop/golf/news-2026-what-beginners-actually-search.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace metadata
html = html.replace(
    '<title>40,500 Search "Beginner Clubs." 1,600 Search "Golf." | GolfRaw</title>',
    '<title>Michigan Had Two Big Tournaments. Soon It May Have None. | GolfRaw</title>'
)
html = html.replace(
    'content="40,500 people a month search for beginner golf clubs. 590 ask what a handicap is. What the search data reveals about how beginners are being sold to."',
    'content="The Rocket Classic is gone and LIV\'s Michigan finale is reportedly cancelled — four weeks apart, for entirely different reasons. What Detroit actually lost."'
)
html = html.replace(
    'href="https://www.golfraw.com/news-2026-what-beginners-actually-search"',
    'href="https://www.golfraw.com/news-2026-michigan-golf-tournaments-rocket-classic-liv-cancelled"'
)
html = html.replace(
    'content="40,500 Search &quot;Beginner Clubs.&quot; 1,600 Search &quot;Golf.&quot; | GolfRaw"',
    'content="Michigan Had Two Big Tournaments. Soon It May Have None. | GolfRaw"'
)
html = html.replace(
    'content="https://www.golfraw.com/news-2026-what-beginners-actually-search"',
    'content="https://www.golfraw.com/news-2026-michigan-golf-tournaments-rocket-classic-liv-cancelled"'
)
html = html.replace(
    'content="https://www.golfraw.com/public/what-beginners-actually-search.webp"',
    'content="https://www.golfraw.com/public/michigan-golf-tournaments-rocket-classic-liv.webp"'
)
html = html.replace(
    'content="The first green at Oakmont Country Club during US Open 2026 setup, with championship rough visible"',
    'content="Michigan Golf Tournaments Rocket Classic LIV Golf"'
)
html = html.replace(
    '<meta property="article:published_time" content="2026-06-13T07:30:00+02:00" />',
    '<meta property="article:published_time" content="2026-08-09T07:30:00+02:00" />'
)
html = html.replace(
    '<meta property="article:modified_time" content="2026-06-13T09:42:00+02:00">',
    '<meta property="article:modified_time" content="2026-08-09T09:42:00+02:00">'
)
html = html.replace(
    '<meta property="article:section" content="Tournaments">',
    '<meta property="article:section" content="PGA TOUR">'
)

# Structured data
import re
new_structured_data = """{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Article",
      "@id": "https://www.golfraw.com/news-2026-michigan-golf-tournaments-rocket-classic-liv-cancelled#article",
      "headline": "Michigan Had Two Elite Golf Tournaments This Year. Soon It May Have None.",
      "description": "The Rocket Classic is gone and LIV's Michigan finale is reportedly cancelled \u2014 four weeks apart, for entirely different reasons. What Detroit actually lost.",
      "mainEntityOfPage": {
        "@type": "WebPage",
        "@id": "https://www.golfraw.com/news-2026-michigan-golf-tournaments-rocket-classic-liv-cancelled"
      },
      "datePublished": "2026-08-09",
      "dateModified": "2026-08-09",
      "publisher": {
        "@type": "Organization",
        "name": "GolfRaw",
        "url": "https://www.golfraw.com"
      }
    }
  ]
}"""
html = re.sub(
    r'<script type="application/ld\+json">.*?</script>',
    f'<script type="application/ld+json">\n{new_structured_data}\n</script>',
    html,
    flags=re.DOTALL
)

# Replace <article> content
article_content = """<article>
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/tournaments">Tournaments</a> / <span>News</span>
        </nav>

        <header class="article-head">
          <span class="cat">PGA TOUR</span>
          <h1>Michigan Had Two Elite Golf Tournaments This Year. Soon It May Have None.</h1>
          <p class="standfirst">Twelve months ago, Michigan enjoyed two elite professional golf events and local praise for how well both treated attending fans. Today, the state faces an elite golf drought in 2027.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>SUN 09 AUG 2026</b></span>
          </div>
        </header>

        <div class="meta-callout" style="border-left: 4px solid #10b981; padding-left: 12px; margin: 16px 0;">
          <strong>Industry Analysis:</strong> August 9, 2026 | Tournament Economics & Venue Restructuring
        </div>

        <figure class="lead-img">
          <img src="/public/michigan-golf-tournaments-rocket-classic-liv.webp" alt="Michigan Golf Tournaments Rocket Classic LIV Golf" />
        </figure>

        <div class="article-body">
          <p>Last August, Detroit media celebrated LIV Golf's Michigan Team Championship at The Cardinal at Saint John's Resort as a top-tier fan experience. Spectators stood mere feet from warming players at the driving range, while music created an approachable atmosphere. At the same time, Detroit Golf Club's PGA Tour stop was leaning into fan-first experiences like the Area 313 zone. Now, both events are slipping away.</p>

          <h2>Where Both Tournaments Stand Now</h2>
          <p>The Rocket Classic concluded on August 2 and will not return. Title sponsor Rocket Mortgage declined its 2027 option after 13 years supporting the PGA Tour. According to reports, the company was unwilling to pay roughly $15 million annually for second-tier status under the Tour's upcoming 2028 restructure, or double that figure for elite status. Its calendar slot has been reassigned to Napa.</p>

          <p>Meanwhile, the LIV Golf Michigan Team Championship scheduled for August 27–30 at The Cardinal is widely reported as cancelled. LIV team captain Martin Kaymer publicly estimated its chances at roughly five percent, and local reporting confirmed no event infrastructure was built at the site. LIV has yet to issue an official confirmation.</p>

          <h2>Course Investment vs. Tournament Reality</h2>
          <p>The loss is striking given the heavy investment made by both venues:</p>

          <ul>
            <li><strong>Detroit Golf Club:</strong> Spent $16.1 million restoring its Donald Ross layout and converting two par-5s into par-4s, completing the project just in time for its final edition.</li>
            <li><strong>The Cardinal at Saint John's:</strong> Invested heavily in fan accessibility and modern golf entertainment, hosting Jon Rahm's Legion XIII playoff victory in 2025.</li>
          </ul>

          <p>Neither course modification nor fan experience dictated these departures. Detroit Golf Club spent millions to toughen its layout, only for players to shoot 61s and tie scoring records. The Cardinal embraced a fun, birdie-heavy setup praised by players like Bryson DeChambeau. Yet neither strategy protected the tournaments.</p>

          <h2>The Business Behind the Departure</h2>
          <p>The two exits stem from completely separate financial shifts arriving four weeks apart:</p>

          <p>The Rocket Classic ended over sponsorship pricing tiers. The PGA Tour is splitting into a two-tiered structure in 2028, and Rocket declined the rising price tag. Conversely, the LIV event faltered as league funding underwent structural changes in the spring, leading to purse reductions and a condensed 2027 schedule after 12 events were played in 2026.</p>

          <div class="faq-section">
            <h2>Frequently Asked Questions</h2>

            <h3>Is the LIV Golf Michigan Team Championship happening in 2026?</h3>
            <p>While officially scheduled for late August 2026 at The Cardinal in Plymouth, it is widely reported as cancelled. Team captain Martin Kaymer put the odds at 5%, and no site infrastructure has been erected.</p>

            <h3>Why did the Rocket Classic end its PGA Tour run?</h3>
            <p>Rocket Mortgage declined its 2027 option after 13 years, opting not to pay an estimated $15 million annually for second-tier status under the PGA Tour's 2028 restructuring plan.</p>

            <h3>Will Michigan host a PGA Tour event in 2027?</h3>
            <p>No, the Rocket Classic's former date on the schedule has been awarded to a new tournament at Silverado in Napa, California.</p>
          </div>

          <h2>The Raw Take</h2>
          <p>The lesson for golf fans in any market is clear: tournament existence relies entirely on sponsor economics, not fan attendance or course history. Neither $16 million course restorations nor world-class spectator zones can shield a local event when global sports financing shifts strategy.</p>
          
          <nav class="tag-row" aria-label="Article tags">
            <a href="#">PGA TOUR</a>
            <a href="#">LIV GOLF</a>
            <a href="#">ROCKET CLASSIC</a>
            <a href="#">MICHIGAN</a>
          </nav>
        </div>
      </article>"""

html = re.sub(
    r'<article>.*?</article>',
    article_content,
    html,
    flags=re.DOTALL
)

with open("/Users/adnan/Desktop/golf/news-2026-michigan-golf-tournaments-rocket-classic-liv-cancelled.html", "w", encoding="utf-8") as f:
    f.write(html)
