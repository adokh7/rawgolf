/* ============================================================================
   DISPATCH (Resend)
   ----------------------------------------------------------------------------
   One message per recipient, never a shared To/BCC. A single message addressed
   to the whole list leaks every subscriber's address to every other subscriber
   and cannot carry a per-person unsubscribe link.

   RFC 8058 one-click unsubscribe headers are set on every message. Gmail and
   Yahoo require them for bulk senders, and without them list-unsubscribe
   surfaces as "report spam" instead.
   ========================================================================== */
'use strict';

var cfg = require('./config');
var tokens = require('./token');
var FROM = 'GolfRaw <contact@golfraw.com>';

async function sendOne(recipient, message) {
  var from = FROM;
  var unsubUrl = tokens.link(recipient.email);
  var replyTo = cfg.env('MAIL_REPLY_TO', 'contact@golfraw.com');

  var payload = {
    from: from,
    to: [recipient.email],
    subject: message.subject,
    html: message.html,
    text: message.text,
    headers: {
      'List-Unsubscribe': '<' + unsubUrl + '>',
      'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click',
      /* Lets a client thread the series without threading it into the reader's
         actual conversations. */
      'List-Id': 'The Card <the-card.golfraw.com>'
    }
  };
  if (replyTo) payload.reply_to = replyTo;

  var res = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + cfg.env('RESEND_API_KEY', ''),
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    var detail = await res.text();
    throw new Error('Resend ' + res.status + ': ' + detail.slice(0, 200));
  }
  return await res.json();
}

/* Sends to every recipient, one at a time, and never throws on a single
   failure: one bad address must not stop the other four hundred. */
async function sendAll(recipients, buildMessage) {
  var sent = 0, failed = [], dryRun = cfg.isDryRun();

  for (var i = 0; i < recipients.length; i++) {
    var r = recipients[i];
    try {
      var message = buildMessage(r);
      if (dryRun) { sent++; continue; }
      await sendOne(r, message);
      sent++;
      /* Stay well inside Resend's rate limit without needing a dependency. */
      await new Promise(function (res) { setTimeout(res, 120); });
    } catch (e) {
      failed.push({ email: r.email, error: (e && e.message) || String(e) });
    }
  }
  return { sent: sent, failed: failed, dryRun: dryRun };
}

module.exports = { sendOne: sendOne, sendAll: sendAll, FROM: FROM };
