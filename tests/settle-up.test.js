'use strict';

// Contract for lib/games/settle-core.js and lib/games/settle-up.js (The Settle
// Up). Expected money is worked out by hand in each scenario, not taken from
// the engine; the sweeps then check the invariants on thousands of rounds.

const C = require('../lib/games/settle-core.js');
const S = require('../lib/games/settle-up.js');

const failures = [];
let checks = 0;
function check(condition, message) { checks++; if (!condition) failures.push(message); }
const eq = (a, b) => JSON.stringify(a) === JSON.stringify(b);
let seed = 20260922;
function rand() { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; }

const PARS = S.DEFAULT_PARS, SI = S.DEFAULT_SI;
function card(n, fill) { return Array.from({ length: n }, (_, p) => Array.from({ length: 18 }, (_, h) => fill(p, h))); }
function game(o) {
  const P = o.players || 4;
  return {
    players: Array.from({ length: P }, (_, i) => ({ name: 'P' + i, hcp: o.hcps ? o.hcps[i] : null })),
    round: o.round || '18', scoring: o.scoring || 'gross', pars: o.pars || PARS, si: o.si || SI,
    scores: o.scores,
    skins: Object.assign({ on: true, stake: 100, carry: true, endCarry: 'lost', playoffWinner: null, birdieDouble: false, strokes: 'full' }, o.skins || {}),
    nassau: Object.assign({ on: false, stake: 500, presses: 'off', manual: [] }, o.nassau || {}),
    ctp: Object.assign({ on: false, stake: 100, winners: {} }, o.ctp || {})
  };
}
const skinsOnly = (o) => { const g = game(o); g.nassau.on = false; return g; };
const nassauOnly = (o) => { const g = game(o); g.skins.on = false; g.nassau.on = true; return g; };
function applyTransfers(n, transfers) {
  const b = new Array(n).fill(0);
  transfers.forEach((t) => { b[t.from] -= t.amount; b[t.to] += t.amount; });
  return b;
}

// ---- MONEY -----------------------------------------------------------------------
check(C.toMinor('2') === 200 && C.toMinor('2.5') === 250 && C.toMinor('0.25') === 25 && C.toMinor('1,50') === 150, 'stakes parse to exact minor units');
for (const bad of ['', 'abc', '-1', '1.234', '1e3', ' ', '10000000']) check(C.toMinor(bad) === null, 'invalid stake refused: "' + bad + '"');
check(C.toMinor('0') === 0, 'zero parses (and is refused by the game)');
check(C.format(650, '€') === '€6.50' && C.format(1200, '$') === '$12' && C.format(123456, '£') === '£1,234.56', 'currency formats');
check(C.format(100, 'pts') === '1 pt' && C.format(250, 'pts') === '2.50 pts' && C.format(0, '$') === '$0', 'points format, no minus zero');

