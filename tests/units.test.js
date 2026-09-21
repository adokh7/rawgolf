'use strict';

// Contract for lib/distance/units.js and for the four distance tools running
// on one canonical model: the same physical input in yards or metres, °F or
// °C, feet or metres, mph or km/h must give the same physical answer.
//
// Rounding rules (screen only; the models never see rounded numbers):
//   club and target distances   whole yards / whole metres
//   course lengths              nearest 50 in the unit shown
//   gaps over the chart range   nearest 10 in the unit shown (Tee Box)
//   temperature                 whole degrees
//   wind                        whole mph / km/h
//   altitude and elevation      whole feet / metres
//   Bag Audit thresholds        one decimal in metres (18.3 m, 7.3 m)

const U = require('../lib/distance/units.js');
const D = require('../lib/distance/club-distance.js');
const P = require('../lib/distance/plays-like.js');
const T = require('../lib/distance/tee-box.js');
const B = require('../lib/distance/bag-audit.js');

const failures = [];
let checks = 0;
function check(condition, message) { checks++; if (!condition) failures.push(message); }
function near(a, b, tol) { return Math.abs(a - b) <= tol; }
let seed = 20260921;
function rand() { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; }
function between(lo, hi) { return lo + (hi - lo) * rand(); }

// ---- CONVERSIONS ----------------------------------------------------------------
check(U.M_PER_YD === 0.9144 && U.M_PER_FT === 0.3048 && U.KMH_PER_MPH === 1.609344, 'exact international constants');
for (const [yd, m] of [[0, 0], [100, 91.44], [200, 182.88], [300, 274.32]]) {
  check(near(U.ydToM(yd), m, 1e-9), `${yd} yd = ${m} m`);
  check(near(U.mToYd(m), yd, 1e-9), `${m} m = ${yd} yd`);
}
for (const [f, c] of [[32, 0], [68, 20], [86, 30], [-40, -40], [212, 100]]) {
  check(near(U.fToC(f), c, 1e-9), `${f} F = ${c} C`);
  check(near(U.cToF(c), f, 1e-9), `${c} C = ${f} F`);
}
check(near(U.ftToM(1000), 304.8, 1e-9) && near(U.mToFt(304.8), 1000, 1e-9), '1,000 ft = 304.8 m');
check(near(U.ftToM(5280), 1609.344, 1e-9) && Math.round(U.ftToM(5280)) === 1609, '5,280 ft = 1,609.34 m');
check(near(U.mphToKmh(10), 16.09344, 1e-9) && near(U.mphToKmh(20), 32.18688, 1e-9), '10 mph = 16.09 km/h, 20 mph = 32.19 km/h');
check(near(U.kmhToMph(16.09344), 10, 1e-9), '16.09 km/h = 10 mph');
for (let i = 0; i < 2000; i++) {
  const v = between(-100, 10000);
  for (const k of ['distance', 'height', 'temp', 'speed']) {
    const other = U.KINDS[k].other;
    check(near(U.toCanon(k, U.fromCanon(k, v, other), other), v, 1e-7), `${k} round trip is exact: ${v}`);
    check(U.toCanon(k, v, U.KINDS[k].canon) === v, `${k} canonical unit is untouched`);
  }
}

// ---- LIMITS AND ROUNDING ------------------------------------------------------------
check(JSON.stringify(U.limits('distance', [20, 400], 'm')) === '[19,365]', 'target limits in metres round inward: 19-365');
check(JSON.stringify(U.limits('distance', [60, 215], 'm')) === '[55,196]', '7-iron limits in metres: 55-196');
check(JSON.stringify(U.limits('temp', [-20, 130], 'C')) === '[-28,54]', 'temperature limits in C: -28 to 54');
check(JSON.stringify(U.limits('speed', [0, 60], 'kmh')) === '[0,96]', 'wind limits in km/h: 0-96');
check(JSON.stringify(U.limits('height', [0, 12000], 'm')) === '[0,3657]', 'altitude limits in metres: 0-3,657');
check(JSON.stringify(U.limits('distance', [20, 400], 'yd')) === '[20,400]', 'limits in the canonical unit are unchanged');
check(U.show('distance', 6152, 'm', 50) === '5,650' && U.show('distance', 6152, 'yd', 50) === '6,150', 'course lengths round to 50 in the unit shown (6,152 yd = 5,625.4 m)');
check(U.show('distance', U.mToYd(5624), 'm', 50) === '5,600', 'and round once: a 5,624 m course shows 5,600, never re-rounded from yards');
check(U.show('distance', 150, 'm') === '137', '150 yards shows as 137 metres');
check(U.show('temp', 31.9, 'C') === '0', 'no minus zero');

