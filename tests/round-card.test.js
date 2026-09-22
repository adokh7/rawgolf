'use strict';

// The Round Card engine (lib/round/round-card.js) and its Locker storage.
// Rounds A-D are worked out by hand from the raw card in the comments, not
// from the engine, then checked against it. After them come the rules each
// finding must obey on thousands of random cards, the Locker round trip in a
// sandbox (the real schema.js and store.js), and export / import.

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const R = require('../lib/round/round-card.js');

const failures = [];
let checks = 0;
function check(condition, message) { checks++; if (!condition) failures.push(message); }
function eq(actual, expected, message) {
  const a = JSON.stringify(actual), e = JSON.stringify(expected);
  check(a === e, message + ': expected ' + e + ', got ' + a);
}

const P18 = R.PARS_18, P9 = R.PARS_9;
function card(pars, scores, putts, pen) {
  return { v: 2, holes: pars.map((p, i) => ({ par: p, score: scores[i], putts: putts ? putts[i] : null,
    pen: pen ? pen[i] : null, fir: null, app: null })) };
}
function fromDiffs(pars, d) { return pars.map((p, i) => p + d[i]); }
const ids = (a) => a.findings.map((f) => f.id);

/* ------------------------------------------------------------ basics --- */
eq(P18.reduce((t, p) => t + p, 0), 72, 'the default card is a par 72');
eq(P9.reduce((t, p) => t + p, 0), 36, 'the default nine is a par 36');

{ // even par, every hole a par
  const a = R.analyse(card(P18, P18.slice()));
  eq([a.gross, a.toPar, a.blowups.length], [72, 0, 0], 'even par totals');
  eq(a.headline, 'No blow-ups and not a single hole over par.', 'even par headline');
  eq(a.findings, [], 'even par has nothing to find');
  eq(a.focus, null, 'even par has no focus');
  eq([a.front.toPar, a.back.toPar], [0, 0], 'even par nines');
}
{ // all bogeys: typical hole is a bogey, doubles would be blow-ups, there are none
  const a = R.analyse(card(P18, fromDiffs(P18, Array(18).fill(1))));
  eq([a.gross, a.toPar, a.typical, a.threshold, a.blowups.length], [90, 18, 1, 2, 0], 'all bogeys');
  eq(a.headline, 'No blow-ups. Eighteen holes went over par, none worse than a bogey, and you finished 18 over par.', 'all-bogey headline');
  eq(a.mix, { under: 0, par: 0, bogey: 18, double: 0, worse: 0 }, 'all-bogey mix');
}
{ // one double in an otherwise par round
  const d = Array(18).fill(0); d[6] = 2;
  const a = R.analyse(card(P18, fromDiffs(P18, d)));
  eq(a.blowups.map((r) => r.hole), [7], 'one double is one blow-up');
  eq(a.headline, 'One hole cost you all 2 of your shots over par.', 'one double headline');
  eq(a.withoutBlowups, 73, 'as a bogey that hole makes it a 73');
}
{ // several doubles and a triple with birdies elsewhere
  const d = [0, 2, 0, -1, 0, 3, 0, 0, -1, 0, 2, 0, -1, 0, 0, 0, 0, 0];
  const a = R.analyse(card(P18, fromDiffs(P18, d)));
  eq([a.toPar, a.blowupToPar], [4, 7], 'blow-ups outweigh the round');
  eq(a.headline, 'Three holes went +7. The other 15 were 3 under par.', 'birdies paid some of it back');
}
{ // under par round with one blow-up
  const d = Array(18).fill(0); d[0] = -1; d[4] = -1; d[9] = -1; d[13] = 2;
  const a = R.analyse(card(P18, fromDiffs(P18, d)));
  eq(a.headline, 'One hole went +2. The other 17 were 3 under par.', 'a 71 with a double');
}

