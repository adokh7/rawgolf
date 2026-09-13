/* Unit tests for lib/pro/lm-import.js. Run: node scripts/test_lm_import.js
   The fixtures are synthetic exports shaped like each vendor's real header
   vocabulary, plus the edge cases that break naive CSV parsing. */
'use strict';
var LM = require('../lib/pro/lm-import.js');
var fails = 0, n = 0;
function eq(a, b, label) { n++; var ok = JSON.stringify(a) === JSON.stringify(b); if (!ok) { fails++; console.log('  FAIL ' + label + '\n      got  ' + JSON.stringify(a) + '\n      want ' + JSON.stringify(b)); } }
function ok(c, label) { n++; if (!c) { fails++; console.log('  FAIL ' + label); } }
function clubMap(res) { var o = {}; res.clubs.forEach(function (c) { o[c.name] = c.shots.length; }); return o; }

/* --- TrackMan-shaped: preamble, mono column names, avg/std rows --- */
var trackman = [
  'Player,Adnan', 'Date,2026-09-12', '',
  'Club,Club Speed,Attack Angle,Ball Speed,Smash Factor,Launch Angle,Spin Rate,Carry,Total,Side',
  '7 Iron,84.1,-3.2,116.0,1.38,17.1,6500,158.2,166.0,-4.1',
  '7 Iron,83.5,-3.0,115.1,1.38,16.8,6600,156.9,165.1,2.0',
  '7 Iron,85.0,-2.9,117.2,1.38,17.5,6400,160.4,168.3,-1.0',
  '7 Iron,80.1,-5.0,101.0,1.26,12.0,4000,101.0,120.0,10.0',   /* fat one */
  '7 Iron,84.4,-3.1,116.5,1.38,17.0,6550,159.0,167.2,0.5',
  'Avg,83.4,-3.4,113.2,1.36,16.1,6010,147.1,157.3,1.5',
  'Std Dev,1.9,0.9,6.8,0.05,2.2,1090,25.3,20.4,5.2',
  'Driver,104.2,2.1,152.3,1.46,12.5,2400,251.0,270.1,-8.0',
  'Driver,103.0,1.8,150.9,1.46,12.0,2500,247.5,266.0,12.0',
  'Driver,105.5,2.4,154.0,1.46,12.9,2300,255.2,275.3,-3.0',
  'Driver,104.0,2.0,152.0,1.46,12.4,2450,250.1,269.0,1.0',
  'Driver,102.2,1.5,149.5,1.46,11.8,2600,244.0,262.7,5.5'
].join('\r\n');
var r = LM.run(trackman);
console.log('TrackMan-shaped'); eq(r.parsed.vendor.id, 'trackman', 'vendor'); eq(r.mapping.club, 0, 'club col'); eq(r.parsed.headers[r.mapping.carry], 'Carry', 'carry col');
eq(clubMap(r), { '7-iron': 4, 'Driver': 5 }, 'clubs+counts (fat 7i dropped)'); eq(r.stats.summary, 2, 'summary rows skipped'); eq(r.clubs[0].dropped, [101], 'dropped mishit');
ok(r.mapping.units === null, 'units unknown when header has no unit (ask the reader)');

/* --- Foresight-shaped, yards in header, semicolon delimiter --- */
var foresight = [
  'Shot;Club;Ball Speed (mph);Launch Angle (Vertical);Club Head Speed (mph);Smash Factor;Carry Distance (yds);Run Distance (yds);Total Distance (yds);Offline Distance (yds);Peak Height (ft);Hang Time (s)',
  '1;PW;96.2;28.1;72.0;1.34;121;5;126;-3;30;5.4',
  '2;PW;95.0;28.5;71.1;1.34;119;6;125;2;29;5.3',
  '3;PW;97.1;27.8;72.8;1.33;123;4;127;-1;31;5.5',
  '4;PW;96.5;28.0;72.3;1.33;122;5;127;0;30;5.4',
  '5;56;84.0;33.0;66.0;1.27;92;2;94;1;26;5.0',
  '6;56;83.1;33.5;65.2;1.27;90;2;92;-2;25;4.9',
  '7;56;85.0;32.8;66.9;1.27;94;3;97;1;27;5.1',
  '8;56;84.4;33.1;66.4;1.27;93;2;95;0;26;5.0'
].join('\n');
r = LM.run(foresight);
console.log('Foresight-shaped'); eq(r.parsed.delimiter, ';', 'semicolon sniffed'); eq(r.parsed.vendor.id, 'foresight', 'vendor');
eq(r.parsed.headers[r.mapping.carry], 'Carry Distance (yds)', 'carry not total/run/offline'); eq(r.mapping.units, 'yards', 'units from header');
eq(clubMap(r), { 'PW': 4, 'SW': 4 }, '56° wedge -> SW');

