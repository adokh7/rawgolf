/* GolfRaw tool ads: the consent loader and the manual ad slots for the tool
 * pages. One file for every tool page; the article pages keep their own
 * deferred Auto ads loader.
 *
 * The rules this file enforces (see docs/monetization-m1.md):
 *   - A tool answers first. No ad code loads, and no slot takes space, until
 *     the golfer has a result on screen. Slot A sits inside the result
 *     container, after its share actions, so it can never appear before a
 *     result or between an input and its button. Slot B sits low on the page,
 *     before the FAQ, and renders at the same moment as slot A.
 *   - GolfRaw Pro is ad-free. With a live Pro pass on this device the slots
 *     are removed and adsbygoogle.js is never requested.
 *   - Nothing here can break a tool. A blocked script, a failed request, no
 *     fill or an exception collapses the slot; the page never waits on it.
 *   - Auto ads must not run inside a calculator. The tool pages never load
 *     adsbygoogle.js until Auto ads are excluded from them in AdSense
 *     (AUTO_ADS_EXCLUDED), because Auto ads would otherwise place in-page and
 *     anchor ads among the controls.
 *   - Consent: Google's certified CMP (Funding Choices, "Privacy & messaging")
 *     loads first, on the first interaction or after 6s, exactly as on the
 *     rest of the site. AdSense reads its TCF string itself.
 *
 * Exposed as window.GolfrawAds. Plain ES5, no dependencies.
 */
