'use strict';

// GolfrawLocker.setUnits: switching the shared yards/metres preference must
// convert stored distances (bag carries, range-session shots), never relabel
// them, and repeated switching must not creep. Runs the real schema.js and
// store.js in a sandbox with no IndexedDB, so the localStorage mirror is used.

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const failures = [];
let checks = 0;
function check(condition, message) { checks++; if (!condition) failures.push(message); }

function sandbox() {
  const store = {};
  const ctx = {
    console, Promise, Math, JSON, Date, Object, Array, String, Number, isFinite, parseFloat, parseInt,
    setTimeout, clearTimeout,
    localStorage: {
      getItem: (k) => (k in store ? store[k] : null),
      setItem: (k, v) => { store[k] = String(v); },
      removeItem: (k) => { delete store[k]; }
    }
  };
  ctx.window = ctx;
  vm.createContext(ctx);
  for (const f of ['schema.js', 'store.js']) {
    vm.runInContext(fs.readFileSync(path.join(__dirname, '..', 'lib', 'locker', f), 'utf8'), ctx, { filename: f });
  }
  return ctx.GolfrawLocker;
}

(async () => {
  const L = sandbox();
  check(L && typeof L.setUnits === 'function', 'the Locker exposes setUnits');
  await L.ready();
  const events = [];
  L.subscribe((k) => events.push(k));

  await L.saveActiveBagClubs([
    { name: 'Driver', carry: 245, usage: 12, conf: 4 },
    { name: '7-iron', carry: 150, usage: 7, conf: 5 },
    { name: 'PW', carry: 110, usage: 8, conf: 5 },
    { name: 'Spare', carry: null, usage: null, conf: 3 }
  ]);
  await L.saveSession({ label: 'Tuesday', clubs: [{ name: '7-iron', shots: [148, 150, 152] }] });

  check((await L.getProfile()).units === 'yards', 'profiles start in yards');
  await L.setUnits('meters');
  let bag = await L.getActiveBag();
  let ses = (await L.listSessions())[0];
  check((await L.getProfile()).units === 'meters', 'the profile now says metres');
  check(JSON.stringify(bag.clubs.map((c) => c.carry)) === JSON.stringify([224, 137.2, 100.6, null]),
    'bag carries are converted, not relabelled: ' + JSON.stringify(bag.clubs.map((c) => c.carry)));
  check(JSON.stringify(ses.clubs[0].shots) === JSON.stringify([135.3, 137.2, 139]),
    'range shots are converted too: ' + JSON.stringify(ses.clubs[0].shots));
  check(bag.clubs[0].name === 'Driver' && bag.clubs[0].usage === 12 && bag.clubs[0].conf === 4, 'nothing but the distances changes');
  check(events.includes('bags') && events.includes('sessions') && events.includes('profile'), 'open tools and the drawer hear about it');

  await L.setUnits('meters');
  bag = await L.getActiveBag();
  check(bag.clubs[0].carry === 224, 'setting the same unit again converts nothing');

  await L.setUnits('yards');
  bag = await L.getActiveBag();
  ses = (await L.listSessions())[0];
  check(JSON.stringify(bag.clubs.map((c) => c.carry)) === JSON.stringify([245, 150, 110, null]), 'back in yards the bag reads as entered');
  check(JSON.stringify(ses.clubs[0].shots) === JSON.stringify([148, 150, 152]), 'and so do the shots');

  for (let i = 0; i < 40; i++) await L.setUnits(i % 2 ? 'yards' : 'meters');
  bag = await L.getActiveBag();
  check(bag.clubs.every((c, i) => c.carry === null || Math.abs(c.carry - [245, 150, 110][i]) <= 0.1),
    'forty switches later every carry is within a tenth of what was entered: ' + JSON.stringify(bag.clubs.map((c) => c.carry)));

  let refused = false;
  try { await L.setUnits('furlongs'); } catch (e) { refused = true; }
  check(refused, 'unknown units are refused');

  if (failures.length) {
    console.error('Locker units contract failed ' + failures.length + ' of ' + checks + ' checks:\n- ' + failures.join('\n- '));
    process.exit(1);
  }
  console.log('Locker units contract passed ' + checks + ' checks.');
})().catch((e) => { console.error(e); process.exit(1); });
