'use strict';

// The Coach Report is built from the Locker's own numbers, which are stored in
// the unit the profile records them in. Its gap verdicts must say that unit,
// and the two thresholds it copies from The Standing Order are yards: 25 yards
// is 22.9 metres on a metric profile, never 25 metres.

const R = require('../lib/pro/report.js');

const failures = [];
let checks = 0;
function check(condition, message) { checks++; if (!condition) failures.push(message); }

const yardSession = { label: 'Range', clubs: [
  { name: 'Driver', shots: [243, 246, 240, 248, 245] },
  { name: '7-iron', shots: [148, 150, 152, 151, 149] },
  { name: 'PW', shots: [112, 110, 108, 111, 110] }
] };
// the same range session on a metric profile: every shot converted, as
// GolfrawLocker.setUnits stores it
const M = 0.9144;
const metricSession = { label: 'Range', clubs: yardSession.clubs.map((c) => ({
  name: c.name, shots: c.shots.map((s) => Math.round(s * M * 10) / 10)
})) };

const yards = R.buildModel({ session: yardSession, units: 'yards', now: 0 });
const metric = R.buildModel({ session: metricSession, units: 'meters', now: 0 });

check(yards.units === 'yards' && metric.units === 'meters', 'the model records its unit');
check(yards.verdicts.length > 0 && metric.verdicts.length === yards.verdicts.length,
  'the same session reads the same either way: ' + yards.verdicts.length + ' vs ' + metric.verdicts.length);
check(yards.verdicts.every((v) => !/metre/.test(v.text)), 'a yards report never says metres');
check(metric.verdicts.every((v) => !/\byards? \b/.test(v.text.replace(/\(\d+ yards\)/g, ''))),
  'a metric report never says yards: ' + JSON.stringify(metric.verdicts.map((v) => v.text)));
check(/\bmetres\b/.test(metric.verdicts[0].text), 'a metric report says metres: ' + metric.verdicts[0].text);

/* A ladder with a 24-yard gap: inside the 25-yard threshold in both units, so
   neither report may call it a hole. Read in raw metres it is 21.9, which the
   old code compared against 25 and then reported in yards. */
const tight = [
  { name: '5-iron', shots: [180, 181, 179, 180, 182] },
  { name: '6-iron', shots: [156, 157, 155, 156, 158] }
];
const tightMetric = tight.map((c) => ({ name: c.name, shots: c.shots.map((s) => Math.round(s * M * 10) / 10) }));
const okYards = R.gapVerdicts(R.analyse(tight), 'yards');
const okMetric = R.gapVerdicts(R.analyse(tightMetric), 'meters');
check(okYards[0].kind === 'ok' && okMetric[0].kind === 'ok', 'a 24-yard gap is clean in both units');
check(/22\.9 metres \(25 yards\)/.test(okMetric[0].text) && /7\.3 metres \(8 yards\)/.test(okMetric[0].text),
  'the metric threshold keeps the yard figure in view: ' + okMetric[0].text);
check(/25 yards/.test(okYards[0].text) && !/metre/.test(okYards[0].text), 'the yards threshold reads plainly: ' + okYards[0].text);

/* A 26-yard gap is a hole in yards; the same physical gap is 23.8 metres and
   must be a hole in metres too. The old raw comparison called it clean. */
const wide = [
  { name: '5-iron', shots: [180, 181, 179, 180, 182] },
  { name: '6-iron', shots: [154, 155, 153, 154, 156] }
];
const wideMetric = wide.map((c) => ({ name: c.name, shots: c.shots.map((s) => Math.round(s * M * 10) / 10) }));
check(R.gapVerdicts(R.analyse(wide), 'yards')[0].kind === 'gap', 'a 26-yard gap is a hole in yards');
check(R.gapVerdicts(R.analyse(wideMetric), 'meters')[0].kind === 'gap',
  'and the same gap is still a hole in metres: ' + JSON.stringify(R.gapVerdicts(R.analyse(wideMetric), 'meters')[0]));

/* Called without a unit (an older caller, or a share link being re-rendered)
   it must behave exactly as it always did. */
check(JSON.stringify(R.gapVerdicts(R.analyse(tight))) === JSON.stringify(okYards), 'no unit given still means yards');

if (failures.length) {
  console.error('Report units failed ' + failures.length + ' of ' + checks + ' checks:\n- ' + failures.join('\n- '));
  process.exit(1);
}
console.log('Report units passed ' + checks + ' checks.');
