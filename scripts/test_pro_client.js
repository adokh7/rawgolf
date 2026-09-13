/* Client state-machine tests for lib/pro/pro.js under node with a fake
   window: config reachable/unreachable, token valid/expired/rejected. */
'use strict';
var n = 0, fails = 0;
function eq(a, b, l) { n++; if (JSON.stringify(a) !== JSON.stringify(b)) { fails++; console.log('  FAIL ' + l + '\n      got  ' + JSON.stringify(a) + '\n      want ' + JSON.stringify(b)); } }
var store = {}; var responses = {}; var calls = [];
global.window = global.self = { localStorage: { getItem: function (k) { return store[k] || null; }, setItem: function (k, v) { store[k] = v; }, removeItem: function (k) { delete store[k]; } },
  fetch: function (url, opts) { calls.push(url); var r = responses[url.split('?')[0]]; if (r === 'fail') return Promise.reject(new Error('offline')); return Promise.resolve({ json: function () { return Promise.resolve(typeof r === 'function' ? r(opts) : r); } }); },
  location: { search: '', pathname: '/x', hash: '' }, history: { replaceState: function () {} }, document: null };
var Pro = require('../lib/pro/pro.js');
var NOW = Math.floor(Date.now() / 1000);
function tok(exp, extra) { var p = Object.assign({ sub: 'a@b.co', cid: 'cus_1', plan: 'Pro', mode: 'subscription', iat: NOW, exp: exp }, extra || {}); return 'v1.' + Buffer.from(JSON.stringify(p)).toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '') + '.sig'; }
async function run(cfg, token, verify, refresh) { Pro._reset(); store = {}; calls = []; if (token) store.golfraw_pro_pass = token; responses = { '/api/pro-config': cfg, '/api/pro-verify': verify || { ok: true }, '/api/pro-refresh': refresh || { ok: false, reason: 'unavailable' } }; return Pro.ready(); }
(async function () {
  eq(await run({ enabled: false, plans: [] }, null), 'preview', 'not on sale, no token -> preview');
  eq(await run('fail', null), 'preview', 'config unreachable -> preview (fail open)');
  eq(await run({ enabled: true, plans: [{ id: 'p' }] }, null), 'gated', 'on sale, no token -> gated');
  eq(await run({ enabled: true, plans: [] }, tok(NOW + 86400 * 30)), 'pro', 'valid token verified -> pro');
  eq(await run({ enabled: true, plans: [] }, tok(NOW - 10)), 'gated', 'expired token, refresh unavailable -> gated');
  eq(await run({ enabled: true, plans: [] }, tok(NOW + 86400 * 30), { ok: false, reason: 'bad-signature' }), 'gated', 'server rejects signature -> token dropped, gated');
  eq(store.golfraw_pro_pass, undefined, 'rejected token removed from storage');
  eq(await run({ enabled: true, plans: [] }, tok(NOW + 86400 * 30), 'fail'), 'pro', 'verify unreachable (offline) -> trust token');
  eq(await run('fail', tok(NOW + 86400 * 30)), 'pro', 'config unreachable but token valid -> pro');
  var fresh = tok(NOW + 86400 * 40); eq(await run({ enabled: true, plans: [] }, tok(NOW + 86400 * 2), null, { ok: true, token: fresh }), 'pro', 'near expiry -> refreshed');
  eq(store.golfraw_pro_pass, fresh, 'refreshed token stored'); eq(calls.some(function (u) { return /pro-refresh/.test(u); }), true, 'refresh endpoint used near expiry');
  eq(await run({ enabled: true, plans: [] }, tok(NOW + 86400 * 2), null, { ok: false, reason: 'lapsed' }), 'gated', 'refresh says lapsed -> gated');
  eq(await run({ enabled: true, plans: [] }, 'v1.notjson.sig'), 'gated', 'undecodable token dropped');
  eq(Pro.decode(tok(NOW + 5)).plan, 'Pro', 'decode payload'); eq(Pro.decode('r1.x.y'), null, 'wrong kind');
  window.location.search = '?pro=cancelled'; eq(Pro.noteCancelled(), true, 'cancelled flag detected'); window.location.search = ''; eq(Pro.noteCancelled(), false, 'no flag');
  console.log((n - fails) + '/' + n + ' checks passed' + (fails ? '  <-- FAILURES' : '')); process.exit(fails ? 1 : 0);
})();
