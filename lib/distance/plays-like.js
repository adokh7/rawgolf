/* GolfRaw Plays Like: how far a shot plays once the conditions are counted.
 *
 * Works in yards, °F, feet and mph; the page does the talking. Each effect is
 * worked out on its own against the flat, still-air yardage and the effects
 * are added, so the breakdown on the page always sums to the total.
 *
 * Sources
 *   ALT   Titleist Learning Lab, "Altitude and ball flight": about 6% more
 *         distance at a mile high (250 -> 265 yds in Denver); shorter, slower
 *         shots are affected less and greenside shots need no adjustment.
 *         Titleist's S. Aoyama gave the rate as elevation (ft) x 0.00116
 *         (PGA TOUR, "Elevated expectations", 28 Feb 2017), where TrackMan's
 *         J. Padjen adds that mid and short irons gain the most. So the full
 *         rate runs down to 100 yards and fades to nothing at 50.
 *   TEMP  Titleist Learning Lab, "Temperature and golf balls": from air
 *         temperature alone, about 1.5% per 20°F, for balls kept at room
 *         temperature (a cold ball loses more).
 *   WIND  A. Rice with C. Broadie (PING), "A better way to play in the wind",
 *         13 Mar 2023: into the wind add 1 yd per mph, downwind take off half
 *         that, for everyday golfers' club selection. GolfRaw applies it at 150
 *         yards and scales it with shot length; TrackMan notes the effect grows
 *         faster than linear in strong wind, so the page flags it.
 *   SLOPE TrackMan University: for a mid-trajectory shot, a yard of rise or
 *         drop is worth about a yard of distance.
 *   HUMID TrackMan University: dry to humid air moves a 6-iron under 1 yd, and
 *         humid air is less dense, so it helps slightly. Counted as zero.
 *
 * Where the model goes beyond the sources it says so: the altitude fade below
 * 100 yards and the wind scaling are GolfRaw simplifications.
 */
(function (root) {
  'use strict';

  var TEMP_BASE_F = 70;
  var TEMP_PCT_PER_10F = 0.0075;     // Titleist: 1.5% per 20°F
  var ALT_PCT_PER_FT = 0.0000116;    // Titleist: 1.16% per 1,000 ft
  var ALT_FULL_FROM = 100;           // full altitude effect at or beyond this
  var ALT_NONE_BELOW = 50;           // greenside: no adjustment
  var WIND_REF_YARDS = 150;          // Rice/Broadie rule is for an approach
  var WIND_HEAD_YD_PER_MPH = 1.0;
  var WIND_TAIL_YD_PER_MPH = 0.5;
  var FT_PER_YD = 3;
  var DEFAULT_GAP = 11;              // yards between clubs, editable on the page

  var LIMITS = {
    yards: [20, 400], temp: [-20, 130], alt: [0, 12000],
    wind: [0, 60], slope: [-200, 200], gap: [5, 25]
  };

  function clamp(x, lo, hi) { return Math.max(lo, Math.min(hi, x)); }
  function num(v) { return typeof v === 'number' ? v : parseFloat(v); }

  // Share of the full altitude effect a shot of this length gets.
  function altitudeFade(yards) {
    return clamp((yards - ALT_NONE_BELOW) / (ALT_FULL_FROM - ALT_NONE_BELOW), 0, 1);
  }

  // Returns null when the input can be used, else the name of the first bad field.
  function validate(o) {
    var y = num(o.yards);
    if (!isFinite(y)) return 'yards_missing';
    var keys = ['yards', 'temp', 'alt', 'wind', 'slope'];
    for (var i = 0; i < keys.length; i++) {
      var v = num(o[keys[i]]), l = LIMITS[keys[i]];
      if (!isFinite(v) || v < l[0] || v > l[1]) return keys[i];
    }
    if (o.windDir !== 'head' && o.windDir !== 'tail') return 'windDir';
    // Past half the shot, "a yard for a yard" stops meaning anything.
    if (Math.abs(num(o.slope)) / FT_PER_YD > y / 2) return 'slope_ratio';
    return null;
  }

  // Round each part so the parts still add up to the rounded total.
  function roundParts(parts, total) {
    var target = Math.round(total);
    var floors = parts.map(Math.floor);
    var left = target - floors.reduce(function (a, b) { return a + b; }, 0);
    var order = parts.map(function (p, i) { return { i: i, r: p - Math.floor(p) }; })
      .sort(function (a, b) { return b.r - a.r; });
    var out = floors.slice();
    for (var k = 0; k < order.length && left > 0; k++, left--) out[order[k].i] += 1;
    for (var j = order.length - 1; j >= 0 && left < 0; j--, left++) out[order[j].i] -= 1;
    return out;
  }

  function compute(o) {
    var bad = validate(o);
    if (bad) return { ok: false, code: bad };
    var yards = num(o.yards), temp = num(o.temp), alt = num(o.alt);
    var wind = num(o.wind), slope = num(o.slope);
    var gap = num(o.gap);
    if (!isFinite(gap) || gap < LIMITS.gap[0] || gap > LIMITS.gap[1]) gap = DEFAULT_GAP;

    // Air that makes the ball fly further makes the shot play shorter.
    var tempGain = TEMP_PCT_PER_10F * (temp - TEMP_BASE_F) / 10;
    var altGain = ALT_PCT_PER_FT * alt * altitudeFade(yards);
    var parts = {
      temp: yards / (1 + tempGain) - yards,
      alt: yards / (1 + altGain) - yards,
      wind: (o.windDir === 'head' ? WIND_HEAD_YD_PER_MPH : -WIND_TAIL_YD_PER_MPH) * wind * yards / WIND_REF_YARDS,
      slope: slope / FT_PER_YD,
      humid: 0
    };
    var keys = ['temp', 'alt', 'wind', 'slope', 'humid'];
    var total = keys.reduce(function (a, k) { return a + parts[k]; }, 0);
    var rounded = roundParts(keys.map(function (k) { return parts[k]; }), total);
    var shown = {};
    keys.forEach(function (k, i) { shown[k] = rounded[i]; });

    var flags = [];
    if (wind >= 20) flags.push('strong_wind');
    if (temp < 40) flags.push('cold_ball');
    if (alt > 0 && yards < ALT_FULL_FROM) flags.push('short_altitude');
    if (Math.abs(slope / FT_PER_YD) > yards * 0.2) flags.push('steep');

    return {
      ok: true,
      input: { yards: yards, temp: temp, alt: alt, wind: wind, windDir: o.windDir, slope: slope, gap: gap },
      parts: parts,
      shown: shown,
      total: total,
      playsLike: yards + total,
      clubs: total / gap,
      gap: gap,
      flags: flags
    };
  }

  var api = {
    version: 1,
    LIMITS: LIMITS,
    DEFAULT_GAP: DEFAULT_GAP,
    TEMP_BASE_F: TEMP_BASE_F,
    RATES: {
      tempPctPer10F: TEMP_PCT_PER_10F, altPctPer1000Ft: ALT_PCT_PER_FT * 1000,
      altFullFrom: ALT_FULL_FROM, altNoneBelow: ALT_NONE_BELOW, windRefYards: WIND_REF_YARDS,
      windHeadYdPerMph: WIND_HEAD_YD_PER_MPH, windTailYdPerMph: WIND_TAIL_YD_PER_MPH
    },
    altitudeFade: altitudeFade,
    validate: validate,
    compute: compute
  };
  root.GolfrawPlaysLike = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : this);
