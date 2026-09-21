#!/usr/bin/env python3
"""Generate tools-club-distance-calculator.html (The Distance Check).

Lifts the shared tool shell from tools-bag-audit.html like the other generated
tools. The distance model is /lib/distance/club-distance.js; this page only
renders it. Re-runnable: rewrites the file wholesale, so edit this builder,
never the HTML. After a rebuild run, in order: this builder, wire_locker.py,
wire_tool_events.py, apply_theme.py (see scripts/README.md).

    PYTHONPATH=.:scripts python3 scripts/build_club_distance.py
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHELL = os.path.join(ROOT, 'tools-bag-audit.html')
OUT = os.path.join(ROOT, 'tools-club-distance-calculator.html')

SITE = 'https://www.golfraw.com'
SLUG = 'tools-club-distance-calculator'
TITLE = 'Golf Club Distance Calculator: Yards or Metres | GolfRaw'
DESC = ('Enter your driver carry, 7-iron carry or swing speed, or just your handicap, and see a '
        'realistic carry range for every club in yards or metres.')
OG_IMAGE = SITE + '/public/raw-golf-practice.webp'
MODEL_VER = '2'   # bump when lib/distance/club-distance.js changes (immutable .js cache)
UNITS_VER = '1'   # bump when lib/distance/units.js changes

from tool_shell import shell_parts as _shell_parts
from scripts.schema_normalizer import normalize_tool_page


def shell_parts():
    return _shell_parts(SHELL)


PREMIUM_LINK = '  <link rel="stylesheet" href="/public/tool-premium.css?v=4">\n'


def rewrite_meta(s):
    s = re.sub(r'<title>.*?</title>', '<title>%s</title>' % TITLE.replace('&', '&amp;'), s, flags=re.S)
    for pat, val in [
        (r'(<meta name="description" content=")[^"]*(")', DESC),
        (r'(<meta property="og:title" content=")[^"]*(")', TITLE.replace('&', '&amp;')),
        (r'(<meta property="og:description" content=")[^"]*(")', DESC),
        (r'(<meta property="og:image" content=")[^"]*(")', OG_IMAGE),
        (r'(<meta name="twitter:title" content=")[^"]*(")', TITLE.replace('&', '&amp;')),
        (r'(<meta name="twitter:description" content=")[^"]*(")', DESC),
        (r'(<meta name="twitter:image" content=")[^"]*(")', OG_IMAGE),
    ]:
        s = re.sub(pat, lambda m, v=val: m.group(1) + v + m.group(2), s)
    s = re.sub(r'(<link rel="canonical" href=")[^"]*(")', r'\g<1>%s/%s\g<2>' % (SITE, SLUG), s)
    s = re.sub(r'(<meta property="og:url" content=")[^"]*(")', r'\g<1>%s/%s\g<2>' % (SITE, SLUG), s)
    return s


# Replaced wholesale by schema_normalizer.normalize_tool_page (WebApplication,
# BreadcrumbList and the FAQ below), which reads the tool from tool_inventory.
JSONLD = """  <!-- ============ STRUCTURED DATA ============ -->
  <script type="application/ld+json">
{"@context": "https://schema.org", "@type": "WebApplication", "name": "The Distance Check"}
  </script>
