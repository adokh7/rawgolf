#!/usr/bin/env python3
"""Render and inject contextual Tool CTAs into selected GolfRaw guides.

The CTA catalog owns only placement, variant, and anchor choices.  Tool names,
routes, access state, and descriptions always come from ``tool_inventory`` so
the public CTA cannot drift from the tools hub.
"""

import argparse
import html
import re
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if __package__ in (None, ""):
    sys.path.insert(0, str(ROOT))

from scripts import tool_inventory as inventory


STYLESHEET_LINK = '<link rel="stylesheet" href="/public/tool-cta.css?v=3">'
SUPPORTED_VARIANTS = frozenset({"inline", "card", "banner"})


# One CTA per deliberately selected guide.  Every pair is already present in
# the Phase 4 guide -> tool map; do not broaden this list to every article.
ARTICLE_TOOL_CTAS = {
    "/golf-clubs-for-beginners": {
        "tool_id": "tools-bag-audit",
        "variant": "inline",
        "anchor": "audit your bag",
    },
    "/how-long-do-golf-clubs-last": {
        "tool_id": "tools-bag-audit",
        "variant": "card",
        "anchor": "audit your set",
    },
    "/news-2026-golf-club-distances-guide": {
        "tool_id": "tools-club-distance-calculator",
        "variant": "banner",
        "anchor": "work out your own club distances",
    },
    "/swing-speed-guide": {
        "tool_id": "tools-standing-order",
        "variant": "inline",
        "anchor": "measure your repeatable carry",
    },
    "/golf-swing-analysis-apps": {
        "tool_id": "tools-tendency-engine",
        "variant": "inline",
        "anchor": "track repeated miss patterns",
    },
    "/golf-swing-drills": {
        "tool_id": "tools-scorecard-analyzer",
        "variant": "inline",
        "anchor": "find the holes that cost you",
    },
    "/swing-guide": {
        "tool_id": "tools-tendency-engine",
        "variant": "inline",
        "anchor": "find the miss pattern",
    },
    "/news-2026-raw-golf-honest-practice-guide": {
        "tool_id": "tools-standing-order",
        "variant": "banner",
        "anchor": "range-session logger",
    },
    "/guides-playing-golf-in-your-fifties-distance-loss": {
        "tool_id": "tools-tee-box-check",
        "variant": "inline",
        "anchor": "Tee Box Reality Check",
    },
    "/guides-the-three-feet-that-decide-whether-you-three-putt": {
        "tool_id": "tools-gimme-audit",
        "variant": "inline",
        "anchor": "Gimme Audit",
    },
    "/amateur-tournament-guide": {
        "tool_id": "tools-handicap-detector",
        "variant": "card",
        "anchor": "WHS handicap check",
    },
    "/guides-how-to-play-in-a-golf-pro-am-costs-etiquette": {
        "tool_id": "tools-settle-up-calculator",
        "variant": "card",
        "anchor": "settle the side bets",
    },
    "/charity-golf-scrambles-access-guide": {
        "tool_id": "tools-settle-up-calculator",
        "variant": "card",
        "anchor": "settle group bets",
    },
    "/news-2026-the-renaissance-club-course-guide": {
        "tool_id": "tools-field-reader",
        "variant": "banner",
        "anchor": "course-fit model",
    },
}


def _tools_by_slug():
    return {tool["slug"]: tool for tool in inventory.TOOLS}


def get_tool(tool_id):
    """Return an authoritative inventory entry or reject an unknown ID."""
    try:
        return _tools_by_slug()[tool_id]
    except KeyError as exc:
        raise ValueError(f"Unknown GolfRaw tool ID: {tool_id}") from exc


def first_sentence(description):
    """Use the inventory's first complete sentence as the CTA value hook."""
    clean = " ".join(description.split())
    match = re.search(r"[.!?](?:\s|$)", clean)
    if match:
        return clean[: match.end()].strip()
    return clean.rstrip(".!?") + "."


def _dom_id(source_route, tool_id):
    value = f"{source_route}-{tool_id}".lower()
    return "tool-cta-title-" + re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def _validate_config(source_route, config):
    if not source_route.startswith("/"):
        raise ValueError(f"CTA source must be a root-relative route: {source_route}")
    variant = config.get("variant")
    if variant not in SUPPORTED_VARIANTS:
        raise ValueError(f"Unsupported Tool CTA variant: {variant}")
    anchor = " ".join(config.get("anchor", "").split())
    if not anchor or "click here" in anchor.lower():
        raise ValueError(f"Tool CTA anchor is not descriptive: {anchor}")
    return get_tool(config.get("tool_id")), anchor


