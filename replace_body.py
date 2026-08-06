import sys
with open('news-2026-memphis-championship-series-fedexcup.html', 'r') as f:
    content = f.read()

start_marker = '<nav class="crumbs" aria-label="Breadcrumb">'
end_marker = '          </nav>\n        </div>'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker) + len(end_marker)

new_body = """<nav class="crumbs" aria-label="Breadcrumb">
          <a href="/">RawGolf</a> / <a href="/pga-tour">PGA Tour</a> / <span>FedExCup</span>
        </nav>

        <header class="article-head">
          <span class="cat">PGA TOUR · FEDEXCUP</span>
          <h1>The Bigger Story Isn't Memphis. It's Whether the FedExCup Survives.</h1>
          <p class="standfirst">The PGA Tour confirmed on Wednesday that the FedEx St. Jude Championship won't be part of the top-tier Championship Series when the schedule is rebuilt in 2028. Every headline is about Memphis losing its playoff event, which is true. But read the Tour's own timeline and there's a much larger question underneath it.</p>
          <div class="byline">
            <span>BY <b><a href="#">GOLFRAW EDITORIAL</a></b></span>
            <span>PUBLISHED <b>AUG 06 2026</b></span>
          </div>
        </header>

        <figure class="lead-img">
          <img src="/public/memphis-championship-series-fedexcup.webp" alt="TPC Southwind Memphis PGA Tour">
        </figure>

        <div class="article-body">
<div class="meta-callout" style="border-left: 4px solid #10b981; padding-left: 12px; margin: 16px 0;">
  <strong>PGA Tour Restructure:</strong> August 6, 2026 | Analysis on Championship Series & FedEx Sponsorship
</div>

<h2>The Contract Nobody's Talking About</h2>
<p>FedEx has sponsored the PGA Tour since 1986. Forty years.</p>

<p>That sponsorship isn't just the tournament in Memphis. It covers the season-long points race and the entire postseason — the FedExCup, in other words, which is the structure professional golf has organised itself around since 2007.</p>

<p>And the deal expires at the end of 2027.</p>

<p>The new two-tier model starts in 2028. So the Tour has just told its 40-year partner that its flagship tournament won't be in the top tier, exactly four months before the contract that carries the Tour's own championship name runs out.</p>

<p>ESPN put it plainly in their reporting: the decision raises questions about the future of the FedEx Cup, its name, and its structure.</p>

<p>I want to be careful here. Nobody has said the FedExCup is ending. The Tour's statement doesn't touch it, and there's a version of the future where FedEx renews and everything keeps its name. But you don't need inside information to see that a sponsor whose event just got demoted, whose contract is up, is a sponsor with a decision to make.</p>

<h2>What Memphis Actually Loses</h2>
<p>The Championship Series will run 23 to 24 events for the highest-rated players. Below it sits a Challenger Series of about 20 tournaments, essentially a feeder tier.</p>

<p>Memphis is still under consideration for the Challenger Series. Not confirmed. Under consideration.</p>

<p>The tournament will be played next week and again in 2027. After that, not in its current role. The Tour's statement is warm — grateful to FedEx, praise for St. Jude, TPC Southwind described as an important asset, and a line about believing Memphis is well positioned to remain part of the Tour. FedEx's own statement says it's disappointed but encouraged by plans to find other ways to bring golf to the city.</p>

<p>Kevin Kane, who runs Memphis Tourism, put it more honestly than either: the city will have golf in 2028, and nobody knows yet what it'll look like.</p>

<h2>The Pattern in How Memphis Got Here</h2>
<p>This is the part I find genuinely striking, and it's sitting in the published history where anyone could have picked it up.</p>

<p>Memphis was given World Golf Championship status in 2019 because the Tour lost its sponsorship at Firestone Country Club.</p>

<p>It became a playoff event in 2022 because another sponsor didn't renew.</p>

<p>Twice promoted, both times because somebody else's money fell over. Not because of ratings, not because the golf demanded it, not because Memphis outcompeted anyone. It was where the Tour put a tournament when a slot came free.</p>

<p>And now, with its own sponsorship approaching expiry, it's being moved down by the same machinery that moved it up. A tournament whose status was always contingent has discovered that it was always contingent.</p>

<h2>Three Stories, One Restructure</h2>
<p>I've written about two other pieces of this in the last fortnight and they only make sense together.</p>

<p><strong>Detroit:</strong> Rocket Companies walked away after thirteen years. Per the AP, it wasn't willing to keep paying around $15 million a year to sit in the second tier, or double that to buy into the elite one. A sponsor was shown the new price list and declined both numbers.</p>

<p><strong>Memphis:</strong> Sixty-eight years of tournament golf, dropped to the second tier, with its title sponsor's contract expiring on the eve of the change.</p>

<p><strong>Greensboro, right now:</strong> The Wyndham Championship is being played this week for one reason: to decide which 70 players advance to the FedEx St. Jude Championship.</p>

<p>This Sunday, seventy players will earn their way to Memphis. In two seasons Memphis won't be where they go, and it isn't clear the thing they're qualifying for will still be called what it's called.</p>

<p>That's not a conspiracy, it's just a restructure. But it's a restructure that has now taken a tournament out of Detroit, taken the top tier away from Memphis, and put a question mark over the name of the trophy — all in about eight weeks.</p>

<h2>Why "Tiers" Should Bother You More Than It Does</h2>
<p>Here's what a two-tier tour actually means, stripped of the corporate language: about 24 events with the best players and the most money. About 20 events without them.</p>

<p>If your local tournament is in the second group, the players you've heard of aren't coming. The television deal is worth less. The sponsorship costs less and delivers less. Attendance falls, which makes the case for promotion harder, which keeps you in the second tier.</p>

<p>Golf has spent four years arguing about whether a breakaway league fragmenting the sport was good or bad. The PGA Tour is now, quite deliberately, fragmenting itself — and doing it through a series of announcements released piecemeal over more than a week, which is not how you communicate good news.</p>

<p>Sixty-eight years in Memphis. Thirteen in Detroit. Both decided by which side of a line a spreadsheet put them on.</p>

<div class="faq-section">
  <h2>Frequently Asked Questions</h2>

  <h3>Is the FedEx St. Jude Championship being cancelled?</h3>
  <p>No. It will be played in 2026 and 2027 as normal. From 2028 it won't be part of the PGA Tour's top-tier Championship Series, and it's currently under consideration for the second-tier Challenger Series.</p>

  <h3>What is the PGA Tour Championship Series?</h3>
  <p>A restructure starting in 2028, announced two months ago. The Championship Series will feature 23 to 24 events with the highest-rated players. A Challenger Series of roughly 20 tournaments will sit below it as a feeder tier.</p>

  <h3>Is the FedExCup ending?</h3>
  <p>Nobody has stated it is ending. However, FedEx's sponsorship — which covers the Memphis tournament, the season-long points race, and the postseason — expires at the end of 2027, the year before the restructure begins. ESPN reported that the Memphis decision raises questions about the FedEx Cup's name and structure moving forward.</p>

  <h3>How long has Memphis hosted PGA Tour golf?</h3>
  <p>Since 1958. It gained World Golf Championship status in 2019 after the Tour lost its sponsorship at Firestone, and became a playoff event in 2022 when another sponsor didn't renew.</p>

  <h3>Which other tournaments have been affected?</h3>
  <p>The Rocket Mortgage Classic in Detroit ended after 2026, with Rocket declining to renew. Per the AP, the sponsor was not prepared to pay around $15 million a year for second-tier status or roughly double that for the top tier.</p>
</div>

<h2>The Raw Take</h2>
<p>There's a way of talking about this that makes it sound like housekeeping. Tiers. Competitive models. Well-positioned to remain part of the Tour.</p>

<p>What it actually means is that a tournament that's been played in one American city since 1958 is being told it isn't good enough for the top division, and that the news arrived as one item in a fortnight of announcements dribbled out a few at a time.</p>

<p>Memphis raises money for a children's hospital. That fact is warmly placed in every official statement. It doesn't appear to have counted for much when the spreadsheet math was done. I don't think the Tour is villainous here. Sponsorship money is finite, the calendar is bloated, and something had to give. But watch what's actually being sorted: not which courses test players best, not where the golf is good, not which tournaments fans care about. Which ones can afford the new rate card.</p>

<p>Detroit couldn't. Memphis apparently can't either. And the trophy everyone's playing for this week might not have a name in two years.</p>

          <nav class="tag-row" aria-label="Article tags">
            <a href="search">FedEx St Jude Championship 2028</a>
            <a href="search">PGA Tour Championship Series</a>
            <a href="search">Memphis PGA Tour</a>
            <a href="search">FedExCup Ending</a>
            <a href="search">Challenger Series</a>
            <a href="search">TPC Southwind</a>
          </nav>
        </div>"""

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + new_body + content[end_idx:]
    with open('news-2026-memphis-championship-series-fedexcup.html', 'w') as f:
        f.write(new_content)
    print("Successfully replaced body.")
else:
    print("Could not find markers.")
    sys.exit(1)