/* ------------------------------------------------ round A (by hand) --- */
// Clean round, score only. Pars 4 4 3 5 4 4 3 4 5 / 4 4 3 5 4 4 3 4 5.
// Scores 4 5 3 5 5 4 3 5 5 / 4 4 4 4 4 5 3 4 5. Five bogeys (2, 5, 8, 12, 15),
// a birdie on 13: 76, +4. Twelve pars, so the median hole is par and a blow-up
// needs a double: none. Out +3, in +1: two apart, so no nines finding.
{
  const a = R.analyse(card(P18, [4, 5, 3, 5, 5, 4, 3, 5, 5, 4, 4, 4, 4, 4, 5, 3, 4, 5]));
  eq([a.gross, a.toPar, a.typical, a.blowups.length, a.front.toPar, a.back.toPar], [76, 4, 0, 0, 3, 1], 'round A numbers');
  eq(a.headline, 'No blow-ups. Five holes went over par, none worse than a bogey, and you finished 4 over par.', 'round A headline');
  eq(ids(a), [], 'round A findings');
  check(a.focus === null && /^Not enough detail to identify a clear practice priority/.test(a.noFocus), 'round A says there is not enough detail');
  eq(a.detail, 'quick', 'round A is score only');
}

/* ------------------------------------------------ round B (by hand) --- */
// Three disasters. Scores 4 5 3 9 4 5 3 4 5 / 5 7 3 5 4 5 3 7 5 = 86, +14.
// Eleven pars, so typical is par: blow-ups are hole 4 (+4 on a par 5), 11 and
// 17 (+3 each) = +10 of +14. As bogeys they are 6+4+4 = 7 shots cheaper: 79.
{
  const a = R.analyse(card(P18, [4, 5, 3, 9, 4, 5, 3, 4, 5, 5, 7, 3, 5, 4, 5, 3, 7, 5]));
  eq([a.gross, a.toPar, a.blowupToPar, a.withoutBlowups], [86, 14, 10, 79], 'round B numbers');
  eq(a.blowups.map((r) => [r.hole, r.d]), [[4, 4], [11, 3], [17, 3]], 'round B blow-ups');
  eq(a.headline, 'Three holes cost you 10 of your 14 shots over par.', 'round B headline');
  eq(a.focus && a.focus.id, 'damage_control', 'round B focus is damage control');
  eq(a.focus.confidence, 'Some evidence', 'the cause is not on a score-only card');
  check(/Add putts and penalties/.test(a.focus.text), 'score-only focus asks for the why');
  eq(R.blowupRule(a), 'A blow-up here is a double bogey or worse.', 'round B rule');
}

/* ------------------------------------------------ round C (by hand) --- */
// Penalty-heavy, every hole detailed. Scores 5 6 3 7 4 5 4 4 6 / 7 5 3 5 5 4 5 5 6
// = 89, +17. Putts all 2 except 1 on hole 8 = 35. Penalties: 1 on 2, 2 on 4,
// 1 on 10, 1 on 16 = 5 strokes. Median hole is a bogey, so blow-ups are
// doubles or worse: 2, 4, 16 (+2) and 10 (+3) = +9, every one with a penalty.
// Hole 10: 7 - 2 putts - 1 penalty = 4 shots to reach a par-4 green, two
// beyond regulation. Taxes: penalties 5, three-putts 0, extra shots 1:
// penalties lead by 4, on a full card, so a strong signal.
{
  const a = R.analyse(card(P18, [5, 6, 3, 7, 4, 5, 4, 4, 6, 7, 5, 3, 5, 5, 4, 5, 5, 6],
    [2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], [0, 1, 0, 2, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0]));
  eq([a.gross, a.toPar, a.putts.total, a.pen.strokes, a.pen.holes], [89, 17, 35, 5, 4], 'round C numbers');
  eq(a.blowups.map((r) => r.hole), [2, 4, 10, 16], 'round C blow-ups');
  eq(a.blowups.map((r) => r.causes), [['penalty'], ['penalty'], ['penalty', 'extra_to_green'], ['penalty']], 'round C causes');
  eq(R.causeText(a.blowups[2]), 'a penalty and two or more extra shots to reach the green', 'cause wording');
  eq(a.gir.hit, 5, 'round C greens: 3, 5, 12, 13 and 15');
  eq(a.headline, 'Four holes cost you 9 of your 17 shots over par.', 'round C headline');
  eq(ids(a), ['penalties'], 'round C findings');
  eq(a.findings[0].text, 'Penalties added five strokes. All four blow-ups had one.', 'round C penalty finding');
  eq([a.focus.id, a.focus.confidence, a.focus.strokes], ['penalties', 'Strong signal', 5], 'round C focus');
  eq(a.withoutBlowups, 84, 'round C as bogeys');
}

