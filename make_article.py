import re
from scripts.fix_template_metadata import finalize_html

with open('/Users/adnan/Desktop/golf/article-template.html', 'r') as f:
    html = f.read()

# Replace title
html = re.sub(r'<title>.*?</title>', '<title>40,500 Search "Beginner Clubs"; 1,600 "Golf" | GolfRaw</title>', html, flags=re.DOTALL)
html = re.sub(r'<meta name="description".*?>', '<meta name="description"\n    content="40,500 people a month search for beginner golf clubs. 590 ask what a handicap is. What the search data reveals about how beginners are being sold to.">', html, flags=re.DOTALL)
html = re.sub(r'<link rel="canonical" href="https://www.golfraw.com/article-template">', '<link rel="canonical" href="https://www.golfraw.com/what-beginners-actually-search">', html)

# Replace OG tags
html = re.sub(r'<meta property="og:title" content=".*?" />', '<meta property="og:title" content="40,500 Search &quot;Beginner Clubs&quot;; 1,600 &quot;Golf&quot; | GolfRaw" />', html)
html = re.sub(r'<meta property="og:description" content=".*?" />', '<meta property="og:description" content="40,500 people a month search for beginner golf clubs. 590 ask what a handicap is. What the search data reveals about how beginners are being sold to." />', html)
html = re.sub(r'<meta property="og:url" content=".*?" />', '<meta property="og:url" content="https://www.golfraw.com/what-beginners-actually-search" />', html)
html = re.sub(r'<meta property="og:image" content=".*?">', '<meta property="og:image" content="https://www.golfraw.com/public/what-beginners-actually-search.webp">', html)

# Replace Twitter tags
html = re.sub(r'<meta name="twitter:title" content=".*?">', '<meta name="twitter:title" content="40,500 Search &quot;Beginner Clubs&quot;; 1,600 &quot;Golf&quot; | GolfRaw">', html)
html = re.sub(r'<meta name="twitter:description".*?>', '<meta name="twitter:description"\n    content="40,500 people a month search for beginner golf clubs. 590 ask what a handicap is. What the search data reveals about how beginners are being sold to.">', html, flags=re.DOTALL)
html = re.sub(r'<meta name="twitter:image" content=".*?">', '<meta name="twitter:image" content="https://www.golfraw.com/public/what-beginners-actually-search.webp">', html)

schema_json = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Article",
      "@id": "https://www.golfraw.com/what-beginners-actually-search#article",
      "headline": "40,500 People a Month Search 'Golf Clubs for Beginners.' 1,600 Search 'Golf for Beginners.'",
      "description": "40,500 people a month search for beginner golf clubs. 590 ask what a handicap is. What the search data reveals about how beginners are being sold to.",
      "mainEntityOfPage": {
        "@type": "WebPage",
        "@id": "https://www.golfraw.com/what-beginners-actually-search"
      },
      "datePublished": "2026-08-05",
      "dateModified": "2026-08-05",
      "publisher": {
        "@type": "Organization",
        "name": "GolfRaw",
        "url": "https://www.golfraw.com"
      }
    },
    {
      "@type": "FAQPage",
      "@id": "https://www.golfraw.com/what-beginners-actually-search#faq",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "How many golf clubs does a beginner need?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "The Rules of Golf (Rule 4.1b) allow a maximum of fourteen clubs. There is no minimum requirement. A beginner can start with a handful—a tee club, a mid-iron, a wedge, and a putter will play a full round perfectly well."
          }
        },
        {
          "@type": "Question",
          "name": "What should a complete beginner do first?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Hire or borrow clubs and go to a driving range. It costs a fraction of buying a set and tells you whether you enjoy the game before you spend anything meaningful."
          }
        },
        {
          "@type": "Question",
          "name": "Do I need a handicap to play golf?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "No. A handicap exists so players of different standards can compete fairly. It isn't a licence, and most public courses do not require one to book a tee time."
          }
        },
        {
          "@type": "Question",
          "name": "Are beginner golf club sets worth buying?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "They can be, but not as a first step. Buying a complete set before hitting balls means choosing shafts, lofts, and lie angles for a swing you don't have yet. Play first, buy second, and consider second-hand options."
          }
        },
        {
          "@type": "Question",
          "name": "Why is everything about golf for beginners about equipment?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Because equipment generates affiliate revenue and search volume. In US search data, equipment queries outnumber rules and handicap questions by roughly fifty-five to one."
          }
        }
      ]
    }
  ]
}
</script>"""

html = re.sub(r'<script type="application/ld\+json">.*?</script>', schema_json, html, flags=re.DOTALL)

article_content = """      <article>
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/guides">Guides</a> / <span>Data</span>
        </nav>

        <header class="article-head">
          <span class="cat">GUIDES · DATA</span>
          <h1>40,500 People a Month Search "Golf Clubs for Beginners." 1,600 Search "Golf for Beginners."</h1>
          <p class="standfirst">40,500 people a month search for beginner golf clubs. 590 ask what a handicap is. What the search data reveals about how beginners are being sold to.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>WED 05 AUG 2026</b></span>
          </div>
        </header>

        <figure class="lead-img">
          <img src="/public/what-beginners-actually-search.webp" alt="40,500 People a Month Search Golf Clubs for Beginners">
        </figure>
        <figcaption>THE DATA SHOWS BEGINNERS ARE FUNNELLED STRAIGHT TO EQUIPMENT. PHOTO: RAWGOLF</figcaption>

        <div class="article-body">