def render_tool_cta(source_route, config):
    """Render one accessible CTA using inventory-backed tool data."""
    tool, anchor = _validate_config(source_route, config)
    badge = "FREE" if tool["access"] == "free" else "PRO"
    badge_class = "free" if badge == "FREE" else "pro"
    availability = ""
    if tool["access"] != "free":
        availability = (
            f'\n      <span class="tool-cta__availability">'
            f"{html.escape(tool['access_label'])}</span>"
        )
    title_id = _dom_id(source_route, tool["slug"])
    marker = f"<!-- TOOL-CTA:START source={source_route} tool={tool['slug']} -->"
    end_marker = "<!-- TOOL-CTA:END -->"
    return f'''{marker}
<aside class="tool-cta tool-cta--{html.escape(config['variant'])}" data-tool-cta data-tool-id="{html.escape(tool['slug'])}" data-access="{html.escape(tool['access'])}" aria-labelledby="{title_id}">
  <div class="tool-cta__top">
    <span class="tool-cta__kicker">GolfRaw tool</span>
    <span class="tool-cta__badge tool-cta__badge--{badge_class}">{badge}</span>{availability}
  </div>
  <h3 class="tool-cta__title" id="{title_id}">{html.escape(tool['name'])}</h3>
  <p class="tool-cta__hook">{html.escape(first_sentence(tool['description']))}</p>
  <a class="tool-cta__link" href="{html.escape(tool['route'])}">{html.escape(anchor)} <span aria-hidden="true">→</span></a>
</aside>
{end_marker}'''


def inject_content(source, source_route, config):
    """Insert one CTA before an article's tag row or article close.

    The marker makes repeated generator runs idempotent.  A different existing
    CTA is rejected rather than silently stacking another one on the page.
    """
    rendered = render_tool_cta(source_route, config)
    marker = rendered.split("\n", 1)[0]
    marker_count = source.count(marker)
    if marker_count > 1:
        raise ValueError(f"Duplicate Tool CTA marker on {source_route}")
    if marker_count == 1:
        return source
    if "data-tool-cta" in source:
        raise ValueError(f"A different Tool CTA already exists on {source_route}")

    head_end = source.find("</head>")
    if head_end == -1:
        raise ValueError(f"Missing </head> on {source_route}")
    if STYLESHEET_LINK not in source:
        source = source[:head_end] + f"  {STYLESHEET_LINK}\n" + source[head_end:]

    article_start = source.find("<article")
    article_end = source.find("</article>", article_start)
    if article_start == -1 or article_end == -1:
        raise ValueError(f"Missing article wrapper on {source_route}")
    tag_row = '<nav class="tag-row" aria-label="Article tags">'
    insertion_point = source.find(tag_row, article_start, article_end)
    if insertion_point == -1:
        insertion_point = article_end

    block = textwrap.indent(rendered, "        ")
    return source[:insertion_point] + "\n\n" + block + "\n\n" + source[insertion_point:]


def apply_ctas(root=ROOT):
    """Apply the curated CTA catalog to its selected static guide pages."""
    for source_route, config in ARTICLE_TOOL_CTAS.items():
        path = root / f"{source_route.lstrip('/')}.html"
        if not path.exists():
            raise FileNotFoundError(path)
        original = path.read_text(encoding="utf-8")
        updated = inject_content(original, source_route, config)
        if updated != original:
            path.write_text(updated, encoding="utf-8")


def check_ctas(root=ROOT):
    """Validate that every curated page contains exactly one matching CTA."""
    for source_route, config in ARTICLE_TOOL_CTAS.items():
        path = root / f"{source_route.lstrip('/')}.html"
        if not path.exists():
            raise FileNotFoundError(path)
        source = path.read_text(encoding="utf-8")
        marker = f"<!-- TOOL-CTA:START source={source_route} tool={config['tool_id']} -->"
        if source.count(marker) != 1 or source.count("data-tool-cta") != 1:
            raise ValueError(f"CTA drift on {source_route}")
        if source.count(STYLESHEET_LINK) != 1:
            raise ValueError(f"CTA stylesheet drift on {source_route}")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check curated pages without writing")
    args = parser.parse_args(argv)
    if args.check:
        check_ctas()
        print(f"Tool CTA contract passed for {len(ARTICLE_TOOL_CTAS)} guides.")
    else:
        apply_ctas()
        check_ctas()
        print(f"Applied Tool CTAs to {len(ARTICLE_TOOL_CTAS)} guides.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
