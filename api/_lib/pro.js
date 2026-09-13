/* ============================================================================
   GOLF RAW PRO — entitlement core (server side)
   ----------------------------------------------------------------------------
   Stateless by design. Stripe is the record of who paid; a signed token in the
   reader's Locker is the proof they carry. No user table, no sessions, no
   cookies. Every endpoint here refuses to operate until it is configured, so a
   deploy with no Stripe keys is safe: the client sees `enabled:false` and the
   Pro tools stay open, badged "free in preview".

   Set these in the Vercel project (Settings -> Environment Variables):

     STRIPE_SECRET_KEY        required. Restricted key is fine: it needs
                              checkout sessions, prices, customers,
                              subscriptions, events (read).
     PRO_PRICE_IDS            required. Comma-separated Stripe Price ids to
                              offer, e.g. "price_abc,price_def". Recurring or
                              one-time; the plan list is read from Stripe, so
                              amounts are never hardcoded here.
     PRO_ENTITLEMENT_SECRET   required. Signs entitlement and restore tokens.
                              Rotating it invalidates every issued pass; readers
                              restore with their email.
     STRIPE_WEBHOOK_SECRET    optional. Enables signature verification on the
                              webhook when the raw body is available; the
                              handler also re-fetches every event from Stripe by
                              id, so a forged POST cannot inject anything.
     RESEND_API_KEY           optional. Enables the welcome email and the
                              restore-by-email path. Without it, readers restore
                              with the receipt link from their purchase page.
     PRO_ONE_TIME_DAYS        optional. Pass length for a one-time price.
                              Default 365.
     PRO_GRACE_DAYS           optional. Days of access kept after a subscription
                              period ends, to survive a late renewal. Default 3.
   ========================================================================== */
'use strict';

var crypto = require('crypto');
var cfg = require('./config');

var STRIPE = 'https://api.stripe.com/v1';
var DAY = 86400;

function env(k, d) { return cfg.env(k, d); }
function b64url(buf) { return Buffer.from(buf).toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, ''); }
function unb64url(s) { s = String(s || '').replace(/-/g, '+').replace(/_/g, '/'); while (s.length % 4) s += '='; return Buffer.from(s, 'base64').toString('utf8'); }
function nowSec() { return Math.floor(Date.now() / 1000); }

/* ----------------------------------------------------------- config ----- */
function priceIds() {
  return env('PRO_PRICE_IDS', '').split(',').map(function (s) { return s.trim(); }).filter(Boolean);
}
function missing() {
  var need = ['STRIPE_SECRET_KEY', 'PRO_PRICE_IDS', 'PRO_ENTITLEMENT_SECRET'], out = [];
  for (var i = 0; i < need.length; i++) if (!env(need[i], '')) out.push(need[i]);
  return out;
}
function enabled() { return missing().length === 0; }
function mailEnabled() { return !!env('RESEND_API_KEY', ''); }
function site() { return env('PRO_SITE_URL', cfg.SITE).replace(/\/+$/, ''); }

/* ------------------------------------------------------------ stripe ---- */
/* Stripe's API is form-encoded, nested keys in brackets. No SDK: one fetch. */
function formEncode(obj, prefix, out) {
  out = out || [];
  Object.keys(obj).forEach(function (k) {
    var v = obj[k], key = prefix ? prefix + '[' + k + ']' : k;
    if (v === undefined || v === null) return;
    if (Array.isArray(v)) v.forEach(function (item, i) { if (typeof item === 'object') formEncode(item, key + '[' + i + ']', out); else out.push(encodeURIComponent(key + '[' + i + ']') + '=' + encodeURIComponent(item)); });
    else if (typeof v === 'object') formEncode(v, key, out);
    else out.push(encodeURIComponent(key) + '=' + encodeURIComponent(v));
  });
  return out.join('&');
}

