#!/usr/bin/env node
/* Render both email templates to disk for review. Sends nothing, needs no
   credentials, makes no network call — it reads the local feed file.

     node scripts/preview_email.js [outDir]

   Open the written .html files in a browser, or drop them into a client to
   check rendering. */
'use strict';
process.env.UNSUBSCRIBE_SECRET = process.env.UNSUBSCRIBE_SECRET || 'preview-only-not-a-real-secret';

var fs = require('fs'), path = require('path');
var root = path.dirname(__dirname);
var templates = require(path.join(root, 'api/_lib/templates.js'));

var out = process.argv[2] || path.join(root, '.email-preview');
fs.mkdirSync(out, { recursive: true });

var feed = JSON.parse(fs.readFileSync(path.join(root, 'data/tournament-field.json'), 'utf8'));
var ctx = {
  unsubscribeUrl: 'https://www.golfraw.com/api/unsubscribe?t=PREVIEW',
  postalAddress: '[MAIL_POSTAL_ADDRESS goes here — required by CAN-SPAM]'
};

var built = [
  ['field-board', templates.fieldBoard(feed, ctx)],
  ['practice-1', templates.practiceReview(0, ctx)],
  ['practice-2', templates.practiceReview(1, ctx)],
  ['practice-3', templates.practiceReview(2, ctx)],
  ['practice-4', templates.practiceReview(3, ctx)]
];

built.forEach(function (pair) {
  fs.writeFileSync(path.join(out, pair[0] + '.html'), pair[1].html);
  fs.writeFileSync(path.join(out, pair[0] + '.txt'), pair[1].text);
  console.log('  ' + pair[0].padEnd(14) + ' ' + JSON.stringify(pair[1].subject));
});
console.log('\n  written to ' + out);