// ---- FIELDS: switching never drifts ----------------------------------------------------
function fakeInput() {
  const on = {};
  return {
    value: '',
    addEventListener(t, f) { (on[t] = on[t] || []).push(f); },
    type(text) { this.value = text; (on.input || []).forEach((f) => f()); }
  };
}
for (const [kind, a, b, typed] of [['distance', 'yd', 'm', '200'], ['temp', 'F', 'C', '68'], ['height', 'ft', 'm', '5280'], ['speed', 'mph', 'kmh', '10']]) {
  let unit = a;
  const input = fakeInput();
  const f = U.field(input, kind, () => unit);
  input.type(typed);
  const canon = f.canon();
  U.switchFields([f], () => { unit = b; });
  const shown = input.value;
  check(String(Math.round(U.fromCanon(kind, canon, b))) === shown, `${kind}: ${typed} ${a} shows as ${shown} ${b}`);
  for (let i = 0; i < 25; i++) {
    U.switchFields([f], () => { unit = unit === a ? b : a; });
    check(near(f.canon(), canon, 1e-12), `${kind}: the exact value survives switch ${i + 1}`);
  }
  U.switchFields([f], () => { unit = a; });
  check(input.value === typed, `${kind}: back in ${a} the field shows exactly what was typed (${input.value})`);
}
{
  let unit = 'yd';
  const input = fakeInput();
  const f = U.field(input, 'distance', () => unit);
  U.switchFields([f], () => { unit = 'm'; });
  input.type('183');
  U.switchFields([f], () => { unit = 'yd'; });
  check(input.value === '200' && near(f.canon(), 183 / 0.9144, 1e-9), '183 m typed shows 200 yd and keeps 183 m exactly');
  U.switchFields([f], () => { unit = 'm'; });
  check(input.value === '183', 'and returns to the 183 that was typed');
  f.set(245);
  U.switchFields([f], () => { unit = 'yd'; });
  check(input.value === '245' && f.canon() === 245, 'a value set by the page (a sample, a restore) behaves the same way');
  input.type('');
  check(f.canon() === null, 'an empty field is null, not zero');
  input.type('abc');
  check(Number.isNaN(f.canon()), 'text is NaN, never a silent zero');
}
for (let i = 0; i < 500; i++) {
  let unit = 'yd';
  const input = fakeInput();
  const f = U.field(input, 'distance', () => unit);
  const typed = String(Math.round(between(20, 400)));
  input.type(typed);
  for (let k = 0; k < 7; k++) U.switchFields([f], () => { unit = unit === 'yd' ? 'm' : 'yd'; });
  U.switchFields([f], () => { unit = 'yd'; });
  check(input.value === typed, 'random yardage survives repeated switching: ' + typed);
}

// ---- FIRST-VISIT WEATHER UNITS (language only, never location) -------------------------
const wd = (tag) => { const d = U.weatherDefaults(tag); return d.temp + '/' + d.speed; };
for (const [tag, want] of [['en-US', 'F/mph'], ['en-GB', 'C/mph'], ['en-AU', 'C/kmh'], ['en-CA', 'C/kmh'], ['en-IE', 'C/kmh'],
  ['fr-FR', 'C/kmh'], ['de', 'C/kmh'], ['en', 'F/mph'], ['', 'F/mph'], ['es-US', 'F/mph'], ['zh-Hant-TW', 'C/kmh']]) {
  check(wd(tag) === want, `weather defaults for "${tag}" are ${want}: got ${wd(tag)}`);
}

