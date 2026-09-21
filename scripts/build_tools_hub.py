#!/usr/bin/env python3
"""Build and check the managed architecture of the public tools hub.

Only regions surrounded by ``TOOLS-HUB-*`` markers are generated.  The rest
of ``tools.html`` remains hand-authored, so this builder does not touch tool
calculations, tool pages, or Pro entitlement/security code.

Usage::

    python3 scripts/build_tools_hub.py          # update tools.html
    python3 scripts/build_tools_hub.py --check  # report drift without writing
"""

import argparse
import html
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HUB_PATH = ROOT / "tools.html"
sys.path.insert(0, str(ROOT))

from scripts import tool_inventory as inventory
from scripts.schema_normalizer import _hub_schema


MARKER_NAMES = ("METADATA", "SCHEMA", "HERO", "CARDS", "PRO-VALUE", "DASHBOARD", "EMPTY")
MARKER_STYLES = {
    "METADATA": ("<!--", "-->",),
    "SCHEMA": ("<!--", "-->",),
    "HERO": ("<!--", "-->",),
    "CARDS": ("<!--", "-->",),
    "PRO-VALUE": ("<!--", "-->",),
    "DASHBOARD": ("<!--", "-->",),
    "EMPTY": ("/*", "*/"),
}


def _escape(value):
    return html.escape(str(value), quote=True)


def _number_word(number):
    return {
        1: "One",
        2: "Two",
        3: "Three",
        4: "Four",
        5: "Five",
        6: "Six",
        7: "Seven",
        8: "Eight",
        9: "Nine",
        10: "Ten",
        11: "Eleven",
        12: "Twelve",
        13: "Thirteen",
    }[number]


def render_metadata():
    title = _escape(inventory.HUB_TITLE)
    description = _escape(inventory.HUB_DESCRIPTION)
    canonical = _escape(inventory.HUB_CANONICAL)
    image = _escape(inventory.HUB_OG_IMAGE)
    return f"""  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="{canonical}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta property="og:site_name" content="GolfRaw">
  <meta name="application-name" content="GolfRaw">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{image}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{description}">
  <meta name="twitter:image" content="{image}">"""


def _schema_document():
    return _hub_schema()


def render_schema():
    payload = json.dumps(_schema_document(), indent=2, ensure_ascii=False)
    payload = payload.replace("</script>", "<\\/script>")
    return f'''  <!-- ============ STRUCTURED DATA ============ -->
  <script type="application/ld+json">
{payload}
  </script>'''


def render_hero():
    counts = inventory.tool_counts()
    free_word = _number_word(counts["free"])
    pro_count = counts["pro_preview"]
    return f"""      <p>{free_word} free <b>unfiltered client-side golf utility apps</b> that do the jobs golf software charges a subscription
        for, plus the <b>Coach Report</b>, a GolfRaw Pro feature currently open as a preview. They cover golf betting
        settlement, strokes-lost round diagnostics, World Handicap System maths, club gapping and
        <b>psychological golf performance diagnostics</b> — and every one runs <b>100% inside your browser</b>.
        No account, no signup, no round data uploaded anywhere, and nothing you type is tracked. Close the tab and it is gone.</p>

      <div class="facts-strip">
        <div><span class="n">{counts['total']}</span><span class="l">Tools live</span></div>
        <div><span class="n">{counts['free']}</span><span class="l">Free tools</span></div>
        <div><span class="n">{pro_count}</span><span class="l">Pro preview</span></div>
        <div><span class="n">0</span><span class="l">Accounts needed</span></div>
        <div><span class="n">0</span><span class="l">Data uploaded</span></div>
      </div>"""


def render_card(tool):
    badge_class = "free" if tool["access"] == "free" else "pro"
    newest = " <span class=\"t-new\">· Newest</span>" if tool["newest"] else ""
    return f"""        <a href="{_escape(tool['route'])}" class="t-card" data-tool-slug="{_escape(tool['slug'])}" data-access="{_escape(tool['access'])}">
          <div class="t-num">Tool {tool['number']:02d}{newest} <span class="t-badge t-badge--{badge_class}">{_escape(tool['access_label'])}</span></div>
          <h3>{_escape(tool['name'])}</h3>
          <div class="t-tagline">{_escape(tool['tagline'])}</div>
          <p>{_escape(tool['description'])}</p>
          <span class="t-cta">{_escape(tool['cta'])}</span>
        </a>"""


def render_cards():
    sections = []
    for group in inventory.GROUPS:
        cards = "\n\n".join(render_card(tool) for tool in inventory.tools_by_group(group["id"]))
        sections.append(
            f'''      <section class="tool-group" data-tool-group="{_escape(group['id'])}">
        <div class="tool-group-head">
          <h3>{_escape(group['label'])}</h3>
          <span class="hint">{_escape(group['hint'])}</span>
        </div>
        <div class="tool-grid">
{cards}
        </div>
      </section>'''
        )
    return "\n\n".join(sections)


def render_dashboard():
    free_count = inventory.tool_counts()["free"]
    return f"""            Every result from the {free_count} free tools, in order, saved in this browser only. No account,
              no upload, no way for us to see it."""


def render_pro_value():
    free = inventory.PRODUCT_MODEL["free"]
    pro = inventory.PRODUCT_MODEL["pro"]
    features = "\n".join(
        f"            <li><b>{_escape(feature['label'])}.</b> {_escape(feature['summary'])}</li>"
        for feature in pro["features"]
    )
    return f"""      <section class="privacy-note" aria-labelledby="pro-value-title">
        <div class="pn-label">{_escape(pro['label'])}</div>
        <h3 id="pro-value-title">What Pro adds</h3>
        <p><b>{_escape(free['promise'])}.</b> {free['tool_count']} tools and their calculations remain available in your browser. Pro adds the handover surfaces that sit on top of those free results.</p>
        <ul>
{features}
        </ul>
        <p><a class="t-cta" href="{_escape(pro['route'])}">See what stays free and what Pro adds →</a></p>
      </section>"""


def render_empty():
    free_count = inventory.tool_counts()["free"]
    return f"""            'Run any of the {free_count} free tools above and it will show up here automatically — ' +
            'no sign-up, no setup.'"""


def _replace_region(source, name, body):
    start_token, end_token = MARKER_STYLES[name]
    start = f"{start_token} TOOLS-HUB-{name}:START {end_token}"
    end = f"{start_token} TOOLS-HUB-{name}:END {end_token}"
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError(f"Expected exactly one managed {name} region")
    before, remainder = source.split(start, 1)
    _, after = remainder.split(end, 1)
    return before + start + "\n" + body.rstrip() + "\n  " + end + after


def generated_source(source):
    regions = {
        "METADATA": render_metadata(),
        "SCHEMA": render_schema(),
        "HERO": render_hero(),
        "CARDS": render_cards(),
        "PRO-VALUE": render_pro_value(),
        "DASHBOARD": render_dashboard(),
        "EMPTY": render_empty(),
    }
    for name in MARKER_NAMES:
        source = _replace_region(source, name, regions[name])
    return source


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check for drift without writing")
    args = parser.parse_args(argv)

    current = HUB_PATH.read_text(encoding="utf-8")
    expected = generated_source(current)
    if args.check:
        if current != expected:
            print("tools.html is out of sync with scripts/tool_inventory.py")
            return 1
        print("tools.html is in sync with scripts/tool_inventory.py")
        return 0

    if current != expected:
        HUB_PATH.write_text(expected, encoding="utf-8")
        print("updated tools.html from scripts/tool_inventory.py")
    else:
        print("tools.html already matches scripts/tool_inventory.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
