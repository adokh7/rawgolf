import json

template_path = "article-template.html"
with open(template_path, "r") as f:
    template = f.read()

# Replace head metadata
template = template.replace(
    "<title>Oakmont US Open Setup: How the USGA Broke the | GOLFRAW</title>",
    "<title>A Rolled-Back Ball Made Him One Yard Longer | GolfRaw</title>"
)
template = template.replace(
    '<meta name="description" content="Average score 74.8, stimp at 15. We walked Oakmont&#x27;s US Open setup with two tour caddies to find out which pins cross the line — and who secretly loves it.">',
    '<meta name="description" content="Cameron Young averages 312 yards this year using a ball that meets the 2030 rules — one further than last season. Why golf\'s rollback just got paused again.">'
)
template = template.replace(
    '<link rel="canonical" href="https://www.golfraw.com/article-template">',
    '<link rel="canonical" href="https://www.golfraw.com/news-2026-golf-ball-rollback-paused-colin-montgomerie">'
)
template = template.replace(
    '<meta property="og:title" content="Oakmont US Open Setup: How the USGA Broke the | GOLFRAW">',
    '<meta property="og:title" content="A Rolled-Back Ball Made Him One Yard Longer | GolfRaw">'
)
template = template.replace(
    '<meta property="og:description" content="Average score 74.8, stimp at 15. We walked Oakmont&#x27;s US Open setup with two tour caddies to find out which pins cross the line — and who secretly loves it.">',
    '<meta property="og:description" content="Cameron Young averages 312 yards this year using a ball that meets the 2030 rules — one further than last season. Why golf\'s rollback just got paused again.">'
)
template = template.replace(
    '<meta property="og:url" content="https://www.golfraw.com/article-template">',
    '<meta property="og:url" content="https://www.golfraw.com/news-2026-golf-ball-rollback-paused-colin-montgomerie">'
)
template = template.replace(
    '<meta property="og:image" content="https://www.golfraw.com/public/raw-golf-practice.webp">',
    '<meta property="og:image" content="https://www.golfraw.com/public/colin-montgomerie-golf-ball-rollback-2026.webp">'
)
template = template.replace(
    '<meta name="twitter:title" content="Oakmont US Open Setup: How the USGA Broke the | GOLFRAW">',
    '<meta name="twitter:title" content="A Rolled-Back Ball Made Him One Yard Longer | GolfRaw">'
)
template = template.replace(
    '<meta name="twitter:description" content="Average score 74.8, stimp at 15. We walked Oakmont&#x27;s US Open setup with two tour caddies to find out which pins cross the line — and who secretly loves it.">',
    '<meta name="twitter:description" content="Cameron Young averages 312 yards this year using a ball that meets the 2030 rules — one further than last season. Why golf\'s rollback just got paused again.">'
)
template = template.replace(
    '<meta name="twitter:image" content="https://www.golfraw.com/public/raw-golf-practice.webp">',
    '<meta name="twitter:image" content="https://www.golfraw.com/public/colin-montgomerie-golf-ball-rollback-2026.webp">'
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
    '"headline": "A Rolled-Back Ball Made Him One Yard Longer",'
)
template = template.replace(
    '"description": "Average score 74.8, greens at 15 on the stimp. Two tour caddies walked us through the US Open setup built to break the field.",',
    '"description": "Cameron Young averages 312 yards this year using a ball that meets the 2030 rules — one further than last season. Why golf\'s rollback just got paused again.",'
)
template = template.replace(
    '"https://www.golfraw.com/public/img/oakmont-2026-setup-og.jpg"',
    '"https://www.golfraw.com/public/colin-montgomerie-golf-ball-rollback-2026.webp"'
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
    '"mainEntityOfPage": "https://www.golfraw.com/news-2026-golf-ball-rollback-paused-colin-montgomerie"'
)

