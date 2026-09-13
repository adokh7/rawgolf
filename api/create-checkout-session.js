/* POST /api/create-checkout-session { priceId } -> { url }
   Redirects the reader to Stripe Checkout. Only prices from PRO_PRICE_IDS are
   accepted; the success page claims the pass by session id. */
'use strict';
var pro = require('./_lib/pro');
module.exports = async function handler(req, res) {
  if (req.method !== 'POST') { pro.json(res, 405, { ok: false, error: 'POST only' }); return; }
  if (!pro.enabled()) { pro.json(res, 503, { ok: false, error: 'Pro is not on sale yet' }); return; }
  if (!pro.sameSite(req)) { pro.json(res, 403, { ok: false, error: 'forbidden' }); return; }
  var body = pro.bodyOf(req), priceId = String(body.priceId || '');
  if (pro.priceIds().indexOf(priceId) === -1) { pro.json(res, 400, { ok: false, error: 'unknown price' }); return; }
  try {
    var plans = await pro.plans(), plan = plans.filter(function (p) { return p.id === priceId; })[0];
    if (!plan) { pro.json(res, 400, { ok: false, error: 'price not available' }); return; }
    var params = {
      mode: plan.mode,
      'line_items[0][price]': priceId, 'line_items[0][quantity]': 1,
      success_url: pro.site() + '/pro-thanks?session_id={CHECKOUT_SESSION_ID}',
      cancel_url: pro.site() + '/tools?pro=cancelled',
      allow_promotion_codes: 'true',
      'metadata[product]': 'golfraw-pro'
    };
    if (plan.mode === 'payment') params.customer_creation = 'always';
    if (body.email && /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(body.email)) params.customer_email = String(body.email).slice(0, 120);
    var session = await pro.stripe('POST', '/checkout/sessions', params);
    pro.json(res, 200, { ok: true, url: session.url });
  } catch (e) { pro.json(res, 502, { ok: false, error: 'Could not start checkout. Try again in a moment.' }); }
};
