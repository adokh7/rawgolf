'use strict';

// lib/ads/tool-ads.js in a fake browser: who is eligible, what gets loaded and
// when, and that every failure collapses the slot instead of breaking the page.
// The real layout and a stubbed AdSense were checked in the browser; this pins
// the decisions so a later edit cannot quietly start loading ads for Pro
// subscribers, before a result, or on a page Auto ads could take over.

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const SRC = fs.readFileSync(path.join(__dirname, '..', 'lib', 'ads', 'tool-ads.js'), 'utf8');
const failures = [];
let checks = 0;
function check(c, m) { checks++; if (!c) failures.push(m); }

function b64url(obj) { return Buffer.from(JSON.stringify(obj)).toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, ''); }
function pass(expSec) { return 'v1.' + b64url({ plan: 'pro', exp: expSec }) + '.sig'; }

function slotEl(placement, when, visible) {
  const attrs = { 'data-gr-ad': placement, hidden: '' };
  if (when) attrs['data-gr-ad-when'] = when;
  const el = {
    attrs, className: 'gr-ad-slot', removed: false, visible, ins: null, _html: '',
    getAttribute: (k) => (k in attrs ? attrs[k] : null),
    setAttribute: (k, v) => { attrs[k] = String(v); },
    removeAttribute: (k) => { delete attrs[k]; },
    getClientRects: () => (el.visible && !el.removed ? [1] : []),
    getElementsByTagName: (t) => (t === 'ins' && el.ins ? [el.ins] : []),
    contains: () => false
  };
  Object.defineProperty(el, 'innerHTML', {
    set(v) {
      el._html = v;
      const m = /data-ad-slot="([^"]*)"/.exec(v);
      el.ins = { slot: m && m[1], attrs: {}, getAttribute(k) { return k in this.attrs ? this.attrs[k] : null; },
        setAttribute(k, val) { this.attrs[k] = val; (el.observers || []).forEach((cb) => cb()); } };
    },
    get() { return el._html; }
  });
  el.parentNode = { removeChild: () => { el.removed = true; } };
  return el;
}

function browser(opts) {
  const scripts = [];
  const listeners = {};
  const docListeners = {};
  const timers = [];
  const slots = opts.slots || [];
  const results = opts.results || {};
  const store = Object.assign({}, opts.storage || {});
  const doc = {
    readyState: 'complete',
    head: { appendChild: (s) => { scripts.push(s); if (s.src && opts.onScript) opts.onScript(s); } },
    documentElement: {},
    body: {},
    createElement: (t) => ({ tag: t }),
    getElementById: () => null,
    querySelector: (sel) => {
      const m = /^script\[src\^="([^"]+)"\]$/.exec(sel);
      if (m) return scripts.find((s) => s.src && s.src.indexOf(m[1]) === 0) || null;
      return results[sel] || null;
    },
    querySelectorAll: (sel) => (sel === '[data-gr-ad]' ? slots.filter((s) => !s.removed) : []),
    addEventListener: (t, fn) => { (docListeners[t] = docListeners[t] || []).push(fn); }
  };
  const win = {
    document: doc,
    location: { hostname: opts.host || 'www.golfraw.com', pathname: opts.path || '/tools-tee-box-check' },
    localStorage: { getItem: (k) => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v); } },
    atob: (s) => Buffer.from(s, 'base64').toString('binary'),
    addEventListener: (t, fn) => { (listeners[t] = listeners[t] || []).push(fn); },
    removeEventListener: (t, fn) => { listeners[t] = (listeners[t] || []).filter((f) => f !== fn); },
    MutationObserver: function (cb) {
      this.observe = (target) => { if (target && target.getAttribute) { target.observersFor = true; } obsList.push(cb); };
      this.disconnect = () => {};
    },
    __gr_consent: true
  };
  const obsList = [];
  if (opts.test) win.__GR_ADS_TEST__ = opts.test;
  // A fake clock: timers and intervals fire only when the test advances it.
  let clock = 0;
  const base = Date.now();
  const FakeDate = { now: () => base + clock };
  const ctx = {
    window: win,
    setTimeout: (fn, ms) => { timers.push({ fn, at: clock + ms }); return timers.length; },
    setInterval: (fn, ms) => { timers.push({ fn, at: clock + ms, every: ms }); return timers.length; },
    clearTimeout: (id) => { if (timers[id - 1]) timers[id - 1].ran = true; },
    clearInterval: (id) => { if (timers[id - 1]) timers[id - 1].ran = true; },
    Date: FakeDate, JSON, Math, Object, Array, String, RegExp, Buffer
  };
  vm.createContext(ctx);
  vm.runInContext(SRC, ctx);
  return {
    win, scripts, listeners, timers, slots, obsList,
    interact() { (listeners.click || []).slice().forEach((f) => f()); },
    setHidden(h) { doc.hidden = h; (docListeners.visibilitychange || []).slice().forEach((f) => f()); },
    runTimers(ms) {
      const end = clock + ms;
      for (;;) {
        const next = timers.filter((t) => !t.ran && t.at <= end).sort((a, b) => a.at - b.at)[0];
        if (!next) break;
        clock = next.at;
        if (next.every) next.at += next.every; else next.ran = true;
        next.fn();
      }
      clock = end;
    },
    mutate() { obsList.slice().forEach((cb) => cb()); },
    adsScripts() { return scripts.filter((s) => /adsbygoogle|stub/.test(s.src || '')); },
    fcScripts() { return scripts.filter((s) => /fundingchoices/.test(s.src || '')); }
  };
}