/* ------------------------------------------------ round D (by hand) --- */
// Putting-heavy. Scores 5 4 4 5 5 4 3 6 6 / 4 5 3 5 5 4 4 4 6 = 82, +10.
// Putts 3 2 3 2 2 2 2 3 3 / 2 3 2 2 2 1 3 2 2 = 41, six three-putts (1, 3, 8,
// 9, 11, 16) = 6 strokes over two-putting. Greens: 13 of 18. Nine pars and
// eight bogeys make the median 0.5, typical par, so the one double (hole 8)
// is the only blow-up: +2 of +10, not the story.
{
  const a = R.analyse(card(P18, [5, 4, 4, 5, 5, 4, 3, 6, 6, 4, 5, 3, 5, 5, 4, 4, 4, 6],
    [3, 2, 3, 2, 2, 2, 2, 3, 3, 2, 3, 2, 2, 2, 1, 3, 2, 2], Array(18).fill(0)));
  eq([a.gross, a.toPar, a.putts.total, a.putts.three, a.putts.threeTax, a.gir.hit], [82, 10, 41, 6, 6, 13], 'round D numbers');
  eq(a.headline, 'Blow-ups were not the story: one hole cost you 2 of your 10 shots over par.', 'round D headline');
  eq(ids(a), ['three_putts'], 'round D findings');
  eq(a.findings[0].text, 'Six three-putts cost you six strokes over two-putting.', 'round D putting finding');
  eq([a.focus.id, a.focus.confidence], ['putting', 'Strong signal'], 'round D focus');
  eq(a.blowups[0].causes, ['three_putt'], 'round D blow-up anatomy');
}

/* ------------------------------------------------------- nine holes --- */
{ // 5 4 3 7 4 6 3 4 5 on a par 36 = 41, +5; doubles on 4 and 6
  const a = R.analyse(card(P9, [5, 4, 3, 7, 4, 6, 3, 4, 5]));
  eq([a.holes, a.gross, a.toPar, a.blowupToPar, a.withoutBlowups], [9, 41, 5, 4, 39], 'nine-hole numbers');
  check(a.front === undefined && a.back === undefined, 'nine holes have no front and back');
  eq(a.headline, 'Two holes cost you 4 of your 5 shots over par.', 'nine-hole headline');
}
{ // a high handicapper: typical double bogey, so only triples or worse are blow-ups
  const d = [2, 2, 3, 2, 1, 2, 4, 2, 2, 2, 3, 2, 2, 1, 2, 2, 2, 5];
  const a = R.analyse(card(P18, fromDiffs(P18, d)));
  eq([a.gross, a.typical, a.threshold, a.blowups.map((r) => r.hole), a.withoutBlowups], [113, 2, 3, [3, 7, 11, 18], 106], 'high handicap');
  eq(R.blowupRule(a), 'Your typical hole today was a double bogey, so a blow-up here is a triple bogey or worse.', 'adaptive rule wording');
}

