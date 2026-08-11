import json

template_path = "article-template.html"
with open(template_path, "r") as f:
    template = f.read()

# Replace head metadata
template = template.replace(
    "<title>Oakmont US Open Setup: How the USGA Broke the | GOLFRAW</title>",
    "<title>Playing With a Pro Costs $10,000. Or $200. | GolfRaw</title>"
)
template = template.replace(
    '<meta name="description" content="Average score 74.8, stimp at 15. We walked Oakmont&#x27;s US Open setup with two tour caddies to find out which pins cross the line — and who secretly loves it.">',
    '<meta name="description" content="PGA Tour pro-ams run $2,500–$10,000 a head. Your local PGA section runs them for $200–$400, at private clubs. How pro-ams work and what pros expect of you.">'
)
template = template.replace(
    '<link rel="canonical" href="https://www.golfraw.com/article-template">',
    '<link rel="canonical" href="https://www.golfraw.com/guides-how-to-play-in-a-golf-pro-am-costs-etiquette">'
)
template = template.replace(
    '<meta property="og:title" content="Oakmont US Open Setup: How the USGA Broke the | GOLFRAW">',
    '<meta property="og:title" content="Playing With a Pro Costs $10,000. Or $200. | GolfRaw">'
)
template = template.replace(
    '<meta property="og:description" content="Average score 74.8, stimp at 15. We walked Oakmont&#x27;s US Open setup with two tour caddies to find out which pins cross the line — and who secretly loves it.">',
    '<meta property="og:description" content="PGA Tour pro-ams run $2,500–$10,000 a head. Your local PGA section runs them for $200–$400, at private clubs. How pro-ams work and what pros expect of you.">'
)
template = template.replace(
    '<meta property="og:url" content="https://www.golfraw.com/article-template">',
    '<meta property="og:url" content="https://www.golfraw.com/guides-how-to-play-in-a-golf-pro-am-costs-etiquette">'
)
template = template.replace(
    '<meta property="og:image" content="https://www.golfraw.com/public/raw-golf-practice.webp">',
    '<meta property="og:image" content="https://www.golfraw.com/public/pro-am-golf-guide-pga-tour.webp">'
)
template = template.replace(
    '<meta name="twitter:title" content="Oakmont US Open Setup: How the USGA Broke the | GOLFRAW">',
    '<meta name="twitter:title" content="Playing With a Pro Costs $10,000. Or $200. | GolfRaw">'
)
template = template.replace(
    '<meta name="twitter:description" content="Average score 74.8, stimp at 15. We walked Oakmont&#x27;s US Open setup with two tour caddies to find out which pins cross the line — and who secretly loves it.">',
    '<meta name="twitter:description" content="PGA Tour pro-ams run $2,500–$10,000 a head. Your local PGA section runs them for $200–$400, at private clubs. How pro-ams work and what pros expect of you.">'
)
template = template.replace(
    '<meta name="twitter:image" content="https://www.golfraw.com/public/raw-golf-practice.webp">',
    '<meta name="twitter:image" content="https://www.golfraw.com/public/pro-am-golf-guide-pga-tour.webp">'
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
    '"headline": "Playing With a Pro Costs $10,000. Or $200.",'
)
template = template.replace(
    '"description": "Average score 74.8, greens at 15 on the stimp. Two tour caddies walked us through the US Open setup built to break the field.",',
    '"description": "PGA Tour pro-ams run $2,500–$10,000 a head. Your local PGA section runs them for $200–$400, at private clubs. How pro-ams work and what pros expect of you.",'
)
template = template.replace(
    '"https://www.golfraw.com/public/img/oakmont-2026-setup-og.jpg"',
    '"https://www.golfraw.com/public/pro-am-golf-guide-pga-tour.webp"'
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
    '"mainEntityOfPage": "https://www.golfraw.com/guides-how-to-play-in-a-golf-pro-am-costs-etiquette"'
)

