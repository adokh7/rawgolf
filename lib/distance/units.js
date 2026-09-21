/* GolfRaw units: one set of conversions and one distance preference for the
 * distance tools (Distance Check, Plays Like, Tee Box, Bag Audit).
 *
 * The models all work in one canonical unit per quantity and never see
 * anything else:
 *   distance  yards   (the USGA and Tee It Forward data are in yards)
 *   height    feet    (altitude and elevation change; Titleist's rate is per foot)
 *   temp      °F      (Titleist's rate is per °F)
 *   speed     mph     (the Rice/Broadie wind rule and the USGA speed fit)
 * Pages convert at the edge: what the golfer types becomes canonical at full
 * precision, the model runs once, and only the final numbers are rounded for
 * the screen. A field remembers its canonical value, so switching units back
 * and forth never drifts.
 *
 * The distance preference is the Locker profile's `units` field
 * ('yards' | 'meters'), the same one the Locker drawer, The Standing Order and
 * the Coach Report read. Changing it goes through GolfrawLocker.setUnits,
 * which converts stored bag and range distances rather than relabelling them.
 * Temperature and wind units are not part of the profile; the one tool that
 * uses them keeps them in its own saved state.
 */
(function (root) {
  'use strict';

  var M_PER_YD = 0.9144;       // exact, by the 1959 international yard
  var M_PER_FT = 0.3048;       // exact
  var KMH_PER_MPH = 1.609344;  // exact

  function ydToM(v) { return v * M_PER_YD; }
  function mToYd(v) { return v / M_PER_YD; }
  function ftToM(v) { return v * M_PER_FT; }
  function mToFt(v) { return v / M_PER_FT; }
  function fToC(v) { return (v - 32) * 5 / 9; }
  function cToF(v) { return v * 9 / 5 + 32; }
  function mphToKmh(v) { return v * KMH_PER_MPH; }
  function kmhToMph(v) { return v / KMH_PER_MPH; }

  // Each kind: its canonical unit and how to reach it from the other unit.
  var KINDS = {
    distance: { canon: 'yd', other: 'm', to: mToYd, from: ydToM },
    height: { canon: 'ft', other: 'm', to: mToFt, from: ftToM },
    temp: { canon: 'F', other: 'C', to: cToF, from: fToC },
    speed: { canon: 'mph', other: 'kmh', to: kmhToMph, from: mphToKmh }
  };

  var LABELS = {
    yd: { short: 'yds', long: 'yards', one: 'yard' },
    m: { short: 'm', long: 'metres', one: 'metre' },
    ft: { short: 'ft', long: 'feet', one: 'foot' },
    F: { short: '°F', long: '°F', one: '°F' },
    C: { short: '°C', long: '°C', one: '°C' },
    mph: { short: 'mph', long: 'mph', one: 'mph' },
    kmh: { short: 'km/h', long: 'km/h', one: 'km/h' }
  };

  function kind(k) {
    if (!KINDS[k]) throw new Error('Unknown unit kind: ' + k);
    return KINDS[k];
  }
  function toCanon(k, v, unit) { var d = kind(k); return unit === d.canon ? v : d.to(v); }
  function fromCanon(k, v, unit) { var d = kind(k); return unit === d.canon ? v : d.from(v); }
  function label(unit, form) { return (LABELS[unit] || {})[form || 'short'] || unit; }

  // The distance preference maps onto units for distance and height.
  function distUnit(pref) { return pref === 'meters' ? 'm' : 'yd'; }
  function heightUnit(pref) { return pref === 'meters' ? 'm' : 'ft'; }

  // Canonical limits shown in another unit, rounded inward so any number the
  // message allows is also accepted.
  function limits(k, canonRange, unit) {
    var a = fromCanon(k, canonRange[0], unit), b = fromCanon(k, canonRange[1], unit);
    var lo = Math.min(a, b), hi = Math.max(a, b);
    return [Math.ceil(lo - 1e-9), Math.floor(hi + 1e-9)];
  }

  function roundTo(v, step) { return Math.round(v / (step || 1)) * (step || 1); }
  function thousands(n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
  // A display number: rounded to `step` in the display unit, never "-0".
  function show(k, canonValue, unit, step) {
    var v = roundTo(fromCanon(k, canonValue, unit), step || 1);
    return thousands(v === 0 ? 0 : v);
  }

  /* ------------------------------------------------------------------ fields
     Keeps the exact canonical value behind a number input. Typing sets it (in
     the unit shown at that moment); a unit switch re-renders from it. Going
     back to the unit the golfer typed in shows exactly what they typed. */
  function parse(text) {
    var s = String(text == null ? '' : text).replace(/^\s+|\s+$/g, '').replace(',', '.');
    if (s === '') return null;
    var v = parseFloat(s);
    return isFinite(v) ? v : NaN;
  }

  function field(input, k, getUnit, step) {
    var st = { canon: null, shown: null, typed: null };
    function capture() {
      if (input.value === st.shown && st.canon !== null) return st.canon;
      var v = parse(input.value);
      if (v === null || isNaN(v)) { st.canon = v; st.shown = input.value; st.typed = null; return v; }
      var u = getUnit();
      st.typed = { unit: u, text: input.value };
      st.canon = toCanon(k, v, u);
      st.shown = input.value;
      return st.canon;
    }
    function render() {
      var c = capture();
      if (c === null || isNaN(c)) return;
      var u = getUnit();
      var text = st.typed && st.typed.unit === u ? st.typed.text : String(roundTo(fromCanon(k, c, u), step || 1) || 0);
      input.value = text;
      st.shown = text;
      st.canon = c;
    }
    function set(canonValue) {
      st.typed = null;
      if (canonValue === null || canonValue === undefined || !isFinite(canonValue)) {
        input.value = ''; st.canon = null; st.shown = ''; return;
      }
      st.canon = canonValue;
      st.shown = null;
      var u = getUnit();
      input.value = String(roundTo(fromCanon(k, canonValue, u), step || 1) || 0);
      st.shown = input.value;
    }
    input.addEventListener('input', function () { capture(); });
    return { input: input, kind: k, canon: capture, render: render, set: set };
  }

  // Switch units without losing anything: capture every field in the old
  // unit, apply the switch, then redraw every field in the new unit.
  function switchFields(fields, apply) {
    for (var i = 0; i < fields.length; i++) fields[i].canon();
    apply();
    for (var j = 0; j < fields.length; j++) fields[j].render();
  }

  /* -------------------------------------------------------------- preference */
  var state = { distance: 'yards', pending: null };
  var subs = [];
  var resolveReady;
  var readyPromise = typeof Promise === 'function' ? new Promise(function (r) { resolveReady = r; }) : null;

  function locker() { return root.GolfrawLocker || null; }
  function notify(reason) {
    for (var i = 0; i < subs.length; i++) {
      try { subs[i](state.distance, reason); } catch (e) { /* one tool must not break another */ }
    }
  }
  function readProfile(reason) {
    var L = locker();
    if (!L || !L.getProfile) return Promise.resolve();
    return L.getProfile().then(function (p) {
      if (state.pending) return;          // a switch the golfer just made is still being saved
      var u = p && p.units === 'meters' ? 'meters' : 'yards';
      if (u !== state.distance) { state.distance = u; notify(reason); }
    })['catch'](function () { });
  }
  function init() {
    var L = locker();
    if (!L || !L.ready) { if (resolveReady) resolveReady(); return; }
    L.ready().then(function () { return readProfile('load'); }).then(resolveReady, resolveReady);
    if (L.subscribe) {
      L.subscribe(function (what) {
        if (what === 'profile' || what === 'import' || what === 'clear') readProfile('external');
      });
    }
  }
  function setDistance(u) {
    u = u === 'meters' ? 'meters' : 'yards';
    if (u === state.distance) return Promise.resolve();
    state.distance = u;
    state.pending = u;
    notify('user');
    var L = locker();
    var done = function () { if (state.pending === u) state.pending = null; };
    if (!L || !L.setUnits) { done(); return Promise.resolve(); }
    return L.setUnits(u).then(done, done);
  }

  // First-visit weather units from the browser language, never location.
  // Only the US (and territories using its conventions) reads °F; mph wind is
  // the US and the UK.
  var F_REGIONS = ['US', 'PR', 'GU', 'VI', 'AS', 'MP', 'UM', 'LR', 'BS', 'BZ', 'KY', 'PW', 'FM', 'MH'];
  var MPH_REGIONS = F_REGIONS.concat(['GB', 'IM', 'JE', 'GG']);
  function weatherDefaults(tag) {
    if (tag === undefined) {
      var nav = root.navigator || {};
      tag = (nav.languages && nav.languages[0]) || nav.language || '';
    }
    var parts = String(tag).split(/[-_]/);
    var lang = (parts[0] || '').toLowerCase();
    var region = '';
    for (var i = 1; i < parts.length; i++) if (/^[A-Za-z]{2}$/.test(parts[i])) { region = parts[i].toUpperCase(); break; }
    var usLike = region ? F_REGIONS.indexOf(region) !== -1 : (lang === 'en' || lang === '');
    var mph = region ? MPH_REGIONS.indexOf(region) !== -1 : (lang === 'en' || lang === '');
    return { temp: usLike ? 'F' : 'C', speed: mph ? 'mph' : 'kmh' };
  }

  if (root.document && root.addEventListener) {
    if (root.document.readyState === 'loading') root.document.addEventListener('DOMContentLoaded', init);
    else root.setTimeout(init, 0);
  }

  var api = {
    version: 1,
    M_PER_YD: M_PER_YD, M_PER_FT: M_PER_FT, KMH_PER_MPH: KMH_PER_MPH,
    ydToM: ydToM, mToYd: mToYd, ftToM: ftToM, mToFt: mToFt,
    fToC: fToC, cToF: cToF, mphToKmh: mphToKmh, kmhToMph: kmhToMph,
    KINDS: KINDS,
    toCanon: toCanon, fromCanon: fromCanon, label: label,
    distUnit: distUnit, heightUnit: heightUnit,
    limits: limits, roundTo: roundTo, thousands: thousands, show: show,
    parse: parse, field: field, switchFields: switchFields,
    distance: function () { return state.distance; },
    setDistance: setDistance,
    onChange: function (fn) { subs.push(fn); },
    ready: function () { return readyPromise || { then: function (f) { f(); } }; },
    weatherDefaults: weatherDefaults
  };
  root.GolfrawUnits = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : this);