(function (root) {
  'use strict';
  if (!root || !root.document || root.GolfrawAds) return;
  var doc = root.document;

  var CLIENT = 'ca-pub-8933725159594062';
  var FC_SRC = 'https://fundingchoicesmessages.google.com/i/pub-8933725159594062?ers=1';
  var ADS_SRC = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + CLIENT;

  /* ---------------------------------------------------------- switches --- */
  /* Responsive display ad units created in AdSense (Ads > By ad unit). An
     empty id switches that placement off: nothing renders, nothing loads. */
  var UNITS = { after_result: '', lower: '' };
  /* Set true only once every tool URL is on AdSense's Auto ads page
     exclusions list (Ads > By site > Page exclusions). */
  var AUTO_ADS_EXCLUDED = false;
  /* Rollout. Phase A: four tools. Add a slug here to switch its slots on. */
  var PAGES = {
    'tools-club-distance-calculator': true,
    'tools-tee-box-check': true,
    'tools-bag-audit': true,
    'tools-plays-like': true
  };

  var EVENTS = ['touchstart', 'scroll', 'mousemove', 'keydown', 'click', 'wheel'];
  var LABEL = 'Advertisements';           // one of the two labels Google allows
  var FILL_TIMEOUT = 12000;               // no status by then: blocked or offline

  /* A local test page may swap the switches and the script for a stub. Never
     honoured outside localhost, so production cannot be steered by it. */
  var local = /^(localhost|127\.0\.0\.1)$/.test(root.location && root.location.hostname || '');
  var T = null;
  if (local) {
    T = root.__GR_ADS_TEST__ || null;
    try { T = T || JSON.parse(root.localStorage.getItem('gr_ads_test') || 'null'); } catch (e) { T = null; }
  }
  if (T) {
    if (T.units) UNITS = T.units;
    if (typeof T.autoAdsExcluded === 'boolean') AUTO_ADS_EXCLUDED = T.autoAdsExcluded;
    if (T.pages) PAGES = T.pages;
    if (T.adsSrc) ADS_SRC = T.adsSrc;
    if (T.fcSrc) FC_SRC = T.fcSrc;
  }

  /* ------------------------------------------------------------- Pro ---- */
  /* The same pass lib/pro/pro.js stores: "v1.<payload>.<signature>", payload
     base64url JSON with an `exp` in seconds. The browser cannot check the
     signature, and does not need to here: a forged pass only removes ads for
     the person who forged it, which an ad blocker does anyway. Pro features
     themselves are verified by the server. */
  function proPass(now) {
    try {
      var t = root.localStorage.getItem('golfraw_pro_pass') || '';
      var parts = t.split('.');
      if (parts.length !== 3 || parts[0] !== 'v1') return false;
      var json = root.atob(parts[1].replace(/-/g, '+').replace(/_/g, '/'));
      var p = JSON.parse(json);
      return !!p && typeof p.exp === 'number' && p.exp * 1000 > (now || Date.now());
    } catch (e) { return false; }
  }

  function pageSlug() {
    var m = /^\/?(tools-[a-z0-9-]+?)(?:\.html)?\/?$/.exec(root.location && root.location.pathname || '');
    return m ? m[1] : '';
  }

  /* Why this page shows ads or not, as one word. */
  function decide() {
    if (proPass()) return 'pro';
    if (!PAGES[pageSlug()]) return 'page_off';
    if (!AUTO_ADS_EXCLUDED) return 'auto_ads_not_excluded';
    if (!UNITS.after_result && !UNITS.lower) return 'no_units';
    return 'eligible';
  }

  /* --------------------------------------------------------- loading ---- */
  function inject(src, isAds, done) {
    var s = doc.createElement('script');
    s.src = src; s.async = true;
    if (isAds) s.crossOrigin = 'anonymous';
    if (done) {
      s.onload = function () { done(true); };
      s.onerror = function () { done(false); };
    }
    (doc.head || doc.documentElement).appendChild(s);
    return s;
  }

  var consentAsked = false, consentReady = false, consentWaiters = [];
  function consentDone() {
    if (consentReady) return;
    consentReady = true;
    var w = consentWaiters; consentWaiters = [];
    for (var i = 0; i < w.length; i++) { try { w[i](); } catch (e) { /* never break the page */ } }
  }
  /* Load Google's CMP once. Ads wait for it, but never for more than 2.5s:
     a blocked CMP must not strand the page (AdSense then serves limited ads or
     none, by its own rules). */
  function askConsent() {
    if (consentAsked) return;
    consentAsked = true;
    if (root.__gr_consent === false) { consentDone(); return; }
    if (doc.querySelector('script[src^="https://fundingchoicesmessages.google.com/i/"]')) consentDone();
    else inject(FC_SRC, false, consentDone);
    setTimeout(consentDone, 2500);
  }
  function afterConsent(fn) { if (consentReady) fn(); else consentWaiters.push(fn); }

  var adsState = 'idle';                  // idle | loading | ready | failed
  var adsWaiters = [];
  function withAds(fn) {
    if (adsState === 'ready') return fn(true);
    if (adsState === 'failed') return fn(false);
    adsWaiters.push(fn);
    if (adsState === 'loading') return;
    adsState = 'loading';
    askConsent();
    afterConsent(function () {
      var already = doc.querySelector('script[src^="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"]');
      var finish = function (ok) {
        adsState = ok ? 'ready' : 'failed';
        var w = adsWaiters; adsWaiters = [];
        for (var i = 0; i < w.length; i++) { try { w[i](ok); } catch (e) { /* never break the page */ } }
      };
      if (already) finish(true); else inject(ADS_SRC, true, finish);
    });
  }

  /* ----------------------------------------------------------- slots ---- */
  var slots = [];                          // { el, placement, when, state }
  var n = 0;

  function css() {
    if (doc.getElementById('gr-ad-css')) return;
    var s = doc.createElement('style');
    s.id = 'gr-ad-css';
    s.textContent =
      /* An unrendered slot is an empty block: no height, no margin, nothing to shift. */
      '.gr-ad-slot{display:block}' +
      /* Rendered: a quiet rule, the label, and space reserved for a responsive
         unit so the fill does not push the page around. The top margin keeps
         a dead zone between the result's buttons and the ad. */
      '.gr-ad{margin:40px 0 28px;padding-top:14px;border-top:1px solid var(--line,#DADDD4);min-height:290px}' +
      '.gr-ad__label{margin:0 0 8px;font:600 10px/1.2 var(--gr-meta,Inter,system-ui,sans-serif);letter-spacing:.16em;' +
      'text-transform:uppercase;color:#5B665E}' +
      '.gr-ad ins.adsbygoogle{display:block;width:100%;min-height:250px}' +
      'ins.adsbygoogle[data-ad-status="unfilled"]{display:none!important}' +
      '.gr-ad[data-state="collapsed"]{display:none!important}' +
      '@media print{.gr-ad{display:none!important}}';
    (doc.head || doc.documentElement).appendChild(s);
  }

  /* Shown on screen: displayed and with a box. A slot inside a hidden result
     container has no box until the result appears. */
  function displayed(el) { return !!el && el.getClientRects().length > 0; }

  function whenOf(slot) {
    var sel = slot.el.getAttribute('data-gr-ad-when');
    return sel ? doc.querySelector(sel) : slot.el;
  }

  function collapse(slot) {
    slot.state = 'collapsed';
    slot.el.setAttribute('data-state', 'collapsed');
  }

  function render(slot) {
    if (slot.state !== 'waiting') return;
    slot.state = 'rendering';
    var id = 'gr-ad-label-' + (++n);
    var el = slot.el;
    el.className += ' gr-ad';
    el.setAttribute('role', 'complementary');
    el.setAttribute('aria-labelledby', id);
    el.innerHTML = '<p class="gr-ad__label" id="' + id + '">' + LABEL + '</p>' +
      '<ins class="adsbygoogle" style="display:block" data-ad-client="' + CLIENT + '" data-ad-slot="' +
      UNITS[slot.placement] + '" data-ad-format="auto" data-full-width-responsive="true"></ins>';
    var ins = el.getElementsByTagName('ins')[0];

    withAds(function (ok) {
      if (!ok) { collapse(slot); return; }
      try { (root.adsbygoogle = root.adsbygoogle || []).push({}); }
      catch (e) { collapse(slot); return; }
      slot.state = 'requested';
      var settle = function () {
        var st = ins.getAttribute('data-ad-status');
        if (st === 'unfilled') collapse(slot);
        else if (st) slot.state = st;          // filled / unfill-optimized: AdSense handles it
      };
      if (root.MutationObserver) new root.MutationObserver(settle).observe(ins, { attributes: true, attributeFilter: ['data-ad-status'] });
      setTimeout(function () { if (!ins.getAttribute('data-ad-status')) collapse(slot); }, FILL_TIMEOUT);
    });
  }

  /* Render every waiting slot whose trigger is on screen. A slot's trigger is
     itself (slot A, inside the result) or the element named in
     data-gr-ad-when (slot B waits for the result container). */
  var resultSeen = false, watcher = null;
  function check() {
    var waiting = 0;
    for (var i = 0; i < slots.length; i++) {
      var s = slots[i];
      if (s.state !== 'waiting') continue;
      if (displayed(whenOf(s)) && displayed(s.el)) { resultSeen = true; render(s); }
      else waiting++;
    }
    /* Every slot has rendered or collapsed: stop watching the page. */
    if (!waiting && watcher) { watcher.disconnect(); watcher = null; }
  }

  var reason = 'not_started';
  function mount() {
    reason = decide();
    var els = doc.querySelectorAll('[data-gr-ad]');
    for (var i = 0; i < els.length; i++) {
      var el = els[i], placement = el.getAttribute('data-gr-ad');
      el.removeAttribute('hidden');
      if (reason !== 'eligible' || !UNITS[placement]) { el.parentNode.removeChild(el); continue; }
      slots.push({ el: el, placement: placement, state: 'waiting' });
    }
    if (!slots.length) return;
    css();
    /* Results appear by a class or attribute change on their container. */
    if (root.MutationObserver) {
      watcher = new root.MutationObserver(function () { try { check(); } catch (e) { /* ignore */ } });
      watcher.observe(doc.body, { attributes: true, subtree: true, attributeFilter: ['class', 'hidden', 'style'] });
    }
    check();
  }

  /* The CMP loads for every visitor, ads or not, as on every GolfRaw page. */
  function startConsent() {
    var started = false, timer;
    var go = function () {
      if (started) return;
      started = true;
      clearTimeout(timer);
      for (var i = 0; i < EVENTS.length; i++) root.removeEventListener(EVENTS[i], go, { passive: true });
      askConsent();
    };
    for (var i = 0; i < EVENTS.length; i++) root.addEventListener(EVENTS[i], go, { passive: true });
    timer = setTimeout(go, 6000);
  }

  function boot() {
    try { startConsent(); } catch (e) { /* never break the page */ }
    try { mount(); } catch (e) { /* never break the page */ }
  }

  root.GolfrawAds = {
    version: 1,
    reason: function () { return reason; },
    slots: function () { return slots.map(function (s) { return { placement: s.placement, state: s.state }; }); },
    resultSeen: function () { return resultSeen; },
    proPass: proPass,
    decide: decide
  };

  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', boot); else boot();
})(typeof window !== 'undefined' ? window : null);