async function stripe(method, path, params) {
  var key = env('STRIPE_SECRET_KEY', '');
  if (!key) throw new Error('STRIPE_SECRET_KEY is not configured');
  var url = STRIPE + path, opts = { method: method, headers: { 'Authorization': 'Bearer ' + key } };
  if (method === 'GET' && params) url += (url.indexOf('?') === -1 ? '?' : '&') + formEncode(params);
  else if (params) { opts.headers['Content-Type'] = 'application/x-www-form-urlencoded'; opts.body = formEncode(params); }
  if (typeof fetch !== 'function') throw new Error('global fetch is unavailable: the function runtime must be Node 18 or newer');
  var res = await fetch(url, opts);
  var body = await res.json()['catch'](function () { return {}; });
  if (!res.ok) {
    var msg = (body.error && body.error.message) || ('HTTP ' + res.status);
    var e = new Error('Stripe ' + res.status + (body.error && body.error.code ? ' [' + body.error.code + ']' : '') + ': ' + msg);
    e.status = res.status; e.stripe = body.error;
    console.error('[pro] Stripe %s %s -> %s', method, path, e.message);
    throw e;
  }
  return body;
}

/* Strip anything that looks like a key before a message leaves the server. */
function sanitize(msg) {
  return String(msg || '').replace(/\b(sk|rk|pk|whsec)_(live|test)?_?[A-Za-z0-9*]+/g, '[key]').slice(0, 240);
}

var planCache = { at: 0, plans: null, errors: [] };   /* mutated in place: it is exported as _cache */
function money(amount, currency) {
  try { return new Intl.NumberFormat('en', { style: 'currency', currency: currency.toUpperCase(), minimumFractionDigits: amount % 100 ? 2 : 0 }).format(amount / 100); }
  catch (e) { return (amount / 100).toFixed(2) + ' ' + currency.toUpperCase(); }
}
/* The plan list the paywall shows. Read from Stripe, cached per instance. */
async function plans() {
  /* an empty result is never cached: a transient Stripe error must not
     keep the paywall off for five minutes */
  if (planCache.plans && planCache.plans.length && Date.now() - planCache.at < 5 * 60 * 1000) return planCache.plans;
  var ids = priceIds(), out = [], errors = [];
  if (!ids.length) errors.push('PRO_PRICE_IDS is empty after trimming');
  for (var i = 0; i < ids.length; i++) {
    var p;
    try { p = await stripe('GET', '/prices/' + encodeURIComponent(ids[i]), { 'expand[]': 'product' }); }
    catch (e) { errors.push(ids[i] + ': ' + sanitize(e.message)); continue; }
    if (!p.active) { console.error('[pro] price %s is archived (active=false) in Stripe; skipping', ids[i]); errors.push(ids[i] + ': archived in Stripe'); continue; }
    var rec = p.recurring || null, product = (p.product && typeof p.product === 'object') ? p.product : {};
    out.push({
      id: p.id,
      label: p.nickname || product.name || (rec ? 'Pro ' + rec.interval + 'ly' : 'Pro pass'),
      description: product.description || '',
      amount: p.unit_amount, currency: p.currency, display: money(p.unit_amount || 0, p.currency),
      mode: rec ? 'subscription' : 'payment',
      interval: rec ? rec.interval : null, intervalCount: rec ? rec.interval_count : null
    });
  }
  /* Any currency Stripe supports is fine here: amounts are displayed with
     Intl in the price's own currency, never compared or converted. */
  planCache.at = Date.now(); planCache.plans = out; planCache.errors = errors;
  if (errors.length) console.error('[pro] %d of %d configured price(s) unusable: %s', errors.length, ids.length, errors.join(' | '));
  return out;
}

