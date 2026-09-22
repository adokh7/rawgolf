/* GolfRaw Settle Up core: money, handicap strokes and settlement.
 *
 * Money is whole minor units (cents, or hundredths of a point) from the moment
 * it is typed to the moment it is shown, so every balance is exact and every
 * settlement sums to zero. Nothing here knows about currencies: the symbol is
 * presentation only.
 *
 * Strokes follow the Rules of Handicapping: a player receives strokes on the
 * holes with the lowest stroke index first (one per hole, then a second round
 * from stroke index 1 again), and a plus handicap gives strokes back starting
 * on the highest stroke index. On a nine-hole round the nine holes are ranked
 * by their 18-hole stroke index and the same rule is applied to the ranks.
 */
(function (root) {
  'use strict';

  var MAX_MINOR = 1000000;               // 10,000.00 per stake is plenty

  /* "2", "2.5", "2.50", "0.25" -> 200, 250, 250, 25. Anything else -> null. */
  function toMinor(text) {
    var s = String(text == null ? '' : text).replace(/^\s+|\s+$/g, '').replace(',', '.');
    if (!/^\d{1,6}(\.\d{0,2})?$/.test(s)) return null;
    var parts = s.split('.');
    var minor = parseInt(parts[0], 10) * 100 + (parts[1] ? parseInt((parts[1] + '0').slice(0, 2), 10) : 0);
    return minor > MAX_MINOR ? null : minor;
  }

  function fromMinor(minor) { return minor / 100; }

  /* "$6", "€6.50", "£12", "6 pts". Never "-0". */
  function format(minor, symbol) {
    var abs = Math.abs(minor);
    var whole = Math.floor(abs / 100), cents = abs % 100;
    var n = String(whole).replace(/\B(?=(\d{3})+(?!\d))/g, ',') + (cents ? '.' + (cents < 10 ? '0' : '') + cents : '');
    if (symbol === 'pts') return n + (abs === 100 ? ' pt' : ' pts');
    return (symbol || '') + n;
  }

  /* Strokes received on each hole in play. `holes` are 0-based hole indexes,
     `si` the 18-hole stroke index card (1..18), `strokes` a whole number
     (negative for a plus handicap). */
  function allocate(strokes, holes, si) {
    var n = holes.length;
    var order = holes.slice().sort(function (a, b) { return si[a] - si[b]; });
    var rank = {};
    for (var i = 0; i < n; i++) rank[order[i]] = i + 1;     // 1 = hardest hole in play
    var out = {};
    for (var k = 0; k < n; k++) {
      var h = holes[k], r = rank[h];
      if (strokes >= 0) {
        out[h] = Math.floor(strokes / n) + (r <= strokes % n ? 1 : 0);
      } else {
        var back = -strokes;
        out[h] = -(Math.floor(back / n) + (r > n - (back % n) ? 1 : 0));
      }
    }
    return out;
  }

  /* A stroke index card must use each of 1..18 exactly once. */
  function validSI(si) {
    if (!si || si.length !== 18) return false;
    var seen = {};
    for (var i = 0; i < 18; i++) {
      var v = si[i];
      if (v !== Math.floor(v) || v < 1 || v > 18 || seen[v]) return false;
      seen[v] = true;
    }
    return true;
  }

  /* ---------------------------------------------------------------- settlement
     Fewest possible payments. The group is split into the largest number of
     sub-groups whose balances already sum to zero (each needs one payment
     fewer than it has members); inside each sub-group the largest debtor pays
     the largest creditor until everyone is square. Nobody both pays and
     receives, nobody pays themselves, and every amount is a whole minor unit. */
  function settle(balances) {
    var idx = [];
    for (var i = 0; i < balances.length; i++) if (balances[i] !== 0) idx.push(i);
    var n = idx.length;
    if (!n) return [];
    var sums = [];
    for (var m = 0; m < (1 << n); m++) {
      var s = 0;
      for (var b = 0; b < n; b++) if (m & (1 << b)) s += balances[idx[b]];
      sums.push(s);
    }
    var best = null;
    function popcount(x) { var c = 0; while (x) { c += x & 1; x >>= 1; } return c; }
    function rec(remaining, groups) {
      if (!remaining) {
        if (!best || groups.length > best.length) best = groups.slice();
        return;
      }
      // Every group has at least two members.
      if (best && groups.length + Math.floor(popcount(remaining) / 2) <= best.length) return;
      var first = remaining & -remaining, rest = remaining ^ first;
      for (var sub = rest; ; sub = (sub - 1) & rest) {
        var g = sub | first;
        if (sums[g] === 0) { groups.push(g); rec(remaining ^ g, groups); groups.pop(); }
        if (!sub) break;
      }
    }
    rec((1 << n) - 1, []);

    var out = [];
    for (var gi = 0; gi < best.length; gi++) {
      var cred = [], debt = [];
      for (var k = 0; k < n; k++) {
        if (!(best[gi] & (1 << k))) continue;
        var p = idx[k], v = balances[p];
        if (v > 0) cred.push({ p: p, v: v }); else debt.push({ p: p, v: -v });
      }
      var byAmount = function (x, y) { return y.v - x.v || x.p - y.p; };
      while (cred.length && debt.length) {
        cred.sort(byAmount); debt.sort(byAmount);
        var amt = Math.min(cred[0].v, debt[0].v);
        out.push({ from: debt[0].p, to: cred[0].p, amount: amt });
        cred[0].v -= amt; debt[0].v -= amt;
        if (!cred[0].v) cred.shift();
        if (!debt[0].v) debt.shift();
      }
    }
    out.sort(function (x, y) { return y.amount - x.amount || x.from - y.from || x.to - y.to; });
    return out;
  }

  var api = {
    version: 1,
    MAX_MINOR: MAX_MINOR,
    toMinor: toMinor, fromMinor: fromMinor, format: format,
    allocate: allocate, validSI: validSI,
    settle: settle
  };
  root.GolfrawSettleCore = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : this);
