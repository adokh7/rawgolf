#!/usr/bin/env python3
"""Wire consent mode and ads across the site (GolfRaw monetization M1).

Three idempotent passes over every root *.html page:

1. CONSENT-MODE block, before the gtag.js tag on every page that loads GA4.
   Google Consent Mode defaults: visitors in the EEA, the UK and Switzerland
   start with every storage type denied until Google's certified CMP
   (Privacy & messaging) records their choice; everyone else keeps the
   behaviour the site already had. Must run before any gtag config.
2. Article pages: the existing deferred Auto ads loader gains a Pro check, so
   a live GolfRaw Pro pass on the device skips AdSense entirely.
3. Tool pages (tool_inventory.tracked_pages()): the inline loader is replaced
   by the managed TOOL-ADS block, which loads lib/ads/tool-ads.js. That module
   loads the same CMP and owns the manual, result-first ad slots.

The guide builders that embed the loader get pass 2 on their source.
Run after any builder, with the other wiring scripts:

    python3 scripts/wire_ads.py           # write
    python3 scripts/wire_ads.py --check   # report drift, exit 1
"""
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts import tool_inventory  # noqa: E402

# Bump whenever lib/ads/tool-ads.js changes: .js is served immutable.
VER = '5'

# ISO 3166-1 codes: the EU 27, Iceland, Liechtenstein and Norway (the EEA),
# the UK and Switzerland, the regions Google's European regulations message
# covers.
REGIONS = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IE',
           'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE',
           'IS', 'LI', 'NO', 'GB', 'CH']

CM_START, CM_END = '<!-- CONSENT-MODE:START -->', '<!-- CONSENT-MODE:END -->'
CONSENT_BLOCK = CM_START + """
  <!-- Consent Mode defaults, before any Google tag runs. In the EEA, the UK
       and Switzerland nothing is stored until the reader answers Google's
       consent message (Privacy & messaging), which updates these. -->
  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('consent','default',{ad_storage:'granted',ad_user_data:'granted',ad_personalization:'granted',analytics_storage:'granted'});gtag('consent','default',{ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',analytics_storage:'denied',region:[""" + ','.join("'%s'" % r for r in REGIONS) + """],wait_for_update:500});</script>
""" + CM_END + '\n'

GTAG_TAG = re.compile(r'[ \t]*<script async(?:="")? src="https://www\.googletagmanager\.com/gtag/js\?id=G-PMECW4VW66"></script>')
CM_BLOCK = re.compile(re.escape(CM_START) + r'.*?' + re.escape(CM_END) + r'\n?', re.S)

TA_START, TA_END = '<!-- TOOL-ADS:START -->', '<!-- TOOL-ADS:END -->'
TOOL_BLOCK = TA_START + """
  <!-- Consent and ads for the tool pages: Google's consent message on the
       first interaction or after 6s, and manual ad slots that render only
       after a result, never for GolfRaw Pro. See lib/ads/tool-ads.js. -->
  <script src="/lib/ads/tool-ads.js?v={v}" defer></script>
""" + TA_END + '\n'
TA_BLOCK = re.compile(re.escape(TA_START) + r'.*?' + re.escape(TA_END) + r'\n?', re.S)

# The inline loader every hand-written page carries (comment header + IIFE).
INLINE_LOADER = re.compile(r'  <!-- Ads \+ consent are deferred.*?</script>\n', re.S)

OLD_GUARD = """      function loadAds() {
        if (adsQueued || !window.__gr_ads) return;"""
NEW_GUARD = """      // GolfRaw Pro is ad-free: a live Pro pass on this device skips AdSense
      // entirely. lib/ads/tool-ads.js explains why a readable pass is enough.
      function proPass() {
        try {
          var p = (localStorage.getItem('golfraw_pro_pass') || '').split('.');
          if (p.length !== 3 || p[0] !== 'v1') return false;
          var d = JSON.parse(atob(p[1].replace(/-/g, '+').replace(/_/g, '/')));
          return typeof d.exp === 'number' && d.exp * 1000 > Date.now();
        } catch (e) { return false; }
      }

      function loadAds() {
        if (adsQueued || !window.__gr_ads || proPass()) return;"""

BUILDER_SOURCES = ['scripts/build_rules_guide.py', 'scripts/build_equipment_guide.py']


def tool_files():
    return {tool['slug'] + '.html' for tool in tool_inventory.tracked_pages()}


def with_consent_mode(s):
    s = CM_BLOCK.sub('', s)
    m = GTAG_TAG.search(s)
    if not m:
        return s
    line_start = s.rfind('\n', 0, m.start()) + 1
    return s[:line_start] + CONSENT_BLOCK + s[line_start:]


def with_pro_guard(s):
    return s.replace(OLD_GUARD, NEW_GUARD)


def with_tool_ads(s):
    s = TA_BLOCK.sub('', s)
    s = INLINE_LOADER.sub('', s)
    block = TOOL_BLOCK.format(v=VER)
    # Directly before TOOL-EVENTS. wire_locker puts LOCKER just before </body>
    # and wire_tool_events puts TOOL-EVENTS just before LOCKER, so this is the
    # one spot none of the three scripts ever moves.
    for anchor in ('<!-- TOOL-EVENTS:START -->', '<!-- LOCKER:START -->', '</body>'):
        if anchor in s:
            return s.replace(anchor, block + anchor, 1)
    return s


def wired(name, s):
    s = with_consent_mode(s)
    if name in tool_files():
        s = with_tool_ads(s)
    else:
        s = with_pro_guard(s)
    return s


def main(argv=None):
    check = '--check' in (argv if argv is not None else sys.argv[1:])
    drift = []
    for path in sorted(glob.glob(os.path.join(ROOT, '*.html'))):
        name = os.path.basename(path)
        with io.open(path, encoding='utf-8') as fh:
            src = fh.read()
        out = wired(name, src)
        if out != src:
            drift.append(name)
            if not check:
                with io.open(path, 'w', encoding='utf-8') as fh:
                    fh.write(out)
    for rel in BUILDER_SOURCES:
        path = os.path.join(ROOT, rel)
        with io.open(path, encoding='utf-8') as fh:
            src = fh.read()
        out = with_pro_guard(src)
        if out != src:
            drift.append(rel)
            if not check:
                with io.open(path, 'w', encoding='utf-8') as fh:
                    fh.write(out)
    verb = 'would wire' if check else 'wired'
    print('  %s %d file(s)' % (verb, len(drift)))
    for name in drift[:20]:
        print('    - ' + name)
    return 1 if (check and drift) else 0


if __name__ == '__main__':
    sys.exit(main())