const TEST = { units: { after_result: '1111111111', lower: '2222222222' }, autoAdsExcluded: true, adsSrc: '/stub.js' };
const now = Math.floor(Date.now() / 1000);

/* ---- shipped switches: live on the four pilots only ------------------- */
{
  const units = /var UNITS = \{ after_result: '(\d{10})', lower: '(\d{10})' \};/.exec(SRC);
  check(units && units[1] === '8457096514' && units[2] === '1432433875', 'shipped: the two real AdSense unit ids');
  check(/var ADS_SRC = 'https:\/\/pagead2\.googlesyndication\.com\/pagead\/js\/adsbygoogle\.js\?client=' \+ CLIENT;/.test(SRC),
    'tool pages load Google\'s standard loader');
  const autoOff = /var AUTO_ADS_EXCLUDED = (true|false);/.exec(SRC)[1] === 'true';
  for (const p of ['/tools-club-distance-calculator', '/tools-tee-box-check', '/tools-plays-like', '/tools-bag-audit']) {
    const b = browser({ path: p });
    check(b.win.GolfrawAds.reason() === (autoOff ? 'eligible' : 'auto_ads_not_excluded'),
      'shipped: ' + p + ' follows AUTO_ADS_EXCLUDED, got ' + b.win.GolfrawAds.reason());
    const q = browser({ path: p, storage: { gr_adtest: '1' } });
    check(q.win.GolfrawAds.reason() === 'eligible', 'a QA browser (gr_adtest=1) can check ' + p + ' live');
  }
  for (const p of ['/tools-scorecard-analyzer', '/tools-settle-up-calculator', '/tools-coach-report', '/tools-gimme-audit', '/tools-round-autopsy']) {
    const b = browser({ path: p, slots: [slotEl('after_result', null, true)] });
    check(b.win.GolfrawAds.reason() === 'page_off', 'shipped: ' + p + ' stays off');
    check(b.slots.every((s) => s.removed), 'shipped: slots on an off page are removed, not left as gaps');
    b.interact(); b.runTimers(20000); b.mutate();
    check(b.adsScripts().length === 0, 'shipped: ' + p + ' never requests adsbygoogle.js');
    check(b.fcScripts().length === 1, 'shipped: ' + p + ' still loads the consent message once');
  }
}
{
  // a pilot with no result yet: the module waits, loads nothing
  const A = slotEl('after_result', null, false);
  const b = browser({ slots: [A, slotEl('lower', '#outWrap', true)] });
  b.interact(); b.runTimers(7000); b.mutate();
  check(b.adsScripts().length === 0, 'shipped pilot: no ad code before a result');
  check(A.ins === null, 'shipped pilot: no unit before a result');
}

/* ---- the test switches only work on localhost ------------------------- */
{
  const off = { units: TEST.units, autoAdsExcluded: true, pages: {} };
  const b = browser({ test: off, storage: { gr_adtest: '1' } });
  check(b.win.GolfrawAds.reason() === 'eligible', 'production ignores __GR_ADS_TEST__');
  const c = browser({ storage: { gr_ads_test: JSON.stringify(off), gr_adtest: '1' } });
  check(c.win.GolfrawAds.reason() === 'eligible', 'production ignores the gr_ads_test storage key');
  const d = browser({ host: 'localhost', test: off });
  check(d.win.GolfrawAds.reason() === 'page_off', 'localhost honours the test switches');
}