<p>I got hold of a keyword dataset for the term “golf for beginners” — Google, Bing, YouTube, TikTok, Amazon, plus the prompts people type into ChatGPT and Gemini. US data, pulled in June 2026.</p>

<p>I expected it to be about swings.</p>

<p>It's about shopping. Almost entirely.</p>

<h2>The Number That Stopped Me</h2>
<p>The single biggest beginner term isn't “how to play golf.” It's “golf for beginners clubs,” at around 40,500 searches a month. On Bing, the equivalent phrasing runs to 49,500. It's also the number one beginner term on YouTube and TikTok.</p>

<p>The plain term — “golf for beginners,” the one you'd type if you had literally never played and wanted to know where to start — gets about 1,600.</p>

<p>Roughly twenty-five to one.</p>

<p>Now, the honest caveats: this is one tool's estimate on one day, and “clubs” is a broad commercial term that hoovers up a lot of intent. It isn't a precise measurement of anything. But the shape is unmistakable, and it repeats across every platform in the file.</p>

<p>Meanwhile: “rules of golf for beginners” gets 590 a month. “What is golf handicap for beginners” gets 590.</p>

<p>Group the equipment terms together and they outweigh those two by something like fifty-five to one.</p>

<p>Think about which of those things actually stops a person playing golf.</p>

<h2>What Beginners Ask the AI</h2>
<p>This is the part I found genuinely strange.</p>

<p>The dataset includes the actual prompts people put into ChatGPT and Gemini, classified by intent. Small sample — thirteen and twelve prompts, so treat it as a hint rather than proof.</p>

<p>Of the thirteen ChatGPT prompts, eight were classified commercial and three navigational. One was informational, and that one was how to choose the right golf balls — which is still shopping.</p>

<p>The prompts themselves: best beginner clubs under $500. Top-rated simulators for practising at home. Affordable golf shoes. Training aids. Rangefinders. Beginner bags with good storage. Sets that include clubs and accessories.</p>

<p>Gemini's list is a bit softer, and it contains the single best question in the entire file: <em>how much do beginner golf lessons typically cost</em>.</p>

<p>That's someone actually trying to get started. It's one prompt out of twenty-five.</p>

<p>Nobody in either sample asked how not to be terrified on the first tee. Nobody asked what happens if you're slow. Nobody asked whether they're allowed to play a course at all, which — having talked to people who've never played — is the question sitting underneath most of the others.</p>

<h2>Why This Is the Wrong Way Round</h2>
<p>You can play golf with a handful of clubs.</p>

<p>The <a href="https://www.randa.org/en/rog/the-rules-of-golf/rule-4" target="_blank" rel="noopener noreferrer">Rules of Golf (Rule 4.1b)</a> cap you at fourteen. There's no minimum. You could legally play a round with one club, and plenty of people learn faster that way because they stop thinking about which one to pull out.</p>

<p>So the first decision every beginner is being funnelled toward — which set do I buy — is a decision you don't need to make to start, can't make well before you've played, and will probably get wrong if you make it now. You don't know your swing speed. You don't know if you'll like it. You don't know whether you'll actually play twice a year or twice a week.</p>

<p>And here's the thing that irritates me: the industry knows all this. The search results for those 40,500 monthly searches are wall-to-wall affiliate round-ups. Somebody is being paid every time a person who has never hit a golf ball buys a full set.</p>

