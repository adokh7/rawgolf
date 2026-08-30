import re
from pathlib import Path
from scripts.fix_template_metadata import finalize_html

ROOT = Path(__file__).resolve().parent
template_path = ROOT / 'article-template.html'
output_path = ROOT / 'news-2026-lee-westwood-liv-golf-bedminster-expectations.html'

with template_path.open('r') as f:
    template = f.read()

# Meta replacements
template = re.sub(r'<title>.*?</title>', '<title>Westwood Is 53, Four Back, and Done With Expectations | GolfRaw</title>', template)
template = re.sub(r'<meta name="description"\s*content=".*?">', '<meta name="description"\n    content="Everyone ran the \'brain-dead\' quote. The one after it is better: Westwood on why he stopped setting expectations — and he\'s four off the lead at 53.">', template)
template = re.sub(r'<link rel="canonical" href=".*?">', '<link rel="canonical" href="https://www.golfraw.com/news-2026-lee-westwood-liv-golf-bedminster-expectations">', template)
template = re.sub(r'<meta property="og:title" content=".*?" />', '<meta property="og:title" content="Lee Westwood Is 53, Four Back, and Done With Expectations" />', template)
template = re.sub(r'<meta property="og:description" content=".*?" />', '<meta property="og:description" content="Everyone ran the \'brain-dead\' quote. The one after it is better: Westwood on why he stopped setting expectations — and he\'s four off the lead at 53." />', template)
template = re.sub(r'<meta property="og:url" content=".*?" />', '<meta property="og:url" content="https://www.golfraw.com/news-2026-lee-westwood-liv-golf-bedminster-expectations" />', template)
template = re.sub(r'<meta property="og:image" content=".*?">', '<meta property="og:image" content="https://www.golfraw.com/public/lee-westwood-liv-golf-bedminster.webp">', template)
template = re.sub(r'<meta name="twitter:title" content=".*?">', '<meta name="twitter:title" content="Lee Westwood Is 53, Four Back, and Done With Expectations">', template)
template = re.sub(r'<meta name="twitter:description"\s*content=".*?">', '<meta name="twitter:description"\n    content="Everyone ran the \'brain-dead\' quote. The one after it is better: Westwood on why he stopped setting expectations — and he\'s four off the lead at 53.">', template)
template = re.sub(r'<meta name="twitter:image" content=".*?">', '<meta name="twitter:image" content="https://www.golfraw.com/public/lee-westwood-liv-golf-bedminster.webp">', template)
template = re.sub(r'<meta property="article:published_time" content=".*?" />', '<meta property="article:published_time" content="2026-08-09T07:30:00+02:00" />', template)

new_article = """<article>
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/#liv-golf">LIV Golf</a> / <span>Bedminster</span>
        </nav>

        <header class="article-head">
          <span class="cat">LIV GOLF · Bedminster</span>
          <h1>Lee Westwood Is 53, Four Back, and Done With Expectations</h1>
          <p class="standfirst">A journalist asked Lee Westwood after his third round at Bedminster whether he's happy with what he's achieved. The answer that made headlines was a blunt dismissal of internet detractors, but the reflection that followed was far more compelling.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>AUG 09 2026</b></span>
          </div>
        </header>

        <div class="meta-callout" style="border-left: 4px solid #10b981; padding-left: 12px; margin: 16px 0;">
          <strong>LIV Golf Dynamics:</strong> August 9, 2026 | Player Psychology & Tournament Standings
        </div>

        <figure class="lead-img">
          <img src="/public/lee-westwood-liv-golf-bedminster.webp" alt="Lee Westwood LIV Golf Bedminster Trump National" />
        </figure>

        <div class="article-body">
          <p>Westwood described himself as a young lad from Worksop, raised in a family where nobody played golf, who picked up a club one summer holiday and eventually became the world's top-ranked golfer by 2010. Reaching the peak of world golf without a silver-spoon background remains an extraordinary feat, regardless of major tallies.</p>

          <h2>Four Back With One Round to Go</h2>
          <p>The actual news on the course is being eclipsed by narrative debates. Westwood is 53 years old and trails Joaquín Niemann by four shots heading into Sunday at Trump National Bedminster — a grinding course playing at 7,651 yards, making it the second-longest venue LIV Golf has visited all season.</p>

          <p>Westwood hasn't won a tournament in four years on LIV. Niemann, at 27, has more LIV titles than anyone and led from the opening round following a bogey-free 64. Four shots is a significant gap on a layout this long, but it isn't insurmountable.</p>

          <h2>The Quote Worth Stealing</h2>
          <p>Asked what he expects from his game now, Westwood offered a masterclass in modern sports psychology: he simply stopped setting expectations altogether.</p>

          <p>He explained that while he remains intensely competitive, his only standard is giving 100 percent effort on every single shot. If that effort is good enough to contend, wonderful. If father time renders it insufficient, he accepts it. Playing without artificial goals, he noted, is what being "in the zone" genuinely feels like.</p>

          <p>For mid-handicap club golfers, this is the ultimate lesson. Fighting natural decline with constant swing overhauls and equipment changes often creates frustration. Accepting where your game sits today allows you to play with complete freedom.</p>

          <h2>Reframing the Legacy Narrative</h2>
          <p>Pundits often claim that missing out on a major championship undoubtedly haunts Westwood's career. Yet, hearing a 44-time professional winner state clearly that he is content with a 34-year career reframes that assumption. Telling a veteran golfer what he secretly feels inside his head ignores the reality of what he says out loud.</p>

          <p>He was the best player in the world. He never won a major. Both facts are true, and only Westwood knows how heavily the latter weighs on his mind.</p>

          <div class="faq-section">
            <h2>Frequently Asked Questions</h2>

            <h3>How old is Lee Westwood?</h3>
            <p>Lee Westwood is 53 years old. He is competing at LIV Golf New York at Trump National Bedminster.</p>

            <h3>How many tournaments has Lee Westwood won?</h3>
            <p>Westwood has won 44 professional tournaments worldwide throughout his career and reached World No. 1 in 2010.</p>

            <h3>Has Lee Westwood won a LIV Golf event?</h3>
            <p>No, Westwood joined LIV Golf in 2022 and is still searching for his first individual victory on the tour.</p>

            <h3>What did Westwood say about golf expectations?</h3>
            <p>He stated that he has stopped setting scoring targets, focusing solely on giving his full competitive effort and accepting whatever result his game produces.</p>
          </div>

          <h2>The Raw Take</h2>
          <p>Most 53-year-old golfers are fighting their swings or nursing bad backs. Lee Westwood is four shots off the lead on a 7,651-yard monster because he stopped measuring his golf against who he was 15 years ago. The secret to longevity in golf isn't pretending you're still 35 — it's playing the exact golf you have today without fear of the scorecard.</p>
        
          <nav class="tag-row" aria-label="Article tags">
            <a href="#">Lee Westwood</a>
            <a href="#">LIV Golf</a>
            <a href="#">Bedminster</a>
            <a href="#">Psychology</a>
          </nav>
        </div>
      </article>"""

template = re.sub(r'<article>.*?</article>', new_article, template, flags=re.DOTALL)

template = finalize_html(
    template,
    output_path,
    force=True,
)

with output_path.open('w') as f:
    f.write(template)

print("Article generated.")
