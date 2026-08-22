#!/usr/bin/env python3
"""Generate tools-standing-order.html from the shared tool-page shell.

The head (fonts, design tokens, shared CSS), header and footer are lifted
verbatim from tools-bag-audit.html so the new tool cannot drift from the rest
of the site. Only the metadata, structured data and the tool itself are new.

Re-runnable: it rewrites the file wholesale from the shell each time.
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHELL = os.path.join(ROOT, 'tools-bag-audit.html')
OUT = os.path.join(ROOT, 'tools-standing-order.html')

SITE = 'https://www.golfraw.com'
SLUG = 'tools-standing-order'
TITLE = 'The Standing Order: Range Session Gapping Logger | GOLFRAW'
DESC = ('Free range session logger. Tap in 5-10 carries per club and get your real median '
        'distance, shot dispersion and the exact gaps and overlaps in your bag.')
OG_IMAGE = SITE + '/public/raw-golf-practice.webp'

# ---------------------------------------------------------------- shell parts

def shell_parts():
    lines = io.open(SHELL, encoding='utf-8').read().split('\n')
    return {
        # 1..45  head open through the primary-SEO comment (metadata rewritten below)
        'head_top': '\n'.join(lines[0:45]),
        # 201..419  fonts, design tokens, shared CSS, </head>
        'head_tail': '\n'.join(lines[200:419]),
        # 420..439  <body> + site header
        'body_open': '\n'.join(lines[419:439]),
        # 638..656  site footer
        'footer': '\n'.join(lines[637:656]),
        # 661..675  nav / burger behaviour
        'nav_script': '\n'.join(lines[660:675]),
        # gtag block
        'gtag': '\n'.join(lines[1169:1175]),
    }


def rewrite_meta(head_top):
    """Point the lifted metadata block at this page."""
    s = head_top
    s = re.sub(r'<title>.*?</title>', '<title>%s</title>' % TITLE, s, flags=re.S)
    s = re.sub(r'(<meta name="description" content=")[^"]*(")', r'\g<1>%s\g<2>' % DESC, s)
    s = re.sub(r'(<link rel="canonical" href=")[^"]*(")', r'\g<1>%s/%s\g<2>' % (SITE, SLUG), s)
    s = re.sub(r'(<meta property="og:title" content=")[^"]*(")', r'\g<1>%s\g<2>' % TITLE, s)
    s = re.sub(r'(<meta property="og:description" content=")[^"]*(")', r'\g<1>%s\g<2>' % DESC, s)
    s = re.sub(r'(<meta property="og:url" content=")[^"]*(")', r'\g<1>%s/%s\g<2>' % (SITE, SLUG), s)
    s = re.sub(r'(<meta property="og:image" content=")[^"]*(")', r'\g<1>%s\g<2>' % OG_IMAGE, s)
    s = re.sub(r'(<meta name="twitter:title" content=")[^"]*(")', r'\g<1>%s\g<2>' % TITLE, s)
    s = re.sub(r'(<meta name="twitter:description" content=")[^"]*(")', r'\g<1>%s\g<2>' % DESC, s)
    s = re.sub(r'(<meta name="twitter:image" content=")[^"]*(")', r'\g<1>%s\g<2>' % OG_IMAGE, s)
    return s


JSONLD = '''  <!-- ============ STRUCTURED DATA ============ -->
  <script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "The Standing Order",
  "alternateName": "Range Session Gapping Logger",
  "url": "%(site)s/%(slug)s",
  "applicationCategory": "SportsApplication",
  "operatingSystem": "Any browser",
  "browserRequirements": "Requires JavaScript",
  "description": "%(desc)s",
  "offers": { "@type": "Offer", "price": "0", "priceCurrency": "USD" },
  "featureList": [
    "Log 5-10 carry distances per club",
    "Median carry and shot dispersion per club",
    "80%% shot band from your own numbers",
    "Automatic overlap and gap detection",
    "Saves to your bag, entirely on your device"
  ],
  "publisher": { "@type": "Organization", "name": "GOLFRAW", "url": "%(site)s/" }
}
  </script>
  <script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "%(site)s/" },
    { "@type": "ListItem", "position": 2, "name": "Tools", "item": "%(site)s/tools" },
    { "@type": "ListItem", "position": 3, "name": "The Standing Order", "item": "%(site)s/%(slug)s" }
  ]
}
  </script>
  <script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How many shots per club do I need to gap my bag?",
      "acceptedAnswer": { "@type": "Answer", "text": "Five is the working minimum and eight to ten is where the numbers settle down. Below five shots a single fat strike drags the median far enough to make the gap chart wrong, which is worse than having no chart at all." }
    },
    {
      "@type": "Question",
      "name": "Should I use my average or my median carry distance?",
      "acceptedAnswer": { "@type": "Answer", "text": "Median. One thinned 7-iron that goes 40 yards short pulls an average down by several yards and quietly invents a gap that is not there. The median ignores it, so it describes the shot you actually hit most of the time." }
    },
    {
      "@type": "Question",
      "name": "What is a normal distance gap between golf clubs?",
      "acceptedAnswer": { "@type": "Answer", "text": "Ten to fifteen yards between irons is the usual target. Once a gap passes 25 yards you have a distance with no club for it, and under 8 yards two clubs are doing the same job and one of them is taking up a slot for nothing." }
    },
    {
      "@type": "Question",
      "name": "Does this range logger send my numbers anywhere?",
      "acceptedAnswer": { "@type": "Answer", "text": "No. Every shot is stored in your own browser using IndexedDB and never leaves the device. There is no account, no upload and no third party. Clearing your browser data deletes it, so export a backup from the locker if you want to keep it." }
    }
  ]
}
  </script>
''' % {'site': SITE, 'slug': SLUG, 'desc': DESC}


# --------------------------------------------------------------- tool styles

STYLE = '''<style>
    /* ---- The Standing Order: range logger --------------------------------
       Thumb-first. Every control the reader touches on the mat sits in the
       lower half of the screen and clears 48px, because this is used one
       handed, outdoors, in sunlight, with a glove on. */
    .so-wrap { max-width: 620px; margin: 0 auto }

    .so-step { font-size: 11px; font-weight: 800; letter-spacing: .12em;
      text-transform: uppercase; color: var(--grey); margin-bottom: 10px }

    /* club strip */
    .so-clubs { display: flex; gap: 8px; overflow-x: auto; padding: 4px 2px 10px;
      -webkit-overflow-scrolling: touch; scrollbar-width: thin }
    .so-club { flex: 0 0 auto; min-height: 48px; padding: 0 16px; background: var(--white);
      border: 2px solid var(--ink); font: 800 13px/1 'Archivo', system-ui, sans-serif;
      text-transform: uppercase; letter-spacing: .04em; cursor: pointer; white-space: nowrap;
      display: flex; align-items: center; gap: 7px; transition: background .15s, color .15s }
    .so-club:hover { background: var(--fairway); color: #fff; border-color: var(--fairway) }
    .so-club[aria-pressed="true"] { background: var(--ink); color: #fff }
    .so-club:focus-visible { outline: 3px solid var(--flag); outline-offset: 2px }
    .so-club .n { font-family: 'IBM Plex Mono', monospace; font-size: 11px; font-weight: 600;
      background: var(--flag); color: #fff; padding: 2px 5px; min-width: 18px; text-align: center }
    .so-club[aria-pressed="true"] .n { background: #fff; color: var(--ink) }

    /* readout */
    .so-readout { background: var(--ink); color: #fff; padding: 18px 20px; margin: 4px 0 12px;
      display: flex; align-items: baseline; justify-content: space-between; gap: 12px }
    .so-readout .val { font-family: 'IBM Plex Mono', monospace; font-size: 46px; font-weight: 600;
      line-height: 1; letter-spacing: -.02em; font-variant-numeric: tabular-nums }
    .so-readout .val.ghost { opacity: .35 }
    .so-readout .unit { font-size: 12px; font-weight: 800; letter-spacing: .12em;
      text-transform: uppercase; opacity: .7 }

    /* keypad */
    .so-pad { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px }
    .so-key { min-height: 58px; background: var(--white); border: 2px solid var(--ink);
      font: 600 22px/1 'IBM Plex Mono', monospace; color: var(--ink); cursor: pointer;
      transition: background .12s, color .12s; touch-action: manipulation }
    .so-key:hover { background: var(--paper) }
    .so-key:active { background: var(--ink); color: #fff }
    .so-key:focus-visible { outline: 3px solid var(--flag); outline-offset: 2px }
    .so-key.util { font-family: 'Archivo', system-ui, sans-serif; font-size: 12px; font-weight: 800;
      letter-spacing: .06em; text-transform: uppercase }

    .so-log { width: 100%; min-height: 58px; margin-top: 10px; background: var(--flag); color: #fff;
      border: 2px solid var(--flag); font: 900 15px/1 'Archivo', system-ui, sans-serif;
      letter-spacing: .08em; text-transform: uppercase; cursor: pointer;
      transition: background .15s; touch-action: manipulation }
    .so-log:hover { background: #c1301f; border-color: #c1301f }
    .so-log:focus-visible { outline: 3px solid var(--ink); outline-offset: 3px }
    .so-log[disabled] { background: var(--line); border-color: var(--line); color: var(--grey);
      cursor: not-allowed }

    /* logged shots */
    .so-shots { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 14px; min-height: 34px }
    .so-shot { display: inline-flex; align-items: center; gap: 6px; min-height: 34px; padding: 0 6px 0 10px;
      background: var(--white); border: 2px solid var(--line);
      font: 600 13px/1 'IBM Plex Mono', monospace }
    .so-shot button { width: 26px; height: 26px; border: 0; background: none; color: var(--grey);
      font-size: 17px; line-height: 1; cursor: pointer; padding: 0 }
    .so-shot button:hover { color: var(--flag) }
    .so-shot button:focus-visible { outline: 2px solid var(--flag) }
    .so-none { font-size: 13px; color: var(--grey); line-height: 34px }

    /* session bar */
    .so-bar { display: flex; justify-content: space-between; align-items: center; gap: 12px;
      flex-wrap: wrap; margin-top: 18px; padding-top: 16px; border-top: 2px solid var(--line);
      font-size: 13px; color: var(--grey) }
    .so-bar b { color: var(--ink); font-family: 'IBM Plex Mono', monospace; font-weight: 600 }

    .so-go { min-height: 52px; padding: 0 22px; background: var(--ink); color: #fff;
      border: 2px solid var(--ink); font: 900 13px/1 'Archivo', system-ui, sans-serif;
      letter-spacing: .08em; text-transform: uppercase; cursor: pointer; transition: background .15s }
    .so-go:hover { background: var(--fairway); border-color: var(--fairway) }
    .so-go:focus-visible { outline: 3px solid var(--flag); outline-offset: 3px }
    .so-go[disabled] { background: var(--line); border-color: var(--line); color: var(--grey); cursor: not-allowed }

    /* results */
    .so-chart { width: 100%; max-width: 560px; height: auto; display: block; margin: 0 auto }
    .so-tbl { width: 100%; border-collapse: collapse; margin-top: 6px; font-size: 13.5px }
    .so-tbl th { text-align: right; font-size: 10.5px; font-weight: 800; letter-spacing: .08em;
      text-transform: uppercase; color: var(--grey); padding: 0 0 7px; border-bottom: 2px solid var(--ink) }
    .so-tbl th:first-child, .so-tbl td:first-child { text-align: left }
    .so-tbl td { text-align: right; padding: 9px 0; border-bottom: 1px solid var(--line);
      font-family: 'IBM Plex Mono', monospace; font-weight: 600 }
    .so-tbl td:first-child { font-family: 'Archivo', system-ui, sans-serif; font-weight: 700 }
    .so-tbl .thin { color: var(--grey); font-weight: 500 }
    .so-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch }

    .so-flag { display: flex; gap: 11px; padding: 13px 15px; margin-top: 10px; background: var(--white);
      border: 2px solid var(--ink); border-left-width: 7px; font-size: 14px; line-height: 1.5 }
    .so-flag.gap { border-left-color: var(--flag) }
    .so-flag.dup { border-left-color: #C98A00 }
    .so-flag.ok { border-left-color: var(--fairway) }
    .so-flag b { display: block; font-size: 11px; letter-spacing: .09em; text-transform: uppercase;
      margin-bottom: 3px }
    .so-flag.gap b { color: var(--flag) }
    .so-flag.dup b { color: #8A5E00 }
    .so-flag.ok b { color: var(--fairway) }

    .so-acts { display: flex; flex-wrap: wrap; gap: 9px; margin-top: 20px }
    .so-note { font-size: 12.5px; color: var(--grey); line-height: 1.55; margin-top: 12px }

    /* modal */
    .so-scrim { position: fixed; inset: 0; z-index: 9100; background: rgba(16,21,17,.6);
      display: none }
    .so-scrim.on { display: block }
    .so-modal { position: fixed; z-index: 9101; left: 50%; top: 50%; transform: translate(-50%,-50%);
      width: min(480px, calc(100% - 28px)); max-height: 88vh; overflow-y: auto; background: var(--paper);
      border: 3px solid var(--ink); display: none }
    .so-modal.on { display: block }
    .so-mhead { display: flex; align-items: center; justify-content: space-between; gap: 12px;
      padding: 15px 17px; border-bottom: 3px solid var(--ink) }
    .so-mhead h3 { font-size: 17px; font-weight: 900; text-transform: uppercase; letter-spacing: -.01em }
    .so-mx { width: 44px; height: 44px; margin: -6px -8px -6px 0; background: none; border: 0;
      font-size: 24px; line-height: 1; cursor: pointer; color: var(--ink) }
    .so-mx:hover { background: var(--ink); color: #fff }
    .so-mx:focus-visible { outline: 3px solid var(--flag); outline-offset: -3px }
    .so-mbody { padding: 17px }
    .so-mbody label { display: block; font-size: 11px; font-weight: 800; letter-spacing: .08em;
      text-transform: uppercase; color: var(--grey); margin-bottom: 6px }
    .so-mbody input[type=email] { width: 100%; min-height: 50px; padding: 12px 14px; background: #fff;
      border: 2px solid var(--ink); font: 600 15px/1.2 'Archivo', system-ui, sans-serif; color: var(--ink) }
    .so-mbody input[type=email]:focus { outline: 3px solid var(--flag); outline-offset: -1px }
    .so-msg { margin-top: 11px; padding: 10px 12px; border: 2px solid var(--ink); background: #fff;
      font-size: 13px; font-weight: 600; line-height: 1.45; display: none }
    .so-msg.on { display: block }
    .so-msg.bad { border-color: var(--flag); color: var(--flag) }
    .so-msg.good { border-color: var(--fairway); color: var(--fairway) }

    .so-sr { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden;
      clip: rect(0 0 0 0); white-space: nowrap; border: 0 }

    /* print: only the gapping chart, laid out for paper */
    #printArea { display: none }
    @media print {
      body > *:not(#printArea) { display: none !important }
      #printArea { display: block !important; padding: 0 }
      #printArea h1 { font-size: 22px; font-weight: 900; text-transform: uppercase; margin-bottom: 2px }
      #printArea .sub { font-size: 12px; color: #444; margin-bottom: 18px }
      #printArea .so-chart { max-width: 100%; margin: 0 0 20px }
      #printArea table { width: 100%; border-collapse: collapse; font-size: 12px }
      #printArea th, #printArea td { padding: 6px 4px; border-bottom: 1px solid #bbb; text-align: right }
      #printArea th:first-child, #printArea td:first-child { text-align: left }
      #printArea .foot { margin-top: 22px; font-size: 10.5px; color: #555 }
      .so-scrim, .so-modal { display: none !important }
    }

    @media (prefers-reduced-motion: reduce) {
      .so-club, .so-key, .so-log, .so-go { transition: none }
    }

    @media (max-width: 520px) {
      .so-readout .val { font-size: 40px }
      .so-key { min-height: 54px; font-size: 20px }
      /* The six-column table only just clears 375px and would overflow a 360px
         handset. Tighten the headers rather than let it scroll by default, and
         pin the club name so it stays readable if it ever does scroll. */
      .so-tbl { font-size: 12.5px }
      .so-tbl th { font-size: 9.5px; letter-spacing: .02em }
      .so-tbl td { padding: 8px 0 }
      .so-tbl th + th, .so-tbl td + td { padding-left: 6px }
      .so-tbl th:first-child, .so-tbl td:first-child {
        position: sticky; left: 0; background: var(--white); padding-right: 6px }
    }
  </style>
'''

# ------------------------------------------------------------------ page body

MAIN = '''
  <div class="hub-hero">
    <div class="wrap">
      <div class="eyebrow">RAWGOLF &middot; TOOLS</div>
      <h1>The Standing Order</h1>
      <p>Your bag is gapped on numbers a fitter read off a launch monitor once, on a good day, indoors.
        This logs what you actually hit on the range &mdash; five to ten balls a club &mdash; and gives you the
        median carry, how far the bad ones stray, and the two clubs quietly doing the same job.
        Runs entirely in your browser. Nothing uploaded, nothing sold to you.</p>
    </div>
  </div>

  <div class="tool-body">
    <div class="wrap">

      <!-- ============ AEO: DIRECT ANSWER ============ -->
      <section class="answer-block" aria-labelledby="aeo-q">
        <div class="ab-tag">The short answer</div>
        <h2 id="aeo-q">How do you gap your golf clubs at the driving range?</h2>
        <blockquote>Hit five to ten balls with each club, write down every carry, and take the
          <b>median</b> rather than the average &mdash; one thinned shot ruins an average. Aim for 10&ndash;15
          yards between clubs. Over 25 yards is a hole in your bag; under 8 yards means two clubs are
          doing one job.</blockquote>
      </section>

      <!-- ============ THE LOGGER ============ -->
      <section class="panel" aria-labelledby="log-h">
        <h2 id="log-h">Log the session</h2>
        <div class="so-wrap">

          <p class="so-step" id="s1">Step 1 &mdash; pick the club</p>
          <div class="so-clubs" id="clubStrip" role="group" aria-labelledby="s1"></div>

          <p class="so-step" id="s2">Step 2 &mdash; tap the carry, then log it</p>
          <div class="so-readout" aria-live="polite" aria-atomic="true">
            <span class="val ghost" id="readout">0</span>
            <span class="unit" id="unitLabel">yards carry</span>
          </div>

          <div class="so-pad" id="pad" role="group" aria-labelledby="s2">
            <button type="button" class="so-key" data-k="1">1</button>
            <button type="button" class="so-key" data-k="2">2</button>
            <button type="button" class="so-key" data-k="3">3</button>
            <button type="button" class="so-key" data-k="4">4</button>
            <button type="button" class="so-key" data-k="5">5</button>
            <button type="button" class="so-key" data-k="6">6</button>
            <button type="button" class="so-key" data-k="7">7</button>
            <button type="button" class="so-key" data-k="8">8</button>
            <button type="button" class="so-key" data-k="9">9</button>
            <button type="button" class="so-key util" data-k="clear" aria-label="Clear the number">Clear</button>
            <button type="button" class="so-key" data-k="0">0</button>
            <button type="button" class="so-key util" data-k="del" aria-label="Delete last digit">&#9003;</button>
          </div>

          <button type="button" class="so-log" id="logBtn" disabled>Log shot</button>

          <div class="so-shots" id="shotList" aria-live="polite" aria-label="Shots logged for this club"></div>

          <div class="so-bar">
            <span><b id="sesClubs">0</b> clubs &middot; <b id="sesShots">0</b> shots this session</span>
            <button type="button" class="so-go" id="goBtn" disabled>See the gaps</button>
          </div>
          <p class="so-note" id="saveState">Every shot saves to this device as you tap. Close the tab and
            come back &mdash; the session will still be here.</p>
        </div>
      </section>

      <!-- ============ RESULTS ============ -->
      <section class="panel" id="results" hidden aria-labelledby="res-h">
        <h2 id="res-h">Your bag, on your own numbers</h2>
        <div class="so-wrap">
          <div id="chartHost"></div>
          <div class="so-scroll">
            <table class="so-tbl" id="statTbl">
              <thead>
                <tr>
                  <th scope="col">Club</th>
                  <th scope="col">Shots</th>
                  <th scope="col">Median</th>
                  <th scope="col">Spread</th>
                  <th scope="col">80% band</th>
                  <th scope="col">Gap</th>
                </tr>
              </thead>
              <tbody id="statBody"></tbody>
            </table>
          </div>
          <div id="verdicts"></div>
          <div class="so-acts">
            <button type="button" class="so-go" id="saveBag">Save these to my bag</button>
            <button type="button" class="so-go" id="chartBtn">Get my gapping chart</button>
          </div>
          <div class="so-msg" id="resMsg" role="status"></div>
          <p class="so-note">The <b>80% band</b> is where 80% of your shots with that club finished &mdash;
            the tenth to the ninetieth percentile of what you actually hit. It is a description of your
            dispersion, not a confidence interval around the median, and it gets meaningful at about eight
            shots. Below five the number is guesswork and this tool says so rather than pretending.</p>
        </div>
      </section>

      <!-- ============ METHOD ============ -->
      <section class="panel explain">
        <h2>Why median, and why 25 yards</h2>
        <p>An average is the wrong tool for range balls. Hit nine 7-irons at 160 and one thinned
          low-runner that carries 105, and the average says 154.5 &mdash; a club you do not own. The median
          says 160, which is the shot you will hit on the course. Every distance on this page is a median
          for that reason.</p>
        <p><b>Spread</b> is the standard deviation of your carries: roughly how far a typical shot strays
          from the middle. A tight iron sits near 4&ndash;6 yards. Anything past 12 is either a club you cannot
          control or a bucket of range balls that vary more than your swing does &mdash; and on a scuffed
          range ball it is usually both, which is why the absolute numbers matter less than the gaps
          between them.</p>
        <p><b>Gaps</b> are measured median to median. Under 8 yards, two clubs are doing one job and one
          of them is spending a slot for nothing. Over 25 yards, there is a distance you simply cannot
          cover, and you will find it on a par three at the worst possible moment.</p>
        <p>Range balls fly shorter than premium balls &mdash; commonly 5&ndash;10% shorter on full swings. That
          offset applies to every club roughly equally, so your <em>gaps</em> stay honest even when the
          absolute yardages read low. Gap on the shape of the ladder, not the height of it.</p>
      </section>

      <!-- ============ FAQ ============ -->
      <section class="faq-block panel" aria-labelledby="faq-h">
        <h2 id="faq-h">Questions</h2>
        <details><summary>How many shots per club do I need?</summary>
          <p>Five is the working minimum, eight to ten is where it settles. Below five, one fat strike
            drags the median far enough to make the chart wrong &mdash; worse than no chart at all. This tool
            marks any club with fewer than five shots as unreliable rather than quietly scoring it.</p></details>
        <details><summary>Should I use my average or my median?</summary>
          <p>Median, every time. One thinned iron pulls an average down several yards and invents a gap
            that is not there. The median ignores the outlier and describes the shot you actually hit.</p></details>
        <details><summary>What is a normal gap between clubs?</summary>
          <p>Ten to fifteen yards between irons. Past 25 yards you have a distance with no club for it;
            under 8 yards two clubs overlap and one is redundant.</p></details>
        <details><summary>Does this send my numbers anywhere?</summary>
          <p>No. Every shot is stored in your own browser and never leaves the device &mdash; no account, no
            upload, no third party. Clearing your browser data deletes it, so export a backup from the
            locker if you want to keep it.</p></details>
      </section>

    </div>
  </div>

  <!-- ============ CHART MODAL ============ -->
  <div class="so-scrim" id="scrim"></div>
  <div class="so-modal" id="modal" role="dialog" aria-modal="true" aria-labelledby="modal-h" hidden>
    <div class="so-mhead">
      <h3 id="modal-h">Your gapping chart</h3>
      <button type="button" class="so-mx" id="modalX" aria-label="Close">&times;</button>
    </div>
    <div class="so-mbody">
      <p style="font-size:14px;line-height:1.55;margin-bottom:15px">Your chart is ready now. Print it or
        save it as a PDF straight from your browser &mdash; it will not be emailed to you and nothing is
        uploaded to build it.</p>
      <button type="button" class="so-go" id="printBtn" style="width:100%">Print / save as PDF</button>

      <hr style="margin:20px 0;border:0;border-top:2px solid var(--line)">

      <p style="font-size:14px;line-height:1.55;margin-bottom:13px"><b>Want The Card?</b> Unfiltered
        player ratings and the stories PR reps tried to kill, every Friday. Optional &mdash; your chart does
        not depend on it.</p>
      <form id="soForm" novalidate>
        <label for="soEmail">Email address</label>
        <input type="email" id="soEmail" placeholder="you@email.com" autocomplete="email">
        <button type="submit" class="so-go" id="soSubmit" style="width:100%;margin-top:10px">Join the list</button>
      </form>
      <div class="so-msg" id="soMsg" role="status"></div>
    </div>
  </div>

  <!-- printed output only -->
  <div id="printArea" aria-hidden="true">
    <h1>Bag Gapping Chart</h1>
    <p class="sub" id="printSub"></p>
    <div id="printChart"></div>
    <div id="printTable"></div>
    <p class="foot">Median carry distances measured on the range with GOLFRAW &mdash; The Standing Order.
      golfraw.com/tools-standing-order</p>
  </div>
'''

# ------------------------------------------------------------------ tool JS

SCRIPT = r'''  <script>
    var $ = function (id) { return document.getElementById(id); };

    /* ==================== CONSTANTS ==================== */
    var DEFAULT_CLUBS = ['Driver', '3-Wood', '5-Wood', '3-Hybrid', '4-Hybrid', '5-iron', '6-iron',
      '7-iron', '8-iron', '9-iron', 'PW', 'GW', 'SW', 'LW'];
    var MIN_SHOTS = 5;        /* below this the median is not worth trusting */
    var GOOD_SHOTS = 8;       /* where the 80% band starts to mean something */
    var GAP_HOLE = 25;        /* median-to-median gap above this = no club for it */
    var GAP_DUP = 8;          /* below this = two clubs doing one job */
    var MAX_SHOTS = 50;
    var MAX_CARRY = 500;

    /* ==================== STATISTICS ==================== */
    /* Medians and percentiles throughout, never means: one thinned range ball
       moves an average by several yards and invents a gap that is not there. */

    function sortNum(a) { return a.slice().sort(function (x, y) { return x - y; }); }

    /* Linear-interpolated percentile on an already-sorted array. */
    function pct(sorted, p) {
      var n = sorted.length;
      if (!n) return null;
      if (n === 1) return sorted[0];
      var idx = (n - 1) * p;
      var lo = Math.floor(idx), hi = Math.ceil(idx);
      if (lo === hi) return sorted[lo];
      return sorted[lo] + (sorted[hi] - sorted[lo]) * (idx - lo);
    }

    function median(sorted) { return pct(sorted, 0.5); }

    /* Sample standard deviation (n-1): these shots are a sample of the swing,
       not the whole population of it. Undefined for a single shot. */
    function stdev(a) {
      var n = a.length;
      if (n < 2) return null;
      var sum = 0, i;
      for (i = 0; i < n; i++) sum += a[i];
      var m = sum / n, acc = 0;
      for (i = 0; i < n; i++) acc += (a[i] - m) * (a[i] - m);
      return Math.sqrt(acc / (n - 1));
    }

    function r1(x) { return x === null ? null : Math.round(x * 10) / 10; }
    function r0(x) { return x === null ? null : Math.round(x); }

    /* One club's shots -> everything the page reports about it. */
    function describe(name, shots) {
      var s = sortNum(shots);
      return {
        name: name,
        n: s.length,
        shots: s,
        median: median(s),
        sd: stdev(s),
        p10: pct(s, 0.10),
        p90: pct(s, 0.90),
        min: s.length ? s[0] : null,
        max: s.length ? s[s.length - 1] : null,
        reliable: s.length >= MIN_SHOTS,
        solid: s.length >= GOOD_SHOTS
      };
    }

    /* Adjacent-club gaps, longest club first. */
    function analyse(clubs) {
      var rows = [];
      for (var i = 0; i < clubs.length; i++) {
        if (clubs[i].shots.length) rows.push(describe(clubs[i].name, clubs[i].shots));
      }
      rows.sort(function (a, b) { return b.median - a.median; });
      for (var j = 0; j < rows.length; j++) {
        rows[j].gapToNext = (j < rows.length - 1) ? rows[j].median - rows[j + 1].median : null;
      }
      return rows;
    }

    function verdicts(rows) {
      var out = [];
      for (var i = 0; i < rows.length - 1; i++) {
        var a = rows[i], b = rows[i + 1], gap = a.median - b.median;
        if (!a.reliable || !b.reliable) continue;
        if (gap > GAP_HOLE) {
          out.push({ kind: 'gap', title: 'Hole in the bag',
            text: r0(gap) + ' yards between your ' + a.name + ' (' + r0(a.median) + ') and your ' +
              b.name + ' (' + r0(b.median) + '). Anything landing in between has no club for it.' });
        } else if (gap < GAP_DUP) {
          out.push({ kind: 'dup', title: 'Two clubs, one job',
            text: a.name + ' and ' + b.name + ' are ' + r0(gap) + ' yards apart. One of them is ' +
              'spending a slot for nothing &mdash; the shorter one is the usual cut.' });
        }
        /* Bands can overlap even when the medians look respectably apart. */
        if (gap >= GAP_DUP && gap <= GAP_HOLE && a.solid && b.solid && a.p10 < b.p90) {
          out.push({ kind: 'dup', title: 'Overlapping dispersion',
            text: a.name + ' and ' + b.name + ' are ' + r0(gap) + ' yards apart on the median, but ' +
              'their 80% bands overlap. On any given swing you cannot reliably tell which one you hit.' });
        }
      }
      if (!out.length && rows.length > 1) {
        out.push({ kind: 'ok', title: 'Ladder looks clean',
          text: 'No gaps over ' + GAP_HOLE + ' yards and no two clubs inside ' + GAP_DUP +
            ' yards of each other. Nothing in this session needs changing.' });
      }
      return out;
    }

    /* ==================== SVG DISPERSION CHART ==================== */
    /* Hand-built SVG: no chart library, nothing to download, nothing to parse
       before the page is usable. */
    function chartSvg(rows) {
      if (!rows.length) return '';
      var W = 560, rowH = 27, padT = 24, padB = 26;
      var labelW = 88, valW = 46;
      var x0 = labelW, x1 = W - valW;
      var H = padT + rows.length * rowH + padB;

      var lo = Infinity, hi = -Infinity;
      for (var i = 0; i < rows.length; i++) {
        lo = Math.min(lo, rows[i].min);
        hi = Math.max(hi, rows[i].max);
      }
      var span = Math.max(10, hi - lo);
      lo -= span * 0.06; hi += span * 0.06;
      var sx = function (v) { return x0 + (v - lo) / (hi - lo) * (x1 - x0); };

      var p = [];
      p.push('<svg class="so-chart" viewBox="0 0 ' + W + ' ' + H + '" role="img" ' +
        'aria-label="Carry distance dispersion by club" xmlns="http://www.w3.org/2000/svg">');
      p.push('<title>Carry distance dispersion by club</title>');

      /* axis ticks every 25 yards */
      var t0 = Math.ceil(lo / 25) * 25;
      for (var t = t0; t <= hi; t += 25) {
        p.push('<line x1="' + sx(t).toFixed(1) + '" y1="' + (padT - 8) + '" x2="' + sx(t).toFixed(1) +
          '" y2="' + (H - padB + 4) + '" stroke="#DADDD4" stroke-width="1"/>');
        p.push('<text x="' + sx(t).toFixed(1) + '" y="' + (H - padB + 17) + '" font-size="9.5" ' +
          'fill="#5B665E" text-anchor="middle" font-family="IBM Plex Mono, monospace">' + t + '</text>');
      }

      for (var r = 0; r < rows.length; r++) {
        var row = rows[r], y = padT + r * rowH + rowH / 2;
        var dim = row.reliable ? '' : ' opacity="0.45"';
        p.push('<g' + dim + '>');
        /* full range whisker */
        p.push('<line x1="' + sx(row.min).toFixed(1) + '" y1="' + y + '" x2="' + sx(row.max).toFixed(1) +
          '" y2="' + y + '" stroke="#101511" stroke-width="1"/>');
        p.push('<line x1="' + sx(row.min).toFixed(1) + '" y1="' + (y - 4) + '" x2="' + sx(row.min).toFixed(1) +
          '" y2="' + (y + 4) + '" stroke="#101511" stroke-width="1"/>');
        p.push('<line x1="' + sx(row.max).toFixed(1) + '" y1="' + (y - 4) + '" x2="' + sx(row.max).toFixed(1) +
          '" y2="' + (y + 4) + '" stroke="#101511" stroke-width="1"/>');
        /* 80% band */
        var bx = sx(row.p10), bw = Math.max(2, sx(row.p90) - sx(row.p10));
        p.push('<rect x="' + bx.toFixed(1) + '" y="' + (y - 7) + '" width="' + bw.toFixed(1) +
          '" height="14" fill="#14402A" fill-opacity="0.18" stroke="#14402A" stroke-width="1"/>');
        /* median */
        p.push('<line x1="' + sx(row.median).toFixed(1) + '" y1="' + (y - 9) + '" x2="' +
          sx(row.median).toFixed(1) + '" y2="' + (y + 9) + '" stroke="#E03E2D" stroke-width="2.5"/>');
        /* labels */
        p.push('<text x="' + (labelW - 8) + '" y="' + (y + 3.5) + '" font-size="10.5" fill="#101511" ' +
          'text-anchor="end" font-family="Archivo, system-ui, sans-serif" font-weight="700">' +
          esc(row.name) + '</text>');
        p.push('<text x="' + (W - 4) + '" y="' + (y + 3.5) + '" font-size="10.5" fill="#101511" ' +
          'text-anchor="end" font-family="IBM Plex Mono, monospace" font-weight="600">' +
          r0(row.median) + '</text>');
        p.push('</g>');
      }
      p.push('</svg>');
      return p.join('');
    }

    function esc(s) {
      return String(s === null || s === undefined ? '' : s)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;')
        .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    /* ==================== SESSION STATE ==================== */
    /* Resolved in boot(), never at parse time: the locker scripts are deferred,
       so window.GolfrawLocker does not exist while this inline script runs.
       Capturing it here would pin L to null and silently discard every shot. */
    var L = null;
    var session = { id: null, label: '', clubs: [], startedAt: 0 };
    var current = null;      /* selected club name */
    var typed = '';
    var writeChain = Promise.resolve();

    function clubEntry(name, make) {
      for (var i = 0; i < session.clubs.length; i++) {
        if (session.clubs[i].name === name) return session.clubs[i];
      }
      if (!make) return null;
      var e = { name: name, shots: [] };
      session.clubs.push(e);
      return e;
    }

    /* Writes are chained rather than fired in parallel: two taps in quick
       succession must not race each other into the same session record. */
    function persist() {
      if (!L) return Promise.resolve();
      writeChain = writeChain.then(function () {
        return L.saveSession(session);
      })['catch'](function () {
        setState('Could not save to this device — the session still works, but it will not survive a reload.');
      });
      return writeChain;
    }

    function setState(msg) {
      var el = $('saveState');
      if (el) el.textContent = msg;
    }

    /* ==================== CLUB STRIP ==================== */
    var clubNames = DEFAULT_CLUBS.slice();

    function renderClubs() {
      var host = $('clubStrip'), html = [];
      for (var i = 0; i < clubNames.length; i++) {
        var name = clubNames[i];
        var e = clubEntry(name, false);
        var n = e ? e.shots.length : 0;
        html.push('<button type="button" class="so-club" data-club="' + esc(name) + '" ' +
          'aria-pressed="' + (name === current ? 'true' : 'false') + '">' + esc(name) +
          (n ? '<span class="n">' + n + '</span>' : '') + '</button>');
      }
      host.innerHTML = html.join('');
    }

    function selectClub(name) {
      current = name;
      typed = '';
      renderClubs();
      renderShots();
      renderReadout();
      var btn = $('clubStrip').querySelector('[data-club="' + name.replace(/"/g, '\\"') + '"]');
      if (btn && btn.scrollIntoView) btn.scrollIntoView({ block: 'nearest', inline: 'center' });
    }

    /* ==================== KEYPAD ==================== */
    function renderReadout() {
      var el = $('readout');
      el.textContent = typed === '' ? '0' : typed;
      el.className = 'val' + (typed === '' ? ' ghost' : '');
      var v = parseInt(typed, 10);
      $('logBtn').disabled = !(current && typed !== '' && v >= 1 && v <= MAX_CARRY);
    }

    function key(k) {
      if (k === 'clear') { typed = ''; }
      else if (k === 'del') { typed = typed.slice(0, -1); }
      else if (typed.length < 3) {
        if (typed === '' && k === '0') return;   /* no leading zero */
        typed += k;
      }
      renderReadout();
    }

    /* ==================== LOG / DELETE ==================== */
    function logShot() {
      var v = parseInt(typed, 10);
      if (!current || !isFinite(v) || v < 1 || v > MAX_CARRY) return;
      var e = clubEntry(current, true);
      if (e.shots.length >= MAX_SHOTS) {
        setState('That is ' + MAX_SHOTS + ' shots with the ' + current + ' — more than enough. Move on.');
        return;
      }
      e.shots.push(v);
      typed = '';
      renderClubs(); renderShots(); renderReadout(); renderBar();
      setState('Saved on this device.');
      persist();
    }

    function delShot(idx) {
      var e = clubEntry(current, false);
      if (!e) return;
      e.shots.splice(idx, 1);
      if (!e.shots.length) {
        for (var i = 0; i < session.clubs.length; i++) {
          if (session.clubs[i] === e) { session.clubs.splice(i, 1); break; }
        }
      }
      renderClubs(); renderShots(); renderBar();
      persist();
    }

    function renderShots() {
      var host = $('shotList');
      var e = current ? clubEntry(current, false) : null;
      if (!e || !e.shots.length) {
        host.innerHTML = '<span class="so-none">' +
          (current ? 'No shots logged with the ' + esc(current) + ' yet.' : 'Pick a club to start.') + '</span>';
        return;
      }
      var html = [];
      for (var i = 0; i < e.shots.length; i++) {
        html.push('<span class="so-shot">' + e.shots[i] +
          '<button type="button" data-del="' + i + '" aria-label="Remove the ' + e.shots[i] +
          ' yard shot">&times;</button></span>');
      }
      host.innerHTML = html.join('');
    }

    function renderBar() {
      var clubs = 0, shots = 0;
      for (var i = 0; i < session.clubs.length; i++) {
        if (session.clubs[i].shots.length) { clubs++; shots += session.clubs[i].shots.length; }
      }
      $('sesClubs').textContent = clubs;
      $('sesShots').textContent = shots;
      $('goBtn').disabled = clubs < 2;
      $('goBtn').title = clubs < 2 ? 'Log at least two clubs to see the gaps between them' : '';
    }

    /* ==================== RESULTS ==================== */
    var lastRows = [];

    function showResults() {
      var rows = analyse(session.clubs);
      lastRows = rows;
      if (rows.length < 2) return;

      $('chartHost').innerHTML = chartSvg(rows);

      var body = [];
      for (var i = 0; i < rows.length; i++) {
        var r = rows[i];
        var band = r.n >= 2 ? (r0(r.p10) + '–' + r0(r.p90)) : '—';
        var sd = r.sd === null ? '—' : ('±' + r1(r.sd));
        var gap = r.gapToNext === null ? '—' : r0(r.gapToNext);
        body.push('<tr>' +
          '<td>' + esc(r.name) + (r.reliable ? '' :
            ' <span class="thin" title="Fewer than ' + MIN_SHOTS + ' shots">(thin)</span>') + '</td>' +
          '<td>' + r.n + '</td>' +
          '<td><b>' + r0(r.median) + '</b></td>' +
          '<td class="thin">' + sd + '</td>' +
          '<td class="thin">' + band + '</td>' +
          '<td>' + gap + '</td>' +
        '</tr>');
      }
      $('statBody').innerHTML = body.join('');

      var v = verdicts(rows), vh = [];
      for (var j = 0; j < v.length; j++) {
        vh.push('<div class="so-flag ' + v[j].kind + '"><div><b>' + v[j].title + '</b>' + v[j].text + '</div></div>');
      }
      var thin = 0;
      for (var k = 0; k < rows.length; k++) if (!rows[k].reliable) thin++;
      if (thin) {
        vh.push('<div class="so-flag dup"><div><b>Not enough shots</b>' + thin +
          ' club' + (thin > 1 ? 's have' : ' has') + ' fewer than ' + MIN_SHOTS +
          ' shots logged. Those medians are shown greyed out and are left out of the gap checks ' +
          'above, because at that sample size one bad strike decides the answer.</div></div>');
      }
      $('verdicts').innerHTML = vh.join('');

      $('results').hidden = false;
      $('results').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    /* ==================== SYNC TO THE LOCKER BAG ==================== */
    /* Median carries replace the bag's distances; usage and trust scores the
       reader set in the Bag Audit are preserved, because this session says
       nothing about either. */
    function saveToBag() {
      if (!L || !lastRows.length) return;
      L.getActiveBag().then(function (bag) {
        var existing = (bag && bag.clubs) || [];
        var byName = {};
        for (var i = 0; i < existing.length; i++) byName[existing[i].name.toLowerCase()] = existing[i];

        var clubs = [], used = {};
        for (var j = 0; j < lastRows.length && clubs.length < 14; j++) {
          var r = lastRows[j];
          if (!r.reliable) continue;               /* never overwrite with a guess */
          var prev = byName[r.name.toLowerCase()];
          clubs.push({
            name: r.name.slice(0, 40),
            carry: r0(r.median),
            usage: prev ? prev.usage : null,
            conf: prev ? prev.conf : 3
          });
          used[r.name.toLowerCase()] = true;
        }
        /* Keep clubs that were not part of this session. */
        for (var k = 0; k < existing.length && clubs.length < 14; k++) {
          if (!used[existing[k].name.toLowerCase()]) clubs.push(existing[k]);
        }
        return L.saveActiveBagClubs(clubs).then(function () {
          msg('resMsg', clubs.length + ' clubs written to your bag. The Bag Audit and the locker ' +
            'drawer will show these numbers now.', 'good');
        });
      })['catch'](function (e) {
        msg('resMsg', (e && e.message) || 'Could not write to your bag.', 'bad');
      });
    }

    function msg(id, text, kind) {
      var el = $(id);
      if (!el) return;
      el.className = 'so-msg on ' + (kind || '');
      el.innerHTML = text;
    }

    /* ==================== CHART MODAL ==================== */
    var lastFocus = null;

    function buildPrint() {
      var d = new Date();
      $('printSub').textContent = 'Median carry distances measured ' + d.toLocaleDateString() +
        ' · ' + lastRows.length + ' clubs';
      $('printChart').innerHTML = chartSvg(lastRows);
      var rowsHtml = ['<table><thead><tr><th>Club</th><th>Shots</th><th>Median</th>' +
        '<th>Spread</th><th>80% band</th><th>Gap</th></tr></thead><tbody>'];
      for (var i = 0; i < lastRows.length; i++) {
        var r = lastRows[i];
        rowsHtml.push('<tr><td>' + esc(r.name) + '</td><td>' + r.n + '</td><td>' + r0(r.median) +
          '</td><td>' + (r.sd === null ? '—' : '±' + r1(r.sd)) + '</td><td>' +
          (r.n >= 2 ? r0(r.p10) + '–' + r0(r.p90) : '—') + '</td><td>' +
          (r.gapToNext === null ? '—' : r0(r.gapToNext)) + '</td></tr>');
      }
      rowsHtml.push('</tbody></table>');
      $('printTable').innerHTML = rowsHtml.join('');
    }

    function openModal() {
      if (!lastRows.length) return;
      buildPrint();
      lastFocus = document.activeElement;
      $('scrim').classList.add('on');
      $('modal').hidden = false;
      $('modal').classList.add('on');
      $('printBtn').focus();
      document.body.style.overflow = 'hidden';
    }

    function closeModal() {
      $('scrim').classList.remove('on');
      $('modal').classList.remove('on');
      $('modal').hidden = true;
      document.body.style.overflow = '';
      if (lastFocus && lastFocus.focus) { try { lastFocus.focus(); } catch (e) { } }
    }

    /* ==================== BOOT ==================== */
    function boot() {
      L = window.GolfrawLocker || null;
      renderClubs();
      renderShots();
      renderReadout();
      renderBar();

      $('clubStrip').addEventListener('click', function (e) {
        var b = e.target.closest ? e.target.closest('[data-club]') : null;
        if (b) selectClub(b.getAttribute('data-club'));
      });
      $('pad').addEventListener('click', function (e) {
        var b = e.target.closest ? e.target.closest('[data-k]') : null;
        if (b) key(b.getAttribute('data-k'));
      });
      $('logBtn').addEventListener('click', logShot);
      $('shotList').addEventListener('click', function (e) {
        var b = e.target.closest ? e.target.closest('[data-del]') : null;
        if (b) delShot(parseInt(b.getAttribute('data-del'), 10));
      });
      $('goBtn').addEventListener('click', showResults);
      $('saveBag').addEventListener('click', saveToBag);
      $('chartBtn').addEventListener('click', openModal);
      $('modalX').addEventListener('click', closeModal);
      $('scrim').addEventListener('click', closeModal);
      $('printBtn').addEventListener('click', function () { window.print(); });
      document.addEventListener('keydown', function (e) {
        if (!$('modal').classList.contains('on')) return;
        if (e.key === 'Escape') { e.preventDefault(); closeModal(); }
      });

      /* A physical keyboard should work too — this is not mobile-only. */
      document.addEventListener('keydown', function (e) {
        if ($('modal').classList.contains('on')) return;
        var t = e.target.tagName;
        if (t === 'INPUT' || t === 'TEXTAREA') return;
        if (e.key >= '0' && e.key <= '9') { key(e.key); }
        else if (e.key === 'Backspace') { e.preventDefault(); key('del'); }
        else if (e.key === 'Enter' && !$('logBtn').disabled) { e.preventDefault(); logShot(); }
      });

      /* Newsletter opt-in — the same HubSpot list as the rest of the site.
         Deliberately separate from the chart: the chart is already downloadable
         and never depends on handing over an address. */
      $('soForm').addEventListener('submit', function (e) {
        e.preventDefault();
        var email = $('soEmail').value.replace(/^\s+|\s+$/g, '');
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) {
          msg('soMsg', 'That does not look like an email address.', 'bad');
          $('soEmail').focus();
          return;
        }
        var btn = $('soSubmit');
        btn.disabled = true; btn.textContent = 'Sending…';
        fetch('https://api.hsforms.com/submissions/v3/integration/submit/148744463/f9b9028c-b648-4563-9b01-2b53b3caae13', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ fields: [{ name: 'email', value: email }] })
        }).then(function (r) {
          if (!r.ok) throw new Error('rejected');
          $('soForm').style.display = 'none';
          msg('soMsg', 'You are on the list.', 'good');
        })['catch'](function () {
          btn.disabled = false; btn.textContent = 'Join the list';
          msg('soMsg', 'Could not connect. Try again in a moment.', 'bad');
        });
      });

      /* Restore today's session and read the reader's real club names. */
      if (!L) { setState('Storage is unavailable in this browser, so this session will not be saved.'); return; }
      L.ready().then(function () {
        return Promise.all([L.getOrStartSession(), L.getActiveBag(), L.getProfile()]);
      }).then(function (res) {
        session = res[0];
        if (!session.clubs) session.clubs = [];
        /* The reader's own club names come first, then any standard club they
           have not named yet. Merging rather than replacing matters: a bag
           holding three clubs must not leave the strip unable to log a driver. */
        var bag = res[1];
        if (bag && bag.clubs && bag.clubs.length) {
          var names = [], seen = {};
          for (var i = 0; i < bag.clubs.length; i++) {
            var nm = bag.clubs[i].name;
            if (nm && !seen[nm.toLowerCase()]) { seen[nm.toLowerCase()] = true; names.push(nm); }
          }
          for (var d = 0; d < DEFAULT_CLUBS.length; d++) {
            if (!seen[DEFAULT_CLUBS[d].toLowerCase()]) names.push(DEFAULT_CLUBS[d]);
          }
          if (names.length) clubNames = names;
        }
        /* Any club logged earlier today must appear even if it left the bag. */
        for (var j = 0; j < session.clubs.length; j++) {
          if (clubNames.indexOf(session.clubs[j].name) === -1) clubNames.push(session.clubs[j].name);
        }
        if (res[2] && res[2].units === 'meters') $('unitLabel').textContent = 'meters carry';
        renderClubs(); renderShots(); renderBar();
        var logged = 0;
        for (var k = 0; k < session.clubs.length; k++) logged += session.clubs[k].shots.length;
        setState(logged
          ? 'Picked up where you left off — ' + logged + ' shots already logged today.'
          : 'Every shot saves to this device as you tap. Close the tab and come back — the session will still be here.');
      })['catch'](function () {
        setState('Could not open local storage, so this session will not be saved.');
      });

      if (L) {
        L.subscribe(function (kind) {
          if (kind === 'clear' || kind === 'import') window.location.reload();
        });
      }
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
    else boot();
  </script>
'''

# ------------------------------------------------------------------- assemble

TAIL = '''  <script>window.__gr_consent=true;window.__gr_ads=false;</script>
'''


def main():
    p = shell_parts()
    doc = '\n'.join([
        rewrite_meta(p['head_top']),
        JSONLD,
        p['head_tail'].replace('</head>', STYLE + '</head>'),
        p['body_open'],
        MAIN,
        p['footer'],
        '',
        '  <script>',
        p['nav_script'].split('<script>', 1)[1] if '<script>' in p['nav_script'] else '',
        '  </script>',
        SCRIPT,
        p['gtag'],
        TAIL + '</body>',
        '',
        '</html>',
    ])
    io.open(OUT, 'w', encoding='utf-8').write(doc)
    print('  wrote %s (%d bytes)' % (os.path.basename(OUT), len(doc.encode('utf-8'))))
    return 0


if __name__ == '__main__':
    sys.exit(main())
