/* POST /api/stripe-webhook
   Stripe is the record; this endpoint reacts. Two layers of trust: the
   Stripe-Signature header is verified when a raw body is available, AND every
   event is re-fetched from Stripe by id before anything is acted on, so a
   forged POST can at most make us look up a real event. On a paid Pro
   checkout it sends the welcome email with a 30-day restore link (if mail is
   configured); the pass itself is claimed by the success page, so nothing here
   is load-bearing for entitlement. */
'use strict';
var crypto = require('crypto');
var pro = require('./_lib/pro');
var cfg = require('./_lib/config');

function verifySignature(raw, header, secret, toleranceSec) {
  if (!raw || !header || !secret) return null;                 /* null = not checked */
  var parts = {}; String(header).split(',').forEach(function (kv) { var i = kv.indexOf('='); if (i > 0) parts[kv.slice(0, i).trim()] = kv.slice(i + 1).trim(); });
  if (!parts.t || !parts.v1) return false;
  if (Math.abs(pro.nowSec() - parseInt(parts.t, 10)) > (toleranceSec || 300)) return false;
  var expected = crypto.createHmac('sha256', secret).update(parts.t + '.' + raw).digest('hex');
  return cfg.safeEqual(parts.v1, expected);
}

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') { pro.json(res, 405, { ok: false }); return; }
  if (!pro.enabled()) { pro.json(res, 503, { ok: false, error: 'Pro is not configured' }); return; }
  var rawBody = (typeof req.body === 'string' || Buffer.isBuffer(req.body)) ? req.body.toString('utf8') : null;
  var sigOk = verifySignature(rawBody, req.headers && req.headers['stripe-signature'], cfg.env('STRIPE_WEBHOOK_SECRET', ''));
  if (sigOk === false) { pro.json(res, 400, { ok: false, error: 'bad signature' }); return; }
  var posted = pro.bodyOf(req);
  if (!posted || !/^evt_[A-Za-z0-9]+$/.test(String(posted.id || ''))) { pro.json(res, 400, { ok: false, error: 'no event id' }); return; }
  var event;
  try { event = await pro.stripe('GET', '/events/' + encodeURIComponent(posted.id)); }
  catch (e) { pro.json(res, 400, { ok: false, error: 'unknown event' }); return; }

  try {
    if (event.type === 'checkout.session.completed') {
      var s = event.data && event.data.object;
      if (s && s.metadata && s.metadata.product === 'golfraw-pro' && (s.payment_status === 'paid' || s.mode === 'subscription')) {
        var full = await pro.stripe('GET', '/checkout/sessions/' + encodeURIComponent(s.id), { 'expand[]': 'subscription' });
        var pass = pro.passFromSession(full);
        if (pass.email && pro.mailEnabled()) {
          var link = pro.site() + '/pro-restore#t=' + pro.mintRestore(pass, 30 * 86400);
          var m = pro.restoreMail(pass.email, link);
          m.subject = 'Welcome to GolfRaw Pro — your pass link';
          await pro.sendMail(pass.email, m.subject, m.html, m.text);
        }
      }
    }
    /* invoice.paid / customer.subscription.* need no action: expiry is read
       from Stripe when the client refreshes. */
    pro.json(res, 200, { ok: true, received: event.type, signatureChecked: sigOk === true });
  } catch (e) { pro.json(res, 200, { ok: true, received: event.type, note: 'handled with errors' }); }
};
module.exports.verifySignature = verifySignature;
