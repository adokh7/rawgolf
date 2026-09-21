'use strict';

// Contract for lib/distance/club-distance.js (The Distance Check model).
// Sweeps every accepted input, then pins the published anchors it is built on.

const D = require('../lib/distance/club-distance.js');
const failures = [];
let checks = 0;

function check(condition, message) {
  checks++;
  if (!condition) failures.push(message);
}
function near(a, b, tol) { return Math.abs(a - b) <= tol; }
function centre(res, id) { return res.clubs.find((c) => c.id === id).centre; }

// ---- INPUT -------------------------------------------------------------------
check(D.estimate({ anchor: 'iron_carry', value: '' }).code === 'empty' ||
  D.estimate({ anchor: 'iron_carry', value: '' }).ok === false, 'empty input is refused');
check(D.estimate({ anchor: 'iron_carry', value: NaN }).code === 'empty', 'NaN is refused as empty');
check(D.estimate({ anchor: 'iron_carry', value: 'abc' }).ok === false, 'text is refused');
check(D.estimate({ anchor: 'iron_carry', value: 59 }).code === 'low', '7-iron below range is refused');
check(D.estimate({ anchor: 'iron_carry', value: 216 }).code === 'high', '7-iron above range is refused');
check(D.estimate({ anchor: 'driver_carry', value: 99 }).code === 'low', 'driver below range is refused');
check(D.estimate({ anchor: 'driver_carry', value: 331 }).code === 'high', 'driver above range is refused');
check(D.estimate({ anchor: 'swing_speed', value: 49 }).code === 'low', 'speed below range is refused');
check(D.estimate({ anchor: 'swing_speed', value: 131 }).code === 'high', 'speed above range is refused');
check(D.estimate({ anchor: 'swing_speed', value: -90 }).ok === false, 'negative speed is refused');
check(D.estimate({ anchor: 'handicap_band', band: 'nope', group: 'men' }).code === 'band', 'unknown band is refused');
check(D.estimate({ anchor: 'carrier_pigeon', value: 150 }).code === 'anchor', 'unknown anchor is refused');
check(D.estimate({}).ok === false, 'no input is refused');

// ---- RESULTS: sweep every accepted input --------------------------------------
const inputs = [];
for (let v = D.LIMITS.driver_carry[0]; v <= D.LIMITS.driver_carry[1]; v += 5) inputs.push({ anchor: 'driver_carry', value: v });
for (let v = D.LIMITS.iron_carry[0]; v <= D.LIMITS.iron_carry[1]; v += 2.5) inputs.push({ anchor: 'iron_carry', value: v });
for (let v = D.LIMITS.swing_speed[0]; v <= D.LIMITS.swing_speed[1]; v += 2.5) inputs.push({ anchor: 'swing_speed', value: v });
for (const b of D.BANDS) for (const group of ['men', 'women']) inputs.push({ anchor: 'handicap_band', band: b.id, group });

const ids = D.CLUBS.map((c) => c.id);
for (const input of inputs) {
  const tag = JSON.stringify(input);
  const res = D.estimate(input);
  check(res.ok, 'accepted input works: ' + tag);
  if (!res.ok) continue;
  check(res.clubs.length === D.CLUBS.length, 'every club is returned: ' + tag);
  for (let i = 1; i < res.clubs.length; i++) {
    check(res.clubs[i].centre < res.clubs[i - 1].centre,
      `${res.clubs[i].id} is shorter than ${res.clubs[i - 1].id}: ${tag}`);
  }
  const driver = centre(res, 'driver');
  for (const id of ['4i', '5i', '6i', '7i', '8i', '9i', 'pw', 'gw', 'sw']) {
    check(driver > centre(res, id), `driver beats ${id}: ${tag}`);
  }
  for (const c of res.clubs) {
    check(c.centre > 0 && c.typical[0] > 0 && c.best[0] > 0, `no negative or zero carry (${c.id}): ${tag}`);
    check(c.typical[0] < c.centre && c.centre < c.typical[1], `typical range brackets the centre (${c.id}): ${tag}`);
    check(c.best[0] > c.typical[0] && c.best[1] > c.typical[1] && c.best[0] < c.best[1],
      `best range sits above the typical range and is ordered (${c.id}): ${tag}`);
    check(['anchor', 'firm', 'fair', 'rough'].includes(c.confidence), `known confidence label (${c.id}): ${tag}`);
  }
  // Confidence follows the quality of the anchor.
  const anchors = res.clubs.filter((c) => c.anchor);
  if (input.anchor === 'iron_carry') {
    check(anchors.length === 1 && anchors[0].id === '7i' && near(anchors[0].centre, input.value, 1e-9), 'the 7-iron row is the entered number: ' + tag);
  } else if (input.anchor === 'driver_carry') {
    check(anchors.length === 1 && anchors[0].id === 'driver' && near(anchors[0].centre, input.value, 1e-9), 'the driver row is the entered number: ' + tag);
  } else {
    check(anchors.length === 0, 'no row claims to be the golfer\'s number: ' + tag);
  }
  if (input.anchor === 'handicap_band') check(res.clubs.every((c) => c.confidence === 'rough'), 'handicap results are all rough: ' + tag);
  if (input.anchor === 'swing_speed') check(!res.clubs.some((c) => c.confidence === 'firm'), 'swing-speed results are never firm: ' + tag);
  check(['gw', 'sw'].every((id) => res.clubs.find((c) => c.id === id).confidence === 'rough'), 'extrapolated wedges are rough: ' + tag);
  // Tee check.
  const tee = res.tee;
  check(tee && tee.course[0] <= tee.course[1], 'course range is ordered: ' + tag);
  check(tee.course[0] % 50 === 0 && tee.course[1] % 50 === 0, 'course lengths are rounded to 50 yards: ' + tag);
  check(tee.course[0] >= 2100 && tee.course[1] <= 6900, 'course range stays inside the Tee It Forward chart: ' + tag);
  const dRow = res.clubs[0];
  check(tee.total[0] > dRow.typical[0] && tee.total[1] > dRow.typical[1], 'total drive adds roll to both ends of the carry range: ' + tag);
}

