import json
import re
import os
from bs4 import BeautifulSoup

base_file = "news-2026-liv-golf-secures-lead-investor.html"
target_file = "news-2026-liv-golf-investor-bc-partners-dechambeau.html"

with open(base_file, "r") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

title_str = "LIV's Secret Investor Lends to DeChambeau's Agency | GolfRaw"
desc_str = "Bloomberg and the FT name BC Partners as LIV's investor — a lender to Bryson DeChambeau's agency. And LIV quietly lost its feeder tour to the PGA Tour."
url = "https://www.golfraw.com/news-2026-liv-golf-investor-bc-partners-dechambeau"
img_url = "https://www.golfraw.com/public/liv-golf-bc-partners-dechambeau.webp"
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

soup.find("meta", {"name": "twitter:title"})["content"] = title_str
soup.find("meta", {"name": "twitter:description"})["content"] = desc_str
soup.find("meta", {"name": "twitter:image"})["content"] = img_url

# Structured data
ld_script = soup.find("script", {"type": "application/ld+json"})
if ld_script:
    data = json.loads(ld_script.string)
    data["headline"] = title_str
    data["description"] = desc_str
    data["image"] = [img_url]
    data["datePublished"] = date_pub
    data["dateModified"] = date_pub
    data["mainEntityOfPage"] = url
    ld_script.string = "\n" + json.dumps(data, indent=2) + "\n  "

# Body
head = soup.find("header", class_="article-head")
head.find("h1").string = "The Mystery Investor Has a Name. It Lends Money to Bryson DeChambeau's Agency."
standfirst = head.find("p", class_="standfirst")
standfirst.clear()
standfirst.append("When Scott O'Neil stood up at Bedminster on Wednesday and said ")
a = soup.new_tag("a", href="/liv-golf-bankruptcy-what-is-confirmed")
a.string = "LIV Golf had a signed term sheet with a lead investor"
standfirst.append(a)
standfirst.append(", he wouldn't say who it was. Bloomberg and the Financial Times have both since reported that it's BC Partners, a British investment firm.")

byline = head.find("div", class_="byline")
pub = byline.find_all("span")[1]
pub.clear()
pub.append("PUBLISHED ")
b = soup.new_tag("b")
b.string = "AUG 08 2026"
pub.append(b)

img = soup.find("img", alt="LIV Golf Lead Investor")
img["src"] = "/public/liv-golf-bc-partners-dechambeau.webp"
img["alt"] = "Bryson DeChambeau LIV Golf BC Partners Investor"

article_body = soup.find("div", class_="article-body")
article_body.clear()

