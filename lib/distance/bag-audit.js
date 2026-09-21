/* GolfRaw Bag Audit: dead wood, gaps and overlaps across a set of clubs.
 *
 * Lifted unchanged from the page so it can be tested in Node. It works in
 * yards only: carries come in as yards, gaps go out as yards, and the
 * thresholds (a gap over 20 yards is a hole, under 8 is two clubs doing one
 * job) are yards. A golfer who enters metres is converted at the page's edge
 * (/lib/distance/units.js), so 20 yards stays 20 yards (about 18.3 metres)
 * and never becomes "20 metres".
 */
(function (root) {
  'use strict';

  var DEAD_SCORE = 4;      /* uses x trust at or below this = passenger */
  var GAP_BIG = 20;        /* yards between clubs above this = gaping hole */
  var GAP_TIGHT = 8;       /* yards between clubs below this = redundancy */
  var LEGAL_LIMIT = 14;    /* Rule 4.1b: the putter counts as one of the fourteen */

  /* Order matters: wedges are tested before woods, because "SW" and "PW" both
     end in a w and would otherwise be classified as fairway woods. */
  function typeOf(name) {
    var n = String(name).toLowerCase().trim();
    if (/driver|^1\s*-?\s*wood$|^1w$/.test(n)) return 'driver';
    if (/wedge|^[pgasl]\s*-?\s*w$|\b(pw|gw|aw|sw|lw)\b/.test(n)) return 'wedge';
    if (/hybrid|rescue|^\d\s*-?\s*h$/.test(n)) return 'hybrid';
    if (/wood|^\d\s*-?\s*w$/.test(n)) return 'wood';
    if (/iron|^\d\s*-?\s*i$/.test(n)) return 'iron';
    return 'other';
  }

  // rows: [{ name, carry (yards), usage (null when blank), conf }]
  function analyse(rows) {
    var clubs = [], i;
    for (i = 0; i < rows.length; i++) {
      var r = rows[i];
      if (!r.name || !String(r.name).trim()) continue;
      if (!isFinite(r.carry) || r.carry <= 0) continue;
      clubs.push({
        name: String(r.name).trim(),
        carry: r.carry,
        usage: r.usage,            /* null when the field was left blank */
        conf: isFinite(r.conf) && r.conf >= 1 ? r.conf : 3,
        type: typeOf(r.name)
      });
    }
    if (clubs.length < 3) return null;

    /* dead wood: only judged where the golfer actually told us the usage */
    var unscored = 0;
    for (i = 0; i < clubs.length; i++) {
      var c = clubs[i];
      if (c.usage === null || !isFinite(c.usage)) {
        c.scored = false; c.score = null; c.never = false; c.dead = false;
        unscored++;
      } else {
        c.scored = true;
        c.score = c.usage * c.conf;
        c.never = c.usage === 0;
        c.dead = c.never || c.score <= DEAD_SCORE;
      }
    }

    var ladder = clubs.slice().sort(function (a, b) { return b.carry - a.carry; });

    var gaps = [];
    for (i = 0; i < ladder.length - 1; i++) {
      var d = ladder[i].carry - ladder[i + 1].carry;
      gaps.push({
        hi: ladder[i], lo: ladder[i + 1], yards: d,
        kind: d > GAP_BIG ? 'hole' : (d < GAP_TIGHT ? 'overlap' : 'ok')
      });
    }

    var holes = gaps.filter(function (g) { return g.kind === 'hole'; });
    var overlaps = gaps.filter(function (g) { return g.kind === 'overlap'; });
    var dead = clubs.filter(function (c) { return c.dead; })
      .sort(function (a, b) { return a.score - b.score; });

    return {
      clubs: clubs, ladder: ladder, gaps: gaps,
      dead: dead, overlaps: overlaps, holes: holes,
      n: clubs.length, unscored: unscored,
      problems: dead.length + overlaps.length + holes.length,
      illegal: clubs.length >= LEGAL_LIMIT,
      longest: ladder[0], shortest: ladder[ladder.length - 1],
      spread: ladder[0].carry - ladder[ladder.length - 1].carry
    };
  }

  var api = {
    version: 1,
    DEAD_SCORE: DEAD_SCORE, GAP_BIG: GAP_BIG, GAP_TIGHT: GAP_TIGHT, LEGAL_LIMIT: LEGAL_LIMIT,
    typeOf: typeOf,
    analyse: analyse
  };
  root.GolfrawBagAudit = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : this);