// More input never means less distance.
for (const anchor of ['driver_carry', 'iron_carry', 'swing_speed']) {
  const lim = D.LIMITS[anchor];
  let prev = null;
  for (let v = lim[0]; v <= lim[1]; v += 1) {
    const res = D.estimate({ anchor, value: v });
    if (prev) {
      for (const id of ids) check(centre(res, id) >= centre(prev, id) - 1e-9, `${id} never shrinks as ${anchor} rises (${v})`);
      check(res.tee.course[1] >= prev.tee.course[1], `course length never shrinks as ${anchor} rises (${v})`);
    }
    prev = res;
  }
}
const hcpMen = D.BANDS.map((b) => centre(D.estimate({ anchor: 'handicap_band', band: b.id, group: 'men' }), 'driver'));
for (let i = 1; i < hcpMen.length; i++) check(hcpMen[i] < hcpMen[i - 1], 'higher handicap bands carry less');

// ---- PUBLISHED ANCHORS ---------------------------------------------------------
// USGA 2023 men's averages (totals 226 driver, 149 7-iron, 117 PW -> carry 198.4, 134.2, 108.1).
const usgaMen = D.estimate({ anchor: 'driver_carry', value: 198.4 });
check(near(centre(usgaMen, '7i'), 134.2, 1.5), 'USGA men: 7-iron from driver matches the study average');
check(near(centre(usgaMen, 'pw'), 108.1, 3), 'USGA men: PW from driver is close to the study average');
// TrackMan 2023 PGA Tour carry: a 176 7-iron reproduces the tour bag.
const pga = D.estimate({ anchor: 'iron_carry', value: 176 });
const tour = { driver: 282, '4i': 209, '5i': 199, '6i': 188, '8i': 164, '9i': 152, pw: 142, hy: 231, '5w': 236, '3w': 249 };
for (const id of Object.keys(tour)) check(near(centre(pga, id), tour[id], 1.5), `PGA Tour ${id} is reproduced (${centre(pga, id).toFixed(1)} vs ${tour[id]})`);
// USGA club-speed regression: total = -45.89 + 2.84 x mph; carry = -34.38 + 1.03 x total.
check(near(centre(D.estimate({ anchor: 'swing_speed', value: 100 }), 'driver'), -34.38 + 1.03 * (-45.89 + 284), 0.01), 'swing speed follows the USGA regression');
// USGA handicap trend at HI 16.5 (men) and the women's own driver-to-7-iron ratio.
check(near(centre(D.estimate({ anchor: 'handicap_band', band: 'hi_13_20', group: 'men' }), 'driver'), -34.38 + 1.03 * (265.32 - 3.02 * 16.5), 0.01), 'men\'s handicap trend matches the USGA fit');
const women = D.estimate({ anchor: 'handicap_band', band: 'hi_13_20', group: 'women' });
check(near(centre(women, '7i') / centre(women, 'driver'), 77.04 / 113.94, 0.001), 'women\'s benchmark uses the women\'s average ratio');
// Tee It Forward: a 250-yard total drive reads 6,200-6,400.
const teeAt250 = D.estimate({ anchor: 'driver_carry', value: -34.38 + 1.03 * 250 });
check(teeAt250.tee.course[0] <= 6250 && teeAt250.tee.course[1] >= 6350, 'Tee It Forward row for 250 yards is honoured');

// ---- UNITS ---------------------------------------------------------------------
// The page converts at the edges; the model is unit-free, so the same carry in
// metres (converted exactly) must give the same bag.
const M = 0.9144;
const fromMetres = D.estimate({ anchor: 'iron_carry', value: 137.16 / M });
const fromYards = D.estimate({ anchor: 'iron_carry', value: 150 });
check(ids.every((id) => near(centre(fromMetres, id), centre(fromYards, id), 1e-6)), '137.16 m and 150 yds give the same bag');
check(near(150 * M, 137.16, 1e-9) && near(137.16 / M, 150, 1e-9), 'yards <-> metres round-trips exactly');

if (failures.length) {
  console.error('Club distance model failed ' + failures.length + ' of ' + checks + ' checks:\n- ' + failures.slice(0, 25).join('\n- '));
  process.exit(1);
}
console.log('Club distance model passed ' + checks + ' checks.');