/* --- Garmin-shaped: Club Type column, Date/Time, meters, quoted club name --- */
var garmin = [
  'Date/Time,Club Type,Club Name,Club Speed,Ball Speed,Launch Angle,Launch Direction,Spin Rate,Spin Axis,Backspin,Sidespin,Carry Distance,Total Distance,Smash Factor',
  'yyyy-mm-dd,,,km/h,km/h,deg,deg,rpm,deg,rpm,rpm,m,m,',
  '"2026-09-10 18:02","Iron","7 Iron, Callaway",135.1,187.0,17.0,-1.0,6400,-2,6390,-220,145,152,1.38',
  '"2026-09-10 18:03","Iron","7 Iron, Callaway",134.0,185.9,16.8,0.5,6500,1,6499,60,144,151,1.39',
  '"2026-09-10 18:04","Iron","7 Iron, Callaway",136.2,188.4,17.2,-0.3,6350,-1,6349,-90,146,153,1.38',
  '"2026-09-10 18:05","Iron","7 Iron, Callaway",135.5,187.6,17.1,0.1,6420,0,6420,10,145,152,1.38',
  '"2026-09-10 18:06","Wood","3 Wood",158.0,232.0,11.0,1.0,3400,3,3395,180,205,225,1.47',
  '"2026-09-10 18:07","Wood","3 Wood",159.1,233.5,11.2,-0.5,3300,-2,3298,-110,207,227,1.47',
  '"2026-09-10 18:08","Wood","3 Wood",157.5,231.0,10.9,0.3,3450,1,3449,55,204,224,1.47',
  '"2026-09-10 18:09","Wood","3 Wood",158.4,232.6,11.1,0.0,3380,0,3380,0,206,226,1.47'
].join('\n');
r = LM.run(garmin);
console.log('Garmin-shaped'); eq(r.parsed.vendor.id, 'garmin', 'vendor'); ok(r.parsed.unitsRow !== null, 'units row detected'); eq(r.mapping.units, 'meters', 'meters from units row');
eq(r.parsed.headers[r.mapping.club], 'Club Name', 'prefers the specific club name over Club Type');
var seven = r.clubs.filter(function (c) { return c.name === '7-iron'; })[0];
ok(seven && seven.shots.length === 4 && seven.shots[0] === Math.round(145 * 1.0936133), '"7 Iron, Callaway" (quoted) -> 7-iron, m->yd (' + (seven && seven.shots[0]) + ')');
eq(clubMap(r), { '7-iron': 4, '3-Wood': 4 }, 'clubs');

/* --- Rapsodo-shaped: Club Type only, Club Brand/Model noise --- */
var rapsodo = [
  'Club Type,Club Brand,Club Model,Carry Distance,Total Distance,Ball Speed,Launch Angle,Launch Direction,Apex,Side Carry,Club Speed,Smash Factor,Descent Angle',
  '9 Iron,Titleist,T200,135,140,105,22,-1,28,-2,79,1.33,45',
  '9 Iron,Titleist,T200,137,142,106,22,1,29,1,80,1.33,45',
  '9 Iron,Titleist,T200,134,139,104,21,0,27,0,78,1.33,44',
  '9 Iron,Titleist,T200,136,141,105,22,0,28,1,79,1.33,45',
  'Hybrid 4,Ping,G430,190,205,132,13,-2,25,-6,95,1.39,38',
  'Hybrid 4,Ping,G430,193,208,133,13,1,26,3,96,1.39,38',
  'Hybrid 4,Ping,G430,188,203,131,13,0,25,0,94,1.39,38'
].join('\n');
r = LM.run(rapsodo);
console.log('Rapsodo-shaped'); eq(r.parsed.vendor.id, 'rapsodo', 'vendor'); eq(r.parsed.headers[r.mapping.club], 'Club Type', 'club type used, brand/model ignored');
eq(r.parsed.headers[r.mapping.carry], 'Carry Distance', 'carry, not Side Carry'); eq(clubMap(r), { '9-iron': 4, '4-Hybrid': 3 }, 'Hybrid 4 -> 4-Hybrid');