// ---- SKINS -----------------------------------------------------------------------
// One clear winner every hole: P0 shoots 3s, everyone else 5s. 18 skins at $1, 3 losers.
{
  const r = S.compute(skinsOnly({ scores: card(4, (p) => (p === 0 ? 3 : 5)) }));
  check(r.ok && eq(r.balances, [5400, -1800, -1800, -1800]), 'one winner every hole: +$54 / -$18 each');
  check(eq(r.transfers, [{ from: 1, to: 0, amount: 1800 }, { from: 2, to: 0, amount: 1800 }, { from: 3, to: 0, amount: 1800 }]), 'three payments to the winner');
  check(r.skins.count[0] === 18 && r.skins.end.carried === 0, '18 skins, nothing carried');
}
// All ties: every skin carries; after 18 nobody wins them, or a playoff winner takes all 18.
{
  const tied = card(4, () => 4);
  const lost = S.compute(skinsOnly({ scores: tied }));
  check(lost.ok && lost.balances.every((v) => v === 0) && lost.transfers.length === 0, 'all ties, nobody wins the carries: all square');
  check(lost.skins.end.carried === 18 && lost.skins.end.rule === 'lost', '18 skins reported as carried and lost');
  const po = S.compute(skinsOnly({ scores: tied, skins: { endCarry: 'playoff', playoffWinner: 2 } }));
  check(po.ok && eq(po.balances, [-1800, -1800, 5400, -1800]), 'playoff winner takes all 18 carried skins');
  const missing = S.compute(skinsOnly({ scores: tied, skins: { endCarry: 'playoff', playoffWinner: null } }));
  check(!missing.ok && missing.errors[0].code === 'playoff_winner' && missing.errors[0].carried === 18, 'playoff rule without a winner asks for one');
}
// Carryover chain: holes 1-3 tied, P1 wins hole 4 outright -> 4 skins. Everyone else ties the rest? No:
// holes 5-18 won alternately so nothing carries at the end.
{
  const sc = card(3, (p, h) => {
    if (h < 3) return 4;                       // tied
    if (h === 3) return p === 1 ? 3 : 5;       // P1 wins 4 skins
    return p === h % 3 ? 3 : 5;                // one outright winner per hole
  });
  const r = S.compute(skinsOnly({ players: 3, scores: sc }));
  const h4 = r.skins.holes[3];
  check(r.ok && h4.outcome === 'won' && h4.winner === 1 && h4.skins === 4 && h4.carried === 3, 'carry chain: 3 carried + 1 = 4 skins on hole 4');
  check(r.skins.holes.slice(0, 3).every((x) => x.outcome === 'carried'), 'holes 1-3 carried');
  // Holes 5-18: winners by h % 3 for h = 4..17 -> P0: 6,9,12,15 (4) ; P1: 4,7,10,13,16 (5) ; P2: 5,8,11,14,17 (5)
  // Skins won: P0 4, P1 4 + 5 = 9, P2 5. Each skin: +2 for the winner, -1 for the other two.
  // P0: 4*2 - 9 - 5 = -6 ; P1: 9*2 - 4 - 5 = 9 ; P2: 5*2 - 4 - 9 = -3  (dollars)
  check(eq(r.balances, [-600, 900, -300]), 'carry chain balances worked by hand: -6 / +9 / -3');
}
// Final-hole carryover: holes 17 and 18 tied after an otherwise decided round.
{
  const sc = card(4, (p, h) => (h >= 16 ? 4 : (p === 0 ? 3 : 5)));
  const r = S.compute(skinsOnly({ scores: sc }));
  check(r.ok && r.skins.end.carried === 2 && r.skins.count[0] === 16, 'last two holes carried off the end');
  check(eq(r.balances, [4800, -1600, -1600, -1600]), 'carried-off skins cost nobody anything');
  const po = S.compute(skinsOnly({ scores: sc, skins: { endCarry: 'playoff', playoffWinner: 3 } }));
  check(eq(po.balances, [4800 - 200, -1600 - 200, -1600 - 200, -1600 + 600]), 'playoff for the last two: P3 +$6, others -$2');
}
// Carryovers off: tied holes are void, nothing moves.
{
  const sc = card(3, (p, h) => (h % 2 === 0 ? 4 : (p === 2 ? 3 : 5)));
  const r = S.compute(skinsOnly({ players: 3, scores: sc, skins: { carry: false } }));
  check(r.ok && r.skins.holes.filter((x) => x.outcome === 'void').length === 9, 'carryovers off: 9 tied holes void');
  check(r.skins.holes.every((x) => x.outcome !== 'won' || x.skins === 1), 'carryovers off: every skin is worth one');
  check(eq(r.balances, [-900, -900, 1800]) && r.skins.end.carried === 0, 'carryovers off: 9 skins at $1 x 2 losers');
}
// Birdie doubles: a birdie win with one carried skin is worth (1 + 1) x 2 = 4.
{
  const sc = card(2, (p, h) => (h === 0 ? 4 : h === 1 ? (p === 0 ? 3 : 4) : 4));    // hole 1 tied, hole 2 birdie (par 4)
  const r = S.compute(skinsOnly({ players: 2, scores: sc, skins: { birdieDouble: true } }));
  const h2 = r.skins.holes[1];
  check(r.ok && h2.birdie && h2.skins === 4, 'birdie with one carried: 4 skins');
  const off = S.compute(skinsOnly({ players: 2, scores: sc }));
  check(off.skins.holes[1].skins === 2, 'without the birdie rule: 2 skins');
}
// Group sizes 2 to 6: one winner per hole, rotating. Money is zero-sum and matches the skin count.
for (let P = 2; P <= 6; P++) {
  const r = S.compute(skinsOnly({ players: P, scores: card(P, (p, h) => (p === h % P ? 3 : 5)) }));
  check(r.ok && r.balances.reduce((a, b) => a + b, 0) === 0, `${P} players: zero-sum`);
  r.skins.count.forEach((n, i) => check(r.balances[i] === n * 100 * (P - 1) - (18 - n) * 100, `${P} players: player ${i} balance = own skins x (P-1) - others' skins`));
}
// Stakes: zero and nonsense are refused; cents stay exact.
check(S.compute(skinsOnly({ scores: card(4, () => 4), skins: { stake: 0 } })).errors[0].code === 'stake_skins', 'zero skin stake is refused');
check(S.compute(skinsOnly({ scores: card(4, () => 4), skins: { stake: null } })).errors[0].code === 'stake_skins', 'invalid skin stake is refused');
{
  const r = S.compute(skinsOnly({ players: 3, scores: card(3, (p, h) => (p === h % 3 ? 3 : 5)), skins: { stake: 25 } }));
  check(r.balances.every((v) => v % 25 === 0 && Number.isInteger(v)) && eq(r.balances, [0, 0, 0]), '25c skins, 6 each: exact and square');
}
// Corrections: the engine is pure, so changing one score changes exactly that hole.
{
  const sc = card(4, (p) => (p === 0 ? 3 : 5));
  const before = S.compute(skinsOnly({ scores: sc }));
  const fixed = sc.map((row) => row.slice()); fixed[0][5] = 5;              // P0's hole 6 was really a 5: now a 4-way tie
  const after = S.compute(skinsOnly({ scores: fixed }));
  check(before.skins.count[0] === 18 && after.skins.holes[5].outcome === 'carried' && after.skins.holes[6].skins === 2, 'a corrected score re-settles from that hole on');
  check(eq(before.skins.count, S.compute(skinsOnly({ scores: sc })).skins.count), 'same card, same answer');
}
// Missing and bad scores name the exact player and hole; a short card never crashes.
{
  const sc = card(4, () => 4); sc[2][6] = null; sc[3][11] = 25;
  const r = S.compute(skinsOnly({ scores: sc }));
  check(!r.ok && r.errors.some((e) => e.code === 'score_missing' && e.player === 2 && e.hole === 6), 'missing score names player 3, hole 7');
  check(r.errors.some((e) => e.code === 'score_range' && e.player === 3 && e.hole === 11), 'score of 25 names player 4, hole 12');
  const short = S.compute(skinsOnly({ players: 5, scores: card(4, () => 4) }));
  check(!short.ok && short.errors.filter((e) => e.player === 4).length === 18, 'a fifth player with no card row gets 18 missing-score errors, not a crash');
}

