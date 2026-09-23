'use strict';

// The Standing Order logs shots in whichever unit the Locker profile holds, so
// only its words change with the unit — except the two gap thresholds, which
// are yards and must stay yards: 25 yards is 22.9 metres, never 25 metres.
//
// The helpers are lifted out of the shipped page (they live inside the page's
// own script, not a module) and run here against a fake document, so this pins
// what golfers actually get rather than what the generator meant to write.

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const PAGE = fs.readFileSync(path.join(__dirname, '..', 'tools-standing-order.html'), 'utf8');

const failures = [];
let checks = 0;
function check(condition, message) { checks++; if (!condition) failures.push(message); }

// GAP_HOLE/GAP_DUP through the units block: everything the unit words rest on.
const block = PAGE.slice(PAGE.indexOf('var GAP_HOLE ='), PAGE.indexOf('/* ==================== STATISTICS'));
check(block.length > 400 && block.indexOf('function applyUnits') !== -1,
  'the page still carries its units block (found ' + block.length + ' chars)');

function el() {
  return { textContent: '' };
}
const dom = { unitLabel: el(), thMedianU: el(), thGapU: el() };
const ctx = { Math: Math, $: function (id) { return dom[id] || null; } };
vm.createContext(ctx);
vm.runInContext(block, ctx, { filename: 'standing-order-units' });

/* ---- yards, the default ------------------------------------------------ */
ctx.applyUnits('yards');
check(ctx.metric() === false, 'yards is not metric');
check(ctx.uShort() === 'yd', 'yards short label');
check(ctx.uWord(1) === 'yard' && ctx.uWord(2) === 'yards', 'yard singular and plural');
check(ctx.thr(ctx.GAP_HOLE) === 25 && ctx.thr(ctx.GAP_DUP) === 8, 'in yards the thresholds are the constants');
check(ctx.thrWords(25) === '25 yards' && ctx.thrWords(8) === '8 yards', 'and read plainly: ' + ctx.thrWords(25));
check(dom.unitLabel.textContent === 'yards carry', 'the readout says yards carry');
check(dom.thMedianU.textContent === '(yd)' && dom.thGapU.textContent === '(yd)', 'the table headers say (yd)');

/* ---- metres ------------------------------------------------------------ */
ctx.applyUnits('meters');
check(ctx.metric() === true, 'meters is metric');
check(ctx.uShort() === 'm', 'metric short label');
check(ctx.uWord(1) === 'metre' && ctx.uWord(2) === 'metres', 'metre singular and plural, British spelling');
check(ctx.thr(ctx.GAP_HOLE) === 22.9, 'a 25-yard hole is 22.9 metres, not 25: ' + ctx.thr(ctx.GAP_HOLE));
check(ctx.thr(ctx.GAP_DUP) === 7.3, 'an 8-yard overlap is 7.3 metres: ' + ctx.thr(ctx.GAP_DUP));
check(ctx.thrWords(25) === '22.9 metres (25 yards)', 'metric keeps the yard figure visible: ' + ctx.thrWords(25));
check(dom.unitLabel.textContent === 'metres carry', 'the readout switches to metres carry');
check(dom.thMedianU.textContent === '(m)' && dom.thGapU.textContent === '(m)', 'the table headers say (m)');

/* ---- anything else is yards, never a blank or a crash ------------------ */
ctx.applyUnits(undefined);
check(ctx.metric() === false && dom.unitLabel.textContent === 'yards carry', 'an unknown unit falls back to yards');

/* ---- the thresholds are never compared in the raw ---------------------- */
const verdicts = PAGE.slice(PAGE.indexOf('function verdicts('), PAGE.indexOf('SVG DISPERSION CHART'));
check(/gap > hole/.test(verdicts) && /gap < dup/.test(verdicts), 'gaps are compared against the converted thresholds');
check(!/\byards\b/.test(verdicts.replace(/\(' \+ yd \+ ' yards\)/g, '')),
  'no verdict hard-codes the word yards');
check(/uWord\(/.test(verdicts), 'verdicts take their unit word from the profile');

/* ---- a unit change while the page is open ------------------------------ */
const boot = PAGE.slice(PAGE.indexOf('function syncUnits('), PAGE.indexOf('function setState('));
check(/getOrStartSession/.test(boot), 'a unit change re-reads the converted session before the next write');
check(/writeChain = writeChain/.test(boot), 'and joins the write chain rather than racing it');
check(/showResults\(true\)/.test(boot), 'results redraw quietly: no scroll, no second completion event');
check(/else if \(kind === 'profile'\) syncUnits\(\);/.test(PAGE), 'the page listens for a profile change');

if (failures.length) {
  console.error('Standing Order units failed ' + failures.length + ' of ' + checks + ' checks:\n- ' + failures.join('\n- '));
  process.exit(1);
}
console.log('Standing Order units passed ' + checks + ' checks.');
