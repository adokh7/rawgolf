#!/usr/bin/env python3
"""Curated Phase 6 answer-first passages for selected GolfRaw guides.

The catalog deliberately covers a small set of high-value, tool-connected
pages.  It stores the question/section context and the page-specific answer,
while the renderer keeps the HTML contract identical and the copy distinct.
It does not add structured-data markup or alter article metadata.
"""

import argparse
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if __package__ in (None, ""):
    sys.path.insert(0, str(ROOT))

from scripts import internal_link_map, tool_inventory


PHASE6_ROUTES = (
    "/news-2026-golf-club-distances-guide",
    "/news-2026-raw-golf-honest-practice-guide",
    "/golf-clubs-for-beginners",
    "/golf-swing-analysis-apps",
    "/guides-the-three-feet-that-decide-whether-you-three-putt",
    "/guides-playing-golf-in-your-fifties-distance-loss",
    "/amateur-tournament-guide",
    "/guides-how-to-play-in-a-golf-pro-am-costs-etiquette",
    "/news-2026-the-renaissance-club-course-guide",
)


ARTICLE_AEO_UPGRADES = {
    "/news-2026-golf-club-distances-guide": {
        "tool_id": "tools-standing-order",
        "heading": "How can I measure my own club distances?",
        "answer": (
            "Use a launch monitor or a normal round to collect carry numbers, then treat "
            "the middle of a representative sample as your playing yardage. A simple range "
            "version is ten shots with one club, discard the obvious best and worst, and "
            "record the centre of the remaining group."
        ),
        "basis_label": "Evidence",
        "basis": (
            "GolfRaw's ten-ball middle-cluster method described in this guide; these are "
            "reference points, not a fitting result for every player."
        ),
    },
    "/news-2026-raw-golf-honest-practice-guide": {
        "tool_id": "tools-standing-order",
        "heading": "What Is GolfRaw?",
        "answer": (
            "Raw golf is a way of practising and playing at your real level, inside the "
            "time and attention your life actually gives you. It is not a swing system; it "
            "is a rule for honest decisions and honest tracking."
        ),
        "basis_label": "Editorial basis",
        "basis": (
            "GolfRaw's definition used throughout this manifesto; it makes no promise about "
            "a guaranteed improvement rate."
        ),
    },
    "/golf-clubs-for-beginners": {
        "tool_id": "tools-bag-audit",
        "heading": "How Many Golf Clubs You Actually Need to Start",
        "answer": (
            "Start with four or five clubs: a driver or fairway wood, a 7-iron, a wedge, a "
            "putter, and optionally a hybrid. That is enough to play a full round while you "
            "learn your distances and misses; add clubs when a real gap appears."
        ),
        "basis_label": "Practical basis",
        "basis": (
            "GolfRaw's starter-set recommendation; the rules allow up to fourteen clubs, "
            "but permission to carry fourteen is not a reason to buy fourteen."
        ),
    },
    "/golf-swing-analysis-apps": {
        "tool_id": "tools-tendency-engine",
        "heading": "What a Swing Analysis App Actually Does for You",
        "answer": (
            "A swing-analysis app turns phone video into something you can inspect: slow "
            "motion, frame stepping, drawing tools, and comparison. It can show a fault; it "
            "cannot do the practice that changes it."
        ),
        "basis_label": "Source note",
        "basis": (
            "Feature summary and limitations drawn from the products described on this page; "
            "app plans and feature sets can change."
        ),
    },
    "/guides-the-three-feet-that-decide-whether-you-three-putt": {
        "tool_id": "tools-gimme-audit",
        "heading": "At what distance does a three-putt become likely?",
        "answer": (
            "There is no single cutoff for everyone, but the Shot Scope benchmark cited here "
            "puts the putting precipice at about 29 feet for scratch golfers and 28 feet for "
            "10-handicappers. Past that range, speed control matters more than chasing the "
            "hole."
        ),
        "basis_label": "Benchmark",
        "basis": (
            "Shot Scope putting data cited in this guide; these distances are skill-band "
            "estimates, not a personal prediction."
        ),
    },
    "/guides-playing-golf-in-your-fifties-distance-loss": {
        "tool_id": "tools-tee-box-check",
        "heading": "What distance should I use when choosing tees?",
        "answer": (
            "Choose tees from measured carry with a repeatable club, not your best total drive. "
            "The USGA's 7-iron tee selector is a sensible starting point; then test one set "
            "forward for three rounds and compare greens reached, penalties, scoring, and pace."
        ),
        "basis_label": "Source",
        "basis": (
            "The USGA golfer-experience report and 7-iron tee selector linked in this guide."
        ),
    },
    "/amateur-tournament-guide": {
        "tool_id": "tools-handicap-detector",
        "heading": "The Week Before: Prepare Honestly, Not Obsessively",
        "answer": (
            "Before your first amateur tournament, confirm the format and handicap requirements, "
            "rehearse the clubs and routine you will actually use, and arrive early enough to "
            "warm up without changing your swing. A simple plan survives pressure better than a "
            "new technical thought."
        ),
        "basis_label": "Preparation note",
        "basis": (
            "GolfRaw's tournament checklist and preparation guidance on this page; event rules "
            "and handicap procedures vary."
        ),
    },
    "/guides-how-to-play-in-a-golf-pro-am-costs-etiquette": {
        "tool_id": "tools-settle-up-calculator",
        "heading": "What is a golf pro-am?",
        "answer": (
            "A golf pro-am is an event in which a professional plays alongside amateur partners, "
            "usually on the tournament course before the main competition. The precise format "
            "varies, but one professional with three or four amateurs is a common setup."
        ),
        "basis_label": "Format note",
        "basis": (
            "The format definition in this guide; costs, pairings, and caddie arrangements vary "
            "by event, tour, and date."
        ),
    },
    "/news-2026-the-renaissance-club-course-guide": {
        "tool_id": "tools-field-reader",
        "heading": "Is The Renaissance Club a true links course?",
        "answer": (
            "No—not in the classic playing sense. The Renaissance Club has coastal, sandy "
            "ground, but its raised greens and collection areas reward a carried, aerial approach "
            "more than a low bump-and-run."
        ),
        "basis_label": "Course note",
        "basis": (
            "GolfRaw's course analysis of the design features described above; wind, setup, and "
            "pin positions can change the shot demanded."
        ),
    },
}


