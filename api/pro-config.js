/* GET /api/pro-config — what the paywall needs to render. Public, cached
   briefly. `enabled:false` means Pro is not on sale yet and the client keeps
   the Pro tools open in preview. When something is misconfigured the
   response says what, in a form safe to show: variable names, Stripe error
   codes and messages with any key-shaped token redacted. */
'use strict';
var pro = require('./_lib/pro');
module.exports = async function handler(req, res) {
  var miss = pro.missing();
  if (miss.length) {
    console.error('[pro] not enabled: missing %s', miss.join(', '));
    pro.json(res, 200, { enabled: false, restoreByEmail: false, plans: [], reason: 'missing ' + miss.join(', ') });
    return;
  }
  try {
    var plans = await pro.plans();
    var errors = (pro._cache && pro._cache.errors) || [];
    var body = { enabled: plans.length > 0, restoreByEmail: pro.mailEnabled(), plans: plans };
    if (errors.length) body.warnings = errors;
    if (!plans.length) body.reason = errors.length ? errors.join(' | ') : 'no active prices in PRO_PRICE_IDS';
    res.setHeader('Cache-Control', plans.length ? 'public, max-age=300' : 'no-store');
    res.status(200).json(body);
  } catch (e) {
    console.error('[pro] pro-config failed: %s', e && e.stack || e);
    pro.json(res, 200, { enabled: false, restoreByEmail: false, plans: [], reason: 'plans-unavailable: ' + pro.sanitize(e && e.message) });
  }
};
