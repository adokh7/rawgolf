#!/usr/bin/env python3
"""Wire the Locker storage layer + drawer into the tool pages.

Idempotent: re-running replaces the managed blocks rather than stacking them.
"""
import glob, io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Bumped whenever a file under lib/locker/ changes. vercel.json serves .js with
# a one-year immutable Cache-Control, so without a new query string readers keep
# running the old locker until their cache expires.
VER = '2'

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
       thirteen clubs. */
    window.addEventListener('DOMContentLoaded', function () {
      var L = window.GolfrawLocker;
      if (!L || typeof SLOTS === 'undefined') return;
      var timer = null, hydrating = false, missedWrite = false;

      function collect() {
        var clubs = [];
        for (var i = 0; i < SLOTS; i++) {
          var name = String($('n' + i).value || '').replace(/^\\s+|\\s+$/g, '');
          var carry = L.util.toNum($('y' + i).value);
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
          L.saveActiveBagClubs(collect())['catch'](function () { /* local-only; the form still works */ });
        }, 400);
      }

      function hydrate(force) {
        return L.getActiveBag().then(function (bag) {
          var clubs = (bag && bag.clubs) || [];
          if (!clubs.length && !force) return;
          hydrating = true;
          for (var i = 0; i < SLOTS; i++) {
            var c = clubs[i];
            if (!c) {
              if (!force) continue;
              $('n' + i).value = ''; $('y' + i).value = ''; $('u' + i).value = '';
              $('c' + i).value = '3';
              continue;
            }
            $('n' + i).value = c.name || '';
            $('y' + i).value = c.carry === null ? '' : c.carry;
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
       than in a shared schema. The reader's unit preference does come from the
       shared profile — it is a property of the person, not of one calculator. */
    window.addEventListener('DOMContentLoaded', function () {
      var L = window.GolfrawLocker;
      if (!L) return;
      var TOOL = 'plays-like';
      var FIELDS = ['yards', 'temp', 'alt', 'wind', 'slope', 'gap'];
      var timer = null, hydrating = false, missedWrite = false;

      function collect() {
        var d = {};
        for (var i = 0; i < FIELDS.length; i++) d[FIELDS[i]] = $(FIELDS[i]).value;
        d.windDir = segValue('windDir');
        d.humidity = segValue('humid');
        return d;
      }

      function push() {
        /* A keystroke during hydration must not be lost: remember it and
           replay once hydration finishes, otherwise the reader's first edit
           after load silently fails to reach the Locker. */
        if (hydrating) { missedWrite = true; return; }
        if (timer) clearTimeout(timer);
        timer = setTimeout(function () {
          L.setToolState(TOOL, collect())['catch'](function () { });
        }, 400);
      }

      function hydrate(force) {
        return L.getToolState(TOOL).then(function (d) {
          if (!d) { if (force) clearFields(); return; }
          hydrating = true;
          for (var i = 0; i < FIELDS.length; i++) {
            var k = FIELDS[i];
            if (d[k] !== undefined && d[k] !== '') $(k).value = d[k];
          }
          if (d.windDir) setSeg('windDir', d.windDir);
          if (d.humidity) setSeg('humid', d.humidity);
          hydrating = false;
          if (missedWrite) { missedWrite = false; push(); }
        })['catch'](function () { hydrating = false; missedWrite = false; });
      }

      function clearFields() {
        hydrating = true;
        for (var i = 0; i < FIELDS.length; i++) $(FIELDS[i]).value = '';
        setSeg('windDir', 'head'); setSeg('humid', 'low');
        hydrating = false;
      }

      for (var i = 0; i < FIELDS.length; i++) $(FIELDS[i]).addEventListener('input', push);
      $('windDir').addEventListener('click', push);
      $('humid').addEventListener('click', push);

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


def main():
    files = sorted(glob.glob(os.path.join(ROOT, 'tools-*.html')))
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
    return 0


if __name__ == '__main__':
    sys.exit(main())
