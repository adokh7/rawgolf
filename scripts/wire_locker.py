#!/usr/bin/env python3
"""Wire the Locker storage layer + drawer into the tool pages.

Idempotent: re-running replaces the managed blocks rather than stacking them.
"""
import glob, io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Bumped whenever a file under lib/locker/ changes. vercel.json serves .js with
# a one-year immutable Cache-Control, so without a new query string readers keep
# running the old locker until their cache expires.
VER = '12'

START = '<!-- LOCKER:START -->'
END = '<!-- LOCKER:END -->'

LOADER = """  <!-- The Locker: local-first storage (IndexedDB) + the My Bag drawer.
       Deferred so it never competes with first paint; execution order is
       guaranteed by `defer`, which the storage layer relies on. -->
  <script src="/lib/locker/schema.js?v={v}" defer></script>
  <script src="/lib/locker/store.js?v={v}" defer></script>
  <script src="/lib/locker/drawer.js?v={v}" defer></script>
"""

BRIDGE_BAG = """  <script>
    /* ---- Locker bridge: Tool #07 Bag Audit ------------------------------
       The fourteen slots are the edit surface; the Locker is the record of
       truth that other tools and the drawer read. Writes are debounced so a
       burst of keystrokes is one transaction, and each club is validated
       individually — one nonsense yardage must not cost the reader the other
       thirteen clubs. Stored carries are in the profile's units; the page holds
       yards, so each write reads the profile first and converts in the same
       step (a switch halfway through an edit cannot convert twice). */
    window.addEventListener('DOMContentLoaded', function () {
      var L = window.GolfrawLocker;
      if (!L || typeof SLOTS === 'undefined') return;
      var timer = null, hydrating = false, missedWrite = false;

      function collect(units) {
        var clubs = [];
        for (var i = 0; i < SLOTS; i++) {
          var name = String($('n' + i).value || '').replace(/^\\s+|\\s+$/g, '');
          var carry = typeof bagCarryOut === 'function' ? bagCarryOut(i, units) : L.util.toNum($('y' + i).value);
          if (!name && carry === null) continue;
          var conf = L.util.toInt($('c' + i).value);
          var candidate = {
            name: name.slice(0, 40),
            carry: carry,
            usage: L.util.toInt($('u' + i).value),
            conf: conf === null ? 3 : Math.min(5, Math.max(1, conf))
          };
          var parsed = L.schemas.Club.parse(candidate, '$');
          if (parsed.ok) clubs.push(parsed.value);
        }
        return clubs;
      }

      function push() {
        /* A keystroke during hydration must not be lost: remember it and
           replay once hydration finishes, otherwise the reader's first edit
           after load silently fails to reach the Locker. */
        if (hydrating) { missedWrite = true; return; }
        if (timer) clearTimeout(timer);
        timer = setTimeout(function () {
          L.getProfile().then(function (p) {
            return L.saveActiveBagClubs(collect(p.units));
          })['catch'](function () { /* local-only; the form still works */ });
        }, 400);
      }

      function hydrate(force) {
        return Promise.all([L.getActiveBag(), L.getProfile()]).then(function (res) {
          var bag = res[0], units = res[1] && res[1].units;
          var clubs = (bag && bag.clubs) || [];
          if (!clubs.length && !force) return;
          hydrating = true;
          for (var i = 0; i < SLOTS; i++) {
            var c = clubs[i];
            if (!c) {
              if (!force) continue;
              $('n' + i).value = ''; $('u' + i).value = '';
              if (typeof bagCarryIn === 'function') bagCarryIn(i, null, units); else $('y' + i).value = '';
              $('c' + i).value = '3';
              continue;
            }
            $('n' + i).value = c.name || '';
            if (typeof bagCarryIn === 'function') bagCarryIn(i, c.carry, units);
            else $('y' + i).value = c.carry === null ? '' : c.carry;
            $('u' + i).value = c.usage === null ? '' : c.usage;
            $('c' + i).value = c.conf || 3;
          }
          hydrating = false;
          updateTally();
          if (missedWrite) { missedWrite = false; push(); }
        })['catch'](function () { hydrating = false; missedWrite = false; });
      }

      $('bagList').addEventListener('input', push);
      $('bagList').addEventListener('change', push);
      L.ready().then(function () { return hydrate(false); });
      L.subscribe(function (kind) { if (kind === 'import' || kind === 'clear') hydrate(true); });
    });
  </script>
"""