/* ----------------------------------------------------- validation ----- */
{
  const c = card(P18, fromDiffs(P18, Array(18).fill(0)));
  c.holes[4].score = null; c.holes[11].score = 16; c.holes[2].par = 7;
  c.holes[6].putts = 7; c.holes[8].pen = 9;
  c.holes[13].putts = 3; c.holes[13].pen = 1; c.holes[13].score = 4;   // 3 putts + 1 penalty leaves no tee shot
  const v = R.validate(c);
  eq(v.errors.map((e) => e.code + ':' + e.hole), ['par:3', 'score_missing:5', 'putts_range:7', 'pen_range:9', 'score_range:12', 'too_many:14'], 'every problem names its hole and box');
  check(!R.analyse(c).ok, 'an invalid card has no analysis');
  eq(R.validate({ holes: new Array(10).fill({ par: 4, score: 4 }) }).errors[0].code, 'holes', 'only 9 or 18 holes');
  const ace = card([3], [1]); ace.holes = ace.holes.concat(card(P18.slice(1), P18.slice(1)).holes);
  ace.holes[0].putts = 0; ace.holes[0].pen = 0;
  check(R.validate(ace).ok, 'a hole-in-one with no putts is valid');
  const zero = card(P18, P18.slice(), Array(18).fill(2)); zero.holes[5].putts = 0; zero.holes[5].score = 3;
  check(R.validate(zero).ok, 'a chip-in with no putts is valid');
  eq(R.greenHit(zero.holes[5]), null, 'no putts means the green is unknown');
}

eq([1, 2, 3, 5].map(R.holeNamePlural), ['bogeys', 'double bogeys', 'triple bogeys', '5 over par'], 'plural hole names');

/* --------------------------------------------------------- greens ------ */
eq(R.greenHit({ par: 4, score: 4, putts: 2 }), true, 'par 4 in two, two putts: green hit');
eq(R.greenHit({ par: 4, score: 5, putts: 2 }), false, 'par 4, three shots to the green: missed');
eq(R.greenHit({ par: 3, score: 3, putts: 2 }), true, 'par 3, on in one');
eq(R.greenHit({ par: 5, score: 5, putts: 2 }), true, 'par 5, on in three');
eq(R.greenHit({ par: 4, score: 5, putts: 2, pen: 1 }), false, 'a penalty stroke counts toward regulation');
eq(R.greenHit({ par: 4, score: 5, putts: null, app: 'hit' }), true, 'a Tendency Engine card falls back to its approach');
eq(R.greenHit({ par: 4, score: 5, putts: null, app: null }), null, 'nothing entered: unknown');
eq(R.approachFor({ par: 4, score: 4, putts: 2, app: null }), 'hit', 'record a hit green');
eq(R.approachFor({ par: 4, score: 5, putts: 2, app: null }), 'miss', 'record a miss');
eq(R.approachFor({ par: 4, score: 5, putts: 2, app: 'short' }), 'short', 'keep a Tendency Engine miss direction');
eq(R.approachFor({ par: 4, score: 4, putts: 2, app: 'short' }), 'hit', 'the card wins when they disagree');

/* ----------------------------------------------------- coverage ------- */
{
  const s = [5, 6, 3, 7, 4, 5, 4, 4, 6, 7, 5, 3, 5, 5, 4, 5, 5, 6];
  const putts = [2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2];
  const pen = [0, 1, 0, 2, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0];
  const some = card(P18, s, putts.map((p, i) => (i < 12 ? p : null)), pen.map((p, i) => (i < 12 ? p : null)));
  const a = R.analyse(some);
  eq([a.coverage.pen.level, a.coverage.putts.level], ['some', 'some'], '12 of 18 holes is some evidence');
  check(a.findings.every((f) => f.id !== 'penalties' || f.confidence === 'Some evidence'), 'partial penalties are some evidence');
  check(/marked as some evidence/.test(a.dataNote), 'the data note says so');
  const none = card(P18, s, putts.map((p, i) => (i < 10 ? p : null)), pen.map((p, i) => (i < 10 ? p : null)));
  const b = R.analyse(none);
  check(b.pen === null && b.putts === null && b.detail === 'quick', '10 of 18 holes is not enough to use');
}