// ---- HANDICAPS ----------------------------------------------------------------------
{
  const gross = card(4, (p, h) => 3 + ((p * 7 + h * 3) % 4));
  const g = S.compute(skinsOnly({ scores: gross }));
  const scratch = S.compute(skinsOnly({ scores: gross, scoring: 'net', hcps: [0, 0, 0, 0] }));
  check(eq(g.balances, scratch.balances), 'scratch players: net equals gross');
  const equal = S.compute(skinsOnly({ scores: gross, scoring: 'net', hcps: [12, 12, 12, 12] }));
  check(eq(g.balances, equal.balances), 'equal handicaps: net equals gross');
  const equalLow = S.compute(skinsOnly({ scores: gross, scoring: 'net', hcps: [12, 12, 12, 12], skins: { strokes: 'low' } }));
  check(eq(g.balances, equalLow.balances), 'equal handicaps off the low: net equals gross');
}
// Strokes land on the right holes: 5 strokes -> stroke index 1-5.
{
  const a = C.allocate(5, S.ALL, SI);
  S.ALL.forEach((h) => check(a[h] === (SI[h] <= 5 ? 1 : 0), `5 strokes: hole ${h + 1} (SI ${SI[h]})`));
  const plus = C.allocate(-2, S.ALL, SI);
  S.ALL.forEach((h) => check(plus[h] === (SI[h] >= 17 ? -1 : 0), `+2: gives back on SI 17 and 18 only (hole ${h + 1})`));
  const big = C.allocate(22, S.ALL, SI);
  S.ALL.forEach((h) => check(big[h] === (SI[h] <= 4 ? 2 : 1), `22 strokes: two on SI 1-4, one elsewhere (hole ${h + 1})`));
}
// Full handicaps vs off the low (Rules of Handicapping, Appendix C): 4 and 10.
{
  const full4 = C.allocate(4, S.ALL, SI), full10 = C.allocate(10, S.ALL, SI), low6 = C.allocate(6, S.ALL, SI);
  S.ALL.forEach((h) => {
    const edgeFull = full10[h] - full4[h];
    check(edgeFull === (SI[h] >= 5 && SI[h] <= 10 ? 1 : 0), `full: the 10 has a one-stroke edge on SI 5-10 only (hole ${h + 1})`);
    check(low6[h] === (SI[h] <= 6 ? 1 : 0), `off the low: the 10 gets 6 strokes on SI 1-6 (hole ${h + 1})`);
  });
}
// Net changes a result: P1 (hcp 18) makes 5 on every hole, P0 (scratch) makes 4. Net: all tied.
{
  const sc = card(2, (p) => (p === 0 ? 4 : 5));
  const gross = S.compute(skinsOnly({ players: 2, scores: sc }));
  const net = S.compute(skinsOnly({ players: 2, scores: sc, scoring: 'net', hcps: [0, 18] }));
  check(eq(gross.balances, [1800, -1800]), 'gross: the scratch player wins every hole');
  check(net.ok && net.balances.every((v) => v === 0) && net.skins.end.carried === 18, 'net: one stroke a hole makes every hole a tie');
}
// Invalid handicaps are refused by name.
for (const bad of [55, -11, 2.5, NaN, null]) {
  const r = S.compute(skinsOnly({ players: 2, scores: card(2, () => 4), scoring: 'net', hcps: [bad, 0] }));
  check(!r.ok && r.errors.some((e) => e.code === 'hcp' && e.player === 0), 'handicap refused: ' + bad);
}
check(S.compute(skinsOnly({ players: 2, scores: card(2, () => 4), scoring: 'net', hcps: [-2, 5] })).ok, 'plus handicap (-2) accepted');
{
  const badSI = SI.slice(); badSI[3] = badSI[4];
  const r = S.compute(skinsOnly({ players: 2, scores: card(2, () => 4), scoring: 'net', hcps: [0, 5], si: badSI }));
  check(!r.ok && r.errors.some((e) => e.code === 'si'), 'a stroke index row with a repeat is refused');
}

