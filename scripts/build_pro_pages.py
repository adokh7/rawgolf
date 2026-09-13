#!/usr/bin/env python3
"""Generate the two Pro account pages from the shared tool shell.

  pro-thanks.html   Stripe's success_url. Claims the pass by session id and
                    stores it in this browser. Bookmarkable: the same URL
                    restores the pass on another device.
  pro-restore.html  Target of the restore link sent by email (#t=...). Also
                    lets a reader request a restore email.

Both are noindex: they are account pages, not content. Re-runnable; then run
wire_locker.py and apply_theme.py.
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHELL = os.path.join(ROOT, 'tools-bag-audit.html')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tool_shell import shell_parts as _shell_parts

SITE = 'https://www.golfraw.com'
PRO_VER = '2'


def rewrite_meta(s, slug, title, desc):
    s = re.sub(r'<title>.*?</title>', '<title>%s</title>' % title, s, flags=re.S)
    for pat, val in [(r'(<meta name="description" content=")[^"]*(")', desc), (r'(<meta property="og:title" content=")[^"]*(")', title),
                     (r'(<meta property="og:description" content=")[^"]*(")', desc), (r'(<meta name="twitter:title" content=")[^"]*(")', title),
                     (r'(<meta name="twitter:description" content=")[^"]*(")', desc)]:
        s = re.sub(pat, lambda m, v=val: m.group(1) + v + m.group(2), s)
    s = re.sub(r'(<link rel="canonical" href=")[^"]*(")', r'\g<1>%s/%s\g<2>' % (SITE, slug), s)
    s = re.sub(r'(<meta property="og:url" content=")[^"]*(")', r'\g<1>%s/%s\g<2>' % (SITE, slug), s)
    s = re.sub(r'<meta name="robots" content="[^"]*">', '<meta name="robots" content="noindex, nofollow">', s)
    return s


STYLE = '''<style>
    .pp-wrap { max-width: 640px; margin: 0 auto }
    .pp-card { background: var(--white); border: 2px solid var(--ink); padding: 26px 28px; margin-top: 8px }
    .pp-card h2 { font-size: 22px; margin: 0 0 10px; padding: 0; border: 0 }
    .pp-card p { font-size: 15px; line-height: 1.6; margin: 0 0 12px }
    .pp-status { display: inline-block; padding: 6px 12px; border-radius: 999px; font: 800 11px/1.2 'Archivo', system-ui, sans-serif;
      letter-spacing: .12em; text-transform: uppercase; background: var(--fairway); color: #fff; margin-bottom: 14px }
    .pp-status.wait { background: var(--line); color: var(--grey) } .pp-status.bad { background: #FFF4DD; color: #8A5E00 }
    .pp-kv { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 14px 0 }
    .pp-kv div { padding: 10px 12px; border: 1px solid var(--line) }
    .pp-kv b { display: block; font-family: 'IBM Plex Mono', monospace; font-size: 10px; letter-spacing: .12em; text-transform: uppercase; color: var(--grey); margin-bottom: 3px }
    .so-go { min-height: 48px; padding: 0 20px; background: var(--ink); color: #fff; border: 2px solid var(--ink);
      font: 900 13px/1 'Archivo', system-ui, sans-serif; letter-spacing: .08em; text-transform: uppercase; cursor: pointer;
      display: inline-flex; align-items: center; text-decoration: none; transition: background .15s }
    .so-go:hover { background: var(--fairway); border-color: var(--fairway); color: #fff }
    .so-go.alt { background: var(--white); color: var(--ink) } .so-go.alt:hover { background: var(--paper); color: var(--ink); border-color: var(--ink) }
    .pp-acts { display: flex; flex-wrap: wrap; gap: 9px; margin-top: 14px }
    .pp-form label { display: block; font: 800 10.5px/1 'Archivo', system-ui, sans-serif; letter-spacing: .08em; text-transform: uppercase; color: var(--grey); margin: 14px 0 6px }
    .pp-form input { width: 100%; min-height: 48px; padding: 10px 12px; border: 2px solid var(--ink); font: 600 15px/1.2 'Archivo', system-ui, sans-serif }
    .pp-msg { margin-top: 11px; padding: 10px 12px; border: 2px solid var(--ink); background: #fff; font-size: 13px; font-weight: 600; line-height: 1.45; display: none }
    .pp-msg.on { display: block } .pp-msg.bad { border-color: #C98A00; color: #8A5E00 } .pp-msg.good { border-color: var(--fairway); color: var(--fairway) }
    .pp-fine { font-size: 12.5px; color: var(--grey); line-height: 1.55; margin-top: 14px }
    @media (max-width: 520px) { .pp-kv { grid-template-columns: 1fr } .pp-card { padding: 20px 18px } }
  </style>
  <script src="/lib/pro/pro.js?v=__PRO_VER__" defer></script>
'''.replace('__PRO_VER__', PRO_VER)

THANKS_MAIN = '''
  <div class="hub-hero"><div class="wrap"><div class="eyebrow">GolfRaw &middot; PRO</div><h1>Thank you</h1>
    <p>Your pass is being switched on in this browser. Keep this page&rsquo;s address: opening it on another
      device switches Pro on there too.</p></div></div>
  <div class="tool-body"><div class="wrap"><div class="pp-wrap">
    <div class="pp-card" aria-live="polite">
      <span class="pp-status wait" id="ppStatus">Confirming with Stripe&hellip;</span>
      <h2 id="ppHead">One moment</h2>
      <p id="ppText">We are confirming the payment and issuing your pass.</p>
      <div class="pp-kv" id="ppKv" hidden><div><b>Plan</b><span id="ppPlan"></span></div><div><b>Valid until</b><span id="ppExp"></span></div></div>
      <div class="pp-acts" id="ppActs" hidden>
        <a class="so-go" href="/tools-standing-order">Open the Standing Order &rarr;</a>
        <a class="so-go alt" href="/tools-coach-report">Build a coach report</a>
      </div>
      <div class="pp-msg" id="ppMsg" role="status"></div>
      <p class="pp-fine">Your pass is stored in this browser only and never uploaded. To use Pro on another
        device, open this same page there, or use the restore link from your welcome email. Stripe&rsquo;s
        receipt email is your record of purchase. Questions: <a href="mailto:contact@golfraw.com">contact@golfraw.com</a>.</p>
    </div>
  </div></div></div>
'''

RESTORE_MAIN = '''
  <div class="hub-hero"><div class="wrap"><div class="eyebrow">GolfRaw &middot; PRO</div><h1>Restore your Pro pass</h1>
    <p>Pro lives in your browser, never on our servers. This page puts it back on a new device.</p></div></div>
  <div class="tool-body"><div class="wrap"><div class="pp-wrap">
    <div class="pp-card" aria-live="polite">
      <span class="pp-status wait" id="ppStatus">Checking&hellip;</span>
      <h2 id="ppHead">Restore</h2>
      <p id="ppText">If you opened a restore link, hold on a second.</p>
      <div class="pp-kv" id="ppKv" hidden><div><b>Plan</b><span id="ppPlan"></span></div><div><b>Valid until</b><span id="ppExp"></span></div></div>
      <div class="pp-acts" id="ppActs" hidden>
        <a class="so-go" href="/tools-standing-order">Open the Standing Order &rarr;</a>
        <a class="so-go alt" href="/tools-coach-report">Build a coach report</a>
      </div>
      <form class="pp-form" id="ppForm" novalidate hidden>
        <label for="ppEmail">Email me a restore link</label>
        <input type="email" id="ppEmail" autocomplete="email" placeholder="the address you paid with">
        <div class="pp-acts"><button type="submit" class="so-go">Send the link</button></div>
      </form>
      <div class="pp-msg" id="ppMsg" role="status"></div>
      <p class="pp-fine">No link and no email? The receipt page from your purchase (the page Stripe returned you
        to) also restores Pro when opened on any device. Questions: <a href="mailto:contact@golfraw.com">contact@golfraw.com</a>.</p>
    </div>
  </div></div></div>
'''

SCRIPT = r'''  <script>
    var $ = function (id) { return document.getElementById(id); };
    function esc(s) { return String(s === null || s === undefined ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
    function show(kind, head, text) { $('ppStatus').className = 'pp-status ' + kind; $('ppStatus').textContent = kind === 'ok' ? 'Pro is on' : (kind === 'bad' ? 'Not confirmed' : 'Working'); $('ppHead').textContent = head; $('ppText').innerHTML = text; }
    function done(r) {
      if (!r.ok) { show('bad', 'That did not work', esc(r.error)); if ($('ppForm')) $('ppForm').hidden = false; return; }
      show('ok', 'Welcome to GolfRaw Pro', 'Your pass is stored in this browser' + (r.email ? ' for ' + esc(r.email) : '') + '. Every Pro feature is open now.');
      $('ppPlan').textContent = r.plan || 'Pro'; $('ppExp').textContent = r.exp ? new Date(r.exp * 1000).toLocaleDateString() : '—';
      $('ppKv').hidden = false; $('ppActs').hidden = false;
    }
    function boot() {
      var Pro = window.GolfrawPro;
      if (!Pro) { show('bad', 'Something is missing', 'The Pro script did not load. Reload the page.'); return; }
      var q = new URLSearchParams(location.search), sid = q.get('session_id');
      var t = /[#&]t=([A-Za-z0-9_.-]+)/.exec(location.hash || '');
      var L = window.GolfrawLocker; var start = L && L.ready ? L.ready()['catch'](function () {}) : Promise.resolve();
      start.then(function () {
        if (sid) return Pro.claim(sid).then(done)['catch'](function () { done({ ok: false, error: 'Could not reach the server. Keep this page and try again in a minute.' }); });
        if (t) return Pro.restore(t[1]).then(done)['catch'](function () { done({ ok: false, error: 'Could not reach the server. Try the link again in a minute.' }); });
        /* no credential in the URL: show what this browser holds, and the form */
        return Pro.ready().then(function (status) {
          if (status === 'pro') { var p = Pro.payload(); done({ ok: true, plan: p.plan, exp: p.exp }); }
          else { show('wait', 'No pass in this browser yet', 'Enter the email you paid with and we will send a link that switches Pro on here.'); if ($('ppForm')) $('ppForm').hidden = false; else $('ppText').innerHTML = 'Open the receipt page from your purchase, or request a restore link from any Pro tool.'; }
        });
      });
      var f = $('ppForm');
      if (f) f.addEventListener('submit', function (e) {
        e.preventDefault(); var email = $('ppEmail').value.trim(), m = $('ppMsg');
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) { m.className = 'pp-msg on bad'; m.textContent = 'That does not look like an email address.'; return; }
        m.className = 'pp-msg on good'; m.textContent = 'Sending…';
        Pro.requestRestore(email).then(function (r) {
          if (r.ok) { m.className = 'pp-msg on good'; m.textContent = r.message || 'If that address has a Pro pass, a link is on its way.'; }
          else if (r.reason === 'restore-unavailable') { m.className = 'pp-msg on bad'; m.textContent = 'Email restore is not switched on yet — open the receipt page from your purchase instead.'; }
          else { m.className = 'pp-msg on bad'; m.textContent = r.error || 'Could not send the link.'; }
        });
      });
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
  </script>
'''

TAIL = '''  <script>window.__gr_consent=true;window.__gr_ads=false;</script>
'''

PAGES = [
    ('pro-thanks', 'Thank you | GolfRaw', 'Your GolfRaw Pro pass is being switched on.', THANKS_MAIN),
    ('pro-restore', 'Restore your pass | GolfRaw', 'Restore your GolfRaw Pro pass on this device.', RESTORE_MAIN),
]


def main():
    p = _shell_parts(SHELL)
    for slug, title, desc, main in PAGES:
        doc = '\n'.join([
            rewrite_meta(p['head_top'], slug, title, desc),
            p['head_tail'].replace('</head>', STYLE + '</head>'),
            p['body_open'], main, p['footer'], '', p['nav_script'], SCRIPT, p['gtag'], TAIL + '</body>', '', '</html>',
        ])
        out = os.path.join(ROOT, slug + '.html')
        io.open(out, 'w', encoding='utf-8').write(doc)
        print('  wrote %s (%d bytes)' % (slug + '.html', len(doc.encode('utf-8'))))
    return 0


if __name__ == '__main__':
    sys.exit(main())
