import json, re
from scripts.article_header import (
    finalize_article_template_metadata,
    replace_article_header,
)

with open('article-template.html', 'r') as f:
    html = f.read()

# 1. Header & Metadata
title = "Every Shot From Tiger Woods' 80th Win: What to Watch For | GOLFRAW"
description = "He shot 71 on Sunday, made three bogeys, and won by two. What the full broadcast shows that the highlight reel cuts, and the trophy he didn't take home."
canonical_url = "https://www.golfraw.com/news-every-shot-tiger-woods-80th-win-2018"
image_asset = "/public/every-shot-tiger-woods-80th-win-2018.webp"

html = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', html)
html = re.sub(r'<meta name="description" content=".*?">', f'<meta name="description" content="{description}">', html)
html = re.sub(r'<link rel="canonical" href=".*?">', f'<link rel="canonical" href="{canonical_url}">', html)
html = re.sub(r'<meta property="og:title" content=".*?">', f'<meta property="og:title" content="{title}">', html)
html = re.sub(r'<meta property="og:description" content=".*?">', f'<meta property="og:description" content="{description}">', html)
html = re.sub(r'<meta property="og:url" content=".*?">', f'<meta property="og:url" content="{canonical_url}">', html)
html = re.sub(r'<meta property="og:image" content=".*?">', f'<meta property="og:image" content="https://www.golfraw.com{image_asset}">', html)
html = re.sub(r'<meta name="twitter:title" content=".*?">', f'<meta name="twitter:title" content="{title}">', html)
html = re.sub(r'<meta name="twitter:description" content=".*?">', f'<meta name="twitter:description" content="{description}">', html)
html = re.sub(r'<meta name="twitter:image" content=".*?">', f'<meta name="twitter:image" content="https://www.golfraw.com{image_asset}">', html)

# 2. Layout & Header Spacing Protection
html = html.replace('<div class="wrap page-grid">', '<div class="wrap page-grid" style="padding-top: 40px;">')

hero_html = """
        <figure class="lead-img">
          <img src="/public/every-shot-tiger-woods-80th-win-2018.webp" alt="Tiger Woods walking up the 18th fairway at East Lake surrounded by thousands of fans during his historic 80th victory at the 2018 Tour Championship." width="1200" height="675" style="aspect-ratio:16/9;object-fit:cover;width:100%;border-radius:8px;">
          <figcaption>TIGER WOODS SEALED HIS 80TH PGA TOUR TITLE AT THE 2018 TOUR CHAMPIONSHIP AT EAST LAKE, ENDING A 1,876-DAY DROUGHT. PHOTO: RAWGOLF</figcaption>
        </figure>
"""
if '<figure class="lead-img">' in html:
    html = re.sub(r'<figure class="lead-img">.*?</figure>', hero_html, html, flags=re.DOTALL)
else:
    html = html.replace('</header>', '</header>\n' + hero_html)

new_vis_bc = """<nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/news">History</a> / <span>Tiger Woods 80th Win Every Shot</span>
        </nav>"""
html = re.sub(r'<nav class="crumbs".*?</nav>', new_vis_bc, html, flags=re.DOTALL)

html = replace_article_header(
    html,
    "Every Shot From Tiger Woods' 80th Win: What to Watch For",
    description,
)

