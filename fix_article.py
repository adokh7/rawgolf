import re

with open("news-2026-solheim-cup-big-names-missing.html", "r", encoding="utf-8") as f:
    template = f.read()

# 1. Extract head start
head_start = template[:template.find("<!-- ============ PRIMARY SEO ============ -->")]

# 2. SEO block
seo_block = """<!-- ============ PRIMARY SEO ============ -->
  <title>LIV Says It's Saved. It Won't Say By Whom. | GolfRaw</title>
  <meta name="description" content="LIV Golf says it has a signed lead investor and players will be majority owners. It won't name the investor or the amount. What was actually announced.">
  <link rel="canonical" href="https://www.golfraw.com/news-2026-liv-golf-secures-lead-investor">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="author" content="GOLFRAW Editorial">

  <!-- ============ OPEN GRAPH ============ -->
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="GolfRaw" />
  <meta property="og:title" content="LIV Says It's Saved. It Won't Say By Whom. | GolfRaw" />
  <meta property="og:description" content="LIV Golf says it has a signed lead investor and players will be majority owners. It won't name the investor or the amount. What was actually announced." />
  <meta property="og:url" content="https://www.golfraw.com/news-2026-liv-golf-secures-lead-investor" />
  <meta property="og:image" content="https://www.golfraw.com/public/liv-golf-lead-investor.webp">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="LIV Golf Lead Investor">
  <meta property="article:published_time" content="2026-08-05T08:00:00+02:00" />
  <meta property="article:modified_time" content="2026-08-05T08:00:00+02:00">
  <meta property="article:author" content="GolfRaw Editorial" />
  <meta property="article:section" content="News">
  <meta property="article:tag" content="LIV Golf">

  <!-- ============ TWITTER CARD ============ -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="LIV Says It's Saved. It Won't Say By Whom. | GolfRaw">
  <meta name="twitter:description" content="LIV Golf says it has a signed lead investor and players will be majority owners. It won't name the investor or the amount. What was actually announced.">
  <meta name="twitter:image" content="https://www.golfraw.com/public/liv-golf-lead-investor.webp">

  <!-- ============ STRUCTURED DATA (Article) ============ -->
  <script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "headline": "LIV Golf Says It's Been Saved. It Won't Say By Whom, or For How Much.",
  "description": "LIV Golf says it has a signed lead investor and players will be majority owners. It won't name the investor or the amount. What was actually announced.",
  "image": [
    "https://www.golfraw.com/public/liv-golf-lead-investor.webp"
  ],
  "datePublished": "2026-08-05T08:00:00+02:00",
  "dateModified": "2026-08-05T08:00:00+02:00",
  "author": {
    "@type": "Organization",
    "name": "GOLFRAW Editorial",
    "url": "https://www.golfraw.com/"
  },
  "publisher": {
    "@type": "Organization",
    "name": "GOLFRAW",
    "logo": {
      "@type": "ImageObject",
      "url": "https://www.golfraw.com/public/favicon-192.webp",
      "width": 1254,
      "height": 1254
    }
  },
  "mainEntityOfPage": "https://www.golfraw.com/news-2026-liv-golf-secures-lead-investor"
}
  </script>
"""

# 3. Head end to main article start
head_end_idx = template.find('  <link rel="preconnect" href="https://fonts.googleapis.com">')
main_start_idx = template.find('<article>')

head_to_main = template[head_end_idx:main_start_idx]

