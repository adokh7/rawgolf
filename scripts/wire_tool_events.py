#!/usr/bin/env python3
"""Wire the shared tool-events script into every tool page.

Injects a managed <!-- TOOL-EVENTS:START/END --> block that loads
lib/analytics/tool-events.js. The page-specific wiring (data-gr-* attributes
and the GRTrack.completed()/shared() calls) lives in each tool's own markup or
builder; this script only makes sure the shared layer is loaded, once.

Idempotent: re-running replaces the block rather than stacking it. Run it after
any tool rebuild, next to wire_locker.py (the block sits just ahead of the
LOCKER block, so the two scripts can run in either order without churn).

    python3 scripts/wire_tool_events.py           # write
    python3 scripts/wire_tool_events.py --check   # report drift, exit 1
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts import tool_inventory  # noqa: E402

# Bump whenever lib/analytics/tool-events.js changes: vercel.json serves .js
# with a one-year immutable Cache-Control, so without a new query string
# returning readers keep the old file.
VER = '2'

START = '<!-- TOOL-EVENTS:START -->'
END = '<!-- TOOL-EVENTS:END -->'
LOCKER_START = '<!-- LOCKER:START -->'
ADS_MARKER = '  <!-- Ads + consent are deferred'

BLOCK = START + """
  <!-- Tool events: which tools people start, finish and share. Actions only,
       never the numbers typed in; see lib/analytics/tool-events.js. -->
  <script src="/lib/analytics/tool-events.js?v={v}" defer></script>
""" + END + '\n'


def tool_pages():
    return [os.path.join(ROOT, tool['slug'] + '.html') for tool in tool_inventory.TOOLS]


def wired(source):
    source = re.sub(re.escape(START) + r'.*?' + re.escape(END) + r'\n?', '', source, flags=re.S)
    block = BLOCK.format(v=VER)
    for anchor in (LOCKER_START, ADS_MARKER, '</body>'):
        if anchor in source:
            return source.replace(anchor, block + anchor, 1)
    raise ValueError('no insertion point')


def main(argv=None):
    check = '--check' in (argv if argv is not None else sys.argv[1:])
    drift = []
    for path in tool_pages():
        name = os.path.basename(path)
        with io.open(path, encoding='utf-8') as fh:
            source = fh.read()
        try:
            updated = wired(source)
        except ValueError:
            print('  !! no insertion point in %s' % name, file=sys.stderr)
            return 1
        if updated != source:
            drift.append(name)
            if not check:
                with io.open(path, 'w', encoding='utf-8') as fh:
                    fh.write(updated)
    verb = 'would wire' if check else 'wired'
    print('  %s %d tool page(s)' % (verb, len(drift)))
    for name in drift:
        print('    - %s' % name)
    return 1 if (check and drift) else 0


if __name__ == '__main__':
    sys.exit(main())
