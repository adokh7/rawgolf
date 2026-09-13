/* ==========================================================================
   GOLFRAW PRO — coach & fitter report engine
   --------------------------------------------------------------------------
   Turns what the Locker already holds — the active bag, a range session, the
   completed scorecards — into one report model, and renders that model as a
   one-page document. The page prints it (Save as PDF) and can encode it into
   a share link. No network code: the model is built and rendered on the
   reader's device, and a share link carries the data in its fragment, which
   browsers never send to a server.

   Every threshold here is copied from the tool that owns it, so a number on
   the report is the same number the reader saw in the tool:
     Standing Order  MIN_SHOTS 5, GOOD_SHOTS 8, GAP_HOLE 25, GAP_DUP 8
     Bag Audit       DEAD_SCORE 4 (usage x trust), never-used = dead
     Tendency Engine MIN_ROUNDS 3, MIN_MISSES 8, BIAS 60%
   ========================================================================== */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.GolfrawReport = factory();
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var MIN_SHOTS = 5, GOOD_SHOTS = 8, GAP_HOLE = 25, GAP_DUP = 8;
  var DEAD_SCORE = 4;
  var MIN_ROUNDS = 3, MIN_MISSES = 8, BIAS = 0.60;
  var SHARE_VERSION = 1, SHARE_MAX = 16 * 1024;

  /* ------------------------------------------------------ statistics --- */
  function sortNum(a) { return a.slice().sort(function (x, y) { return x - y; }); }
  function pct(s, p) { var n = s.length; if (!n) return null; if (n === 1) return s[0]; var i = (n - 1) * p, lo = Math.floor(i), hi = Math.ceil(i); return lo === hi ? s[lo] : s[lo] + (s[hi] - s[lo]) * (i - lo); }
  function stdev(a) { var n = a.length; if (n < 2) return null; var m = 0, i; for (i = 0; i < n; i++) m += a[i]; m /= n; var acc = 0; for (i = 0; i < n; i++) acc += (a[i] - m) * (a[i] - m); return Math.sqrt(acc / (n - 1)); }
  function r0(x) { return x === null || x === undefined ? null : Math.round(x); }
  function r1(x) { return x === null || x === undefined ? null : Math.round(x * 10) / 10; }

  function describe(name, shots) {
    var s = sortNum(shots);
    return { name: name, n: s.length, median: pct(s, 0.5), sd: stdev(s), p10: pct(s, 0.10), p90: pct(s, 0.90),
      min: s.length ? s[0] : null, max: s.length ? s[s.length - 1] : null, reliable: s.length >= MIN_SHOTS, solid: s.length >= GOOD_SHOTS };
  }
  function analyse(clubs) {
    var rows = [];
    for (var i = 0; i < clubs.length; i++) if (clubs[i].shots && clubs[i].shots.length) rows.push(describe(clubs[i].name, clubs[i].shots));
    rows.sort(function (a, b) { return b.median - a.median; });
    for (var j = 0; j < rows.length; j++) rows[j].gapToNext = j < rows.length - 1 ? rows[j].median - rows[j + 1].median : null;
    return rows;
  }
  function gapVerdicts(rows) {
    var out = [];
    for (var i = 0; i < rows.length - 1; i++) {
      var a = rows[i], b = rows[i + 1], gap = a.median - b.median;
      if (!a.reliable || !b.reliable) continue;
      if (gap > GAP_HOLE) out.push({ kind: 'gap', title: 'Hole in the bag', text: r0(gap) + ' yards between ' + a.name + ' (' + r0(a.median) + ') and ' + b.name + ' (' + r0(b.median) + '). Nothing covers the distance in between.' });
      else if (gap < GAP_DUP) out.push({ kind: 'dup', title: 'Two clubs, one job', text: a.name + ' and ' + b.name + ' are ' + r0(gap) + ' yards apart on the median; the shorter one is the usual cut.' });
      if (gap >= GAP_DUP && gap <= GAP_HOLE && a.solid && b.solid && a.p10 < b.p90) out.push({ kind: 'dup', title: 'Overlapping dispersion', text: a.name + ' and ' + b.name + ' sit ' + r0(gap) + ' yards apart, but their 80% bands overlap: on a given swing you cannot tell which one you hit.' });
    }
    if (!out.length && rows.length > 1) out.push({ kind: 'ok', title: 'Ladder is clean', text: 'No gap over ' + GAP_HOLE + ' yards and no two clubs inside ' + GAP_DUP + ' yards of each other.' });
    return out;
  }

  /* ---------------------------------------------------------- bag ------ */
  function deadWood(bag) {
    if (!bag || !bag.clubs || !bag.clubs.length) return null;
    var clubs = [], dead = [], audited = 0;
    for (var i = 0; i < bag.clubs.length; i++) {
      var c = bag.clubs[i], usage = (c.usage === null || c.usage === undefined) ? null : c.usage;
      var conf = c.conf >= 1 ? c.conf : 3, score = null, isDead = false, never = false, scored = false;
      if (usage !== null) { scored = true; audited++; score = usage * conf; never = usage === 0; isDead = never || score <= DEAD_SCORE; }
      var rec = { name: c.name, carry: c.carry, usage: usage, conf: conf, score: score, dead: isDead, never: never, scored: scored };
      clubs.push(rec); if (isDead) dead.push(c.name);
    }
    return { clubs: clubs, dead: dead, audited: audited };
  }

  /* --------------------------------------------------- tendencies ------ */
  function summarise(card) {
    var s = { played: 0, gross: 0, par: 0, firOpp: 0, firHit: 0, firLeft: 0, firRight: 0, girOpp: 0, girHit: 0, appShort: 0, appLong: 0, appLeft: 0, appRight: 0, putts: 0, puttsCounted: 0, threePutts: 0 };
    var holes = card.holes || [];
    for (var i = 0; i < holes.length; i++) {
      var h = holes[i];
      if (h.score === null || h.score === undefined) continue;
      s.played++; s.gross += h.score; s.par += h.par;
      if (h.par >= 4 && h.fir) { s.firOpp++; if (h.fir === 'hit') s.firHit++; else if (h.fir === 'left') s.firLeft++; else if (h.fir === 'right') s.firRight++; }
      if (h.app) { s.girOpp++; if (h.app === 'hit') s.girHit++; else if (h.app === 'short') s.appShort++; else if (h.app === 'long') s.appLong++; else if (h.app === 'left') s.appLeft++; else if (h.app === 'right') s.appRight++; }
      if (h.putts !== null && h.putts !== undefined) { s.putts += h.putts; s.puttsCounted++; if (h.putts >= 3) s.threePutts++; }
    }
    return s;
  }
  function bias(a, b, la, lb) {
    var total = a + b;
    if (total < MIN_MISSES) return { enough: false, total: total };
    var share = a / total, side = la, count = a;
    if (b > a) { share = b / total; side = lb; count = b; }
    return { enough: true, total: total, side: side, share: share, count: count, strong: share >= BIAS };
  }
  function tendencies(cards) {
    var rounds = [];
    for (var i = 0; i < cards.length; i++) rounds.push(summarise(cards[i]));
    var n = rounds.length;
    if (!n) return null;
    var t = { firLeft: 0, firRight: 0, appShort: 0, appLong: 0, appLeft: 0, appRight: 0, firOpp: 0, firHit: 0, girOpp: 0, girHit: 0, putts: 0, puttsCounted: 0, threePutts: 0, toPar: 0 };
    for (var k = 0; k < n; k++) { var r = rounds[k]; for (var key in t) if (key in r) t[key] += r[key]; t.toPar += r.gross - r.par; }
    return {
      rounds: n, enough: n >= MIN_ROUNDS,
      avgToPar: r1(t.toPar / n),
      firPct: t.firOpp ? Math.round(100 * t.firHit / t.firOpp) : null,
      girPct: t.girOpp ? Math.round(100 * t.girHit / t.girOpp) : null,
      puttsPerRound: t.puttsCounted ? r1(t.putts / n) : null,
      threePutts: t.threePutts,
      tee: bias(t.firLeft, t.firRight, 'left', 'right'),
      distance: bias(t.appShort, t.appLong, 'short', 'long')
    };
  }

  /* ---------------------------------------------------------- model ---- */
  function buildModel(input) {
    input = input || {};
    var session = input.session || null, rows = session ? analyse(session.clubs || []) : [];
    var shots = 0; for (var i = 0; i < rows.length; i++) shots += rows[i].n;
    return {
      v: SHARE_VERSION,
      generated: input.now || Date.now(),
      coach: String(input.coach || '').slice(0, 60),
      client: String(input.client || '').slice(0, 60),
      notes: String(input.notes || '').slice(0, 1200),
      handicap: (input.handicap === null || input.handicap === undefined || input.handicap === '') ? null : Number(input.handicap),
      units: input.units === 'meters' ? 'meters' : 'yards',
      session: session ? { label: session.label || '', startedAt: session.startedAt || 0, shots: shots, clubs: rows.length } : null,
      rows: rows.map(function (r) { return { name: r.name, n: r.n, median: r0(r.median), sd: r1(r.sd), p10: r0(r.p10), p90: r0(r.p90), min: r.min, max: r.max, reliable: r.reliable, solid: r.solid, gap: r0(r.gapToNext) }; }),
      verdicts: gapVerdicts(rows),
      bag: deadWood(input.bag),
      tendencies: input.scorecards && input.scorecards.length ? tendencies(input.scorecards) : null
    };
  }

  /* ------------------------------------------------------- sharing ----- */
  function utf8ToB64Url(str) {
    var b64;
    if (typeof Buffer !== 'undefined') b64 = Buffer.from(str, 'utf8').toString('base64');
    else b64 = btoa(unescape(encodeURIComponent(str)));
    return b64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  }
  function b64UrlToUtf8(s) {
    var b64 = s.replace(/-/g, '+').replace(/_/g, '/'); while (b64.length % 4) b64 += '=';
    if (typeof Buffer !== 'undefined') return Buffer.from(b64, 'base64').toString('utf8');
    return decodeURIComponent(escape(atob(b64)));
  }
  function encodeShare(model) {
    var json = JSON.stringify(model);
    if (json.length > SHARE_MAX) return { ok: false, error: 'This report is too large to fit in a link (' + Math.round(json.length / 1024) + ' KB). Shorten the notes.' };
    return { ok: true, payload: utf8ToB64Url(json), bytes: json.length };
  }
  function decodeShare(payload) {
    try {
      var m = JSON.parse(b64UrlToUtf8(String(payload || '')));
      if (!m || m.v !== SHARE_VERSION || !Array.isArray(m.rows)) return { ok: false, error: 'That link does not contain a GolfRaw report.' };
      return { ok: true, model: m };
    } catch (e) { return { ok: false, error: 'That link is damaged or incomplete.' }; }
  }

  /* -------------------------------------------------------- render ----- */
  function esc(s) { return String(s === null || s === undefined ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  function pctText(x) { return Math.round(x * 100) + '%'; }
  function dateText(ts) { try { return new Date(ts).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' }); } catch (e) { return ''; } }

  function chartSvg(rows) {
    if (!rows.length) return '';
    var W = 560, rowH = 22, padT = 20, padB = 24, labelW = 84, valW = 40, x0 = labelW, x1 = W - valW, H = padT + rows.length * rowH + padB;
    var lo = Infinity, hi = -Infinity;
    for (var i = 0; i < rows.length; i++) { lo = Math.min(lo, rows[i].min); hi = Math.max(hi, rows[i].max); }
    var span = Math.max(10, hi - lo); lo -= span * 0.06; hi += span * 0.06;
    var sx = function (v) { return x0 + (v - lo) / (hi - lo) * (x1 - x0); };
    var p = ['<svg class="rp-chart" viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="Carry dispersion by club" xmlns="http://www.w3.org/2000/svg">'];
    for (var t = Math.ceil(lo / 25) * 25; t <= hi; t += 25) {
      p.push('<line x1="' + sx(t).toFixed(1) + '" y1="' + (padT - 6) + '" x2="' + sx(t).toFixed(1) + '" y2="' + (H - padB + 3) + '" stroke="#D9E0DA" stroke-width="1"/>');
      p.push('<text x="' + sx(t).toFixed(1) + '" y="' + (H - padB + 15) + '" font-size="9" fill="#55655B" text-anchor="middle" font-family="Inter, system-ui, sans-serif">' + t + '</text>');
    }
    for (var r = 0; r < rows.length; r++) {
      var row = rows[r], y = padT + r * rowH + rowH / 2, dim = row.reliable ? '' : ' opacity="0.45"';
      p.push('<g' + dim + '><line x1="' + sx(row.min).toFixed(1) + '" y1="' + y + '" x2="' + sx(row.max).toFixed(1) + '" y2="' + y + '" stroke="#0B1F15" stroke-width="1"/>');
      var bx = sx(row.p10), bw = Math.max(2, sx(row.p90) - sx(row.p10));
      p.push('<rect x="' + bx.toFixed(1) + '" y="' + (y - 6) + '" width="' + bw.toFixed(1) + '" height="12" fill="#0A4D2E" fill-opacity="0.18" stroke="#0A4D2E" stroke-width="1"/>');
      p.push('<line x1="' + sx(row.median).toFixed(1) + '" y1="' + (y - 8) + '" x2="' + sx(row.median).toFixed(1) + '" y2="' + (y + 8) + '" stroke="#1B7A43" stroke-width="2.5"/>');
      p.push('<text x="' + (labelW - 8) + '" y="' + (y + 3.5) + '" font-size="10" fill="#0B1F15" text-anchor="end" font-family="Inter, Archivo, system-ui, sans-serif" font-weight="700">' + esc(row.name) + '</text>');
      p.push('<text x="' + (W - 4) + '" y="' + (y + 3.5) + '" font-size="10" fill="#0B1F15" text-anchor="end" font-family="Inter, system-ui, sans-serif" font-weight="600">' + row.median + '</text></g>');
    }
    p.push('</svg>');
    return p.join('');
  }

  function renderReport(m) {
    var u = m.units === 'meters' ? 'm' : 'yd', h = [];
    h.push('<header class="rp-head"><div class="rp-brand">GOLF<span>RAW</span> <em>Pro</em></div><div class="rp-title"><h2>Bag &amp; Gapping Report</h2><p>' + esc(dateText(m.generated)) + '</p></div></header>');
    h.push('<dl class="rp-meta">' +
      '<div><dt>Player</dt><dd>' + (m.client ? esc(m.client) : '—') + '</dd></div>' +
      '<div><dt>Coach / fitter</dt><dd>' + (m.coach ? esc(m.coach) : '—') + '</dd></div>' +
      '<div><dt>Handicap</dt><dd>' + (m.handicap === null ? '—' : esc(m.handicap)) + '</dd></div>' +
      '<div><dt>Session</dt><dd>' + (m.session ? esc(m.session.label || 'Range session') + (m.session.startedAt ? ' · ' + esc(dateText(m.session.startedAt)) : '') + ' · ' + m.session.shots + ' shots, ' + m.session.clubs + ' clubs' : 'No range session logged') + '</dd></div></dl>');

    h.push('<section class="rp-sec"><h3>Carry dispersion</h3>');
    if (m.rows.length) {
      h.push(chartSvg(m.rows));
      h.push('<table class="rp-tbl"><thead><tr><th>Club</th><th>Shots</th><th>Median (' + u + ')</th><th>Spread</th><th>80% band</th><th>Gap</th></tr></thead><tbody>');
      for (var i = 0; i < m.rows.length; i++) {
        var r = m.rows[i];
        h.push('<tr' + (r.reliable ? '' : ' class="thin"') + '><td>' + esc(r.name) + (r.reliable ? '' : ' <small>(thin)</small>') + '</td><td>' + r.n + '</td><td><b>' + r.median + '</b></td><td>' + (r.sd === null ? '—' : '±' + r.sd) + '</td><td>' + (r.n >= 2 ? r.p10 + '–' + r.p90 : '—') + '</td><td>' + (r.gap === null ? '—' : r.gap) + '</td></tr>');
      }
      h.push('</tbody></table>');
      h.push('<p class="rp-note">Median carry, not average: one thinned shot cannot move it. The 80% band is the 10th to 90th percentile of what was actually hit. Clubs marked <em>thin</em> have fewer than ' + MIN_SHOTS + ' shots and are excluded from the gap checks.</p>');
    } else h.push('<p class="rp-empty">No range session to report. Log shots in the Standing Order, or import a launch-monitor export, and rebuild.</p>');
    h.push('</section>');

    h.push('<section class="rp-sec"><h3>Bag recommendations</h3>');
    var flags = [];
    for (var v = 0; v < m.verdicts.length; v++) flags.push('<li class="' + m.verdicts[v].kind + '"><b>' + esc(m.verdicts[v].title) + '</b> ' + esc(m.verdicts[v].text) + '</li>');
    if (m.bag && m.bag.audited) {
      if (m.bag.dead.length) flags.push('<li class="dup"><b>Passengers</b> ' + esc(m.bag.dead.join(', ')) + ' score ' + DEAD_SCORE + ' or below on uses × trust in the Bag Audit' + (m.bag.clubs.some(function (c) { return c.never; }) ? ', or were never used' : '') + '. Candidates to drop before adding anything.</li>');
      else flags.push('<li class="ok"><b>No passengers</b> Every audited club clears the uses × trust bar.</li>');
    }
    if (!flags.length) flags.push('<li class="thin">Nothing to recommend yet — the gap checks need at least two clubs with ' + MIN_SHOTS + '+ shots, and the passenger check needs usage entered in the Bag Audit.</li>');
    h.push('<ul class="rp-flags">' + flags.join('') + '</ul></section>');

    h.push('<section class="rp-sec"><h3>On-course tendencies</h3>');
    var t = m.tendencies;
    if (!t) h.push('<p class="rp-empty">No completed rounds in the Tendency Engine.</p>');
    else {
      h.push('<dl class="rp-stats"><div><dt>Rounds</dt><dd>' + t.rounds + '</dd></div><div><dt>Avg to par</dt><dd>' + (t.avgToPar === null ? '—' : (t.avgToPar > 0 ? '+' : '') + t.avgToPar) + '</dd></div><div><dt>Fairways</dt><dd>' + (t.firPct === null ? '—' : t.firPct + '%') + '</dd></div><div><dt>Greens</dt><dd>' + (t.girPct === null ? '—' : t.girPct + '%') + '</dd></div><div><dt>Putts / round</dt><dd>' + (t.puttsPerRound === null ? '—' : t.puttsPerRound) + '</dd></div><div><dt>Three-putts</dt><dd>' + t.threePutts + '</dd></div></dl>');
      var lines = [];
      if (!t.enough) lines.push('Fewer than ' + MIN_ROUNDS + ' rounds logged: nothing below is called a tendency yet.');
      if (t.tee.enough) lines.push(t.tee.strong ? 'Misses ' + t.tee.side + ' off the tee ' + pctText(t.tee.share) + ' of the time (' + t.tee.count + ' of ' + t.tee.total + ' missed fairways). A pattern, not variance.' : 'No strong directional bias off the tee: misses split ' + pctText(t.tee.share) + ' ' + t.tee.side + '.');
      else lines.push('Too few missed fairways (' + t.tee.total + ') to call a directional tendency.');
      if (t.distance.enough) lines.push(t.distance.strong ? 'Approaches finish ' + t.distance.side + ' ' + pctText(t.distance.share) + ' of the time when they miss on distance — a club-selection pattern.' : 'Distance control on approach is balanced (' + pctText(t.distance.share) + ' ' + t.distance.side + ').');
      h.push('<ul class="rp-lines"><li>' + lines.map(esc).join('</li><li>') + '</li></ul>');
    }
    h.push('</section>');

    if (m.notes) h.push('<section class="rp-sec"><h3>Notes</h3><p class="rp-notes">' + esc(m.notes).replace(/\n/g, '<br>') + '</p></section>');
    h.push('<footer class="rp-foot">Measured by the player on the range and logged with GolfRaw tools; range balls commonly fly 5–10% shorter than premium balls, so read the gaps, not the absolute yardages. Built on the player’s own device — nothing was uploaded. golfraw.com/tools-coach-report</footer>');
    return h.join('');
  }

  return { buildModel: buildModel, renderReport: renderReport, chartSvg: chartSvg, encodeShare: encodeShare, decodeShare: decodeShare,
    analyse: analyse, gapVerdicts: gapVerdicts, deadWood: deadWood, tendencies: tendencies, summarise: summarise,
    thresholds: { MIN_SHOTS: MIN_SHOTS, GOOD_SHOTS: GOOD_SHOTS, GAP_HOLE: GAP_HOLE, GAP_DUP: GAP_DUP, DEAD_SCORE: DEAD_SCORE, MIN_ROUNDS: MIN_ROUNDS, MIN_MISSES: MIN_MISSES, BIAS: BIAS } };
}));
