import json

template_path = "article-template.html"
with open(template_path, "r") as f:
    template = f.read()

# Replace head metadata
template = template.replace(
    "<title>Oakmont US Open Setup: How the USGA Broke the | GOLFRAW</title>",
    "<title>99% From 3 Feet. 71% From 6. That's the Whole Game. | GolfRaw</title>"
)
template = template.replace(
    '<meta name="description" content="Average score 74.8, stimp at 15. We walked Oakmont&#x27;s US Open setup with two tour caddies to find out which pins cross the line — and who secretly loves it.">',
    '<meta name="description" content="Tour players hole 99.42% from three feet and 70.98% from six. Everything about three-putting is which one you leave yourself. The data, and what to do.">'
)
template = template.replace(
    '<link rel="canonical" href="https://www.golfraw.com/article-template">',
    '<link rel="canonical" href="https://www.golfraw.com/guides-the-three-feet-that-decide-whether-you-three-putt">'
)
template = template.replace(
    '<meta property="og:title" content="Oakmont US Open Setup: How the USGA Broke the | GOLFRAW">',
    '<meta property="og:title" content="99% From 3 Feet. 71% From 6. That\'s the Whole Game. | GolfRaw">'
)
template = template.replace(
    '<meta property="og:description" content="Average score 74.8, stimp at 15. We walked Oakmont&#x27;s US Open setup with two tour caddies to find out which pins cross the line — and who secretly loves it.">',
    '<meta property="og:description" content="Tour players hole 99.42% from three feet and 70.98% from six. Everything about three-putting is which one you leave yourself. The data, and what to do.">'
)
template = template.replace(
    '<meta property="og:url" content="https://www.golfraw.com/article-template">',
    '<meta property="og:url" content="https://www.golfraw.com/guides-the-three-feet-that-decide-whether-you-three-putt">'
)
template = template.replace(
    '<meta property="og:image" content="https://www.golfraw.com/public/raw-golf-practice.webp">',
    '<meta property="og:image" content="https://www.golfraw.com/public/lag-putting-three-putt-avoidance-guide.webp">'
)
template = template.replace(
    '<meta name="twitter:title" content="Oakmont US Open Setup: How the USGA Broke the | GOLFRAW">',
    '<meta name="twitter:title" content="99% From 3 Feet. 71% From 6. That\'s the Whole Game. | GolfRaw">'
)
template = template.replace(
    '<meta name="twitter:description" content="Average score 74.8, stimp at 15. We walked Oakmont&#x27;s US Open setup with two tour caddies to find out which pins cross the line — and who secretly loves it.">',
    '<meta name="twitter:description" content="Tour players hole 99.42% from three feet and 70.98% from six. Everything about three-putting is which one you leave yourself. The data, and what to do.">'
)
template = template.replace(
    '<meta name="twitter:image" content="https://www.golfraw.com/public/raw-golf-practice.webp">',
    '<meta name="twitter:image" content="https://www.golfraw.com/public/lag-putting-three-putt-avoidance-guide.webp">'
)
template = template.replace(
    '<meta property="article:published_time" content="2026-06-13T07:30:00+02:00" />',
    '<meta property="article:published_time" content="2026-08-11T12:00:00+02:00" />'
)
template = template.replace(
    '<meta property="article:modified_time" content="2026-06-13T09:42:00+02:00">',
    '<meta property="article:modified_time" content="2026-08-11T12:00:00+02:00">'
)

# JSON-LD Schema Replace
template = template.replace(
    '"headline": "Oakmont Is Eating the Field Alive — and the USGA Planned It That Way",',
    '"headline": "99% From 3 Feet. 71% From 6. That\'s the Whole Game.",'
)
template = template.replace(
    '"description": "Average score 74.8, greens at 15 on the stimp. Two tour caddies walked us through the US Open setup built to break the field.",',
    '"description": "Tour players hole 99.42% from three feet and 70.98% from six. Everything about three-putting is which one you leave yourself. The data, and what to do.",'
)
template = template.replace(
    '"https://www.golfraw.com/public/img/oakmont-2026-setup-og.jpg"',
    '"https://www.golfraw.com/public/lag-putting-three-putt-avoidance-guide.webp"'
)
template = template.replace(
    '"datePublished": "2026-06-13T07:30:00+02:00",',
    '"datePublished": "2026-08-11T12:00:00+02:00",'
)
template = template.replace(
    '"dateModified": "2026-06-13T09:42:00+02:00",',
    '"dateModified": "2026-08-11T12:00:00+02:00",'
)
template = template.replace(
    '"mainEntityOfPage": "https://www.golfraw.com/article-template"',
    '"mainEntityOfPage": "https://www.golfraw.com/guides-the-three-feet-that-decide-whether-you-three-putt"'
)