def _tool_ids():
    return {tool["slug"] for tool in tool_inventory.TOOLS}


def render_answer_block(route, config):
    """Render the exact managed fragment expected in a selected article."""
    if route not in ARTICLE_AEO_UPGRADES:
        raise ValueError(f"Uncatalogued Phase 6 route: {route}")
    if config["tool_id"] not in _tool_ids():
        raise ValueError(f"Unknown tool for Phase 6 answer: {config['tool_id']}")
    tool = next(tool for tool in tool_inventory.TOOLS if tool["slug"] == config["tool_id"])
    if not any(
        link["source"] == route
        and link["target"] == tool["route"]
        and link["direction"] == "guide_to_tool"
        for link in internal_link_map.CONTEXTUAL_LINKS
    ):
        raise ValueError(f"Phase 6 tool is not mapped to its guide: {route} -> {tool['route']}")
    marker = f"<!-- AEO-ANSWER:START route={route} -->"
    return f'''{marker}
<div class="aeo-answer" data-aeo-answer="true" role="note" aria-label="Direct answer">
  <p class="aeo-answer__text">{html.escape(config["answer"], quote=False)}</p>
  <p class="aeo-answer__basis"><strong>{html.escape(config["basis_label"], quote=False)}:</strong> {html.escape(config["basis"], quote=False)}</p>
</div>
<!-- AEO-ANSWER:END -->'''


def check_catalog(root=ROOT):
    """Check catalog shape and exact, single-fragment article placement."""
    if tuple(ARTICLE_AEO_UPGRADES) != PHASE6_ROUTES:
        raise ValueError("Phase 6 route catalog order drifted")
    if len({config["answer"] for config in ARTICLE_AEO_UPGRADES.values()}) != len(ARTICLE_AEO_UPGRADES):
        raise ValueError("Phase 6 answer copy must remain page-specific")
    for route, config in ARTICLE_AEO_UPGRADES.items():
        path = root / f"{route.lstrip('/')}.html"
        if not path.exists():
            raise FileNotFoundError(path)
        source = path.read_text(encoding="utf-8")
        block = render_answer_block(route, config)
        if source.count(block) != 1:
            raise ValueError(f"Phase 6 answer drift on {route}")
        heading = re.search(rf"<h[23][^>]*>{re.escape(config['heading'])}</h[23]>", source)
        if heading is None or source.find("AEO-ANSWER:START", heading.end()) == -1:
            raise ValueError(f"Phase 6 answer is not below its heading on {route}")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check content without writing")
    parser.parse_args()
    check_catalog()
    print(f"Phase 6 AEO contract passed for {len(ARTICLE_AEO_UPGRADES)} guides.")


if __name__ == "__main__":
    main()
