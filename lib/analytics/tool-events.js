/* GolfRaw tool events: the one analytics layer every tool page shares.
 *
 * It records what golfers DO with a tool (open it, start, finish, share, move
 * on to another tool), never what they type. Every event passes an allowlist:
 * a known event name, known parameter keys, and values that are registry ids
 * or short lowercase enums. Numbers and free text cannot pass, so scores,
 * handicaps, distances, names, stakes and results never reach analytics.
 *
 * Events ride on the page's existing gtag queue (GA4 G-PMECW4VW66) and so
 * inherit whatever consent state that tag has. Nothing here sets cookies. The
 * one thing it stores, on this device only and never sent, is a flag that the
 * tool is holding sample data (see data-gr-saved). If this file or gtag.js is
 * blocked, tools keep working: pages only call `window.GRTrack && ...`.
 *
 * Page wiring (see scripts/README.md, "Tool events"):
 *   data-gr-inputs          container whose edits count as the golfer starting;
 *                           a value ("import") keeps that mode instead of manual
 *   data-gr-run             run button inside that container (starts, keeps mode)
 *   data-gr-ignore          control inside it that is not a start (reset, copy)
 *   data-gr-mode="sample"   control that loads demo data ("import" for imports);
 *     + data-gr-saved       the tool saves that data, so a reload restores it
 *   data-gr-placement="x"   names where a link to another tool sits
 *   <html data-gr-view="shared_result">  page is showing someone else's result
 *   GRTrack.completed()     call on the valid-result path only
 *   GRTrack.shared(method)  call once a share, copy, download or print succeeds
 */
