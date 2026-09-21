/* GolfRaw Distance Check: estimate carry for every club from one number.
 *
 * Works in yards (carry) and mph only; the page converts units. Every constant
 * below is published data, cited where it is used. Where the model has to go
 * beyond the data (wedges below PW, and how wide each range is) it says so.
 *
 * Sources
 *   TOUR  TrackMan, "New PGA & LPGA Tour Averages", 2 May 2024 (2023 data):
 *         per-club carry for PGA Tour (+DP World) and LPGA (+LET) players.
 *   USGA  D. Pierce, "Quantitative Analysis of Recreational Golfer Club Hitting
 *         Distances: Measured versus Perception", USGA, 1 Dec 2023. TrackMan 4,
 *         627 recreational golfers (548 men, 79 women), average HI 13.2. Its
 *         regressions are on TOTAL distance; the carry-from-total fits (R 0.98)
 *         turn them into carry.
 *   TIF   PGA of America / USGA, "Tee It Forward" guidelines (2011): driving
 *         distance (total) to recommended 18-hole yardage.
 */
(function (root) {
  'use strict';

  var CLUBS = [
    { id: 'driver', label: 'Driver' },
    { id: '3w', label: '3-wood' },
    { id: '5w', label: '5-wood' },
    { id: 'hy', label: 'Hybrid' },
    { id: '4i', label: '4-iron' },
    { id: '5i', label: '5-iron' },
    { id: '6i', label: '6-iron' },
    { id: '7i', label: '7-iron' },
    { id: '8i', label: '8-iron' },
    { id: '9i', label: '9-iron' },
    { id: 'pw', label: 'Pitching wedge' },
    { id: 'gw', label: 'Gap wedge' },
    { id: 'sw', label: 'Sand wedge' }
  ];
  var INDEX = {};
  CLUBS.forEach(function (c, i) { INDEX[c.id] = i; });

  // TOUR carry, yards.
  var TOUR = {
    pga: { driver: 282, '3w': 249, '5w': 236, hy: 231, '4i': 209, '5i': 199, '6i': 188, '7i': 176, '8i': 164, '9i': 152, pw: 142 },
    lpga: { driver: 223, '3w': 200, '5w': 189, hy: 178, '4i': 175, '5i': 166, '6i': 155, '7i': 143, '8i': 133, '9i': 123, pw: 111 }
  };

  // USGA regressions: [intercept, slope].
  var USGA = {
    carryFromTotal: { driver: [-34.38, 1.03], '7i': [-32.72, 1.12], pw: [-20.6, 1.1] },
    sevenTotalFromDriverTotal: [22.22, 0.56],
    pwTotalFromSevenTotal: [16, 0.67],
    driverTotalFromSpeed: [-45.89, 2.84],
    driverTotalFromHandicap: { men: [265.32, -3.02], women: [200.8, -2.34] },
    // Table 5 average totals for the women in the sample (driver, 7-iron).
    womenAverage: { driver: 144, '7i': 98 }
  };

  // TIF: driving distance (total, yards) -> recommended 18-hole yardage.
  var TEE_IT_FORWARD = [
    [100, 2100, 2300], [125, 2800, 3000], [150, 3500, 3700], [175, 4400, 4600],
    [200, 5200, 5400], [225, 5800, 6000], [250, 6200, 6400], [275, 6700, 6900]
  ];

  // Accepted inputs (yards carry, mph). The swing-speed limits are the span of
  // the USGA sample; the carry limits run from beginner to tour speed.
  var LIMITS = { driver_carry: [100, 330], iron_carry: [60, 215], swing_speed: [50, 130] };

  // Handicap bands, evaluated at the Handicap Index shown.
  var BANDS = [
    { id: 'hi_0_5', label: 'Scratch to 5', hi: 2.5 },
    { id: 'hi_6_12', label: '6 to 12', hi: 9 },
    { id: 'hi_13_20', label: '13 to 20', hi: 16.5 },
    { id: 'hi_21_28', label: '21 to 28', hi: 24.5 },
    { id: 'hi_29_36', label: '29 to 36', hi: 32.5 },
    { id: 'hi_none', label: 'No handicap yet', hi: 36 }
  ];
  var DEFAULT_BAND = 'hi_13_20';

  function clamp(x, lo, hi) { return Math.max(lo, Math.min(hi, x)); }
  function lerp(a, b, t) { return a + (b - a) * t; }
  function line(fit, x) { return fit[0] + fit[1] * x; }
  function carryFromTotal(club, total) { return line(USGA.carryFromTotal[club], total); }
  function totalFromCarry(club, carry) { var f = USGA.carryFromTotal[club]; return (carry - f[0]) / f[1]; }

  // 0 at LPGA scale, 1 at PGA Tour scale, held outside that span.
  function tourMix(value, club) { return clamp((value - TOUR.lpga[club]) / (TOUR.pga[club] - TOUR.lpga[club]), 0, 1); }
  function tourRatio(club, base, mix) { return lerp(TOUR.lpga[club] / TOUR.lpga[base], TOUR.pga[club] / TOUR.pga[base], mix); }

  // Typical 7-iron carry from typical driver carry. Recreational golfers keep
  // more of their distance with irons than tour ratios imply (USGA 7-iron =
  // 22 + 0.56 x driver, totals), so that link is used through the sample's
  // range and eased onto the PGA Tour ratio between 250 and 282 yards, where
  // the recreational data runs out.
  function sevenFromDriver(d) {
    var amateur = carryFromTotal('7i', line(USGA.sevenTotalFromDriverTotal, totalFromCarry('driver', d)));
    var tour = d * TOUR.pga['7i'] / TOUR.pga.driver;
    var w = clamp((d - 250) / (TOUR.pga.driver - 250), 0, 1);
    return lerp(amateur, tour, w);
  }

  // The 7-iron link above is fitted on men and women together, and reads about
  // 7% long for the women's averages. The women's benchmark uses their own
  // ratio of average carries instead (77 / 114 = 0.68).
  function womenSevenRatio() {
    var w = USGA.womenAverage;
    return carryFromTotal('7i', w['7i']) / carryFromTotal('driver', w.driver);
  }

  function driverFromSeven(s) {
    var lo = 20, hi = 500;
    for (var i = 0; i < 60; i++) {
      var mid = (lo + hi) / 2;
      if (sevenFromDriver(mid) < s) lo = mid; else hi = mid;
    }
    return (lo + hi) / 2;
  }

  // Pitching wedge from the USGA 7-iron link (PW = 16 + 0.67 x 7-iron, totals),
  // eased onto the PGA Tour ratio between 160 and 176 yards of 7-iron carry.
  // Very slow swings compress the irons; the PW never gets closer than 0.88 of
  // the 7-iron, the ratio in the USGA women's averages.
  function pwFromSeven(s) {
    var amateur = carryFromTotal('pw', line(USGA.pwTotalFromSevenTotal, totalFromCarry('7i', s)));
    var tour = s * TOUR.pga.pw / TOUR.pga['7i'];
    var w = clamp((s - 160) / (TOUR.pga['7i'] - 160), 0, 1);
    return Math.min(lerp(amateur, tour, w), s * 0.88);
  }

  // Centre of the typical carry for every club, from driver D and 7-iron S.
  function bag(d, s) {
    var ironMix = tourMix(s, '7i');
    var woodMix = tourMix(d, 'driver');
    var c = { driver: d, '7i': s };
    c['4i'] = s * tourRatio('4i', '7i', ironMix);
    c['5i'] = s * tourRatio('5i', '7i', ironMix);
    c['6i'] = s * tourRatio('6i', '7i', ironMix);
    c.pw = pwFromSeven(s);
    // 8- and 9-iron sit between the 7-iron and PW where the tours put them.
    ['8i', '9i'].forEach(function (id) {
      var at = lerp((TOUR.lpga['7i'] - TOUR.lpga[id]) / (TOUR.lpga['7i'] - TOUR.lpga.pw),
        (TOUR.pga['7i'] - TOUR.pga[id]) / (TOUR.pga['7i'] - TOUR.pga.pw), ironMix);
      c[id] = s - at * (s - c.pw);
    });
    // Woods and hybrid sit between the driver and 4-iron where the tours put them,
    // so slower swings get the bunched-up long game they actually have.
    ['3w', '5w', 'hy'].forEach(function (id) {
      var at = lerp((TOUR.lpga.driver - TOUR.lpga[id]) / (TOUR.lpga.driver - TOUR.lpga['4i']),
        (TOUR.pga.driver - TOUR.pga[id]) / (TOUR.pga.driver - TOUR.pga['4i']), woodMix);
      c[id] = d - at * (d - c['4i']);
    });
    // No published average covers full gap and sand wedges: continue the
    // 9-iron-to-PW step twice. Flagged rough.
    var step = c.pw / c['9i'];
    c.gw = c.pw * step;
    c.sw = c.gw * step;
    return c;
  }

  // Half-width of the typical range as a share of carry. A modelling choice,
  // not a published figure: tight around a measured number, wider with each
  // club step away from it, wider still across the driver-to-iron link and for
  // swing speed or handicap. The page labels the result firm, fair or rough.
  var BASE = { measured: 0.02, speed: 0.07, benchmark: 0.13 };
  function spread(id, quality, anchorId, s) {
    var i = INDEX[id], a = INDEX[anchorId];
    var u = BASE[quality] + Math.min(0.01 * Math.abs(i - a), 0.04);
    var ironSide = i >= INDEX['4i'], anchorIronSide = a >= INDEX['4i'];
    if (id === 'hy') u += 0.02;
    else if (ironSide !== anchorIronSide) u += 0.04;
    if (id === 'pw') u += 0.01;
    if (id === 'gw') u += 0.06;
    if (id === 'sw') u += 0.08;
    if ((id === '4i' || id === '5i') && s < 120) u += 0.04;
    return Math.min(u, 0.22);
  }
  function confidence(u) { return u <= 0.05 ? 'firm' : u <= 0.10 ? 'fair' : 'rough'; }

  function teeCheck(dLo, dHi) {
    var tLo = totalFromCarry('driver', dLo), tHi = totalFromCarry('driver', dHi);
    function at(t, col) {
      var rows = TEE_IT_FORWARD;
      if (t <= rows[0][0]) return rows[0][col];
      for (var i = 1; i < rows.length; i++) {
        if (t <= rows[i][0]) return lerp(rows[i - 1][col], rows[i][col], (t - rows[i - 1][0]) / (rows[i][0] - rows[i - 1][0]));
      }
      return rows[rows.length - 1][col];
    }
    var r50 = function (x) { return Math.round(x / 50) * 50; };
    return {
      total: [tLo, tHi],
      course: [r50(at(tLo, 1)), r50(at(tHi, 2))],
      beyondChart: tHi > TEE_IT_FORWARD[TEE_IT_FORWARD.length - 1][0] || tLo < TEE_IT_FORWARD[0][0]
    };
  }

  function estimate(input) {
    input = input || {};
    var anchor = input.anchor, d, s, quality, anchorId, bandLabel = null;
    if (anchor === 'handicap_band') {
      var band = BANDS.filter(function (b) { return b.id === input.band; })[0];
      var fit = USGA.driverTotalFromHandicap[input.group === 'women' ? 'women' : 'men'];
      if (!band) return { ok: false, code: 'band' };
      d = carryFromTotal('driver', line(fit, band.hi));
      if (input.group === 'women') s = d * womenSevenRatio();
      quality = 'benchmark'; anchorId = 'driver';
      bandLabel = band.label + ' handicap, ' + (input.group === 'women' ? "women's" : "men's") + ' data';
    } else {
      var v = Number(input.value);
      var lim = LIMITS[anchor];
      if (!lim) return { ok: false, code: 'anchor' };
      if (!isFinite(v)) return { ok: false, code: 'empty' };
      if (v < lim[0] || v > lim[1]) return { ok: false, code: v < lim[0] ? 'low' : 'high' };
      if (anchor === 'driver_carry') { d = v; quality = 'measured'; anchorId = 'driver'; }
      else if (anchor === 'iron_carry') { s = v; d = driverFromSeven(v); quality = 'measured'; anchorId = '7i'; }
      else { d = carryFromTotal('driver', line(USGA.driverTotalFromSpeed, v)); quality = 'speed'; anchorId = 'driver'; }
    }
    if (s === undefined) s = sevenFromDriver(d);
    var centres = bag(d, s);
    var clubs = CLUBS.map(function (c) {
      var mid = centres[c.id];
      var isAnchor = quality === 'measured' && c.id === anchorId;
      var u = spread(c.id, quality, anchorId, s);
      var lo = mid * (1 - u), hi = mid * (1 + u);
      return {
        id: c.id, label: c.label, centre: mid, anchor: isAnchor,
        typical: [lo, hi], best: [lo * 1.03, hi * 1.04],
        confidence: isAnchor ? 'anchor' : confidence(u)
      };
    });
    var dRow = clubs[0];
    return {
      ok: true, anchor: anchor, quality: quality, bandLabel: bandLabel,
      clubs: clubs, tee: teeCheck(dRow.typical[0], dRow.typical[1])
    };
  }

  var api = {
    version: 1, CLUBS: CLUBS, BANDS: BANDS, DEFAULT_BAND: DEFAULT_BAND, LIMITS: LIMITS,
    TOUR: TOUR, USGA: USGA, TEE_IT_FORWARD: TEE_IT_FORWARD,
    estimate: estimate, sevenFromDriver: sevenFromDriver, driverFromSeven: driverFromSeven
  };
  root.GolfrawDistance = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : this);
