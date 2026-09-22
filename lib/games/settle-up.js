/* GolfRaw Settle Up rules: skins, Nassau and closest to the pin.
 *
 * Needs /lib/games/settle-core.js first (window.GolfrawSettleCore): money is
 * whole minor units, strokes come from core.allocate, payments from
 * core.settle. Every rule the group can disagree about is an explicit input;
 * nothing is decided silently.
 *
 * SKINS. A hole's skin goes to the one player with the lowest score. Two or
 * more tied for low: nobody wins it ("two tie, all tie"). With carryovers on,
 * a tied skin moves to the next hole and the next outright winner takes
 * everything that has built up; with carryovers off, a tied skin is simply not
 * won. Every other player pays the winner the stake for each skin won. Skins
 * still carried after the last hole are either not won by anyone or go to the
 * winner of a playoff the group names. Optional: a skin won with a gross birdie
 * or better counts double (carried skins included).
 * Net skins: each player's strokes are their full playing handicap, or the
 * difference from the lowest in the group ("off the low"). The Rules of
 * Handicapping make no recommendation for skins, so the group picks.
 *
 * NASSAU. Match play (holes won, not total strokes). Three bets of the same
 * stake: front nine, back nine, all eighteen; a halved bet is a push. With
 * more than two players every pair plays its own Nassau. Net: in each pair the
 * higher playing handicap receives the difference, 100% (singles match play,
 * Rules of Handicapping Appendix C), placed across the 18 holes by stroke
 * index; each nine plays with the strokes that fall on it.
 * Presses: none; automatic (whenever the most recent bet on a nine or on the
 * 18 goes 2 down, the player who is down starts a new bet on the next hole
 * that runs to the end of that nine or the 18; presses can be pressed); or
 * entered by hand.
 *
 * CLOSEST TO THE PIN. On each par 3 in play, every other player pays the
 * winner the stake.
 */
