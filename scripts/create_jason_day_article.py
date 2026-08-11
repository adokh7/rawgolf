import json
import re
from bs4 import BeautifulSoup

base_file = "news-2026-what-beginners-actually-search.html"
target_file = "news-2026-jason-day-wyndham-streak-ended.html"

with open(base_file, "r") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

title_str = "19 Straight Playoffs. Jason Day's Streak Just Ended. | GolfRaw"
desc_str = "Jason Day missed the cut at Sedgefield and ended 19 consecutive FedExCup Playoffs appearances. Bradley and Finau survived on the number. Who needs what now."
url = "https://www.golfraw.com/news-2026-jason-day-wyndham-streak-ended"
img_url = "https://www.golfraw.com/public/jason-day-wyndham-streak-ended.webp"
date_pub = "2026-08-08T08:00:00+02:00"

soup.title.string = title_str
soup.find("meta", {"name": "description"})["content"] = desc_str
soup.find("link", {"rel": "canonical"})["href"] = url

soup.find("meta", {"property": "og:title"})["content"] = title_str
soup.find("meta", {"property": "og:description"})["content"] = desc_str
soup.find("meta", {"property": "og:url"})["content"] = url
soup.find("meta", {"property": "og:image"})["content"] = img_url
soup.find("meta", {"property": "article:published_time"})["content"] = date_pub
soup.find("meta", {"property": "article:modified_time"})["content"] = date_pub
soup.find("meta", {"property": "article:section"})["content"] = "News"

soup.find("meta", {"name": "twitter:title"})["content"] = title_str
soup.find("meta", {"name": "twitter:description"})["content"] = desc_str
soup.find("meta", {"name": "twitter:image"})["content"] = img_url

# Breadcrumbs
crumbs = soup.find("nav", class_="crumbs")
if crumbs:
    crumbs.clear()
    a1 = soup.new_tag("a", href="/")
    a1.string = "RawGolf"
    a2 = soup.new_tag("a", href="news")
    a2.string = "Latest News"
    sp = soup.new_tag("span")
    sp.string = "PGA Tour"
    crumbs.append(a1)
    crumbs.append(" / ")
    crumbs.append(a2)
    crumbs.append(" / ")
    crumbs.append(sp)

# Article Head
head = soup.find("header", class_="article-head")
if head:
    cat = head.find("span", class_="cat")
    if cat: cat.string = "NEWS · PGA TOUR"
    h1 = head.find("h1")
    if h1: h1.string = "Jason Day's Streak Ended on a Friday in Greensboro"
    sf = head.find("p", class_="standfirst")
    if sf: sf.string = "Jason Day missed the cut at Sedgefield and ended 19 consecutive FedExCup Playoffs appearances. Bradley and Finau survived on the number. Who needs what now."
    byline = head.find("div", class_="byline")
    if byline:
        # replace second span with PUBLISHED
        spans = byline.find_all("span")
        if len(spans) > 1:
            pub = spans[1]
            pub.clear()
            pub.append("PUBLISHED ")
            b = soup.new_tag("b")
            b.string = "AUG 08 2026"
            pub.append(b)

# Replace image
fig = soup.find("figure", class_="lead-img")
if fig:
    img = fig.find("img")
    if not img:
        img = soup.new_tag("img")
        fig.append(img)
    img["src"] = "/public/jason-day-wyndham-streak-ended.webp"
    img["alt"] = "Jason Day Wyndham Championship FedExCup Streak Ended"
    figcap = soup.find("figcaption")
    if figcap:
        figcap.decompose()

# Article Body
article_body = soup.find("div", class_="article-body")
article_body.clear()

