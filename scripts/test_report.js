'use strict';
var R = require('../lib/pro/report.js');
var n = 0, fails = 0;
function eq(a, b, l) { n++; if (JSON.stringify(a) !== JSON.stringify(b)) { fails++; console.log('  FAIL ' + l + '\n      got  ' + JSON.stringify(a) + '\n      want ' + JSON.stringify(b)); } }
function ok(c, l) { n++; if (!c) { fails++; console.log('  FAIL ' + l); } }
var session = { id: 's1', label: 'TrackMan import', startedAt: 1757700000000, clubs: [
  { name: 'Driver', shots: [251, 247, 255, 250, 244, 249, 252, 248] },
  { name: '7-iron', shots: [158, 157, 160, 159, 156, 161, 158, 159] },
  { name: '9-iron', shots: [135, 137, 134, 136, 133, 136, 135, 138] },
  { name: 'PW', shots: [121, 119] } ] };
var bag = { clubs: [ { name: 'Driver', carry: 250, usage: 14, conf: 5 }, { name: '3-Wood', carry: 230, usage: 1, conf: 2 }, { name: '7-iron', carry: 158, usage: 8, conf: 4 }, { name: 'LW', carry: 70, usage: 0, conf: 3 }, { name: 'GW', carry: 110, usage: null, conf: 3 } ] };
function card(id, fir, app, putts) { var holes = []; for (var i = 0; i < 18; i++) holes.push({ par: i % 3 === 0 ? 3 : 4, score: (i % 3 === 0 ? 3 : 4) + (i % 4 === 0 ? 1 : 0), fir: i % 3 === 0 ? null : fir[i % fir.length], app: app[i % app.length], putts: putts[i % putts.length] }); return { id: id, course: 'Test', playedAt: 1, holes: holes }; }
var cards = [ card('c1', ['left','hit','left'], ['hit','short','short'], [2,2,3]), card('c2', ['left','left','hit'], ['short','hit','long'], [2,1,2]), card('c3', ['left','hit','right'], ['short','short','hit'], [2,2,2]) ];

console.log('model');
var m = R.buildModel({ coach: 'Coach K', client: 'Adnan', handicap: 12.4, units: 'yards', session: session, bag: bag, scorecards: cards, notes: 'Work on GW gap.', now: 1757800000000 });
eq(m.rows.map(function (r) { return r.name; }), ['Driver', '7-iron', '9-iron', 'PW'], 'rows sorted longest first');
eq(m.rows[0].median, 250, 'driver median'); eq(m.rows[3].reliable, false, 'PW thin (2 shots)'); eq(m.session.shots, 26, 'shot count');
ok(m.verdicts.some(function (v) { return v.kind === 'gap' && /Driver/.test(v.text); }), 'driver->7-iron 92yd gap flagged as hole');
ok(!m.verdicts.some(function (v) { return /PW/.test(v.text); }), 'thin PW excluded from gap checks');
eq(m.bag.dead, ['3-Wood', 'LW'], 'dead wood: 3-Wood (1x2=2<=4) and LW (never used)'); eq(m.bag.audited, 4, 'GW without usage not audited');
eq(m.tendencies.rounds, 3, '3 rounds'); ok(m.tendencies.enough, 'enough rounds');
ok(m.tendencies.tee.enough && m.tendencies.tee.side === 'left' && m.tendencies.tee.strong, 'left tee bias called (' + JSON.stringify(m.tendencies.tee) + ')');
ok(m.tendencies.distance.enough && m.tendencies.distance.side === 'short', 'short approach bias');
ok(m.tendencies.puttsPerRound > 30 && m.tendencies.puttsPerRound < 40, 'putts per round sane (' + m.tendencies.puttsPerRound + ')');

console.log('empties');
var e = R.buildModel({});
eq(e.rows, [], 'no session -> no rows'); eq(e.bag, null, 'no bag'); eq(e.tendencies, null, 'no cards'); eq(e.verdicts, [], 'no verdicts');
var html0 = R.renderReport(e); ok(/No range session/.test(html0) && /No completed rounds/.test(html0) && /Nothing to recommend yet/.test(html0), 'empty render explains itself');

console.log('render');
var html = R.renderReport(m);
ok(/<svg class="rp-chart"/.test(html), 'chart present'); ok(/Adnan/.test(html) && /Coach K/.test(html) && /12\.4/.test(html), 'meta rendered');
ok(/Hole in the bag/.test(html) && /Passengers/.test(html) && /3-Wood, LW/.test(html), 'flags rendered');
ok(/Misses left off the tee/.test(html), 'tendency line'); ok(/Work on GW gap\./.test(html), 'notes'); ok(/nothing was uploaded/.test(html), 'privacy footer');
var xss = R.renderReport(R.buildModel({ client: '<img src=x onerror=alert(1)>', notes: '<b>hi</b>' }));
ok(xss.indexOf('<img') === -1 && xss.indexOf('&lt;img') !== -1 && xss.indexOf('<b>hi</b>') === -1, 'names and notes are escaped');

console.log('share link');
var enc = R.encodeShare(m); ok(enc.ok && /^[A-Za-z0-9_-]+$/.test(enc.payload), 'base64url payload');
var dec = R.decodeShare(enc.payload); ok(dec.ok, 'decodes'); eq(dec.model, JSON.parse(JSON.stringify(m)), 'round-trips exactly');
eq(R.decodeShare('not-a-report').ok, false, 'garbage rejected'); eq(R.decodeShare(R.encodeShare({ v: 99, rows: [] }).payload).ok, false, 'wrong version rejected');
var big = R.buildModel({ notes: new Array(1200).join('x'), session: session }); ok(R.encodeShare(big).ok, 'max-length notes still fit');
var uni = R.buildModel({ client: 'Søren Ødegård — 7°' }); eq(R.decodeShare(R.encodeShare(uni).payload).model.client, 'Søren Ødegård — 7°', 'unicode survives');

console.log('\n' + (n - fails) + '/' + n + ' checks passed' + (fails ? '  <-- FAILURES' : ''));
process.exit(fails ? 1 : 0);
