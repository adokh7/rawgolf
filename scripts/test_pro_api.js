/* Server-side tests for the Pro entitlement layer. Run: node scripts/test_pro_api.js
   Uses throwaway in-process env values and a mocked Stripe API. Nothing here
   touches the network or a real key. */
'use strict';
process.env.STRIPE_SECRET_KEY = 'sk_test_fake_for_unit_tests';
process.env.PRO_PRICE_IDS = 'price_month, price_year,price_once';
process.env.PRO_ENTITLEMENT_SECRET = 'unit-test-secret-not-real';
process.env.STRIPE_WEBHOOK_SECRET = 'whsec_unit_test';
delete process.env.RESEND_API_KEY;

var crypto = require('crypto');
var n = 0, fails = 0;
function eq(a, b, l) { n++; if (JSON.stringify(a) !== JSON.stringify(b)) { fails++; console.log('  FAIL ' + l + '\n      got  ' + JSON.stringify(a) + '\n      want ' + JSON.stringify(b)); } }
function ok(c, l) { n++; if (!c) { fails++; console.log('  FAIL ' + l); } }

/* ---- mocked Stripe ---- */
var calls = [];
var NOW = Math.floor(Date.now() / 1000);
var STORE = {
  '/prices/price_month': { id: 'price_month', active: true, unit_amount: 500, currency: 'usd', nickname: 'Pro Monthly', recurring: { interval: 'month', interval_count: 1 }, product: { name: 'GolfRaw Pro' } },
  '/prices/price_year': { id: 'price_year', active: true, unit_amount: 3900, currency: 'usd', nickname: null, recurring: { interval: 'year', interval_count: 1 }, product: { name: 'GolfRaw Pro' } },
  '/prices/price_once': { id: 'price_once', active: true, unit_amount: 1999, currency: 'gbp', nickname: 'Season pass', recurring: null, product: { name: 'GolfRaw Pro' } },
  '/checkout/sessions/cs_paid': { id: 'cs_paid', mode: 'subscription', status: 'complete', payment_status: 'paid', customer: 'cus_1', customer_details: { email: 'Buyer@Example.com' }, metadata: { product: 'golfraw-pro' }, subscription: { id: 'sub_1', current_period_end: NOW + 30 * 86400, items: { data: [{ price: { id: 'price_month', nickname: 'Pro Monthly' } }] } } },
  '/checkout/sessions/cs_once': { id: 'cs_once', mode: 'payment', status: 'complete', payment_status: 'paid', customer: 'cus_2', created: NOW - 10, customer_details: { email: 'once@example.com' }, metadata: { product: 'golfraw-pro' } },
  '/checkout/sessions/cs_open': { id: 'cs_open', mode: 'payment', status: 'open', payment_status: 'unpaid', metadata: { product: 'golfraw-pro' } },
  '/checkout/sessions/cs_other': { id: 'cs_other', mode: 'payment', status: 'complete', payment_status: 'paid', metadata: {} },
  '/events/evt_1': { id: 'evt_1', type: 'checkout.session.completed', data: { object: { id: 'cs_paid', metadata: { product: 'golfraw-pro' }, payment_status: 'paid', mode: 'subscription' } } },
  '/subscriptions': function (q) { return q.customer === 'cus_1' ? { data: [{ id: 'sub_1', status: 'active', current_period_end: NOW + 20 * 86400, items: { data: [{ price: { id: 'price_month', nickname: 'Pro Monthly' } }] } }] } : { data: [] }; },
  '/checkout/sessions': function (q) { return q.customer === 'cus_2' ? { data: [{ id: 'cs_once', mode: 'payment', payment_status: 'paid', created: NOW - 100 }] } : { data: [] }; },
  '/customers': function (q) { return q.email === 'buyer@example.com' ? { data: [{ id: 'cus_1' }] } : { data: [] }; }
};
global.fetch = async function (url, opts) {
  var u = new URL(url); calls.push({ method: (opts && opts.method) || 'GET', path: u.pathname.replace('/v1', ''), body: opts && opts.body, query: Object.fromEntries(u.searchParams) });
  var path = u.pathname.replace('/v1', '');
  if (path === '/checkout/sessions' && opts && opts.method === 'POST') return { ok: true, status: 200, json: async function () { return { id: 'cs_new', url: 'https://checkout.stripe.com/c/pay/cs_new' }; } };
  var hit = STORE[path];
  if (typeof hit === 'function') hit = hit(Object.fromEntries(u.searchParams));
  if (!hit) return { ok: false, status: 404, json: async function () { return { error: { message: 'No such object: ' + path } }; }, text: async function () { return 'nope'; } };
  return { ok: true, status: 200, json: async function () { return hit; } };
};
function mockRes() { var r = { code: 0, body: null, headers: {} }; r.setHeader = function (k, v) { r.headers[k] = v; }; r.status = function (c) { r.code = c; return r; }; r.json = function (b) { r.body = b; return r; }; return r; }

