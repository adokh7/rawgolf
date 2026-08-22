/* ============================================================================
   ONE-CLICK UNSUBSCRIBE  (RFC 8058)
   ----------------------------------------------------------------------------
   POST  — what Gmail and Yahoo call directly from the inbox. No confirmation
           page, no login, no "are you sure". That is the entire point.
   GET   — what a human clicking the footer link gets: it also unsubscribes
           immediately and then says so, rather than presenting a form.

   Unsubscribing must never be harder than subscribing was.
   ========================================================================== */
'use strict';

var cfg = require('./_lib/config');
var tokens = require('./_lib/token');
var subscribers = require('./_lib/subscribers');

function page(title, body, code) {
  return '<!doctype html><html lang="en"><head><meta charset="utf-8">' +
    '<meta name="viewport" content="width=device-width,initial-scale=1">' +
    '<title>' + title + ' | GOLFRAW</title></head>' +
    '<body style="margin:0;background:#F3F4F0;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif;color:#101511;">' +
    '<div style="max-width:560px;margin:0 auto;padding:56px 20px;">' +
    '<a href="https://www.golfraw.com" style="text-decoration:none;color:#101511;font-weight:800;font-size:26px;letter-spacing:-0.5px;">' +
      'GOLF<span style="color:#E03E2D;">RAW</span></a>' +
    '<h1 style="font-size:28px;line-height:1.2;margin:28px 0 14px;">' + title + '</h1>' +
    body +
    '</div></body></html>';
}

module.exports = async function handler(req, res) {
  var token = (req.query && (req.query.t || req.query.token)) || '';
  var email = tokens.verify(token);

  if (!email) {
    /* A bad token must not reveal whether an address exists. */
    if (req.method === 'POST') { res.status(400).json({ ok: false, error: 'invalid token' }); return; }
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.status(400).send(page('That link is not valid',
      '<p style="font-size:16px;line-height:1.6;">The unsubscribe link was incomplete or has been altered. ' +
      'Reply to any email from us and we will take you off by hand — that always works.</p>'));
    return;
  }

  var result = { updated: 0, note: '' };
  var failed = null;
  try {
    if (cfg.env('HUBSPOT_TOKEN', '')) result = await subscribers.markUnsubscribed(email);
    else failed = 'HUBSPOT_TOKEN is not configured';
  } catch (e) {
    failed = (e && e.message) || String(e);
  }

  if (req.method === 'POST') {
    /* RFC 8058 wants a 2xx for a successful one-click. Report a backend failure
       honestly rather than pretending, so it can be retried. */
    if (failed) { res.status(500).json({ ok: false, error: failed }); return; }
    res.status(200).json({ ok: true, unsubscribed: email });
    return;
  }

  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  if (failed) {
    res.status(500).send(page('We could not complete that',
      '<p style="font-size:16px;line-height:1.6;">Something went wrong on our side, so <b>' + templatesEsc(email) +
      '</b> may still be on the list. Reply to any email from us and we will remove you by hand.</p>'));
    return;
  }
  res.status(200).send(page('You are off the list',
    '<p style="font-size:16px;line-height:1.6;"><b>' + templatesEsc(email) + '</b> will not get another one. ' +
    'No confirmation step, no winback sequence, no "are you sure".</p>' +
    '<p style="font-size:16px;line-height:1.6;">The tools stay free and need no account at all &mdash; ' +
    'they never emailed you in the first place.</p>' +
    '<p style="margin-top:26px;"><a href="https://www.golfraw.com/tools" ' +
    'style="display:inline-block;background:#101511;color:#fff;padding:14px 22px;text-decoration:none;' +
    'font-weight:800;text-transform:uppercase;font-size:13px;letter-spacing:.5px;">Go to the tools</a></p>'));
};

function templatesEsc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