// ---- MODEL EQUIVALENCE: imperial input vs its exact metric equivalent -----------------------
// The metric route is what a page does: the golfer's metres become yards at
// full precision before the model runs.
const viaMetric = (k, v) => U.toCanon(k, U.fromCanon(k, v, U.KINDS[k].other), U.KINDS[k].other);

// Distance Check
for (let i = 0; i < 1500; i++) {
  const anchor = ['driver_carry', 'iron_carry', 'swing_speed'][i % 3];
  const kind = anchor === 'swing_speed' ? 'speed' : 'distance';
  const lim = D.LIMITS[anchor];
  const v = between(lim[0] + 1e-6, lim[1] - 1e-6);
  const a = D.estimate({ anchor, value: v }), b = D.estimate({ anchor, value: viaMetric(kind, v) });
  const tag = `${anchor} ${v.toFixed(3)}`;
  check(a.ok && b.ok, 'both routes run: ' + tag);
  check(a.clubs.every((c, j) => near(c.centre, b.clubs[j].centre, 1e-9) && near(c.typical[1], b.clubs[j].typical[1], 1e-9)), 'same bag either way: ' + tag);
  check(a.clubs.every((c, j) => U.show('distance', c.typical[0], 'm') === U.show('distance', b.clubs[j].typical[0], 'm')), 'same metres on screen: ' + tag);
  check(U.show('distance', a.tee.courseRaw[0], 'm', 50) === U.show('distance', b.tee.courseRaw[0], 'm', 50), 'same course length on screen: ' + tag);
}
// Plays Like: altitude, temperature, wind, slope, gap all through the metric route.
for (let i = 0; i < 3000; i++) {
  const o = {
    yards: between(40, 400), temp: between(-20, 130), alt: between(0, 12000), wind: between(0, 60),
    windDir: rand() < 0.5 ? 'head' : 'tail', slope: between(-60, 60), gap: between(6, 24)
  };
  const m = {
    yards: viaMetric('distance', o.yards), temp: viaMetric('temp', o.temp), alt: viaMetric('height', o.alt),
    wind: viaMetric('speed', o.wind), windDir: o.windDir, slope: viaMetric('height', o.slope), gap: viaMetric('distance', o.gap)
  };
  const a = P.compute(o), b = P.compute(m);
  const tag = JSON.stringify(o);
  if (!a.ok) { check(!b.ok && a.code === b.code, 'both routes refuse the same input: ' + tag); continue; }
  check(b.ok && near(a.playsLike, b.playsLike, 1e-9) && near(a.clubs, b.clubs, 1e-9), 'same plays-like either way: ' + tag);
  check(JSON.stringify(a.flags) === JSON.stringify(b.flags), 'same cautions either way: ' + tag);
  const inM = (r) => P.roundParts(['temp', 'alt', 'wind', 'slope', 'humid'].map((k) => U.ydToM(r.parts[k])), U.ydToM(r.total));
  check(JSON.stringify(inM(a)) === JSON.stringify(inM(b)), 'same metric breakdown on screen: ' + tag);
  const shown = inM(a).reduce((s, x) => s + x, 0);
  check(shown === Math.round(U.ydToM(a.total)), 'the metric breakdown adds up to the metric total: ' + tag);
}
// Same physical altitude, either unit: 5,280 ft and 1,609.344 m.
check(near(P.compute({ yards: 150, temp: 70, alt: 5280, wind: 0, windDir: 'head', slope: 0 }).playsLike,
  P.compute({ yards: 150, temp: 70, alt: U.mToFt(1609.344), wind: 0, windDir: 'head', slope: 0 }).playsLike, 1e-9), '5,280 ft and 1,609.344 m play the same');
