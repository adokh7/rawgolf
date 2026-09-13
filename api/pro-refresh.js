/* POST /api/pro-refresh { token } -> { ok, token, exp }
   A subscription renews on Stripe with no way to push a new expiry into the
   reader's browser, so the client asks for one when its pass is near expiry.
   The old token must still verify (expired ones may refresh within the grace
   window); Stripe decides whether the customer is still entitled. */
'use strict';
var pro = require('./_lib/pro');
module.exports = async function handler(req, res) {
  if (req.method !== 'POST') { pro.json(res, 405, { ok: false, reason: 'POST only' }); return; }
  if (!pro.enabled()) { pro.json(res, 200, { ok: false, reason: 'unconfigured' }); return; }
  var v = pro.verify(pro.bodyOf(req).token, 'v1');
  var p = v.payload;
  if (!v.ok && !(v.reason === 'expired' && p && p.exp > pro.nowSec() - 30 * 86400)) { pro.json(res, 200, { ok: false, reason: v.reason || 'invalid' }); return; }
  if (!p || !p.cid) { pro.json(res, 200, { ok: false, reason: 'no-customer' }); return; }
  try {
    var pass = await pro.passForCustomer(p.cid, p.sub);
    if (!pass) { pro.json(res, 200, { ok: false, reason: 'lapsed' }); return; }
    pro.json(res, 200, { ok: true, token: pro.mintEntitlement(pass), plan: pass.plan, mode: pass.mode, exp: pass.exp });
  } catch (e) { pro.json(res, 200, { ok: false, reason: 'unavailable' }); }
};
