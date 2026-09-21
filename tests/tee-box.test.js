'use strict';

// Contract for lib/distance/tee-box.js (The Tee Box Reality Check model).
// It must read the published Tee It Forward chart, share its data with The
// Distance Check, and never produce an impossible answer.

const D = require('../lib/distance/club-distance.js');
const T = require('../lib/distance/tee-box.js');
const failures = [];
let checks = 0;

function check(condition, message) {
  checks++;
  if (!condition) failures.push(message);
}
function near(a, b, tol) { return Math.abs(a - b) <= tol; }
function carryFor(total) { return -34.38 + 1.03 * total; }

// ---- INPUT -------------------------------------------------------------------
check(T.analyse({ carry: '', score: 95, yards: 6500 }).code === 'missing', 'a missing number is refused');
check(T.analyse({ carry: 'abc', score: 95, yards: 6500 }).code === 'missing', 'text is refused');
check(T.analyse({ carry: 49, score: 95, yards: 6500 }).code === 'carry' && T.analyse({ carry: 401, score: 95, yards: 6500 }).code === 'carry', 'carry outside 50-400 is refused');
check(T.analyse({ carry: 220, score: 54, yards: 6500 }).code === 'score' && T.analyse({ carry: 220, score: 201, yards: 6500 }).code === 'score', 'score outside 55-200 is refused');
check(T.analyse({ carry: 220, score: 95, yards: 2999 }).code === 'yards' && T.analyse({ carry: 220, score: 95, yards: 8501 }).code === 'yards', 'yardage outside 3,000-8,500 is refused');
for (const [carry, score, yards] of [[50, 55, 3000], [400, 200, 8500], [50, 200, 8500], [400, 55, 3000]]) {
  check(T.analyse({ carry, score, yards }).ok, `boundary values are accepted: ${carry}/${score}/${yards}`);
}

// ---- PUBLISHED CHART -------------------------------------------------------------
check(D.TEE_IT_FORWARD.length === 8, 'the published chart has eight rows (100 to 275 yards)');
for (const [total, lo, hi] of D.TEE_IT_FORWARD) {
  const c = T.courseRange(total);
  check(c.range[0] === lo && c.range[1] === hi, `Tee It Forward row ${total} yds reads ${lo}-${hi}: got ${c.range.join('-')}`);
  check(c.beyond === null, 'chart rows are inside the chart: ' + total);
}
// Between rows the chart is read in a straight line, rounded to 50.
const between = T.courseRange(237.5);
check(between.range[0] === 6000 && between.range[1] === 6200, 'halfway between 225 and 250 reads 6,000-6,200: ' + between.range.join('-'));
check(T.courseRange(90).beyond === 'short' && T.courseRange(300).beyond === 'long', 'drives off the chart are flagged');
check(T.courseRange(90).range[0] === 2100 && T.courseRange(300).range[1] === 6900, 'off-chart drives stay at the chart edge');
// Carry becomes total through the USGA fit (carry = -34.38 + 1.03 x total).
for (const total of [100, 150, 200, 250, 275]) check(near(T.totalFromCarry(carryFor(total)), total, 1e-9), 'carry -> total inverts the USGA fit at ' + total);
const avg = T.analyse({ carry: carryFor(250), score: 90, yards: 6300 });
check(avg.range[0] === 6200 && avg.range[1] === 6400 && avg.status === 'fits', 'a 250-yard total drive on 6,300 yards fits');
check(T.analyse({ carry: 220, score: 95, yards: 6700 }).range.join('-') === '6150-6350', 'the 220-yard carry example reads 6,150-6,350');

