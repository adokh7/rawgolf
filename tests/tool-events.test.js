'use strict';

// Runs lib/analytics/tool-events.js against a stub page and checks what it
// would hand to GA4. The allowlist is the privacy guarantee, so it is tested
// directly: values that are not ids or enums must never reach the dataLayer.

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const source = fs.readFileSync(path.join(__dirname, '..', 'lib', 'analytics', 'tool-events.js'), 'utf8');
const failures = [];

function check(condition, message) {
  if (!condition) failures.push(message);
}

function page(pathname, opts) {
  opts = opts || {};
  const listeners = {};
  const htmlAttrs = Object.assign({}, opts.htmlAttrs);
  const store = opts.storage || {};
  const window = {
    dataLayer: [],
    localStorage: {
      getItem: (k) => (k in store ? store[k] : null),
      setItem: (k, v) => { store[k] = String(v); },
      removeItem: (k) => { delete store[k]; }
    },
    addEventListener: (type, fn) => { (listeners['window:' + type] = listeners['window:' + type] || []).push(fn); }
  };
  const document = {
    visibilityState: opts.hidden ? 'hidden' : 'visible',
    documentElement: { getAttribute: (k) => (k in htmlAttrs ? htmlAttrs[k] : null) },
    addEventListener: (type, fn) => { (listeners[type] = listeners[type] || []).push(fn); },
    removeEventListener: () => {}
  };
  const location = { pathname, hostname: 'www.golfraw.com', origin: 'https://www.golfraw.com', href: 'https://www.golfraw.com' + pathname };
  window.window = window;
  window.document = document;
  window.location = location;
  vm.runInNewContext(source, Object.assign(window, { URL }));
  const events = () => window.dataLayer.map((args) => ({ event: args[1], params: args[2] }));
  return { GRTrack: window.GRTrack, events, listeners, window, store };
}

// Minimal element stub: `inside` lists the selectors this element sits in.
function el(attrs, inside) {
  const self = {
    nodeType: 1,
    getAttribute: (k) => (k in attrs ? attrs[k] : null),
    hasAttribute: (k) => k in attrs,
    closest: (sel) => (inside[sel] === undefined ? null : (inside[sel] || self))
  };
  return self;
}

function fire(p, type, target) {
  (p.listeners[type] || []).forEach((fn) => fn({ isTrusted: true, target }));
}

function names(p) {
  return p.events().map((e) => e.event + (e.params.input_mode ? ':' + e.params.input_mode : ''));
}

// 1. A tool page fires exactly one tool_viewed with ids only.
{
  const p = page('/tools-bag-audit');
  const viewed = p.events();
  check(viewed.length === 1 && viewed[0].event === 'tool_viewed', 'tool_viewed fires once on load');
  const v = viewed[0].params;
  check(v.tool_id === 'bag_audit' && v.tool_name === 'The Bag Audit' && v.page_path === '/tools-bag-audit' &&
    v.view_type === 'tool' && v.tool_access === 'free', 'tool_viewed carries registry values only');
}

// 2. Completion implies a start, and repeats are deduped per input mode.
{
  const p = page('/tools-tilt-meter.html');
  p.GRTrack.completed();
  p.GRTrack.completed();
  p.GRTrack.completed();
  check(JSON.stringify(names(p)) === JSON.stringify(['tool_viewed', 'tool_started:manual', 'tool_completed:manual']),
    'completed() starts once and completes once per mode: ' + names(p).join(','));
}

// 3. Sample and manual completions stay separate.
{
  const p = page('/tools-bag-audit');
  p.GRTrack.inputMode('sample');
  p.GRTrack.started();
  p.GRTrack.completed();
  p.GRTrack.inputMode('manual');
  p.GRTrack.completed();
  check(JSON.stringify(names(p).slice(1)) === JSON.stringify([
    'tool_started:sample', 'tool_completed:sample', 'tool_started:manual', 'tool_completed:manual'
  ]), 'sample and manual runs are recorded separately: ' + names(p).join(','));
}