BRIDGE_PLAYSLIKE = """  <script>
    /* ---- Locker bridge: Tool #05 Plays Like -----------------------------
       Conditions are this tool's own state, so they live in toolState rather
       than in a shared schema. They are stored in the model's own units
       (yards, °F, feet, mph) with the temperature and wind units the golfer
       picked, so switching yards and metres later cannot change what they
       mean. The page owns the conversion (plState / plApply). */
    window.addEventListener('DOMContentLoaded', function () {
      var L = window.GolfrawLocker;
      if (!L || typeof plState !== 'function' || typeof plApply !== 'function') return;
      var TOOL = 'plays-like';
      var timer = null, hydrating = false, missedWrite = false;

      function push() {
        /* A keystroke during hydration must not be lost: remember it and
           replay once hydration finishes, otherwise the reader's first edit
           after load silently fails to reach the Locker. */
        if (hydrating) { missedWrite = true; return; }
        if (timer) clearTimeout(timer);
        timer = setTimeout(function () {
          L.setToolState(TOOL, plState())['catch'](function () { });
        }, 400);
      }

      function hydrate(force) {
        return L.getToolState(TOOL).then(function (d) {
          if (!d && !force) return;
          hydrating = true;
          plApply(d || null);
          hydrating = false;
          if (missedWrite) { missedWrite = false; push(); }
        })['catch'](function () { hydrating = false; missedWrite = false; });
      }

      // Typing, the direction and humidity buttons, the quick picks and the
      // unit switches all live in the conditions panel.
      $('plInputs').addEventListener('input', push);
      $('plInputs').addEventListener('click', push);

      L.ready().then(function () { return hydrate(false); });
      L.subscribe(function (kind) { if (kind === 'import' || kind === 'clear') hydrate(true); });
    });
  </script>
"""

BRIDGE_HANDICAP = """  <script>
    /* ---- Locker bridge: Tool #04 Handicap Lie Detector ------------------
       Rounds are shared data, so they go to the rounds store rather than to
       this tool's scratch state, and the claimed handicap belongs on the
       profile. The tool owns the whole list, so a write replaces it. */
    window.addEventListener('DOMContentLoaded', function () {
      var L = window.GolfrawLocker;
      if (!L) return;
      var timer = null, hydrating = false, missedWrite = false;

      function collect() {
        var rows = [];
        $('rounds').querySelectorAll('.rnd').forEach(function (r) {
          var rec = {
            score: L.util.toInt(r.querySelector('.sc').value),
            cr: L.util.toNum(r.querySelector('.cr').value),
            slope: L.util.toInt(r.querySelector('.sl').value)
          };
          if (rec.score === null && rec.cr === null && rec.slope === null) return;
          /* Out-of-range entries are the reader mid-typing; drop them from the
             saved record instead of failing the whole write. */
          var probe = L.schemas.Round.parse({ id: 'probe', seq: 0, score: rec.score, cr: rec.cr, slope: rec.slope }, '$');
          if (probe.ok) rows.push(rec);
        });
        return rows;
      }

      function push() {
        /* A keystroke during hydration must not be lost: remember it and
           replay once hydration finishes, otherwise the reader's first edit
           after load silently fails to reach the Locker. */
        if (hydrating) { missedWrite = true; return; }
        if (timer) clearTimeout(timer);
        timer = setTimeout(function () {
          var hcp = L.util.toNum($('claimed').value);
          L.saveRounds(collect())['catch'](function () { });
          if (hcp === null || (hcp >= -10 && hcp <= 54)) {
            L.saveProfile({ claimedHandicap: hcp })['catch'](function () { });
          }
        }, 500);
      }

      function hydrate(force) {
        return Promise.all([L.listRounds(), L.getProfile()]).then(function (res) {
          var rounds = res[0], profile = res[1];
          if (!rounds.length && !force) {
            if (profile.claimedHandicap !== null) $('claimed').value = profile.claimedHandicap;
            return;
          }
          hydrating = true;
          $('rounds').innerHTML = '';
          for (var i = 0; i < rounds.length && i < MAX_ROUNDS; i++) {
            addRow({
              score: rounds[i].score === null ? null : rounds[i].score,
              cr: rounds[i].cr === null ? null : rounds[i].cr,
              slope: rounds[i].slope === null ? null : rounds[i].slope
            });
          }
          while ($('rounds').querySelectorAll('.rnd').length < MIN_ROUNDS) addRow();
          $('claimed').value = profile.claimedHandicap === null ? '' : profile.claimedHandicap;
          renumber();
          hydrating = false;
          refresh();
          if (missedWrite) { missedWrite = false; push(); }
        })['catch'](function () { hydrating = false; missedWrite = false; });
      }

      $('rounds').addEventListener('input', push);
      $('rounds').addEventListener('change', push);
      $('claimed').addEventListener('input', push);

      L.ready().then(function () { return hydrate(false); });
      L.subscribe(function (kind) { if (kind === 'import' || kind === 'clear') hydrate(true); });
    });
  </script>
"""