// ---- COURSE RATING STROKES ---------------------------------------------------------------
check(near(T.strokesPerYard(72) * 200, 200 / 220, 1e-9), 'scratch: 1 stroke per 220 yards');
check(near(T.strokesPerYard(92) * 200, 200 / 160, 1e-9), 'bogey: 1 stroke per 160 yards');
check(T.strokesPerYard(60) === T.strokesPerYard(72) && T.strokesPerYard(130) === T.strokesPerYard(92), 'the rate stops at scratch and bogey');
for (let s = 55; s < 200; s++) check(T.strokesPerYard(s + 1) >= T.strokesPerYard(s), 'the rate never falls as scores rise: ' + s);
check(T.analyse({ carry: 220, score: 95, yards: 6300 }).strokes === 0, 'no strokes are charged inside the range');

// ---- SWEEP: monotonic and possible ----------------------------------------------------------
const clubs = new Set(['a driver', 'a 3-wood', 'a 5-wood', 'a hybrid', 'a 4-iron', 'a 5-iron', 'a 6-iron', 'a 7-iron',
  'an 8-iron', 'a 9-iron', 'a pitching wedge', 'a gap wedge', 'a sand wedge', 'a short chip', 'a fairway wood or more']);
let prevRange = null;
for (let carry = 50; carry <= 400; carry += 5) {
  const a = T.analyse({ carry, score: 95, yards: 6500 });
  check(a.ok, 'every carry in range works: ' + carry);
  check(a.range[0] <= a.range[1] && a.range[0] >= 2100 && a.range[1] <= 6900, 'range is ordered and inside the chart: ' + carry);
  check(a.range[0] % 50 === 0 && a.range[1] % 50 === 0, 'range is rounded to 50: ' + carry);
  check(a.total > carry, 'total drive includes roll: ' + carry);
  if (prevRange) check(a.range[0] >= prevRange[0] && a.range[1] >= prevRange[1], 'longer drives never get a shorter course: ' + carry);
  prevRange = a.range;
  for (const yards of [3000, 4500, 6000, 7200, 8500]) {
    for (const score of [55, 72, 85, 92, 110, 200]) {
      const b = T.analyse({ carry, score, yards });
      const tag = `${carry}/${score}/${yards}`;
      check(b.strokes >= 0 && isFinite(b.strokes), 'strokes are never negative: ' + tag);
      check(b.projectedScore >= 18 && b.projectedScore <= score, 'projected score is possible: ' + tag);
      check(b.approachNow >= 0 && b.approachIdeal >= 0, 'approaches are never negative: ' + tag);
      check(clubs.has(b.clubNow) && clubs.has(b.clubIdeal), 'clubs are named from the bag: ' + tag);
      check(!(b.over > 0 && b.under > 0), 'never both too long and too short: ' + tag);
      check(['far_back', 'back', 'fits', 'forward'].includes(b.status), 'known status: ' + tag);
    }
  }
}
// Longer tees never cost fewer strokes.
for (let yards = 3000; yards < 8500; yards += 50) {
  check(T.analyse({ carry: 220, score: 95, yards: yards + 50 }).strokes >= T.analyse({ carry: 220, score: 95, yards }).strokes, 'more yards never cost less: ' + yards);
}

// ---- STATUS BOUNDARIES ----------------------------------------------------------------
// Status is measured against the unrounded chart; only the screen rounds.
const hi = T.analyse({ carry: 220, score: 95, yards: 6500 }).rangeRaw[1];
const lo = T.analyse({ carry: 220, score: 95, yards: 6500 }).rangeRaw[0];
check(T.analyse({ carry: 220, score: 95, yards: hi + 290 }).status === 'fits', 'just past the range still fits');
check(T.analyse({ carry: 220, score: 95, yards: hi + 300 }).status === 'back', '300 past the range is too far back');
check(T.analyse({ carry: 220, score: 95, yards: hi + 810 }).status === 'far_back', 'over 800 past is far too far back');
check(T.analyse({ carry: 220, score: 95, yards: lo - 300 }).status === 'forward', '300 short of the range is too far forward');

if (failures.length) {
  console.error('Tee Box model failed ' + failures.length + ' of ' + checks + ' checks:\n- ' + failures.slice(0, 25).join('\n- '));
  process.exit(1);
}
console.log('Tee Box model passed ' + checks + ' checks.');