# 4. New Article content
article_block = """<article>
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="news">Latest News</a> / <span>LIV Golf</span>
        </nav>

        <header class="article-head">
          <span class="cat">NEWS · LIV GOLF</span>
          <h1>LIV Golf Says It's Been Saved. It Won't Say By Whom, or For How Much.</h1>
          <p class="standfirst">Scott O'Neil stood up at Trump National Bedminster on Wednesday morning, hours before LIV Golf New York, and announced that the league has a signed lead investor. Terms are expected to be finalized in September, with players set to become majority equity holders. But crucial details—namely who the investor is and how much money was committed—remain completely unannounced.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>AUG 05 2026</b></span>
          </div>
        </header>

        <img src="/public/liv-golf-lead-investor.webp" alt="LIV Golf Lead Investor" style="width: 100%; border-radius: 4px; margin-bottom: 40px;">

        <div class="article-body">
          <h2>Take the Announcement Seriously, But Read What It Says</h2>
          <p>A term sheet signed by both parties and approved by a board is a real development. It is considerably more than "we're in talks," which is where this story sat a week ago. Something concrete happened.</p>

          <p>But it is not a closed deal, and the two facts a person would most want — the name and the number — were both withheld.</p>

          <p>Here's how quickly that becomes a problem. Bleacher Report headlined the announcement as LIV securing a "$250M investment." That figure is nowhere in O'Neil's statement. The Washington Post, CBS, Forbes, Front Office Sports, and Yahoo all reported explicitly that the sum was not disclosed. What Forbes noted was that previous reports had put O'Neil's fundraising target at $250–300 million; Front Office Sports said he'd previously talked about seeking as much as $350 million.</p>

          <p>A month-old fundraising ambition became today's confirmed investment figure in a headline within hours.</p>

          <p>If you read one thing about LIV Golf this week, make it this: nobody outside the room knows how much money is coming, and anyone publishing a hard number is quoting an old target.</p>

          <h2>What I Got Wrong and What I Got Right</h2>
          <p>I wrote a piece on Sunday arguing that almost the whole LIV financial story traced back to one man with an X account — Tom Hobbs, who runs the Flushing It accounts — plus a handful of anonymous sources, and that outlets downstream were adding nothing while dropping caveats.</p>

          <p>Two things happened since.</p>

          <p>Hobbs was right. The player-equity story was his, reported days before anyone confirmed it, and LIV has now confirmed it on the record with the CEO's name attached. I flagged it at the time as single-origin and unconfirmed, which was the correct call to make with the evidence available. It was also, as it turns out, true. That's worth saying out loud: "not yet confirmed" is not the same as "wrong," and a well-sourced independent reporter can beat every newsroom in the sport.</p>

          <p>And the caveat-stripping happened again, in the same news cycle. A number that belonged to a sentence about what someone was seeking got promoted into a headline about what they'd got.</p>

          <h2>The Bit That Actually Tells You Something</h2>
          <p>Front Office Sports noticed something nobody else built on. O'Neil spent part of Wednesday's pro-am playing golf with David Orlofsky of AlixPartners, LIV's financial adviser; Bradley Robins of Ducera Partners, its investment banker; and Michael Chaisanguanthum, a managing director of asset management at UBS.</p>

          <p>I'm not going to tell you what that means, because I don't know and neither does anyone else writing about it. AlixPartners is a restructuring firm. Ducera is running the raise. A UBS asset-management executive on the same fourball on announcement day is either a coincidence or it isn't.</p>

          <p>That's a genuine detail, obtained by a reporter being physically present, which is the sort of reporting that has been in short supply in this story.</p>

          <h2>What LIV 2.0 Actually Looks Like</h2>
          <p>Underneath the announcement is the shape of the league that survives, and it's smaller:</p>

          <ul>
            <li><strong>10 events across five continents</strong>, down from 13–14 in recent seasons.</li>
            <li><strong>Purses of around $10 million</strong>, down from $20 million in 2026.</li>
          </ul>

          <p>That is a cut of about half in prize money. No 2027 schedule has been finalised.</p>

          <p>O'Neil also said there's interest from more than a dozen additional parties as potential minority investors, which he framed as a multi-partner model.</p>

          <h2>What Still Hasn't Been Answered</h2>
          <p><strong>Who owns what:</strong> "Majority equity holders" is a phrase, not a cap table. Which players? What percentage? On what terms? And critically — what happens to the money LIV reportedly still owes players, Jon Rahm included, in nine figures? Swapping debt for stock is a very different proposition from receiving stock on top of being paid.</p>

          <p><strong>Whether bankruptcy is off the table:</strong> Nothing on Wednesday withdrew the reporting that a filing has been under consideration to restructure debt. A company can take new investment and restructure at the same time. Those aren't opposites.</p>

          <p><strong>Whether the Michigan team championship is happening:</strong> Many people expected Wednesday's press conference to be its cancellation. It wasn't. But nothing was said confirming it either, and a team captain publicly put it at around five per cent last week. Three events remain on the published schedule; that's a schedule, not a guarantee.</p>

          <h2>What This Means If You Just Like Golf</h2>
          <p>Nothing changes this month. There's golf at Bedminster from Thursday. Whatever happens to the corporate structure, DeChambeau and the rest are teeing off.</p>

          <p>Player ownership is genuinely interesting, if it's real. Athletes owning the majority of the league they play in is unusual, and it's the one part of this that could outlast LIV itself as an idea. Whether it turns out to be ownership or a way of converting an unpayable debt into paper is the question, and we won't know until the terms are published.</p>

          <p>And smaller purses might not be the disaster it sounds. Twenty million dollars per event with no cut was always the least sporting thing about LIV. Ten million and a league the players own is, on paper, closer to an actual sports league than a very expensive exhibition.</p>

          <div class="faq-section" style="background:var(--white); border:2px solid var(--ink); padding:24px; margin:32px 0;">
            <h2 style="margin-top:0;">Frequently Asked Questions</h2>

            <h3 style="font-size:18px; margin-top:16px;">Has LIV Golf been saved?</h3>
            <p>LIV Golf announced a signed, board-approved term sheet with a lead investor, targeting a September transaction. While a significant step, it is not a closed deal, and neither the investor's name nor the investment amount was disclosed.</p>

            <h3 style="font-size:18px; margin-top:16px;">Who is investing in LIV Golf?</h3>
            <p>The identity of the lead investor has not been disclosed. CEO Scott O'Neil declined to name the party, adding that over a dozen other groups have expressed interest as potential minority partners.</p>

            <h3 style="font-size:18px; margin-top:16px;">How much money has LIV Golf secured?</h3>
            <p>The sum has not been disclosed. Headline figures referencing $250 million or $350 million refer to previously reported fundraising targets rather than confirmed investment commitments.</p>

            <h3 style="font-size:18px; margin-top:16px;">Will LIV Golf players own the league?</h3>
            <p>LIV stated that players will become majority equity holders. However, specific details regarding equity distribution, player eligibility, and how this relates to existing contractual debts remain unannounced.</p>

            <h3 style="font-size:18px; margin-top:16px;">What will LIV Golf look like in 2027?</h3>
            <p>LIV 2.0 is expected to feature 10 events across five continents with purses reduced to approximately $10 million per tournament, down from $20 million in 2026.</p>

            <h3 style="font-size:18px; margin-top:16px;">Is LIV Golf still facing bankruptcy?</h3>
            <p>Wednesday's announcement did not refute earlier reports regarding potential debt restructuring or filing options. Securing new investment and executing debt restructuring can occur simultaneously.</p>
          </div>

          <h2>The Raw Take</h2>
          <p>The most honest sentence anyone produced about all this came from Front Office Sports, whose headline noted that LIV had signed a lead investor but big questions remain.</p>

          <p>That's the story. A real step, taken by a real company, with the two numbers that would let you judge it left out. Golf will find out in September whether any of this was real. Until then, the only thing anybody actually knows is that somebody signed something.</p>

          <div class="tag-row">
            <a href="search">LIV Golf</a>
            <a href="search">Scott O'Neil</a>
            <a href="search">GOLFRAW</a>
          </div>
        </div>
      </article>"""

# 5. Get the rest of the template
rest_idx = template.find('<!-- ============ SIDEBAR ============ -->')
rest = template[rest_idx:]

final_html = head_start + seo_block + head_to_main + article_block + "\n\n      " + rest

with open("news-2026-liv-golf-secures-lead-investor.html", "w", encoding="utf-8") as f:
    f.write(final_html)