<h2>The Order That Actually Works</h2>
<p>If someone asked me how to start, in the order I'd genuinely do it:</p>

<ol>
  <li><strong>Go to a driving range with borrowed or hired clubs.</strong> Ranges hire them. Cost of a bucket and a session is less than a single mid-range iron. Find out whether you enjoy hitting a golf ball before you buy fourteen ways to do it.</li>
  <li><strong>Take one lesson, early.</strong> Not six. One. A decent coach will fix your grip and your setup in half an hour, and those two things determine more about your ball flight than any club you could buy. “How much do beginner lessons cost” was the best question in the whole dataset and hardly anyone's asking it.</li>
  <li><strong>Learn the two things that stop people playing: pace and etiquette.</strong> Not the full rulebook. Just: keep up with the group ahead, don't stand where someone's looking, rake the bunker, shout if it's heading at anyone. That's about ninety per cent of what a course actually cares about. Nobody minds a high score. Everybody minds waiting.</li>
  <li><strong>Play a short course or a par-3.</strong> Nine holes. Less walking, less searching, less time, less money, far less intimidating.</li>
  <li><strong>Then buy clubs.</strong> By this point you'll know if you're left or right dominant in the swing, whether you generate speed, whether you're going to play enough to justify it. And you'll buy second-hand, which is what most experienced golfers quietly recommend anyway.</li>
</ol>

<p>Notice that four of those five steps cost almost nothing, and the one big purchase comes last.</p>

<h2>What About the Handicap Question?</h2>
<p>590 people a month are asking what a golf handicap is, and it's worth answering plainly because the mystique around it is doing damage.</p>

<p>A handicap is just a number that lets you compete fairly against someone better than you. That's it. It's not a badge of legitimacy, you don't need one to play, and no beginner needs one to book a tee time at the vast majority of courses.</p>

<p>The reason it feels like a barrier is that certain clubs have historically used it as one. That's a policy choice by those clubs, not a rule of the game.</p>

<div class="faq-section">
  <h2>Frequently Asked Questions</h2>
  
  <h3>How many golf clubs does a beginner need?</h3>
  <p>The Rules of Golf allow a maximum of fourteen. There is no minimum. A beginner can start with a handful — something to hit off the tee, a mid-iron, a wedge and a putter will play a full round perfectly well.</p>

  <h3>What should a complete beginner do first?</h3>
  <p>Hire or borrow clubs and go to a driving range. It costs a fraction of buying a set and it tells you whether you enjoy the game before you spend anything meaningful.</p>

  <h3>Do I need a handicap to play golf?</h3>
  <p>No. A handicap exists so players of different standards can compete fairly. It isn't a licence, and most courses don't require one to book a round.</p>

  <h3>Are beginner golf club sets worth buying?</h3>
  <p>They can be, but not as a first step. Buying a set before you've hit balls means choosing shafts, lofts and lie angles for a swing you don't have yet. Play first, buy second, and look at second-hand.</p>

  <h3>Why is everything about golf for beginners about equipment?</h3>
  <p>Because that's what gets searched and that's what earns commission. In this dataset, equipment terms outnumbered “rules of golf for beginners” and “what is a golf handicap” by roughly fifty-five to one.</p>
</div>

<h2>The Raw Take</h2>
<p>There is a version of golf that wants your money before it wants your company.</p>

<p>It's the version where the first question is what's in your bag, where the answer to “I'd like to try golf” is a $700 starter set, and where a person who has never swung a club is reading a review of rangefinders.</p>

<p>Forty thousand people a month are being walked down that path. Five hundred and ninety are asking what a handicap is.</p>

<p>Borrow some clubs. Hit some balls. Have one lesson. Play nine holes on a short course with a mate who won't mind that you're rubbish, because everyone was rubbish, and the ones who tell you otherwise are lying.</p>

<p>Buy the clubs in the spring, when you know you want them.</p>

          <nav class="tag-row" aria-label="Article tags">
            <a href="#">Beginners</a>
            <a href="#">Golf</a>
            <a href="#">Data</a>
          </nav>
        </div>
      </article>"""

html = re.sub(r'<article>.*?</article>', article_content, html, flags=re.DOTALL)

html = finalize_html(
    html,
    'news-2026-what-beginners-actually-search.html',
    force=True,
)

with open('/Users/adnan/Desktop/golf/news-2026-what-beginners-actually-search.html', 'w') as f:
    f.write(html)