// Tee Box
for (let i = 0; i < 2000; i++) {
  const o = { carry: between(50, 400), score: Math.round(between(55, 200)), yards: between(3000, 8500) };
  const a = T.analyse(o), b = T.analyse({ carry: viaMetric('distance', o.carry), score: o.score, yards: viaMetric('distance', o.yards) });
  const tag = JSON.stringify(o);
  check(a.ok && b.ok && a.status === b.status && near(a.strokes, b.strokes, 1e-9) && a.clubNow === b.clubNow, 'same tee verdict either way: ' + tag);
  for (const u of ['yd', 'm']) {
    check(U.show('distance', a.rangeRaw[0], u, 50) === U.show('distance', b.rangeRaw[0], u, 50) &&
      U.show('distance', a.rangeRaw[1], u, 50) === U.show('distance', b.rangeRaw[1], u, 50), `same range on screen in ${u}: ` + tag);
  }
}
// Bag Audit: thresholds stay 20 and 8 yards, whatever the golfer typed in.
const NAMES = ['Driver', '3-Wood', '5-Wood', '4-Hybrid', '5-iron', '6-iron', '7-iron', '8-iron', '9-iron', 'PW', 'GW', 'SW', 'LW'];
for (let i = 0; i < 3000; i++) {
  const rows = NAMES.map((name) => ({ name, carry: between(40, 300), usage: rand() < 0.2 ? null : Math.floor(rand() * 10), conf: 1 + Math.floor(rand() * 5) }));
  const metricRows = rows.map((r) => Object.assign({}, r, { carry: viaMetric('distance', r.carry) }));
  const a = B.analyse(rows), b = B.analyse(metricRows);
  const kinds = (x) => x.gaps.map((g) => g.hi.name + '>' + g.lo.name + ':' + g.kind).join(',');
  check(kinds(a) === kinds(b), 'same ladder, gaps and overlaps either way');
  check(a.gaps.every((g, j) => near(g.yards, b.gaps[j].yards, 1e-9)), 'same gap sizes either way');
}
check(B.GAP_BIG === 20 && B.GAP_TIGHT === 8, 'Bag Audit thresholds are 20 and 8 yards');
{
  const bag = (gap) => [{ name: 'A', carry: 150, usage: 5, conf: 5 }, { name: 'B', carry: 150 - gap, usage: 5, conf: 5 }, { name: 'C', carry: 100 - gap, usage: 5, conf: 5 }];
  check(B.analyse(bag(U.mToYd(18.3))).gaps[0].kind === 'hole', '18.3 m (20.01 yd) is a hole');
  check(B.analyse(bag(U.mToYd(18.2))).gaps[0].kind === 'ok', '18.2 m (19.9 yd) is not: 20 yards never becomes 20 metres');
  check(B.analyse(bag(U.mToYd(7.3))).gaps[0].kind === 'overlap', '7.3 m (7.98 yd) is an overlap');
}

// ---- DISTANCE CHECK AND TEE BOX NEVER DISAGREE -------------------------------------------
for (let carry = 100; carry <= 330; carry += 0.5) {
  const total = D.totalFromCarry(carry);
  const tb = T.courseRange(total).raw, raw = D.teeRange(total, total).course;
  check(tb[0] === raw[0] && tb[1] === raw[1], 'Tee Box reads the same chart function: ' + carry);
  const dc = D.estimate({ anchor: 'driver_carry', value: carry }).tee.courseRaw;
  for (const u of ['yd', 'm']) {
    const s = (v) => parseInt(U.show('distance', v, u, 50).replace(/,/g, ''), 10);
    check(s(dc[0]) <= s(tb[0]) && s(dc[1]) >= s(tb[1]), `the Distance Check range contains the Tee Box range in ${u}: ${carry}`);
  }
}

if (failures.length) {
  console.error('Units contract failed ' + failures.length + ' of ' + checks + ' checks:\n- ' + failures.slice(0, 25).join('\n- '));
  process.exit(1);
}
console.log('Units contract passed ' + checks + ' checks.');