/* ------------------------------------------------ par-type leak ------ */
{ // par 3s at +2 each, everything else par
  const d = P18.map((p) => (p === 3 ? 2 : 0));
  const a = R.analyse(card(P18, fromDiffs(P18, d)));
  eq(ids(a), ['par_type'], 'par 3 leak found');
  eq(a.findings[0].text, 'The par 3s cost you most: +8 across four of them, 2.0 a hole against 0.0 everywhere else.', 'par 3 leak wording');
}

/* ---------------------------------------------- random card rules ---- */
function rnd(n) { return Math.floor(Math.random() * n); }
function randomCard() {
  const holes = Math.random() < 0.25 ? 9 : 18;
  const pars = (holes === 9 ? P9 : P18).map((p) => (Math.random() < 0.1 ? 3 + rnd(3) : p));
  const detail = Math.random() < 0.6;
  const partial = Math.random() < 0.3;
  const hs = pars.map((p) => {
    const d = [-1, 0, 0, 0, 1, 1, 1, 2, 2, 3, 4][rnd(11)];
    const score = Math.max(1, Math.min(15, p + d));
    let putts = null, pen = null;
    if (detail && !(partial && Math.random() < 0.5)) {
      pen = Math.random() < 0.12 ? 1 + rnd(2) : 0;
      putts = rnd(4);
      while (putts + pen > score - 1) { if (putts > 0) putts--; else pen--; }
    }
    return { par: p, score, putts, pen, fir: null, app: null };
  });
  return { v: 2, holes: hs };
}

const CONFS = Object.values(R.CONF);
for (let t = 0; t < 6000; t++) {
  const c = randomCard();
  const a = R.analyse(c);
  if (!a.ok) { check(false, 'random card failed validation: ' + JSON.stringify(R.validate(c).errors)); continue; }
  const T = a.toPar, S = a.blowupToPar;
  check(a.findings.length <= 3, 'at most three findings');
  check(new Set(ids(a)).size === a.findings.length, 'no finding twice');
  check(a.findings.every((f) => CONFS.includes(f.confidence) && f.confidence !== R.CONF.none), 'every finding carries its evidence');
  check(a.blowups.every((r) => r.d >= a.threshold && r.d >= 2), 'every blow-up is a double or worse');
  check(a.rows.filter((r) => r.d >= a.threshold).length === a.blowups.length, 'no blow-up missed');
  check(a.withoutBlowups === a.gross - a.blowups.reduce((x, r) => x + r.d - a.fallback, 0), 'the as-bogeys score adds up');
  check(a.withoutBlowups <= a.gross, 'removing blow-ups never adds strokes');
  check((a.blowups.length === 0) === /^No blow-ups/.test(a.headline), 'the headline agrees with the blow-up count');
  if (a.blowups.length && T > 0 && S <= T) check(a.headline.indexOf(' ' + S + ' of your ' + T + ' ') > 0 || a.headline.indexOf('all ' + T) > 0, 'blow-up headline quotes the card: ' + a.headline);
  if (a.holes === 9) check(!ids(a).includes('nines'), 'nine holes have no nines finding');
  if (ids(a).includes('nines')) check(Math.abs(a.front.toPar - a.back.toPar) >= 3, 'nines finding needs three shots');
  if (ids(a).includes('penalties')) check(a.pen && a.pen.strokes >= 2, 'penalty finding needs two penalty strokes on the card');
  if (ids(a).includes('three_putts')) check(a.putts && a.putts.three >= (a.holes === 18 ? 3 : 2), 'three-putt finding needs the three-putts');
  if (ids(a).includes('missed_greens')) check(!ids(a).includes('penalties') && !ids(a).includes('three_putts'), 'before-the-green never sits beside a penalty or putting story');
  if (ids(a).includes('extra_to_green')) check(a.reach && a.reach.holes >= 2, 'extra-shots finding needs two holes');
  if (a.detail === 'quick') {
    check(ids(a).every((id) => id === 'par_type' || id === 'nines'), 'a score-only card only has score findings');
    check(!a.focus || a.focus.id === 'damage_control', 'a score-only card can only suggest damage control');
  }
  if (a.focus) {
    check(CONFS.includes(a.focus.confidence), 'focus carries its evidence');
    if (['penalties', 'putting', 'short_game'].includes(a.focus.id)) {
      const tax = { penalties: a.pen && a.pen.strokes, putting: a.putts && a.putts.threeTax, short_game: a.reach && a.reach.tax };
      const others = Object.keys(tax).filter((k) => k !== a.focus.id && tax[k] !== null && tax[k] !== undefined).map((k) => tax[k]);
      check(others.every((x) => tax[a.focus.id] > x), 'the focus is the single biggest cost');
      check(tax[a.focus.id] >= (a.holes === 18 ? 3 : 2), 'the focus is worth enough strokes');
    }
    if (a.focus.id === 'damage_control' || a.focus.id === 'approach') check(a.focus.confidence === 'Some evidence', 'a guess at the cause is never a strong signal');
  } else {
    check(typeof a.noFocus === 'string' && a.noFocus.length > 20, 'no focus says why');
  }
  const summary = R.summary(c);
  check(summary.gross === a.gross && summary.blowups === a.blowups.length && summary.holes === a.holes, 'summary matches');
  const share = R.shareText(a);
  check(!/hole \d/i.test(share) && !/card-[0-9a-z]+-[0-9a-z]+/.test(share), 'the share text has no hole-by-hole detail or ids');
}