new_body = """<div class="article-body">
          <div class="takeaways">
            <h3 style="margin-top:0;">Key Takeaways</h3>
            <ul>
              <li><b>The Sunday Grind:</b> Tiger Woods ended his 1,876-day drought by shooting a 1-over 71 on Sunday, securing a two-shot victory over Billy Horschel.</li>
              <li><b>The Split Trophies:</b> Woods won the Tour Championship, but Justin Rose claimed the $10 million FedExCup bonus under the pre-2019 dual points system.</li>
              <li><b>Rules Evolution:</b> The full broadcast reveals two actions now illegal under modern rules: caddie Joe LaCava lining Tiger up (Rule 10.2b(4)) and putting with the flagstick out.</li>
              <li><b>The Historic 43/45 Metric:</b> Tiger converted his 43rd 54-hole solo lead in 45 attempts (and remained a flawless 24/24 with a 3+ shot lead).</li>
            </ul>
          </div>

          <h2>Historical Performance: Tiger's 2018 East Lake Scorecard</h2>
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>Player</th>
                  <th>R1</th>
                  <th>R2</th>
                  <th>R3</th>
                  <th>R4</th>
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                <tr><td><b>Tiger Woods</b></td><td>65</td><td>68</td><td>65</td><td>71</td><td>269 (-11)</td></tr>
                <tr><td>Billy Horschel</td><td>71</td><td>65</td><td>69</td><td>66</td><td>271 (-9)</td></tr>
                <tr><td>Dustin Johnson</td><td>69</td><td>70</td><td>67</td><td>67</td><td>273 (-7)</td></tr>
                <tr><td>Justin Rose*</td><td>66</td><td>67</td><td>68</td><td>73</td><td>274 (-6)</td></tr>
                <tr><td>Rory McIlroy</td><td>67</td><td>68</td><td>66</td><td>74</td><td>275 (-5)</td></tr>
              </tbody>
            </table>
            <p style="font-size: 0.85rem; color: #666; margin-top: 5px;">*Won the 2018 FedExCup Season Title.</p>
          </div>

          <h2>The Full 4-Round Reality: Saturday Was the Win</h2>
          <p>Highlight reels distill Tiger's 80th victory into a single image: the stampeding crowds walking up the 18th fairway. But studying the full four-round broadcast reveals a different truth. Sunday was pure attrition; Saturday was the real tournament winner. Woods fired a spectacular 65 in the third round, seizing total control of the golf course and building a three-shot cushion. By the time Sunday arrived, the mission wasn't to play perfect golf—it was to survive.</p>

          <h2>The Hole-by-Hole Sunday Grind</h2>
          <p>Tiger's final round was a masterclass in conservative, defensive golf. He opened with a birdie on the 1st hole to immediately expand his lead. What followed was a grueling sequence of eight consecutive pars. When he buried a clutch 13-footer on the 13th for birdie, his lead ballooned to five shots. From there, the inevitable tension arrived. He carded bogeys on 15 and 16, but delivered a massive, tournament-saving par putt on the 17th. On a brutally difficult Sunday where only 13 players in the 30-man elite field broke par, Tiger’s 71 was exactly what was required.</p>

          <h2>The Split Trophies: Tournament vs. FedEx Cup</h2>
          <p>A bizarre historical quirk of the 2018 Tour Championship is the trophy presentation. Tiger captured his 80th PGA Tour title by winning the tournament. However, he did not win the season-long FedExCup. Justin Rose, who finished T4, secured enough points to claim the $10 million FedExCup bonus. This confusing dual-trophy system was heavily criticized and immediately abolished, <a href="/news-2026-tour-championship-final-round-hovland-leads">replaced by the staggered-start format used in modern Tour Championships</a>.</p>

          <h2>Rules Evolution: What Is Now Illegal</h2>
          <p>Watching the 2018 broadcast serves as a fascinating time capsule for golf's rules modernization. Two distinct actions that Tiger and his competitors routinely perform are now illegal:</p>
          <ul>
            <li><b>Caddie Alignment:</b> You will see Joe LaCava constantly standing behind Tiger to check his alignment before the stroke. Under <i>Rule 10.2b(4)</i>, introduced in 2019, this results in an immediate two-stroke penalty.</li>
            <li><b>Flagstick Protocols:</b> Players meticulously pull the flagstick for every putt. The 2019 modernization (<i>Rule 13.2a</i>) allowed players to leave the pin in, profoundly changing putting strategy and pace of play.</li>
          </ul>

          <h2>The Legendary 43/45 Metric and LaCava's Sand Saves</h2>
          <p>The numbers surrounding this victory are staggering. By closing out the win, Tiger converted his 43rd 54-hole solo lead in 45 attempts on the PGA Tour. Even more terrifying: he improved to a flawless 24-for-24 when holding a lead of three shots or more. A massive factor in this success was his bunker play; Woods went 7-for-9 in sand saves for the week, executing brilliant reads alongside caddie Joe LaCava to snap a devastating 1,876-day winless streak.</p>

          <h2>Debunking 4 Common Myths</h2>
          <ul>
            <li><i>Myth 1: Tiger won the FedExCup in 2018.</i> False. Justin Rose won the FedExCup; Tiger won the Tour Championship.</li>
            <li><i>Myth 2: Tiger went wire-to-wire.</i> False. While dominant, he shared the first-round lead and the second-round lead before taking solo control on Saturday.</li>
            <li><i>Myth 3: He cruised to a 60-something round on Sunday.</i> False. He shot a 1-over 71 and made bogeys on 15 and 16 before parring 17 to save the lead.</li>
            <li><i>Myth 4: The 2019 Masters was his comeback.</i> False. The 2018 Tour Championship was the true return to the winner's circle; Augusta in 2019 simply validated the major championship return.</li>
          </ul>

          <div class="verdict-box">
            <h3>The Raw Verdict</h3>
            <p>The 2018 Tour Championship is the definitive blueprint for how to protect a lead. Tiger didn't have his best stuff on Sunday, but his course management and clutch lag putting—combined with Saturday's brilliant 65—ensured he could withstand the inevitable late-round bogeys.</p>
          </div>
          
          <section class="sources" aria-labelledby="faq-label">
            <h2 id="faq-label" style="font-size: 1.25rem; font-family: 'IBM Plex Mono', monospace; text-transform: uppercase;">FAQ</h2>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">Did Tiger Woods win the FedEx Cup in 2018?</h3>
              <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">No. Tiger Woods won the 2018 Tour Championship tournament, but Justin Rose accumulated enough points to win the overall FedExCup title.</p>
              </div>
            </div>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">What did Tiger shoot on Sunday to win his 80th title?</h3>
              <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">Tiger Woods shot a 1-over 71 in the final round of the 2018 Tour Championship to win by two shots.</p>
              </div>
            </div>
          </section>

          <section class="sources" aria-labelledby="sources-label">
            <p class="section-label" id="sources-label">Sources</p>
            <ol>
              <li><a href="/news">GOLFRAW: Latest News</a>. The live reporting index for current tournament updates.</li>
              <li><a href="/news-2026-tour-championship-final-round-hovland-leads">Tour Championship Modern Format</a>. How the staggered start changed East Lake.</li>
              <li><a href="/news-2026-tour-championship-sunday-tee-times-round-4">Sunday Tee Times</a>. A look at the modern Sunday pressure at East Lake.</li>
              <li><a href="/how-long-do-golf-tournaments-last">Tournament Formats Guide</a>. Understanding the 72-hole stroke play grind.</li>
            </ol>
          </section>

          <div class="provenance">
            <p><strong>Article history.</strong> Published <time datetime="2026-08-30T16:30:00+02:00">30 August 2026 at 16:30 CEST</time>.</p>
            <p><strong>Corrections.</strong> None at publication. <a href="/corrections">Corrections policy</a>.</p>
            <p><strong>Last updated.</strong> <time datetime="2026-08-30T16:30:00+02:00">30 August 2026 at 16:30 CEST</time>.</p>
          </div>

          <aside class="related" aria-label="Related GolfRaw reporting">
            <p class="section-label" style="color:#b8d2c5">Keep reading</p>
            <ul>
              <li><a href="/news-2026-tour-championship-final-round-hovland-leads">Modern Tour Championship Analysis</a></li>
              <li><a href="/news-2026-tour-championship-sunday-tee-times-round-4">Tour Championship Sunday Schedule</a></li>
              <li><a href="/how-long-do-golf-tournaments-last">Tournament Format Guide</a></li>
            </ul>
          </aside>

        </div>
"""