var pro = require('../api/_lib/pro');

(async function () {
  console.log('tokens');
  var tok = pro.mintEntitlement({ email: 'Buyer@Example.com', customerId: 'cus_1', subscriptionId: 'sub_1', plan: 'Pro Monthly', mode: 'subscription', exp: NOW + 100 });
  ok(/^v1\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$/.test(tok), 'entitlement token shape');
  var v = pro.verify(tok, 'v1'); ok(v.ok && v.payload.sub === 'buyer@example.com' && v.payload.plan === 'Pro Monthly', 'verifies; email lowercased');
  eq(pro.verify(tok.slice(0, -2) + 'xx', 'v1').reason, 'bad-signature', 'tampered signature');
  var parts = tok.split('.'); var forged = parts[0] + '.' + Buffer.from(JSON.stringify(Object.assign(JSON.parse(Buffer.from(parts[1].replace(/-/g, '+').replace(/_/g, '/'), 'base64')), { exp: NOW + 9e6 }))).toString('base64').replace(/=+$/, '') + '.' + parts[2];
  eq(pro.verify(forged, 'v1').reason, 'bad-signature', 'tampered payload');
  eq(pro.verify(pro.mintEntitlement({ email: 'a@b.co', mode: 'payment', exp: NOW - 1 }), 'v1').reason, 'expired', 'expired');
  eq(pro.verify(tok, 'r1').reason, 'malformed', 'kind mismatch rejected');
  eq(pro.verify('garbage', 'v1').reason, 'malformed', 'garbage');
  var rt = pro.mintRestore({ email: 'x@y.z', customerId: 'cus_9' }, 60); ok(pro.verify(rt, 'r1').ok && pro.verify(rt, 'r1').payload.cid === 'cus_9', 'restore token');

  console.log('stripe helpers');
  eq(pro.formEncode({ mode: 'payment', 'line_items[0][price]': 'p', meta: { a: 1 } }), 'mode=payment&line_items%5B0%5D%5Bprice%5D=p&meta%5Ba%5D=1', 'form encoding');
  eq(pro.money(500, 'usd'), '$5', 'money whole'); eq(pro.money(1999, 'gbp'), '£19.99', 'money pence');
  var plans = await pro.plans(); eq(plans.map(function (p) { return p.id + ':' + p.mode + ':' + p.display; }), ['price_month:subscription:$5', 'price_year:subscription:$39', 'price_once:payment:£19.99'], 'plans from Stripe, no hardcoded prices');
  eq(plans[1].label, 'GolfRaw Pro', 'label falls back to product name');

  console.log('endpoints');
  var res = mockRes(); await require('../api/pro-config')({ method: 'GET' }, res); ok(res.body.enabled === true && res.body.plans.length === 3 && res.body.restoreByEmail === false, 'config enabled, mail off');
  res = mockRes(); await require('../api/create-checkout-session')({ method: 'POST', headers: { origin: 'https://www.golfraw.com' }, body: { priceId: 'price_once' } }, res);
  ok(res.code === 200 && /checkout\.stripe\.com/.test(res.body.url), 'checkout url returned');
  var c = calls[calls.length - 1]; ok(/mode=payment/.test(c.body) && /customer_creation=always/.test(c.body) && /success_url=.*pro-thanks.*CHECKOUT_SESSION_ID/.test(c.body) && /metadata%5Bproduct%5D=golfraw-pro/.test(c.body), 'session params (' + c.body.slice(0, 80) + ')');
  res = mockRes(); await require('../api/create-checkout-session')({ method: 'POST', headers: {}, body: { priceId: 'price_evil' } }, res); eq(res.code, 400, 'unknown price rejected');
  res = mockRes(); await require('../api/create-checkout-session')({ method: 'POST', headers: { origin: 'https://evil.example' }, body: { priceId: 'price_once' } }, res); eq(res.code, 403, 'cross-site origin rejected');
  res = mockRes(); await require('../api/pro-claim')({ query: { session_id: 'cs_paid' } }, res); ok(res.code === 200 && res.body.ok && res.body.mode === 'subscription' && res.body.email === 'b***@example.com', 'claim paid subscription (masked email)');
  var claimed = res.body.token; var cp = pro.verify(claimed, 'v1'); ok(cp.ok && cp.payload.exp === NOW + 30 * 86400 + 3 * 86400 && cp.payload.cid === 'cus_1', 'exp = period end + 3d grace');
  res = mockRes(); await require('../api/pro-claim')({ query: { session_id: 'cs_once' } }, res); ok(res.body.ok && res.body.mode === 'payment' && res.body.exp === NOW - 10 + 365 * 86400, 'one-time pass = 365 days from purchase');
  res = mockRes(); await require('../api/pro-claim')({ query: { session_id: 'cs_open' } }, res); eq(res.code, 402, 'unpaid session refused');
  res = mockRes(); await require('../api/pro-claim')({ query: { session_id: 'cs_other' } }, res); eq(res.code, 400, 'non-Pro checkout refused');
  res = mockRes(); await require('../api/pro-claim')({ query: { session_id: 'cs_nope' } }, res); eq(res.code, 502, 'unknown session -> soft error');
  res = mockRes(); await require('../api/pro-claim')({ query: { restore: pro.mintRestore({ email: 'buyer@example.com', customerId: 'cus_1' }, 60) } }, res); ok(res.body.ok && res.body.plan === 'Pro Monthly', 'restore token -> active subscription pass');
  res = mockRes(); await require('../api/pro-claim')({ query: { restore: pro.mintRestore({ email: 'x@y.z', customerId: 'cus_none' }, 60) } }, res); eq(res.code, 402, 'restore for lapsed customer refused');
  res = mockRes(); await require('../api/pro-verify')({ method: 'POST', body: { token: claimed } }, res); ok(res.body.ok && res.body.plan === 'Pro Monthly', 'verify ok');
  res = mockRes(); await require('../api/pro-verify')({ method: 'POST', body: { token: 'v1.x.y' } }, res); eq(res.body, { ok: false, reason: 'bad-signature' }, 'verify bad');
  res = mockRes(); await require('../api/pro-refresh')({ method: 'POST', body: { token: claimed } }, res); ok(res.body.ok && pro.verify(res.body.token, 'v1').payload.exp === NOW + 20 * 86400 + 3 * 86400, 'refresh reads new period end from Stripe');
  var lapsed = pro.mintEntitlement({ email: 'x@y.z', customerId: 'cus_none', mode: 'subscription', exp: NOW + 5 }); res = mockRes(); await require('../api/pro-refresh')({ method: 'POST', body: { token: lapsed } }, res); eq(res.body.reason, 'lapsed', 'refresh lapsed');
  res = mockRes(); await require('../api/pro-restore')({ method: 'POST', headers: {}, body: { email: 'buyer@example.com' } }, res); eq(res.body, { ok: false, reason: 'restore-unavailable' }, 'restore needs mail configured');
  process.env.RESEND_API_KEY = 're_unit'; var mails = 0; var realFetch = global.fetch; global.fetch = async function (u, o) { if (/resend\.com/.test(u)) { mails++; return { ok: true, json: async function () { return {}; }, text: async function () { return ''; } }; } return realFetch(u, o); };
  res = mockRes(); await require('../api/pro-restore')({ method: 'POST', headers: {}, body: { email: 'buyer@example.com' } }, res); ok(res.body.ok && mails === 1, 'known customer gets a mail');
  res = mockRes(); await require('../api/pro-restore')({ method: 'POST', headers: {}, body: { email: 'stranger@example.com' } }, res); ok(res.body.ok && mails === 1 && res.body.message === 'If that address has a Pro pass, a restore link is on its way.', 'unknown address: same response, no mail');
  res = mockRes(); await require('../api/pro-restore')({ method: 'POST', headers: {}, body: { email: 'buyer@example.com' } }, res); ok(mails === 1, 'throttled: no second mail within a minute');

  console.log('webhook');
  var wh = require('../api/stripe-webhook'); var raw = JSON.stringify({ id: 'evt_1', type: 'checkout.session.completed' }); var t = String(pro.nowSec());
  var sig = 't=' + t + ',v1=' + crypto.createHmac('sha256', 'whsec_unit_test').update(t + '.' + raw).digest('hex');
  eq(wh.verifySignature(raw, sig, 'whsec_unit_test'), true, 'signature verifies'); eq(wh.verifySignature(raw, sig.replace(/v1=.*/, 'v1=00'), 'whsec_unit_test'), false, 'bad signature'); eq(wh.verifySignature(raw, 't=1,v1=abc', 'whsec_unit_test'), false, 'stale timestamp'); eq(wh.verifySignature(null, sig, 'whsec_unit_test'), null, 'no raw body -> not checked');
  mails = 0; res = mockRes(); await wh({ method: 'POST', headers: { 'stripe-signature': sig }, body: raw }, res); ok(res.code === 200 && res.body.signatureChecked === true && mails === 1, 'signed event: refetched from Stripe, welcome mail sent');
  res = mockRes(); await wh({ method: 'POST', headers: { 'stripe-signature': 't=' + t + ',v1=deadbeef' }, body: raw }, res); eq(res.code, 400, 'forged signature rejected');
  res = mockRes(); await wh({ method: 'POST', headers: {}, body: { id: 'evt_forged', type: 'checkout.session.completed' } }, res); eq(res.code, 400, 'unknown event id rejected even without signature');
  res = mockRes(); await wh({ method: 'POST', headers: {}, body: { id: 'evt_1', type: 'x' } }, res); ok(res.code === 200 && res.body.received === 'checkout.session.completed', 'parsed body (no raw): event refetched by id, type taken from Stripe not the POST');

  console.log('unconfigured');
  delete process.env.STRIPE_SECRET_KEY; delete require.cache[require.resolve('../api/_lib/pro')];
  var pro2 = require('../api/_lib/pro'); eq(pro2.enabled(), false, 'disabled without keys'); eq(pro2.missing(), ['STRIPE_SECRET_KEY'], 'names what is missing');
  res = mockRes(); await require('../api/pro-config')({ method: 'GET' }, res); eq(res.body, { enabled: false, restoreByEmail: false, plans: [] }, 'config says disabled -> client keeps tools open');

  console.log('\n' + (n - fails) + '/' + n + ' checks passed' + (fails ? '  <-- FAILURES' : ''));
  process.exit(fails ? 1 : 0);
})();