new_article_content = """<article>
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/#guides">Guides</a> / <span>Pro-Ams</span>
        </nav>

        <header class="article-head">
          <span class="cat">Guides · Experiences</span>
          <h1>You Can Play With a Professional Golfer. It Doesn't Have to Cost $10,000.</h1>
          <p class="standfirst">Playing inside the ropes alongside a touring professional buys a decade of invested interest in their career. But while high-profile PGA Tour pro-ams carry eye-watering price tags, local PGA section events offer the exact same experience at a tiny fraction of the cost.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>TUE 11 AUG 2026</b></span>
            <span><b>4 MIN READ</b></span>
          </div>
        </header>

        <div class="meta-callout" style="border-left: 4px solid #10b981; padding-left: 12px; margin: 16px 0;">
          <strong>Golf Experience & Access Guide:</strong> August 11, 2026 | Pro-Am Costs, Formats & Etiquette
        </div>

        <figure class="lead-img">
            <img src="/public/pro-am-golf-guide-pga-tour.webp" alt="PGA Tour Pro-Am Golf Guide and Etiquette" />
        </figure>
        <figcaption>PRO-AM EVENTS OFFER UNMATCHED COURSE ACCESS, BUT PRICING AND ETIQUETTE VARY WIDELY.</figcaption>

        <div class="article-body">
          <h2>What a Pro-Am Actually Is</h2>
          <p>A pro-am pairs a professional with amateur partners on the official tournament course under tournament setup conditions, usually a day or two before competitive rounds begin. Formats typically feature one professional alongside three or four amateurs.</p>

          <p>To ease physical fatigue, the PGA Tour allows members to play nine holes each with two separate amateur groups. Every player receives a caddie, and amateur group pairings are generally decided via an evening draw party prior to the round.</p>

          <h2>The True Cost Across Different Tiers</h2>
          <p>Pricing varies significantly depending on the tour level and geographic section:</p>

          <ul>
            <li><strong>PGA Tour Pro-Ams:</strong> Range from $2,500 to $10,000+ per spot. Monday pro-ams cost less than Wednesday sessions. Premium marquee events like Pebble Beach operate on an invitation-only basis with estimates ranging from $25,000 to over $70,000.</li>
            <li><strong>LIV Golf Pro-Ams:</strong> Typically reported around €7,500, inclusive of VIP hospitality access for the tournament week.</li>
            <li><strong>Local PGA Section Pro-Ams:</strong> Run by regional PGA sections at prestigious private clubs, costing between $200 and $400 per player with food and beverages included.</li>
          </ul>

          <h2>Why Tournaments Rely on Pro-Ams</h2>
          <p>Pro-ams represent the single largest revenue engine for most tournament operations. Entry fees directly underwrite operational expenses and generate the charitable contributions that underpin tour events.</p>

          <h2>What Touring Pros Expect From Amateurs</h2>
          <p>According to PGA Tour player Michael Kim, proper pro-am etiquette comes down to two primary rules:</p>

          <ul>
            <li><strong>Maintain Reasonable Pace:</strong> Keep moving efficiently without rushing, avoiding unnecessary delays between shots.</li>
            <li><strong>Skip Full Routines on Double Bogeys:</strong> Do not go through an elaborate pre-shot alignment routine for a double-bogey putt when the team score is already established.</li>
            <li><strong>Keep Apologies to a Minimum:</strong> Avoid repeatedly apologizing for poor shots; professionals expect amateurs to hit missed shots.</li>
            <li><strong>Play Forward Tees:</strong> Amateurs play from forward tees (typically 6,400–6,500 yards) under net team best-ball formats.</li>
          </ul>

          <div class="faq-section">
            <h2>Frequently Asked Questions</h2>

            <h3>What is a golf pro-am?</h3>
            <p>A pro-am is an official exhibition round pairing a professional golfer with amateur teammates prior to the main tournament.</p>

            <h3>How much does it cost to play in a PGA Tour pro-am?</h3>
            <p>PGA Tour pro-ams typically cost between $2,500 and $10,000 per amateur, though exclusive invitation-only events cost substantially more.</p>

            <h3>What is the most affordable way to play with a professional?</h3>
            <p>Regional PGA Section pro-ams offer amateur spots for $200 to $400 per person at private country clubs.</p>

            <h3>Do you tip the professional's caddie in a pro-am?</h3>
            <p>Tipping is not expected on the PGA Tour, but it is customary and welcomed on the Korn Ferry Tour.</p>
          </div>

          <h2>The Raw Take</h2>
          <p>You don't need a corporate expense account or $10,000 to walk inside the ropes with a touring professional. Regional PGA section pro-ams provide unmatched course access and close-up ball-striking observations for the price of a standard weekend round.</p>
        </div>
      </article>"""

article_start_tag = "<article>"
article_end_tag = "</article>"

start_idx = template.find(article_start_tag)
end_idx = template.find(article_end_tag) + len(article_end_tag)

new_html = template[:start_idx] + new_article_content + template[end_idx:]

with open("guides-how-to-play-in-a-golf-pro-am-costs-etiquette.html", "w") as f:
    f.write(new_html)

print("Created guides-how-to-play-in-a-golf-pro-am-costs-etiquette.html")

# Update articles.json
with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "url": "/guides-how-to-play-in-a-golf-pro-am-costs-etiquette",
  "title": "Playing With a Pro Costs $10,000. Or $200.",
  "category": "GUIDES",
  "date": "AUG 11 2026",
  "image": "/public/pro-am-golf-guide-pga-tour.webp",
  "snippet": "PGA Tour pro-ams run $2,500–$10,000 a head. Your local PGA section runs them for $200–$400, at private clubs. How pro-ams work and what pros expect of you.",
  "keywords": "what is a pro am golf, how to play in a pro am, pga tour pro am cost, pga section pro am, pro am etiquette, pebble beach pro am cost"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)

print("Updated articles.json")