"""

STYLE = r'''<style>
    /* ---- The Distance Check --------------------------------------------------
       Built for a phone in one hand in daylight: 44px targets, one big numeric
       field, and the result directly under the button. State is always written
       out in words, never carried by colour alone. */
    .tool-body > .wrap > .cd-out { order: 1 }
    .cd-panel .panel-in { max-width: 620px }
    .cd-seg { border: 0; margin: 0 0 18px; padding: 0; display: flex; flex-wrap: wrap; gap: 8px }
    .cd-legend { width: 100%; padding: 0; margin-bottom: 8px; font-size: 13px; font-weight: 700; color: var(--ink) }
    .cd-legend-note { font-weight: 500; color: var(--grey); margin-left: 6px }
    .cd-seg label { position: relative; flex: 1 1 calc(50% - 8px); min-width: 0 }
    .cd-units label, .cd-group label { flex: 0 1 auto }
    .cd-seg input { position: absolute; opacity: 0; width: 1px; height: 1px }
    .cd-seg span { display: flex; align-items: center; justify-content: center; min-height: 46px; padding: 10px 14px;
      border: 2px solid var(--line); border-radius: 10px; background: var(--white); font-size: 15px; font-weight: 700;
      color: var(--ink); text-align: center; cursor: pointer; line-height: 1.2 }
    .cd-seg input:checked + span { border-color: var(--ink); background: var(--ink); color: #fff }
    .cd-seg input:focus-visible + span { outline: 3px solid var(--flag); outline-offset: 2px }
    .cd-field { margin-bottom: 18px }
    .cd-field > label { display: block; font-size: 15px; font-weight: 800; margin-bottom: 8px }
    .cd-input { display: flex; align-items: stretch; max-width: 280px }
    .cd-input input { flex: 1; min-width: 0; font-size: 26px; font-weight: 800; padding: 10px 12px;
      border: 2px solid var(--ink); border-right: 0; border-radius: 10px 0 0 10px; font-variant-numeric: tabular-nums }
    .cd-input input[aria-invalid="true"] { border-color: #8f2015 }
    .cd-suffix { display: flex; align-items: center; padding: 0 14px; border: 2px solid var(--ink);
      border-radius: 0 10px 10px 0; background: var(--paper); font-weight: 800; font-size: 15px }
    .cd-field select { width: 100%; max-width: 320px; min-height: 48px; font-size: 16px; padding: 8px 10px;
      border: 2px solid var(--ink); border-radius: 10px; background: var(--white); margin-bottom: 14px }
    .cd-hint { font-size: 13.5px; color: var(--grey); line-height: 1.55; margin-top: 8px; max-width: 60ch }
    .cd-go { width: 100%; max-width: 320px; min-height: 52px; font-size: 13px }
    /* The shared styles cap tool buttons at 40px and number fields at 16px with
       rules that outrank a plain class; this tool wants a 52px button and a big,
       daylight-readable number, so scope the override tightly. */
    .cd-panel .panel-in button.cd-go { min-height: 52px !important }
    .cd-panel .cd-input input[type="number"] { font-size: 26px !important; font-weight: 800 !important;
      min-height: 52px }

    .cd-result { border: 2px solid var(--ink); border-radius: 16px; background: var(--white); padding: 20px 18px;
      margin-bottom: 24px }
    .cd-result h2 { font-size: clamp(22px, 4vw, 28px); line-height: 1.15; margin-bottom: 6px }
    .cd-result h2:focus { outline: none }
    .cd-result h3 { font-size: 17px; margin-bottom: 6px }
    .cd-echo { font-size: 16px; font-weight: 700; margin-bottom: 8px }
    .cd-quality { font-size: 14px; line-height: 1.5; padding: 10px 12px; border: 1px solid var(--line);
      border-radius: 10px; background: var(--paper); margin-bottom: 16px }
    .cd-quality[data-quality="speed"], .cd-quality[data-quality="benchmark"] { border-color: #f5c07a }
    .cd-quality[data-quality="benchmark"] { background: #fffbeb }
    .cd-table { width: 100%; max-width: 640px; border-collapse: collapse; font-variant-numeric: tabular-nums }
    .cd-key, .cd-quality { max-width: 640px }
    .cd-table th, .cd-table td { padding: 10px 6px; border-bottom: 1px solid var(--line); text-align: right;
      font-size: 16px; vertical-align: top }
    .cd-table thead th { font-size: 11px; letter-spacing: .08em; text-transform: uppercase; color: var(--grey);
      font-weight: 700; border-bottom: 2px solid var(--ink) }
    .cd-table th[scope="row"], .cd-table thead th:first-child { text-align: left }
    .cd-table th[scope="row"] { font-weight: 800 }
    /* tool-premium.css paints every table th dark with !important; club names are
       row labels here, so they stay ink on white where the grey confidence line
       keeps its contrast. The column-header row keeps the site style. */
    .cd-table tbody th { background: var(--white) !important; color: var(--ink) !important;
      text-transform: none; letter-spacing: normal; font-family: inherit; font-size: 16px }
    .cd-table td:nth-child(2) { font-weight: 800 }
    .cd-table td:nth-child(3) { color: var(--grey) }
    .cd-conf { display: block; font-size: 11.5px; font-weight: 600; color: var(--grey); margin-top: 2px }
    .cd-table tbody tr.is-anchor th[scope="row"], .cd-table tbody tr.is-anchor td { background: #eef7f1 !important }
    .cd-key { font-size: 13.5px; color: var(--grey); line-height: 1.55; margin: 12px 0 14px }
    .cd-bag { margin-bottom: 18px }
    .cd-bag summary { cursor: pointer; font-weight: 700; font-size: 14.5px; min-height: 44px; display: flex;
      align-items: center }
    .cd-clubs { display: grid; grid-template-columns: repeat(auto-fill, minmax(118px, 1fr)); gap: 4px 10px; padding-top: 6px }
    .cd-club { display: flex; align-items: center; gap: 8px; min-height: 40px; font-size: 15px }
    .cd-club input { width: 20px; height: 20px }
    .cd-tee, .cd-next { border-top: 1px solid var(--line); padding-top: 16px; margin-top: 16px }
    .cd-tee p, .cd-next p { font-size: 15px; line-height: 1.55; margin-bottom: 8px }
    .cd-next .btn { display: inline-flex; align-items: center; min-height: 48px; text-decoration: none; margin-top: 4px }
    .cd-real { font-size: 14.5px; line-height: 1.55; margin-top: 16px }
    .cd-acts { margin-top: 16px; align-items: center; gap: 12px }
    .cd-sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap }
    .cd-examples { width: 100%; border-collapse: collapse; margin: 6px 0 14px; font-variant-numeric: tabular-nums }
    .cd-examples th, .cd-examples td { border-bottom: 1px solid var(--line); padding: 8px 6px; text-align: right; font-size: 14.5px }
    .cd-examples th:first-child, .cd-examples td:first-child { text-align: left }
    .cd-sources li { font-size: 14px; line-height: 1.55; margin-bottom: 8px }
    .cd-updated { font-size: 13px; color: var(--grey); margin-top: 8px }
    @media (min-width: 700px) {
      .cd-seg label { flex: 0 1 auto }
      .cd-result { padding: 26px 26px }
    }
  </style>
'''

MAIN = r'''
  <div class="hub-hero">
    <div class="wrap">
      <div class="eyebrow">GolfRaw &middot; TOOLS</div>
      <h1>Golf Club Distance Calculator</h1>
      <p class="tool-brand">The Distance Check</p>
      <p>Give it one number you actually know: your typical driver carry, your 7-iron, or your swing speed. It
        works out what the rest of your bag should carry, as a range to plan around and a separate best-strike
        range, because the shot you remember is not the one to club off. Runs in your browser; nothing you type
        leaves it.</p>
    </div>
  </div>

  <div class="tool-body">
    <div class="wrap">

      <section class="answer-block" aria-labelledby="aeo-q">
        <div class="ab-tag">The short answer</div>
        <h2 id="aeo-q">How far should you hit each golf club?</h2>
        <p class="ab-answer">It depends on your speed, which is why one chart misleads most golfers. PGA Tour
          players carry a 7-iron about 176 yards; the average man in a USGA study of 627 recreational golfers hit
          it 149 yards in total, about 134 of that in the air.</p>
        <p class="ab-body">Start from one number you really know and scale the bag from it. This calculator uses
          TrackMan&rsquo;s 2024 tour averages for the shape of a bag and the USGA&rsquo;s 2023 launch-monitor data for
          how recreational golfers hit it, then gives each club a <b>carry range</b> instead of one
          fake-precise number.</p>
        <ul class="ab-facts"><li><b>Carry</b>, not total</li><li><b>Yards</b> or metres</li><li><b>0</b> data uploaded</li><li><b>100%</b> in your browser</li></ul>
      </section>

      <!-- ============ THE TOOL ============ -->
      <section class="panel cd-panel" aria-labelledby="cd-in-h" data-gr-inputs>
        <div class="panel-head"><span id="cd-in-h"><span class="step">01 &middot;</span> What do you know?</span></div>
        <div class="panel-in">
          <fieldset class="cd-seg">
            <legend class="cd-legend">Start from one number</legend>
            <label><input type="radio" name="cdAnchor" value="driver_carry"><span>Driver carry</span></label>
            <label><input type="radio" name="cdAnchor" value="iron_carry" checked><span>7-iron carry</span></label>
            <label><input type="radio" name="cdAnchor" value="swing_speed"><span>Swing speed</span></label>
            <label><input type="radio" name="cdAnchor" value="handicap_band"><span>Only my handicap</span></label>
          </fieldset>

          <fieldset class="cd-seg cd-units" data-gr-ignore>
            <legend class="cd-legend">Units <span class="cd-legend-note">Pick once. GolfRaw remembers it on this device.</span></legend>
            <label><input type="radio" name="cdUnit" value="yd" checked><span>Yards</span></label>
            <label><input type="radio" name="cdUnit" value="m"><span>Metres</span></label>
          </fieldset>

          <div class="err" id="cdErr" role="alert"></div>

          <div id="cdNumber" class="cd-field">
            <label for="cdValue" id="cdValueLabel">Your typical 7-iron carry (yards)</label>
            <div class="cd-input">
              <input type="number" id="cdValue" inputmode="decimal" min="60" max="230" step="1"
                placeholder="e.g. 140" aria-describedby="cdHint" autocomplete="off">
              <span class="cd-suffix" id="cdSuffix" aria-hidden="true">yds</span>
            </div>
            <p class="cd-hint" id="cdHint">How far it flies before landing, on a normal swing. Not your best one.</p>
          </div>

          <div id="cdBandWrap" class="cd-field" hidden>
            <label for="cdBand">Your handicap</label>
            <select id="cdBand"></select>
            <fieldset class="cd-seg cd-group">
              <legend class="cd-legend">Compare with</legend>
              <label><input type="radio" name="cdGroup" value="men" checked><span>Men&rsquo;s data</span></label>
              <label><input type="radio" name="cdGroup" value="women"><span>Women&rsquo;s data</span></label>
            </fieldset>
            <p class="cd-hint">The published distance data is split this way, so the benchmark is too. A rough starting
              point only: one real carry number beats any handicap table.</p>
          </div>

          <button type="button" class="btn cd-go" id="cdGo" data-gr-run>Show my distances</button>
        </div>
      </section>

      <!-- ============ THE RESULT ============ -->
      <section class="out-wrap cd-out" id="cdOut" aria-labelledby="cdResultHead">
        <div class="cd-result">
          <h2 id="cdResultHead" tabindex="-1">Your carry distances</h2>
          <p class="cd-echo" id="cdEcho" aria-live="polite"></p>
          <p class="cd-quality" id="cdQuality"></p>

          <table class="cd-table">
            <caption class="cd-sr">Estimated carry distance for each club: the range to plan around and a best-strike range</caption>
            <thead>
              <tr><th scope="col">Club</th><th scope="col" data-cd-head="Plan on">Plan on (yds)</th><th scope="col" data-cd-head="Best strike">Best strike (yds)</th></tr>
            </thead>
            <tbody id="cdRows"></tbody>
          </table>
          <p class="cd-key"><b>Plan on</b> is the carry to choose clubs by. <b>Best strike</b> is a flushed one: it
            happens, but clubbing off it is how you come up short.</p>

          <details class="cd-bag">
            <summary>Hide clubs you don&rsquo;t carry</summary>
            <div class="cd-clubs" id="cdClubs"></div>
          </details>

          <div class="cd-tee" id="cdTee" hidden>
            <h3>Where to tee it up</h3>
            <p>A course of about <b id="cdTeeRange"></b> is a sensible starting point.</p>
            <p class="cd-hint" id="cdTeeBasis"></p>
            <p><a href="/tools-tee-box-check" data-gr-placement="result_tee_check">Check your tees</a> for the full
              comparison against the course you play.</p>
          </div>

          <div class="cd-next" data-gr-placement="result_bag_gaps">
            <h3>Next: the gaps between them</h3>
            <p>Estimates tell you what each club should do. The Bag Audit tells you whether two of your clubs do the
              same job, or leave a distance nothing covers.</p>
            <a class="btn" href="/tools-bag-audit">Check my bag gaps</a>
          </div>

          <p class="cd-real" data-gr-placement="result_measured_carry">These are estimates. For your real numbers,
            <a href="/tools-standing-order">log a range session in the Standing Order</a>: five balls a club gives you
            measured carry, and measured beats estimated every time.</p>

          <div class="btn-row cd-acts">
            <button type="button" class="btn ghost sm" id="cdCopy">Copy my distances</button>
            <span class="cd-hint" id="cdCopyMsg" role="status"></span>
          </div>
        </div>
      </section>

      <!-- ============ HOW IT WORKS ============ -->
      <section class="panel explain" aria-labelledby="cd-how-h">
        <div class="panel-in">
          <h2 id="cd-how-h">How this estimate works</h2>
          <p><b>Your number sets the scale.</b> A carry you have measured is the best anchor, swing speed is next,
            and a handicap band is a last resort. Enter a driver or 7-iron carry and it is used as given; enter a
            swing speed and the USGA&rsquo;s regression turns it into a typical driver carry; pick a handicap band
            and the same study&rsquo;s handicap trend does the job, with far wider ranges.</p>
          <p><b>Recreational ratios link the driver and the irons.</b> Club golfers keep more of their distance
            with irons than tour players do. In the USGA data a 7-iron went 22 yards plus 56% of the driver in total,
            which puts a typical 7-iron at about 0.68 of driver carry, against 0.62 on the PGA Tour. Using tour
            ratios would make an amateur&rsquo;s irons look about 5&ndash;8% too short.</p>
          <p><b>Tour data fills in the shape.</b> Woods, hybrid, long irons and short irons sit where TrackMan&rsquo;s
            2023 PGA Tour and LPGA averages put them, blended by how fast you swing. Slower swings get the
            bunched-up long game they really have: a hybrid and a 4-iron a few yards apart, not twenty.</p>
          <p><b>Ranges, not one number.</b> Each range is tight next to your own number and widens with every
            club away from it, and wider again for swing speed or handicap. The width is our modelling choice, not a
            published figure, which is why each club is labelled firm, fair or rough. <b>Best strike</b> sits 3&ndash;4%
            past the plan-on range. That is roughly how far golfers&rsquo; best two shots out of seven ran past
            their middle one in the USGA data.</p>
          <p>For tour and amateur averages club by club, see our
            <a href="/news-2026-golf-club-distances-guide">average golf club distance chart</a>.</p>

          <h3>Limitations</h3>
          <ul class="cd-sources">
            <li>It estimates; it does not measure. Swing speed explains most of how far a golfer hits it, not
              all of it: strike, launch and spin decide the rest.</li>
            <li>Gap and sand wedges have no published full-swing averages, so those two rows continue the
              9-iron-to-pitching-wedge step. Treat them as rough.</li>
            <li>A &ldquo;7-iron&rdquo; is not a fixed loft. Many game-improvement 7-irons are under 30 degrees; a
              generation ago that was a 4-iron (Golf Digest, 2023).</li>
            <li>Range balls usually fly shorter than your course ball: tests put the gap anywhere from 2% to 6%, so
              there is no single correction to apply. Hitting mats flatter iron strikes: the USGA recorded a
              7-iron smash factor of 1.41 off mats and 1.33 off grass.</li>
            <li>Altitude adds carry. Titleist&rsquo;s ball scientists put it at about 1.2% per 1,000 feet for a
              drive, less for shorter shots. This calculator assumes sea level.</li>
            <li>Handicap is a weak guide to distance. The women&rsquo;s benchmark uses the USGA&rsquo;s women&rsquo;s
              averages; both benchmarks come from a range study of golfers who were mostly 45 to 74.</li>
          </ul>
        </div>
      </section>

      <!-- ============ STATIC EXPLAINERS (readable without JavaScript) ============ -->
      <section class="panel explain" aria-labelledby="cd-carry-h">
        <div class="panel-in">
          <h2 id="cd-carry-h">Carry vs total distance</h2>
          <p><b>Carry</b> is how far the ball flies before it lands. <b>Total</b> adds the bounce and roll. Pick
            clubs on carry: bunkers, water and the front of the green have to be flown, not rolled over. In the
            USGA&rsquo;s TrackMan data a recreational driver rolled out roughly 25 to 30 yards, so carry is about
            86&ndash;89% of total; a 7-iron rolled 10&ndash;15 yards and a pitching wedge about 9. Real roll changes with the turf,
            which is why this calculator reports carry only.</p>

          <h2 id="cd-best-h">Typical shot vs best shot</h2>
          <p><b>Typical</b> is the middle of what you hit: the number to plan around. <b>Best</b> is a flushed one.
            It happens, but clubbing off it is how most amateur approaches end up short. The USGA found golfers
            overestimate their typical driver by 7% and their 7-iron by 4%. Their best two shots out of seven ran
            only about 3&ndash;4% past their middle one.</p>

          <h2 id="cd-seven-h">Why your 7-iron goes further or shorter than a chart</h2>
          <p>Loft, speed and strike. Lofts have strengthened so much that one brand&rsquo;s 7-iron can match
            another&rsquo;s 6-iron. Slower swings bunch the long clubs together because they cannot launch them
            high enough. Off-centre strikes lose distance in a hurry. And range balls, mats, cold air and
            altitude all move the number. That is why this tool starts from your number rather than a chart&rsquo;s.</p>

          <h2 id="cd-hcp-h">How handicap affects distance</h2>
          <p>Better players hit it further on average: in the USGA study, men gained about 30 yards of driver
            distance for every 10 handicap points lower, women about 23. But the spread around that trend is
            huge. Plenty of 20-handicappers outdrive a 10. Handicap is the fallback here, and the result says so.</p>

          <h2 id="cd-metres-h">Yards or metres</h2>
          <p>Switch units and everything converts: your input, every club, the course length and swing speed
            (km/h). It is the same data converted at the edges, not a separate metric table: the calculator works
            in yards and converts at exactly 0.9144 metres to the yard, so a 150-yard carry is about 137 metres and
            a 6,000-yard course about 5,490 metres. Many courses in Australia and Europe are measured in metres;
            use whichever your card uses. Pick once and GolfRaw remembers it on this device, so its other distance
            tools open in the same units.</p>

          <h3>What it returns for three golfers</h3>
          <table class="cd-examples">
            <caption class="cd-sr">Plan-on carry ranges in <span data-cd-word>yards</span> for three example golfers, from their typical 7-iron carry</caption>
            <thead><tr><th scope="col">Typical 7-iron carry</th><th scope="col">Driver</th><th scope="col">5-iron</th><th scope="col">Pitching wedge</th></tr></thead>
            <tbody>
              <tr><td data-cd-ex="120">120 yards</td><td data-cd-ex="157.996,193.106">158&ndash;193</td><td data-cd-ex="133.729,144.873">134&ndash;145</td><td data-cd-ex="91.646,103.345">92&ndash;103</td></tr>
              <tr><td data-cd-ex="145">145 yards</td><td data-cd-ex="194.946,238.267">195&ndash;238</td><td data-cd-ex="161.334,174.779">161&ndash;175</td><td data-cd-ex="107.109,120.783">107&ndash;121</td></tr>
              <tr><td data-cd-ex="170">170 yards</td><td data-cd-ex="237.923,290.794">238&ndash;291</td><td data-cd-ex="185.422,200.874">185&ndash;201</td><td data-cd-ex="126.546,142.701">127&ndash;143</td></tr>
            </tbody>
          </table>
          <p class="cd-hint"><span data-cd-cap>Yards</span>, carry, plan-on ranges straight from the calculator. The driver ranges are wider
            because they sit furthest from the 7-iron that was entered.</p>
        </div>
      </section>

      <section class="panel explain" aria-labelledby="cd-src-h">
        <div class="panel-in">
          <h2 id="cd-src-h">Sources</h2>
          <ul class="cd-sources">
            <li><b>TrackMan</b>, &ldquo;New PGA &amp; LPGA Tour Averages&rdquo;, 2 May 2024 (2023 data, carry): per-club
              club speed and carry for 200+ PGA Tour and DP World Tour players and 150+ LPGA and LET players.</li>
            <li><b>USGA</b>, D. Pierce, &ldquo;Quantitative Analysis of Recreational Golfer Club Hitting Distances:
              Measured versus Perception&rdquo;, 1 December 2023. TrackMan 4, 627 recreational golfers (548 men,
              79 women), average Handicap Index 13.2, measured 2021&ndash;2023. Its distance, speed and handicap
              regressions are on total distance; its carry-from-total fits (R&nbsp;0.98) convert them to carry.</li>
            <li><b>PGA of America and USGA</b>, &ldquo;Tee It Forward&rdquo; guidelines, 2011: average driving distance
              to recommended 18-hole yardage.</li>
            <li><b>Titleist</b>, S. Aoyama, &ldquo;The Effect of Altitude on Golf Ball Aerodynamics&rdquo;, 2019;
              <b>Golf Digest</b>, iron-loft testing, September 2023, and range-ball testing, September 2024;
              <b>GOLF.com</b>, range-ball testing, April 2021.</li>
          </ul>
          <p class="cd-updated">Updated 21 September 2026. Model version 1.</p>
        </div>
      </section>

      <section class="faq-block panel" aria-labelledby="faq-h">
        <h2 id="faq-h">Questions</h2>
        <details><summary>How far should a beginner hit a 7-iron?</summary>
          <p>There is no single right answer, and that is the point of starting from your own number. In the
            USGA&rsquo;s measured data the average recreational man hit a 7-iron 149 yards in total and the average
            woman 98, with a wide spread either side. If you have no number yet, pick the handicap option for a rough
            benchmark, then measure a real one.</p></details>
        <details><summary>Should I use carry or total distance to choose a club?</summary>
          <p>Carry. It is the part you control and the part that has to clear trouble. Total adds roll, which
            changes with every fairway, so it is a poor basis for club selection.</p></details>
        <details><summary>Why do my long irons go about the same distance?</summary>
          <p>Because at moderate swing speeds a 4-iron cannot get high enough to use its extra speed. The tour
            data shows the same squeeze at slower speeds, and this calculator reproduces it. It is also why a
            hybrid often replaces a 4- or 5-iron.</p></details>
        <details><summary>Does it work in metres?</summary>
          <p>Yes. Switch to metres and your input, every club, the course length and the swing speed (km/h)
            convert together. It is the same data converted, not a separate metric table, and GolfRaw remembers the
            choice on this device for its other distance tools.</p></details>
        <details><summary>Is anything I type stored or sent anywhere?</summary>
          <p>No. The calculation runs in your browser. GolfRaw counts that the calculator was used and which kind
            of number it started from, never the number itself or the result.</p></details>
      </section>

    </div>
  </div>
'''

SCRIPT = r'''  <script>
    /* ---- The Distance Check: page wiring ------------------------------------
       All maths lives in /lib/distance/club-distance.js (window.GolfrawDistance),
       which works in yards and mph. This script only converts units, validates,
       renders and reports actions (never values) to the tool-events layer. */
    (function () {
      'use strict';
      var D = window.GolfrawDistance;
      var $ = function (id) { return document.getElementById(id); };
      // Conversions and the shared yards/metres preference: /lib/distance/units.js.
      var U = window.GolfrawUnits;
      var state = { anchor: 'iron_carry', unit: U ? U.distUnit(U.distance()) : 'yd', last: null, used: null, hidden: {} };
      var fDist = null, fSpeed = null;

      var COPY = {
        driver_carry: { label: 'Your typical driver carry', hint: 'How far it flies before landing, on a normal swing. Not your best one.' },
        iron_carry: { label: 'Your typical 7-iron carry', hint: 'How far it flies before landing, on a normal swing. Not your best one.' },
        swing_speed: { label: 'Your driver swing speed', hint: 'Club-head speed from a launch monitor or radar, not ball speed.' }
      };

      function speedUnit() { return state.unit === 'm' ? 'km/h' : 'mph'; }
      function distUnit() { return state.unit === 'm' ? 'm' : 'yds'; }
      function distWord() { return state.unit === 'm' ? 'metres' : 'yards'; }

      // Model units (yards, mph) <-> what the golfer sees. Speed follows the
      // distance choice: km/h with metres, mph with yards.
      function speedCode() { return state.unit === 'm' ? 'kmh' : 'mph'; }
      function kindNow() { return state.anchor === 'swing_speed' ? 'speed' : 'distance'; }
      function codeNow() { return kindNow() === 'speed' ? speedCode() : state.unit; }
      function activeField() { return state.anchor === 'swing_speed' ? fSpeed : fDist; }
      function fromModel(v, isSpeed) { return U.fromCanon(isSpeed ? 'speed' : 'distance', v, isSpeed ? speedCode() : state.unit); }
      function limits() { return U.limits(kindNow(), D.LIMITS[state.anchor], codeNow()); }
      function show(yd) { return Math.round(fromModel(yd, false)); }
      function range(r) { return show(r[0]) + '–' + show(r[1]); }
      // Course lengths round once, to 50 in the unit on screen, from the unrounded chart.
      function course(yd) { return U.show('distance', yd, state.unit, 50); }

      function syncInputs() {
        var hcp = state.anchor === 'handicap_band';
        $('cdNumber').hidden = hcp;
        $('cdBandWrap').hidden = !hcp;
        if (!hcp) {
          var c = COPY[state.anchor], l = limits();
          var unit = state.anchor === 'swing_speed' ? speedUnit() : distWord();
          $('cdValueLabel').textContent = c.label + ' (' + unit + ')';
          $('cdSuffix').textContent = state.anchor === 'swing_speed' ? speedUnit() : distUnit();
          $('cdHint').textContent = c.hint + ' This works from ' + l[0] + ' to ' + l[1] + ' ' + unit + '.';
          $('cdValue').min = l[0]; $('cdValue').max = l[1];
        }
        var marks = document.querySelectorAll('[data-cd-unit]');
        for (var i = 0; i < marks.length; i++) marks[i].textContent = marks[i].getAttribute('data-cd-unit') === 'speed' ? speedUnit() : distUnit();
      }

      function err(msg) {
        var e = $('cdErr');
        e.textContent = msg || '';
        e.className = msg ? 'err show' : 'err';
        $('cdValue').setAttribute('aria-invalid', msg ? 'true' : 'false');
      }

      function read() {
        if (state.anchor === 'handicap_band') {
          return { anchor: 'handicap_band', band: $('cdBand').value, group: document.querySelector('input[name="cdGroup"]:checked').value };
        }
        // The exact value behind the field, already in model units.
        var c = activeField().canon();
        if (c === null) return { error: 'Enter ' + COPY[state.anchor].label.toLowerCase() + ' first.' };
        if (isNaN(c)) return { error: 'That is not a number we can use.' };
        var l = limits(), lim = D.LIMITS[state.anchor];
        var unit = state.anchor === 'swing_speed' ? speedUnit() : distWord();
        if (c < lim[0] - 1e-9 || c > lim[1] + 1e-9) {
          var low = c < lim[0];
          return { error: 'This works from ' + l[0] + ' to ' + l[1] + ' ' + unit + '. ' +
            (low && state.unit === 'yd' && state.anchor !== 'swing_speed' ? 'Did you mean metres?' :
             !low && state.unit === 'm' && state.anchor !== 'swing_speed' ? 'Did you mean yards?' : 'Check the number.') };
        }
        return { anchor: state.anchor, value: c };
      }

      var QUALITY = {
        measured: 'Built from a real carry number. The clubs either side of it are the firmest; the far ends of the bag are rougher.',
        speed: 'Built from swing speed. Speed explains most of your distance, not all of it: strike, launch and spin decide the rest, so treat these as rougher than a measured carry.',
        benchmark: 'Rough benchmark only. Handicap says a lot about scoring and much less about distance. One real carry number would make this far better.'
      };
      var CONF = { firm: 'Firm', fair: 'Fair', rough: 'Rough' };

      function anchorEcho(res) {
        if (res.anchor === 'handicap_band') return 'From the ' + res.bandLabel + ' benchmark';
        // The number the result was built from, shown in whichever units are on now.
        var shown = Math.round(fromModel(state.used, res.anchor === 'swing_speed'));
        if (res.anchor === 'swing_speed') return 'From a driver swing speed of ' + shown + ' ' + speedUnit();
        return 'From a typical ' + (res.anchor === 'driver_carry' ? 'driver' : '7-iron') + ' carry of ' + shown + ' ' + distUnit();
      }

      function render() {
        var res = state.last;
        if (!res) return;
        $('cdEcho').textContent = anchorEcho(res);
        $('cdQuality').textContent = QUALITY[res.quality];
        $('cdQuality').setAttribute('data-quality', res.quality);
        var rows = [];
        for (var i = 0; i < res.clubs.length; i++) {
          var c = res.clubs[i];
          if (state.hidden[c.id]) continue;
          rows.push('<tr' + (c.anchor ? ' class="is-anchor"' : '') + '><th scope="row">' + c.label +
            '<span class="cd-conf">' + (c.anchor ? 'Your number' : CONF[c.confidence] + ' estimate') + '</span></th>' +
            '<td>' + range(c.typical) + '</td><td>' + range(c.best) + '</td></tr>');
        }
        $('cdRows').innerHTML = rows.join('');
        var heads = document.querySelectorAll('[data-cd-head]');
        for (var h = 0; h < heads.length; h++) heads[h].textContent = heads[h].getAttribute('data-cd-head') + ' (' + distUnit() + ')';
        if (res.tee) {
          $('cdTee').hidden = false;
          $('cdTeeRange').textContent = course(res.tee.courseRaw[0]) + '–' + course(res.tee.courseRaw[1]) + ' ' + distWord() +
            (res.tee.beyondChart ? ' (your drive sits at the edge of the chart, so read this loosely)' : '');
          $('cdTeeBasis').textContent = 'That is the Tee It Forward chart read at an estimated total drive of ' +
            range(res.tee.total) + ' ' + distUnit() + ' (your carry plus normal roll). Guidance, not a rule: firm, flat courses play shorter than the card.';
        } else {
          $('cdTee').hidden = true;
        }
      }

      function run() {
        if (!D) { err('The calculator did not load. Reload the page and try again.'); return; }
        var input = read();
        if (input.error) { err(input.error); return; }
        var res = D.estimate(input);
        if (!res.ok) { err('That combination did not work. Pick an option and try again.'); return; }
        err('');
        state.last = res;
        state.used = input.value;
        render();
        var out = $('cdOut');
        out.classList.add('show');
        $('cdResultHead').focus({ preventScroll: true });
        out.scrollIntoView({ behavior: 'smooth', block: 'start' });
        if (window.GRTrack) GRTrack.completed({ anchor_type: res.anchor });
      }

      function copySummary() {
        var res = state.last;
        if (!res) return;
        var lines = ['MY CLUB DISTANCES (carry, ' + distWord() + ')', anchorEcho(res), ''];
        for (var i = 0; i < res.clubs.length; i++) {
          var c = res.clubs[i];
          if (state.hidden[c.id]) continue;
          lines.push(c.label + ': plan on ' + range(c.typical) + ', best ' + range(c.best));
        }
        lines.push('', 'Estimates from golfraw.com/tools-club-distance-calculator');
        var txt = lines.join('\n');
        var done = function () {
          if (window.GRTrack) GRTrack.shared('copy_result');
          $('cdCopyMsg').textContent = 'Copied. Paste it into your notes or yardage book.';
        };
        var fail = function () { $('cdCopyMsg').textContent = 'Could not copy on this device.'; };
        // Same fallback as the other tools: some browsers refuse the async
        // clipboard, so fall back to a hidden textarea and execCommand.
        var legacy = function () {
          var ta = document.createElement('textarea');
          ta.value = txt; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.opacity = '0';
          document.body.appendChild(ta); ta.select();
          var ok = false;
          try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
          document.body.removeChild(ta);
          if (ok) done(); else fail();
        };
        if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt).then(done, legacy);
        else legacy();
      }

      function buildClubList() {
        var html = [];
        for (var i = 0; i < D.CLUBS.length; i++) {
          var c = D.CLUBS[i];
          html.push('<label class="cd-club"><input type="checkbox" value="' + c.id + '" checked> ' + c.label + '</label>');
        }
        $('cdClubs').innerHTML = html.join('');
      }

      // The worked examples carry exact model values; show them in the chosen unit.
      function renderExamples() {
        var cells = document.querySelectorAll('[data-cd-ex]');
        for (var i = 0; i < cells.length; i++) {
          var v = cells[i].getAttribute('data-cd-ex').split(',').map(parseFloat);
          cells[i].textContent = v.length === 1 ? show(v[0]) + ' ' + distWord() : range(v);
        }
        var words = document.querySelectorAll('[data-cd-word]');
        for (var w = 0; w < words.length; w++) words[w].textContent = distWord();
        var caps = document.querySelectorAll('[data-cd-cap]');
        for (var k = 0; k < caps.length; k++) caps[k].textContent = state.unit === 'm' ? 'Metres' : 'Yards';
      }

      function syncUnitRadios() {
        var radios = document.querySelectorAll('input[name="cdUnit"]');
        for (var i = 0; i < radios.length; i++) radios[i].checked = radios[i].value === state.unit;
      }

      // Switching keeps the exact value typed: the field redraws from it, so
      // yards -> metres -> yards returns the original number.
      function setUnit(next) {
        if (next === state.unit) return;
        U.switchFields([activeField()], function () { state.unit = next; });
        syncUnitRadios();
        syncInputs();
        err('');
        render();
        renderExamples();
      }

      function boot() {
        if (!D) { err('The calculator did not load. Reload the page and try again.'); return; }
        var bands = [];
        for (var i = 0; i < D.BANDS.length; i++) bands.push('<option value="' + D.BANDS[i].id + '">' + D.BANDS[i].label + '</option>');
        $('cdBand').innerHTML = bands.join('');
        $('cdBand').value = D.DEFAULT_BAND;
        buildClubList();

        fDist = U.field($('cdValue'), 'distance', function () { return state.unit; });
        fSpeed = U.field($('cdValue'), 'speed', speedCode);
        var anchors = document.querySelectorAll('input[name="cdAnchor"]');
        for (var a = 0; a < anchors.length; a++) {
          anchors[a].addEventListener('change', function (e) {
            state.anchor = e.target.value;
            fDist.set(null); fSpeed.set(null);
            err('');
            syncInputs();
          });
        }
        // One preference for every GolfRaw distance tool, kept in the Locker.
        var units = document.querySelectorAll('input[name="cdUnit"]');
        for (var u = 0; u < units.length; u++) {
          units[u].addEventListener('change', function (e) { U.setDistance(e.target.value === 'm' ? 'meters' : 'yards'); });
        }
        U.onChange(function (pref) { setUnit(U.distUnit(pref)); });
        syncUnitRadios();
        renderExamples();
        $('cdValue').addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); run(); } });
        $('cdGo').addEventListener('click', run);
        $('cdCopy').addEventListener('click', copySummary);
        $('cdClubs').addEventListener('change', function (e) {
          if (e.target && e.target.type === 'checkbox') { state.hidden[e.target.value] = !e.target.checked; render(); }
        });
        syncInputs();
      }

      if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
    })();
  </script>
'''

MODEL = ('  <script src="/lib/distance/units.js?v=%s"></script>\n' % UNITS_VER +
         '  <script src="/lib/distance/club-distance.js?v=%s"></script>\n' % MODEL_VER)

TAIL = '''  <script>window.__gr_consent=true;window.__gr_ads=false;</script>
'''


def main():
    p = shell_parts()
    doc = '\n'.join([
        rewrite_meta(p['head_top']),
        JSONLD,
        p['head_tail'].replace(PREMIUM_LINK, '').replace('</head>', STYLE + PREMIUM_LINK + '</head>'),
        p['body_open'],
        MAIN,
        p['footer'],
        '',
        p['nav_script'],
        MODEL + SCRIPT,
        p['gtag'],
        TAIL + '</body>',
        '',
        '</html>',
    ])
    doc = normalize_tool_page(doc, OUT)
    io.open(OUT, 'w', encoding='utf-8').write(doc)
    print('  wrote %s (%d bytes)' % (os.path.basename(OUT), len(doc.encode('utf-8'))))
    return 0


if __name__ == '__main__':
    sys.exit(main())