// ---- NASSAU -------------------------------------------------------------------------
// A wins holes 1-2 (front), B wins 10-11 (back), everything else halved: front A, back B, 18 all square.
{
  const sc = card(2, (p, h) => (h <= 1 ? (p === 0 ? 3 : 4) : h === 9 || h === 10 ? (p === 1 ? 3 : 4) : 4));
  const r = S.compute(nassauOnly({ players: 2, scores: sc }));
  const bets = r.nassau[0].bets.map((b) => b.seg + ':' + b.margin + ':' + b.winner);
  check(r.ok && eq(bets, ['front:2:0', 'back:-2:1', 'overall:0:null']), 'front A 2 up, back B 2 up, 18 all square');
  check(eq(r.balances, [0, 0]) && r.transfers.length === 0, 'front win, back loss, overall push: nobody pays');
}
// All three halved.
{
  const r = S.compute(nassauOnly({ players: 2, scores: card(2, () => 4) }));
  check(r.ok && r.nassau[0].bets.every((b) => b.winner === null) && eq(r.balances, [0, 0]), 'all segments halved: all square');
}
// One player wins everything: front, back and 18 at $5 = $15.
{
  const r = S.compute(nassauOnly({ players: 2, scores: card(2, (p) => (p === 0 ? 4 : 5)) }));
  check(eq(r.balances, [1500, -1500]) && eq(r.transfers, [{ from: 1, to: 0, amount: 1500 }]), 'clean sweep: $15');
}
// Three players: three pairs. P0 beats both, P1 beats P2: P0 +30, P1 0, P2 -30.
{
  const r = S.compute(nassauOnly({ players: 3, scores: card(3, (p) => 4 + p) }));
  check(r.nassau.length === 3 && eq(r.balances, [3000, 0, -3000]), 'round robin of three pairs');
  check(eq(r.transfers, [{ from: 2, to: 0, amount: 3000 }]), 'P1 is square and never pays or receives');
}
// Net Nassau: P1 (hcp 9) gets 9 strokes from P0 (hcp 0) on SI 1-9. Scores: P0 4s, P1 5s.
// Stroke holes are halved; P0 wins the other 9. Front: SI<=9 holes on the front are 7,1,3,9,5 -> 5 halved, 4 won by P0.
{
  const sc = card(2, (p) => (p === 0 ? 4 : 5));
  const r = S.compute(nassauOnly({ players: 2, scores: sc, scoring: 'net', hcps: [0, 9] }));
  const front = r.nassau[0].bets.find((b) => b.seg === 'front');
  const back = r.nassau[0].bets.find((b) => b.seg === 'back');
  check(r.nassau[0].give.player === 1 && r.nassau[0].give.strokes === 9, 'the higher handicap gets the difference');
  check(front.margin === 4 && back.margin === 5, 'net: P0 4 up on the front (5 stroke holes), 5 up on the back (4)');
  check(eq(r.balances, [1500, -1500]), 'still a sweep: $15');
  const flip = S.compute(nassauOnly({ players: 2, scores: sc, scoring: 'net', hcps: [0, 18] }));
  check(eq(flip.balances, [0, 0]), 'net with 18 strokes: every hole halved');
}
// Automatic presses. B loses holes 1 and 2 -> 2 down -> press by B from hole 3.
// Then everything halved. Front main: A 2 up (+5). Press 3-9: halved (0). Back, 18 halved... 18: A 2 up (+5).
{
  const sc = card(2, (p, h) => (h <= 1 ? (p === 0 ? 3 : 4) : 4));
  const r = S.compute(nassauOnly({ players: 2, scores: sc, nassau: { presses: 'auto' } }));
  const presses = r.nassau[0].bets.filter((b) => b.kind === 'press');
  check(presses.length === 2, 'two presses: one on the front, one on the 18');
  check(presses.every((b) => b.by === 1 && b.from === 2 && b.auto && b.margin === 0), 'pressed by the player 2 down, from hole 3, halved');
  check(presses[0].to === 8 && presses[1].to === 17, 'presses run to the end of their nine or the 18');
  check(eq(r.balances, [1000, -1000]), 'front and 18 to A, presses halved: $10');
}
// Presses of presses: A wins holes 1-4. Main 4 up; press from 3 goes 2 down after hole 4 -> press from 5.
{
  const sc = card(2, (p, h) => (h <= 3 ? (p === 0 ? 3 : 4) : 4));
  const r = S.compute(nassauOnly({ players: 2, scores: sc, nassau: { presses: 'auto' } }));
  const front = r.nassau[0].bets.filter((b) => b.seg === 'front').map((b) => b.kind + '@' + (b.from + 1) + ':' + b.margin);
  check(eq(front, ['main@1:4', 'press@3:2', 'press@5:0']), 'a press that goes 2 down is pressed again');
  // Front: main +5, press@3 +5, press@5 0. Back: halved. 18: main 4 up (+5), press@3 2 up (+5), press@5 0. A +20.
  check(eq(r.balances, [2000, -2000]), 'presses of presses settle: $20');
}
// No new press on the last hole of a nine.
{
  const sc = card(2, (p, h) => (h === 7 || h === 8 ? (p === 0 ? 3 : 4) : 4));
  const r = S.compute(nassauOnly({ players: 2, scores: sc, nassau: { presses: 'auto' } }));
  check(r.nassau[0].bets.filter((b) => b.seg === 'front' && b.kind === 'press').length === 0, 'going 2 down on hole 9 starts nothing on the front');
}
// Manual press: B presses the back nine from hole 14 and wins holes 14 and 15.
{
  const sc = card(2, (p, h) => (h === 13 || h === 14 ? (p === 1 ? 3 : 4) : 4));
  const r = S.compute(nassauOnly({ players: 2, scores: sc, nassau: { presses: 'manual', manual: [{ by: 1, against: 0, bet: 'back', from: 13 }] } }));
  const press = r.nassau[0].bets.find((b) => b.kind === 'press');
  check(r.ok && press.by === 1 && press.from === 13 && press.to === 17 && press.winner === 1 && !press.auto, 'manual press recorded: who, where, result');
  check(eq(r.balances, [-1500, 1500]), 'back, press and 18 to B: $15');
  const bad = S.compute(nassauOnly({ players: 2, scores: sc, nassau: { presses: 'manual', manual: [{ by: 1, against: 1, bet: 'back', from: 13 }] } }));
  check(!bad.ok && bad.errors[0].code === 'press', 'a press against yourself is refused');
  const first = S.compute(nassauOnly({ players: 2, scores: sc, nassau: { presses: 'manual', manual: [{ by: 1, against: 0, bet: 'back', from: 9 }] } }));
  check(!first.ok, 'a press on the first hole of its bet is refused');
}
check(S.compute(Object.assign(nassauOnly({ players: 2, scores: card(2, () => 4) }), { round: 'front' })).errors[0].code === 'nassau_needs_18', 'a Nassau needs 18 holes');

