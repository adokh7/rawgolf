import json

template_path = "article-template.html"
with open(template_path, "r") as f:
    template = f.read()

# Replace head metadata
template = template.replace(
    "<title>Oakmont US Open Setup: How the USGA Broke the | GOLFRAW</title>",
    "<title>A Home Solheim Cup, and the Dutch Star Can't Play | GolfRaw</title>"
)
template = template.replace(
    '<meta name="description" content="Average score 74.8, stimp at 15. We walked Oakmont&#x27;s US Open setup with two tour caddies to find out which pins cross the line — and who secretly loves it.">',
    '<meta name="description" content="Dewi Weber is ranked ahead of three of Europe\'s captain\'s picks. She can\'t be selected for the Solheim Cup in her own country because of an LET rule.">'
)
template = template.replace(
    '<link rel="canonical" href="https://www.golfraw.com/article-template">',
    '<link rel="canonical" href="https://www.golfraw.com/news-2026-solheim-cup-dewi-weber-dutch-eligibility-let">'
)
template = template.replace(
    '<meta property="og:title" content="Oakmont US Open Setup: How the USGA Broke the | GOLFRAW">',
    '<meta property="og:title" content="A Home Solheim Cup, and the Dutch Star Can\'t Play | GolfRaw">'
)
template = template.replace(
    '<meta property="og:description" content="Average score 74.8, stimp at 15. We walked Oakmont&#x27;s US Open setup with two tour caddies to find out which pins cross the line — and who secretly loves it.">',
    '<meta property="og:description" content="Dewi Weber is ranked ahead of three of Europe\'s captain\'s picks. She can\'t be selected for the Solheim Cup in her own country because of an LET rule.">'
)
template = template.replace(
    '<meta property="og:url" content="https://www.golfraw.com/article-template">',
    '<meta property="og:url" content="https://www.golfraw.com/news-2026-solheim-cup-dewi-weber-dutch-eligibility-let">'
)
template = template.replace(
    '<meta property="og:image" content="https://www.golfraw.com/public/raw-golf-practice.webp">',
    '<meta property="og:image" content="https://www.golfraw.com/public/dewi-weber-solheim-cup-2026-eligibility.webp">'
)
template = template.replace(
    '<meta name="twitter:title" content="Oakmont US Open Setup: How the USGA Broke the | GOLFRAW">',
    '<meta name="twitter:title" content="A Home Solheim Cup, and the Dutch Star Can\'t Play | GolfRaw">'
)
template = template.replace(
    '<meta name="twitter:description" content="Average score 74.8, stimp at 15. We walked Oakmont&#x27;s US Open setup with two tour caddies to find out which pins cross the line — and who secretly loves it.">',
    '<meta name="twitter:description" content="Dewi Weber is ranked ahead of three of Europe\'s captain\'s picks. She can\'t be selected for the Solheim Cup in her own country because of an LET rule.">'
)
template = template.replace(
    '<meta name="twitter:image" content="https://www.golfraw.com/public/raw-golf-practice.webp">',
    '<meta name="twitter:image" content="https://www.golfraw.com/public/dewi-weber-solheim-cup-2026-eligibility.webp">'
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
    '"headline": "A Home Solheim Cup, and the Dutch Star Can\'t Play",'
)
template = template.replace(
    '"description": "Average score 74.8, greens at 15 on the stimp. Two tour caddies walked us through the US Open setup built to break the field.",',
    '"description": "Dewi Weber is ranked ahead of three of Europe\'s captain\'s picks. She can\'t be selected for the Solheim Cup in her own country because of an LET rule.",'
)
template = template.replace(
    '"https://www.golfraw.com/public/img/oakmont-2026-setup-og.jpg"',
    '"https://www.golfraw.com/public/dewi-weber-solheim-cup-2026-eligibility.webp"'
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
    '"mainEntityOfPage": "https://www.golfraw.com/news-2026-solheim-cup-dewi-weber-dutch-eligibility-let"'
)

