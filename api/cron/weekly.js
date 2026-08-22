/* ============================================================================
   WEEKLY DISPATCH — the scheduled entry point
   ----------------------------------------------------------------------------
   Vercel calls this on a schedule with `Authorization: Bearer $CRON_SECRET`.
   Nothing else can trigger it.

   One daily cron, and this decides whether today is a send day. That is done
   here rather than with two cron entries because the Vercel Hobby plan allows
   only one invocation per day per job — checking the weekday in code works on
   every plan, and makes the schedule visible in one place.

   Safety, in order:
     1. reject unauthenticated callers
     2. refuse to send live if any compliance-critical config is missing
     3. dry run unless EMAIL_DRY_RUN is explicitly "0"
     4. divert to EMAIL_TEST_RECIPIENT when one is set
     5. hard cap the recipient count
   ========================================================================== */
'use strict';

var cfg = require('../_lib/config');
var templates = require('../_lib/templates');
var subscribers = require('../_lib/subscribers');
var send = require('../_lib/send');
var tokens = require('../_lib/token');

var WEDNESDAY = 3, MONDAY = 1;

function weekIndex(d) {
  /* Stable rotation through the practice pieces: whole weeks since epoch. */
  return Math.floor(d.getTime() / (7 * 24 * 60 * 60 * 1000));
}

async function loadFeed() {
  var res = await fetch(cfg.SITE + '/data/tournament-field.json', { cache: 'no-store' });
  if (!res.ok) throw new Error('feed HTTP ' + res.status);
  return await res.json();
}

module.exports = async function handler(req, res) {
  var auth = cfg.authorised(req);
  if (!auth.ok) {
    res.status(401).json({ ok: false, error: 'unauthorised: ' + auth.reason });
    return;
  }

  var now = new Date();
  var forced = (req.query && req.query.template) || '';
  var day = now.getUTCDay();
  var which = forced || (day === WEDNESDAY ? 'field' : (day === MONDAY ? 'practice' : ''));

  if (!which) {
    res.status(200).json({ ok: true, skipped: true,
      reason: 'not a send day (UTC day ' + day + '); Wednesday sends the board, Monday the practice note' });
    return;
  }

  /* Compliance gate. A commercial email without a postal address is unlawful
     under CAN-SPAM, and an unsigned unsubscribe link is worse than none. If
     anything required is missing we refuse the live send rather than shipping
     a non-compliant message, and say exactly what is absent. */
  var missing = cfg.missingForLiveSend();
  var dryRun = cfg.isDryRun() || missing.length > 0;

  var postalAddress = cfg.env('MAIL_POSTAL_ADDRESS', '[MAIL_POSTAL_ADDRESS is not set]');

  try {
    var recipients;
    var testTo = cfg.env('EMAIL_TEST_RECIPIENT', '');
    if (testTo) {
      recipients = [{ email: testTo.toLowerCase(), firstName: '' }];
    } else if (dryRun && !cfg.env('HUBSPOT_TOKEN', '')) {
      /* A dry run should work before any credential exists, so the templates
         can be reviewed on day one. */
      recipients = [{ email: 'dry-run@example.invalid', firstName: '' }];
    } else {
      recipients = await subscribers.list();
    }

    var message;
    if (which === 'field') {
      var feed = await loadFeed();
      message = function (r) {
        return templates.fieldBoard(feed, {
          unsubscribeUrl: safeUnsub(r.email),
          postalAddress: postalAddress
        });
      };
    } else {
      message = function (r) {
        return templates.practiceReview(weekIndex(now), {
          unsubscribeUrl: safeUnsub(r.email),
          postalAddress: postalAddress
        });
      };
    }

    /* Force dry run when the config gate failed, whatever EMAIL_DRY_RUN says. */
    var prev = process.env.EMAIL_DRY_RUN;
    if (dryRun) process.env.EMAIL_DRY_RUN = '1';
    var result = await send.sendAll(recipients, message);
    process.env.EMAIL_DRY_RUN = prev;

    var sample = message(recipients[0] || { email: 'preview@example.invalid' });

    res.status(200).json({
      ok: true,
      template: which,
      dryRun: result.dryRun,
      blockedBy: missing.length ? missing : undefined,
      recipients: recipients.length,
      sent: result.sent,
      failed: result.failed,
      subject: sample.subject,
      note: result.dryRun
        ? 'DRY RUN — nothing was delivered. Set EMAIL_DRY_RUN=0 and supply the missing config to send.'
        : 'Live send completed.'
    });
  } catch (e) {
    res.status(500).json({ ok: false, template: which, error: (e && e.message) || String(e) });
  }
};

/* An unsigned link is never emitted: if the secret is missing the message
   carries a plain mailto instead, which still gives the reader a way out. */
function safeUnsub(email) {
  try { return tokens.link(email); }
  catch (e) { return 'mailto:' + (cfg.env('MAIL_REPLY_TO', 'contact@golfraw.com')) + '?subject=unsubscribe'; }
}
