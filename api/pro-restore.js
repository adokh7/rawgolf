/* POST /api/pro-restore { email }
   Emails a restore link to an address that has a Pro pass. The response is
   the same whether or not the address is known, so the endpoint cannot be
   used to test who is a customer. Needs RESEND_API_KEY; without it the client
   is told to use the receipt link instead. */
'use strict';
var pro = require('./_lib/pro');
var recent = {};   /* per-instance throttle: one mail per address per minute */
module.exports = async function handler(req, res) {
  if (req.method !== 'POST') { pro.json(res, 405, { ok: false, error: 'POST only' }); return; }
  if (!pro.enabled()) { pro.json(res, 503, { ok: false, error: 'Pro is not configured' }); return; }
  if (!pro.mailEnabled()) { pro.json(res, 200, { ok: false, reason: 'restore-unavailable' }); return; }
  if (!pro.sameSite(req)) { pro.json(res, 403, { ok: false, error: 'forbidden' }); return; }
  var email = String(pro.bodyOf(req).email || '').trim().toLowerCase();
  var generic = { ok: true, message: 'If that address has a Pro pass, a restore link is on its way.' };
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) { pro.json(res, 200, generic); return; }
  var last = recent[email] || 0; if (Date.now() - last < 60 * 1000) { pro.json(res, 200, generic); return; }
  recent[email] = Date.now();
  try {
    var customers = await pro.stripe('GET', '/customers', { email: email, limit: 5 });
    var pass = null;
    for (var i = 0; i < (customers.data || []).length && !pass; i++) pass = await pro.passForCustomer(customers.data[i].id, email);
    if (pass) {
      var link = pro.site() + '/pro-restore#t=' + pro.mintRestore(pass, 30 * 86400);
      var m = pro.restoreMail(email, link);
      await pro.sendMail(email, m.subject, m.html, m.text);
    }
  } catch (e) { /* deliberately silent: the response must not vary */ }
  pro.json(res, 200, generic);
};
