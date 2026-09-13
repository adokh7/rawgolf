/* ==========================================================================
   GOLFRAW PRO — launch-monitor import engine
   --------------------------------------------------------------------------
   Turns a CSV export from a launch monitor (TrackMan, Foresight, Garmin,
   FlightScope, Rapsodo, SkyTrak, or anything with a club column and a carry
   column) into the same {name, shots[]} club records the Standing Order logs
   by hand. Everything downstream — medians, 80% bands, gaps, the bag sync —
   is unchanged, because the import produces exactly what the keypad does.

   Design rules:
     - Heuristic mapping, never vendor-locked. Vendors rename columns between
       app versions; a header that says "carry" is the signal, the vendor name
       is only a label shown to the reader.
     - The reader can always override the mapping. The engine suggests; the
       UI confirms.
     - Nothing leaves the device. This file has no network code.

   Exposed as window.GolfrawLMImport in the browser and module.exports under
   node, so the same code is unit-tested with `node scripts/test_lm_import.js`.
   ========================================================================== */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.GolfrawLMImport = factory();
}(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var MAX_SHOTS = 50;          /* per club, mirrors the Locker's RangeClubSchema */
  var MAX_CARRY = 500;
  var YARDS_PER_METER = 1.0936133;

  /* ------------------------------------------------------------ CSV ----- */

  /* RFC 4180 tokenizer with delimiter sniffing. Handles quoted fields with
     embedded delimiters and newlines, doubled quotes, BOM, CRLF. */
  function sniffDelimiter(text) {
    var head = text.split(/\r?\n/).slice(0, 12).join('\n');
    var cands = [',', ';', '\t', '|'], best = ',', bestN = -1;
    for (var i = 0; i < cands.length; i++) {
      var n = (head.split(cands[i]).length - 1);
      if (n > bestN) { bestN = n; best = cands[i]; }
    }
    return best;
  }

  function tokenize(text, delim) {
    var rows = [], row = [], field = '', inQ = false, i = 0, c;
    if (text.charCodeAt(0) === 0xFEFF) text = text.slice(1);
    for (i = 0; i < text.length; i++) {
      c = text[i];
      if (inQ) {
        if (c === '"') {
          if (text[i + 1] === '"') { field += '"'; i++; }
          else inQ = false;
        } else field += c;
      } else if (c === '"') inQ = true;
      else if (c === delim) { row.push(field); field = ''; }
      else if (c === '\n' || c === '\r') {
        if (c === '\r' && text[i + 1] === '\n') i++;
        row.push(field); field = '';
        rows.push(row); row = [];
      } else field += c;
    }
    if (field !== '' || row.length) { row.push(field); rows.push(row); }
    return rows.filter(function (r) { return r.some(function (x) { return String(x).trim() !== ''; }); });
  }

  /* ------------------------------------------------------- HEADERS ----- */

  var norm = function (s) { return String(s || '').toLowerCase().replace(/[^a-z0-9%°]+/g, ' ').trim(); };

  var UNIT_TOKENS = /^(yds?|yards?|m|meters?|metres?|mph|km\/?h|m\/s|deg|degrees?|°|rpm|ft|feet|%|s|sec|in|inches)$/;

  function isNumericCell(v) {
    var s = String(v).trim().replace(/,/g, '');
    return s !== '' && /^-?\d+(\.\d+)?$/.test(s);
  }

  /* The header is the first row that looks like column names AND contains a
     club-ish and a distance-ish label. Vendor exports often begin with a
     preamble ("Player: …", "Session date: …") that must be skipped. */
  function findHeader(rows) {
    for (var i = 0; i < Math.min(rows.length, 25); i++) {
      var r = rows[i];
      if (r.length < 2) continue;
      var textCells = r.filter(function (c) { return !isNumericCell(c) && String(c).trim() !== ''; }).length;
      if (textCells < Math.max(2, r.length * 0.5)) continue;
      var joined = r.map(norm).join(' | ');
      if (/\bclub\b/.test(joined) && /carry|distance|total/.test(joined)) return i;
    }
    /* fall back: first mostly-text row */
    for (var j = 0; j < Math.min(rows.length, 25); j++) {
      var q = rows[j];
      if (q.length >= 2 && q.filter(function (c) { return !isNumericCell(c) && String(c).trim() !== ''; }).length >= q.length * 0.5) return j;
    }
    return 0;
  }

  /* A row immediately after the header whose cells are mostly unit tokens
     ("yds", "mph", "deg") is a units row, not data. */
  function isUnitsRow(r) {
    var cells = r.map(function (c) { return String(c).trim().toLowerCase(); }).filter(Boolean);
    if (!cells.length) return false;
    var hits = cells.filter(function (c) { return UNIT_TOKENS.test(c.replace(/[()\[\]]/g, '')); }).length;
    return hits >= Math.max(2, cells.length * 0.5);
  }

  /* Summary rows vendors append per club or per session. */
  var SUMMARY = /^(avg|average|mean|median|std|st ?dev|sd|stdev|std dev|consistency|total|totals|summary|max|maximum|min|minimum|range|count|session)\b/i;

  /* ------------------------------------------------------- MAPPING ----- */

  function unitsFromLabel(label) {
    var l = norm(label);
    if (/\b(yds?|yards?)\b/.test(l)) return 'yards';
    if (/\b(m|meters?|metres?)\b/.test(l)) return 'meters';
    return null;
  }

  /* Score every header for each role; the best score wins, ties broken by
     column order so a consistent choice is made for identical labels. */
  function scoreHeader(label, role) {
    var l = norm(label);
    if (!l) return 0;
    if (role === 'club') {
      if (/^club( name)?$/.test(l)) return 100;
      if (/^club type$/.test(l)) return 90;       /* "Iron" is a category, not a club */
      if (/\bclub\b/.test(l) && !/speed|path|face|head|angle|lie|loft|brand|model|mph|ms/.test(l)) return 80;
      if (/\bclub (brand|model)\b/.test(l)) return 20;    /* last resort: Rapsodo */
      return 0;
    }
    if (role === 'carry') {
      if (/side|lateral|offline|curve|carry side|carry \(side/.test(l)) return 0;
      if (/^carry( distance)?( \(?(yds?|yards?|m|meters?|metres?)\)?)?$/.test(l)) return 100;
      if (/\bcarry\b/.test(l)) return 85;
      if (/^total( distance)?/.test(l)) return 40;   /* better than nothing, flagged as total */
      if (/\bdistance\b/.test(l) && !/total|run|roll|offline|lateral|target/.test(l)) return 50;
      return 0;
    }
    if (role === 'total') {
      if (/^total( distance)?( \(?(yds?|yards?|m|meters?|metres?)\)?)?$/.test(l)) return 100;
      if (/\btotal\b/.test(l) && !/spin|score/.test(l)) return 70;
      return 0;
    }
    return 0;
  }

  function pickColumn(headers, role) {
    var best = -1, bestScore = 0;
    for (var i = 0; i < headers.length; i++) {
      var s = scoreHeader(headers[i], role);
      if (s > bestScore) { bestScore = s; best = i; }
    }
    return { index: best, score: bestScore };
  }

  var VENDORS = [
    { id: 'trackman',   label: 'TrackMan',   need: ['club speed', 'smash factor', 'carry', 'total'], any: ['attack angle', 'dynamic loft', 'spin rate', 'club path', 'face angle'] },
    { id: 'foresight',  label: 'Foresight',  need: ['carry distance', 'total distance'], any: ['club head speed', 'run distance', 'offline distance', 'hang time', 'back spin', 'closure rate'] },
    { id: 'garmin',     label: 'Garmin',     need: ['carry distance'], any: ['club type', 'backspin', 'sidespin', 'date time', 'club speed', 'launch direction'] },
    { id: 'rapsodo',    label: 'Rapsodo',    need: ['carry distance', 'club type'], any: ['club brand', 'club model', 'side carry', 'apex', 'descent angle'] },
    { id: 'flightscope',label: 'FlightScope',need: ['carry distance'], any: ['launch angle v', 'spin', 'height', 'roll distance', 'lateral landing', 'spin loft', 'vertical swing plane'] },
    { id: 'skytrak',    label: 'SkyTrak',    need: ['carry'], any: ['skytrak', 'side angle', 'offline', 'back spin', 'side spin'] }
  ];

  function detectVendor(headers) {
    /* normalise and drop a trailing unit word so "Carry (yds)" compares as "carry" */
    var hs = headers.map(norm).map(function (h) { return h.replace(/\s+(yds?|yards?|m|meters?|metres?|mph|km h|m s|deg|rpm|ft|s)$/, '').trim(); });
    var has = function (t) { return hs.indexOf(t) !== -1; };
    var best = null, bestScore = 0, bestMax = 1;
    for (var i = 0; i < VENDORS.length; i++) {
      var v = VENDORS[i];
      if (!v.need.every(has)) continue;
      var extra = v.any.filter(has).length;
      var score = v.need.length * 2 + extra;
      /* every vendor must clear its own bar before it competes: shared words
         like "carry" and "total" are not a fingerprint on their own */
      if (score < v.need.length * 2 + 2) continue;
      if (score > bestScore) { bestScore = score; best = v; bestMax = v.need.length * 2 + v.any.length; }
    }
    if (best) return { id: best.id, label: best.label, confidence: Math.round(100 * bestScore / bestMax) / 100 };
    return { id: 'generic', label: 'Generic CSV', confidence: 0 };
  }

  /* -------------------------------------------------- CLUB NAMING ----- */

  /* Canonical names match the Standing Order's own club strip so imported
     shots land on the same club the reader taps for. Unknown names are kept
     (trimmed) rather than dropped: the reader can rename them in the preview. */
  function normalizeClub(raw) {
    var s = String(raw || '').trim();
    if (!s) return null;
    var l = s.toLowerCase().replace(/[_]+/g, ' ').replace(/\s+/g, ' ').trim();
    var m;
    if (/^(putter|putt|pt)$/.test(l)) return { name: 'Putter', skip: true };
    if (/^(driver|dr|d|1w|1 wood|1-wood|1 w)$/.test(l) || /^driver\b/.test(l)) return { name: 'Driver' };
    if ((m = l.match(/^(\d)\s*-?\s*(w|wd|wood|fw|fairway( wood)?)$/)) || (m = l.match(/^(?:wood|fw|fairway(?: wood)?)\s*-?\s*(\d)$/))) return { name: m[1] + '-Wood' };
    if ((m = l.match(/^(\d)\s*-?\s*(h|hy|hyb|hybrid|rescue|r|u|ut|utility)$/)) || (m = l.match(/^(?:hybrid|rescue|utility)\s*-?\s*(\d)$/))) return { name: m[1] + '-Hybrid' };
    if ((m = l.match(/^(\d)\s*-?\s*(i|ir|iron)$/)) || (m = l.match(/^(?:iron|i)\s*-?\s*(\d)$/))) return { name: m[1] + '-iron' };
    if (/^(pw|p|pitching( wedge)?|pitch)$/.test(l)) return { name: 'PW' };
    if (/^(gw|aw|uw|gap( wedge)?|approach( wedge)?|utility wedge|a)$/.test(l)) return { name: 'GW' };
    if (/^(sw|s|sand( wedge)?)$/.test(l)) return { name: 'SW' };
    if (/^(lw|l|lob( wedge)?)$/.test(l)) return { name: 'LW' };
    if ((m = l.match(/^(\d{2})\s*(°|deg|degrees?)?\s*(w|wedge)?$/)) || (m = l.match(/^(?:wedge)\s*(\d{2})\s*(°|deg)?$/))) {
      var loft = parseInt(m[1], 10);
      if (loft >= 44 && loft <= 47) return { name: 'PW', loft: loft };
      if (loft >= 48 && loft <= 53) return { name: 'GW', loft: loft };
      if (loft >= 54 && loft <= 57) return { name: 'SW', loft: loft };
      if (loft >= 58 && loft <= 64) return { name: 'LW', loft: loft };
    }
    /* "7 Iron, Callaway Apex" / "Titleist - 3 Wood": look for a club token
       anywhere before giving up, longest-first so "3 hybrid" is not read as "3 wood". */
    var seg = l.split(/[,|/()]/)[0].trim();
    if (seg !== l) { var again = normalizeClub(seg); if (again && !again.unknown) return again; }
    if (/\bdriver\b/.test(l)) return { name: 'Driver' };
    if ((m = l.match(/\b(\d)\s*-?\s*(?:h|hyb|hybrid|rescue|utility)\b/)) || (m = l.match(/\b(?:hybrid|rescue)\s*-?\s*(\d)\b/))) return { name: m[1] + '-Hybrid' };
    if ((m = l.match(/\b(\d)\s*-?\s*(?:w|wd|wood|fw)\b/)) || (m = l.match(/\b(?:wood|fw)\s*-?\s*(\d)\b/))) return { name: m[1] + '-Wood' };
    if ((m = l.match(/\b(\d)\s*-?\s*(?:i|iron)\b/)) || (m = l.match(/\biron\s*-?\s*(\d)\b/))) return { name: m[1] + '-iron' };
    if (/\b(pw|pitching)\b/.test(l)) return { name: 'PW' };
    if (/\b(gw|aw|gap|approach)\b/.test(l)) return { name: 'GW' };
    if (/\b(sw|sand)\b/.test(l)) return { name: 'SW' };
    if (/\b(lw|lob)\b/.test(l)) return { name: 'LW' };
    return { name: s.slice(0, 40), unknown: true };
  }

  /* ------------------------------------------------------ PIPELINE ----- */

  function parse(text) {
    var delim = sniffDelimiter(text);
    var rows = tokenize(text, delim);
    if (!rows.length) return { ok: false, error: 'The file is empty.' };
    var h = findHeader(rows);
    var headers = rows[h].map(function (c) { return String(c).trim(); });
    var body = rows.slice(h + 1);
    var unitsRow = null;
    if (body.length && isUnitsRow(body[0])) { unitsRow = body[0]; body = body.slice(1); }
    return {
      ok: true,
      delimiter: delim,
      headerRow: h,
      headers: headers,
      unitsRow: unitsRow,
      rows: body,
      vendor: detectVendor(headers)
    };
  }

  function suggestMapping(parsed) {
    var club = pickColumn(parsed.headers, 'club');
    var carry = pickColumn(parsed.headers, 'carry');
    var total = pickColumn(parsed.headers, 'total');
    var units = null;
    if (carry.index >= 0) units = unitsFromLabel(parsed.headers[carry.index]);
    if (!units && parsed.unitsRow && carry.index >= 0) units = unitsFromLabel(parsed.unitsRow[carry.index]);
    if (!units) {
      /* a global hint anywhere in the headers (e.g. "Distance unit: m") */
      var all = parsed.headers.map(norm).join(' ');
      if (/\b(yds?|yards?)\b/.test(all)) units = 'yards';
      else if (/\b(meters?|metres?)\b/.test(all)) units = 'meters';
    }
    return {
      club: club.index, clubScore: club.score,
      carry: carry.index, carryScore: carry.score,
      total: total.index,
      carryIsTotal: carry.index >= 0 && carry.score <= 40,
      units: units,                 /* null = unknown, ask the reader */
      confidence: Math.min(club.score, carry.score) / 100
    };
  }

  /* Extract per-club shot lists. opts: { units: 'yards'|'meters' (of the
     file), target: 'yards'|'meters' (what the session stores), dropMishits:
     bool, mishitRatio: 0.65 } */
  function extract(parsed, mapping, opts) {
    opts = opts || {};
    var fileUnits = opts.units || mapping.units || 'yards';
    var target = opts.target || 'yards';
    var factor = 1;
    if (fileUnits === 'meters' && target === 'yards') factor = YARDS_PER_METER;
    if (fileUnits === 'yards' && target === 'meters') factor = 1 / YARDS_PER_METER;
    var ratio = typeof opts.mishitRatio === 'number' ? opts.mishitRatio : 0.65;

    var byClub = {}, order = [], stats = { rows: parsed.rows.length, used: 0, summary: 0, blank: 0, badCarry: 0, putter: 0, unknownClubs: [] };
    for (var i = 0; i < parsed.rows.length; i++) {
      var r = parsed.rows[i];
      var rawClub = mapping.club >= 0 ? r[mapping.club] : '';
      var rawCarry = mapping.carry >= 0 ? r[mapping.carry] : '';
      if (rawClub === undefined || String(rawClub).trim() === '') { stats.blank++; continue; }
      if (SUMMARY.test(String(rawClub).trim())) { stats.summary++; continue; }
      var cleaned = String(rawCarry === undefined ? '' : rawCarry).trim().replace(/,/g, '').replace(/[^\d.\-]/g, '');
      var v = parseFloat(cleaned);
      if (!isFinite(v) || v <= 0) { stats.badCarry++; continue; }
      v = v * factor;
      if (v < 1 || v > MAX_CARRY) { stats.badCarry++; continue; }
      var nc = normalizeClub(rawClub);
      if (!nc) { stats.blank++; continue; }
      if (nc.skip) { stats.putter++; continue; }
      if (nc.unknown && stats.unknownClubs.indexOf(nc.name) === -1) stats.unknownClubs.push(nc.name);
      if (!byClub[nc.name]) { byClub[nc.name] = { name: nc.name, raw: String(rawClub).trim(), all: [] }; order.push(nc.name); }
      byClub[nc.name].all.push(Math.round(v));
      stats.used++;
    }

    var clubs = [];
    for (var k = 0; k < order.length; k++) {
      var c = byClub[order[k]];
      var kept = c.all.slice(), dropped = [];
      if (opts.dropMishits !== false && kept.length >= 4) {
        var sorted = kept.slice().sort(function (a, b) { return a - b; });
        var med = sorted[Math.floor(sorted.length / 2)];
        var keep2 = [];
        for (var q = 0; q < kept.length; q++) {
          if (kept[q] < med * ratio) dropped.push(kept[q]); else keep2.push(kept[q]);
        }
        kept = keep2;
      }
      /* the Locker caps a club at MAX_SHOTS; a monitor session is chronological,
         so the newest shots are the ones to keep */
      var trimmed = 0;
      if (kept.length > MAX_SHOTS) { trimmed = kept.length - MAX_SHOTS; kept = kept.slice(-MAX_SHOTS); }
      clubs.push({ name: c.name, raw: c.raw, shots: kept, dropped: dropped, trimmed: trimmed });
    }
    return { clubs: clubs, stats: stats, fileUnits: fileUnits, targetUnits: target, factor: factor };
  }

  /* One call for the UI: text in, preview out. The mapping can be overridden
     by passing { club, carry, units } in opts. */
  function run(text, opts) {
    opts = opts || {};
    var parsed = parse(text);
    if (!parsed.ok) return parsed;
    var mapping = suggestMapping(parsed);
    if (typeof opts.club === 'number') mapping.club = opts.club;
    if (typeof opts.carry === 'number') mapping.carry = opts.carry;
    if (opts.units) mapping.units = opts.units;
    var result = extract(parsed, mapping, opts);
    result.ok = true;
    result.parsed = parsed;
    result.mapping = mapping;
    return result;
  }

  return {
    parse: parse,
    suggestMapping: suggestMapping,
    extract: extract,
    run: run,
    normalizeClub: normalizeClub,
    detectVendor: detectVendor,
    sniffDelimiter: sniffDelimiter,
    tokenize: tokenize,
    MAX_SHOTS: MAX_SHOTS
  };
}));