/* ------------------------------------------------------------ tokens ---- */
function sign(kind, payloadB64) {
  var secret = env('PRO_ENTITLEMENT_SECRET', '');
  if (!secret) throw new Error('PRO_ENTITLEMENT_SECRET is not configured');
  return b64url(crypto.createHmac('sha256', secret).update(kind + '.' + payloadB64).digest());
}
function mint(kind, payload) {
  var p = b64url(JSON.stringify(payload));
  return kind + '.' + p + '.' + sign(kind, p);
}
/* Returns the payload only when the signature and expiry both hold. */
function verify(token, kind) {
  var parts = String(token || '').split('.');
  if (parts.length !== 3 || parts[0] !== kind) return { ok: false, reason: 'malformed' };
  var expected;
  try { expected = sign(kind, parts[1]); } catch (e) { return { ok: false, reason: 'unconfigured' }; }
  if (!cfg.safeEqual(parts[2], expected)) return { ok: false, reason: 'bad-signature' };
  var payload;
  try { payload = JSON.parse(unb64url(parts[1])); } catch (e) { return { ok: false, reason: 'malformed' }; }
  if (!payload || typeof payload.exp !== 'number') return { ok: false, reason: 'malformed' };
  if (payload.exp <= nowSec()) return { ok: false, reason: 'expired', payload: payload };
  return { ok: true, payload: payload };
}

/* Entitlement: what the reader's Locker holds. `v1` tokens. */
function mintEntitlement(f) {
  return mint('v1', { sub: String(f.email || '').toLowerCase(), cid: f.customerId || null, sid: f.subscriptionId || null,
    plan: f.plan || '', mode: f.mode, iat: nowSec(), exp: f.exp });
}
/* Restore: short-lived, emailed. `r1` tokens. */
function mintRestore(f, ttlSec) {
  return mint('r1', { sub: String(f.email || '').toLowerCase(), cid: f.customerId || null, iat: nowSec(), exp: nowSec() + (ttlSec || 30 * 60) });
}

function graceSec() { var d = parseInt(env('PRO_GRACE_DAYS', '3'), 10); return (isFinite(d) ? d : 3) * DAY; }
function oneTimeSec() { var d = parseInt(env('PRO_ONE_TIME_DAYS', '365'), 10); return (isFinite(d) ? d : 365) * DAY; }

/* From a paid Checkout Session (expanded subscription), decide the pass. */
function passFromSession(s) {
  var email = String((s.customer_details && s.customer_details.email) || s.customer_email || '').toLowerCase();
  var cid = typeof s.customer === 'string' ? s.customer : (s.customer && s.customer.id) || null;
  if (s.mode === 'subscription') {
    var sub = (s.subscription && typeof s.subscription === 'object') ? s.subscription : null;
    var end = sub && sub.current_period_end ? sub.current_period_end : nowSec() + 31 * DAY;
    var price = sub && sub.items && sub.items.data && sub.items.data[0] && sub.items.data[0].price;
    return { email: email, customerId: cid, subscriptionId: sub ? sub.id : (typeof s.subscription === 'string' ? s.subscription : null),
      plan: price ? (price.nickname || price.id) : 'subscription', mode: 'subscription', exp: end + graceSec() };
  }
  return { email: email, customerId: cid, subscriptionId: null, plan: 'pass', mode: 'payment', exp: (s.created || nowSec()) + oneTimeSec() };
}

/* Is this Stripe customer entitled right now? Used by restore and refresh.
   Subscriptions first, then a paid one-time session inside the pass window. */
async function passForCustomer(cid, email) {
  email = String(email || '').toLowerCase();
  var subs = await stripe('GET', '/subscriptions', { customer: cid, status: 'all', limit: 10 });
  var best = null;
  (subs.data || []).forEach(function (sub) {
    if (['active', 'trialing', 'past_due'].indexOf(sub.status) === -1) return;
    if (!best || sub.current_period_end > best.current_period_end) best = sub;
  });
  if (best) {
    var price = best.items && best.items.data && best.items.data[0] && best.items.data[0].price;
    return { email: email, customerId: cid, subscriptionId: best.id, plan: price ? (price.nickname || price.id) : 'subscription', mode: 'subscription', exp: best.current_period_end + graceSec() };
  }
  var sessions = await stripe('GET', '/checkout/sessions', { customer: cid, status: 'complete', limit: 20 });
  var cut = nowSec() - oneTimeSec(), latest = null;
  (sessions.data || []).forEach(function (s) {
    if (s.mode !== 'payment' || s.payment_status !== 'paid' || s.created < cut) return;
    if (!latest || s.created > latest.created) latest = s;
  });
  if (latest) return { email: email, customerId: cid, subscriptionId: null, plan: 'pass', mode: 'payment', exp: latest.created + oneTimeSec() };
  return null;
}