/* ---- QA test mode ------------------------------------------------------ */
{
  const A = slotEl('after_result', null, true);
  browser({ slots: [A], storage: { gr_adtest: '1' } }).runTimers(11000);
  check(/data-adtest="on"/.test(A.innerHTML), 'gr_adtest=1 asks AdSense for test ads');
  check(/data-ad-slot="8457096514"/.test(A.innerHTML), 'slot A requests unit 8457096514');
  check(/data-ad-format="rectangle" data-full-width-responsive="false"/.test(A.innerHTML), 'units are rectangles, never full-screen');
  const B = slotEl('after_result', null, true);
  browser({ slots: [B], host: 'localhost', test: TEST }).runTimers(11000);
  check(!/data-adtest/.test(B.innerHTML) && B.ins, 'everyone else gets normal units');
}

/* ---- Pro -------------------------------------------------------------- */
{
  const b = browser({ host: 'localhost', test: TEST, storage: { golfraw_pro_pass: pass(now + 86400) },
    slots: [slotEl('after_result', null, true), slotEl('lower', '#outWrap', true)] });
  check(b.win.GolfrawAds.reason() === 'pro', 'a live Pro pass switches ads off');
  check(b.slots.every((s) => s.removed), 'Pro: slots removed, no placeholders');
  b.interact(); b.runTimers(20000);
  check(b.adsScripts().length === 0, 'Pro: adsbygoogle.js is never requested');
  check(b.fcScripts().length === 1, 'Pro: the consent message still loads (analytics)');
}
for (const [label, value] of [['expired', pass(now - 60)], ['malformed', 'garbage'], ['wrong version', 'v2.' + b64url({ exp: now + 999 }) + '.x'], ['no exp', 'v1.' + b64url({ plan: 'pro' }) + '.x']]) {
  const b = browser({ host: 'localhost', test: TEST, storage: { golfraw_pro_pass: value } });
  check(b.win.GolfrawAds.reason() === 'eligible', 'an ' + label + ' pass does not count as Pro');
}

/* ---- result first ----------------------------------------------------- */
{
  const outWrap = { visible: false, getClientRects() { return this.visible ? [1] : []; } };
  const A = slotEl('after_result', null, false);
  const B = slotEl('lower', '#outWrap', true);
  let pushed = 0;
  const b = browser({ host: 'localhost', test: TEST, slots: [A, B], results: { '#outWrap': outWrap },
    onScript: (s) => { if (/stub/.test(s.src)) setImmediate(() => s.onload && s.onload()); else if (s.onload) setImmediate(() => s.onload()); } });
  check(b.win.GolfrawAds.reason() === 'eligible', 'test switches make the pilot eligible');
  b.mutate();
  check(b.adsScripts().length === 0, 'no ad code before a result');
  check(A.ins === null && B.ins === null, 'no ad unit before a result');
  // the result appears: its container and slot A inside it become visible
  outWrap.visible = true; A.visible = true;
  b.mutate();
  check(A.ins === null, 'no unit until the consent script has answered or given up');
  b.runTimers(2500);   // the consent script has had its chance
  check(A.ins === null, 'still no unit: the TCF API may appear a moment after the loader');
  b.runTimers(8500);   // no TCF API after 8s more: treat the CMP as blocked
  check(A.ins && A.ins.slot === '1111111111', 'slot A renders the after_result unit');
  check(B.ins && B.ins.slot === '2222222222', 'slot B renders the lower unit with the result');
  check(/>Advertisements</.test(A.innerHTML), 'the label is "Advertisements"');
  check(A.getAttribute('role') === 'complementary', 'the slot is a labelled complementary region');
  setImmediate(() => {
    check(b.adsScripts().length === 1, 'adsbygoogle.js loads once for both slots');
    b.win.adsbygoogle = b.win.adsbygoogle || [];
    // no fill: AdSense marks the unit unfilled
    A.ins.setAttribute('data-ad-status', 'unfilled');
    b.mutate();
    check(A.getAttribute('data-state') === 'collapsed' || b.win.GolfrawAds.slots()[0].state === 'collapsed', 'an unfilled unit collapses its slot');
    B.ins.setAttribute('data-ad-status', 'filled');
    b.mutate();
    check(b.win.GolfrawAds.slots()[1].state === 'filled', 'a filled unit stays');
    finish();
  });
}