body_content = """
  <div class="meta-callout" style="border-left: 4px solid #10b981; padding-left: 12px; margin: 16px 0;">
    <strong>LIV Golf Funding Update:</strong> August 8, 2026 | Investors & Structural Changes
  </div>
  
  <p>That's newsworthy on its own. What makes it more than newsworthy is a detail golf.com noticed and almost nobody else has picked up: BC Partners is a lender to GSE Worldwide, the agency that represents Bryson DeChambeau.</p>
  
  <p>DeChambeau is LIV's biggest American draw. He led a players-only meeting at Bedminster the day before the announcement. He has been visibly involved in the league's business discussions throughout the <a href="/liv-golf-bankruptcy-what-is-confirmed">funding crisis</a>. And his contract expires at the end of this season.</p>
  
  <p>I want to be careful here. Neither Bloomberg nor the FT has alleged wrongdoing, LIV has not confirmed the investor's identity at all, and a firm lending to an agency is several steps removed from that agency's clients. This is not a scandal. But it is a connection that anyone assessing the deal should know about, and it is the sort of thing that usually surfaces later and looks worse for having surfaced late.</p>
  
  <h2>The Thing That Happened While Everyone Watched the Money</h2>
  <p>Here's what I think is the bigger story, and it's barely being covered. <strong>The Asian Tour has left.</strong></p>
  
  <p>LIV founded the ten-event International Series on the Asian Tour before its 2022 launch. That circuit was LIV's feeder system, its promotion and relegation pathway, and — crucially — a significant part of how its players accumulated world ranking points. It was the mechanism by which LIV argued it belonged in the sport's official structure.</p>
  
  <p>The Asian Tour has now signed with the PGA Tour and the DP World Tour instead.</p>
  
  <p>So in the same few weeks, LIV lost its funder and its ladder. Money can be replaced; several firms are apparently willing to try. A route into the world rankings is considerably harder to rebuild, and without one, LIV players have to qualify for majors on results earned elsewhere.</p>
  
  <p>Nobody at the Bedminster press conference was asked about it, as far as I can tell from the coverage.</p>
  
  <h2>What the Deal Actually Has to Cover</h2>
  <p>O'Neil has said he needs between $300 and $350 million, by roughly the first of September, and that with $350m the LIV 2.0 plan turns a profit within three years. The New York Post reported anchor investors ready for $250 million.</p>
  
  <p>Set that against what it's replacing. LIV launched in 2022 with a $400 million initial investment and $250 million in prize purses. PIF has put in billions since. Golfweek's Eamon Lynch put the incoming figure at roughly a quarter of what the Saudis were spending annually.</p>
  
  <p>And there are obligations sitting underneath it. Jon Rahm is reportedly owed $150 million from his original contract. LIV is being sued by World Golf Group and Premier Golf League for somewhere between $210 and $630 million, and separately by a Canadian technology supplier for over a million.</p>
  
  <p>Which is why O'Neil's own framing matters so much. Asked how players get paid in the new structure, he said this second bite is equity instead of cash. He added that some players like the responsibility of controlling their own financial destiny.</p>
  
  <p>That's a considerably more honest description of the arrangement than "players become majority owners," and he gave it himself, within hours.</p>
  
  <h2>Two People in the Industry, Saying It Plainly</h2>
  <p>Max Greyserman, a PGA Tour player, told the NUCLR golf podcast that even with funding, LIV as it was is finished — that you're kidding yourself if you think commercial success is in its future, because that's been tested already. He thinks it continues as a shell of itself.</p>
  
  <p>Dan Rapaport made the arithmetic point: $250 million doesn't stretch to $40 million in a single week, and even with the Saudi money the audience never arrived, so a scaled-down version breaking through is a hard case to make.</p>
  
  <p>Both are opinions rather than reporting, and both come from people with a view. But neither is contradicted by anything LIV has said, and the second one is just division.</p>
  
  <h2>What LIV 2.0 Is Supposed to Be</h2>
  <p>Ten events. Five in the United States, positioned in the weeks before the majors, and five overseas. Down from fourteen this season — or from what was meant to be fourteen, since New Orleans was cancelled and the Michigan team championship's status remains genuinely unresolved with three weeks to go and no build-out reported at the venue.</p>
  
  <p>Purses around $10 million, against something between $25 and $30 million now, depending on which reported figure you use. Nobody has published one I can reconcile.</p>
  
  <h2>Where This Leaves Things</h2>
  <ul>
    <li><strong>Confirmed by LIV, on the record:</strong> a signed term sheet, board-approved, targeted to close in September, with players becoming majority equity holders instead of receiving cash.</li>
    <li><strong>Reported but unconfirmed by LIV:</strong> the investor is BC Partners. The sum is somewhere between $250 and $350 million. The Michigan finale is cancelled. Staff have received termination notices.</li>
    <li><strong>Not in dispute and largely undiscussed:</strong> the Asian Tour has gone.</li>
  </ul>
  
  <p>Golf's most expensive experiment is being refinanced at roughly a quarter of its old running cost by a firm nobody at the league will name, whose exposure includes a lender relationship with the agency of its most marketable player, three weeks before a season finale that may not happen, without the feeder tour that justified its place in the sport.</p>
  
  <p>Somebody is going to write the book on this. It'll be a good one.</p>
  
  <div class="faq-section" style="background:var(--white); border:2px solid var(--ink); padding:24px; margin:32px 0;">
    <h2 style="margin-top:0;">Frequently Asked Questions</h2>
  
    <h3 style="font-size:18px; margin-top:16px;">Who is investing in LIV Golf?</h3>
    <p>LIV has not named the investor. Bloomberg and the Financial Times have both reported it is BC Partners, a British investment firm. LIV confirmed only that a term sheet has been signed and board-approved, with the transaction targeted for September.</p>
  
    <h3 style="font-size:18px; margin-top:16px;">What is the connection to Bryson DeChambeau?</h3>
    <p>BC Partners is reported to be a lender to GSE Worldwide, the agency that represents DeChambeau. No wrongdoing has been alleged by anyone, and LIV has not confirmed the investor's identity.</p>
  
    <h3 style="font-size:18px; margin-top:16px;">How much money does LIV need?</h3>
    <p>O'Neil has said $300–350 million, by around 1 September. Reports have put the incoming figure at $250–300 million. LIV launched in 2022 with a $400 million initial investment.</p>
  
    <h3 style="font-size:18px; margin-top:16px;">What happened with the Asian Tour?</h3>
    <p>The Asian Tour, which hosted LIV's ten-event International Series and provided a promotion pathway and world ranking points, has signed a deal with the PGA Tour and DP World Tour instead.</p>
  
    <h3 style="font-size:18px; margin-top:16px;">What will LIV Golf look like in 2027?</h3>
    <p>Ten events — five in the US before the majors, five overseas — down from fourteen, with purses around $10 million rather than $25–30 million.</p>
  
    <h3 style="font-size:18px; margin-top:16px;">Are players really becoming owners?</h3>
    <p>LIV says players will be majority equity holders. O'Neil clarified that the equity comes instead of cash rather than in addition to it. LIV reportedly still owes some players nine-figure sums.</p>
  </div>
  
  <h2>The Raw Take</h2>
  <p>LIV's scramble for cash is loud, but losing the Asian Tour is the structural earthquake nobody is talking about. Without ranking points or a pathway to the majors, the new investors aren't buying a rival global league — they're buying a closed-loop exhibition struggling to pay its own players.</p>

  <div class="tag-row">
    <a href="search">LIV Golf</a>
    <a href="search">Bryson DeChambeau</a>
    <a href="search">BC Partners</a>
  </div>
"""

parsed_body = BeautifulSoup(body_content, "html.parser")
article_body.append(parsed_body)

# Write using pretty print but preserving our structure
with open(target_file, "w") as f:
    f.write(str(soup))
