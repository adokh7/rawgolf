/* ============================================================================
   EMAIL TEMPLATES
   ----------------------------------------------------------------------------
   Table-based layout with inline styles. Email clients strip <style> blocks,
   ignore flexbox and grid, and Outlook renders through Word — so this is built
   the way email actually works rather than the way the website is built.

   Every template returns { subject, html, text }. The plaintext part is real
   content, not a "view in browser" stub: a message with no usable text/plain
   alternative is a spam signal and a genuine accessibility failure.

   Palette matches the site: ink #101511, paper #F3F4F0, flag #E03E2D,
   fairway #14402A. Body copy is near-black on white for contrast, because a
   grey-on-grey email is unreadable on a phone in daylight.
   ========================================================================== */
'use strict';

var INK = '#101511', PAPER = '#F3F4F0', FLAG = '#E03E2D',
    FAIRWAY = '#14402A', GREY = '#5B665E', LINE = '#DADDD4';
var SITE = 'https://www.golfraw.com';
var LOGO = SITE + '/public/favicon-192.png';
var FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif";
var MONO = "'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace";

function esc(s) {
  return String(s === null || s === undefined ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/* ------------------------------------------------------------------ chrome */

function shell(opts) {
  var preheader = esc(opts.preheader || '');
  return '<!doctype html>' +
'<html lang="en" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office"><head>' +
'<meta charset="utf-8">' +
'<meta name="viewport" content="width=device-width,initial-scale=1">' +
'<meta name="x-apple-disable-message-reformatting">' +
'<meta name="format-detection" content="telephone=no,address=no,email=no,date=no,url=no">' +
'<meta name="color-scheme" content="light">' +
'<meta name="supported-color-schemes" content="light">' +
'<style type="text/css">' +
  ':root{color-scheme:light;supported-color-schemes:light}' +
  '.gr-logo-bg,.gr-logo-img{background-color:#ffffff!important;color:#101511!important}' +
  '@media(prefers-color-scheme:dark){.gr-logo-bg,.gr-logo-img{background-color:#ffffff!important;color:#101511!important}}' +
  '[data-ogsc] .gr-logo-bg,[data-ogsc] .gr-logo-img{background-color:#ffffff!important;color:#101511!important}' +
'</style>' +
'<!--[if mso]><noscript><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch>' +
  '</o:OfficeDocumentSettings></xml></noscript><![endif]-->' +
'<title>' + esc(opts.title) + '</title>' +
'</head>' +
'<body style="margin:0;padding:0;background:' + PAPER + ';font-family:' + FONT + ';">' +
/* The preheader is the grey line the inbox shows next to the subject. Hidden
   in the body, then padded so the client does not pull the footer into it. */
'<div style="display:none;font-size:1px;color:' + PAPER + ';line-height:1px;max-height:0;max-width:0;opacity:0;overflow:hidden;">' +
  preheader + '&#8199;&#65279;&#847; '.repeat(30) +
'</div>' +
'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="' + PAPER + '" style="background:' + PAPER + ';">' +
'<tr><td align="center" style="padding:20px 12px;">' +
'<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:600px;">' +

/* masthead */
'<tr><td class="gr-logo-bg" bgcolor="#ffffff" style="background-color:#ffffff;padding:0 22px;">' +
  '<table role="presentation" width="160" cellpadding="0" cellspacing="0" border="0" bgcolor="#ffffff" ' +
    'style="width:160px;max-width:160px;background-color:#ffffff;">' +
    '<tr><td class="gr-logo-bg" align="left" valign="middle" bgcolor="#ffffff" ' +
      'style="background-color:#ffffff;padding:0;line-height:0;font-size:0;">' +
      '<a href="' + SITE + '" aria-label="GolfRaw" style="display:block;text-decoration:none;background-color:#ffffff;">' +
        '<img class="gr-logo-img" src="' + LOGO + '" width="140" height="140" alt="GolfRaw" border="0" ' +
          'style="display:block;width:140px;max-width:140px;height:auto;border:0;outline:none;text-decoration:none;' +
          'background-color:#ffffff;color:#101511;font-family:' + FONT + ';font-size:22px;font-weight:800;line-height:1;">' +
      '</a>' +
    '</td></tr>' +
  '</table>' +
'</td></tr>' +
'<tr><td bgcolor="' + INK + '" style="background:' + INK + ';padding:8px 22px 7px;font-family:' + MONO +
  ';font-size:11px;line-height:1.4;letter-spacing:2px;text-transform:uppercase;color:#b9c1bb;">' +
  esc(opts.kicker || '') + '</td></tr>' +

/* body */
'<tr><td style="background:#ffffff;padding:20px 22px 24px;font-family:' + FONT + ';color:' + INK + ';">' +
  opts.body +
'</td></tr>' +

/* footer */
'<tr><td style="background:' + PAPER + ';padding:18px 22px;font-family:' + FONT + ';font-size:12px;line-height:1.6;color:' + GREY + ';border-top:2px solid ' + INK + ';">' +
  '<p style="margin:0 0 10px;">You are getting this because you asked for The Card on golfraw.com. ' +
    'That is the only reason.</p>' +
  '<p style="margin:0 0 10px;">' +
    '<a href="' + esc(opts.unsubscribeUrl) + '" style="color:' + INK + ';font-weight:700;">Unsubscribe in one click</a>' +
    ' &nbsp;&middot;&nbsp; <a href="' + SITE + '/privacy" style="color:' + GREY + ';">Privacy</a>' +
    ' &nbsp;&middot;&nbsp; <a href="' + SITE + '/tools" style="color:' + GREY + ';">The tools</a>' +
  '</p>' +
  '<p style="margin:0;color:' + GREY + ';">' + esc(opts.postalAddress) + '</p>' +
'</td></tr>' +

'</table></td></tr></table></body></html>';
}

function h1(t) {
  return '<h1 style="margin:0 0 14px;font-family:' + FONT + ';font-size:26px;line-height:1.2;font-weight:800;letter-spacing:-0.5px;color:' + INK + ';">' + esc(t) + '</h1>';
}
function p(t) {
  return '<p style="margin:0 0 14px;font-size:16px;line-height:1.6;color:' + INK + ';">' + t + '</p>';
}
function small(t) {
  return '<p style="margin:0 0 12px;font-size:13px;line-height:1.55;color:' + GREY + ';">' + t + '</p>';
}
function rule() {
  return '<div style="height:2px;background:' + LINE + ';margin:20px 0;line-height:2px;font-size:2px;">&nbsp;</div>';
}
function button(href, label) {
  return '<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:6px 0 18px;">' +
    '<tr><td style="background:' + FLAG + ';">' +
      '<a href="' + esc(href) + '" style="display:inline-block;padding:14px 22px;font-family:' + FONT +
      ';font-size:14px;font-weight:800;letter-spacing:0.5px;text-transform:uppercase;color:#ffffff;text-decoration:none;">' +
      esc(label) + '</a>' +
    '</td></tr></table>';
}

/* --------------------------------------------------- A: course fit board -- */

function fieldBoard(feed, ctx) {
  var ev = feed.event, players = feed.players || [];
  var demands = ev.profile || {};

  /* Rank on the course's own profile, which is what the board defaults to on
     the site. Same maths as the tool, kept deliberately short here. */
  var keys = ['distance', 'approach', 'aroundGreen', 'putting'];
  var rows = players.map(function (pl) {
    var acc = 0, tot = 0;
    keys.forEach(function (k) {
      var w = demands[k];
      if (!w) return;
      var skill = (k === 'putting') ? pl.skills.putting[ev.surface] : pl.skills[k];
      acc += w * skill; tot += w;
    });
    return { name: pl.name, archetype: !!pl.archetype, score: tot ? acc / tot : 0 };
  }).sort(function (a, b) { return b.score - a.score; }).slice(0, 8);

  var isSample = !!ev.isSample;

  var listHtml = rows.map(function (r, i) {
    return '<tr>' +
      '<td style="padding:9px 8px 9px 0;border-bottom:1px solid ' + LINE + ';font-family:' + MONO +
        ';font-size:15px;color:' + (i < 3 ? FLAG : GREY) + ';width:28px;">' + (i + 1) + '</td>' +
      '<td style="padding:9px 8px 9px 0;border-bottom:1px solid ' + LINE + ';font-size:15px;font-weight:700;color:' + INK + ';">' +
        esc(r.name) +
        (r.archetype ? '<span style="font-family:' + MONO + ';font-size:9px;letter-spacing:1px;color:' + GREY +
          ';border:1px solid ' + LINE + ';padding:1px 4px;margin-left:6px;">ARCHETYPE</span>' : '') +
      '</td>' +
      '<td align="right" style="padding:9px 0;border-bottom:1px solid ' + LINE + ';font-family:' + MONO +
        ';font-size:16px;font-weight:700;color:' + INK + ';">' + Math.round(r.score) + '</td>' +
    '</tr>';
  }).join('');

  var demandLine = 'Distance ' + (demands.distance || 0) + ' &middot; Approach ' + (demands.approach || 0) +
    ' &middot; Short game ' + (demands.aroundGreen || 0) + ' &middot; Putting ' + (demands.putting || 0);

  var body =
    h1(ev.name) +
    small(esc([ev.location, ev.dates, ev.par ? 'Par ' + ev.par : '', ev.surface ? ev.surface + ' greens' : '']
      .filter(Boolean).join(' · '))) +
    (isSample
      ? '<p style="margin:0 0 16px;padding:10px 12px;border:2px solid ' + FLAG + ';color:' + FLAG +
        ';font-size:13px;font-weight:700;line-height:1.5;">Sample course. The live feed has not been ' +
        'updated for a real event yet, so this board is illustrative.</p>'
      : '') +
    (ev.readTheCourse ? p(esc(ev.readTheCourse)) : '') +
    rule() +
    '<div style="font-family:' + MONO + ';font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:' + GREY + ';margin-bottom:4px;">What the week asks for</div>' +
    small(demandLine) +
    '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:10px 0 4px;">' +
      listHtml +
    '</table>' +
    small('Fit score out of 100 against this course profile. <b>It is not a probability.</b> ' +
      'It says the course asks for skills a player happens to have, and knows nothing about form, ' +
      'the draw, or the weather on Thursday.') +
    button(SITE + '/tools-field-reader', 'Move the sliders yourself') +
    p('The board on the site is live. Disagree with the weights &mdash; and you should &mdash; and it ' +
      're-ranks as you drag.');

  var text = [
    ev.name,
    [ev.location, ev.dates].filter(Boolean).join(' - '),
    '',
    isSample ? '(Sample course - the live feed has not been updated for a real event yet.)\n' : '',
    ev.readTheCourse || '',
    '',
    'WHAT THE WEEK ASKS FOR',
    demandLine.replace(/&middot;/g, '-'),
    '',
    'THE BOARD'
  ].concat(rows.map(function (r, i) {
    return (i + 1) + '. ' + r.name + (r.archetype ? ' [archetype]' : '') + ' - ' + Math.round(r.score);
  })).concat([
    '',
    'Fit score out of 100 against this course profile. It is not a probability.',
    '',
    'Move the sliders yourself: ' + SITE + '/tools-field-reader',
    '',
    'Unsubscribe: ' + ctx.unsubscribeUrl,
    ctx.postalAddress
  ]).join('\n');

  return {
    subject: 'The board for ' + ev.name,
    preheader: 'What this week actually asks for, and who has it.',
    kicker: 'Course fit · Wednesday',
    html: shell({
      title: 'The board for ' + ev.name,
      kicker: 'Course fit · Wednesday',
      preheader: 'What this week actually asks for, and who has it.',
      body: body,
      unsubscribeUrl: ctx.unsubscribeUrl,
      postalAddress: ctx.postalAddress
    }),
    text: text
  };
}

/* ------------------------------------------------ B: practice review ------
   Deliberately NOT personalised. Every number the tools produce lives in the
   reader's own browser and never reaches a server — that is printed on each
   tool page and is the whole architecture. A "your tendencies this week" email
   would require uploading it, which would make that promise a lie. So this is
   a prompt to go and look, plus one genuinely useful idea. */

var PRACTICE = [
  {
    title: 'Your gaps are guesses until you measure them',
    lead: 'Most bags are gapped on numbers a fitter read off a launch monitor once, indoors, on a good day.',
    body: 'Take five balls with each club on the range and write down every carry. Use the <b>median</b>, ' +
      'never the average &mdash; one thinned 7-iron drags an average down four yards and invents a gap ' +
      'you do not have. Ten to fifteen yards between irons is the target. Over 25 and there is a distance ' +
      'you cannot cover; under 8 and two clubs are doing one job.',
    cta: ['/tools-standing-order', 'Log a range session']
  },
  {
    title: 'Two pulls in a row is not a pattern',
    lead: 'The fastest way to waste a winter is practising against a miss you do not actually have.',
    body: 'A genuine directional bias needs at least three rounds and eight missed fairways behind it before ' +
      'it means anything, and even then one side has to take 60% or more. Anything less is noise. ' +
      'Track which side you miss for a month before you change a single thing in your swing.',
    cta: ['/tools-tendency-engine', 'Track your miss pattern']
  },
  {
    title: 'The shot you practise least is the one you hit most',
    lead: 'Nobody warms up by hitting forty-yard pitches, and everybody faces one on the back nine.',
    body: 'Count the shots inside 100 yards in your next three rounds. For most amateurs it is between a ' +
      'quarter and a third of the round, against maybe fourteen drives. Then compare that to how your ' +
      'last range session was actually spent.',
    cta: ['/tools-bag-audit', 'Audit what is in the bag']
  },
  {
    title: 'Range balls fly short, and that is fine',
    lead: 'Beaten-up range balls commonly carry 5 to 10% shorter than the ball you play.',
    body: 'That offset lands on every club roughly equally, so your <b>gaps</b> stay honest even when the ' +
      'absolute yardages read low. Gap on the shape of the ladder, not the height of it. What you must not ' +
      'do is take a range number onto the course and expect it to hold.',
    cta: ['/tools-plays-like', 'Adjust for the conditions']
  }
];

function practiceReview(weekIndex, ctx) {
  var item = PRACTICE[weekIndex % PRACTICE.length];
  var body =
    h1(item.title) +
    p('<b>' + item.lead + '</b>') +
    p(item.body) +
    button(SITE + item.cta[0], item.cta[1]) +
    rule() +
    small('Every one of the tools runs entirely in your browser. Nothing you enter is uploaded, which is ' +
      'also why this email cannot tell you what <i>your</i> numbers did last week &mdash; we genuinely do ' +
      'not have them, and would rather keep it that way.');

  var text = [
    item.title, '',
    item.lead, '',
    item.body.replace(/<[^>]+>/g, ''), '',
    SITE + item.cta[0], '',
    'Every tool runs entirely in your browser. Nothing you enter is uploaded, which is also why this',
    'email cannot tell you what your numbers did last week - we do not have them.', '',
    'Unsubscribe: ' + ctx.unsubscribeUrl,
    ctx.postalAddress
  ].join('\n');

  return {
    subject: item.title,
    preheader: item.lead,
    kicker: 'Practice · Monday',
    html: shell({
      title: item.title,
      kicker: 'Practice · Monday',
      preheader: item.lead,
      body: body,
      unsubscribeUrl: ctx.unsubscribeUrl,
      postalAddress: ctx.postalAddress
    }),
    text: text
  };
}

module.exports = { fieldBoard: fieldBoard, practiceReview: practiceReview, PRACTICE: PRACTICE, esc: esc };