(function () {
  'use strict';
  if (window.GRTrack) return;

  // slug -> [tool_id, tool_name, access]. Mirrors scripts/tool_inventory.py;
  // tests/test_tool_events.py fails if the two drift apart.
  var TOOLS = {
    'tools-settle-up-calculator': ['settle_up', 'The Settle Up', 'free'],
    'tools-tee-box-check': ['tee_box_check', 'The Tee Box Reality Check', 'free'],
    'tools-plays-like': ['plays_like', 'The Plays Like Calculator', 'free'],
    'tools-bag-audit': ['bag_audit', 'The Bag Audit', 'free'],
    'tools-handicap-detector': ['handicap_detector', 'The Handicap Lie Detector', 'free'],
    'tools-round-autopsy': ['round_autopsy', 'The Round Autopsy', 'free'],
    'tools-tilt-meter': ['tilt_meter', 'The Tilt Meter', 'free'],
    'tools-gimme-audit': ['gimme_audit', 'The Gimme Audit', 'free'],
    'tools-the-grudge-match': ['grudge_match', 'The Grudge Match', 'free'],
    'tools-standing-order': ['standing_order', 'The Standing Order', 'free'],
    'tools-tendency-engine': ['tendency_engine', 'The Tendency Engine', 'free'],
    'tools-field-reader': ['field_reader', 'The Field Reader', 'free'],
    'tools-coach-report': ['coach_report', 'The Coach Report', 'pro_preview']
  };

  // The only events that can be sent, and the only keys each may carry.
  var EVENTS = {
    tool_viewed: ['tool_id', 'tool_name', 'tool_access', 'page_path', 'view_type'],
    tool_started: ['tool_id', 'tool_name', 'input_mode'],
    tool_completed: ['tool_id', 'tool_name', 'input_mode'],
    result_shared: ['tool_id', 'tool_name', 'share_method'],
    related_tool_clicked: ['from_tool', 'to_tool', 'placement'],
    tool_error: ['tool_id', 'error_code']
  };

  // Named now so the taxonomy is agreed before the features exist. track()
  // refuses them: a feature enables its event by moving it into EVENTS with
  // its own key allowlist, in the same change that ships the feature.
  var RESERVED = [
    'round_logged', 'round_history_opened', 'pro_preview_viewed',
    'pro_waitlist_clicked', 'pro_waitlist_joined', 'review_ready', 'review_unlocked'
  ];

  var ENUMS = {
    input_mode: ['manual', 'sample', 'import'],
    share_method: ['copy_link', 'native_share', 'download', 'print', 'copy_result'],
    tool_access: ['free', 'pro_preview'],
    view_type: ['tool', 'shared_result']
  };
  var TOKEN = /^[a-z][a-z0-9_]{0,39}$/;       // placement, error_code
  // Controls inside an input container that are never a start. Pro gate buttons
  // belong to the reserved pro_* events, not to the tool they cover.
  var NOT_A_START = '[data-gr-ignore], [data-pro-open], [data-pro-restore], [data-pro-send]';
  var TOOL_IDS = {};
  Object.keys(TOOLS).forEach(function (slug) { TOOL_IDS[TOOLS[slug][0]] = slug; });

  // Own properties only: "constructor" or "hasOwnProperty" must never pass as
  // an event name or a tool id.
  function has(obj, key) {
    return typeof key === 'string' && Object.prototype.hasOwnProperty.call(obj, key);
  }

  function slugFor(path) {
    var m = /^\/?(tools-[a-z0-9-]+?)(?:\.html)?\/?$/.exec(path || '');
    return m && has(TOOLS, m[1]) ? m[1] : null;
  }

  function valid(key, value) {
    if (typeof value !== 'string') return false;
    if (has(ENUMS, key)) return ENUMS[key].indexOf(value) !== -1;
    if (key === 'tool_id' || key === 'from_tool' || key === 'to_tool') return has(TOOL_IDS, value);
    if (key === 'tool_name') return Object.keys(TOOLS).some(function (s) { return TOOLS[s][1] === value; });
    if (key === 'page_path') return !!slugFor(value);
    return TOKEN.test(value);
  }

  function sanitize(name, params) {
    if (!has(EVENTS, name)) return null;
    var keys = EVENTS[name];
    var out = {};
    for (var i = 0; i < keys.length; i++) {
      if (params && valid(keys[i], params[keys[i]])) out[keys[i]] = params[keys[i]];
    }
    return out;
  }

  var slug = slugFor(location.pathname);
  var tool = slug ? { slug: slug, id: TOOLS[slug][0], name: TOOLS[slug][1], access: TOOLS[slug][2] } : null;
  var debug = /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
  try { debug = debug || window.localStorage.getItem('gr_track_debug') === '1'; } catch (e) { /* storage blocked */ }

  var log = [];
  var mode = 'manual';
  var started = {}, completed = {}, errors = {};
  var completedAny = false, viewed = false;

  // A tool that saves what its sample button loads restores that demo data on
  // the next visit; without this flag a Run after a reload would count as the
  // golfer's own data. Local only, never sent, cleared by the first real edit.
  var sampleKey = tool ? 'gr_track_sample:' + tool.id : null;
  function rememberSample(on) {
    if (!sampleKey) return;
    try {
      if (on) window.localStorage.setItem(sampleKey, '1');
      else window.localStorage.removeItem(sampleKey);
    } catch (e) { /* storage blocked: the mode just resets on reload */ }
  }
  try { if (sampleKey && window.localStorage.getItem(sampleKey) === '1') mode = 'sample'; } catch (e) { /* ignore */ }

  function setMode(next) {
    if (next === mode) return;
    if (mode === 'sample') rememberSample(false);
    mode = next;
  }

  function send(name, params) {
    var clean = sanitize(name, params);
    if (!clean) return false;
    if (debug) clean.debug_mode = true;
    log.push({ event: name, params: clean });
    if (log.length > 50) log.shift();
    try {
      // Same queue the page's gtag() writes to; gtag.js drains it when loaded.
      window.dataLayer = window.dataLayer || [];
      (function () { window.dataLayer.push(arguments); })('event', name, clean);
    } catch (e) { /* analytics must never break a tool */ }
    return true;
  }

  function base() {
    return { tool_id: tool.id, tool_name: tool.name };
  }

  function start() {
    if (!tool || started[mode]) return;
    view();   // a golfer acting on the page has seen it, even if it opened in the background
    started[mode] = true;
    var p = base(); p.input_mode = mode;
    send('tool_started', p);
  }

  var api = {
    version: 1,
    tool: tool ? { id: tool.id, name: tool.name } : null,

    /** Say where the data now in the tool came from: manual, sample or import. */
    inputMode: function (next) {
      if (ENUMS.input_mode.indexOf(next) !== -1) setMode(next);
    },

    /** The golfer acted on the tool. Once per input mode per page view. */
    started: start,

    /** A valid result is on screen. Once per input mode per page view, so
     *  recalculating, live re-renders and Save-reruns are not new completions. */
    completed: function () {
      if (!tool) return;
      start();
      completedAny = true;
      if (completed[mode]) return;
      completed[mode] = true;
      var p = base(); p.input_mode = mode;
      send('tool_completed', p);
    },

    /** A share, copy, download or print succeeded. Only counts once a result
     *  exists in this page view, so copying an empty card is not a share. */
    shared: function (method) {
      if (!tool || !completedAny || ENUMS.share_method.indexOf(method) === -1) return;
      var p = base(); p.share_method = method;
      send('result_shared', p);
    },

    /** A meaningful product failure, as a fixed code. Once per code per view. */
    error: function (code) {
      if (!tool || errors[code] || !TOKEN.test(code || '')) return;
      errors[code] = true;
      send('tool_error', { tool_id: tool.id, error_code: code });
    },

    /** Generic entry for events added later; refuses anything not in EVENTS. */
    track: function (name, params) {
      if (!has(EVENTS, name) || RESERVED.indexOf(name) !== -1) return false;
      return send(name, params || {});
    },

    /** Sanitised copies of what this page sent, for tests and debugging. */
    events: function () { return log.map(function (e) { return { event: e.event, params: e.params }; }); }
  };
  window.GRTrack = api;
  if (!tool) return;

  function view() {
    if (viewed) return;
    viewed = true;
    var shown = document.documentElement.getAttribute('data-gr-view') === 'shared_result' ? 'shared_result' : 'tool';
    send('tool_viewed', {
      tool_id: tool.id, tool_name: tool.name, tool_access: tool.access,
      page_path: '/' + tool.slug, view_type: shown
    });
  }

  function closest(el, selector) {
    return el && el.nodeType === 1 && el.closest ? el.closest(selector) : null;
  }

  // Mode an edit inside this input container implies: manual unless the
  // container says its data comes from elsewhere (data-gr-inputs="import").
  function editMode(container) {
    var declared = container.getAttribute('data-gr-inputs');
    return ENUMS.input_mode.indexOf(declared) !== -1 ? declared : 'manual';
  }

  // Edits the golfer makes. Capture phase, so mode is set before the page's own
  // handlers run (a sample button that auto-calculates, a live re-render).
  function onEdit(e) {
    if (!e.isTrusted) return;
    var field = closest(e.target, 'input, select, textarea');
    var container = closest(field, '[data-gr-inputs]');
    if (!container || closest(field, NOT_A_START)) return;
    setMode(editMode(container));
    start();
  }

  function onClick(e) {
    if (!e.isTrusted) return;
    var t = e.target;

    var source = closest(t, '[data-gr-mode]');
    if (source) {
      api.inputMode(source.getAttribute('data-gr-mode'));
      if (mode === 'sample' && source.hasAttribute('data-gr-saved')) rememberSample(true);
      start();
      return;
    }

    var link = closest(t, 'a[href]');
    if (link) {
      var url;
      try { url = new URL(link.getAttribute('href'), location.href); } catch (err) { return; }
      var target = url.origin === location.origin ? slugFor(url.pathname) : null;
      if (target && target !== tool.slug && !closest(link, 'header, nav, footer')) {
        var placement = closest(link, '#gr-lk-panel') ? 'locker_drawer' : '';
        var marked = closest(link, '[data-gr-placement]');
        if (marked) placement = marked.getAttribute('data-gr-placement');
        send('related_tool_clicked', {
          from_tool: tool.id, to_tool: TOOLS[target][0], placement: placement || 'tool_body'
        });
      }
      return;
    }

    // Buttons only: a click on a <label> just focuses a field (a checkbox it
    // toggles fires its own change event, handled above).
    var control = closest(t, 'button, [role="button"]');
    var container = closest(control, '[data-gr-inputs]');
    if (!container || closest(control, NOT_A_START)) return;
    if (!closest(control, '[data-gr-run]')) setMode(editMode(container));
    start();
  }

  document.addEventListener('input', onEdit, true);
  document.addEventListener('change', onEdit, true);
  document.addEventListener('click', onClick, true);

  // Uncaught exceptions from GolfRaw's own scripts. Cross-origin errors (ads,
  // gtag) carry no filename and are ignored; no message or stack is ever sent.
  window.addEventListener('error', function (e) {
    if (e && typeof e.filename === 'string' && e.filename.indexOf(location.origin + '/') === 0) {
      api.error('uncaught_exception');
    }
  });

  if (document.visibilityState === 'visible') {
    view();
  } else {
    document.addEventListener('visibilitychange', function onShow() {
      if (document.visibilityState !== 'visible') return;
      document.removeEventListener('visibilitychange', onShow);
      view();
    });
  }
})();