new_article_content = """<article>
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/#news">News</a> / <span>Solheim Cup</span>
        </nav>

        <header class="article-head">
          <span class="cat">News · Solheim Cup</span>
          <h1>The First Dutch Woman to Make a Solheim Cup Won't Be Playing the One in the Netherlands</h1>
          <p class="standfirst">Dewi Weber discovered her ineligibility for the 2026 Solheim Cup from a reporter shortly after finishing tied for third at the KPMG Women's PGA Championship at Hazeltine—a career-best major result that earned her $752,089 and vaulted her to 82nd in the world rankings. Because she plays exclusively on the LPGA and lacks Ladies European Tour (LET) membership, European team rules prohibit her selection as either an automatic qualifier or a captain's pick.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>TUE 11 AUG 2026</b></span>
            <span><b>4 MIN READ</b></span>
          </div>
        </header>

        <div class="meta-callout" style="border-left: 4px solid #10b981; padding-left: 12px; margin: 16px 0;">
          <strong>Solheim Cup 2026 News:</strong> August 11, 2026 | Team Europe Eligibility & Selection Rules
        </div>

        <figure class="lead-img">
            <img src="/public/dewi-weber-solheim-cup-2026-eligibility.webp" alt="Dewi Weber Solheim Cup 2026 Eligibility" />
        </figure>
        <figcaption>WEBER'S LET INELIGIBILITY BARS HER FROM THE HISTORIC TOURNAMENT.</figcaption>

        <div class="article-body">
          <h2>Why the Ruling Stings in a Historic Host Year</h2>
          <p>The 2026 Solheim Cup takes place at Bernardus Golf in Cromvoirt, North Brabant, marking the first time the matches have been hosted in the Netherlands. No Dutch woman has ever competed in the Solheim Cup, leaving a home tournament without a native player on the European roster despite Weber ranking ahead of three of captain Anna Nordqvist's four wildcards.</p>

          <h2>Understanding the LET Membership Requirement</h2>
          <p>The LET mandates active tour membership for Solheim Cup eligibility to protect the tour's identity and ensure players support European events. To gain emergency eligibility during the qualifying window, Weber would have needed a victory in an LET-sanctioned event—a feat previously accomplished by Finland's Matilda Castren in 2021.</p>

          <h2>Team Europe Roster Lineup</h2>
          <p>Captain Anna Nordqvist's European squad looking to regain the trophy includes:</p>

          <ul>
            <li><strong>Automatic via LET Points:</strong> Charley Hull and Esther Henseleit.</li>
            <li><strong>Automatic via World Ranking:</strong> Lottie Woad, Maja Stark, Linn Grant, Carlota Ciganda, Céline Boutier, Nanna Koerstz Madsen.</li>
            <li><strong>Captain's Picks:</strong> Leona Maguire, Julia López Ramírez, Nastasia Nadaud, Mimi Rhodes.</li>
          </ul>

          <div class="faq-section">
            <h2>Frequently Asked Questions</h2>

            <h3>Why can't Dewi Weber play in the 2026 Solheim Cup?</h3>
            <p>Weber lacks active membership on the Ladies European Tour (LET), which is a mandatory prerequisite for European Solheim Cup qualification and captain selection.</p>

            <h3>Where is the 2026 Solheim Cup being held?</h3>
            <p>The 2026 Solheim Cup takes place at Bernardus Golf in Cromvoirt, Netherlands, from September 7 to 13.</p>

            <h3>Has a player ever gained emergency LET membership to qualify?</h3>
            <p>Yes. Finland's Matilda Castren won the 2021 Grant Ladies Open in Finland to secure immediate LET membership and subsequently represented Europe at Inverness.</p>

            <h3>Is Dewi Weber ranked higher than any selected European players?</h3>
            <p>Yes. Ranked 82nd in the world following her T3 finish at Hazeltine, Weber sits ahead of three captain's picks, including Mimi Rhodes (91st).</p>
          </div>

          <h2>The Raw Take</h2>
          <p>An eligibility rule designed to safeguard tour loyalty has inadvertently barred the host nation's highest-ranked player from a milestone home event. While protecting tour interests is essential, Weber's exclusion highlights how rigid administrative barriers can undermine major promotional opportunities for European golf.</p>
        </div>
      </article>"""

article_start_tag = "<article>"
article_end_tag = "</article>"

start_idx = template.find(article_start_tag)
end_idx = template.find(article_end_tag) + len(article_end_tag)

new_html = template[:start_idx] + new_article_content + template[end_idx:]

with open("news-2026-solheim-cup-dewi-weber-dutch-eligibility-let.html", "w") as f:
    f.write(new_html)

print("Created news-2026-solheim-cup-dewi-weber-dutch-eligibility-let.html")

# Update articles.json
with open("articles.json", "r") as f:
    data = json.load(f)

new_article = {
  "url": "/news-2026-solheim-cup-dewi-weber-dutch-eligibility-let",
  "title": "A Home Solheim Cup, and the Dutch Star Can't Play",
  "category": "SOLHEIM CUP",
  "date": "AUG 11 2026",
  "image": "/public/dewi-weber-solheim-cup-2026-eligibility.webp",
  "snippet": "Dewi Weber is ranked ahead of three of Europe's captain's picks. She can't be selected for the Solheim Cup in her own country because of an LET rule.",
  "keywords": "dewi weber solheim cup, solheim cup eligibility rules, let membership solheim cup, solheim cup 2026 netherlands, why is dewi weber not in the solheim cup"
}

data["articles"].insert(0, new_article)

with open("articles.json", "w") as f:
    json.dump(data, f, indent=2)

print("Updated articles.json")
