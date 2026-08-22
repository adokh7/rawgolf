/* ============================================================================
   GOLFRAW LOCKER — STORE
   ----------------------------------------------------------------------------
   Local-first persistence for the tools. Everything lives in the reader's own
   browser; nothing here touches the network.

   Dexie stands in as a hand-written IndexedDB wrapper for the same reason Zod
   does in schema.js — no bundler on this site. What Dexie gives us that plain
   IDB does not is a promise API, schema versioning and a store abstraction, so
   that is exactly what this file provides and nothing more.

   Durability rules this layer guarantees:
     - every write is schema-validated first; invalid data never reaches disk
     - IndexedDB failure (private mode, disabled storage, quota) degrades to a
       localStorage mirror rather than breaking the tool
     - legacy per-tool localStorage keys are migrated once, and are left in
       place afterwards so an older cached page still finds its data
     - all mutations publish an event, so any open drawer stays truthful

   Exposed as window.GolfrawLocker.
   ========================================================================== */
(function (root) {
  'use strict';

  var S = root.GolfrawSchema;
  if (!S) { return; }

  var DB_NAME = 'golfraw-locker';
  /* v2 added `sessions` (range logger), v3 added `scorecards` (tendency
     engine). onupgradeneeded creates any store that is missing, so an existing
     database upgrades in place without touching the records already in it.

     `scorecards` is deliberately NOT the `rounds` store. `rounds` belongs to
     the Handicap Lie Detector, whose saveRounds() clears and rewrites the whole
     store on every keystroke — hole-by-hole data written there would be
     destroyed the moment the reader opened that tool. */
  var DB_VERSION = 3;
  var STORES = ['profile', 'bags', 'rounds', 'toolState', 'sessions', 'scorecards', 'meta'];
  var MIRROR_KEY = 'golfraw_locker_mirror';
  var EXPORT_FORMAT = 'golfraw.locker';
  /* v2 exports carry `sessions`, v3 adds `scorecards`. Older files still
     import: missing fields default to empty, which is why the version check is
     `>` and not `!==`. */
  var EXPORT_VERSION = 3;
  var MAX_CLUBS = 14;      /* Rule 4.1b */
  var MAX_ROUNDS = 20;     /* what the handicap tool scores against */
  var MAX_SHOTS = 50;      /* per club, per session */
  var HOLES = 18;

  /* ======================================================== SCHEMAS ======= */

  var ClubSchema = S.object({
    name: S.string({ max: 40 }).def(''),
    carry: S.number({ min: 1, max: 500 }).nullable().def(null),
    usage: S.integer({ min: 0, max: 100 }).nullable().def(null),
    conf: S.integer({ min: 1, max: 5 }).def(3)
  });

  var BagSchema = S.object({
    id: S.string({ min: 1, max: 64 }),
    name: S.string({ max: 60 }).def('My Bag'),
    clubs: S.arrayOf(ClubSchema, { max: MAX_CLUBS }).def([]),
    createdAt: S.integer({ min: 0 }).def(0),
    updatedAt: S.integer({ min: 0 }).def(0)
  });

  var RoundSchema = S.object({
    id: S.string({ min: 1, max: 64 }),
    seq: S.integer({ min: 0, max: 999 }).def(0),
    score: S.integer({ min: 40, max: 200 }).nullable().def(null),
    cr: S.number({ min: 50, max: 90 }).nullable().def(null),
    slope: S.integer({ min: 55, max: 155 }).nullable().def(null),
    updatedAt: S.integer({ min: 0 }).def(0)
  });

  /* One club's shots inside a range session. Shots are raw carry yardages in
     entry order — the statistics are derived, never stored, so a mis-tapped
     shot can be deleted and every figure recomputes from the source. */
  var RangeClubSchema = S.object({
    name: S.string({ min: 1, max: 40 }),
    shots: S.arrayOf(S.number({ min: 1, max: 500 }), { max: MAX_SHOTS }).def([])
  });

  var RangeSessionSchema = S.object({
    id: S.string({ min: 1, max: 64 }),
    label: S.string({ max: 60 }).def(''),
    clubs: S.arrayOf(RangeClubSchema, { max: MAX_CLUBS }).def([]),
    startedAt: S.integer({ min: 0 }).def(0),
    updatedAt: S.integer({ min: 0 }).def(0)
  });

  /* One hole as tapped in after the round. Every field is nullable because a
     card is saved continuously while it is still being filled in, and because
     a par 3 has no fairway to hit. */
  var HoleSchema = S.object({
    par: S.integer({ min: 3, max: 6 }).def(4),
    score: S.integer({ min: 1, max: 15 }).nullable().def(null),
    fir: S.oneOf(['left', 'hit', 'right']).nullable().def(null),
    app: S.oneOf(['hit', 'short', 'long', 'left', 'right']).nullable().def(null),
    putts: S.integer({ min: 0, max: 6 }).nullable().def(null)
  });

  var ScorecardSchema = S.object({
    id: S.string({ min: 1, max: 64 }),
    course: S.string({ max: 80 }).def(''),
    playedAt: S.integer({ min: 0 }).def(0),
    holes: S.arrayOf(HoleSchema, { max: HOLES }).def([]),
    updatedAt: S.integer({ min: 0 }).def(0)
  });

  var UserProfileSchema = S.object({
    id: S.string({ min: 1, max: 32 }).def('me'),
    displayName: S.string({ max: 60 }).def(''),
    claimedHandicap: S.number({ min: -10, max: 54 }).nullable().def(null),
    homeCourse: S.string({ max: 80 }).def(''),
    units: S.oneOf(['yards', 'meters']).def('yards'),
    activeBagId: S.string({ max: 64 }).nullable().def(null),
    createdAt: S.integer({ min: 0 }).def(0),
    updatedAt: S.integer({ min: 0 }).def(0)
  });

  var ToolStateSchema = S.object({
    tool: S.string({ min: 1, max: 64 }),
    data: S.jsonBlob(32 * 1024).def({}),
    updatedAt: S.integer({ min: 0 }).def(0)
  });

  /* The export envelope. `LockerSchema` is the whole locker as one document —
     it is what export writes and what import must satisfy before a single
     record is committed. */
  var LockerSchema = S.object({
    format: S.oneOf([EXPORT_FORMAT]),
    version: S.integer({ min: 1, max: EXPORT_VERSION }),
    exportedAt: S.integer({ min: 0 }).def(0),
    profile: UserProfileSchema.nullable().def(null),
    bags: S.arrayOf(BagSchema, { max: 50 }).def([]),
    rounds: S.arrayOf(RoundSchema, { max: 500 }).def([]),
    toolState: S.arrayOf(ToolStateSchema, { max: 50 }).def([]),
    sessions: S.arrayOf(RangeSessionSchema, { max: 200 }).def([]),
    scorecards: S.arrayOf(ScorecardSchema, { max: 500 }).def([])
  });

  /* ========================================================= HELPERS ====== */

  function now() { return Date.now(); }

  function uid(prefix) {
    return (prefix || 'id') + '-' + now().toString(36) + '-' +
      Math.floor(Math.random() * 1e9).toString(36);
  }

  /* Inputs are DOM strings. Empty means "not provided", not zero. */
  function toNum(v) {
    if (v === null || v === undefined) return null;
    var s = String(v).replace(/^\s+|\s+$/g, '');
    if (s === '') return null;
    var n = parseFloat(s);
    return isFinite(n) ? n : null;
  }

  function toInt(v) {
    var n = toNum(v);
    return n === null ? null : Math.round(n);
  }

  function errText(errors) {
    var parts = [];
    for (var i = 0; i < errors.length && i < 4; i++) {
      parts.push(errors[i].path.replace(/^\$\.?/, '') + ' ' + errors[i].message);
    }
    if (errors.length > 4) parts.push('and ' + (errors.length - 4) + ' more');
    return parts.join('; ');
  }

  /* ======================================================== ADAPTERS ====== */
  /* Both adapters expose the same promise API, so nothing above this line
     needs to know which one is live. */

  function IDBAdapter(db) {
    this.db = db;
    this.kind = 'indexeddb';
  }

  IDBAdapter.prototype._tx = function (store, mode, run) {
    var self = this;
    return new Promise(function (resolve, reject) {
      var tx, os, req;
      try {
        tx = self.db.transaction(store, mode);
        os = tx.objectStore(store);
        req = run(os);
      } catch (e) { reject(e); return; }
      tx.onabort = function () { reject(tx.error || new Error('transaction aborted')); };
      tx.onerror = function () { reject(tx.error || new Error('transaction failed')); };
      /* Resolve on complete, not on request success: only complete means the
         write is actually durable. */
      tx.oncomplete = function () { resolve(req ? req.result : undefined); };
    });
  };

  IDBAdapter.prototype.getAll = function (store) {
    return this._tx(store, 'readonly', function (os) { return os.getAll(); })
      .then(function (r) { return r || []; });
  };
  IDBAdapter.prototype.get = function (store, key) {
    return this._tx(store, 'readonly', function (os) { return os.get(key); })
      .then(function (r) { return r === undefined ? null : r; });
  };
  IDBAdapter.prototype.put = function (store, rec) {
    return this._tx(store, 'readwrite', function (os) { return os.put(rec); });
  };
  IDBAdapter.prototype.putAll = function (store, recs) {
    return this._tx(store, 'readwrite', function (os) {
      var last;
      for (var i = 0; i < recs.length; i++) last = os.put(recs[i]);
      return last;
    });
  };
  IDBAdapter.prototype.del = function (store, key) {
    return this._tx(store, 'readwrite', function (os) { return os['delete'](key); });
  };
  IDBAdapter.prototype.clear = function (store) {
    return this._tx(store, 'readwrite', function (os) { return os.clear(); });
  };

  /* Fallback: the whole locker as one localStorage document. Same API, far
     less capable, but it keeps the tools working where IDB is unavailable. */
  function MirrorAdapter() {
    this.kind = 'localstorage';
    this.mem = null;
  }

  MirrorAdapter.prototype._read = function () {
    if (this.mem) return this.mem;
    var doc = null;
    try { doc = JSON.parse(root.localStorage.getItem(MIRROR_KEY) || 'null'); } catch (e) { doc = null; }
    if (!doc || typeof doc !== 'object') doc = {};
    for (var i = 0; i < STORES.length; i++) if (!doc[STORES[i]]) doc[STORES[i]] = {};
    this.mem = doc;
    return doc;
  };

  MirrorAdapter.prototype._write = function () {
    try { root.localStorage.setItem(MIRROR_KEY, JSON.stringify(this.mem)); } catch (e) { /* memory-only from here */ }
    return Promise.resolve();
  };

  MirrorAdapter.prototype._keyOf = function (store, rec) {
    if (store === 'profile') return rec.id;
    if (store === 'toolState') return rec.tool;
    if (store === 'meta') return rec.key;
    /* bags, rounds and sessions are all keyed by id */
    return rec.id;
  };

  MirrorAdapter.prototype.getAll = function (store) {
    var d = this._read()[store], out = [];
    for (var k in d) if (Object.prototype.hasOwnProperty.call(d, k)) out.push(d[k]);
    return Promise.resolve(out);
  };
  MirrorAdapter.prototype.get = function (store, key) {
    var d = this._read()[store];
    return Promise.resolve(Object.prototype.hasOwnProperty.call(d, key) ? d[key] : null);
  };
  MirrorAdapter.prototype.put = function (store, rec) {
    this._read()[store][this._keyOf(store, rec)] = rec;
    return this._write();
  };
  MirrorAdapter.prototype.putAll = function (store, recs) {
    var d = this._read()[store];
    for (var i = 0; i < recs.length; i++) d[this._keyOf(store, recs[i])] = recs[i];
    return this._write();
  };
  MirrorAdapter.prototype.del = function (store, key) {
    delete this._read()[store][key];
    return this._write();
  };
  MirrorAdapter.prototype.clear = function (store) {
    this._read()[store] = {};
    return this._write();
  };

  function openAdapter() {
    return new Promise(function (resolve) {
      var idb = null;
      try { idb = root.indexedDB; } catch (e) { idb = null; }
      if (!idb) { resolve(new MirrorAdapter()); return; }

      var req;
      try { req = idb.open(DB_NAME, DB_VERSION); } catch (e) { resolve(new MirrorAdapter()); return; }

      var settled = false;
      function fallback() { if (!settled) { settled = true; resolve(new MirrorAdapter()); } }

      /* Another tab holding an older version open would stall us forever. */
      req.onblocked = fallback;
      req.onerror = fallback;

      req.onupgradeneeded = function (ev) {
        var db = ev.target.result;
        if (!db.objectStoreNames.contains('profile')) db.createObjectStore('profile', { keyPath: 'id' });
        if (!db.objectStoreNames.contains('bags')) db.createObjectStore('bags', { keyPath: 'id' });
        if (!db.objectStoreNames.contains('rounds')) db.createObjectStore('rounds', { keyPath: 'id' });
        if (!db.objectStoreNames.contains('toolState')) db.createObjectStore('toolState', { keyPath: 'tool' });
        if (!db.objectStoreNames.contains('sessions')) db.createObjectStore('sessions', { keyPath: 'id' });
        if (!db.objectStoreNames.contains('scorecards')) db.createObjectStore('scorecards', { keyPath: 'id' });
        if (!db.objectStoreNames.contains('meta')) db.createObjectStore('meta', { keyPath: 'key' });
      };

      req.onsuccess = function (ev) {
        if (settled) { try { ev.target.result.close(); } catch (e) { } return; }
        settled = true;
        var db = ev.target.result;
        /* If a future version opens elsewhere, close so we never block it. */
        db.onversionchange = function () { try { db.close(); } catch (e) { } };
        resolve(new IDBAdapter(db));
      };

      /* Some privacy modes neither fire success nor error. Do not hang. */
      root.setTimeout(fallback, 3000);
    });
  }

  /* ========================================================== EVENTS ====== */

  var listeners = [];

  function emit(kind) {
    for (var i = 0; i < listeners.length; i++) {
      try { listeners[i](kind); } catch (e) { /* a bad listener must not break a write */ }
    }
  }

  /* ============================================================ CORE ====== */

  var adapter = null;
  var readyPromise = null;

  function ready() {
    if (readyPromise) return readyPromise;
    readyPromise = openAdapter()
      .then(function (a) { adapter = a; return migrateLegacy(); })
      .then(function () { return adapter; })
      .catch(function () {
        /* Last resort: never let a storage fault reject into tool code. */
        adapter = new MirrorAdapter();
        return adapter;
      });
    return readyPromise;
  }

  function validated(schema, value, label) {
    var r = schema.parse(value, '$');
    if (!r.ok) throw new Error((label || 'record') + ' rejected: ' + errText(r.errors));
    return r.value;
  }

  /* --------------------------------------------------------------- profile */

  function getProfile() {
    return ready().then(function (a) { return a.get('profile', 'me'); }).then(function (rec) {
      var r = UserProfileSchema.parse(rec || { id: 'me' }, '$');
      /* A corrupt profile falls back to defaults rather than blocking the UI. */
      return r.ok ? r.value : UserProfileSchema.parse({ id: 'me' }, '$').value;
    });
  }

  function saveProfile(patch) {
    return getProfile().then(function (cur) {
      var next = S.clone(cur);
      for (var k in patch) if (Object.prototype.hasOwnProperty.call(patch, k)) next[k] = patch[k];
      next.id = 'me';
      next.createdAt = cur.createdAt || now();
      next.updatedAt = now();
      var rec = validated(UserProfileSchema, next, 'Profile');
      return ready().then(function (a) { return a.put('profile', rec); }).then(function () {
        emit('profile');
        return rec;
      });
    });
  }

  /* ------------------------------------------------------------------ bags */

  function listBags() {
    return ready().then(function (a) { return a.getAll('bags'); }).then(function (recs) {
      var out = [];
      for (var i = 0; i < recs.length; i++) {
        var r = BagSchema.parse(recs[i], '$');
        if (r.ok) out.push(r.value);
      }
      out.sort(function (x, y) { return (y.updatedAt || 0) - (x.updatedAt || 0); });
      return out;
    });
  }

  function saveBag(bag) {
    var next = S.clone(bag || {});
    if (!next.id) next.id = uid('bag');
    if (!next.name) next.name = 'My Bag';
    next.createdAt = next.createdAt || now();
    next.updatedAt = now();
    var rec = validated(BagSchema, next, 'Bag');
    return ready().then(function (a) { return a.put('bags', rec); }).then(function () {
      emit('bags');
      return rec;
    });
  }

  function deleteBag(id) {
    return ready().then(function (a) { return a.del('bags', id); }).then(function () { emit('bags'); });
  }

  /* The bag the tools read and write by default. Created on first use so a
     first-time reader never sees an empty-state dead end. */
  function getActiveBag() {
    return Promise.all([getProfile(), listBags()]).then(function (res) {
      var profile = res[0], bags = res[1];
      if (profile.activeBagId) {
        for (var i = 0; i < bags.length; i++) if (bags[i].id === profile.activeBagId) return bags[i];
      }
      if (bags.length) return bags[0];
      return null;
    });
  }

  function setActiveBag(id) { return saveProfile({ activeBagId: id }); }

  /* Upsert the active bag's clubs — the write path for Tool #07. */
  function saveActiveBagClubs(clubs) {
    return getActiveBag().then(function (bag) {
      var next = bag ? S.clone(bag) : { id: uid('bag'), name: 'My Bag', createdAt: now() };
      next.clubs = clubs;
      return saveBag(next).then(function (rec) {
        if (!bag) return setActiveBag(rec.id).then(function () { return rec; });
        return rec;
      });
    });
  }

  /* ---------------------------------------------------------------- rounds */

  function listRounds() {
    return ready().then(function (a) { return a.getAll('rounds'); }).then(function (recs) {
      var out = [];
      for (var i = 0; i < recs.length; i++) {
        var r = RoundSchema.parse(recs[i], '$');
        if (r.ok) out.push(r.value);
      }
      out.sort(function (x, y) { return (x.seq || 0) - (y.seq || 0); });
      return out;
    });
  }

  /* The handicap tool owns the whole list, so replace rather than merge. */
  function saveRounds(rows) {
    var recs = [], t = now();
    for (var i = 0; i < rows.length && i < MAX_ROUNDS; i++) {
      var src = rows[i] || {};
      recs.push(validated(RoundSchema, {
        id: src.id || uid('rnd'),
        seq: i,
        score: src.score === undefined ? null : src.score,
        cr: src.cr === undefined ? null : src.cr,
        slope: src.slope === undefined ? null : src.slope,
        updatedAt: t
      }, 'Round ' + (i + 1)));
    }
    return ready()
      .then(function (a) { return a.clear('rounds').then(function () { return a.putAll('rounds', recs); }); })
      .then(function () { emit('rounds'); return recs; });
  }

  function clearRounds() {
    return ready().then(function (a) { return a.clear('rounds'); }).then(function () { emit('rounds'); });
  }

  /* -------------------------------------------------------------- sessions */
  /* A range session is one visit to the mat: a set of clubs, each with the
     carry yardages hit in entry order. The logger rewrites the whole session
     document on every shot, which is cheap (14 clubs x 50 shots at most) and
     removes any chance of a partial write leaving a club out of step. */

  function listSessions() {
    return ready().then(function (a) { return a.getAll('sessions'); }).then(function (recs) {
      var out = [];
      for (var i = 0; i < recs.length; i++) {
        var r = RangeSessionSchema.parse(recs[i], '$');
        if (r.ok) out.push(r.value);
      }
      out.sort(function (x, y) { return (y.startedAt || 0) - (x.startedAt || 0); });
      return out;
    });
  }

  function getSession(id) {
    return ready().then(function (a) { return a.get('sessions', id); }).then(function (rec) {
      if (!rec) return null;
      var r = RangeSessionSchema.parse(rec, '$');
      return r.ok ? r.value : null;
    });
  }

  function saveSession(session) {
    var next = S.clone(session || {});
    if (!next.id) next.id = uid('ses');
    next.startedAt = next.startedAt || now();
    next.updatedAt = now();
    var rec = validated(RangeSessionSchema, next, 'Session');
    return ready().then(function (a) { return a.put('sessions', rec); }).then(function () {
      emit('sessions');
      return rec;
    });
  }

  function deleteSession(id) {
    return ready().then(function (a) { return a.del('sessions', id); }).then(function () { emit('sessions'); });
  }

  /* The session the logger is currently filling: the newest one started today,
     otherwise a fresh one. Sessions are never implicitly merged across days —
     a bag gapped in July should not be averaged with one gapped in December. */
  function getOrStartSession() {
    return listSessions().then(function (all) {
      var dayStart = new Date();
      dayStart.setHours(0, 0, 0, 0);
      var floor = dayStart.getTime();
      for (var i = 0; i < all.length; i++) {
        if ((all[i].startedAt || 0) >= floor) return all[i];
      }
      return saveSession({ id: uid('ses'), label: '', clubs: [], startedAt: now() });
    });
  }

  /* ----------------------------------------------------------- scorecards */
  /* A scorecard is one played round, tapped in afterwards: par, score, tee
     result, approach result and putts for each hole. Kept apart from `rounds`
     on purpose (see the DB_VERSION note above) — that store belongs to the
     Handicap Lie Detector and is cleared wholesale on every write. */

  function listScorecards() {
    return ready().then(function (a) { return a.getAll('scorecards'); }).then(function (recs) {
      var out = [];
      for (var i = 0; i < recs.length; i++) {
        var r = ScorecardSchema.parse(recs[i], '$');
        if (r.ok) out.push(r.value);
      }
      out.sort(function (x, y) { return (y.playedAt || 0) - (x.playedAt || 0); });
      return out;
    });
  }

  function getScorecard(id) {
    return ready().then(function (a) { return a.get('scorecards', id); }).then(function (rec) {
      if (!rec) return null;
      var r = ScorecardSchema.parse(rec, '$');
      return r.ok ? r.value : null;
    });
  }

  function saveScorecard(card) {
    var next = S.clone(card || {});
    if (!next.id) next.id = uid('card');
    next.playedAt = next.playedAt || now();
    next.updatedAt = now();
    var rec = validated(ScorecardSchema, next, 'Scorecard');
    return ready().then(function (a) { return a.put('scorecards', rec); }).then(function () {
      emit('scorecards');
      return rec;
    });
  }

  function deleteScorecard(id) {
    return ready().then(function (a) { return a.del('scorecards', id); })
      .then(function () { emit('scorecards'); });
  }

  /* A card counts as finished once every hole has a score. Anything else is a
     draft the reader can walk back into. */
  function scorecardComplete(card) {
    if (!card || !card.holes || card.holes.length < HOLES) return false;
    for (var i = 0; i < card.holes.length; i++) {
      if (card.holes[i].score === null || card.holes[i].score === undefined) return false;
    }
    return true;
  }

  /* Resume the newest unfinished card, otherwise report none. Deliberately not
     "start one automatically": an empty card created by merely visiting the
     page would pollute the trend history. */
  function getDraftScorecard() {
    return listScorecards().then(function (all) {
      for (var i = 0; i < all.length; i++) {
        if (!scorecardComplete(all[i])) return all[i];
      }
      return null;
    });
  }

  function listCompletedScorecards() {
    return listScorecards().then(function (all) {
      var out = [];
      for (var i = 0; i < all.length; i++) if (scorecardComplete(all[i])) out.push(all[i]);
      return out;
    });
  }

  /* Hand scores to the Handicap Lie Detector. Merges rather than replaces:
     saveRounds() clears the store, so anything typed by hand there would be
     lost if this simply wrote its own list. Scores already present are left
     alone so repeated presses cannot duplicate a round. */
  function pushScoresToRounds(scores) {
    return listRounds().then(function (existing) {
      var rows = [], seen = {}, i;
      for (i = 0; i < existing.length; i++) {
        rows.push({ score: existing[i].score, cr: existing[i].cr, slope: existing[i].slope });
        if (existing[i].score !== null) seen[existing[i].score] = (seen[existing[i].score] || 0) + 1;
      }
      var added = 0;
      for (i = 0; i < scores.length && rows.length < MAX_ROUNDS; i++) {
        var sc = scores[i];
        if (sc === null || sc === undefined) continue;
        if (seen[sc]) { seen[sc]--; continue; }   /* already on the card */
        rows.push({ score: sc, cr: null, slope: null });
        added++;
      }
      return saveRounds(rows).then(function () { return { added: added, total: rows.length }; });
    });
  }

  /* ------------------------------------------------------------- toolState */

  function getToolState(tool) {
    return ready().then(function (a) { return a.get('toolState', tool); }).then(function (rec) {
      if (!rec) return null;
      var r = ToolStateSchema.parse(rec, '$');
      return r.ok ? r.value.data : null;
    });
  }

  function setToolState(tool, data) {
    var rec = validated(ToolStateSchema, { tool: tool, data: data || {}, updatedAt: now() }, 'Tool state');
    return ready().then(function (a) { return a.put('toolState', rec); }).then(function () {
      emit('toolState');
      return rec;
    });
  }

  /* ================================================= LEGACY MIGRATION ===== */
  /* Readers already have data under the old per-tool localStorage keys. Move
     it across once, keyed by a meta flag. The old keys are deliberately left
     alone: a cached copy of an older page still reads them. */

  var LEGACY_BAG = 'golfraw_bag_audit';
  var LEGACY_ROUNDS = 'golfraw_handicap_rounds';
  var LEGACY_PLAYSLIKE = 'golfraw_playslike';

  function lsGet(key) {
    try { return root.localStorage.getItem(key); } catch (e) { return null; }
  }

  function migrateLegacy() {
    return adapter.get('meta', 'legacyMigrated').then(function (flag) {
      if (flag && flag.value) return null;

      /* Everything below talks to `adapter` directly, never through the public
         API: those helpers await ready(), and ready() is awaiting this
         function. Profile fields are collected into one patch and written
         once, so the bag and rounds migrations cannot race each other. */
      var jobs = [];
      var profilePatch = { id: 'me', createdAt: now(), updatedAt: now() };
      var profileTouched = false;

      /* Bag: [[name, carry, usage, conf], ...] as raw input strings. */
      var rawBag = lsGet(LEGACY_BAG);
      if (rawBag) {
        try {
          var arr = JSON.parse(rawBag);
          if (S.isArray(arr)) {
            var clubs = [];
            for (var i = 0; i < arr.length && i < MAX_CLUBS; i++) {
              var row = arr[i];
              if (!S.isArray(row)) continue;
              var name = String(row[0] === undefined || row[0] === null ? '' : row[0]).replace(/^\s+|\s+$/g, '');
              var carry = toNum(row[1]);
              if (!name && carry === null) continue;
              var parsed = ClubSchema.parse({
                name: name.slice(0, 40),
                carry: carry,
                usage: toInt(row[2]),
                conf: toInt(row[3]) === null ? 3 : Math.min(5, Math.max(1, toInt(row[3])))
              }, '$');
              if (parsed.ok) clubs.push(parsed.value);
            }
            if (clubs.length) {
              var bagId = uid('bag');
              var bagRec = BagSchema.parse({
                id: bagId, name: 'My Bag', clubs: clubs, createdAt: now(), updatedAt: now()
              }, '$');
              if (bagRec.ok) {
                jobs.push(adapter.put('bags', bagRec.value));
                profilePatch.activeBagId = bagId;
                profileTouched = true;
              }
            }
          }
        } catch (e) { /* a corrupt legacy blob is dropped, not fatal */ }
      }

      /* Rounds: { claimed, rows:[{score, cr, slope}] } as raw input strings. */
      var rawRounds = lsGet(LEGACY_ROUNDS);
      if (rawRounds) {
        try {
          var d = JSON.parse(rawRounds);
          if (d && S.isArray(d.rows)) {
            var recs = [];
            for (var j = 0; j < d.rows.length && j < MAX_ROUNDS; j++) {
              var r0 = d.rows[j] || {};
              var pr = RoundSchema.parse({
                id: uid('rnd'), seq: recs.length,
                score: toInt(r0.score), cr: toNum(r0.cr), slope: toInt(r0.slope),
                updatedAt: now()
              }, '$');
              if (pr.ok) recs.push(pr.value);
            }
            if (recs.length) jobs.push(adapter.putAll('rounds', recs));
            var claimed = toNum(d.claimed);
            if (claimed !== null && claimed >= -10 && claimed <= 54) {
              profilePatch.claimedHandicap = claimed;
              profileTouched = true;
            }
          }
        } catch (e) { /* ignore */ }
      }

      /* Plays Like: free-form conditions, kept as tool state verbatim. */
      var rawPL = lsGet(LEGACY_PLAYSLIKE);
      if (rawPL) {
        try {
          var pl = JSON.parse(rawPL);
          if (S.isPlainObject(pl)) {
            var ts = ToolStateSchema.parse({ tool: 'plays-like', data: pl, updatedAt: now() }, '$');
            if (ts.ok) jobs.push(adapter.put('toolState', ts.value));
          }
        } catch (e) { /* ignore */ }
      }

      if (profileTouched) {
        var pv = UserProfileSchema.parse(profilePatch, '$');
        if (pv.ok) jobs.push(adapter.put('profile', pv.value));
      }

      return Promise.all(jobs)
        .catch(function () { return null; })
        .then(function () { return adapter.put('meta', { key: 'legacyMigrated', value: true, at: now() }); });
    }).catch(function () { return null; });
  }

  /* ==================================================== EXPORT / IMPORT === */

  function exportLocker() {
    return ready().then(function () {
      return Promise.all([getProfile(), listBags(), listRounds(), adapter.getAll('toolState'), listSessions(), listScorecards()]);
    }).then(function (res) {
      var states = [], raw = res[3];
      for (var i = 0; i < raw.length; i++) {
        var r = ToolStateSchema.parse(raw[i], '$');
        if (r.ok) states.push(r.value);
      }
      var doc = {
        format: EXPORT_FORMAT,
        version: EXPORT_VERSION,
        exportedAt: now(),
        profile: res[0],
        bags: res[1],
        rounds: res[2],
        toolState: states,
        sessions: res[4],
        scorecards: res[5]
      };
      /* Validate our own output: an export that cannot be re-imported is a bug
         we want to catch here, not in the reader's downloads folder. */
      return validated(LockerSchema, doc, 'Export');
    });
  }

  function exportJSON() {
    return exportLocker().then(function (doc) { return JSON.stringify(doc, null, 2); });
  }

  /* mode 'replace' wipes first; 'merge' keeps existing records and overlays
     the file's by key. Nothing is written unless the whole file validates. */
  function importJSON(text, mode) {
    mode = mode === 'replace' ? 'replace' : 'merge';
    return ready().then(function (a) {
      var parsed;
      try { parsed = JSON.parse(text); } catch (e) { throw new Error('That file is not valid JSON.'); }
      if (!S.isPlainObject(parsed)) throw new Error('That file is not a locker backup.');
      if (parsed.format !== EXPORT_FORMAT) throw new Error('That file is not a GOLFRAW locker backup.');
      if (typeof parsed.version === 'number' && parsed.version > EXPORT_VERSION) {
        throw new Error('That backup was written by a newer version of the site.');
      }

      var r = LockerSchema.parse(parsed, '$');
      if (!r.ok) throw new Error('Backup rejected: ' + errText(r.errors));
      var doc = r.value;

      var chain = Promise.resolve();
      if (mode === 'replace') {
        chain = chain.then(function () {
          return Promise.all([a.clear('bags'), a.clear('rounds'), a.clear('toolState'),
            a.clear('sessions'), a.clear('scorecards'), a.clear('profile')]);
        });
      }

      return chain.then(function () {
        var jobs = [];
        if (doc.profile) {
          var p = S.clone(doc.profile);
          p.id = 'me';
          p.updatedAt = now();
          jobs.push(a.put('profile', UserProfileSchema.parse(p, '$').value));
        }
        if (doc.bags.length) jobs.push(a.putAll('bags', doc.bags));
        if (doc.rounds.length) jobs.push(a.putAll('rounds', doc.rounds));
        if (doc.toolState.length) jobs.push(a.putAll('toolState', doc.toolState));
        if (doc.sessions.length) jobs.push(a.putAll('sessions', doc.sessions));
        if (doc.scorecards.length) jobs.push(a.putAll('scorecards', doc.scorecards));
        return Promise.all(jobs);
      }).then(function () {
        emit('import');
        return {
          bags: doc.bags.length,
          rounds: doc.rounds.length,
          toolState: doc.toolState.length,
          sessions: doc.sessions.length,
          scorecards: doc.scorecards.length,
          mode: mode
        };
      });
    });
  }

  function clearAll() {
    return ready().then(function (a) {
      return Promise.all([a.clear('profile'), a.clear('bags'), a.clear('rounds'),
        a.clear('toolState'), a.clear('sessions'), a.clear('scorecards')]);
    }).then(function () { emit('clear'); });
  }

  /* ============================================================ PUBLIC ==== */

  root.GolfrawLocker = {
    ready: ready,
    backend: function () { return adapter ? adapter.kind : null; },

    getProfile: getProfile,
    saveProfile: saveProfile,

    listBags: listBags,
    saveBag: saveBag,
    deleteBag: deleteBag,
    getActiveBag: getActiveBag,
    setActiveBag: setActiveBag,
    saveActiveBagClubs: saveActiveBagClubs,

    listRounds: listRounds,
    saveRounds: saveRounds,
    clearRounds: clearRounds,

    listSessions: listSessions,
    getSession: getSession,
    saveSession: saveSession,
    deleteSession: deleteSession,
    getOrStartSession: getOrStartSession,

    listScorecards: listScorecards,
    listCompletedScorecards: listCompletedScorecards,
    getScorecard: getScorecard,
    saveScorecard: saveScorecard,
    deleteScorecard: deleteScorecard,
    getDraftScorecard: getDraftScorecard,
    scorecardComplete: scorecardComplete,
    pushScoresToRounds: pushScoresToRounds,

    getToolState: getToolState,
    setToolState: setToolState,

    exportLocker: exportLocker,
    exportJSON: exportJSON,
    importJSON: importJSON,
    clearAll: clearAll,

    subscribe: function (fn) {
      listeners.push(fn);
      return function () {
        for (var i = 0; i < listeners.length; i++) {
          if (listeners[i] === fn) { listeners.splice(i, 1); return; }
        }
      };
    },

    /* Exposed for the tool adapters and for tests. */
    util: { uid: uid, toNum: toNum, toInt: toInt, now: now },
    schemas: {
      Club: ClubSchema, Bag: BagSchema, Round: RoundSchema,
      UserProfile: UserProfileSchema, ToolState: ToolStateSchema, Locker: LockerSchema,
      RangeClub: RangeClubSchema, RangeSession: RangeSessionSchema,
      Hole: HoleSchema, Scorecard: ScorecardSchema
    },
    limits: { MAX_CLUBS: MAX_CLUBS, MAX_ROUNDS: MAX_ROUNDS, MAX_SHOTS: MAX_SHOTS, HOLES: HOLES }
  };
})(window);