// ---- CLOSEST TO THE PIN --------------------------------------------------------------
{
  const g = skinsOnly({ players: 3, scores: card(3, () => 4) });
  g.skins.on = false; g.nassau.on = true; g.nassau.stake = 500;
  g.ctp = { on: true, stake: 200, winners: { 2: 1, 6: 1, 10: null, 15: 2 } };
  const r = S.compute(g);
  // Par 3s on the default card: holes 3, 7, 11, 16. P1 wins two, P2 one.
  check(r.ok && r.ctp.length === 4 && eq(r.parts.ctp, [-600, 600, 0]), 'closest to the pin: P1 +$8 -$2, P2 +$4 -$4, P0 -$6');
}

// ---- SETTLEMENT ------------------------------------------------------------------------
// Minimal transfers, checked against an independent brute force.
function bruteMin(b) {
  // Minimum payments = players with a balance - most zero-sum groups they split into.
  const idx = b.map((v, i) => i).filter((i) => b[i] !== 0);
  let best = 0;
  (function go(rem, groups) {
    if (!rem.length) { best = Math.max(best, groups); return; }
    const [f, ...rest] = rem;
    for (let m = 0; m < (1 << rest.length); m++) {
      const g = [f], left = [];
      rest.forEach((x, k) => (m & (1 << k) ? g : left).push(x));
      if (g.reduce((s, i) => s + b[i], 0) === 0) go(left, groups + 1);
    }
  })(idx, 0);
  return idx.length - best;
}
for (let t = 0; t < 4000; t++) {
  const n = 2 + Math.floor(rand() * 5);
  const b = []; let s = 0;
  for (let i = 0; i < n - 1; i++) { const v = Math.round((rand() - 0.5) * 12) * 250; b.push(v); s += v; }
  b.push(-s);
  const tr = C.settle(b);
  const tag = JSON.stringify(b);
  check(eq(applyTransfers(n, tr), b), 'transfers reproduce the balances: ' + tag);
  check(tr.every((x) => x.amount > 0 && Number.isInteger(x.amount) && x.from !== x.to), 'positive whole amounts, nobody pays themselves: ' + tag);
  check(tr.length === bruteMin(b), `fewest payments (${tr.length} vs ${bruteMin(b)}): ` + tag);
  const payers = new Set(tr.map((x) => x.from)), payees = new Set(tr.map((x) => x.to));
  check([...payers].every((p) => !payees.has(p)), 'nobody both pays and receives: ' + tag);
}
check(eq(C.settle([500, -500, 300, -300]), [{ from: 1, to: 0, amount: 500 }, { from: 3, to: 2, amount: 300 }]), 'two pairs settle as two payments, not three');