body_content = """
<p class="standfirst">Jason Day has played in the FedExCup Playoffs every year since they started counting his appearances — eighteen consecutive seasons, going back to a time when he was 20 and the tournament had a different sponsor structure and half the current field weren't born golfers yet. It ended on Friday afternoon at Sedgefield Country Club with a 73.</p>

<div class="meta-callout" style="border-left: 4px solid #10b981; padding-left: 12px; margin: 16px 0;">
  <strong>Wyndham Championship Cut Line:</strong> August 8, 2026 | FedExCup Playoffs Bubble
</div>

<p>He finished at four over, the cut fell at three under, and there was nothing left to play for. He'd withdrawn before teeing off at each of his last two events with a back problem that had already ended his U.S. Open early. He arrived 75th in the FedExCup needing at least a two-way tie for twelfth just to reach the top seventy. In his nineteenth season, the arithmetic ran out. Nobody hits a shot to end a streak like that. It just stops.</p>

<h2>Bradley and Finau Made It By Nothing At All</h2>
<p>The cut line hovered at three under all Friday afternoon, meaning every group coming in was doing mental arithmetic on the walk down eighteen.</p>

<p>Keegan Bradley played his last six holes in three under to finish exactly on the number. He's made fifteen straight Playoffs and said plainly that he wants to make this one a lot. He sits 73rd and needs at least a two-way tie for thirty-eighth over the weekend.</p>

<p>Tony Finau also finished at three under, keeping alive a run of eleven consecutive appearances. He's 89th, which means he needs a two-way tie for third — a top-three finish, more or less, in two rounds. Finau's assessment of his year was harder than anything a journalist would have written. He called it a failed season up to this point, said there was no sugarcoating it, and added he'd always worked on the principle that you either win or you learn, and that this year had been a lot of learning. Six-time Tour winner, fifteen cuts made from twenty-one starts, one top ten. He's not wrong about the season and he's not making excuses about it either, which is rarer.</p>

<h2>The Detail That Makes the Weekend Strange</h2>
<p>Bradley is chasing Jackson Koivun. Koivun is the 21-year-old rookie who holds seventieth place, the last playoff spot, after winning the 3M Open two weeks ago by three shots over Scottie Scheffler. Bradley, at 73rd, needs to climb past him or past somebody near him.</p>

<p>Bradley is also part of the United States' Presidents Cup leadership alongside Brandt Snedeker. So one of the men who will have a say in whether Koivun makes that team is spending this weekend trying to take his playoff place off him. Both things are entirely proper and neither man has said a word about it. It's just an unusually direct version of a situation that exists all over professional sport, and the fact that nobody has remarked on it says something about how normal it's become. Snedeker, incidentally, played a practice round with Koivun on Tuesday and called him a generational player.</p>

<h2>Where the Rest of It Stands</h2>
<p>Beau Hossler leads, having holed a birdie putt on the last for the solo lead. He began the week 122nd and needing to win outright; after Thursday's 61 the projections had him around 52nd. Round two was interrupted by a lightning delay.</p>

<p>Brooks Koepka is 86th and needs no worse than a solo fourth. Andrew Novak is 91st, also needing a two-way tie for third. Max Greyserman is 99th and needs a solo third. Sedgefield is a par 70 of 7,131 yards that has required at least twenty under to win in eight of the past ten years. Cameron Young tied the tournament record at 22-under 258 here last season for his first Tour victory, winning by six. He's back defending, and after opening one over he was in danger of missing his first cut of the year.</p>

<h2>What This Looks Like From a Normal Golf Club</h2>
<p>Day's streak didn't end because he played badly this week, particularly. It ended because he had a back injury in June, withdrew from two tournaments, and arrived somewhere he couldn't recover from in four rounds.</p>

<p>That's how these things usually go. Not a collapse — an accumulation. A bad month in the spring, an injury at the wrong moment, and by August the numbers have already decided. The version of this that happens to you is missing your club's order of merit by two points because you were away for a fortnight in June. It feels like a verdict on your golf. It's mostly a verdict on your calendar.</p>

<p>The other thing worth taking is Bradley's last six holes. Three under, needing every one of them, knowing exactly what the number was. Most people play worse when the situation is that clear. Playing better is a skill and it isn't the same skill as hitting a golf ball.</p>

<div class="faq-section" style="background:var(--white); border:2px solid var(--ink); padding:24px; margin:32px 0;">
  <h2 style="margin-top:0;">Frequently Asked Questions</h2>

  <h3 style="font-size:18px; margin-top:16px;">Did Jason Day make the cut at the Wyndham Championship?</h3>
  <p>No. A second-round 73 left him at four over, and the cut fell at three under. It ended his streak of 19 consecutive FedExCup Playoff seasons.</p>

  <h3 style="font-size:18px; margin-top:16px;">Did Keegan Bradley make the cut?</h3>
  <p>Yes, exactly on the number at three under, after playing his last six holes in three under. He's 73rd in the FedExCup and needs at least a two-way tie for 38th to reach Memphis.</p>

  <h3 style="font-size:18px; margin-top:16px;">What does Tony Finau need?</h3>
  <p>A two-way tie for third or better. He's 89th in the FedExCup and made the cut at three under, keeping alive a run of 11 straight Playoffs appearances.</p>

  <h3 style="font-size:18px; margin-top:16px;">Who leads the Wyndham Championship?</h3>
  <p>Beau Hossler, after birdieing the last for the solo lead. He started the week 122nd in points and needing to win outright to reach the playoffs.</p>

  <h3 style="font-size:18px; margin-top:16px;">Who else needs a big weekend?</h3>
  <p>Brooks Koepka at 86th needs no worse than a solo fourth. Andrew Novak at 91st needs a two-way tie for third. Max Greyserman at 99th needs a solo third. Jackson Koivun, 21, holds the final spot at 70th.</p>
</div>

<h2>The Raw Take</h2>
<p>Endings in professional golf are rarely dramatic; they are usually mathematical. Jason Day didn't lose his 18-year streak on the 18th green at Sedgefield — he lost it in the trainer's room in June. And while guys like Keegan Bradley proved they have the distinct, unteachable skill of playing great golf when they absolutely have to, Day's early exit is a reminder that you can't outplay an empty calendar.</p>

  <div class="tag-row">
    <a href="search">Jason Day</a>
    <a href="search">Wyndham Championship</a>
    <a href="search">FedExCup</a>
  </div>
"""

parsed_body = BeautifulSoup(body_content, "html.parser")
article_body.append(parsed_body)

# Structured JSON
ld_script = soup.find("script", {"type": "application/ld+json"})
if ld_script:
    data = json.loads(ld_script.string)
    
    # Check if it's an array of items (like in what-beginners-actually-search.html)
    if "@graph" in data:
        article_data = data["@graph"][0]
        article_data["headline"] = title_str
        article_data["description"] = desc_str
        if "image" in article_data:
            article_data["image"] = [img_url]
        article_data["datePublished"] = date_pub
        article_data["dateModified"] = date_pub
        article_data["mainEntityOfPage"] = {"@type": "WebPage", "@id": url}
        article_data["@id"] = f"{url}#article"
        if len(data["@graph"]) > 1:
            data["@graph"].pop(1) # remove FAQ schema from template if there
    else:
        data["headline"] = title_str
        data["description"] = desc_str
        data["image"] = [img_url]
        data["datePublished"] = date_pub
        data["dateModified"] = date_pub
        data["mainEntityOfPage"] = url
        
    ld_script.string = "\n" + json.dumps(data, indent=2) + "\n  "

with open(target_file, "w") as f:
    f.write(str(soup))
