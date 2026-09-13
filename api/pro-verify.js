/* POST /api/pro-verify { token } -> { ok, plan, exp } | { ok:false, reason }
   Pure signature + expiry check. The client calls it when online and drops a
   token the server rejects; offline, it trusts the token until its expiry. */
'use strict';
var pro = require('./_lib/pro');
module.exports = async function handler(req, res) {
  if (req.method !== 'POST') { pro.json(res, 405, { ok: false, reason: 'POST only' }); return; }
  if (!pro.enabled()) { pro.json(res, 200, { ok: false, reason: 'unconfigured' }); return; }
  var v = pro.verify(pro.bodyOf(req).token, 'v1');
  if (!v.ok) { pro.json(res, 200, { ok: false, reason: v.reason }); return; }
  pro.json(res, 200, { ok: true, plan: v.payload.plan, mode: v.payload.mode, exp: v.payload.exp });
};