/* --------------------------------------------------------- share ------ */
{
  const c = card(P18, [5, 6, 3, 7, 4, 5, 4, 4, 6, 7, 5, 3, 5, 5, 4, 5, 5, 6],
    [2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], [0, 1, 0, 2, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0]);
  const a = R.analyse(c);
  eq(R.shareText(a).split('\n'), ['GolfRaw Round Card', '89 (+17)', 'Four holes cost you 9 of your 17 shots over par.',
    'Penalty strokes: 5', 'Putts: 35', '', 'golfraw.com/tools-scorecard-analyzer'], 'share text for round C');
  check(R.shareText(a, { course: 'Muni' }).split('\n')[1] === 'Muni', 'the course only when asked');
}

/* ------------------------------------------------ export / import ---- */
{
  const a = Object.assign(card(P18, fromDiffs(P18, Array(18).fill(1)), Array(18).fill(2), Array(18).fill(0)),
    { id: 'card-a', course: 'Muni', playedAt: Date.UTC(2026, 8, 21, 12), createdAt: 5, updatedAt: 9 });
  const b = Object.assign(card(P9, P9.slice()), { id: 'card-b', course: '', playedAt: Date.UTC(2026, 8, 14, 12), createdAt: 3, updatedAt: 4 });
  const text = R.exportRounds([a, b], 1000);
  const back = R.parseImport(text);
  check(back.ok && back.skipped === 0, 'export reads back');
  eq(back.rounds.map((r) => [r.id, r.course, r.playedAt, r.holes.length]), [['card-a', 'Muni', a.playedAt, 18], ['card-b', '', b.playedAt, 9]], 'round trip keeps the rounds');
  eq(back.rounds[0].holes, a.holes, 'round trip keeps every hole');
  eq(R.parseImport('not json').error, 'not_json', 'garbage is refused');
  eq(R.parseImport('{"format":"something"}').error, 'not_rounds', 'another file is refused');
  eq(R.parseImport('{"format":"golfraw.rounds","version":9,"rounds":[]}').error, 'newer', 'a newer export says so');
  // a Tendency Engine card from a whole-Locker backup: no v, no penalties
  const te = { id: 'card-te', course: '', playedAt: 1, updatedAt: 2, holes: P18.map((p) => ({ par: p, score: p + 1, fir: 'left', app: 'short', putts: 2 })) };
  const half = { id: 'card-half', holes: P18.map((p, i) => ({ par: p, score: i < 9 ? p : null })) };
  const lk = R.parseImport(JSON.stringify({ format: 'golfraw.locker', version: 3, scorecards: [te, half] }));
  check(lk.ok && lk.rounds.length === 1 && lk.skipped === 1, 'a Locker backup gives its finished cards');
  eq([lk.rounds[0].v, lk.rounds[0].holes[0].pen, lk.rounds[0].holes[0].fir], [1, null, 'left'], 'an older card keeps its version and fields');
  const plan = R.mergePlan([{ id: 'card-a', updatedAt: 9 }, { id: 'card-b', updatedAt: 1 }], back.rounds);
  eq([plan.write.map((c) => c.id), plan.alreadyHere], [['card-b'], 1], 'import adds new or newer rounds only');
  const csv = R.toCSV([Object.assign({}, a, { course: '=HYPERLINK("x")' })]).split('\r\n');
  eq(csv[0], 'date,course,hole,par,score,putts,penalties,green_in_regulation,fairway', 'CSV header');
  eq(csv.length, 20, 'one CSV row per hole plus the header');
  check(csv[1].indexOf('"\'=HYPERLINK(""x"")"') > 0, 'a course name cannot run as a formula: ' + csv[1]);
  eq(csv[1].split(',').slice(-5), ['5', '2', '0', 'no', ''], 'CSV hole row');
}
{
  const cards = [{ holes: [] }, Object.assign(card(P9, P9.slice()), { createdAt: 50, playedAt: 7 }), Object.assign(card(P18, P18.slice()), { createdAt: 20, playedAt: 3 })];
  eq(R.habit(cards), { validRounds: 2, dates: [3, 7], firstLoggedAt: 20 }, 'habit counts valid rounds only');
}

