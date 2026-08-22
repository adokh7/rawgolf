/* ============================================================================
   SUBSCRIBER LIST (HubSpot)
   ----------------------------------------------------------------------------
   The site's forms already post to HubSpot, so HubSpot is the list of record.
   This reads it; it never writes marketing data back except the unsubscribe
   flag set in unsubscribe.js.

   Zero dependencies: Vercel's Node runtime has global fetch.
   ========================================================================== */
'use strict';

var cfg = require('./config');
var API = 'https://api.hubapi.com';

function authHeaders() {
  var token = cfg.env('HUBSPOT_TOKEN', '');
  if (!token) throw new Error('HUBSPOT_TOKEN is not configured');
  return { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json' };
}

/* Contacts who can legally be emailed: subscribed, not bounced, has an address.
   HubSpot's own opt-out flag is authoritative — if someone unsubscribed through
   any other GOLFRAW email, they must not receive this one either. */
function isMailable(props) {
  if (!props || !props.email) return false;
  if (props.hs_email_optout === 'true' || props.hs_email_optout === true) return false;
  if (props.gr_unsubscribed === 'true' || props.gr_unsubscribed === true) return false;
  if (String(props.hs_email_hard_bounce_reason || '')) return false;
  return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(props.email);
}

/* Paginates the whole list. Caps out so a runaway list cannot produce an
   unbounded send. */
async function list(limitTotal) {
  var out = [], after = null, guard = 0;
  var cap = limitTotal || cfg.maxRecipients();

  while (out.length < cap && guard < 50) {
    guard++;
    var url = API + '/crm/v3/objects/contacts?limit=100' +
      '&properties=email,firstname,hs_email_optout,gr_unsubscribed,hs_email_hard_bounce_reason' +
      (after ? '&after=' + encodeURIComponent(after) : '');

    var res = await fetch(url, { headers: authHeaders() });
    if (!res.ok) {
      var detail = await res.text();
      throw new Error('HubSpot ' + res.status + ': ' + detail.slice(0, 200));
    }
    var data = await res.json();
    var results = data.results || [];
    for (var i = 0; i < results.length && out.length < cap; i++) {
      var props = results[i].properties || {};
      if (isMailable(props)) {
        out.push({ id: results[i].id, email: String(props.email).toLowerCase(),
                   firstName: props.firstname || '' });
      }
    }
    after = data.paging && data.paging.next && data.paging.next.after;
    if (!after) break;
  }
  /* One address can exist on more than one contact record. */
  var seen = {}, unique = [];
  for (var j = 0; j < out.length; j++) {
    if (!seen[out[j].email]) { seen[out[j].email] = true; unique.push(out[j]); }
  }
  return unique;
}

/* Marks a contact opted out. Used by the unsubscribe endpoint. */
async function markUnsubscribed(email) {
  var search = await fetch(API + '/crm/v3/objects/contacts/search', {
    method: 'POST', headers: authHeaders(),
    body: JSON.stringify({
      filterGroups: [{ filters: [{ propertyName: 'email', operator: 'EQ', value: String(email).toLowerCase() }] }],
      properties: ['email'], limit: 10
    })
  });
  if (!search.ok) throw new Error('HubSpot search ' + search.status);
  var found = (await search.json()).results || [];
  if (!found.length) return { updated: 0, note: 'address is not on the list' };

  var updated = 0;
  for (var i = 0; i < found.length; i++) {
    var res = await fetch(API + '/crm/v3/objects/contacts/' + found[i].id, {
      method: 'PATCH', headers: authHeaders(),
      body: JSON.stringify({ properties: { gr_unsubscribed: 'true' } })
    });
    if (res.ok) updated++;
  }
  return { updated: updated };
}

module.exports = { list: list, markUnsubscribed: markUnsubscribed, isMailable: isMailable };