/* --- FlightScope-shaped (basic Mevo) + unknown club kept + no header preamble --- */
var mevo = [
  'Ball Speed,Club Speed,Smash Factor,Carry Distance,Launch Angle V,Spin,Height,Time,Club',
  '150,102,1.47,240,12,2500,30,6.1,Dr',
  '151,103,1.47,243,12,2450,31,6.2,Dr',
  '149,101,1.47,238,12,2550,30,6.0,Dr',
  '148,100,1.48,236,12,2600,29,6.0,Dr',
  '118,82,1.44,170,15,5200,26,5.6,Mystery Stick',
  '117,81,1.44,168,15,5300,26,5.5,Mystery Stick',
  '119,83,1.43,172,15,5100,27,5.7,Mystery Stick'
].join('\n');
r = LM.run(mevo);
console.log('FlightScope-shaped'); eq(r.parsed.vendor.id, 'flightscope', 'vendor'); eq(r.mapping.club, 8, 'club is the last column');
eq(clubMap(r), { 'Driver': 4, 'Mystery Stick': 3 }, 'Dr -> Driver; unknown kept'); eq(r.stats.unknownClubs, ['Mystery Stick'], 'unknown reported');

/* --- Generic: BOM, tabs, total-only (no carry) flagged, putter skipped, >50 shots trimmed --- */
var rows = ['﻿Club\tTotal (m)'];
for (var i = 0; i < 60; i++) rows.push('6i\t' + (150 + (i % 7)));
rows.push('Putter\t12');
r = LM.run(rows.join('\n'));
console.log('Generic edge cases'); eq(r.parsed.delimiter, '\t', 'tab sniffed'); ok(r.mapping.carryIsTotal, 'total used as carry is flagged');
eq(r.mapping.units, 'meters', 'meters from header'); eq(r.stats.putter, 1, 'putter skipped'); eq(r.clubs[0].shots.length, 50, 'capped at 50'); eq(r.clubs[0].trimmed, 10, 'trimmed count');

/* --- Override: reader corrects the mapping + forces units --- */
r = LM.run(trackman, { carry: 8, units: 'meters', dropMishits: false });
console.log('Overrides'); eq(r.parsed.headers[r.mapping.carry], 'Total', 'carry override honoured'); eq(clubMap(r)['7-iron'], 5, 'mishit filter off keeps all 5');
ok(r.clubs[0].shots[0] === Math.round(166.0 * 1.0936133), 'forced meters converted');

/* --- Club normaliser table --- */
console.log('Club names');
[['Driver','Driver'],['1W','Driver'],['3 Wood','3-Wood'],['5w','5-Wood'],['Wood 7','7-Wood'],['4H','4-Hybrid'],['Rescue 3','3-Hybrid'],['3 Hybrid','3-Hybrid'],
 ['7i','7-iron'],['Iron 5','5-iron'],['9-Iron','9-iron'],['PW','PW'],['Pitching Wedge','PW'],['AW','GW'],['Gap Wedge','GW'],['52','GW'],['SW','SW'],['56°','SW'],['60 deg','LW'],['Lob Wedge','LW'],['Putter',null]
].forEach(function (p) { var c = LM.normalizeClub(p[0]); eq(c.skip ? null : c.name, p[1], p[0]); });

/* --- Empty / garbage --- */
eq(LM.run('').ok, false, 'empty file rejected'); r = LM.run('hello world\nfoo bar'); eq(r.clubs.length, 0, 'garbage yields no clubs, no throw');

console.log('\n' + (n - fails) + '/' + n + ' checks passed' + (fails ? '  <-- FAILURES' : ''));
process.exit(fails ? 1 : 0);
