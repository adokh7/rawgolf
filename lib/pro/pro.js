/* ==========================================================================
   GOLFRAW PRO — client (window.GolfrawPro)
   --------------------------------------------------------------------------
   Decides whether a Pro feature is open, gated, or unlocked, and owns the
   paywall UI. Three states:

     preview  — /api/pro-config says enabled:false (Stripe not configured) OR
                the config cannot be fetched at all. The feature stays open,
                badged "free in preview". Failing OPEN is deliberate: an
                outage must never lock a paid customer or a preview reader out
                of a tool that runs entirely in their browser.
     gated    — Pro is on sale and this browser holds no valid pass.
     pro      — a pass with a future expiry is stored in the Locker's meta
                store (localStorage when the Locker is unavailable).

   The pass is an HMAC token minted by the server. The browser can read its
   payload (plan, expiry) but cannot verify its signature, so when online it
   asks /api/pro-verify and drops a token the server rejects. Offline, it
   trusts the token until its expiry. Gating here is a convenience for
   honest readers, not a security boundary — the Pro outputs are built on the
   device, so there is nothing on a server to protect.
   ========================================================================== */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.GolfrawPro = factory();
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var META_KEY = 'pro.pass', LS_KEY = 'golfraw_pro_pass', CFG_TTL = 5 * 60 * 1000, REFRESH_AHEAD = 7 * 86400;
  var state = { config: null, configAt: 0, token: null, payload: null, verified: null, status: 'preview' };
  var listeners = [];
  var W = typeof window !== 'undefined' ? window : null;

  /* ------------------------------------------------------------ utils --- */
  function unb64url(s) {
    s = String(s || '').replace(/-/g, '+').replace(/_/g, '/'); while (s.length % 4) s += '=';
    if (typeof atob === 'function') { try { return decodeURIComponent(escape(atob(s))); } catch (e) { return null; } }
    return Buffer.from(s, 'base64').toString('utf8');
  }
  function nowSec() { return Math.floor(Date.now() / 1000); }
  function decode(token) {
    var parts = String(token || '').split('.');
    if (parts.length !== 3 || parts[0] !== 'v1') return null;
    try { var p = JSON.parse(unb64url(parts[1])); return (p && typeof p.exp === 'number') ? p : null; } catch (e) { return null; }
  }
  function esc(s) { return String(s === null || s === undefined ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  function emit() { for (var i = 0; i < listeners.length; i++) { try { listeners[i](state.status, state); } catch (e) {} } }
  function locker() { return W && W.GolfrawLocker ? W.GolfrawLocker : null; }
  function fetchJSON(url, opts) {
    if (!W || !W.fetch) return Promise.reject(new Error('no fetch'));
    return W.fetch(url, opts).then(function (r) { return r.json(); });
  }

  /* ---------------------------------------------------------- storage --- */
  function loadToken() {
    var L = locker();
    if (L && L.getMeta) return L.getMeta(META_KEY)['catch'](function () { return null; }).then(function (t) {
      if (t) return t;
      try { return W.localStorage.getItem(LS_KEY); } catch (e) { return null; }
    });
    try { return Promise.resolve(W && W.localStorage.getItem(LS_KEY)); } catch (e) { return Promise.resolve(null); }
  }
  function storeToken(token) {
    try { if (W) W.localStorage.setItem(LS_KEY, token); } catch (e) {}
    var L = locker();
    return L && L.setMeta ? L.setMeta(META_KEY, token)['catch'](function () {}) : Promise.resolve();
  }
  function clearToken() {
    try { if (W) W.localStorage.removeItem(LS_KEY); } catch (e) {}
    var L = locker();
    return L && L.deleteMeta ? L.deleteMeta(META_KEY)['catch'](function () {}) : Promise.resolve();
  }

  /* ----------------------------------------------------------- config --- */
  function config(force) {
    if (!force && state.config && Date.now() - state.configAt < CFG_TTL) return Promise.resolve(state.config);
    return fetchJSON('/api/pro-config', { cache: 'no-store' }).then(function (c) {
      state.config = c && typeof c.enabled === 'boolean' ? c : { enabled: false, plans: [], unreachable: true };
      state.configAt = Date.now(); return state.config;
    })['catch'](function () {
      state.config = { enabled: false, plans: [], unreachable: true }; state.configAt = Date.now(); return state.config;
    });
  }

  /* ------------------------------------------------------------ resolve -- */
  function resolveStatus() {
    var c = state.config, p = state.payload;
    if (p && p.exp > nowSec() && state.verified !== false) return 'pro';
    if (!c || !c.enabled) return 'preview';
    return 'gated';
  }

  /* Loads the pass, checks the config, verifies/refreshes best-effort.
     Resolves with the status. Safe to call many times. */
  var readyP = null;
  function ready() {
    if (readyP) return readyP;
    readyP = Promise.all([config(), loadToken()]).then(function (r) {
      var token = r[1];
      state.token = token || null; state.payload = token ? decode(token) : null;
      if (state.token && !state.payload) { state.token = null; return clearToken(); }
    }).then(function () {
      if (!state.payload || !state.config || !state.config.enabled) return;
      var p = state.payload, soon = p.exp - nowSec() < REFRESH_AHEAD;
      /* near expiry (or just past it, inside the grace window) → refresh; else verify */
      var call = soon && p.cid ? fetchJSON('/api/pro-refresh', post({ token: state.token })) : fetchJSON('/api/pro-verify', post({ token: state.token }));
      return call.then(function (res) {
        if (!res) return;
        if (res.ok && res.token) { state.token = res.token; state.payload = decode(res.token); state.verified = true; return storeToken(res.token); }
        if (res.ok) { state.verified = true; return; }
        if (res.reason === 'unconfigured' || res.reason === 'unavailable') return;     /* server can't say: trust the token */
        if (res.reason === 'lapsed' || res.reason === 'bad-signature' || res.reason === 'malformed' || (res.reason === 'expired' && !soon)) { state.verified = false; state.token = null; state.payload = null; return clearToken(); }
      })['catch'](function () { /* offline: trust the token until its expiry */ });
    }).then(function () { state.status = resolveStatus(); emit(); return state.status; });
    return readyP;
  }
  function post(body) { return { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }; }

  /* ---------------------------------------------------------- actions --- */
  function claim(sessionId) {
    return fetchJSON('/api/pro-claim?session_id=' + encodeURIComponent(sessionId)).then(accept);
  }
  function restore(restoreToken) {
    return fetchJSON('/api/pro-claim?restore=' + encodeURIComponent(restoreToken)).then(accept);
  }
  function accept(res) {
    if (!res || !res.ok || !res.token) return { ok: false, error: (res && res.error) || 'Could not confirm the pass.' };
    state.token = res.token; state.payload = decode(res.token); state.verified = true;
    return storeToken(res.token).then(function () { state.status = resolveStatus(); emit(); return { ok: true, plan: res.plan, exp: res.exp, email: res.email }; });
  }
  function checkout(priceId, email) {
    return fetchJSON('/api/create-checkout-session', post({ priceId: priceId, email: email || undefined })).then(function (r) {
      if (r && r.ok && r.url) { navigate(r.url); return { ok: true }; }
      return { ok: false, error: (r && r.error) || 'Could not start checkout.' };
    })['catch'](function () { return { ok: false, error: 'Could not reach the checkout. Check your connection and try again.' }; });
  }
  /* Indirection so tests can observe the redirect without leaving the page;
     production always goes to Stripe's hosted Checkout. */
  var navigate = function (url) { W.location.assign(url); };
  function requestRestore(email) {
    return fetchJSON('/api/pro-restore', post({ email: email })).then(function (r) { return r || { ok: false }; })['catch'](function () { return { ok: false, error: 'Could not reach the server.' }; });
  }
  function signOut() { state.token = null; state.payload = null; state.verified = null; return clearToken().then(function () { state.status = resolveStatus(); emit(); }); }

  /* --------------------------------------------------------------- UI ---- */
  var CSS = '.gr-pro-badge{display:inline-block;vertical-align:middle;margin-left:10px;padding:4px 9px;border-radius:999px;font:800 10px/1.2 Inter,Archivo,system-ui,sans-serif;letter-spacing:.12em;text-transform:uppercase;background:#0A4D2E;color:#fff}' +
    '.gr-pro-badge.is-preview{background:#EAF4EE;color:#0A4D2E;border:1px solid #CBD5CF}.gr-pro-badge.is-pro{background:#1B7A43}' +
    '.gr-pro-gate{position:relative}.gr-pro-gate>.gr-pro-inner{filter:blur(2px) saturate(.7);pointer-events:none;user-select:none;opacity:.55}' +
    '.gr-pro-cover{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;text-align:center;padding:24px;background:linear-gradient(180deg,rgba(247,250,247,.55),rgba(247,250,247,.92));border:2px dashed #0A4D2E;border-radius:12px}' +
    '.gr-pro-cover h3{margin:0;font:800 20px/1.15 "Plus Jakarta Sans",Inter,system-ui,sans-serif;color:#0A4D2E;letter-spacing:-.02em}.gr-pro-cover p{margin:0;max-width:44ch;font:500 14px/1.5 Inter,system-ui,sans-serif;color:#0B1F15}' +
    '.gr-pro-btn{min-height:48px;padding:0 22px;border-radius:10px;border:2px solid #1B7A43;background:#1B7A43;color:#fff;font:800 13px/1 Inter,system-ui,sans-serif;letter-spacing:.06em;text-transform:uppercase;cursor:pointer;display:inline-flex;align-items:center;gap:8px;transition:transform .2s,box-shadow .25s,background .2s}' +
    '.gr-pro-btn:hover{transform:translateY(-2px);box-shadow:0 10px 22px rgba(6,51,30,.18);background:#0A4D2E;border-color:#0A4D2E}.gr-pro-btn.alt{background:#fff;color:#0A4D2E;border-color:#CBD5CF}.gr-pro-btn.alt:hover{background:#EAF4EE;color:#0A4D2E;border-color:#1B7A43}' +
    '.gr-pro-link{background:none;border:0;padding:8px 2px;min-height:40px;color:#1B7A43;font:700 13px/1 Inter,system-ui,sans-serif;text-decoration:underline;text-underline-offset:3px;cursor:pointer}' +
    '.gr-pro-scrim{position:fixed;inset:0;z-index:9200;background:rgba(6,51,30,.55);-webkit-backdrop-filter:blur(3px);backdrop-filter:blur(3px)}' +
    '.gr-pro-modal{position:fixed;z-index:9201;left:50%;top:50%;transform:translate(-50%,-50%);width:min(520px,calc(100% - 28px));max-height:90vh;overflow-y:auto;background:#fff;border:1px solid #CBD5CF;border-radius:16px;box-shadow:0 30px 60px rgba(6,51,30,.25);font-family:Inter,system-ui,sans-serif;color:#0B1F15}' +
    '.gr-pro-mh{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:18px 20px;border-bottom:1px solid #E5E7EB}.gr-pro-mh b{font:800 20px/1.1 "Plus Jakarta Sans",Inter,system-ui,sans-serif;color:#0A4D2E;letter-spacing:-.02em}' +
    '.gr-pro-x{width:44px;height:44px;border:0;background:none;font-size:26px;line-height:1;cursor:pointer;color:#0B1F15;border-radius:8px}.gr-pro-x:hover{background:#EAF4EE}' +
    '.gr-pro-mb{padding:18px 20px}.gr-pro-mb p{margin:0 0 12px;font-size:14.5px;line-height:1.55}.gr-pro-mb ul{margin:0 0 16px;padding-left:18px;font-size:14px;line-height:1.6}' +
    '.gr-pro-plans{display:grid;gap:10px;margin:6px 0 14px}.gr-pro-plan{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 16px;border:2px solid #CBD5CF;border-radius:12px;background:#fff;cursor:pointer;text-align:left;font:inherit;color:inherit;min-height:56px;transition:border-color .2s,transform .2s}.gr-pro-plan:hover{border-color:#1B7A43;transform:translateY(-1px)}' +
    '.gr-pro-plan b{display:block;font-weight:800;font-size:15px}.gr-pro-plan small{display:block;color:#55655B;font-size:12.5px;margin-top:2px}.gr-pro-plan .amt{font:700 18px/1 "IBM Plex Mono",monospace;color:#0A4D2E;white-space:nowrap}' +
    '.gr-pro-sep{margin:14px 0;border:0;border-top:1px solid #E5E7EB}.gr-pro-mb label{display:block;font:800 10.5px/1 Inter,system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:#55655B;margin:0 0 6px}' +
    '.gr-pro-mb input[type=email]{width:100%;min-height:46px;padding:10px 12px;border:2px solid #CBD5CF;border-radius:10px;font:600 15px/1.2 Inter,system-ui,sans-serif}.gr-pro-mb input:focus{outline:3px solid #2FB35C;outline-offset:1px}' +
    '.gr-pro-row{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}.gr-pro-msg{margin-top:10px;padding:10px 12px;border-radius:8px;font-size:13px;font-weight:600;line-height:1.45;display:none}.gr-pro-msg.on{display:block}.gr-pro-msg.bad{background:#FFF4DD;color:#8A5E00}.gr-pro-msg.good{background:#EAF4EE;color:#0A4D2E}' +
    '.gr-pro-fine{font-size:12px;color:#55655B;line-height:1.5;margin-top:12px}@media(prefers-reduced-motion:reduce){.gr-pro-btn,.gr-pro-plan{transition:none}}';
  var cssDone = false;
  function injectCSS() { if (cssDone || !W) return; cssDone = true; var s = W.document.createElement('style'); s.textContent = CSS; W.document.head.appendChild(s); }

  var FEATURES = {
    'lm-import': { title: 'Import your launch-monitor sessions', line: 'Drop a TrackMan, Foresight, Garmin, FlightScope, Rapsodo or SkyTrak export straight into the Standing Order and get medians, 80% bands and gap verdicts per club.' },
    'coach-report': { title: 'The one-page coach & fitter report', line: 'Your carry dispersion, the gaps and passengers in the bag, and the tendencies your rounds support — printed to PDF or shared by link.' }
  };

  /* Sets a badge element's text and class for the current status. */
  function badge(el) {
    if (!el) return;
    var s = state.status;
    el.className = 'gr-pro-badge' + (s === 'pro' ? ' is-pro' : (s === 'preview' ? ' is-preview' : ''));
    el.textContent = s === 'pro' ? 'Golf Raw Pro · active' : (s === 'preview' ? 'Golf Raw Pro · free in preview' : 'Golf Raw Pro');
  }

  /* Wraps a feature container. When gated, its content is dimmed and inert
     under a cover that explains the feature and opens the paywall. */
  function gate(container, featureKey, badgeEl) {
    if (!container) return Promise.resolve(state.status);
    injectCSS();
    return ready().then(function (status) {
      badge(badgeEl);
      var existing = container.querySelector(':scope > .gr-pro-cover');
      if (status !== 'gated') {
        container.classList.remove('gr-pro-gate');
        var inner = container.querySelector(':scope > .gr-pro-inner');
        if (inner) { while (inner.firstChild) container.insertBefore(inner.firstChild, inner); inner.remove(); }
        if (existing) existing.remove();
        return status;
      }
      if (!container.querySelector(':scope > .gr-pro-inner')) {
        var wrap = W.document.createElement('div'); wrap.className = 'gr-pro-inner';
        while (container.firstChild) wrap.appendChild(container.firstChild);
        container.appendChild(wrap);
      }
      container.classList.add('gr-pro-gate');
      if (!existing) {
        var f = FEATURES[featureKey] || { title: 'A Golf Raw Pro feature', line: '' };
        var cover = W.document.createElement('div'); cover.className = 'gr-pro-cover';
        cover.innerHTML = '<span class="gr-pro-badge">Golf Raw Pro</span><h3>' + esc(f.title) + '</h3><p>' + esc(f.line) + '</p>' +
          '<div class="gr-pro-row"><button type="button" class="gr-pro-btn" data-pro-open>Upgrade to Pro</button><button type="button" class="gr-pro-link" data-pro-restore>I already have Pro</button></div>';
        container.appendChild(cover);
        cover.querySelector('[data-pro-open]').addEventListener('click', function () { openModal(featureKey, 'plans'); });
        cover.querySelector('[data-pro-restore]').addEventListener('click', function () { openModal(featureKey, 'restore'); });
      }
      return status;
    });
  }

  var modal = null, lastFocus = null;
  function closeModal() { if (!modal) return; modal.scrim.remove(); modal.box.remove(); modal = null; W.document.body.style.overflow = ''; if (lastFocus && lastFocus.focus) { try { lastFocus.focus(); } catch (e) {} } }
  function openModal(featureKey, view) {
    injectCSS(); closeModal();
    var f = FEATURES[featureKey] || {}, c = state.config || { plans: [] };
    lastFocus = W.document.activeElement;
    var scrim = W.document.createElement('div'); scrim.className = 'gr-pro-scrim';
    var box = W.document.createElement('div'); box.className = 'gr-pro-modal'; box.setAttribute('role', 'dialog'); box.setAttribute('aria-modal', 'true'); box.setAttribute('aria-labelledby', 'gr-pro-title');
    var plansHtml = (c.plans || []).map(function (p) {
      var per = p.mode === 'subscription' ? ' / ' + (p.intervalCount > 1 ? p.intervalCount + ' ' + p.interval + 's' : p.interval) : ' once';
      return '<button type="button" class="gr-pro-plan" data-price="' + esc(p.id) + '"><span><b>' + esc(p.label) + '</b><small>' + esc(p.description || (p.mode === 'subscription' ? 'Cancel any time' : 'One payment, ' + 'a year of Pro')) + '</small></span><span class="amt">' + esc(p.display) + esc(per) + '</span></button>';
    }).join('');
    box.innerHTML = '<div class="gr-pro-mh"><b id="gr-pro-title">Golf Raw Pro</b><button type="button" class="gr-pro-x" aria-label="Close">&times;</button></div>' +
      '<div class="gr-pro-mb">' +
      (view === 'restore' ? '' :
        '<p><b>' + esc(f.title || 'Pro tools for serious players and coaches') + '.</b> ' + esc(f.line || '') + '</p>' +
        '<ul><li>Import launch-monitor CSV exports into the Standing Order</li><li>One-page coach &amp; fitter report: PDF and share link</li><li>Every free tool stays free. Pro is the outputs, not the arithmetic.</li></ul>' +
        (plansHtml ? '<div class="gr-pro-plans">' + plansHtml + '</div>' : '<p class="gr-pro-msg on bad">Plans are not available right now. Try again in a moment.</p>') +
        '<p class="gr-pro-fine">Payment is handled by Stripe on Stripe&rsquo;s page; GolfRaw never sees your card. Your pass is stored in this browser and never uploaded &mdash; restore it on another device with your email.</p><hr class="gr-pro-sep">') +
      '<label for="gr-pro-email">Already Pro? Restore with the email you paid with</label><input type="email" id="gr-pro-email" autocomplete="email" placeholder="you@email.com">' +
      '<div class="gr-pro-row"><button type="button" class="gr-pro-btn alt" data-pro-send>Email me a restore link</button></div>' +
      '<div class="gr-pro-msg" role="status"></div>' +
      '<p class="gr-pro-fine">Or open the receipt page from your purchase &mdash; its link restores Pro on any device.' + (c.restoreByEmail === false && c.enabled ? ' Email restore is not switched on yet.' : '') + '</p>' +
      '</div>';
    W.document.body.appendChild(scrim); W.document.body.appendChild(box); W.document.body.style.overflow = 'hidden';
    modal = { scrim: scrim, box: box };
    var msgEl = box.querySelector('.gr-pro-msg');
    function say(t, k) { msgEl.className = 'gr-pro-msg on ' + (k || ''); msgEl.textContent = t; }
    box.querySelector('.gr-pro-x').addEventListener('click', closeModal);
    scrim.addEventListener('click', closeModal);
    box.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeModal(); });
    box.querySelectorAll('[data-price]').forEach(function (b) {
      b.addEventListener('click', function () {
        b.disabled = true; say('Taking you to Stripe…', 'good');
        checkout(b.getAttribute('data-price'), box.querySelector('#gr-pro-email').value).then(function (r) { if (!r.ok) { b.disabled = false; say(r.error, 'bad'); } });
      });
    });
    box.querySelector('[data-pro-send]').addEventListener('click', function () {
      var email = box.querySelector('#gr-pro-email').value.trim();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) { say('That does not look like an email address.', 'bad'); box.querySelector('#gr-pro-email').focus(); return; }
      say('Sending…', 'good');
      requestRestore(email).then(function (r) {
        if (r.ok) say(r.message || 'If that address has a Pro pass, a restore link is on its way.', 'good');
        else if (r.reason === 'restore-unavailable') say('Email restore is not switched on yet. Open the receipt page from your purchase instead — its link restores Pro on any device.', 'bad');
        else say(r.error || 'Could not send the link.', 'bad');
      });
    });
    var first = box.querySelector('[data-price]') || box.querySelector('#gr-pro-email'); if (first) first.focus();
  }

  /* `?pro=cancelled` after a Stripe cancel: say so, once, quietly. */
  function noteCancelled() {
    if (!W || !/[?&]pro=cancelled/.test(W.location.search)) return false;
    try { W.history.replaceState(null, '', W.location.pathname + W.location.hash); } catch (e) {}
    return true;
  }
  function subscribe(fn) { listeners.push(fn); return function () { var i = listeners.indexOf(fn); if (i >= 0) listeners.splice(i, 1); }; }

  return { ready: ready, status: function () { return state.status; }, payload: function () { return state.payload; }, config: config,
    gate: gate, badge: badge, openModal: openModal, closeModal: closeModal,
    claim: claim, restore: restore, checkout: checkout, requestRestore: requestRestore, signOut: signOut, noteCancelled: noteCancelled,
    subscribe: subscribe, decode: decode, _state: state, _setNavigate: function (fn) { navigate = fn; }, _reset: function () { readyP = null; state.config = null; state.configAt = 0; state.token = null; state.payload = null; state.verified = null; state.status = 'preview'; } };
}));
