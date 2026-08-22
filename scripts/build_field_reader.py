#!/usr/bin/env python3
"""Generate tools-field-reader.html from the shared tool-page shell.

Re-runnable: rewrites the file wholesale. Edits to the HTML are destroyed.
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHELL = os.path.join(ROOT, 'tools-bag-audit.html')
OUT = os.path.join(ROOT, 'tools-field-reader.html')

SITE = 'https://www.golfraw.com'
SLUG = 'tools-field-reader'
TITLE = 'Golf Field Reader: Course Fit Model &amp; Rankings | GolfRaw'
DESC = ('Rank any golf field by course fit. Adjust distance, approach, short game and putting demands '
        'to reveal which players are best suited to the week.')
OG_IMAGE = SITE + '/public/raw-golf-practice.webp'


def shell_parts():
    lines = io.open(SHELL, encoding='utf-8').read().split('\n')
    return {
        'head_top': '\n'.join(lines[0:45]),
        'head_tail': '\n'.join(lines[200:420]),
        'body_open': '\n'.join(lines[421:442]),
        'footer': '\n'.join(lines[639:658]),
        'nav_script': '\n'.join(lines[662:677]),
        'gtag': '\n'.join(lines[1171:1177]),
    }


PREMIUM_LINK = '  <link rel="stylesheet" href="/public/tool-premium.css?v=2">\n'


def rewrite_meta(s):
    s = re.sub(r'<title>.*?</title>', '<title>%s</title>' % TITLE, s, flags=re.S)
    for pat, val in [
        (r'(<meta name="description" content=")[^"]*(")', DESC),
        (r'(<meta property="og:title" content=")[^"]*(")', TITLE),
        (r'(<meta property="og:description" content=")[^"]*(")', DESC),
        (r'(<meta property="og:image" content=")[^"]*(")', OG_IMAGE),
        (r'(<meta name="twitter:title" content=")[^"]*(")', TITLE),
        (r'(<meta name="twitter:description" content=")[^"]*(")', DESC),
        (r'(<meta name="twitter:image" content=")[^"]*(")', OG_IMAGE),
    ]:
        s = re.sub(pat, lambda m, v=val: m.group(1) + v + m.group(2), s)
    s = re.sub(r'(<link rel="canonical" href=")[^"]*(")', r'\g<1>%s/%s\g<2>' % (SITE, SLUG), s)
    s = re.sub(r'(<meta property="og:url" content=")[^"]*(")', r'\g<1>%s/%s\g<2>' % (SITE, SLUG), s)
    return s


JSONLD = '''  <!-- ============ STRUCTURED DATA ============ -->
  <script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "The Field Reader",
  "alternateName": "Golf Course Fit Model",
  "url": "%(site)s/%(slug)s",
  "applicationCategory": "SportsApplication",
  "operatingSystem": "Any browser",
  "browserRequirements": "Requires JavaScript",
  "description": "%(desc)s",
  "offers": { "@type": "Offer", "price": "0", "priceCurrency": "USD" },
  "featureList": [
    "Weight distance, approach, short game and putting to match the week",
    "The field re-ranks live as the weights move",
    "Fit score out of 100 with the reason behind it",
    "Lock four picks and keep them on your device"
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
    { "@type": "ListItem", "position": 3, "name": "The Field Reader", "item": "%(site)s/%(slug)s" }
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
      "name": "What is course fit in golf?",
      "acceptedAnswer": { "@type": "Answer", "text": "Course fit is the idea that a golf course rewards particular skills more than others. A long par 71 with small greens asks for approach play, a short course with thick rough asks for accuracy and scrambling, and the same player can be a contender at one and miss the cut at the other. A fit model weights each skill by how much the week demands it." }
    },
    {
      "@type": "Question",
      "name": "Does putting surface really matter for course fit?",
      "acceptedAnswer": { "@type": "Answer", "text": "It matters more than most other single factors. Bermuda grain, Poa annua bumpiness in the afternoon and the true roll of bentgrass all reward different reads and different stroke types. Players with a genuine surface preference show it in their putting numbers, which is why this model splits putting by surface rather than treating it as one skill." }
    },
    {
      "@type": "Question",
      "name": "Are the players in this tool real?",
      "acceptedAnswer": { "@type": "Answer", "text": "The list shipped with the tool is made of archetypes, not real golfers, and each one is labelled as an archetype on the board. They exist so the model works out of the box. A real field can be loaded by editing the tournament feed with real, sourced strokes-gained numbers." }
    },
    {
      "@type": "Question",
      "name": "Is this a betting tool?",
      "acceptedAnswer": { "@type": "Answer", "text": "No. It is a course fit model that shows which skills a week rewards and which players in the loaded field have them. It does not price markets, take stakes or predict winners, and a fit score is not a probability. Golf is won by whoever plays best over four days, not by whoever fits the course best on Tuesday." }
    }
  ]
}
  </script>
''' % {'site': SITE, 'slug': SLUG, 'desc': DESC.replace('—', '-')}


STYLE = '''<style>
    /* ---- The Field Reader ------------------------------------------------
       Sliders are the whole interaction, so they get a 44px thumb and a live
       numeric readout. The board below them re-ranks on every input event. */
    .fr-wrap { max-width: 660px; margin: 0 auto }

    .fr-course { border: 3px solid var(--ink); background: var(--ink); color: #fff; padding: 16px 17px;
      margin-bottom: 18px }
    .fr-course .ev { font-size: 10.5px; font-weight: 800; letter-spacing: .13em; text-transform: uppercase;
      color: var(--flag); margin-bottom: 7px }
    .fr-course h3 { font: 900 21px/1.15 'Archivo', system-ui, sans-serif; letter-spacing: -.02em;
      margin-bottom: 5px }
    .fr-course .meta { font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: rgba(255,255,255,.62);
      margin-bottom: 10px }
    .fr-course p { font-size: 14px; line-height: 1.55; color: rgba(255,255,255,.85) }
    .fr-sample { display: inline-block; margin-top: 11px; padding: 5px 9px; border: 2px solid var(--flag);
      color: var(--flag); font: 800 10px/1.3 'Archivo', system-ui, sans-serif; letter-spacing: .08em;
      text-transform: uppercase }

    .fr-sliders { border: 2px solid var(--ink); background: var(--white); padding: 15px 16px; margin-bottom: 14px }
    .fr-s { margin-bottom: 16px }
    .fr-s:last-child { margin-bottom: 0 }
    .fr-s .row { display: flex; justify-content: space-between; align-items: baseline; gap: 10px; margin-bottom: 6px }
    .fr-s label { font-size: 11.5px; font-weight: 800; letter-spacing: .06em; text-transform: uppercase;
      color: var(--ink) }
    .fr-s .val { font-family: 'IBM Plex Mono', monospace; font-weight: 600; font-size: 14px }
    .fr-s .hint { font-size: 12px; color: var(--grey); line-height: 1.45; margin-top: 5px }

    input[type=range].fr-range { -webkit-appearance: none; appearance: none; width: 100%; height: 44px;
      background: transparent; cursor: pointer; margin: 0; display: block }
    input[type=range].fr-range:focus { outline: none }
    input[type=range].fr-range:focus-visible::-webkit-slider-thumb { outline: 3px solid var(--flag); outline-offset: 2px }
    input[type=range].fr-range:focus-visible::-moz-range-thumb { outline: 3px solid var(--flag); outline-offset: 2px }
    input[type=range].fr-range::-webkit-slider-runnable-track { height: 8px; background: var(--line);
      border: 2px solid var(--ink) }
    input[type=range].fr-range::-moz-range-track { height: 8px; background: var(--line); border: 2px solid var(--ink) }
    input[type=range].fr-range::-webkit-slider-thumb { -webkit-appearance: none; appearance: none;
      width: 30px; height: 30px; margin-top: -13px; background: var(--flag); border: 3px solid var(--ink) }
    input[type=range].fr-range::-moz-range-thumb { width: 24px; height: 24px; background: var(--flag);
      border: 3px solid var(--ink); border-radius: 0 }

    .fr-surface { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px }
    .fr-surface button { flex: 1; min-width: 84px; min-height: 44px; background: var(--white);
      border: 2px solid var(--ink); font: 800 11.5px/1 'Archivo', system-ui, sans-serif;
      letter-spacing: .04em; text-transform: uppercase; cursor: pointer; color: var(--ink) }
    .fr-surface button[aria-pressed="true"] { background: var(--ink); color: #fff }
    .fr-surface button:focus-visible { outline: 3px solid var(--flag); outline-offset: 2px }

    .fr-acts { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px }
    .fr-go { min-height: 48px; padding: 0 16px; background: var(--ink); color: #fff; border: 2px solid var(--ink);
      font: 800 11.5px/1 'Archivo', system-ui, sans-serif; letter-spacing: .06em; text-transform: uppercase;
      cursor: pointer; transition: background .15s }
    .fr-go:hover { background: var(--fairway); border-color: var(--fairway) }
    .fr-go:focus-visible { outline: 3px solid var(--flag); outline-offset: 3px }
    .fr-go.ghost { background: var(--white); color: var(--ink) }
    .fr-go.ghost:hover { background: var(--ink); color: #fff }
    .fr-go[disabled] { background: var(--line); border-color: var(--line); color: var(--grey); cursor: not-allowed }

    /* board */
    .fr-board { display: grid; gap: 8px }
    .fr-card { display: grid; grid-template-columns: 42px 1fr auto; gap: 11px; align-items: start;
      border: 2px solid var(--ink); background: var(--white); padding: 12px 13px }
    .fr-card.picked { border-left: 1px solid var(--flag) }
    .fr-rank { font: 600 20px/1 'IBM Plex Mono', monospace; color: var(--grey); padding-top: 2px }
    .fr-card.top .fr-rank { color: var(--flag) }
    .fr-name { font: 800 15px/1.2 'Archivo', system-ui, sans-serif; margin-bottom: 3px }
    .fr-tag { display: inline-block; margin-left: 6px; padding: 2px 5px; border: 1px solid var(--grey);
      font: 600 8.5px/1.35 'IBM Plex Mono', monospace; letter-spacing: .07em; text-transform: uppercase;
      color: var(--grey); vertical-align: 2px }
    .fr-why { font-size: 12.8px; line-height: 1.45; color: var(--grey) }
    .fr-why b { color: var(--ink); font-weight: 700 }
    .fr-right { text-align: right; display: flex; flex-direction: column; align-items: flex-end; gap: 6px }
    .fr-score { font: 600 22px/1 'IBM Plex Mono', monospace; letter-spacing: -.02em }
    .fr-pick { min-width: 44px; min-height: 44px; background: var(--white); border: 2px solid var(--ink);
      font: 800 10px/1 'Archivo', system-ui, sans-serif; letter-spacing: .05em; text-transform: uppercase;
      cursor: pointer; color: var(--ink); padding: 0 8px }
    .fr-pick[aria-pressed="true"] { background: var(--flag); border-color: var(--flag); color: #fff }
    .fr-pick:focus-visible { outline: 3px solid var(--flag); outline-offset: 2px }
    .fr-bar { height: 5px; background: var(--line); width: 68px }
    .fr-bar span { display: block; height: 100%; background: var(--fairway) }

    .fr-msg { margin-top: 12px; padding: 10px 12px; border: 2px solid var(--ink); background: var(--white);
      font-size: 13px; font-weight: 600; line-height: 1.45; display: none }
    .fr-msg.on { display: block }
    .fr-msg.bad { border-color: var(--flag); color: var(--flag) }
    .fr-msg.good { border-color: var(--fairway); color: var(--fairway) }
    .fr-note { font-size: 12.5px; color: var(--grey); line-height: 1.55; margin-top: 12px }
    .fr-sr { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden;
      clip: rect(0 0 0 0); white-space: nowrap; border: 0 }

    @media (prefers-reduced-motion: reduce) { .fr-go, .fr-pick { transition: none } }
    @media (max-width: 380px) {
      .fr-card { grid-template-columns: 32px 1fr; }
      .fr-right { grid-column: 1 / -1; flex-direction: row; align-items: center;
        justify-content: space-between; width: 100%; margin-top: 4px }
      .fr-course h3 { font-size: 19px }
    }
  </style>
'''

MAIN = '''
  <div class="hub-hero">
    <div class="wrap">
      <div class="eyebrow">RAWGOLF &middot; TOOLS</div>
      <h1>The Field Reader</h1>
      <p>Every course asks a different question. Some weeks it is length, some weeks it is a wedge to
        fifteen feet, and some weeks it is whether you can read grainy Bermuda at five in the afternoon.
        Set what this week actually demands and watch the field reorder itself. Runs entirely in your
        browser &mdash; move a slider, the board moves with it.</p>
    </div>
  </div>

  <div class="tool-body">
    <div class="wrap">

      <section class="answer-block" aria-labelledby="aeo-q">
        <div class="ab-tag">The short answer</div>
        <h2 id="aeo-q">What is course fit in golf?</h2>
        <blockquote>Course fit is the idea that a course <b>rewards particular skills more than others</b>.
          A long par 71 with small greens pays for approach play; a short course with heavy rough pays for
          accuracy and scrambling. Weight each skill by how much the week demands it, score every player
          against those weights, and the ranking that falls out is the fit.</blockquote>
      </section>

      <section class="panel" aria-labelledby="board-h">
        <h2 id="board-h">Set the week</h2>
        <div class="fr-wrap">

          <div class="fr-course" id="courseCard"></div>

          <div class="fr-sliders">
            <div class="fr-s">
              <div class="row"><label for="wDistance">Driving distance premium</label>
                <span class="val" id="vDistance">70</span></div>
              <input type="range" class="fr-range" id="wDistance" min="0" max="100" step="5" value="70"
                aria-describedby="hDistance">
              <p class="hint" id="hDistance">How much raw length is worth. High on a long, soft course with
                wide fairways; low when the rough punishes a miss more than the extra fifty yards helps.</p>
            </div>
            <div class="fr-s">
              <div class="row"><label for="wApproach">Approach play</label>
                <span class="val" id="vApproach">85</span></div>
              <input type="range" class="fr-range" id="wApproach" min="0" max="100" step="5" value="85"
                aria-describedby="hApproach">
              <p class="hint" id="hApproach">Small greens, firm surfaces and long second shots all push this
                up. It is the single biggest separator most weeks.</p>
            </div>
            <div class="fr-s">
              <div class="row"><label for="wAroundGreen">Short game severity</label>
                <span class="val" id="vAroundGreen">55</span></div>
              <input type="range" class="fr-range" id="wAroundGreen" min="0" max="100" step="5" value="55"
                aria-describedby="hAround">
              <p class="hint" id="hAround">Runoffs, deep bunkers and thick greenside rough. High when missing
                a green is genuinely expensive.</p>
            </div>
            <div class="fr-s">
              <div class="row"><label for="wPutting">Putting weight</label>
                <span class="val" id="vPutting">60</span></div>
              <input type="range" class="fr-range" id="wPutting" min="0" max="100" step="5" value="60"
                aria-describedby="hPutting">
              <p class="hint" id="hPutting">How much the greens decide it. Each player is scored on the
                surface below, because a good Bermuda putter is not automatically a good Poa putter.</p>
              <div class="fr-surface" id="surfacePick" role="group" aria-label="Putting surface this week">
                <button type="button" data-surface="bentgrass" aria-pressed="true">Bentgrass</button>
                <button type="button" data-surface="bermuda" aria-pressed="false">Bermuda</button>
                <button type="button" data-surface="poa" aria-pressed="false">Poa</button>
              </div>
            </div>
          </div>

          <div class="fr-acts">
            <button type="button" class="fr-go ghost" id="resetBtn">Reset to this course</button>
            <button type="button" class="fr-go ghost" id="clearPicks">Clear my picks</button>
          </div>

          <div class="fr-board" id="board" aria-live="polite" aria-label="Field ranked by fit"></div>
          <div class="fr-msg" id="msg" role="status"></div>
          <p class="fr-note" id="pickNote"></p>

          <div style="border:2px solid var(--ink);background:var(--white);padding:15px 16px;margin-top:22px">
            <div style="font-size:10.5px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;
                        color:var(--grey);margin-bottom:6px">Before Thursday</div>
            <p style="font-size:14px;line-height:1.55;margin-bottom:12px">This board is live in your browser
              every week the feed updates &mdash; there is nothing to subscribe to for that. What lands in
              your inbox is <b>The Card</b>: unfiltered player ratings and the stories PR reps tried to kill,
              every Friday.</p>
            <form id="frForm" novalidate style="display:flex;gap:8px;flex-wrap:wrap">
              <label for="frEmail" class="fr-sr">Email address</label>
              <input type="email" id="frEmail" placeholder="you@email.com" autocomplete="email"
                style="flex:1;min-width:170px;min-height:48px;padding:10px 12px;background:#fff;
                       border:2px solid var(--ink);font:600 15px/1.2 Archivo,system-ui,sans-serif;color:var(--ink)">
              <button type="submit" class="fr-go" id="frSubmit">Join</button>
            </form>
            <div class="fr-msg" id="frMsg" role="status"></div>
          </div>
        </div>
      </section>

      <section class="panel explain">
        <h2>How the fit score is built, and what it cannot tell you</h2>
        <p>Each player carries four ratings from 0 to 100, where 50 is a tour-average performer: distance,
          approach, short game, and putting <em>on the surface being played</em>. The fit score is a
          weighted average of those four against the weights you set. Set approach to 100 and everything
          else to 0 and you get a pure iron-play ranking. That is the whole model, and it is deliberately
          simple enough to argue with.</p>
        <p><b>A fit score is not a probability.</b> It says a course asks for skills a player happens to
          have. It knows nothing about form, injury, travel, the draw, the weather on Thursday afternoon,
          or whether someone is putting well this month. Golf is won by whoever plays best over four days,
          not by whoever fits best on Tuesday. Treat the board as an argument, not an answer.</p>
        <p><b>The shipped field is archetypes, not real players.</b> Every card on the board is labelled.
          They exist so the model is usable and testable out of the box. A real field is loaded by editing
          <code>/data/tournament-field.json</code> with real strokes-gained numbers from a source you can
          point at. Estimating a named player's numbers by feel and publishing them would be inventing
          statistics about a real person, so this tool ships without doing it.</p>
      </section>

      <section class="faq-block panel" aria-labelledby="faq-h">
        <h2 id="faq-h">Questions</h2>
        <details><summary>Does putting surface really matter that much?</summary>
          <p>More than almost any other single factor. Bermuda grain, afternoon Poa bumpiness and the true
            roll of bentgrass reward different reads and different strokes. Players with a real surface
            preference show it in their numbers, which is why putting is split three ways here.</p></details>
        <details><summary>Are these real players?</summary>
          <p>No. The shipped list is archetypes, each one labelled on the board. Load a real field by
            editing the tournament feed with sourced numbers.</p></details>
        <details><summary>Is this a betting tool?</summary>
          <p>No. It ranks skills against course demands. It does not price markets, take stakes or predict
            winners, and a fit score is not a probability.</p></details>
        <details><summary>Where do my picks go?</summary>
          <p>Into your own browser, alongside everything else in the locker. Nothing is uploaded and there
            is no account. Clearing browser data deletes them.</p></details>
      </section>

    </div>
  </div>
'''

SCRIPT = r'''  <script>
    var $ = function (id) { return document.getElementById(id); };

    var FEED_URL = '/data/tournament-field.json';
    var SURFACES = ['bentgrass', 'bermuda', 'poa'];
    var KEYS = ['distance', 'approach', 'aroundGreen', 'putting'];
    var LABEL = { distance: 'distance', approach: 'approach play',
                  aroundGreen: 'short game', putting: 'putting' };
    var MAX_PICKS = 4;
    var TOOL = 'field-reader';

    function esc(s) {
      return String(s === null || s === undefined ? '' : s)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;')
        .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }
    function clamp(n, lo, hi) { return Math.max(lo, Math.min(hi, n)); }
    function num(v) { return typeof v === 'number' && isFinite(v); }

    /* ==================== FEED VALIDATION ====================
       A half-parsed feed is worse than none: it would render a board that
       looks authoritative and is missing half the field. Anything that does
       not validate is refused with a reason. */
    /* Two classes of problem, and they are not interchangeable. A malformed
       EVENT is fatal: an unknown surface makes every putting lookup undefined
       and the whole board becomes nonsense. A malformed PLAYER is not: that
       one entry is dropped and the rest of the field still ranks. */
    function validateFeed(d) {
      var fatal = [], dropped = [];
      if (!d || typeof d !== 'object') return { fatal: ['feed is not an object'], dropped: [], players: [] };
      if (d.format !== 'golfraw.field') fatal.push('format must be "golfraw.field"');
      if (!num(d.version) || d.version > 1) fatal.push('unsupported feed version');

      var ev = d.event;
      if (!ev || typeof ev !== 'object') { fatal.push('event is missing'); }
      else {
        if (!ev.name) fatal.push('event.name is required');
        if (SURFACES.indexOf(ev.surface) === -1) fatal.push('event.surface must be bentgrass, bermuda or poa');
        var pr = ev.profile || {};
        for (var i = 0; i < KEYS.length; i++) {
          if (!num(pr[KEYS[i]]) || pr[KEYS[i]] < 0 || pr[KEYS[i]] > 100) {
            fatal.push('event.profile.' + KEYS[i] + ' must be 0-100');
          }
        }
      }

      var players = [];
      if (Object.prototype.toString.call(d.players) !== '[object Array]' || !d.players.length) {
        fatal.push('players must be a non-empty array');
      } else {
        for (var p = 0; p < d.players.length; p++) {
          var pl = d.players[p], bad = null;
          if (!pl || !pl.name) bad = 'player ' + (p + 1) + ' has no name';
          else {
            var sk = pl.skills || {};
            for (var k = 0; k < 3; k++) {
              if (!num(sk[KEYS[k]]) || sk[KEYS[k]] < 0 || sk[KEYS[k]] > 100) {
                bad = pl.name + ': ' + KEYS[k] + ' must be 0-100';
              }
            }
            var pu = sk.putting || {};
            for (var s = 0; s < SURFACES.length; s++) {
              if (!num(pu[SURFACES[s]]) || pu[SURFACES[s]] < 0 || pu[SURFACES[s]] > 100) {
                bad = pl.name + ': putting.' + SURFACES[s] + ' must be 0-100';
              }
            }
          }
          /* One malformed player is dropped with a note rather than taking the
             whole field down with it. */
          if (bad) dropped.push(bad); else players.push(pl);
        }
      }
      if (!players.length && !fatal.length) fatal.push('no usable players in the feed');
      return { fatal: fatal, dropped: dropped, players: players, event: d.event };
    }

    /* ==================== SCORING ====================
       Weighted mean of four 0-100 skills. Putting is read off the surface being
       played. With every weight at zero the result is undefined rather than a
       division by zero, so the board says so instead of printing NaN. */
    function fitScore(player, weights, surface) {
      var total = 0, acc = 0;
      for (var i = 0; i < KEYS.length; i++) {
        var k = KEYS[i], w = weights[k];
        if (!w) continue;
        var skill = (k === 'putting') ? player.skills.putting[surface] : player.skills[k];
        acc += w * skill;
        total += w;
      }
      if (!total) return null;
      return acc / total;
    }

    /* Which categories this player gains and loses on, given the weights.
       Contribution is measured against a 50 (tour-average) baseline so a
       heavily weighted average skill does not read as a strength. */
    function drivers(player, weights, surface) {
      var out = [];
      for (var i = 0; i < KEYS.length; i++) {
        var k = KEYS[i], w = weights[k];
        if (!w) continue;
        var skill = (k === 'putting') ? player.skills.putting[surface] : player.skills[k];
        out.push({ key: k, weight: w, skill: skill, effect: (skill - 50) * w });
      }
      out.sort(function (a, b) { return b.effect - a.effect; });
      return out;
    }

    /* The one-line read. Built from the numbers rather than written by hand, so
       it cannot drift out of step with the board when the weights move. */
    function verdict(player, weights, surface) {
      var d = drivers(player, weights, surface);
      if (!d.length) return 'Every weight is at zero, so nothing separates anyone.';
      var best = d[0], worst = d[d.length - 1];
      var parts = [];

      function name(k) {
        return '<b>' + esc(LABEL[k]) + '</b>' + (k === 'putting' ? ' on ' + esc(surface) : '');
      }

      if (d.length === 1) {
        /* Only one category carries any weight, so best and worst are the same
           driver. Reporting it once, with its sign, is the only honest read —
           the two-sided phrasing below would silently drop it. */
        if (best.effect > 0) parts.push(name(best.key) + ' is the edge, and it is the only thing that counts here');
        else if (best.effect < 0) parts.push(name(best.key) + ' is the problem, and it is the only thing that counts here');
        else parts.push('dead average at ' + name(best.key) + ', the only thing this week asks for');
      } else {
        if (best.effect > 0) parts.push(name(best.key) + ' is the edge');
        if (worst.effect < 0 && worst.key !== best.key) {
          parts.push('gives it back on ' + name(worst.key));
        }
        if (!parts.length) {
          parts.push('nothing this course asks for is a strength or a weakness here');
        }
      }
      var line = parts.join(', ') + '.';
      return line.charAt(0).toUpperCase() + line.slice(1);
    }

    function rankField(players, weights, surface) {
      var rows = [];
      for (var i = 0; i < players.length; i++) {
        var s = fitScore(players[i], weights, surface);
        rows.push({ player: players[i], score: s });
      }
      rows.sort(function (a, b) {
        if (a.score === null && b.score === null) return 0;
        if (a.score === null) return 1;
        if (b.score === null) return -1;
        if (b.score !== a.score) return b.score - a.score;
        return a.player.name < b.player.name ? -1 : 1;   /* stable, alphabetical tie-break */
      });
      for (var r = 0; r < rows.length; r++) {
        /* Equal scores share a rank rather than being ordered arbitrarily. */
        rows[r].rank = (r > 0 && rows[r].score === rows[r - 1].score) ? rows[r - 1].rank : r + 1;
      }
      return rows;
    }
  </script>
'''

SCRIPT2 = r'''  <script>
    var L = null;                /* resolved in boot(): the locker is deferred */
    var FIELD = null;            /* validated feed */
    var weights = { distance: 70, approach: 85, aroundGreen: 55, putting: 60 };
    var surface = 'bentgrass';
    var picks = [];              /* player names, max 4 */
    var saveTimer = null;

    /* ==================== RENDER ==================== */
    function renderCourse() {
      var ev = FIELD.event;
      var meta = [];
      if (ev.location) meta.push(esc(ev.location));
      if (ev.dates) meta.push(esc(ev.dates));
      if (ev.par) meta.push('Par ' + esc(ev.par));
      if (ev.yardage) meta.push(esc(ev.yardage) + ' yds');
      meta.push(esc(ev.surface) + ' greens');
      $('courseCard').innerHTML =
        '<div class="ev">This week</div>' +
        '<h3>' + esc(ev.name) + '</h3>' +
        '<div class="meta">' + meta.join(' &middot; ') + '</div>' +
        (ev.readTheCourse ? '<p>' + esc(ev.readTheCourse) + '</p>' : '') +
        (ev.isSample ? '<div class="fr-sample">Sample course &mdash; load a real event in the feed</div>' : '');
    }

    function renderWeights() {
      for (var i = 0; i < KEYS.length; i++) {
        var k = KEYS[i], cap = k.charAt(0).toUpperCase() + k.slice(1);
        var el = $('w' + cap);
        if (el) { el.value = weights[k]; $('v' + cap).textContent = weights[k]; }
      }
      var b = $('surfacePick').querySelectorAll('[data-surface]');
      for (var s = 0; s < b.length; s++) {
        b[s].setAttribute('aria-pressed', String(b[s].dataset.surface === surface));
      }
    }

    function renderBoard() {
      /* The board is rebuilt wholesale, which destroys the element the reader
         just activated. Without restoring focus, every lock throws a keyboard
         or screen-reader user back to the top of the document. */
      var focusName = null;
      var ae = document.activeElement;
      if (ae && ae.getAttribute && ae.getAttribute('data-pick')) focusName = ae.getAttribute('data-pick');

      var rows = rankField(FIELD.players, weights, surface);
      var allZero = rows.length && rows[0].score === null;
      var html = [];
      for (var i = 0; i < rows.length; i++) {
        var r = rows[i], p = r.player;
        var picked = picks.indexOf(p.name) !== -1;
        var score = r.score === null ? '—' : Math.round(r.score);
        html.push(
          '<div class="fr-card' + (r.rank <= 3 ? ' top' : '') + (picked ? ' picked' : '') + '">' +
            '<div class="fr-rank">' + (r.score === null ? '–' : r.rank) + '</div>' +
            '<div>' +
              '<div class="fr-name">' + esc(p.name) +
                (p.archetype ? '<span class="fr-tag">Archetype</span>' : '') + '</div>' +
              '<div class="fr-why">' + verdict(p, weights, surface) +
                (p.note ? ' <span style="opacity:.85">' + esc(p.note) + '</span>' : '') + '</div>' +
            '</div>' +
            '<div class="fr-right">' +
              '<div class="fr-score">' + score + '</div>' +
              '<div class="fr-bar"><span style="width:' +
                (r.score === null ? 0 : clamp(r.score, 0, 100)) + '%"></span></div>' +
              '<button type="button" class="fr-pick" data-pick="' + esc(p.name) + '" ' +
                'aria-pressed="' + picked + '" aria-label="' +
                (picked ? 'Remove ' : 'Lock ') + esc(p.name) + ' as a pick">' +
                (picked ? 'Locked' : 'Lock') + '</button>' +
            '</div>' +
          '</div>');
      }
      $('board').innerHTML = html.join('');
      if (focusName) {
        var back = $('board').querySelector('[data-pick="' + focusName.replace(/"/g, '\\"') + '"]');
        if (back) { try { back.focus(); } catch (e) { } }
      }
      if (allZero) {
        msg('Every weight is at zero, so there is nothing to rank on. Move a slider.', 'bad');
      } else { $('msg').className = 'fr-msg'; }
      renderPickNote();
    }

    function renderPickNote() {
      var n = picks.length;
      $('pickNote').innerHTML = n
        ? '<b>' + n + ' of ' + MAX_PICKS + ' locked:</b> ' + picks.map(esc).join(', ') +
          '. Saved on this device only — a fit score is not a prediction, and this is a record of what ' +
          'you thought on Tuesday, not advice.'
        : 'Lock up to ' + MAX_PICKS + ' picks to keep them on this device for the week.';
    }

    function msg(text, kind) {
      var el = $('msg');
      el.className = 'fr-msg on ' + (kind || '');
      el.innerHTML = text;
    }

    /* ==================== PICKS ==================== */
    function togglePick(name) {
      var i = picks.indexOf(name);
      if (i !== -1) picks.splice(i, 1);
      else {
        if (picks.length >= MAX_PICKS) {
          msg('That is ' + MAX_PICKS + ' picks already. Unlock one first.', 'bad');
          return;
        }
        picks.push(name);
      }
      renderBoard();
      savePicks();
    }

    /* Picks live in toolState rather than a new store: they are this tool's own
       weekly scratch data, which is exactly what toolState is for. */
    function savePicks() {
      if (!L) return;
      if (saveTimer) clearTimeout(saveTimer);
      saveTimer = setTimeout(function () {
        L.setToolState(TOOL, {
          eventId: FIELD.event.id || '',
          eventName: FIELD.event.name || '',
          surface: surface,
          weights: weights,
          picks: picks,
          lockedAt: Date.now()
        })['catch'](function () { });
      }, 300);
    }

    function loadPicks() {
      if (!L) return Promise.resolve();
      return L.getToolState(TOOL).then(function (d) {
        if (!d) return;
        /* Picks belong to the event they were made for. A new week starts clean
           rather than carrying last week's names onto a different course. */
        if (d.eventId && FIELD.event.id && d.eventId !== FIELD.event.id) return;
        if (d.weights) {
          for (var i = 0; i < KEYS.length; i++) {
            if (num(d.weights[KEYS[i]])) weights[KEYS[i]] = clamp(d.weights[KEYS[i]], 0, 100);
          }
        }
        if (SURFACES.indexOf(d.surface) !== -1) surface = d.surface;
        if (Object.prototype.toString.call(d.picks) === '[object Array]') {
          var live = {};
          for (var p = 0; p < FIELD.players.length; p++) live[FIELD.players[p].name] = true;
          picks = [];
          for (var q = 0; q < d.picks.length && picks.length < MAX_PICKS; q++) {
            if (live[d.picks[q]]) picks.push(d.picks[q]);   /* drop names no longer in the field */
          }
        }
      })['catch'](function () { });
    }

    /* ==================== BOOT ==================== */
    function applyCourseDefaults() {
      var pr = FIELD.event.profile;
      for (var i = 0; i < KEYS.length; i++) weights[KEYS[i]] = clamp(pr[KEYS[i]], 0, 100);
      surface = FIELD.event.surface;
    }

    function wire() {
      for (var i = 0; i < KEYS.length; i++) {
        (function (k) {
          var cap = k.charAt(0).toUpperCase() + k.slice(1);
          var el = $('w' + cap);
          if (!el) return;
          el.addEventListener('input', function () {
            weights[k] = clamp(parseInt(el.value, 10) || 0, 0, 100);
            $('v' + cap).textContent = weights[k];
            renderBoard();
            savePicks();
          });
        })(KEYS[i]);
      }
      $('surfacePick').addEventListener('click', function (e) {
        var b = e.target.closest && e.target.closest('[data-surface]');
        if (!b) return;
        surface = b.dataset.surface;
        renderWeights(); renderBoard(); savePicks();
      });
      $('board').addEventListener('click', function (e) {
        var b = e.target.closest && e.target.closest('[data-pick]');
        if (b) togglePick(b.getAttribute('data-pick'));
      });
      $('resetBtn').addEventListener('click', function () {
        applyCourseDefaults(); renderWeights(); renderBoard(); savePicks();
        msg('Weights reset to this course profile.', 'good');
      });
      $('clearPicks').addEventListener('click', function () {
        picks = []; renderBoard(); savePicks();
      });

      /* The site's existing Friday list, described as exactly that. Nothing
         here can assemble and send a Wednesday board, so nothing promises one:
         the board is already live in the browser whenever the feed updates. */
      $('frForm').addEventListener('submit', function (e) {
        e.preventDefault();
        var email = $('frEmail').value.replace(/^\s+|\s+$/g, '');
        var box = $('frMsg');
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) {
          box.className = 'fr-msg on bad'; box.textContent = 'That does not look like an email address.';
          $('frEmail').focus(); return;
        }
        var btn = $('frSubmit');
        btn.disabled = true; btn.textContent = 'Sending…';
        fetch('https://api.hsforms.com/submissions/v3/integration/submit/148744463/f9b9028c-b648-4563-9b01-2b53b3caae13', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ fields: [{ name: 'email', value: email }] })
        }).then(function (r) {
          if (!r.ok) throw new Error('rejected');
          $('frForm').style.display = 'none';
          box.className = 'fr-msg on good'; box.textContent = 'You are on the list.';
        })['catch'](function () {
          btn.disabled = false; btn.textContent = 'Join';
          box.className = 'fr-msg on bad'; box.textContent = 'Could not connect. Try again in a moment.';
        });
      });
    }

    function fail(reason) {
      $('board').innerHTML = '';
      msg('Could not load the tournament feed: ' + esc(reason) +
        '. The board is not shown rather than shown half-built.', 'bad');
    }

    function boot() {
      L = window.GolfrawLocker || null;
      wire();

      fetch(FEED_URL, { cache: 'no-cache' }).then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      }).then(function (d) {
        var v = validateFeed(d);
        if (v.fatal.length || !v.players.length) { fail(v.fatal[0] || 'the feed did not validate'); return; }
        FIELD = { event: v.event, players: v.players };
        applyCourseDefaults();
        renderCourse();
        var ready = L ? L.ready().then(loadPicks) : Promise.resolve();
        return ready.then(function () {
          renderWeights();
          renderBoard();
          if (v.dropped.length) {
            msg(v.dropped.length + ' player' + (v.dropped.length === 1 ? ' was' : 's were') +
              ' dropped from the feed: ' + esc(v.dropped[0]), 'bad');
          }
        });
      })['catch'](function (e) { fail((e && e.message) || 'unknown error'); });

      if (L) {
        L.subscribe(function (kind) {
          if (kind === 'clear') { picks = []; if (FIELD) renderBoard(); }
        });
      }
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
    else boot();
  </script>
'''

TAIL = '''  <script>window.__gr_consent=true;window.__gr_ads=false;</script>
'''

LOCKER = '''<!-- LOCKER:START -->
  <!-- The Locker: local-first storage (IndexedDB) + the My Bag drawer.
       Deferred so it never competes with first paint; execution order is
       guaranteed by `defer`, which the storage layer relies on. -->
  <script src="/lib/locker/schema.js?v=4" defer></script>
  <script src="/lib/locker/store.js?v=4" defer></script>
  <script src="/lib/locker/drawer.js?v=5" defer></script>
<!-- LOCKER:END -->
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
        '  <script>',
        p['nav_script'].split('<script>', 1)[1] if '<script>' in p['nav_script'] else '',
        '  </script>',
        SCRIPT,
        SCRIPT2,
        p['gtag'],
        TAIL,
        LOCKER + '</body>',
        '',
        '</html>',
    ])
    io.open(OUT, 'w', encoding='utf-8').write(doc)
    print('  wrote %s (%d bytes)' % (os.path.basename(OUT), len(doc.encode('utf-8'))))
    return 0


if __name__ == '__main__':
    sys.exit(main())
