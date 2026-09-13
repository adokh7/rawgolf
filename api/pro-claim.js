/* GET /api/pro-claim?session_id=cs_...  or  ?restore=r1....
   Turns a paid Checkout Session, or a valid restore token, into an entitlement
   token for the reader's Locker. Stripe is consulted every time: a session id
   or a restore token is a key to ask, never the pass itself. */
'use strict';
var pro = require('./_lib/pro');
module.exports = async function handler(req, res) {
  if (!pro.enabled()) { pro.json(res, 503, { ok: false, error: 'Pro is not configured' }); return; }
  var q = req.query || {};
  try {
    var pass = null;
    if (q.session_id) {
      var sid = String(q.session_id);
      if (!/^cs_[A-Za-z0-9_]+$/.test(sid)) { pro.json(res, 400, { ok: false, error: 'bad session id' }); return; }
      var s = await pro.stripe('GET', '/checkout/sessions/' + encodeURIComponent(sid), { 'expand[]': 'subscription' });
      if (s.payment_status !== 'paid' && !(s.mode === 'subscription' && s.status === 'complete')) { pro.json(res, 402, { ok: false, error: 'This checkout was not completed.' }); return; }
      if (!(s.metadata && s.metadata.product === 'golfraw-pro')) { pro.json(res, 400, { ok: false, error: 'not a Pro checkout' }); return; }
      pass = pro.passFromSession(s);
    } else if (q.restore) {
      var v = pro.verify(String(q.restore), 'r1');
      if (!v.ok) { pro.json(res, 400, { ok: false, error: v.reason === 'expired' ? 'That restore link has expired. Request a new one.' : 'That restore link is not valid.' }); return; }
      pass = v.payload.cid ? await pro.passForCustomer(v.payload.cid, v.payload.sub) : null;
      if (!pass) { pro.json(res, 402, { ok: false, error: 'No active Pro pass was found for that customer.' }); return; }
    } else { pro.json(res, 400, { ok: false, error: 'missing session_id or restore' }); return; }
    var token = pro.mintEntitlement(pass);
    pro.json(res, 200, { ok: true, token: token, plan: pass.plan, mode: pass.mode, exp: pass.exp, email: pass.email.replace(/^(.).*(@.*)$/, '$1***$2') });
  } catch (e) { pro.json(res, 502, { ok: false, error: 'Could not confirm the purchase right now. Keep this page open and try again in a minute.' }); }
};
