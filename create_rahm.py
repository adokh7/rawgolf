import re

with open('article-template.html', 'r') as f:
    html = f.read()

# 1. Update basic meta tags (Title, canonical, description, image)
html = re.sub(r'<title>.*?</title>', "<title>Jon Rahm's LIV Money: What He's Owed and Who Gets Paid | GOLFRAW</title>", html)
html = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="Three outlets give three different figures for what he\'s owed. The bigger question is where a player ranks when the bankruptcy queue forms.">', html)
html = re.sub(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="https://www.golfraw.com/news-2026-jon-rahm-liv-money-owed">', html)

# Open Graph
html = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="Jon Rahm\'s LIV Money: What He\'s Owed and Who Gets Paid | GOLFRAW">', html)
html = re.sub(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="Three outlets give three different figures for what he\'s owed. The bigger question is where a player ranks when the bankruptcy queue forms.">', html)
html = re.sub(r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="https://www.golfraw.com/news-2026-jon-rahm-liv-money-owed">', html)
html = re.sub(r'<meta property="og:image" content="[^"]*">', '<meta property="og:image" content="https://www.golfraw.com/news-2026-jon-rahm-liv-money-owed.webp">', html)
html = re.sub(r'<meta property="og:image:alt" content="[^"]*">', '<meta property="og:image:alt" content="Jon Rahm LIV Golf unpaid contract money and creditor ranking 2026 season">', html)

# Twitter
html = re.sub(r'<meta name="twitter:title" content="[^"]*">', '<meta name="twitter:title" content="Jon Rahm\'s LIV Money: What He\'s Owed and Who Gets Paid | GOLFRAW">', html)
html = re.sub(r'<meta name="twitter:description" content="[^"]*">', '<meta name="twitter:description" content="Three outlets give three different figures for what he\'s owed. The bigger question is where a player ranks when the bankruptcy queue forms.">', html)
html = re.sub(r'<meta name="twitter:image" content="[^"]*">', '<meta name="twitter:image" content="https://www.golfraw.com/news-2026-jon-rahm-liv-money-owed.webp">', html)
html = re.sub(r'<meta name="twitter:image:alt" content="[^"]*">', '<meta name="twitter:image:alt" content="Jon Rahm LIV Golf unpaid contract money and creditor ranking 2026 season">', html)

# Tags
tags = ["LIV GOLF", "MONEY", "NEWS"]
tag_html = "\n".join([f'  <meta property="article:tag" content="{tag}">' for tag in tags])
# Remove existing article tags
html = re.sub(r'<meta property="article:tag" content="[^"]*">\n?', '', html)
html = html.replace('</head>', f'{tag_html}\n</head>')

# Header
new_header = """<header class="article-header">
      <div class="cats">
        <a href="/liv-golf" class="cat">LIV GOLF</a>
        <span class="cat">MONEY</span>
        <span class="cat">NEWS</span>
      </div>
      <h1>Jon Rahm's LIV Money: What He's Owed and Who Gets Paid</h1>
      <p class="subdeck">Three outlets give three different figures for what he's owed. The bigger question is where a player ranks when the bankruptcy queue forms.</p>
      <div class="meta">
        <div class="auth">
          <div class="av"></div>
          <div>
            <b>GOLFRAW Editorial</b>
            <span>Independent coverage</span>
          </div>
        </div>
        <div class="date">
          <time datetime="2026-09-01">01 September 2026</time>
          <span>4 MIN READ</span>
        </div>
      </div>
      <figure class="hero-fig">
        <img src="/news-2026-jon-rahm-liv-money-owed.webp" width="1200" height="675" alt="Jon Rahm LIV Golf unpaid contract money and creditor ranking 2026 season" fetchpriority="high">
        <figcaption>Jon Rahm LIV Golf unpaid contract money and creditor ranking 2026 season — GOLFRAW</figcaption>
      </figure>
    </header>"""

html = re.sub(r'<header class="article-header">.*?</header>', new_header, html, flags=re.DOTALL)

# Body
new_body = """<div class="article-body">
          <p class="lead">A software company sued LIV Golf over $992,870.75 in unpaid invoices. That's the number that tells you more about this league's finances than any nine-figure contract does...</p>
          
          <h2>Nobody agrees what Rahm is owed</h2>
          <p>Since the news broke of unpaid invoices, the discussion inevitably turned to the massive player contracts—chief among them Jon Rahm's. Reports on the exact structure of his deal vary wildly, with three outlets giving three different figures for the balance of his guarantee.</p>
          
          <h2>He's already been paid a great deal</h2>
          <p>Rahm received a substantial upfront payment upon signing. But if LIV Golf faces a financial restructuring or a sudden halt in funding, the remaining unearned portions of that contract become a massive question mark.</p>
          
          <h2>Why a back-loaded contract is the worst kind to hold now</h2>
          <p>In standard corporate insolvency, unearned future compensation on a multi-year deal is incredibly vulnerable. A back-loaded contract—where the largest payouts are deferred to later years—leaves the athlete exposed if the league's cash flow stops.</p>

          <h2>Where the players actually rank if LIV files</h2>
          <p>If a bankruptcy queue forms, players are considered unsecured creditors. This means their massive contracts sit behind secured debts, legal settlements, and court administrative fees. They don't jump to the front of the line just because they hit golf balls.</p>

          <h2>The vendors are the part that matters</h2>
          <p>The vendor lawsuits are the canary in the coal mine. A league backed by a multi-hundred-billion dollar wealth fund doesn't typically slow-pay a million-dollar software invoice unless there are internal capital controls, audits, or a fundamental shift in how the money is being released.</p>

          <h2>The PIF question nobody has answered</h2>
          <p>The Saudi Public Investment Fund (PIF) bankrolls LIV, but PIF itself is not LIV Golf. If the corporate entity operating LIV Golf goes insolvent, is the PIF legally obligated to backstop the player contracts? The guarantee might not be as ironclad as the agents suggested.</p>

          <h2>Five things being said about Rahm's money that don't hold up</h2>
          <ul>
            <li><i>The PIF guarantees it all personally.</i> Sovereign wealth funds generally ring-fence their investments into corporate entities to avoid direct liability.</li>
            <li><i>Rahm can just go back to the PGA Tour.</i> He faces significant fines and suspensions that would need to be resolved first.</li>
            <li><i>The contract is in escrow.</i> There is zero evidence a half-billion dollars was placed in a third-party escrow account.</li>
            <li><i>He gets paid even if the league folds.</i> If the employer ceases to exist, collecting on an employment contract requires liquidating assets.</li>
            <li><i>This is just a temporary cash flow hiccup.</i> Unpaid operational vendors usually signal broader budgetary freezes.</li>
          </ul>

          <div class="verdict-box">
            <h3>The Raw Verdict</h3>
            <p>The exact dollar figure Jon Rahm is owed matters less than his legal standing to collect it. If LIV Golf undergoes a financial restructuring, the biggest contracts in golf history will be tested in bankruptcy court, where being a star player means nothing, and being an unsecured creditor means everything.</p>
          </div>

          <section class="sources" aria-labelledby="faq-label">
            <h2 id="faq-label" style="font-size: 1.25rem; font-family: 'IBM Plex Mono', monospace; text-transform: uppercase;">FAQ</h2>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">How much is Jon Rahm owed by LIV Golf?</h3>
              <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">Reports vary significantly on the exact remaining balance of his contract, as the initial upfront payment and structure were never publicly verified by the league.</p>
              </div>
            </div>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">How much was Rahm's LIV contract worth?</h3>
              <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">The reported figure at the time of signing was between $300 million and $500 million, though the ratio of upfront cash to equity and future payouts remains unclear.</p>
              </div>
            </div>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">Where do players rank in bankruptcy?</h3>
              <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">Players are generally considered unsecured creditors for their unearned future compensation, placing them behind secured creditors and administrative costs.</p>
              </div>
            </div>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">Why are vendors suing LIV Golf?</h3>
              <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">At least one software vendor sued over nearly $1 million in unpaid invoices, sparking concerns about the league's operational cash flow and vendor management.</p>
              </div>
            </div>
            <div itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
              <h3 itemprop="name">Does the PIF guarantee player obligations?</h3>
              <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">It depends on the exact corporate structure of the contracts, but typically sovereign wealth funds use corporate entities (like LIV Golf) to shield the parent fund from direct liability.</p>
              </div>
            </div>
          </section>

          <section class="sources" aria-labelledby="sources-label">
            <p class="section-label" id="sources-label">Sources</p>
            <ol>
              <li><a href="/news-2026-liv-golf-settlement-offers-bankruptcy">LIV Golf Vendor Settlements</a>. Background on the recent software company lawsuits.</li>
              <li><a href="/news-2026-liv-golf-bankruptcy-chapter-11-explained">LIV Golf Chapter 11 Risks</a>. Explaining unsecured creditors in sports bankruptcies.</li>
            </ol>
          </section>

          <div class="provenance">
            <p><strong>Article history.</strong> Published <time datetime="2026-09-01T21:30:00+02:00">01 September 2026</time>.</p>
            <p><strong>Corrections.</strong> None at publication. <a href="/corrections">Corrections policy</a>.</p>
            <p><strong>Last updated.</strong> <time datetime="2026-09-01T21:30:00+02:00">01 September 2026</time>.</p>
          </div>

          <aside class="related" aria-label="Related GolfRaw reporting">
            <p class="section-label" style="color:#b8d2c5">Keep reading</p>
            <ul>
              <li><a href="/news-2026-liv-golf-settlement-offers-bankruptcy">LIV Golf Vendor Lawsuits</a></li>
              <li><a href="/news-2026-liv-golf-bankruptcy-chapter-11-explained">What Chapter 11 Means for LIV</a></li>
            </ul>
          </aside>
        </div>"""

html = re.sub(r'<div class="article-body">.*?</article>', new_body + '\n      </article>', html, flags=re.DOTALL)

with open('news-2026-jon-rahm-liv-money-owed.html', 'w') as f:
    f.write(html)
