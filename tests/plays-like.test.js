'use strict';

// Contract for lib/distance/plays-like.js (The Plays Like Calculator model).
// Pins the published rates it is built on, then sweeps every accepted input.

const P = require('../lib/distance/plays-like.js');
const failures = [];
let checks = 0;

function check(condition, message) {
  checks++;
  if (!condition) failures.push(message);
}
function near(a, b, tol) { return Math.abs(a - b) <= tol; }
const BASE = { yards: 150, temp: 70, alt: 0, wind: 0, windDir: 'head', slope: 0, gap: 11 };
function run(o) { return P.compute(Object.assign({}, BASE, o)); }

// ---- INPUT -------------------------------------------------------------------
check(run({ yards: '' }).code === 'yards_missing', 'empty yardage is refused');
check(run({ yards: 'abc' }).code === 'yards_missing', 'text yardage is refused');
check(run({ yards: 19 }).code === 'yards' && run({ yards: 401 }).code === 'yards', 'yardage outside 20-400 is refused');
check(run({ temp: -21 }).code === 'temp' && run({ temp: 131 }).code === 'temp', 'temperature outside -20 to 130 F is refused');
check(run({ alt: -1 }).code === 'alt' && run({ alt: 12001 }).code === 'alt', 'altitude outside 0-12,000 ft is refused');
check(run({ wind: -1 }).code === 'wind' && run({ wind: 61 }).code === 'wind', 'wind outside 0-60 mph is refused');
check(run({ slope: 201 }).code === 'slope' && run({ slope: -201 }).code === 'slope', 'elevation outside +-200 ft is refused');
check(run({ temp: NaN }).code === 'temp', 'NaN temperature is refused');
check(run({ windDir: 'cross' }).code === 'windDir', 'unknown wind direction is refused');
check(run({ yards: 20, slope: -200 }).code === 'slope_ratio', 'a drop bigger than half the shot is refused');
check(run({ yards: 60, slope: 90 }).ok && run({ yards: 60, slope: 91 }).code === 'slope_ratio', 'the slope limit is half the shot');
check(run({ gap: 99 }).gap === P.DEFAULT_GAP && run({ gap: '' }).gap === P.DEFAULT_GAP, 'a bad club gap falls back to 11');
for (const edge of [{ yards: 20 }, { yards: 400 }, { temp: -20 }, { temp: 130 }, { alt: 12000 }, { wind: 60 }, { yards: 400, slope: 200 }, { yards: 400, slope: -200 }]) {
  check(run(edge).ok, 'boundary values are accepted: ' + JSON.stringify(edge));
}

// ---- PUBLISHED RATES -----------------------------------------------------------
check(run({}).total === 0 && run({}).playsLike === 150, 'sea level, 70 F, still and flat plays its number');
// Titleist: 250 yds at sea level goes about 265 in Denver (5,280 ft), ~6%.
const denver = run({ yards: 250, alt: 5280 });
check(near(250 / denver.playsLike, 265 / 250, 0.005), 'Denver matches Titleist (250 -> 265): ' + denver.playsLike.toFixed(1));
check(near(P.RATES.altPctPer1000Ft, 0.0116, 1e-9), 'altitude rate is 1.16% per 1,000 ft');
check(near(run({ alt: 1000 }).parts.alt, 150 / 1.0116 - 150, 1e-9), '1,000 ft on a full shot uses the full rate');
check(near(run({ alt: 5000 }).parts.alt, 150 / 1.058 - 150, 1e-9), '5,000 ft on a full shot uses the full rate');
// Titleist: 1.5% per 20 F; a 200-yard shot at 50 F loses about 3 yards.
check(near(run({ yards: 200, temp: 50 }).parts.temp, 3, 0.1), 'Titleist 200 yds at 50 F is about 3 yds');
// Rice/Broadie: 1 yd per mph into the wind, half downwind, for a 150-yard shot.
check(near(run({ wind: 10 }).parts.wind, 10, 1e-9) && near(run({ wind: 10, windDir: 'tail' }).parts.wind, -5, 1e-9), 'wind rule at 150 yards');
check(near(run({ slope: 30 }).parts.slope, 10, 1e-9) && near(run({ slope: -30 }).parts.slope, -10, 1e-9), 'a yard of rise is a yard of distance');