// 4. A share before any result in this page view is not a share.
{
  const p = page('/tools-settle-up-calculator');
  p.GRTrack.shared('copy_result');
  check(!p.events().some((e) => e.event === 'result_shared'), 'no result_shared before a completion');
  p.GRTrack.completed();
  p.GRTrack.shared('copy_result');
  p.GRTrack.shared('screenshot');
  const shares = p.events().filter((e) => e.event === 'result_shared');
  check(shares.length === 1 && shares[0].params.share_method === 'copy_result', 'only known share methods are sent');
}

// 5. Private values cannot pass the allowlist.
{
  const p = page('/tools-handicap-detector');
  p.GRTrack.track('tool_started', { tool_id: 'handicap_detector', input_mode: 'manual', score: 91, handicap: '14.2', name: 'Dave' });
  p.GRTrack.track('related_tool_clicked', { from_tool: 'handicap_detector', to_tool: 'bag_audit', placement: 'Dave 247 yds' });
  p.GRTrack.track('tool_error', { tool_id: 'handicap_detector', error_code: 'score 91 out of range' });
  p.GRTrack.error('Bad Value 14');
  const sent = JSON.stringify(p.events());
  check(!/91|14\.2|Dave|247/.test(sent), 'numbers and free text never reach the dataLayer: ' + sent);
  const started = p.events().find((e) => e.event === 'tool_started');
  check(started && Object.keys(started.params).sort().join() === 'input_mode,tool_id', 'unknown keys are dropped');
}

// 6. Reserved future events are refused until a feature enables them.
{
  const p = page('/tools-tendency-engine');
  const before = p.events().length;
  check(p.GRTrack.track('round_logged', {}) === false, 'round_logged is reserved');
  check(p.GRTrack.track('pro_waitlist_joined', {}) === false, 'pro_waitlist_joined is reserved');
  check(p.GRTrack.track('made_up_event', {}) === false, 'unknown events are refused');
  check(p.events().length === before, 'reserved and unknown events send nothing');
}

// 7. Errors are fixed codes, once per code per page view.
{
  const p = page('/tools-standing-order');
  p.GRTrack.error('import_unreadable');
  p.GRTrack.error('import_unreadable');
  const errs = p.events().filter((e) => e.event === 'tool_error');
  check(errs.length === 1 && errs[0].params.error_code === 'import_unreadable', 'tool_error is deduped per code');
}

// 8. Shared-result views are labelled, and non-tool pages send nothing.
{
  const p = page('/tools-coach-report', { htmlAttrs: { 'data-gr-view': 'shared_result' } });
  check(p.events()[0].params.view_type === 'shared_result', 'a shared report view is labelled shared_result');
  const q = page('/news-2026-some-article');
  q.GRTrack.completed();
  check(q.events().length === 0 && q.GRTrack.tool === null, 'non-tool pages send nothing');
}

// 9. Page-level data never rides along: no location, URL or storage values.
{
  const p = page('/tools-plays-like');
  p.GRTrack.completed();
  const sent = JSON.stringify(p.events());
  check(!/https?:|golfraw\.com|localStorage/.test(sent), 'no URLs or storage contents in params');
}

// 10. Inherited object names are not events or tool ids.
{
  const p = page('/tools-bag-audit');
  const before = p.events().length;
  check(p.GRTrack.track('hasOwnProperty', {}) === false, 'hasOwnProperty is not an event');
  check(p.GRTrack.track('constructor', { undefined: 'zzz' }) === false, 'constructor is not an event');
  p.GRTrack.track('related_tool_clicked', { from_tool: 'constructor', to_tool: 'toString', placement: 'x' });
  const sent = JSON.stringify(p.events().slice(before));
  check(!/constructor|toString|zzz/.test(sent), 'inherited names never pass as values: ' + sent);
}

