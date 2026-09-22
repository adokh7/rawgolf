/* GolfRaw Round Card: what one finished round says, from the card alone.
 *
 * Input is what a golfer can write down after the round without having
 * tracked a single shot: par and score for every hole, and, if they have them,
 * putts and penalty strokes. Greens in regulation are not asked for: a green
 * is hit in regulation when the ball is on it with two strokes to spare
 * against par, so score minus putts says whether it was (putts count only on
 * the green, as on every stats sheet).
 *
 * Everything here is arithmetic on that card. Nothing is benchmarked against
 * a handicap and nothing is called strokes gained, because the card cannot
 * support either. A finding is shown only when the numbers it quotes are on
 * the card, and each says how complete the data behind it is.
 *
 * The card is the Locker's scorecard record (lib/locker/store.js), so rounds
 * saved here and in the Tendency Engine are one history. Schema v2 is
 * documented in scripts/README.md, "The Round Card".
 */
(function (root) {
  'use strict';

  var SCHEMA_VERSION = 2;
  var LIMITS = { par: [3, 6], score: [1, 15], putts: [0, 6], pen: [0, 6] };
  /* The Tendency Engine's par 72: par 3s on 3, 7, 12, 16; par 5s on 4, 9, 13, 18. */
  var PARS_18 = [4, 4, 3, 5, 4, 4, 3, 4, 5, 4, 4, 3, 5, 4, 4, 3, 4, 5];
  var PARS_9 = PARS_18.slice(0, 9);
  var STRONG = 0.9;    // share of holes a stat must cover to be a strong signal
  var SOME = 0.6;      // below this a stat is not used at all
  var CONF = { strong: 'Strong signal', some: 'Some evidence', none: 'Not enough data' };

  function isInt(v) { return typeof v === 'number' && isFinite(v) && Math.floor(v) === v; }
  function known(v) { return v !== null && v !== undefined; }
  function inRange(v, r) { return isInt(v) && v >= r[0] && v <= r[1]; }

  function median(list) {
    var a = list.slice().sort(function (x, y) { return x - y; });
    var m = Math.floor(a.length / 2);
    return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2;
  }

  /* ------------------------------------------------------------ words ---- */
  var WORDS = ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
    'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen'];
  function word(n) { return n >= 0 && n < WORDS.length ? WORDS[n] : String(n); }
  function cap(s) { return s.charAt(0).toUpperCase() + s.slice(1); }
  function plural(n, one, many) { return n === 1 ? one : (many || one + 's'); }
  function toParText(n) { return n === 0 ? 'E' : (n > 0 ? '+' + n : '−' + (-n)); }
  /* "3 over par", "2 under par", "level par". */
  function againstPar(n) { return n === 0 ? 'level par' : (n > 0 ? n + ' over par' : (-n) + ' under par'); }
  function avg1(n) { return (Math.round(n * 10) / 10).toFixed(1); }

  function holeName(d) {
    if (d <= -3) return 'albatross';
    if (d === -2) return 'eagle';
    if (d === -1) return 'birdie';
    if (d === 0) return 'par';
    if (d === 1) return 'bogey';
    if (d === 2) return 'double bogey';
    if (d === 3) return 'triple bogey';
    if (d === 4) return 'quadruple bogey';
    return d + ' over par';
  }
  /* "bogeys", "double bogeys", "pars"; "5 over par" has no plural. */
  function holeNamePlural(d) {
    if (d >= 5) return holeName(d);
    return holeName(d) + (d <= -3 ? 'es' : 's');
  }

  /* ---------------------------------------------------------- the card --- */
  function blankCard(holes) {
    var pars = holes === 9 ? PARS_9 : PARS_18, out = [];
    for (var i = 0; i < pars.length; i++) out.push({ par: pars[i], score: null, putts: null, pen: null, fir: null, app: null });
    return { v: SCHEMA_VERSION, holes: out };
  }

  /* A green hit in regulation: on the putting surface with two strokes to
     spare, so strokes before the first putt <= par - 2. Penalty strokes count
     as strokes. A hole with no putt was holed from off the green, where the
     card cannot say whether the green was hit, so it is unknown, as it is
     with no putts on record; a Tendency Engine card's approach result fills
     in when there is one. TheGrint and SwingU derive GIR the same way. */
  function greenHit(h) {
    if (known(h.putts) && h.putts >= 1) return h.score - h.putts <= h.par - 2;
    if (h.app) return h.app === 'hit';
    return null;
  }

  /* Where the approach finished, for the Locker record: 'hit' or 'miss' from
     the card, keeping a Tendency Engine miss direction when it still agrees. */
  function approachFor(h) {
    var g = greenHit(h);
    if (g === null) return h.app || null;
    if (g) return 'hit';
    return h.app && h.app !== 'hit' ? h.app : 'miss';
  }

  /* Every problem, each naming its hole and its box. */
  function validate(card) {
    var errors = [];
    var holes = card && card.holes;
    if (!holes || (holes.length !== 9 && holes.length !== 18)) {
      return { ok: false, errors: [{ code: 'holes' }] };
    }
    for (var i = 0; i < holes.length; i++) {
      var h = holes[i], n = i + 1;
      if (!inRange(h.par, LIMITS.par)) errors.push({ code: 'par', hole: n });
      if (!known(h.score)) { errors.push({ code: 'score_missing', hole: n }); continue; }
      if (!inRange(h.score, LIMITS.score)) { errors.push({ code: 'score_range', hole: n }); continue; }
      if (known(h.putts) && !inRange(h.putts, LIMITS.putts)) errors.push({ code: 'putts_range', hole: n });
      if (known(h.pen) && !inRange(h.pen, LIMITS.pen)) errors.push({ code: 'pen_range', hole: n });
      /* At least one stroke on every hole is neither a putt nor a penalty:
         the tee shot. */
      if (inRange(h.putts, LIMITS.putts) || inRange(h.pen, LIMITS.pen)) {
        var p = known(h.putts) ? h.putts : 0, q = known(h.pen) ? h.pen : 0;
        if (p + q > h.score - 1) errors.push({ code: 'too_many', hole: n, putts: p, pen: q, score: h.score });
      }
    }
    return { ok: errors.length === 0, errors: errors };
  }

  function isValidRound(card) { return validate(card).ok; }

  /* ---------------------------------------------------------- analysis --- */
  function coverage(count, of) {
    var share = of ? count / of : 0;
    return { count: count, of: of, share: share, level: share >= STRONG ? 'strong' : share >= SOME ? 'some' : 'none' };
  }

  /* Shots taken to reach the green beyond regulation, not counting penalty
     strokes. One is a normal missed green; two or more is a chip that stayed
     off, a recovery from trouble, or a duff. Needs putts and penalties. */
  function extraToGreen(r) {
    if (r.putts === null || r.putts < 1 || r.pen === null) return null;
    return (r.score - r.putts - r.pen) - (r.par - 2);
  }

  function analyse(card) {
    var v = validate(card);
    if (!v.ok) return { ok: false, errors: v.errors };
    var H = card.holes, n = H.length, i;
    var a = { ok: true, holes: n, gross: 0, par: 0, toPar: 0, rows: [] };

    for (i = 0; i < n; i++) {
      var h = H[i];
      var row = { hole: i + 1, par: h.par, score: h.score, d: h.score - h.par,
        putts: known(h.putts) ? h.putts : null, pen: known(h.pen) ? h.pen : null, gir: greenHit(h) };
      row.extra = extraToGreen(row);
      a.gross += h.score; a.par += h.par;
      a.rows.push(row);
    }
    a.toPar = a.gross - a.par;
    var R = a.rows;

    if (n === 18) { a.front = nine(R.slice(0, 9)); a.back = nine(R.slice(9)); }

    /* Scoring mix, and every stroke over par before birdies give any back. */
    a.mix = { under: 0, par: 0, bogey: 0, double: 0, worse: 0 };
    a.overShots = 0;
    for (i = 0; i < n; i++) {
      var dd = R[i].d;
      if (dd < 0) a.mix.under++; else if (dd === 0) a.mix.par++; else if (dd === 1) a.mix.bogey++;
      else if (dd === 2) a.mix.double++; else a.mix.worse++;
      if (dd > 0) a.overShots += dd;
    }

    /* By par type: 3s, 4s, 5s (and 6s, rarely). */
    a.byPar = [];
    [3, 4, 5, 6].forEach(function (p) {
      var rows = R.filter(function (r) { return r.par === p; });
      if (rows.length) a.byPar.push({ par: p, holes: rows.length, toPar: sum(rows, 'd') });
    });

    /* Blow-ups: double bogey or worse, the usual meaning. When double bogey is
       the golfer's typical hole that day, only holes worse than typical count,
       so a card full of doubles is not one long list of blow-ups. Typical is
       the median hole against par, rounded down. */
    a.typical = Math.floor(median(R.map(function (r) { return r.d; })));
    a.threshold = Math.max(2, a.typical + 1);
    a.blowups = R.filter(function (r) { return r.d >= a.threshold; });
    a.blowupToPar = sum(a.blowups, 'd');
    /* The same holes played as a bogey (or as the typical hole, when that is
       worse than bogey). */
    a.fallback = Math.max(1, a.typical);
    a.blowupExtra = 0;
    a.blowups.forEach(function (r) {
      a.blowupExtra += r.d - a.fallback;
      r.causes = causesOf(r);
    });
    a.withoutBlowups = a.gross - a.blowupExtra;

    /* Optional stats, used only where they were entered. */
    var puttRows = R.filter(function (r) { return r.putts !== null; });
    var penRows = R.filter(function (r) { return r.pen !== null; });
    var girRows = R.filter(function (r) { return r.gir !== null; });
    var reachRows = R.filter(function (r) { return r.extra !== null; });
    a.coverage = { putts: coverage(puttRows.length, n), pen: coverage(penRows.length, n),
      gir: coverage(girRows.length, n), reach: coverage(reachRows.length, n) };

    a.putts = a.coverage.putts.level === 'none' ? null : (function () {
      var three = puttRows.filter(function (r) { return r.putts >= 3; });
      var tax = 0;
      three.forEach(function (r) { tax += r.putts - 2; });
      return { total: sum(puttRows, 'putts'), holes: puttRows.length, three: three.length, threeTax: tax,
        four: three.some(function (r) { return r.putts >= 4; }),
        one: puttRows.filter(function (r) { return r.putts === 1; }).length };
    })();
    a.pen = a.coverage.pen.level === 'none' ? null : (function () {
      var hit = penRows.filter(function (r) { return r.pen > 0; });
      var rest = penRows.filter(function (r) { return r.pen === 0; });
      return { strokes: sum(penRows, 'pen'), holes: hit.length, recorded: penRows.length,
        onHoles: sum(hit, 'd'), onRest: sum(rest, 'd'), restHoles: rest.length,
        list: hit.map(function (r) { return r.hole; }) };
    })();
    a.gir = a.coverage.gir.level === 'none' ? null : (function () {
      var hit = girRows.filter(function (r) { return r.gir; });
      var miss = girRows.filter(function (r) { return !r.gir; });
      return { hit: hit.length, of: girRows.length, missed: miss.length, onHit: sum(hit, 'd'), onMissed: sum(miss, 'd') };
    })();
    a.reach = a.coverage.reach.level === 'none' ? null : (function () {
      var slow = reachRows.filter(function (r) { return r.extra >= 2; });
      var tax = 0;
      slow.forEach(function (r) { tax += r.extra - 1; });
      return { holes: slow.length, tax: tax, list: slow.map(function (r) { return r.hole; }) };
    })();
    a.detail = (a.coverage.putts.level !== 'none' || a.coverage.pen.level !== 'none') ? 'detailed' : 'quick';

    a.headline = headline(a);
    a.findings = findings(a);
    a.focus = focus(a);
    /* With no focus, say why rather than guess. */
    a.noFocus = a.focus ? null : (a.detail === 'quick'
      ? 'Not enough detail to identify a clear practice priority. Add putts and penalties and the card can say more.'
      : 'Nothing on this card points to one clear practice priority.');
    a.dataNote = dataNote(a);
    return a;
  }

  /* What a blow-up had in it, from the optional stats. Empty when they were
     not entered: the card then shows the number, not a guess at the cause. */
  function causesOf(r) {
    var out = [];
    if (r.pen !== null && r.pen > 0) out.push('penalty');
    if (r.putts !== null && r.putts >= 3) out.push('three_putt');
    if (r.extra !== null && r.extra >= 2) out.push('extra_to_green');
    return out;
  }
  var CAUSE_WORDS = { penalty: 'a penalty', three_putt: 'three putts or more', extra_to_green: 'two or more extra shots to reach the green' };
  function causeText(r) {
    if (!r.causes || !r.causes.length) return '';
    var w = r.causes.map(function (c) { return CAUSE_WORDS[c]; });
    return w.length === 1 ? w[0] : w.slice(0, -1).join(', ') + ' and ' + w[w.length - 1];
  }

  function nine(rows) {
    var g = sum(rows, 'score'), p = sum(rows, 'par');
    return { gross: g, par: p, toPar: g - p };
  }
  function sum(rows, key) { var t = 0; for (var i = 0; i < rows.length; i++) t += rows[i][key]; return t; }
  function listHoles(list) {
    return list.length === 1 ? 'hole ' + list[0] : 'holes ' + list.slice(0, -1).join(', ') + ' and ' + list[list.length - 1];
  }

  /* ---------------------------------------------------------- the words -- */
  function blowupRule(a) {
    if (a.threshold === 2) return 'A blow-up here is a double bogey or worse.';
    return 'Your typical hole today was a ' + holeName(a.typical) + ', so a blow-up here is a ' +
      holeName(a.threshold) + ' or worse.';
  }

  function headline(a) {
    var B = a.blowups, nB = B.length, T = a.toPar, S = a.blowupToPar;
    if (!nB) {
      if (a.overShots === 0) return 'No blow-ups and not a single hole over par.';
      var over = a.rows.filter(function (r) { return r.d > 0; }).length;
      if (over === 1) return 'No blow-ups. One hole went over par, a ' + holeName(maxD(a.rows)) +
        ', and you finished ' + againstPar(T) + '.';
      return 'No blow-ups. ' + cap(word(over)) + ' holes went over par, none worse than a ' +
        holeName(maxD(a.rows)) + ', and you finished ' + againstPar(T) + '.';
    }
    var who = cap(word(nB)) + ' ' + plural(nB, 'hole');
    if (T > 0 && S <= T) {
      if (S === T) return who + ' cost you all ' + T + ' of your shots over par.';
      /* Blow-ups happened but most of the round's damage was elsewhere. */
      if (T >= 4 && S < 0.5 * T) return 'Blow-ups were not the story: ' + word(nB) + ' ' + plural(nB, 'hole') +
        ' cost you ' + S + ' of your ' + T + ' shots over par.';
      return who + ' cost you ' + S + ' of your ' + T + ' shots over par.';
    }
    /* Birdies elsewhere paid some of it back. */
    return who + ' went ' + toParText(S) + '. The other ' + (a.holes - nB) + ' were ' + againstPar(T - S) + '.';
  }
  function maxD(rows) { var m = -9; for (var i = 0; i < rows.length; i++) if (rows[i].d > m) m = rows[i].d; return m; }

  /* At most three, most specific first, none that contradict another. Each
     quotes only numbers on the card, and none compares the golfer with a
     handicap benchmark: the published ones disagree too much to be used. */
  function findings(a) {
    var out = [];
    var big = a.holes === 18;

    if (a.pen && a.pen.strokes >= 2) {
      var P = a.pen, nB = a.blowups.length;
      var withPen = a.blowups.filter(function (r) { return r.pen !== null && r.pen > 0; }).length;
      var t = 'Penalties added ' + word(P.strokes) + ' strokes. ';
      if (withPen && nB === 1) t += 'Your blow-up on hole ' + a.blowups[0].hole + ' had one.';
      else if (withPen) t += (withPen === nB ? 'All ' + word(nB) : cap(word(withPen)) + ' of your ' + word(nB)) + ' blow-ups had one.';
      else if (P.holes === 1) t += 'All of them came on hole ' + P.list[0] + '.';
      else if (P.restHoles >= 3) t += 'The ' + word(P.holes) + ' holes with a penalty averaged ' + avg1(P.onHoles / P.holes) +
        ' over par; the rest averaged ' + avg1(P.onRest / P.restHoles) + '.';
      else t += 'They came on ' + listHoles(P.list) + '.';
      out.push({ id: 'penalties', confidence: CONF[a.coverage.pen.level], text: t });
    }

    if (a.putts && a.putts.three >= (big ? 3 : 2)) {
      out.push({ id: 'three_putts', confidence: CONF[a.coverage.putts.level],
        text: cap(word(a.putts.three)) + (a.putts.four ? ' holes with three putts or more' : ' three-putts') +
          ' cost you ' + word(a.putts.threeTax) + ' ' + plural(a.putts.threeTax, 'stroke') + ' over two-putting.' });
    }

    if (a.reach && a.reach.holes >= 2) {
      out.push({ id: 'extra_to_green', confidence: CONF[a.coverage.reach.level],
        text: cap(word(a.reach.holes)) + ' holes took two or more extra shots just to reach the green (' +
          a.reach.list.join(', ') + ').' });
    } else if (approachStory(a)) {
      out.push({ id: 'missed_greens', confidence: CONF[a.coverage.gir.level],
        text: a.gir.hit === 0
          ? 'No greens in regulation, so the damage came before the green: ' + toParText(a.gir.onMissed) + ' across ' +
            word(a.gir.missed) + ' holes.'
          : 'The damage came before the green: ' + toParText(a.gir.onMissed) + ' on the ' + word(a.gir.missed) +
            ' greens you missed, ' + toParText(a.gir.onHit) + ' on the ' + word(a.gir.hit) + ' you hit.' });
    }

    var pt = parTypeLeak(a);
    if (pt) out.push(pt);

    if (a.front && Math.abs(a.front.toPar - a.back.toPar) >= 3) {
      var back = a.back.toPar < a.front.toPar, diff = Math.abs(a.front.toPar - a.back.toPar);
      out.push({ id: 'nines', confidence: CONF.strong,
        text: 'Your ' + (back ? 'back' : 'front') + ' nine was ' + diff + ' shots better than your ' +
          (back ? 'front' : 'back') + ' (' + toParText(a.front.toPar) + ' out, ' + toParText(a.back.toPar) + ' in).' });
    }
    return out.slice(0, 3);
  }

  /* One par type played clearly worse than the rest: at least 3 of them (2 on
     nine holes), at least 3 over between them, and 0.75 a hole worse than
     every other hole on the card. */
  function parTypeLeak(a) {
    var worst = null;
    a.byPar.forEach(function (g) {
      var restHoles = a.holes - g.holes;
      if (g.holes < (a.holes === 18 ? 3 : 2) || restHoles < 3 || g.toPar < 3) return;
      var gap = g.toPar / g.holes - (a.toPar - g.toPar) / restHoles;
      if (gap >= 0.75 && (!worst || gap > worst.gap)) worst = { g: g, gap: gap, rest: (a.toPar - g.toPar) / restHoles };
    });
    if (!worst) return null;
    var g = worst.g;
    return { id: 'par_type', confidence: CONF.strong,
      text: 'The par ' + g.par + 's cost you most: ' + toParText(g.toPar) + ' across ' + word(g.holes) + ' of them, ' +
        avg1(g.toPar / g.holes) + ' a hole against ' + avg1(worst.rest) + ' everywhere else.' };
  }

  /* Most of the over-par strokes came on greens missed, while putting and
     penalties explain little. Only then is "before the green" the story. */
  function approachStory(a) {
    if (!a.gir || a.gir.missed < 3) return false;
    if (a.pen && a.pen.strokes > 1) return false;
    if (a.putts && a.putts.three > 1) return false;
    if (a.overShots < 4 || a.gir.onMissed <= 0) return false;
    return a.gir.onMissed >= 0.75 * (a.gir.onMissed + Math.max(0, a.gir.onHit));
  }

  /* One next-round or practice focus, only when the card points at one. The
     three things a card can price are penalty strokes, putts beyond two, and
     shots beyond one to reach a missed green: the documented routes to a
     double bogey. The biggest wins if it is worth at least 3 strokes (2 on
     nine holes) and is not tied. */
  var FOCUS_TEXT = {
    penalties: function (x) {
      return 'Next round: keep the ball in play. Penalties cost you ' + word(x) + ' strokes; when there is trouble, ' +
        'take the club that takes it out of play, even if it leaves a longer shot in.';
    },
    putting: function (x, a) {
      return 'Practice: lag putting, getting long first putts close enough to hole the next one. ' +
        cap(word(a.putts.three)) + ' three-putts cost you ' + word(x) + ' strokes today.';
    },
    short_game: function (x, a) {
      return 'Next round: one shot onto the green. On ' + word(a.reach.holes) + ' holes it took two or more extra ' +
        'shots to get there; from close in, play the shot that finds the putting surface, even if it leaves a long putt.';
    }
  };
  function focus(a) {
    var taxes = [];
    if (a.pen) taxes.push({ id: 'penalties', tax: a.pen.strokes, level: a.coverage.pen.level });
    if (a.putts) taxes.push({ id: 'putting', tax: a.putts.threeTax, level: a.coverage.putts.level });
    if (a.reach) taxes.push({ id: 'short_game', tax: a.reach.tax, level: a.coverage.reach.level });
    taxes.sort(function (x, y) { return y.tax - x.tax; });   // stable: penalties, putting, short game on a tie
    var min = a.holes === 18 ? 3 : 2;
    if (taxes.length && taxes[0].tax >= min && (taxes.length === 1 || taxes[0].tax > taxes[1].tax)) {
      var top = taxes[0];
      var clear = taxes.length === 1 || top.tax >= taxes[1].tax + 2;
      return { id: top.id, strokes: top.tax, confidence: top.level === 'strong' && clear ? CONF.strong : CONF.some,
        text: FOCUS_TEXT[top.id](top.tax, a) };
    }
    if (approachStory(a)) {
      return { id: 'approach', confidence: CONF.some,
        text: 'Practice: approach shots. Most of today’s damage came on holes where you missed the green, ' +
          'not on the greens themselves.' };
    }
    /* The blow-ups are certain; what caused them is not on the card, so this
       is never more than some evidence. */
    if (a.blowups.length && a.toPar >= 5 && a.blowupToPar >= 0.5 * a.toPar) {
      return { id: 'damage_control', confidence: CONF.some,
        text: 'Next round: damage control. When a hole starts going wrong, take the safe way back into play and ' +
          'settle for a ' + holeName(a.fallback) + '.' +
          (a.detail === 'quick' ? ' Add putts and penalties next time to see what caused the big numbers.' : '') };
    }
    return null;
  }

  function dataNote(a) {
    var c = a.coverage;
    if (a.detail === 'quick') return 'Score only: this shows where the shots went, not why. Putts and penalties would show the why.';
    var parts = [];
    if (c.putts.level !== 'none') parts.push('putts on ' + c.putts.count + ' of ' + a.holes);
    if (c.pen.level !== 'none') parts.push('penalties on ' + c.pen.count + ' of ' + a.holes);
    var weak = c.putts.level === 'some' || c.pen.level === 'some';
    return cap(parts.join(', ')) + ' holes.' + (weak ? ' Anything built on the gaps is marked as some evidence.' : '');
  }

  /* ---------------------------------------------------------- summary ---- */
  /* The small derived record saved beside the holes. Always recomputed from
     them on save and never trusted over them. */
  function summary(card) {
    var a = analyse(card);
    if (!a.ok) return null;
    return {
      holes: a.holes, gross: a.gross, par: a.par, toPar: a.toPar,
      blowups: a.blowups.length, blowupToPar: a.blowupToPar,
      putts: a.putts && a.coverage.putts.level === 'strong' ? a.putts.total : null,
      pen: a.pen && a.coverage.pen.level === 'strong' ? a.pen.strokes : null,
      gir: a.gir && a.coverage.gir.level === 'strong' ? a.gir.hit : null,
      detail: a.detail
    };
  }

  /* Plain text for the group chat: the story, never the hole-by-hole card,
     and the course only when the golfer ticks it. */
  function shareText(a, opts) {
    opts = opts || {};
    var lines = ['GolfRaw Round Card'];
    if (opts.course) lines.push(opts.course);
    lines.push(a.gross + ' (' + toParText(a.toPar) + ')' + (a.holes === 9 ? ' over 9 holes' : ''));
    lines.push(a.headline);
    if (a.pen && a.coverage.pen.level === 'strong') lines.push('Penalty strokes: ' + a.pen.strokes);
    if (a.putts && a.coverage.putts.level === 'strong') lines.push('Putts: ' + a.putts.total + (a.putts.three ? ', ' + a.putts.three + ' three-putts' : ''));
    for (var i = 0; i < a.findings.length; i++) if (a.findings[i].id === 'nines') lines.push(a.findings[i].text);
    /* Native share passes the link separately, so it can leave it off. */
    if (opts.link !== false) lines.push('', 'golfraw.com/tools-scorecard-analyzer');
    return lines.join('\n');
  }

  /* ---------------------------------------------------------- history ---- */
  function habit(cards) {
    var valid = (cards || []).filter(isValidRound);
    var dates = valid.map(function (c) { return c.playedAt || 0; }).sort(function (x, y) { return x - y; });
    var logged = valid.map(function (c) { return c.createdAt || c.updatedAt || c.playedAt || 0; }).filter(Boolean);
    return { validRounds: valid.length, dates: dates, firstLoggedAt: logged.length ? Math.min.apply(null, logged) : null };
  }

  /* ---------------------------------------------------- export / import -- */
  var EXPORT_FORMAT = 'golfraw.rounds';
  var EXPORT_VERSION = 1;
  var ROUND_KEYS = ['id', 'v', 'course', 'playedAt', 'createdAt', 'updatedAt', 'holes', 'summary'];
  var HOLE_KEYS = ['par', 'score', 'putts', 'pen', 'fir', 'app'];

  function exportRounds(cards, now) {
    return JSON.stringify({ format: EXPORT_FORMAT, version: EXPORT_VERSION, exportedAt: now || Date.now(),
      rounds: (cards || []).map(pick) }, null, 2);
  }
  function pick(c) {
    var o = {};
    ROUND_KEYS.forEach(function (k) { if (known(c[k])) o[k] = c[k]; });
    o.holes = (c.holes || []).map(function (h) {
      var x = {};
      HOLE_KEYS.forEach(function (k) { x[k] = known(h[k]) ? h[k] : null; });
      return x;
    });
    return o;
  }

  var FIR = { hit: 1, left: 1, right: 1 };
  var APP = { hit: 1, miss: 1, short: 1, long: 1, left: 1, right: 1 };
  function cleanRound(r) {
    if (!r || typeof r !== 'object' || !Array.isArray(r.holes)) return null;
    if (typeof r.id !== 'string' || !r.id || r.id.length > 64) return null;
    var holes = [];
    for (var i = 0; i < r.holes.length; i++) {
      var h = r.holes[i] || {};
      holes.push({ par: h.par, score: known(h.score) ? h.score : null, putts: known(h.putts) ? h.putts : null,
        pen: known(h.pen) ? h.pen : null, fir: FIR[h.fir] ? h.fir : null, app: APP[h.app] ? h.app : null });
    }
    var card = { id: r.id, v: isInt(r.v) ? r.v : 1, course: typeof r.course === 'string' ? r.course.slice(0, 80) : '',
      playedAt: isInt(r.playedAt) && r.playedAt >= 0 ? r.playedAt : 0,
      createdAt: isInt(r.createdAt) && r.createdAt >= 0 ? r.createdAt : 0,
      updatedAt: isInt(r.updatedAt) && r.updatedAt >= 0 ? r.updatedAt : 0, holes: holes };
    return isValidRound(card) ? card : null;
  }

  /* Reads this tool's export, or a whole-Locker backup (its scorecards).
     Rounds that are not complete, valid cards are skipped and counted. */
  function parseImport(text) {
    var doc;
    try { doc = JSON.parse(text); } catch (e) { return { ok: false, error: 'not_json' }; }
    if (!doc || typeof doc !== 'object') return { ok: false, error: 'not_rounds' };
    var list;
    if (doc.format === EXPORT_FORMAT) {
      if (!isInt(doc.version) || doc.version > EXPORT_VERSION) return { ok: false, error: 'newer' };
      list = doc.rounds;
    } else if (doc.format === 'golfraw.locker') {
      list = doc.scorecards || [];
    } else {
      return { ok: false, error: 'not_rounds' };
    }
    if (!Array.isArray(list)) return { ok: false, error: 'not_rounds' };
    var rounds = [], skipped = 0;
    for (var i = 0; i < list.length && i < 500; i++) {
      var c = cleanRound(list[i]);
      if (c) rounds.push(c); else skipped++;
    }
    return { ok: true, rounds: rounds, skipped: skipped + Math.max(0, list.length - 500) };
  }

  /* Which imported rounds to write: new ids, and newer copies of ones here. */
  function mergePlan(existing, incoming) {
    var have = {};
    (existing || []).forEach(function (c) { have[c.id] = c.updatedAt || 0; });
    var write = [], same = 0;
    incoming.forEach(function (c) {
      if (!(c.id in have) || (c.updatedAt || 0) > have[c.id]) write.push(c); else same++;
    });
    return { write: write, alreadyHere: same };
  }

  /* One row per hole, for a spreadsheet. */
  function toCSV(cards) {
    var rows = [['date', 'course', 'hole', 'par', 'score', 'putts', 'penalties', 'green_in_regulation', 'fairway']];
    (cards || []).forEach(function (c) {
      var date = c.playedAt ? isoDate(c.playedAt) : '';
      (c.holes || []).forEach(function (h, i) {
        var g = known(h.score) ? greenHit(h) : null;
        rows.push([date, c.course || '', i + 1, h.par, h.score, h.putts, h.pen, g === null ? '' : (g ? 'yes' : 'no'),
          h.par >= 4 && h.fir ? h.fir : '']);
      });
    });
    return rows.map(function (r) { return r.map(csvCell).join(','); }).join('\r\n') + '\r\n';
  }
  function csvCell(v) {
    var s = known(v) ? String(v) : '';
    /* A leading = + - @ would run as a formula in a spreadsheet. */
    if (/^[=+\-@]/.test(s)) s = "'" + s;
    return /[",\r\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }
  function isoDate(ms) {
    var d = new Date(ms);
    return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2);
  }

  var api = {
    version: 1,
    SCHEMA_VERSION: SCHEMA_VERSION, LIMITS: LIMITS, PARS_18: PARS_18, PARS_9: PARS_9, CONF: CONF,
    blankCard: blankCard, validate: validate, isValidRound: isValidRound, analyse: analyse,
    greenHit: greenHit, approachFor: approachFor, holeName: holeName, holeNamePlural: holeNamePlural,
    toParText: toParText, blowupRule: blowupRule, causeText: causeText, summary: summary, shareText: shareText, habit: habit,
    exportRounds: exportRounds, parseImport: parseImport, mergePlan: mergePlan, toCSV: toCSV
  };
  root.GolfrawRoundCard = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : this);
