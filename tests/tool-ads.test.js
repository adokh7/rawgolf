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
    addEventListener: () => {}
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
  const ctx = {
    window: win, setTimeout: (fn, ms) => { timers.push({ fn, ms }); return timers.length; }, clearTimeout: () => {},
    Date, JSON, Math, Object, Array, String, RegExp, Buffer
  };
  vm.createContext(ctx);
  vm.runInContext(SRC, ctx);
  return {
    win, scripts, listeners, timers, slots, obsList,
    interact() { (listeners.click || []).slice().forEach((f) => f()); },
    runTimers(maxMs) { const due = timers.filter((t) => !t.ran && t.ms <= maxMs); due.forEach((t) => { t.ran = true; t.fn(); }); },
    mutate() { obsList.slice().forEach((cb) => cb()); },
    adsScripts() { return scripts.filter((s) => /adsbygoogle|stub/.test(s.src || '')); },
    fcScripts() { return scripts.filter((s) => /fundingchoices/.test(s.src || '')); }
  };
}

const TEST = { units: { after_result: '1111111111', lower: '2222222222' }, autoAdsExcluded: true, adsSrc: '/stub.js' };
const now = Math.floor(Date.now() / 1000);

/* ---- shipped switches: dormant ---------------------------------------- */
{
  const b = browser({ slots: [slotEl('after_result', null, false), slotEl('lower', '#outWrap', true)] });
  check(b.win.GolfrawAds.reason() === 'auto_ads_not_excluded', 'shipped: a pilot page waits for Auto ads to be excluded, got ' + b.win.GolfrawAds.reason());
  check(b.slots.every((s) => s.removed), 'shipped: the empty slots are removed, not left as gaps');
  b.interact(); b.runTimers(7000);
  check(b.adsScripts().length === 0, 'shipped: adsbygoogle.js is never requested');
  check(b.fcScripts().length === 1, 'shipped: the consent message still loads once');
}
{
  const b = browser({ path: '/tools-scorecard-analyzer', test: TEST, host: 'localhost' });
  check(b.win.GolfrawAds.reason() === 'page_off', 'Round Card is not in the rollout yet');
}
{
  const b = browser({ path: '/tools-coach-report', host: 'localhost', test: TEST });
  check(b.win.GolfrawAds.reason() === 'page_off', 'the Pro preview tool never carries ads');
}

/* ---- the test switches only work on localhost ------------------------- */
{
  const b = browser({ test: TEST });
  check(b.win.GolfrawAds.reason() === 'auto_ads_not_excluded', 'production ignores __GR_ADS_TEST__');
  const c = browser({ storage: { gr_ads_test: JSON.stringify(TEST) } });
  check(c.win.GolfrawAds.reason() === 'auto_ads_not_excluded', 'production ignores the gr_ads_test storage key');
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
  check(A.ins && A.ins.slot === '1111111111', 'slot A renders the after_result unit');
  check(B.ins && B.ins.slot === '2222222222', 'slot B renders the lower unit with the result');
  check(/>Advertisements</.test(A.innerHTML), 'the label is "Advertisements"');
  check(A.getAttribute('role') === 'complementary', 'the slot is a labelled complementary region');
  b.runTimers(2500);   // consent wait ends
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

/* ---- failures collapse, never throw ----------------------------------- */
function failureCase(name, onScript, afterLoad, prep) {
  const A = slotEl('after_result', null, true);
  const b = browser({ host: 'localhost', test: TEST, slots: [A], onScript });
  if (prep) prep(b);
  b.runTimers(2500);
  return new Promise((resolve) => setImmediate(() => { if (afterLoad) afterLoad(b); check(b.win.GolfrawAds.slots()[0].state === 'collapsed', name + ': slot collapses (' + b.win.GolfrawAds.slots()[0].state + ')'); resolve(); }));
}

let pending = 1;
function finish() {
  if (--pending > 0) return;
  Promise.all([
    failureCase('blocked script', (s) => { if (/stub/.test(s.src)) setImmediate(() => s.onerror && s.onerror()); else if (s.onload) setImmediate(() => s.onload()); }),
    failureCase('push throws', (s) => { if (s.onload) setImmediate(() => s.onload()); }, null,
      (b) => { b.win.adsbygoogle = { push() { throw new Error('adsbygoogle failed'); } }; }),
    failureCase('no answer in time', (s) => { if (s.onload) setImmediate(() => s.onload()); }, (b) => b.runTimers(13000))
  ]).then(() => {
    if (failures.length) { console.error(failures.join('\n')); console.error(failures.length + ' of ' + checks + ' tool-ads checks failed'); process.exit(1); }
    console.log('tool-ads: ' + checks + ' checks passed');
  });
}