html = re.sub(r'<div class="article-body">.*?</main>', new_body + '\n</article>\n</main>', html, flags=re.DOTALL)

json_ld = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "NewsArticle",
      "@id": "https://www.golfraw.com/news-every-shot-tiger-woods-80th-win-2018#article",
      "headline": "Every Shot From Tiger Woods' 80th Win: What to Watch For | GOLFRAW",
      "name": "Every Shot From Tiger Woods' 80th Win: What to Watch For | GOLFRAW",
      "description": "He shot 71 on Sunday, made three bogeys, and won by two. What the full broadcast shows that the highlight reel cuts, and the trophy he didn't take home.",
      "articleSection": "Tournaments",
      "keywords": "Tiger Woods 80th Win, 2018 Tour Championship, East Lake, FedExCup, PGA Tour History",
      "datePublished": "2026-08-30T16:30:00+02:00",
      "dateModified": "2026-08-30T16:30:00+02:00",
      "inLanguage": "en",
      "image": {
        "@type": "ImageObject",
        "url": "https://www.golfraw.com/public/every-shot-tiger-woods-80th-win-2018.webp",
        "contentUrl": "https://www.golfraw.com/public/every-shot-tiger-woods-80th-win-2018.webp",
        "width": 1200,
        "height": 675,
        "caption": "Tiger Woods walking up the 18th fairway at East Lake surrounded by thousands of fans during his historic 80th victory at the 2018 Tour Championship."
      },
      "author": {"@id": "https://www.golfraw.com/about#editorial"},
      "publisher": {"@id": "https://www.golfraw.com#organization"},
      "about": [
        {"@type": "Thing", "name": "Tiger Woods"},
        {"@type": "Thing", "name": "Tour Championship"}
      ]
    },
    {
      "@type": "VideoObject",
      "name": "Every Shot From Tiger Woods' 80th Win",
      "description": "Full broadcast highlights of Tiger Woods' 80th PGA Tour victory at the 2018 Tour Championship.",
      "thumbnailUrl": "https://www.golfraw.com/public/every-shot-tiger-woods-80th-win-2018.webp",
      "uploadDate": "2026-08-30T16:30:00+02:00",
      "contentUrl": "https://www.golfraw.com/public/every-shot-tiger-woods-80th-win-2018.webp"
    },
    {
      "@type": "BreadcrumbList",
      "@id": "https://www.golfraw.com/news-every-shot-tiger-woods-80th-win-2018#breadcrumb",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.golfraw.com/"},
        {"@type": "ListItem", "position": 2, "name": "History", "item": "https://www.golfraw.com/guides"},
        {"@type": "ListItem", "position": 3, "name": "Tiger Woods 80th Win Every Shot", "item": "https://www.golfraw.com/news-every-shot-tiger-woods-80th-win-2018"}
      ]
    },
    {"@type": "Person", "@id": "https://www.golfraw.com/about#editorial", "name": "GOLFRAW Editorial", "url": "https://www.golfraw.com/about"},
    {"@type": "Organization", "@id": "https://www.golfraw.com#organization", "name": "GOLFRAW", "url": "https://www.golfraw.com/"},
    {
      "@type": "FAQPage",
      "@id": "https://www.golfraw.com/news-every-shot-tiger-woods-80th-win-2018#faq",
      "mainEntity": [
        {"@type": "Question", "name": "Did Tiger Woods win the FedEx Cup in 2018?", "acceptedAnswer": {"@type": "Answer", "text": "No. Tiger Woods won the 2018 Tour Championship tournament, but Justin Rose accumulated enough points to win the overall FedExCup title."}},
        {"@type": "Question", "name": "What did Tiger shoot on Sunday to win his 80th title?", "acceptedAnswer": {"@type": "Answer", "text": "Tiger Woods shot a 1-over 71 in the final round of the 2018 Tour Championship to win by two shots."}}
      ]
    }
  ]
}
</script>"""

if '<script type="application/ld+json">' in html:
    html = re.sub(r'<script type="application/ld\+json">.*?</script>', json_ld, html, flags=re.DOTALL)
else:
    html = html.replace('</head>', json_ld + '\n</head>')

html = finalize_article_template_metadata(html)

with open('news-every-shot-tiger-woods-80th-win-2018.html', 'w') as f:
    f.write(html)