BRIDGES = {
    'tools-bag-audit.html': BRIDGE_BAG,
    'tools-plays-like.html': BRIDGE_PLAYSLIKE,
    'tools-handicap-detector.html': BRIDGE_HANDICAP,
}

ADS_MARKER = '  <!-- Ads + consent are deferred'


def build_block(name):
    body = LOADER.format(v=VER)
    if name in BRIDGES:
        body += BRIDGES[name]
    return START + '\n' + body + END + '\n'


LOCKER_SRC = re.compile(r'(/lib/locker/(?:schema|store|drawer)\.js\?v=)\d+')


def refresh_other_pages(skip):
    """Articles and hubs carry a Locker block from an earlier site-wide pass.
    They are not rewired here, but their asset version must follow VER: .js is
    served immutable, so a stale ?v= keeps a returning reader's drawer on old
    Locker code (for example one that relabels units instead of converting)."""
    changed = []
    for path in sorted(glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True)):
        if os.path.basename(path) in skip or os.sep + 'node_modules' + os.sep in path:
            continue
        s = io.open(path, encoding='utf-8').read()
        if START not in s:
            continue
        t = re.sub(re.escape(START) + r'.*?' + re.escape(END),
                   lambda m: LOCKER_SRC.sub(lambda v: v.group(1) + VER, m.group(0)), s, flags=re.S)
        if t != s:
            io.open(path, 'w', encoding='utf-8').write(t)
            changed.append(os.path.relpath(path, ROOT))
    return changed


def main():
    # Pro account pages store the pass in the Locker's meta store too.
    files = sorted(glob.glob(os.path.join(ROOT, 'tools-*.html')) + glob.glob(os.path.join(ROOT, 'pro-*.html')))
    if not files:
        print('no tool pages found', file=sys.stderr)
        return 1
    changed = []
    for path in files:
        name = os.path.basename(path)
        s = io.open(path, encoding='utf-8').read()
        orig = s

        # Drop any previous managed block so this stays idempotent.
        s = re.sub(re.escape(START) + r'.*?' + re.escape(END) + r'\n?', '', s, flags=re.S)

        block = build_block(name)
        if ADS_MARKER in s:
            s = s.replace(ADS_MARKER, block + ADS_MARKER, 1)
        elif '</body>' in s:
            s = s.replace('</body>', block + '</body>', 1)
        else:
            print('  !! no insertion point in %s' % name, file=sys.stderr)
            continue

        if s != orig:
            io.open(path, 'w', encoding='utf-8').write(s)
            changed.append(name)

    print('  wired %d tool page(s)' % len(changed))
    for c in changed:
        print('    - %s%s' % (c, '  [+ bridge]' if c in BRIDGES else ''))
    others = refresh_other_pages(set(os.path.basename(f) for f in files))
    print('  refreshed the Locker version on %d other page(s)' % len(others))
    return 0


if __name__ == '__main__':
    sys.exit(main())