// ---- SHAPE OF EACH EFFECT ----------------------------------------------------------
// Altitude fades out on short shots (Titleist: greenside shots need no adjustment).
check(P.altitudeFade(50) === 0 && P.altitudeFade(100) === 1 && near(P.altitudeFade(75), 0.5, 1e-9), 'altitude fade: 0 at 50 yds, full from 100');
check(run({ yards: 45, alt: 8000 }).parts.alt === 0, 'greenside shots get no altitude change');
check(run({ yards: 75, alt: 5000 }).parts.alt / 75 > run({ yards: 150, alt: 5000 }).parts.alt / 150, 'short shots move less at altitude');
check(near(run({ yards: 100, alt: 5000 }).parts.alt, 100 / 1.058 - 100, 1e-9), 'a 100-yard shot gets the full altitude rate (TrackMan: short irons gain)');
// Temperature and wind scale with the shot; slope does not.
check(near(run({ yards: 100, temp: 40 }).parts.temp * 2, run({ yards: 200, temp: 40 }).parts.temp, 1e-9), 'temperature scales with shot length');
check(near(run({ yards: 75, wind: 12 }).parts.wind * 2, run({ yards: 150, wind: 12 }).parts.wind, 1e-9), 'wind scales with shot length');
check(near(run({ yards: 80, slope: 30 }).parts.slope, run({ yards: 240, slope: 30 }).parts.slope, 1e-9), 'slope is yards, not a share of the shot');
check(['low', 'high'].every(() => run({}).parts.humid === 0), 'humidity is counted as zero');
for (let mph = 1; mph <= 60; mph++) {
  check(run({ wind: mph }).parts.wind > -run({ wind: mph, windDir: 'tail' }).parts.wind, 'a headwind hurts more than a tailwind helps at ' + mph + ' mph');
}

// More of a condition always moves the number the same way.
for (const yards of [20, 60, 100, 150, 220, 300, 400]) {
  let prev = null;
  for (let alt = 0; alt <= 12000; alt += 250) {
    const r = run({ yards, alt });
    if (prev) check(r.playsLike <= prev.playsLike + 1e-9, `higher never plays longer (${yards} yds, ${alt} ft)`);
    prev = r;
  }
  prev = null;
  for (let temp = -20; temp <= 130; temp += 5) {
    const r = run({ yards, temp });
    if (prev) check(r.playsLike <= prev.playsLike + 1e-9, `warmer never plays longer (${yards} yds, ${temp} F)`);
    prev = r;
  }
  for (const dir of ['head', 'tail']) {
    prev = null;
    for (let wind = 0; wind <= 60; wind += 2) {
      const r = run({ yards, wind, windDir: dir });
      if (prev) check(dir === 'head' ? r.playsLike >= prev.playsLike : r.playsLike <= prev.playsLike, `${dir}wind moves one way (${yards} yds, ${wind} mph)`);
      prev = r;
    }
  }
}

// ---- COMBINATIONS: no impossible values ----------------------------------------------
let sweeps = 0;
for (const yards of [20, 50, 90, 150, 250, 400]) {
  for (const temp of [-20, 40, 70, 100, 130]) {
    for (const alt of [0, 1000, 5000, 12000]) {
      for (const wind of [0, 15, 60]) {
        for (const windDir of ['head', 'tail']) {
          for (const slope of [-200, -30, 0, 30, 200]) {
            const r = run({ yards, temp, alt, wind, windDir, slope });
            if (!r.ok) { check(r.code === 'slope_ratio', 'only the slope ratio can refuse a full sweep input'); continue; }
            sweeps++;
            const tag = JSON.stringify({ yards, temp, alt, wind, windDir, slope });
            check(isFinite(r.playsLike) && r.playsLike > 0, 'plays-like is a positive number: ' + tag);
            const shown = Object.values(r.shown).reduce((a, b) => a + b, 0);
            check(shown === Math.round(r.total), 'rounded breakdown adds up to the rounded total: ' + tag);
            check(Object.values(r.shown).every(Number.isInteger), 'breakdown is whole yards: ' + tag);
            check(near(r.clubs, r.total / r.gap, 1e-9), 'club change is total / gap: ' + tag);
          }
        }
      }
    }
  }
}
check(sweeps > 2000, 'the combination sweep ran: ' + sweeps);

// ---- FLAGS: say when the estimate is shaky ---------------------------------------------
check(run({ wind: 20 }).flags.includes('strong_wind') && !run({ wind: 19 }).flags.includes('strong_wind'), 'strong wind is flagged from 20 mph');
check(run({ temp: 39 }).flags.includes('cold_ball') && !run({ temp: 40 }).flags.includes('cold_ball'), 'cold ball is flagged below 40 F');
check(run({ yards: 99, alt: 3000 }).flags.includes('short_altitude') && !run({ yards: 100, alt: 3000 }).flags.includes('short_altitude'), 'short shots at altitude are flagged');
check(run({ yards: 100, slope: 61 }).flags.includes('steep') && !run({ yards: 100, slope: 60 }).flags.includes('steep'), 'big elevation changes are flagged');
check(run({}).flags.length === 0, 'neutral conditions carry no flags');

if (failures.length) {
  console.error('Plays Like model failed ' + failures.length + ' of ' + checks + ' checks:\n- ' + failures.slice(0, 25).join('\n- '));
  process.exit(1);
}
console.log('Plays Like model passed ' + checks + ' checks.');