new_article_content = """<article>
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/#guides">Guides</a> / <span>Putting</span>
        </nav>

        <header class="article-head">
          <span class="cat">Guides · Performance</span>
          <h1>The Three Feet That Decide Whether You Three-Putt</h1>
          <p class="standfirst">PGA Tour players hole 99.42% of putts from three feet, but that number drops to 70.98% from six feet. That three-foot difference accounts for nearly a thirty percent swing in outcome—making your first putt's leave distance the single most critical factor in eliminating three- and four-putts.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>TUE 11 AUG 2026</b></span>
            <span><b>4 MIN READ</b></span>
          </div>
        </header>

        <div class="meta-callout" style="border-left: 4px solid #10b981; padding-left: 12px; margin: 16px 0;">
          <strong>Golf Data & Performance Guide:</strong> August 11, 2026 | Lag Putting Analytics & Drills
        </div>

        <figure class="lead-img">
            <img src="/public/lag-putting-three-putt-avoidance-guide.webp" alt="Lag Putting Three-Putt Avoidance Guide" />
        </figure>
        <figcaption>THE DIFFERENCE BETWEEN A TAP-IN AND A SWEATY SIX-FOOTER IS THE ENTIRE GAME OF GOLF.</figcaption>

        <div class="article-body">
          <h2>Where the Danger Actually Starts</h2>
          <p>According to Shot Scope tracking data, the distance at which a three-putt becomes more likely than a one-putt—known as the "putting precipice"—is 29 feet for a scratch golfer and 28 feet for a 10-handicapper. This single-foot gap reveals that lag putting is far less handicap-dependent than tee-to-green performance.</p>

          <p>While scratch players beat higher handicappers dramatically off the tee and with wedges, long putting puts players on nearly equal footing. However, total three-putt rates vary significantly across handicaps:</p>

          <ul>
            <li><strong>Scratch Golfers:</strong> Three-putt roughly 7.8% of the time (1.4 times per round).</li>
            <li><strong>20-Handicappers:</strong> Three-putt approximately 20% of the time.</li>
            <li><strong>25+ Handicappers:</strong> Three-putt roughly 24.5% of the time, costing 3.5 to 4.5 strokes per round.</li>
          </ul>

          <h2>What Professionals Actually Do From Long Range</h2>
          <p>PGA Tour players average an approach putt proximity of 2 feet 4 inches from the hole. From 30 feet out, tour professionals only make 7% of their putts and three-putt 5% of the time. From 40 to 50 feet, their three-putt rate rises to between 10% and 20%.</p>

          <p>Strokes-gained research pioneered by Mark Broadie confirms that eliminating three-putts delivers a faster route to lower scoring averages for amateurs than chasing extra distance or minor swing modifications.</p>

          <h2>The Anatomy of a Four-Putt</h2>
          <p>Four-putts rarely result from four bad swings. Instead, they stem from a single poorly judged first putt followed by emotional, defensive recoveries:</p>

          <ul>
            <li><strong>Putt 1:</strong> Overhit first putt running 8 to 10 feet past the hole.</li>
            <li><strong>Putt 2:</strong> Defensive second putt struck timidly that leaves 3 feet short.</li>
            <li><strong>Putt 3:</strong> Tense short putt missed due to score anxiety.</li>
            <li><strong>Putt 4:</strong> Tap-in finish.</li>
          </ul>

          <h2>Actionable Steps to Fix Lag Putting</h2>
          <p>To eliminate costly three-putts, adjust your target focus and practice methodology:</p>

          <ul>
            <li><strong>Target a 3-Foot Circle:</strong> From outside 30 feet, focus entirely on speed control to leave putts within a 3-foot radius around the cup.</li>
            <li><strong>Track First-Putt Proximity:</strong> Measure your average leave distance from 30+ feet instead of counting total putts. Reducing proximity from 6 feet to 3 feet halves your three-putt frequency.</li>
            <li><strong>15-Minute Point Drill:</strong> Putt 5 balls from 30 feet. Award 3 points for a holed putt, 2 points for finishing within 18 inches past, 1 point for 19–36 inches past, and 0 points for any putt left short or more than 3 feet past.</li>
          </ul>

          <div class="faq-section">
            <h2>Frequently Asked Questions</h2>

            <h3>At what distance does a three-putt become likely?</h3>
            <p>Data indicates that a three-putt becomes more likely than a one-putt at approximately 29 feet for scratch golfers and 28 feet for 10-handicappers.</p>

            <h3>How often do amateur golfers three-putt?</h3>
            <p>Scratch golfers three-putt around 7.8% of greens, while 20-handicappers three-putt close to 20% of the time.</p>

            <h3>How close do PGA Tour players leave their lag putts?</h3>
            <p>The PGA Tour average approach putt leaves 2 feet 4 inches to the hole, leading to a 99.42% make rate on second putts.</p>

            <h3>What is the fastest way to stop three-putting?</h3>
            <p>Focus on speed control from outside 30 feet and track your first-putt proximity average, aiming to bring leave distances under 3 feet.</p>
          </div>

          <h2>The Raw Take</h2>
          <p>Eliminating three-putts requires zero extra athleticism or swing adjustments—just disciplined speed control. Spending 15 minutes twice a week tracking lag proximity delivers immediate score reductions that no new driver or swing overhaul can replicate.</p>
        </div>
      </article>"""

article_start_tag = "<article>"
article_end_tag = "</article>"

start_idx = template.find(article_start_tag)
end_idx = template.find(article_end_tag) + len(article_end_tag)

new_html = template[:start_idx] + new_article_content + template[end_idx:]

with open("guides-the-three-feet-that-decide-whether-you-three-putt.html", "w") as f:
    f.write(new_html)

print("Created guides-the-three-feet-that-decide-whether-you-three-putt.html")

# Update articles.json
with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "url": "/guides-the-three-feet-that-decide-whether-you-three-putt",
  "title": "The Three Feet That Decide Whether You Three-Putt",
  "category": "GUIDES",
  "date": "AUG 11 2026",
  "image": "/public/lag-putting-three-putt-avoidance-guide.webp",
  "snippet": "Tour players hole 99.42% from three feet and 70.98% from six. Everything about three-putting is which one you leave yourself.",
  "keywords": "how to stop three putting, how to stop four putting, lag putting drills, three putt avoidance by handicap, putting distance control"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)

print("Updated articles.json")