/* ------------------------------------------------------------- mail ----- */
async function sendMail(to, subject, html, text) {
  var key = env('RESEND_API_KEY', '');
  if (!key) return { ok: false, reason: 'mail-unconfigured' };
  var res = await fetch('https://api.resend.com/emails', {
    method: 'POST', headers: { 'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json' },
    body: JSON.stringify({ from: 'GolfRaw <contact@golfraw.com>', to: [to], subject: subject, html: html, text: text, reply_to: cfg.env('MAIL_REPLY_TO', 'contact@golfraw.com') })
  });
  if (!res.ok) { var d = await res.text(); throw new Error('Resend ' + res.status + ': ' + d.slice(0, 160)); }
  return { ok: true };
}
function esc(s) { return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
function restoreMail(email, link) {
  var html = '<div style="font-family:-apple-system,Segoe UI,Arial,sans-serif;max-width:560px;margin:0 auto;padding:28px 20px;color:#0B1F15">' +
    '<p style="font-weight:800;font-size:22px;margin:0 0 18px;color:#0A4D2E">GOLF<span style="font-weight:500">RAW</span> Pro</p>' +
    '<p style="font-size:16px;line-height:1.6">Tap the button and Pro is switched on in that browser. The link works for 30 days and can be used on every device you own.</p>' +
    '<p style="margin:24px 0"><a href="' + esc(link) + '" style="display:inline-block;background:#1B7A43;color:#fff;text-decoration:none;font-weight:800;padding:14px 22px;border-radius:10px">Restore my Pro pass</a></p>' +
    '<p style="font-size:13px;line-height:1.6;color:#55655B">If the button does not work, copy this address into your browser:<br>' + esc(link) + '</p>' +
    '<p style="font-size:13px;line-height:1.6;color:#55655B">Did not ask for this? Ignore it; nothing changes. Your pass lives only in your browsers and is never uploaded to us.</p></div>';
  var text = 'GolfRaw Pro\n\nOpen this link to restore your Pro pass (valid 30 days, any device):\n' + link + '\n\nDid not ask for this? Ignore it.';
  return { subject: 'Your GolfRaw Pro pass', html: html, text: text };
}

/* ------------------------------------------------------------ http ------ */
function json(res, code, body) { res.setHeader('Cache-Control', 'no-store'); res.status(code).json(body); }
function sameSite(req) {
  var o = (req.headers && (req.headers.origin || req.headers.referer)) || '';
  if (!o) return true;                     /* curl, some privacy modes: allow */
  try { var h = new URL(o).hostname; return h === 'www.golfraw.com' || h === 'golfraw.com' || h === 'localhost'; } catch (e) { return false; }
}
function bodyOf(req) {
  var b = req.body;
  if (b && typeof b === 'object' && !Buffer.isBuffer(b)) return b;
  try { return JSON.parse(Buffer.isBuffer(b) ? b.toString('utf8') : String(b || '{}')); } catch (e) { return {}; }
}

module.exports = {
  enabled: enabled, missing: missing, mailEnabled: mailEnabled, site: site, priceIds: priceIds, plans: plans,
  stripe: stripe, formEncode: formEncode, money: money,
  mint: mint, verify: verify, mintEntitlement: mintEntitlement, mintRestore: mintRestore,
  passFromSession: passFromSession, passForCustomer: passForCustomer,
  sendMail: sendMail, restoreMail: restoreMail,
  json: json, sameSite: sameSite, bodyOf: bodyOf, nowSec: nowSec, sanitize: sanitize,
  _cache: planCache
};