new_article_content = """<article>
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/#news">News</a> / <span>Equipment</span>
        </nav>

        <header class="article-head">
          <span class="cat">News · Equipment</span>
          <h1>Montgomerie Has Been Right About This Since 2020. His Solution Was Still Nonsense.</h1>
          <p class="standfirst">Colin Montgomerie spent six years insisting professional golf needs a shorter ball. On June 17, 2026, the USGA, R&A, PGA Tour, and DP World Tour effectively admitted he was right about the distance crisis—by issuing a joint statement pausing the proposed golf ball rollback until at least January 2030.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>TUE 11 AUG 2026</b></span>
            <span><b>4 MIN READ</b></span>
          </div>
        </header>

        <div class="meta-callout" style="border-left: 4px solid #10b981; padding-left: 12px; margin: 16px 0;">
          <strong>Equipment & Distance Analysis:</strong> August 11, 2026 | USGA & R&A Golf Ball Testing Pause
        </div>

        <figure class="lead-img">
            <img src="/public/colin-montgomerie-golf-ball-rollback-2026.webp" alt="Colin Montgomerie and Golf Ball Rollback 2026" />
        </figure>
        <figcaption>THE PROPOSED 2030 ROLLBACK FACES INSURMOUNTABLE TOUR RESISTANCE.</figcaption>

        <div class="article-body">
          <h2>Why Montgomerie's 80% Ball Failed the Math Test</h2>
          <p>In 2020, following Bryson DeChambeau's 340-yard drives, Montgomerie championed Jack Nicklaus's proposal for a tournament ball flying only 80% to 85% as far. However, math exposes the flaw: cutting distance across all clubs reduces a 340-yard drive to 280 yards, while turning a 160-yard 8-iron into a 135-yard shot, rendering par fours virtually unreachable for shorter hitters.</p>

          <p>Yet the underlying distance trend remains real. Average PGA Tour driving distance has expanded by nearly 25 yards since governing bodies first declared distance a formal concern in their 2002 Joint Statement of Principles.</p>

          <h2>The Paradox: Longer With a Rolled-Back Ball</h2>
          <p>The most devastating hurdle facing the proposal came during real-world testing. Cameron Young hit a prototype ball conforming to proposed 2030 regulations during the 2026 Players Championship—and has averaged 312 yards off the tee this season, one yard farther than his previous year's average.</p>

          <p>When a regulation change fails to reduce driving distance for top-tier hitters, its core purpose evaporates—a concern explicitly acknowledged in the joint tour statement.</p>

          <h2>Testing Conditions and Player Objections</h2>
          <p>The proposed rule retained the 317-yard Overall Distance Standard limit but altered robot testing parameters:</p>

          <ul>
            <li><strong>Clubhead Speed:</strong> Increased from 120 mph to 125 mph.</li>
            <li><strong>Spin Rate:</strong> Reduced from 2,520 rpm to 2,200 rpm.</li>
            <li><strong>Launch Angle:</strong> Adjusted from 10 degrees to 11 degrees.</li>
          </ul>

          <p>PGA Tour players voiced strong opposition, arguing the revised testing penalizes low-launch, low-spin players disproportionately compared to higher-launch swing types, creating competitive inequality.</p>

          <h2>Bifurcation Returns to the Table</h2>
          <p>USGA CEO Mike Whan acknowledged that a universal Model Local Rule faced insurmountable tour resistance, placing equipment bifurcation back under active consideration. This means touring professionals and recreational amateurs may ultimately play under entirely separate equipment rules.</p>

          <div class="faq-section">
            <h2>Frequently Asked Questions</h2>

            <h3>Is the golf ball rollback cancelled?</h3>
            <p>No, but it is paused. The governing bodies delayed any testing standard implementation until January 2030 at the earliest.</p>

            <h3>How much distance will recreational golfers lose under a rollback?</h3>
            <p>The USGA and R&A estimate that amateur club golfers would lose 5 yards or fewer off the tee.</p>

            <h3>What is golf ball bifurcation?</h3>
            <p>Bifurcation refers to establishing separate equipment testing rules for professional competitions versus recreational play.</p>

            <h3>What was Colin Montgomerie's rollback proposal?</h3>
            <p>Montgomerie advocated for a professional tournament ball restricted to 80–85% of standard flight distance.</p>
          </div>

          <h2>The Raw Take</h2>
          <p>Golf's governing bodies spent a decade crafting a middle-ground distance compromise mild enough to appease stakeholders, only to create a solution too weak to reduce distance and too disruptive for players to accept. As January 2030 approaches, equipment bifurcation remains the most realistic path forward.</p>
        </div>
      </article>"""

article_start_tag = "<article>"
article_end_tag = "</article>"

start_idx = template.find(article_start_tag)
end_idx = template.find(article_end_tag) + len(article_end_tag)

new_html = template[:start_idx] + new_article_content + template[end_idx:]

with open("news-2026-golf-ball-rollback-paused-colin-montgomerie.html", "w") as f:
    f.write(new_html)

print("Created news-2026-golf-ball-rollback-paused-colin-montgomerie.html")

# Update articles.json
with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "url": "/news-2026-golf-ball-rollback-paused-colin-montgomerie",
  "title": "Montgomerie Has Been Right About This Since 2020",
  "category": "EQUIPMENT",
  "date": "AUG 11 2026",
  "image": "/public/colin-montgomerie-golf-ball-rollback-2026.webp",
  "snippet": "Cameron Young averages 312 yards this year using a ball that meets the 2030 rules — one further than last season. Why golf's rollback just got paused again.",
  "keywords": "golf ball rollback 2030, is the golf ball rollback cancelled, colin montgomerie rollback, usga distance standard change, how much distance will the rollback cost"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)

print("Updated articles.json")