/* ---------------------------------------------- Locker round trip ---- */
function sandbox(storage) {
  const ctx = { console, Promise, Math, JSON, Date, Object, Array, String, Number, isFinite, parseFloat, parseInt,
    setTimeout, clearTimeout, localStorage: storage };
  ctx.window = ctx;
  vm.createContext(ctx);
  for (const f of ['schema.js', 'store.js']) {
    vm.runInContext(fs.readFileSync(path.join(__dirname, '..', 'lib', 'locker', f), 'utf8'), ctx, { filename: f });
  }
  return ctx.GolfrawLocker;
}
function memoryStorage() {
  const store = {};
  return { getItem: (k) => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v); },
    removeItem: (k) => { delete store[k]; }, _store: store };
}
function toRecord(c, extra) {
  const rec = Object.assign({ v: 2, course: '', holes: c.holes.map((h) => Object.assign({}, h, { app: R.approachFor(h) })) }, extra);
  rec.summary = R.summary(c);
  return rec;
}

(async () => {
  const mem = memoryStorage();
  const L = sandbox(mem);
  await L.ready();
  const c18 = card(P18, [5, 6, 3, 7, 4, 5, 4, 4, 6, 7, 5, 3, 5, 5, 4, 5, 5, 6],
    [2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], [0, 1, 0, 2, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0]);
  const saved = await L.saveScorecard(toRecord(c18, { course: 'Muni', playedAt: 2000 }));
  check(saved.v === 2 && saved.createdAt > 0 && saved.holes[1].pen === 1, 'a v2 round saves with penalties and createdAt');
  eq(saved.holes.filter((h) => h.app === 'miss').length, 13, 'missed greens are stored as miss');
  eq(saved.summary.gross, 89, 'the summary is stored');
  const again = await L.getScorecard(saved.id);
  check(R.analyse(again).gross === 89 && again.course === 'Muni', 'reopen gives the same round');

  const edited = Object.assign({}, again, { holes: again.holes.map((h, i) => (i === 0 ? Object.assign({}, h, { score: 4, app: 'hit' }) : h)) });
  edited.summary = R.summary(edited);
  const resaved = await L.saveScorecard(edited);
  check(resaved.id === saved.id && resaved.createdAt === saved.createdAt && resaved.summary.gross === 88, 'edit keeps the id and first-saved date');

  const nine = await L.saveScorecard(toRecord(card(P9, [5, 4, 3, 7, 4, 6, 3, 4, 5]), { playedAt: 3000 }));
  const te = await L.saveScorecard({ course: '', playedAt: 1000, holes: P18.map((p, i) => ({ par: p, score: i < 5 ? p : null })) });
  check(te.v === 1, 'a Tendency Engine card is v1');
  const draft = await L.getDraftScorecard();
  check(draft && draft.id === te.id, 'the unfinished Tendency Engine card is still the draft, not the finished nine');
  const done = await L.listCompletedScorecards();
  eq(done.map((c) => c.id), [saved.id], 'the Tendency Engine and Coach Report only see full 18-hole rounds');
  const all = await L.listScorecards();
  eq(all.map((c) => c.id), [nine.id, saved.id, te.id], 'every card, newest played first');
  eq(all.filter(R.isValidRound).map((c) => c.id), [nine.id, saved.id], 'the Round Card history is every finished card');

  await L.deleteScorecard(nine.id);
  eq((await L.listScorecards()).length, 2, 'delete removes one round');

  const exp = await L.exportLocker();
  check(exp.version === 4 && exp.scorecards.length === 2, 'the Locker backup is v4 with both cards');
  const fresh = sandbox(memoryStorage());
  await fresh.ready();
  const imported = await fresh.importJSON(JSON.stringify(exp), 'merge');
  check(imported.scorecards === 2 && (await fresh.listScorecards()).length === 2, 'the backup restores into an empty Locker');
  const fromBackup = R.parseImport(JSON.stringify(exp));
  eq(fromBackup.rounds.map((c) => c.id).sort(), [saved.id, te.id].filter((id) => id !== te.id).sort(), 'the Round Card reads its rounds out of a Locker backup');

  // corrupt mirror: the Locker opens empty rather than failing
  const broken = memoryStorage(); broken.setItem('golfraw_locker_mirror', '{not json');
  const B = sandbox(broken); await B.ready();
  eq((await B.listScorecards()).length, 0, 'corrupt local data opens as an empty history');
  // a record that fails the schema is skipped, the rest still load
  const mixed = memoryStorage();
  const M = sandbox(mixed); await M.ready();
  await M.saveScorecard(toRecord(c18, { playedAt: 10 }));
  const doc = JSON.parse(mixed.getItem('golfraw_locker_mirror'));
  doc.scorecards.bad = { id: 'bad', holes: [{ par: 9, score: 'x' }] };
  mixed.setItem('golfraw_locker_mirror', JSON.stringify(doc));
  const M2 = sandbox(mixed); await M2.ready();
  eq((await M2.listScorecards()).length, 1, 'a damaged record is skipped, the good one loads');
  // storage switched off: every call throws, the Locker keeps the round in memory
  const off = { getItem() { throw new Error('denied'); }, setItem() { throw new Error('denied'); }, removeItem() { throw new Error('denied'); } };
  const O = sandbox(off);
  let offOk = true;
  try { await O.ready(); await O.saveScorecard(toRecord(c18, { playedAt: 10 })); } catch (e) { offOk = false; }
  check(offOk && (await O.listScorecards()).length === 1, 'with storage blocked the round still works for the visit');

  if (failures.length) {
    console.error(failures.slice(0, 40).join('\n'));
    console.error(failures.length + ' of ' + checks + ' Round Card checks failed');
    process.exit(1);
  }
  console.log('round-card: ' + checks + ' checks passed');
})().catch((e) => { console.error(e); process.exit(1); });