// Full-game sweep: random groups, games, rules. Always zero-sum, never an impossible payment.
for (let t = 0; t < 1500; t++) {
  const P = 2 + Math.floor(rand() * 5);
  const scores = card(P, () => 3 + Math.floor(rand() * 4));
  const g = game({ players: P, scores, scoring: rand() < 0.5 ? 'net' : 'gross', hcps: Array.from({ length: P }, () => Math.floor(rand() * 30) - 2) });
  g.skins.on = rand() < 0.8; g.nassau.on = !g.skins.on || rand() < 0.5;
  g.skins.carry = rand() < 0.7; g.skins.birdieDouble = rand() < 0.3; g.skins.strokes = rand() < 0.5 ? 'full' : 'low';
  g.skins.endCarry = rand() < 0.5 ? 'lost' : 'playoff'; g.skins.playoffWinner = Math.floor(rand() * P);
  g.nassau.presses = ['off', 'auto'][Math.floor(rand() * 2)];
  g.skins.stake = 25 * (1 + Math.floor(rand() * 20)); g.nassau.stake = 50 * (1 + Math.floor(rand() * 20));
  const r = S.compute(g);
  const tag = `sweep ${t}`;
  check(r.ok, tag + ' runs');
  if (!r.ok) continue;
  check(r.balances.reduce((a, b) => a + b, 0) === 0, tag + ' zero-sum');
  ['skins', 'nassau', 'ctp'].forEach((k) => check(r.parts[k].reduce((a, b) => a + b, 0) === 0, tag + ' ' + k + ' zero-sum'));
  check(eq(applyTransfers(P, r.transfers), r.balances), tag + ' transfers settle the balances');
  check(r.transfers.length <= Math.max(0, r.balances.filter((v) => v).length - 1), tag + ' at most one fewer payment than players owed');
  if (r.skins) {
    const paid = r.skins.count.reduce((a, b) => a + b, 0) * g.skins.stake * (P - 1);
    const won = r.parts.skins.filter((v) => v > 0).reduce((a, b) => a + b, 0);
    check(won <= paid, tag + ' nobody wins more than the skins paid out');
  }
}

if (failures.length) {
  console.error('Settle Up contract failed ' + failures.length + ' of ' + checks + ' checks:\n- ' + failures.slice(0, 25).join('\n- '));
  process.exit(1);
}
console.log('Settle Up contract passed ' + checks + ' checks.');
