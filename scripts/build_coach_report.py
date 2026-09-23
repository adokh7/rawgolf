#!/usr/bin/env python3
"""Generate tools-coach-report.html from the shared tool-page shell.

Re-runnable: rewrites the file wholesale. Edits to the HTML are destroyed.
After running: python3 scripts/wire_locker.py && python3 scripts/apply_theme.py
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHELL = os.path.join(ROOT, 'tools-bag-audit.html')
OUT = os.path.join(ROOT, 'tools-coach-report.html')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tool_shell import shell_parts as _shell_parts
from scripts.schema_normalizer import normalize_tool_page

SITE = 'https://www.golfraw.com'
SLUG = 'tools-coach-report'
TITLE = 'Coach &amp; Fitter Report: Gapping, Bag, Tendencies | GolfRaw'
DESC = ('GolfRaw Pro coach report from your range session, bag and rounds: dispersion, gaps, passengers and tendencies. Open as a preview; print or share.')
OG_IMAGE = SITE + '/public/raw-golf-practice.webp'
# Bump when lib/pro/report.js changes (immutable .js cache).
REPORT_VER = '3'
# Pro client (paywall / entitlement). Bump when lib/pro/pro.js changes.
PRO_VER = '2'
PREMIUM_LINK = '  <link rel="stylesheet" href="/public/tool-premium.css?v=4">\n'
HEAD_EXTRA = ('  <script src="/lib/pro/report.js?v=%s" defer></script>\n' % REPORT_VER +
              '  <script src="/lib/pro/pro.js?v=%s" defer></script>\n' % PRO_VER)


def shell_parts():
    return _shell_parts(SHELL)


def rewrite_meta(s):
    s = re.sub(r'<title>.*?</title>', '<title>%s</title>' % TITLE, s, flags=re.S)
    for pat, val in [(r'(<meta name="description" content=")[^"]*(")', DESC),
                     (r'(<meta property="og:title" content=")[^"]*(")', TITLE),
                     (r'(<meta property="og:description" content=")[^"]*(")', DESC),
                     (r'(<meta property="og:image" content=")[^"]*(")', OG_IMAGE),
                     (r'(<meta name="twitter:title" content=")[^"]*(")', TITLE),
                     (r'(<meta name="twitter:description" content=")[^"]*(")', DESC),
                     (r'(<meta name="twitter:image" content=")[^"]*(")', OG_IMAGE)]:
        s = re.sub(pat, lambda m, v=val: m.group(1) + v + m.group(2), s)
    s = re.sub(r'(<link rel="canonical" href=")[^"]*(")', r'\g<1>%s/%s\g<2>' % (SITE, SLUG), s)
    s = re.sub(r'(<meta property="og:url" content=")[^"]*(")', r'\g<1>%s/%s\g<2>' % (SITE, SLUG), s)
    return s


JSONLD = '''  <!-- ============ STRUCTURED DATA ============ -->
  <script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebApplication",
      "name": "The Coach Report",
      "alternateName": "Golf Coach and Fitter Report Builder",
      "url": "%(site)s/%(slug)s",
      "applicationCategory": "SportsApplication",
      "operatingSystem": "Any browser",
      "browserRequirements": "Requires JavaScript",
      "description": "%(desc)s",
      "featureList": [
        "One-page report from your own range session, bag and rounds",
        "Carry dispersion chart with medians and 80%% bands",
        "Gap and passenger verdicts using the same thresholds as the tools",
        "On-course tendencies from the Tendency Engine",
        "Print or save as PDF; share by a link that carries the data itself"
      ],
      "publisher": { "@type": "Organization", "name": "GolfRaw", "url": "%(site)s/" }
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        { "@type": "ListItem", "position": 1, "name": "Home", "item": "%(site)s/" },
        { "@type": "ListItem", "position": 2, "name": "Tools", "item": "%(site)s/tools" },
        { "@type": "ListItem", "position": 3, "name": "The Coach Report", "item": "%(site)s/%(slug)s" }
      ]
    },
    {
      "@type": "FAQPage",
      "mainEntity": [
        { "@type": "Question", "name": "Where does the report get its numbers?",
          "acceptedAnswer": { "@type": "Answer", "text": "From the tools you already used on this device: the Standing Order range session (typed or imported from a launch monitor), the Bag Audit usage and trust scores, and completed rounds from the Tendency Engine. It uses the same thresholds those tools use, so nothing on the page contradicts what you saw in the tool." } },
        { "@type": "Question", "name": "How do I get a PDF?",
          "acceptedAnswer": { "@type": "Answer", "text": "Use the Print / save as PDF button and choose Save as PDF in your browser's print dialog. The page is laid out for a single A4 or Letter sheet. Nothing is generated on a server and nothing is uploaded." } },
        { "@type": "Question", "name": "How does the share link work if nothing is uploaded?",
          "acceptedAnswer": { "@type": "Answer", "text": "The link carries the report itself, encoded after the hash in the address. Browsers never send that part to a server, so GolfRaw never receives it. Anyone you give the link to can open the report; treat it like sending the PDF." } }
      ]
    }
  ]
}
  </script>
''' % {'site': SITE, 'slug': SLUG, 'desc': DESC}


STYLE = '''<style>
    /* ---- The Coach Report -------------------------------------------- */
    .cr-wrap { max-width: 760px; margin: 0 auto }
    .cr-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px }
    .cr-grid .full { grid-column: 1 / -1 }
    .cr-grid label { display: block; font-size: 10.5px; font-weight: 800; letter-spacing: .08em;
      text-transform: uppercase; color: var(--grey); margin-bottom: 6px }
    .cr-grid input, .cr-grid select, .cr-grid textarea { width: 100%; min-height: 48px; padding: 10px 12px;
      background: #fff; border: 2px solid var(--ink); font: 600 15px/1.3 'Archivo', system-ui, sans-serif; color: var(--ink) }
    .cr-grid textarea { min-height: 96px; font-weight: 500; resize: vertical }
    .cr-grid input:focus, .cr-grid select:focus, .cr-grid textarea:focus { outline: 3px solid var(--flag); outline-offset: -1px }
    .cr-hint { font-size: 12.5px; color: var(--grey); line-height: 1.5; margin-top: 6px }
    .cr-src { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 16px 0 }
    .cr-src div { padding: 12px 14px; background: var(--white); border: 2px solid var(--line); font-size: 13px; line-height: 1.45 }
    .cr-src b { display: block; font-family: 'IBM Plex Mono', monospace; font-size: 10px; letter-spacing: .12em;
      text-transform: uppercase; color: var(--grey); margin-bottom: 4px }
    .cr-src .on { border-color: var(--fairway) }
    .cr-src .on b { color: var(--fairway) }
    .so-go { min-height: 52px; padding: 0 22px; background: var(--ink); color: #fff; border: 2px solid var(--ink);
      font: 900 13px/1 'Archivo', system-ui, sans-serif; letter-spacing: .08em; text-transform: uppercase;
      cursor: pointer; transition: background .15s; display: inline-flex; align-items: center; text-decoration: none }
    .so-go:hover { background: var(--fairway); border-color: var(--fairway); color: #fff }
    .so-go:focus-visible { outline: 3px solid var(--flag); outline-offset: 3px }
    .so-go[disabled] { background: var(--line); border-color: var(--line); color: var(--grey); cursor: not-allowed }
    .so-go.alt { background: var(--white); color: var(--ink) }
    .so-go.alt:hover { background: var(--paper); color: var(--ink); border-color: var(--ink) }
    .cr-acts { display: flex; flex-wrap: wrap; gap: 9px; margin-top: 18px }
    .so-msg { margin-top: 11px; padding: 10px 12px; border: 2px solid var(--ink); background: #fff;
      font-size: 13px; font-weight: 600; line-height: 1.45; display: none }
    .so-msg.on { display: block }
    .so-msg.bad { border-color: var(--flag); color: var(--flag) }
    .so-msg.good { border-color: var(--fairway); color: var(--fairway) }
    .cr-shared { padding: 14px 16px; margin-bottom: 18px; background: var(--white); border: 2px solid var(--fairway);
      font-size: 14px; line-height: 1.5 }
    .cr-shared b { color: var(--fairway) }

    /* ---- the report document (screen preview and print share one DOM) ---- */
    .rp { background: #fff; color: #0B1F15; border: 2px solid var(--ink); padding: 28px 30px; margin-top: 22px;
      font-family: 'Inter', 'Archivo', system-ui, sans-serif; font-size: 12.5px; line-height: 1.45 }
    .rp[hidden] { display: none }
    .rp-head { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; padding-bottom: 12px;
      border-bottom: 2px solid #0A4D2E; margin-bottom: 14px }
    .rp-brand { font: 800 22px/1 'Plus Jakarta Sans', 'Archivo', system-ui, sans-serif; letter-spacing: -.02em; color: #0A4D2E }
    .rp-brand span { font-weight: 500 }
    .rp-brand em { font: 700 9px/1 'Inter', system-ui, sans-serif; letter-spacing: .14em; text-transform: uppercase;
      color: #fff; background: #0A4D2E; padding: 3px 7px; border-radius: 999px; vertical-align: middle; margin-left: 6px }
    .rp-title { text-align: right }
    .rp-title h2 { font: 800 18px/1.1 'Plus Jakarta Sans', 'Archivo', system-ui, sans-serif; margin: 0 0 3px; padding: 0; border: 0; text-transform: none; letter-spacing: -.015em }
    .rp-title p { margin: 0; font-family: 'IBM Plex Mono', monospace; font-size: 10.5px; color: #55655B }
    .rp-meta { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 0 0 14px; padding: 0 }
    .rp-meta div { padding: 8px 10px; border: 1px solid #E5E7EB; border-radius: 6px }
    .rp-meta dt, .rp-stats dt { font-family: 'IBM Plex Mono', monospace; font-size: 9px; letter-spacing: .12em; text-transform: uppercase; color: #55655B; margin-bottom: 3px }
    .rp-meta dd, .rp-stats dd { margin: 0; font-weight: 700; font-size: 12.5px }
    .rp-sec { margin-top: 12px }
    .rp-sec h3 { font: 800 12px/1.2 'Inter', 'Archivo', system-ui, sans-serif; letter-spacing: .08em; text-transform: uppercase;
      color: #0A4D2E; margin: 0 0 8px; padding: 0 0 5px; border-bottom: 1px solid #E5E7EB }
    .rp-sec h3::before { content: none }
    .rp-chart { width: 100%; height: auto; display: block; margin: 2px 0 8px }
    .rp-tbl { width: 100%; border-collapse: collapse; font-size: 11.5px }
    .rp-tbl th { text-align: right; font-family: 'IBM Plex Mono', monospace; font-size: 9px; font-weight: 700; letter-spacing: .08em;
      text-transform: uppercase; color: #55655B; padding: 0 4px 5px; border-bottom: 1px solid #0A4D2E }
    .rp-tbl td { text-align: right; padding: 5px 4px; border-bottom: 1px solid #E5E7EB; font-family: 'IBM Plex Mono', monospace }
    .rp-tbl th:first-child, .rp-tbl td:first-child { text-align: left; font-family: 'Inter', 'Archivo', system-ui, sans-serif; font-weight: 700 }
    .rp-tbl tr.thin td { color: #8A968F }
    .rp-tbl small { font-weight: 500; color: #8A968F }
    .rp-note, .rp-empty, .rp-foot { font-size: 10.5px; color: #55655B; line-height: 1.45; margin: 8px 0 0 }
    .rp-empty { font-style: italic }
    .rp-flags, .rp-lines { margin: 0; padding: 0; list-style: none }
    .rp-flags li { padding: 7px 10px; margin-bottom: 6px; border: 1px solid #E5E7EB; border-left: 5px solid #CBD5CF; font-size: 11.5px; line-height: 1.4 }
    .rp-flags li.gap { border-left-color: #A85F06 } .rp-flags li.dup { border-left-color: #C98A00 } .rp-flags li.ok { border-left-color: #1B7A43 }
    .rp-flags b { display: inline-block; margin-right: 6px; font-size: 10px; letter-spacing: .08em; text-transform: uppercase }
    .rp-stats { display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; margin: 0 0 10px; padding: 0 }
    .rp-stats div { padding: 6px 8px; border: 1px solid #E5E7EB; border-radius: 6px; text-align: center }
    .rp-lines li { padding: 3px 0 3px 14px; position: relative; font-size: 11.5px }
    .rp-lines li::before { content: ""; position: absolute; left: 0; top: 9px; width: 6px; height: 6px; background: #1B7A43; border-radius: 50% }
    .rp-notes { font-size: 12px; white-space: normal; margin: 0 }
    .rp-foot { margin-top: 14px; padding-top: 8px; border-top: 1px solid #E5E7EB }

    #printRoot { display: none }
    @media print {
      @page { size: A4; margin: 11mm 12mm }
      body > *:not(#printRoot) { display: none !important }
      #printRoot { display: block !important }
      #printRoot .rp { border: 0; padding: 0; margin: 0; font-size: 11.5px }
      #printRoot .rp-flags li, #printRoot .rp-meta div, #printRoot .rp-stats div { break-inside: avoid }
      #printRoot svg { max-height: 68mm }
    }

    @media (max-width: 640px) {
      .cr-grid, .cr-src { grid-template-columns: 1fr }
      .rp { padding: 18px 16px }
      .rp-meta { grid-template-columns: 1fr 1fr }
      .rp-stats { grid-template-columns: repeat(3, 1fr) }
      .rp-head { flex-direction: column; align-items: flex-start }
      .rp-title { text-align: left }
      .rp-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch }
    }
  </style>
'''


MAIN = '''
  <div class="hub-hero">
    <div class="wrap">
      <div class="eyebrow">GolfRaw &middot; TOOLS &middot; PRO</div>
      <h1>The Coach Report</h1>
      <p>One page a coach or fitter can actually use: your carry dispersion by club, the gaps and the
        passengers in the bag, and what your last rounds say about where you miss. Built from the numbers
        already on this device &mdash; the Standing Order, the Bag Audit and the Tendency Engine &mdash; then
        printed to PDF or handed over as a link. Nothing is uploaded to build it.</p>
      <p class="cr-hint"><a href="/pro">See what stays free and what Pro adds &rarr;</a></p>
    </div>
  </div>

  <div class="tool-body">
    <div class="wrap">

      <section class="answer-block" aria-labelledby="aeo-q">
        <div class="ab-tag">The short answer</div>
        <h2 id="aeo-q">What should a golf fitting or coaching report contain?</h2>
        <blockquote>The player&rsquo;s <b>median carry per club</b> with its dispersion, the <b>gaps</b> between
          adjacent clubs, which clubs are <b>passengers</b>, and any on-course <b>tendency</b> the data
          supports. Medians, not averages; bands, not single numbers; and a stated sample size for each.
          The <a href="/news-2026-golf-club-distances-guide">realistic club-distance chart</a> explains
          the baseline, while the <a href="/golf-swing-analysis-apps">swing-analysis app guide</a> shows
          why recorded evidence beats a remembered swing.</blockquote>
      </section>

      <div class="cr-shared" id="sharedNote" hidden><b>Shared report.</b> This was built on someone else&rsquo;s device and
        the data travelled inside the link you opened &mdash; GolfRaw never received it. You can print it or
        <a href="/tools-coach-report">build your own</a>.</div>

      <section class="panel" id="setup" data-gr-inputs="import" aria-labelledby="set-h">
        <h2 id="set-h">Build the report <span class="gr-pro-badge" id="crBadge">GolfRaw Pro</span></h2>
        <div class="cr-wrap" id="crGate">
          <div class="cr-src" aria-label="Data found on this device">
            <div id="srcSession"><b>Range session</b><span>Looking&hellip;</span></div>
            <div id="srcBag"><b>Bag audit</b><span>Looking&hellip;</span></div>
            <div id="srcRounds"><b>Rounds</b><span>Looking&hellip;</span></div>
          </div>
          <div class="cr-grid">
            <div><label for="fClient">Player</label><input id="fClient" type="text" maxlength="60" autocomplete="name" placeholder="Player name"></div>
            <div><label for="fCoach">Coach / fitter</label><input id="fCoach" type="text" maxlength="60" placeholder="Your name or business"></div>
            <div><label for="fHcp">Handicap</label><input id="fHcp" type="number" inputmode="decimal" step="0.1" min="-10" max="54" placeholder="e.g. 12.4"></div>
            <div><label for="fSession">Range session</label><select id="fSession"><option value="">No session found</option></select></div>
            <div class="full"><label for="fNotes">Notes for the report (optional)</label>
              <textarea id="fNotes" maxlength="1200" placeholder="Recommendations, the fitting outcome, what to practise next&hellip;"></textarea>
              <p class="cr-hint">Names and notes are kept on this device and included in the report and its share link.</p></div>
          </div>
          <div class="cr-acts">
            <button type="button" class="so-go" id="buildBtn">Build the report</button>
          </div>
          <div class="so-msg" id="setMsg" role="status"></div>
        </div>
      </section>

      <section class="panel" id="out" hidden aria-labelledby="out-h">
        <h2 id="out-h">Your report</h2>
        <div class="cr-wrap">
          <div class="cr-acts" style="margin-top:0">
            <button type="button" class="so-go" id="printBtn">Print / save as PDF</button>
            <button type="button" class="so-go alt" id="shareBtn">Copy share link</button>
          </div>
          <div class="so-msg" id="outMsg" role="status"></div>
          <div class="rp-scroll"><div class="rp" id="report" aria-live="polite"></div></div>
          <p class="cr-hint" style="margin-top:12px">In the print dialog choose <b>Save as PDF</b>. The share link contains the
            whole report after the hash in the address, so it can be long; it works on any device and never
            touches a server.</p>
        </div>
      </section>

      <section class="faq-block panel" aria-labelledby="faq-h">
        <h2 id="faq-h">Questions</h2>
        <details><summary>Is the report free?</summary>
          <p>Building the report is a <b>GolfRaw Pro</b> feature. While Pro is not yet on sale it is open
            to everyone as a preview; once it is, this page asks you to upgrade or restore a pass you already
            own. Opening a report someone shared with you is always free, and every free tool stays free.</p></details>
        <details><summary>Where does the report get its numbers?</summary>
          <p>From the tools you already used on this device: the Standing Order range session (typed in or
            imported from a launch monitor), the Bag Audit usage and trust scores, and completed rounds from
            the Tendency Engine. It applies the same thresholds those tools use, so nothing on the page
            contradicts what you saw in the tool.</p></details>
        <details><summary>How do I get a PDF?</summary>
          <p>Press <b>Print / save as PDF</b> and choose <b>Save as PDF</b> in your browser&rsquo;s print dialog.
            The page is laid out for a single A4 or Letter sheet. No server generates it and nothing is uploaded.</p></details>
        <details><summary>How does the share link work if nothing is uploaded?</summary>
          <p>The link carries the report itself, encoded after the hash in the address. Browsers never send
            that part to a server, so GolfRaw never receives it. Anyone you give the link to can open the
            report, so treat it exactly as you would treat sending the PDF.</p></details>
        <details><summary>What if a section says there is no data?</summary>
          <p>Then there is none on this device yet. Log a range session in the Standing Order (or import a
            launch-monitor CSV there), enter usage in the Bag Audit, and tap in rounds in the Tendency Engine.
            The report never fills a gap with a guess.</p></details>
      </section>

    </div>
  </div>

  <!-- print-only clone of the report, at body level so the print rule can isolate it -->
  <div id="printRoot" aria-hidden="true"><div class="rp" id="printReport"></div></div>
'''


SCRIPT = r'''  <script>
    var $ = function (id) { return document.getElementById(id); };
    var L = null, R = null;          /* Locker + report engine, resolved in boot() (deferred scripts) */
    var data = { profile: null, bag: null, sessions: [], cards: [] };
    var model = null;
    var TOOL = 'coach-report';

    /* A shared link shows someone else's report; the tool-events layer counts
       that reader separately from people building their own. */
    if (/[#&]r=/.test(location.hash || '')) document.documentElement.setAttribute('data-gr-view', 'shared_result');

    function esc(s) { return String(s === null || s === undefined ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
    function msg(id, text, kind) { var el = $(id); el.className = 'so-msg on ' + (kind || ''); el.innerHTML = text; }
    function dateText(ts) { try { return new Date(ts).toLocaleDateString(); } catch (e) { return ''; } }

    function sourceCard(id, on, text) {
      var el = $(id); el.className = on ? 'on' : ''; el.querySelector('span').textContent = text;
    }

    function fillSessions() {
      var sel = $('fSession'), opts = [];
      var ses = data.sessions.slice().sort(function (a, b) { return (b.startedAt || 0) - (a.startedAt || 0); });
      for (var i = 0; i < ses.length; i++) {
        var n = 0; for (var j = 0; j < (ses[i].clubs || []).length; j++) n += ses[i].clubs[j].shots.length;
        if (!n) continue;
        opts.push('<option value="' + esc(ses[i].id) + '">' + esc(ses[i].label || 'Range session') + ' · ' + esc(dateText(ses[i].startedAt)) + ' · ' + n + ' shots</option>');
      }
      sel.innerHTML = opts.length ? opts.join('') : '<option value="">No session with shots found</option>';
      sel.disabled = !opts.length;
      return opts.length;
    }

    function currentSession() {
      var id = $('fSession').value;
      for (var i = 0; i < data.sessions.length; i++) if (data.sessions[i].id === id) return data.sessions[i];
      return null;
    }

    function inputs() {
      return { client: $('fClient').value, coach: $('fCoach').value, handicap: $('fHcp').value, notes: $('fNotes').value };
    }

    function build() {
      if (!R) { msg('setMsg', 'The report engine did not load. Reload the page and try again.', 'bad'); return; }
      var f = inputs();
      model = R.buildModel({
        coach: f.coach, client: f.client, handicap: f.handicap === '' ? null : f.handicap, notes: f.notes,
        units: data.profile && data.profile.units === 'meters' ? 'meters' : 'yards',
        session: currentSession(), bag: data.bag, scorecards: data.cards
      });
      render(model);
      if (L) L.setToolState(TOOL, { client: f.client, coach: f.coach, notes: f.notes })['catch'](function () {});
      $('out').hidden = false;
      $('out').scrollIntoView({ behavior: 'smooth', block: 'start' });
      /* The report is built from other tools' data; with none of it there is
         only a placeholder page, which counts as a start, not a finished report. */
      if (window.GRTrack) {
        GRTrack.inputMode('import');
        if (currentSession() || (data.bag && data.bag.clubs && data.bag.clubs.length) || (data.cards && data.cards.length)) GRTrack.completed();
        else GRTrack.started();
      }
    }

    function render(m) {
      var html = R.renderReport(m);
      $('report').innerHTML = html;
      $('printReport').innerHTML = html;
    }

    function share() {
      if (!model) return;
      var enc = R.encodeShare(model);
      if (!enc.ok) { if (window.GRTrack) GRTrack.error('share_link_too_long'); msg('outMsg', enc.error, 'bad'); return; }
      var url = location.origin + '/tools-coach-report#r=' + enc.payload;
      var done = function () { if (window.GRTrack) GRTrack.shared('copy_link'); msg('outMsg', 'Link copied — ' + Math.round(url.length / 100) / 10 + ' KB, carries the whole report, never touches a server.', 'good'); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(done)['catch'](function () { fallback(url); });
      else fallback(url);
      function fallback(u) { msg('outMsg', 'Copy this link: <input type="text" readonly value="' + esc(u) + '" style="width:100%;margin-top:6px;font-size:12px" onclick="this.select()">', ''); }
    }

    /* A shared link renders read-only from the fragment; nothing is read from
       or written to this device's Locker. */
    function openShared(payload) {
      var dec = R ? R.decodeShare(payload) : { ok: false, error: 'Engine unavailable.' };
      $('setup').hidden = true;
      $('sharedNote').hidden = false;
      if (!dec.ok) { if (window.GRTrack) GRTrack.error('shared_link_invalid'); $('sharedNote').innerHTML = '<b>Could not open this report.</b> ' + esc(dec.error); return; }
      model = dec.model;
      render(model);
      $('out').hidden = false;
      $('shareBtn').hidden = true;
    }

    function boot() {
      L = window.GolfrawLocker || null;
      R = window.GolfrawReport || null;
      $('buildBtn').addEventListener('click', build);
      $('printBtn').addEventListener('click', function () {
        window.print();
        if (window.GRTrack) GRTrack.shared('print');
      });
      $('shareBtn').addEventListener('click', share);
      $('fSession').addEventListener('change', function () { if (model) build(); });

      var m = /[#&]r=([A-Za-z0-9_-]+)/.exec(location.hash || '');
      if (m) { openShared(m[1]); return; }

      /* Paywall on the builder only. The recipient of a shared report is the
         player or the coach on the other side of the handover; they never
         need a pass to read it. */
      var Pro = window.GolfrawPro || null;
      if (Pro) {
        Pro.gate($('crGate'), 'coach-report', $('crBadge'));
        Pro.subscribe(function () { Pro.gate($('crGate'), 'coach-report', $('crBadge')); });
        if (Pro.noteCancelled()) msg('setMsg', 'Checkout was cancelled — nothing was charged.', 'bad');
      }

      if (!L) { msg('setMsg', 'Storage is unavailable in this browser, so there is nothing to report from.', 'bad'); return; }
      L.ready().then(function () {
        return Promise.all([L.getProfile(), L.getActiveBag(), L.listSessions(), L.listCompletedScorecards(), L.getToolState(TOOL)]);
      }).then(function (res) {
        data.profile = res[0]; data.bag = res[1]; data.sessions = res[2] || []; data.cards = res[3] || [];
        var saved = res[4] || {};
        $('fClient').value = saved.client || (data.profile && data.profile.displayName) || '';
        $('fCoach').value = saved.coach || '';
        $('fNotes').value = saved.notes || '';
        if (data.profile && data.profile.claimedHandicap !== null && data.profile.claimedHandicap !== undefined) $('fHcp').value = data.profile.claimedHandicap;
        var nS = fillSessions();
        sourceCard('srcSession', nS > 0, nS ? nS + ' session' + (nS > 1 ? 's' : '') + ' with shots' : 'None yet — log one in the Standing Order');
        var audited = 0; if (data.bag && data.bag.clubs) for (var i = 0; i < data.bag.clubs.length; i++) if (data.bag.clubs[i].usage !== null && data.bag.clubs[i].usage !== undefined) audited++;
        sourceCard('srcBag', audited > 0, data.bag && data.bag.clubs && data.bag.clubs.length ? data.bag.clubs.length + ' clubs, ' + audited + ' with usage entered' : 'No bag yet — fill the Bag Audit');
        sourceCard('srcRounds', data.cards.length > 0, data.cards.length ? data.cards.length + ' completed round' + (data.cards.length > 1 ? 's' : '') : 'None yet — tap one in the Tendency Engine');
        $('buildBtn').disabled = false;
      })['catch'](function () { msg('setMsg', 'Could not open local storage.', 'bad'); });

      L && L.subscribe(function (kind) { if (kind === 'clear' || kind === 'import') window.location.reload(); });
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
  </script>
'''

TAIL = '''  <script>window.__gr_consent=true;window.__gr_ads=false;</script>
'''


def main():
    p = shell_parts()
    doc = '\n'.join([
        rewrite_meta(p['head_top']), JSONLD,
        p['head_tail'].replace(PREMIUM_LINK, '').replace('</head>', STYLE + PREMIUM_LINK + HEAD_EXTRA + '</head>'),
        p['body_open'], MAIN, p['footer'], '', p['nav_script'], SCRIPT, p['gtag'], TAIL + '</body>', '', '</html>',
    ])
    doc = normalize_tool_page(doc, OUT)
    io.open(OUT, 'w', encoding='utf-8').write(doc)
    print('  wrote %s (%d bytes)' % (os.path.basename(OUT), len(doc.encode('utf-8'))))
    return 0


if __name__ == '__main__':
    sys.exit(main())
