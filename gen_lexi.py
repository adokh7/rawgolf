import re
from scripts.fix_template_metadata import finalize_html

with open("article-template.html", "r") as f:
    template = f.read()

# Replace title
template = re.sub(
    r'<title>.*?</title>', 
    '<title>Lexi Thompson Is Expecting a Daughter in February | GolfRaw</title>', 
    template
)

# Replace meta description
template = re.sub(
    r'<meta name="description" content="[^"]*">', 
    '<meta name="description" content="Lexi Thompson and Max Provost are expecting a baby girl in February 2027. Why the coverage of pregnancy in women\'s golf has changed — and what still hasn\'t.">', 
    template
)

# Make sure robots is exactly correct
template = re.sub(
    r'<meta name="robots" content="[^"]*">', 
    '<meta name="robots" content="index, follow, max-image-preview:large">', 
    template
)

# Open Graph tags
template = re.sub(
    r'<meta property="og:title" content="[^"]*">', 
    '<meta property="og:title" content="Lexi Thompson Is Expecting a Daughter in February | GolfRaw">', 
    template
)
template = re.sub(
    r'<meta property="og:description" content="[^"]*">', 
    '<meta property="og:description" content="Lexi Thompson and Max Provost are expecting a baby girl in February 2027. Why the coverage of pregnancy in women\'s golf has changed — and what still hasn\'t.">', 
    template
)
template = re.sub(
    r'<meta property="og:url" content="[^"]*">', 
    '<meta property="og:url" content="https://www.golfraw.com/news-2026-lexi-thompson-pregnant-baby-daughter-lpga">', 
    template
)
template = re.sub(
    r'<link rel="canonical" href="[^"]*">', 
    '<link rel="canonical" href="https://www.golfraw.com/news-2026-lexi-thompson-pregnant-baby-daughter-lpga">', 
    template
)
template = re.sub(
    r'<meta property="og:image" content="[^"]*">', 
    '<meta property="og:image" content="https://www.golfraw.com/public/lexi-thompson-pregnant-baby-daughter-2026.webp">', 
    template
)
template = re.sub(
    r'<meta name="twitter:title" content="[^"]*">', 
    '<meta name="twitter:title" content="Lexi Thompson Is Expecting a Daughter in February | GolfRaw">', 
    template
)
template = re.sub(
    r'<meta name="twitter:description" content="[^"]*">', 
    '<meta name="twitter:description" content="Lexi Thompson and Max Provost are expecting a baby girl in February 2027. Why the coverage of pregnancy in women\'s golf has changed — and what still hasn\'t.">', 
    template
)
template = re.sub(
    r'<meta name="twitter:image" content="[^"]*">', 
    '<meta name="twitter:image" content="https://www.golfraw.com/public/lexi-thompson-pregnant-baby-daughter-2026.webp">', 
    template
)

# Generate new article content
article_content = """
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/#pga-tour">LPGA Tour</a> / <span>News</span>
        </nav>

        <header class="article-head">
          <span class="cat">LPGA Tour · News</span>
          <h1>Lexi Thompson Is Expecting a Daughter. She's the Fourth Name in Two Years.</h1>
          <p class="standfirst">Lexi Thompson announced that she and her husband Max Provost are expecting a baby girl in February 2027. Following similar announcements from Madelene Sagström, Georgia Hall, and Jessica Korda, Thompson represents the fourth major name in women's golf to announce a pregnancy within two years—highlighting how maternity coverage in the sport has shifted from career speculation to straightforward celebration.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>AUG 11 2026</b></span>
          </div>
        </header>
        
        <figure class="lead-img" style="border:none;">
          <img src="/public/lexi-thompson-pregnant-baby-daughter-2026.webp" alt="Lexi Thompson Pregnant Baby Daughter Announcement 2026" />
        </figure>
        <figcaption>PHOTO: GETTY IMAGES / RAWGOLF</figcaption>

        <div class="article-body">
          <div class="meta-callout" style="border-left: 4px solid #10b981; padding-left: 12px; margin: 16px 0;">
            <strong>LPGA News:</strong> August 11, 2026 | Family Announcement & Tour Maternity Shift
          </div>

          <h2>Four Prominent Names in One Competitive Cycle</h2>
          <p>The announcement underscores a broader trend across women's professional golf. Madelene Sagström is missing the <a href="/news-2026-solheim-cup-dewi-weber-dutch-eligibility-let">Solheim Cup</a> expecting her first child in September, Georgia Hall returned to competition in May following childbirth in February, and Jessica Korda is expecting her second child. Fifteen years ago, such announcements were frequently framed as sudden career conclusions; today, they are met with support and protected tour status.</p>

          <h2>A Distinct Transition Following 2024 Step-Back</h2>
          <p>Unlike players stepping away during peak full-time schedules, Thompson transitioned to a selective schedule after 2024, citing mental health and personal wellbeing. Having played four to five events in 2026—highlighted by a T12 finish at the Chevron Championship—her pregnancy reflects a planned life transition rather than an abrupt competitive interruption.</p>

          <p>Questions remain regarding her commitment to the inaugural Women's TGL roster, but any return parameters to the LPGA Tour will be dictated by her personal timetable rather than tour pressure.</p>

          <h2>Evolving LPGA Maternity Provisions</h2>
          <p>The respectful shift in media coverage stems largely from updated LPGA maternity policies, which now offer robust status protection for returning mothers. While female athletes still face significant physical recovery and competitive rhythm adjustments post-partum, modern tour rules ensure returning players retain their status and tournament playing opportunities.</p>

          <div class="faq-section" style="background:#F3F4F0; padding:20px; border:2px solid var(--ink); margin: 34px 0;">
            <h2>Frequently Asked Questions</h2>

            <h3>When is Lexi Thompson's baby due?</h3>
            <p>Lexi Thompson and her husband Max Provost are expecting a baby girl in February 2027.</p>

            <h3>Is Lexi Thompson retired from golf?</h3>
            <p>No. She stepped back from full-time tournament play after the 2024 season and continues to play a selective schedule of events.</p>

            <h3>How many LPGA Tour titles has Lexi Thompson won?</h3>
            <p>Thompson has won 11 official LPGA Tour titles, including the 2014 Kraft Nabisco Championship at age 19.</p>

            <h3>How has the LPGA maternity policy changed?</h3>
            <p>The LPGA updated its maternity provisions to preserve tournament entry status and exemptions for players taking maternity leave.</p>
          </div>

          <h2>The Raw Take</h2>
          <p>Stepping back from full-time competition at age 29 after 13 years under the professional spotlight was a brave decision. Thompson prioritized personal fulfillment over endless tour grind, providing a quiet reminder that success outside the ropes matters far more than career length.</p>

          <nav class="tag-row" aria-label="Article tags">
            <a href="#">LPGA Tour</a>
            <a href="#">Lexi Thompson</a>
            <a href="#">Maternity</a>
          </nav>
        </div>
"""

# Replace the `<article>` content
template = re.sub(
    r'<article>.*?</article>', 
    '<article>\n' + article_content + '\n      </article>', 
    template,
    flags=re.DOTALL
)

template = finalize_html(
    template,
    "news-2026-lexi-thompson-pregnant-baby-daughter-lpga.html",
    force=True,
)

with open("news-2026-lexi-thompson-pregnant-baby-daughter-lpga.html", "w") as f:
    f.write(template)

print("Created news-2026-lexi-thompson-pregnant-baby-daughter-lpga.html")