// 11. Sample data a tool saved is still sample after a reload, until a real edit.
{
  const storage = {};
  const first = page('/tools-bag-audit', { storage });
  const sampleBtn = el({ 'data-gr-mode': 'sample', 'data-gr-saved': '' }, { '[data-gr-mode]': null });
  fire(first, 'click', sampleBtn);
  check(storage['gr_track_sample:bag_audit'] === '1', 'a saved sample load is remembered locally');

  const reload = page('/tools-bag-audit', { storage });
  reload.GRTrack.completed();
  check(names(reload).includes('tool_completed:sample'), 'a Run after reload on restored sample data counts as sample');

  const container = el({ 'data-gr-inputs': '' }, {});
  const field = el({}, { 'input, select, textarea': null, '[data-gr-inputs]': container });
  fire(reload, 'input', field);
  reload.GRTrack.completed();
  check(names(reload).includes('tool_completed:manual'), 'a real edit switches to manual');
  check(!('gr_track_sample:bag_audit' in storage), 'the first real edit clears the sample flag');
  check(!JSON.stringify(reload.events()).includes('gr_track_sample'), 'the flag is never sent');
}

// 12. A label click is not a start; buttons in the input panel are.
{
  const p = page('/tools-gimme-audit');
  const container = el({ 'data-gr-inputs': '' }, {});
  const label = el({}, { '[data-gr-inputs]': container });
  fire(p, 'click', label);
  check(!names(p).some((n) => n.startsWith('tool_started')), 'clicking a label does not start the tool');
  const chip = el({}, { 'button, [role="button"]': null, '[data-gr-inputs]': container });
  fire(p, 'click', chip);
  check(names(p).includes('tool_started:manual'), 'a button in the input panel starts the tool');
}

// 13. A start in a page that opened in the background still records the view first.
{
  const p = page('/tools-tee-box-check', { hidden: true });
  check(p.events().length === 0, 'no tool_viewed while the page is hidden');
  p.GRTrack.completed();
  check(JSON.stringify(names(p)) === JSON.stringify(['tool_viewed', 'tool_started:manual', 'tool_completed:manual']),
    'the view is recorded before the first start: ' + names(p).join(','));
}

// 14. anchor_type is an enum of what a distance estimate was built from, never a value.
{
  const p = page('/tools-club-distance-calculator');
  check(p.GRTrack.tool && p.GRTrack.tool.id === 'club_distance_check', 'the distance check is registered');
  p.GRTrack.completed({ anchor_type: 'iron_carry', value: 152 });
  const done = p.events().find((e) => e.event === 'tool_completed');
  check(done && done.params.anchor_type === 'iron_carry', 'a known anchor type is sent');
  check(done && !('value' in done.params), 'extra detail keys are dropped');
  const q = page('/tools-club-distance-calculator');
  q.GRTrack.completed({ anchor_type: '152' });
  const bad = q.events().find((e) => e.event === 'tool_completed');
  check(bad && !('anchor_type' in bad.params), 'an unknown anchor type is dropped, not sent');
  check(!/152/.test(JSON.stringify(p.events().concat(q.events()))), 'no anchor value is ever sent');
}

// 15. Settle Up sends which games and which scoring, as enums, never money or names.
{
  const p = page('/tools-settle-up-calculator');
  p.GRTrack.completed({ game_type: 'skins_nassau', scoring_mode: 'net', stake: 500, player: 'Sam' });
  const done = p.events().find((e) => e.event === 'tool_completed');
  check(done && done.params.game_type === 'skins_nassau' && done.params.scoring_mode === 'net', 'game and scoring labels are sent');
  check(done && !('stake' in done.params) && !('player' in done.params), 'money and names are dropped');
  const q = page('/tools-settle-up-calculator');
  q.GRTrack.completed({ game_type: 'wolf', scoring_mode: '5' });
  const bad = q.events().find((e) => e.event === 'tool_completed');
  check(bad && !('game_type' in bad.params) && !('scoring_mode' in bad.params), 'unknown labels are dropped, not sent');
  check(!/Sam|500/.test(JSON.stringify(p.events().concat(q.events()))), 'no player name or stake is ever sent');
}

if (failures.length) {
  console.error('Tool events contract failed:\n- ' + failures.join('\n- '));
  process.exit(1);
}
console.log('Tool events contract passed (15 scenarios).');