(function (root) {
  'use strict';

  var C = root.GolfrawSettleCore || (typeof require === 'function' ? require('./settle-core.js') : null);

  var FRONT = [0, 1, 2, 3, 4, 5, 6, 7, 8];
  var BACK = [9, 10, 11, 12, 13, 14, 15, 16, 17];
  var ALL = FRONT.concat(BACK);
  var SEGMENTS = { front: FRONT, back: BACK, overall: ALL };
  var LIMITS = { players: [2, 6], hcp: [-10, 54], score: [1, 20], par: [3, 6] };
  var DEFAULT_PARS = [4, 4, 3, 5, 4, 4, 3, 4, 5, 4, 3, 4, 5, 4, 4, 3, 4, 5];
  // A common card pattern (odd indexes out, even home), only a starting point:
  // net games need the stroke index row from the course's own card.
  var DEFAULT_SI = [7, 11, 15, 1, 3, 13, 17, 9, 5, 8, 16, 2, 10, 4, 14, 18, 6, 12];

  function holesFor(round) { return round === 'front' ? FRONT : round === 'back' ? BACK : ALL; }
  function isInt(v) { return typeof v === 'number' && isFinite(v) && Math.floor(v) === v; }

  /* -------------------------------------------------------------- validation
     Returns [] or a list of { code, player?, hole?, index? }. Holes and
     players are 0-based here; the page words them for people. */
  function validate(g) {
    var errs = [];
    var P = g.players ? g.players.length : 0;
    if (P < LIMITS.players[0] || P > LIMITS.players[1]) return [{ code: 'players' }];
    var skins = g.skins && g.skins.on, nassau = g.nassau && g.nassau.on, ctp = g.ctp && g.ctp.on;
    if (!skins && !nassau) errs.push({ code: 'no_game' });
    if (nassau && g.round !== '18') errs.push({ code: 'nassau_needs_18' });
    if (skins && !(g.skins.stake > 0)) errs.push({ code: 'stake_skins' });
    if (nassau && !(g.nassau.stake > 0)) errs.push({ code: 'stake_nassau' });
    if (ctp && !(g.ctp.stake > 0)) errs.push({ code: 'stake_ctp' });

    var holes = holesFor(g.round);
    var net = g.scoring === 'net';
    if (net) {
      for (var p = 0; p < P; p++) {
        var h = g.players[p].hcp;
        if (!isInt(h) || h < LIMITS.hcp[0] || h > LIMITS.hcp[1]) errs.push({ code: 'hcp', player: p });
      }
      if (!C.validSI(g.si)) errs.push({ code: 'si' });
    }
    if ((skins && g.skins.birdieDouble) || ctp) {
      for (var k = 0; k < holes.length; k++) {
        var par = g.pars[holes[k]];
        if (!isInt(par) || par < LIMITS.par[0] || par > LIMITS.par[1]) { errs.push({ code: 'par', hole: holes[k] }); break; }
      }
    }
    for (var q = 0; q < P; q++) {
      for (var j = 0; j < holes.length; j++) {
        var s = g.scores[q] ? g.scores[q][holes[j]] : null;
        if (s === null || s === undefined || s === '') errs.push({ code: 'score_missing', player: q, hole: holes[j] });
        else if (!isInt(s) || s < LIMITS.score[0] || s > LIMITS.score[1]) errs.push({ code: 'score_range', player: q, hole: holes[j] });
      }
    }
    if (nassau && g.nassau.presses === 'manual') {
      (g.nassau.manual || []).forEach(function (m, i) {
        var seg = SEGMENTS[m.bet];
        var ok = seg && isInt(m.by) && isInt(m.against) && m.by !== m.against &&
          m.by >= 0 && m.by < P && m.against >= 0 && m.against < P &&
          isInt(m.from) && seg.indexOf(m.from) > 0;          // not on the bet's first hole
        if (!ok) errs.push({ code: 'press', index: i });
      });
    }
    if (ctp) {
      var w = g.ctp.winners || {};
      for (var key in w) {
        if (!Object.prototype.hasOwnProperty.call(w, key)) continue;
        var v = w[key];
        if (v !== null && v !== undefined && !(isInt(v) && v >= 0 && v < P)) errs.push({ code: 'ctp', hole: +key });
      }
    }
    return errs;
  }

  /* ------------------------------------------------------------------ skins */
  function playSkins(g, holes, bal) {
    var P = g.players.length, cfg = g.skins, stake = cfg.stake;
    var net = g.scoring === 'net';
    var strokes = [];
    var low = 0;
    if (net && cfg.strokes === 'low') {
      low = Math.min.apply(null, g.players.map(function (p) { return p.hcp; }));
    }
    for (var p = 0; p < P; p++) strokes.push(net ? C.allocate(g.players[p].hcp - low, holes, g.si) : {});

    var rows = [], count = new Array(P).fill(0), carry = 0;
    for (var i = 0; i < holes.length; i++) {
      var h = holes[i];
      var scores = [];
      for (var q = 0; q < P; q++) scores.push(g.scores[q][h] - (net ? strokes[q][h] : 0));
      var low2 = Math.min.apply(null, scores);
      var at = [];
      for (var r = 0; r < P; r++) if (scores[r] === low2) at.push(r);
      var row = { hole: h, scores: scores, low: low2 };
      if (at.length === 1) {
        var w = at[0];
        var skins = 1 + carry;
        var birdie = cfg.birdieDouble && g.scores[w][h] <= g.pars[h] - 1;
        if (birdie) skins *= 2;
        row.outcome = 'won'; row.winner = w; row.skins = skins; row.carried = carry; row.birdie = birdie;
        row.each = skins * stake;
        bal[w] += row.each * (P - 1);
        for (var o = 0; o < P; o++) if (o !== w) bal[o] -= row.each;
        count[w] += skins;
        carry = 0;
      } else {
        row.outcome = cfg.carry ? 'carried' : 'void';
        row.tied = at;
        if (cfg.carry) carry += 1;
      }
      rows.push(row);
    }
    var end = { carried: carry, rule: cfg.endCarry === 'playoff' ? 'playoff' : 'lost', winner: null, each: 0 };
    // A playoff winner only matters when skins are still carried; without a
    // valid one the page is asked for it rather than guessing.
    var pw = cfg.playoffWinner;
    if (carry && end.rule === 'playoff' && isInt(pw) && pw >= 0 && pw < P) {
      end.winner = pw;
      end.each = carry * stake;
      bal[end.winner] += end.each * (P - 1);
      for (var z = 0; z < P; z++) if (z !== end.winner) bal[z] -= end.each;
      count[end.winner] += carry;
    }
    return { holes: rows, strokes: strokes, low: low, count: count, end: end };
  }

  /* ----------------------------------------------------------------- nassau */
  function playPair(g, a, b, bal) {
    var cfg = g.nassau, stake = cfg.stake;
    var net = g.scoring === 'net';
    var give = { player: null, strokes: 0, onHole: {} };
    if (net) {
      var diff = g.players[a].hcp - g.players[b].hcp;
      if (diff) {
        give.player = diff > 0 ? a : b;
        give.strokes = Math.abs(diff);
        give.onHole = C.allocate(give.strokes, ALL, g.si);
      }
    }
    // +1 when a wins the hole, -1 when b does, 0 halved.
    var hole = {};
    ALL.forEach(function (h) {
      var sa = g.scores[a][h], sb = g.scores[b][h];
      if (give.player === a) sa -= give.onHole[h];
      if (give.player === b) sb -= give.onHole[h];
      hole[h] = sa < sb ? 1 : sa > sb ? -1 : 0;
    });

    var bets = [];
    ['front', 'back', 'overall'].forEach(function (seg) {
      var holes = SEGMENTS[seg];
      var list = [{ kind: 'main', seg: seg, from: holes[0], margin: 0, by: null }];
      if (cfg.presses === 'manual') {
        (cfg.manual || []).forEach(function (m) {
          var pair = (m.by === a && m.against === b) || (m.by === b && m.against === a);
          if (pair && m.bet === seg) list.push({ kind: 'press', seg: seg, from: m.from, margin: 0, by: m.by, auto: false });
        });
      }
      for (var i = 0; i < holes.length; i++) {
        var h = holes[i];
        for (var k = 0; k < list.length; k++) if (h >= list[k].from) list[k].margin += hole[h];
        if (cfg.presses === 'auto' && i < holes.length - 1) {
          var latest = list[list.length - 1];
          if (Math.abs(latest.margin) >= 2 && h >= latest.from) {
            list.push({ kind: 'press', seg: seg, from: holes[i + 1], margin: 0, by: latest.margin < 0 ? a : b, auto: true });
          }
        }
      }
      list.forEach(function (bet) {
        bet.to = holes[holes.length - 1];
        bet.winner = bet.margin > 0 ? a : bet.margin < 0 ? b : null;
        bet.amount = bet.winner === null ? 0 : stake;
        if (bet.winner !== null) {
          bal[bet.winner] += stake;
          bal[bet.winner === a ? b : a] -= stake;
        }
        bets.push(bet);
      });
    });
    return { a: a, b: b, give: { player: give.player, strokes: give.strokes }, bets: bets };
  }

  /* ------------------------------------------------------------------- run */
  function compute(g) {
    var errs = validate(g);
    var P = g.players ? g.players.length : 0;
    if (errs.length) return { ok: false, errors: errs };

    var holes = holesFor(g.round);
    var zero = function () { return new Array(P).fill(0); };
    var parts = { skins: zero(), nassau: zero(), ctp: zero() };
    var out = { ok: true, holes: holes, parts: parts };

    if (g.skins && g.skins.on) {
      out.skins = playSkins(g, holes, parts.skins);
      if (out.skins.end.carried && out.skins.end.rule === 'playoff' && out.skins.end.winner === null) {
        return { ok: false, errors: [{ code: 'playoff_winner', carried: out.skins.end.carried }] };
      }
    }
    if (g.nassau && g.nassau.on) {
      out.nassau = [];
      for (var a = 0; a < P; a++) for (var b = a + 1; b < P; b++) out.nassau.push(playPair(g, a, b, parts.nassau));
    }
    if (g.ctp && g.ctp.on) {
      out.ctp = [];
      holes.forEach(function (h) {
        if (g.pars[h] !== 3) return;
        var w = g.ctp.winners ? g.ctp.winners[h] : null;
        var row = { hole: h, winner: isInt(w) ? w : null, each: 0 };
        if (row.winner !== null) {
          row.each = g.ctp.stake;
          parts.ctp[row.winner] += g.ctp.stake * (P - 1);
          for (var o = 0; o < P; o++) if (o !== row.winner) parts.ctp[o] -= g.ctp.stake;
        }
        out.ctp.push(row);
      });
    }
    out.balances = zero().map(function (_, i) { return parts.skins[i] + parts.nassau[i] + parts.ctp[i]; });
    out.transfers = C.settle(out.balances);
    return out;
  }

  var api = {
    version: 1,
    FRONT: FRONT, BACK: BACK, ALL: ALL, LIMITS: LIMITS,
    DEFAULT_PARS: DEFAULT_PARS, DEFAULT_SI: DEFAULT_SI,
    holesFor: holesFor,
    validate: validate,
    compute: compute
  };
  root.GolfrawSettleUp = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : this);
