/* ============================================================================
   UNSUBSCRIBE TOKENS
   ----------------------------------------------------------------------------
   An unsubscribe link that is just `?email=someone@example.com` lets anyone
   unsubscribe anyone else, and lets a scraper walk the list. These are signed
   with HMAC-SHA256 so a link only works for the address it was issued for.

   No expiry. An unsubscribe link must work when someone digs up a six-month-old
   email — that is the whole point of one-click unsubscribe, and expiring it
   would be hostile.
   ========================================================================== */
'use strict';

var crypto = require('crypto');
var cfg = require('./config');

function b64url(buf) {
  return Buffer.from(buf).toString('base64')
    .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function unb64url(s) {
  s = String(s || '').replace(/-/g, '+').replace(/_/g, '/');
  while (s.length % 4) s += '=';
  return Buffer.from(s, 'base64').toString('utf8');
}

function sign(email) {
  var secret = cfg.env('UNSUBSCRIBE_SECRET', '');
  if (!secret) throw new Error('UNSUBSCRIBE_SECRET is not configured');
  return b64url(crypto.createHmac('sha256', secret).update(String(email).toLowerCase()).digest());
}

function make(email) {
  return b64url(String(email).toLowerCase()) + '.' + sign(email);
}

/* Returns the email only when the signature matches it. */
function verify(token) {
  var parts = String(token || '').split('.');
  if (parts.length !== 2) return null;
  var email;
  try { email = unb64url(parts[0]); } catch (e) { return null; }
  if (!email || email.indexOf('@') === -1) return null;
  var expected;
  try { expected = sign(email); } catch (e) { return null; }
  return cfg.safeEqual(parts[1], expected) ? email : null;
}

function link(email) {
  return cfg.SITE + '/api/unsubscribe?t=' + encodeURIComponent(make(email));
}

module.exports = { make: make, verify: verify, link: link };
