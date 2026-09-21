/* GolfRaw Tee Box: a starting course length from driving distance, and what
 * playing longer than that tends to cost.
 *
 * Needs /lib/distance/club-distance.js loaded first (window.GolfrawDistance):
 * the Tee It Forward chart, the carry-to-total fit and the club estimates live
 * there, so this tool and The Distance Check always give the same answer.
 *
 * Sources
 *   TIF   PGA of America / USGA, "Tee It Forward" guidelines (2011): average
 *         driving distance -> recommended 18-hole length, eight rows from 100
 *         to 275 yards. Driving distance there is total (carry plus roll), as
 *         the R&A/USGA Distance Insights playing-lengths study (2019) reads it.
 *         Between rows the chart is read in a straight line.
 *   USGA  D. Pierce, USGA, 1 Dec 2023: driver carry = -34.38 + 1.03 x total,
 *         used to turn the carry a golfer enters into a total drive.
 *   CR    USGA Course Rating length formulas (D. Knuth, USGA): men's scratch
 *         rating rises 1 stroke per 220 yards, bogey rating 1 per 160 yards.
 *         The golfer's typical score places them between the two; the
 *         formulas stop at bogey, so higher scores use the bogey rate.
 *
 * GolfRaw simplifications, said as such on the page: an average par 4 is
 * taken as about 6% of the course, and a scratch round as 72, bogey as 92.
 */
(function (root) {
  'use strict';

  var D = root.GolfrawDistance || (typeof require === 'function' ? require('./club-distance.js') : null);

  var LIMITS = { carry: [50, 400], score: [55, 200], yards: [3000, 8500] };
  var PAR4_SHARE = 0.0594;
  var SCRATCH = { score: 72, perYard: 1 / 220 };
  var BOGEY = { score: 92, perYard: 1 / 160 };
  var FAR_BACK = 800, OFF = 300;   // yards past the range edge

  var ARTICLE = {
    driver: 'a driver', '3w': 'a 3-wood', '5w': 'a 5-wood', hy: 'a hybrid', '4i': 'a 4-iron',
    '5i': 'a 5-iron', '6i': 'a 6-iron', '7i': 'a 7-iron', '8i': 'an 8-iron', '9i': 'a 9-iron',
    pw: 'a pitching wedge', gw: 'a gap wedge', sw: 'a sand wedge'
  };

  function clamp(x, lo, hi) { return Math.max(lo, Math.min(hi, x)); }
  function lerp(a, b, t) { return a + (b - a) * t; }
  function r50(x) { return Math.round(x / 50) * 50; }

  function totalFromCarry(carry) { return D.totalFromCarry(carry); }

  // The Tee It Forward range for a total drive, straight from The Distance
  // Check's model: `raw` is unrounded, `range` is rounded to 50 yards.
  function courseRange(total) {
    var t = D.teeRange(total, total);
    var rows = D.TEE_IT_FORWARD;
    return {
      raw: t.course,
      range: [r50(t.course[0]), r50(t.course[1])],
      beyond: total < rows[0][0] ? 'short' : total > rows[rows.length - 1][0] ? 'long' : null
    };
  }

  // Course Rating strokes per yard for a golfer with this typical score.
  function strokesPerYard(score) {
    var t = clamp((score - SCRATCH.score) / (BOGEY.score - SCRATCH.score), 0, 1);
    return lerp(SCRATCH.perYard, BOGEY.perYard, t);
  }

  // The club the golfer would hit to a green this far away, from their driver.
  function clubFor(carry, yards) {
    if (yards <= 30) return 'a short chip';
    var bag = D.estimate({ anchor: 'driver_carry', value: clamp(carry, D.LIMITS.driver_carry[0], D.LIMITS.driver_carry[1]) });
    var pick = null;
    for (var i = bag.clubs.length - 1; i >= 0; i--) {
      if (bag.clubs[i].id !== 'driver' && bag.clubs[i].centre >= yards) { pick = bag.clubs[i].id; break; }
    }
    return pick ? ARTICLE[pick] : 'a fairway wood or more';
  }

  function validate(o) {
    var keys = ['carry', 'score', 'yards'];
    for (var i = 0; i < keys.length; i++) {
      var v = typeof o[keys[i]] === 'number' ? o[keys[i]] : parseFloat(o[keys[i]]);
      if (!isFinite(v)) return 'missing';
    }
    for (var j = 0; j < keys.length; j++) {
      var n = parseFloat(o[keys[j]]), l = LIMITS[keys[j]];
      if (n < l[0] || n > l[1]) return keys[j];
    }
    return null;
  }

  function analyse(o) {
    var bad = validate(o);
    if (bad) return { ok: false, code: bad };
    var carry = parseFloat(o.carry), score = parseFloat(o.score), yards = parseFloat(o.yards);
    var total = totalFromCarry(carry);
    var c = courseRange(total);
    // Everything is measured against the unrounded chart; only the screen rounds.
    var lo = c.raw[0], hi = c.raw[1], mid = (lo + hi) / 2;
    var over = Math.max(0, yards - hi), under = Math.max(0, lo - yards);
    var status = over > FAR_BACK ? 'far_back' : over >= OFF ? 'back' : under >= OFF ? 'forward' : 'fits';
    var perYard = strokesPerYard(score);
    var strokes = over * perYard;
    var approachNow = Math.max(0, yards * PAR4_SHARE - total);
    var approachIdeal = Math.max(0, mid * PAR4_SHARE - total);
    return {
      ok: true,
      carry: carry, score: score, yards: yards, total: total,
      range: c.range, rangeRaw: c.raw, mid: mid, beyond: c.beyond,
      over: over, under: under, status: status,
      strokesPer200: perYard * 200, strokes: strokes,
      projectedScore: Math.max(18, score - strokes),
      approachNow: approachNow, approachIdeal: approachIdeal,
      clubNow: clubFor(carry, approachNow), clubIdeal: clubFor(carry, approachIdeal)
    };
  }

  var api = {
    version: 2,
    LIMITS: LIMITS,
    PAR4_SHARE: PAR4_SHARE,
    SCRATCH: SCRATCH,
    BOGEY: BOGEY,
    totalFromCarry: totalFromCarry,
    courseRange: courseRange,
    strokesPerYard: strokesPerYard,
    validate: validate,
    analyse: analyse
  };
  root.GolfrawTeeBox = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : this);
