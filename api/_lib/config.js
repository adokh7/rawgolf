/* ============================================================================
   WEEKLY EMAIL — CONFIGURATION AND SAFETY GATES
   ----------------------------------------------------------------------------
   Every value here comes from an environment variable. Nothing is hard-coded,
   and no credential is ever committed to this repository.

   Set these in the Vercel project (Settings -> Environment Variables):

     CRON_SECRET            required. Vercel sends it as `Authorization: Bearer`
                            on scheduled invocations. Without it the endpoint
                            refuses every request, so nobody can trigger a send
                            by hitting the URL.
     RESEND_API_KEY         required to send.
     MAIL_FROM              e.g. "GOLFRAW <the-card@golfraw.com>". The domain
                            must be verified in Resend or everything bounces.
     MAIL_POSTAL_ADDRESS    required to send. A real postal address is a legal
                            requirement for commercial email under CAN-SPAM,
                            and this pipeline refuses to send live without one
                            rather than quietly shipping non-compliant mail.
     UNSUBSCRIBE_SECRET     required. Signs unsubscribe links so they cannot be
                            forged or enumerated.
     HUBSPOT_TOKEN          required to read the subscriber list. A private-app
                            token with `crm.objects.contacts.read`.

   Optional:
     EMAIL_DRY_RUN          "1" (default) renders and logs without sending.
                            Must be explicitly set to "0" to send real mail.
     EMAIL_TEST_RECIPIENT   when set, the send goes ONLY to this address no
                            matter what the subscriber list says.
     EMAIL_MAX_RECIPIENTS   hard cap per run. Default 500.
   ========================================================================== */
'use strict';

var SITE = 'https://www.golfraw.com';

function env(name, fallback) {
  var v = process.env[name];
  return (v === undefined || v === '') ? fallback : v;
}

/* Dry run is the default in both directions: an unset variable, a typo, or a
   value that is not exactly "0" all mean "do not send". Sending real mail to
   real people should require a deliberate act, not the absence of one. */
function isDryRun() {
  return env('EMAIL_DRY_RUN', '1') !== '0';
}

function maxRecipients() {
  var n = parseInt(env('EMAIL_MAX_RECIPIENTS', '500'), 10);
  return (isFinite(n) && n > 0) ? n : 500;
}

/* Everything that must be present before a single live message goes out.
   Returns the list of what is missing so the caller can say so precisely. */
function missingForLiveSend() {
  var need = ['RESEND_API_KEY', 'MAIL_FROM', 'MAIL_POSTAL_ADDRESS', 'UNSUBSCRIBE_SECRET'];
  var missing = [];
  for (var i = 0; i < need.length; i++) {
    if (!env(need[i], '')) missing.push(need[i]);
  }
  return missing;
}

/* Constant-time-ish comparison so the secret cannot be probed by timing. */
function safeEqual(a, b) {
  a = String(a || ''); b = String(b || '');
  if (a.length !== b.length) return false;
  var out = 0;
  for (var i = 0; i < a.length; i++) out |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return out === 0;
}

/* Vercel Cron sends `Authorization: Bearer $CRON_SECRET`. Anything else is
   refused, including an unauthenticated browser hitting the URL. */
function authorised(req) {
  var secret = env('CRON_SECRET', '');
  if (!secret) return { ok: false, reason: 'CRON_SECRET is not configured' };
  var header = (req.headers && (req.headers.authorization || req.headers.Authorization)) || '';
  /* Only the exact form Vercel sends is accepted. A bare token would also be
     safe, since possession of the secret is the credential, but accepting more
     shapes than the one contract is surface area for nothing. */
  var m = /^Bearer\s+(.+)$/i.exec(header);
  if (!m) return { ok: false, reason: 'missing bearer token' };
  if (!safeEqual(m[1], secret)) return { ok: false, reason: 'bad bearer token' };
  return { ok: true };
}

module.exports = {
  SITE: SITE,
  env: env,
  isDryRun: isDryRun,
  maxRecipients: maxRecipients,
  missingForLiveSend: missingForLiveSend,
  authorised: authorised,
  safeEqual: safeEqual
};
