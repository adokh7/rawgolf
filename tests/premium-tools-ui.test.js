'use strict';

const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const failures = [];

function check(condition, message) {
  if (!condition) failures.push(message);
}

const toolPages = fs.readdirSync(root)
  .filter((name) => /^tools-.*\.html$/.test(name))
  .sort();

check(toolPages.length >= 12, `expected at least 12 interactive tool pages, found ${toolPages.length}`);

for (const page of toolPages) {
  const html = fs.readFileSync(path.join(root, page), 'utf8');
  const link = '<link rel="stylesheet" href="/public/tool-premium.css?v=2">';
  const linkIndex = html.indexOf(link);
  check(linkIndex !== -1, `${page} must load the premium stylesheet`);
  check(linkIndex > html.lastIndexOf('</style>'), `${page} must load the premium stylesheet after embedded styles`);
  check(linkIndex < html.indexOf('</head>'), `${page} must load the premium stylesheet inside <head>`);
  check(html.includes('/lib/locker/drawer.js?v=5'), `${page} must retain the shared Locker drawer`);
  check(!/border-left(?:-width)?:\s*[4-9]px/.test(html), `${page} must not retain thick side-tab accents`);
  check(!/transition:\s*(?:width|height)\b/.test(html), `${page} must not animate layout dimensions`);
}

const cssPath = path.join(root, 'public', 'tool-premium.css');
check(fs.existsSync(cssPath), 'public/tool-premium.css must exist');

if (fs.existsSync(cssPath)) {
  const css = fs.readFileSync(cssPath, 'utf8');
  const required = [
    ['--gr-forest: #0f392b', 'forest-green design token'],
    ['--gr-canvas:', 'canvas design token'],
    ['--gr-radius-xl:', 'radius design token'],
    ['.te-opt', 'Tendency Engine tap-card styles'],
    ['.fr-card', 'Field Reader ranking-card styles'],
    ['@keyframes gr-rank-settle', 'authored Field Reader ranking motion'],
    ['.answer-block + .panel', 'workspace-first visual ordering'],
    ['backdrop-filter: blur', 'blurred sticky surfaces'],
    ['env(safe-area-inset-bottom', 'mobile safe-area support'],
    [':focus-visible', 'visible keyboard focus'],
    ['prefers-reduced-motion', 'reduced-motion support'],
    ['@media (max-width: 760px)', 'mobile responsive rules']
  ];
  for (const [needle, label] of required) {
    check(css.includes(needle), `premium stylesheet must define ${label}`);
  }
}

for (const script of ['scripts/build_tendency_engine.py', 'scripts/build_field_reader.py']) {
  const source = fs.readFileSync(path.join(root, script), 'utf8');
  check(source.includes('/public/tool-premium.css?v=2'), `${script} must preserve the premium stylesheet link`);
  check(source.includes('/lib/locker/drawer.js?v=5'), `${script} must preserve the Locker scripts`);
}

const drawer = fs.readFileSync(path.join(root, 'lib/locker/drawer.js'), 'utf8');
for (const [needle, label] of [
  ['border:1px solid', 'subtle one-pixel borders'],
  ['border-radius:999px', 'pill launcher'],
  ['backdrop-filter:blur', 'blurred launcher surface'],
  ['box-shadow:', 'soft elevation'],
  ["panel.setAttribute('aria-modal', 'true')", 'modal semantics'],
  ["doc.addEventListener('keydown', onKey)", 'keyboard close and focus trap wiring'],
  ['env(safe-area-inset-bottom', 'safe-area support'],
  ['prefers-reduced-motion:reduce', 'reduced-motion support']
]) {
  check(drawer.includes(needle), `Locker drawer must retain ${label}`);
}

check(!drawer.includes("style=\"color:' + FLAG"), 'Locker cross-tool links must use the tournament-green link treatment');
check(drawer.includes('top:calc(8px + env(safe-area-inset-top,0px))'), 'mobile Locker launcher must sit in the sticky header rail');

if (failures.length) {
  console.error(`Premium tools UI contract failed (${failures.length}):`);
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log(`Premium tools UI contract passed for ${toolPages.length} tool pages.`);
