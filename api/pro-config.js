/* GET /api/pro-config — what the paywall needs to render. Public, cached
   briefly. `enabled:false` means Pro is not on sale yet and the client keeps
   the Pro tools open in preview. */
'use strict';
var pro = require('./_lib/pro');
module.exports = async function handler(req, res) {
  if (!pro.enabled()) { pro.json(res, 200, { enabled: false, restoreByEmail: false, plans: [] }); return; }
  try {
    var plans = await pro.plans();
    res.setHeader('Cache-Control', 'public, max-age=300');
    res.status(200).json({ enabled: plans.length > 0, restoreByEmail: pro.mailEnabled(), plans: plans });
  } catch (e) { pro.json(res, 200, { enabled: false, restoreByEmail: false, plans: [], error: 'plans-unavailable' }); }
};