/* ---- Google's consent message (TCF) ----------------------------------- */
function tcfBrowser(events) {
  const A = slotEl('after_result', null, true);
  const b = browser({ host: 'localhost', test: TEST, slots: [A] });
  let listener = null;
  b.win.__tcfapi = (cmd, v, cb) => { if (cmd === 'addEventListener') listener = cb; };
  b.mutate();
  return { A, b, send: (d) => { listener && listener(d, true); } };
}
{
  const t = tcfBrowser();
  t.send({ gdprApplies: true, eventStatus: 'cmpuishown' });
  t.b.runTimers(20000);
  check(t.A.ins === null, 'message open: the slot waits and takes no space');
  check(t.b.win.GolfrawAds.slots()[0].state === 'waiting', 'message open: nothing collapses or times out');
  check(t.b.adsScripts().length === 0, 'message open: no ad code yet');
  t.send({ gdprApplies: true, eventStatus: 'useractioncomplete' });
  check(t.A.ins && t.A.ins.slot === '1111111111', 'a choice made: the slot renders');
}
{
  const t = tcfBrowser();
  t.send({ gdprApplies: true, eventStatus: 'tcloaded' });
  check(t.A.ins !== null, 'a returning reader who already chose: renders at once');
}
{
  const t = tcfBrowser();
  t.send({ gdprApplies: false, eventStatus: 'tcloaded' });
  check(t.A.ins !== null, 'outside Europe: renders at once');
}

{
  // What happened live: Google's loader finishes, __tcfapi appears a second
  // later, and the message is open. The slot must wait, not give up at 8s.
  const A = slotEl('after_result', null, true);
  const b = browser({ host: 'localhost', test: TEST, slots: [A] });
  b.runTimers(2500);
  check(A.ins === null, 'late TCF API: nothing before the API appears');
  let listener = null;
  b.win.__tcfapi = (cmd, v, cb) => { if (cmd === 'addEventListener') { listener = cb; cb({ gdprApplies: true, eventStatus: 'cmpuishown' }, true); } };
  b.runTimers(30000);
  check(A.ins === null && b.win.GolfrawAds.slots()[0].state === 'waiting', 'late TCF API with the message open: still waiting, no gap');
  listener({ gdprApplies: true, eventStatus: 'useractioncomplete' }, true);
  check(A.ins && A.ins.slot === '1111111111', 'late TCF API: renders on the choice');
}

/* ---- failures collapse, never throw ----------------------------------- */
function failureCase(name, onScript, afterLoad, prep) {
  const A = slotEl('after_result', null, true);
  const b = browser({ host: 'localhost', test: TEST, slots: [A], onScript });
  if (prep) prep(b);
  b.runTimers(11000);
  return new Promise((resolve) => setImmediate(() => { if (afterLoad) afterLoad(b); check(b.win.GolfrawAds.slots()[0].state === 'collapsed', name + ': slot collapses (' + b.win.GolfrawAds.slots()[0].state + ')'); resolve(); }));
}

/* AdSense requests nothing in a background tab, so the no-answer clock only
   counts visible time: a reader who switches tabs after a result does not
   come back to a collapsed slot that AdSense was about to fill. */
function hiddenTabCase() {
  const A = slotEl('after_result', null, true);
  const b = browser({ host: 'localhost', test: TEST, slots: [A], onScript: (s) => { if (s.onload) setImmediate(() => s.onload()); } });
  b.setHidden(true);
  b.runTimers(11000);
  return new Promise((resolve) => setImmediate(() => {
    const st = () => b.win.GolfrawAds.slots()[0].state;
    b.runTimers(30000);
    check(st() === 'requested', 'a background tab never runs the no-answer clock (' + st() + ')');
    b.setHidden(false); b.runTimers(6000); b.setHidden(true); b.runTimers(30000);
    check(st() === 'requested', 'hiding the tab again stops the clock (' + st() + ')');
    b.setHidden(false); b.runTimers(11000);
    check(st() === 'requested', 'coming back restarts the full 12s (' + st() + ')');
    b.runTimers(2000);
    check(st() === 'collapsed', 'visible and silent for 12s: the slot collapses (' + st() + ')');
    resolve();
  }));
}

let pending = 1;
function finish() {
  if (--pending > 0) return;
  Promise.all([
    failureCase('blocked script', (s) => { if (/stub/.test(s.src)) setImmediate(() => s.onerror && s.onerror()); else if (s.onload) setImmediate(() => s.onload()); }),
    failureCase('push throws', (s) => { if (s.onload) setImmediate(() => s.onload()); }, null,
      (b) => { b.win.adsbygoogle = { push() { throw new Error('adsbygoogle failed'); } }; }),
    failureCase('no answer in time', (s) => { if (s.onload) setImmediate(() => s.onload()); }, (b) => b.runTimers(13000)),
    hiddenTabCase()
  ]).then(() => {
    if (failures.length) { console.error(failures.join('\n')); console.error(failures.length + ' of ' + checks + ' tool-ads checks failed'); process.exit(1); }
    console.log('tool-ads: ' + checks + ' checks passed');
  });
}
