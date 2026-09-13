#!/usr/bin/env python3
"""The single source of truth for the public GolfRaw tools hub.

The hub, its metadata, and its collection schema are generated from ``TOOLS``
so that the visible portfolio and the machine-readable portfolio cannot drift
apart.  This module describes the public catalog only; it does not contain or
change any tool calculation, Pro entitlement, or security logic.
"""

SITE = "https://www.golfraw.com"
HUB_ROUTE = "/tools"
HUB_CANONICAL = SITE + HUB_ROUTE
HUB_OG_IMAGE = SITE + "/public/raw-golf-practice.webp"
HUB_TITLE = "Golf Tools: 12 Free Utilities + Coach Report | GOLFRAW"
HUB_DESCRIPTION = (
    "Twelve free client-side golf tools plus the Coach Report Pro preview. "
    "Run them in your browser with no signup, account or data upload."
)

# Public product truth lives beside the tool catalog.  Builders may render this
# copy, but it deliberately contains no entitlement or checkout logic.  Keep
# only capabilities that exist in the current repository in ``features``;
# roadmap ideas do not belong on a public promise page.
PRODUCT_MODEL = {
    "free": {
        "label": "Free",
        "promise": "Free forever, no login",
        "tool_count": 12,
        "description": (
            "All 12 core golf tools stay free forever, with no login, account or "
            "data upload. Their calculations and current browser-based outputs "
            "remain available on the device."
        ),
        "route": HUB_ROUTE,
    },
    "pro": {
        "label": "GolfRaw Pro",
        "status": "preview",
        "route": "/pro",
        "title": "GolfRaw Pro: What Pro Adds to the Free Golf Tools | GOLFRAW",
        "description": (
            "GolfRaw keeps 12 browser-based golf tools free forever with no login. "
            "GolfRaw Pro currently adds launch-monitor CSV import to Standing Order "
            "and a one-page Coach and Fitter Report with PDF and share-link output."
        ),
        "features": (
            {
                "id": "lm-import",
                "label": "Launch-monitor CSV import",
                "summary": (
                    "Import a TrackMan, Foresight, Garmin, FlightScope, Rapsodo or "
                    "SkyTrak CSV into the free Standing Order logger on this device."
                ),
                "route": "/tools-standing-order",
                "verified_current": True,
            },
            {
                "id": "coach-report",
                "label": "Coach & Fitter Report",
                "summary": (
                    "Build a one-page report from the numbers already on this device, "
                    "then print it to PDF or share it by link."
                ),
                "route": "/tools-coach-report",
                "verified_current": True,
            },
        ),
    },
}


GROUPS = (
    {
        "id": "performance-practice",
        "label": "Performance & Practice",
        "hint": "Diagnose the leaks. Measure the work.",
    },
    {
        "id": "course-management",
        "label": "Course Management",
        "hint": "Make the smarter call before the shot.",
    },
    {
        "id": "bag-equipment",
        "label": "Bag & Equipment",
        "hint": "Stop carrying dead wood.",
    },
    {
        "id": "games-scoring",
        "label": "Games & Scoring",
        "hint": "Settle the money and the card.",
    },
    {
        "id": "pro-output",
        "label": "Pro Output",
        "hint": "Turn the numbers into a handover.",
    },
)


def _tool(
    slug,
    number,
    name,
    tagline,
    description,
    cta,
    group,
    *,
    access="free",
    access_label="Free",
    newest=False,
):
    """Define one public tool without duplicating route or access plumbing."""
    return {
        "slug": slug,
        "route": "/" + slug,
        "number": number,
        "name": name,
        "tagline": tagline,
        "description": description,
        "cta": cta,
        "group": group,
        "access": access,
        "access_label": access_label,
        "newest": newest,
    }


# Keep this order intentional: it is the order used by both the grouped card
# output and the ItemList schema generated for /tools.
TOOLS = (
    _tool(
        "tools-tendency-engine",
        11,
        "The Tendency Engine",
        "Miss Patterns · Last 10 Rounds",
        "One bad round tells you nothing. Ten tell you everything. Tap the card in afterwards and find the miss that keeps repeating — which way you leak it off the tee, short or long on approach, and which part of your game is quietly taking the most.",
        "What do I actually keep doing? →",
        "performance-practice",
    ),
    _tool(
        "tools-standing-order",
        10,
        "The Standing Order",
        "Range Logger · Gapping",
        "Your gaps were set by a fitter on a launch monitor once, indoors, on a good day. Tap in five balls a club on the range and find out what you actually carry, how far the bad ones stray, and which two clubs are quietly doing the same job.",
        "Gap my bag for real →",
        "performance-practice",
    ),
    _tool(
        "tools-round-autopsy",
        2,
        "The Round Autopsy",
        "Diagnostic · Strokes Lost",
        "Eighteen holes in. A blunt cause-of-death verdict, a strokes-lost breakdown, and no comfortable excuses about your equipment.",
        "Run the autopsy →",
        "performance-practice",
    ),
    _tool(
        "tools-handicap-detector",
        4,
        "The Handicap Lie Detector",
        "WHS Index · Call-Out",
        "Real WHS maths on your last 5 to 20 scores. Your actual index, and whether you are a vanity handicapper or a bandit.",
        "Run the lie detector →",
        "performance-practice",
    ),
    _tool(
        "tools-tilt-meter",
        6,
        "The Tilt Meter",
        "Psychological · Meltdown Index",
        "Everyone remembers the triple. Nobody notices the three holes after it. Works out exactly what your temper threw away.",
        "How badly do I tilt? →",
        "performance-practice",
    ),
    _tool(
        "tools-field-reader",
        12,
        "The Field Reader",
        "Course Fit · Live Re-Rank",
        "Every course asks a different question. Set what this week actually demands — length, iron play, short game, the grass on the greens — and watch the field reorder itself as you move the sliders.",
        "Who does this course suit? →",
        "course-management",
        newest=True,
    ),
    _tool(
        "tools-plays-like",
        5,
        "The Plays Like Calculator",
        "Environmental · On the Course",
        "Wind, cold, altitude and slope in. The distance your shot is genuinely playing out, plus the club that number demands.",
        "What does it play? →",
        "course-management",
    ),
    _tool(
        "tools-tee-box-check",
        3,
        "The Tee Box Reality Check",
        "Ego · Course Management",
        "Three honest numbers reveal the course length you have earned, and how far back your ego has wandered.",
        "Check my tees →",
        "course-management",
    ),
    _tool(
        "tools-bag-audit",
        7,
        "The Bag Audit",
        "Equipment · Dead Wood",
        "Fourteen slots and some of them are luggage. Finds the passengers, the two clubs doing one job, and the distance you have no club for.",
        "Find the dead wood →",
        "bag-equipment",
    ),
    _tool(
        "tools-settle-up-calculator",
        1,
        "The Settle Up",
        "Betting · Nassau · Skins",
        "Nassau, skins with carryovers, automatic presses and junk. One clean who-owes-who card, built for the group chat.",
        "Settle the money →",
        "games-scoring",
    ),
    _tool(
        "tools-gimme-audit",
        8,
        "The Gimme Audit",
        "Delusion · The Honest Card",
        "You have never holed out a round in your life. Real make rates by distance and handicap turn the putts you picked up into the score you actually shot.",
        "What did I really shoot? →",
        "games-scoring",
    ),
    _tool(
        "tools-the-grudge-match",
        9,
        "The Grudge Match",
        "Simulation · 10,000 Rounds",
        "He says he would beat you. You say the strokes are wrong. Ten thousand simulated matches settle it in half a second, including the number of shots that would make it honest.",
        "Do I actually beat him? →",
        "games-scoring",
    ),
    _tool(
        "tools-coach-report",
        13,
        "The Coach Report",
        "One-Page PDF · Gapping, Bag, Tendencies",
        "Golf Raw Pro coach and fitter report builder from the numbers already on this device: carry dispersion, club gaps, passengers and on-course tendencies. Open as a preview while Pro is not on sale; print to PDF or share by link.",
        "Build the report →",
        "pro-output",
        access="pro_preview",
        access_label="Pro preview",
    ),
)


def tools_by_group(group_id):
    """Return the catalog entries assigned to one visible hub group."""
    return tuple(tool for tool in TOOLS if tool["group"] == group_id)


def free_tools():
    return tuple(tool for tool in TOOLS if tool["access"] == "free")


def pro_tools():
    return tuple(tool for tool in TOOLS if tool["access"] == "pro_preview")


def tool_counts():
    return {
        "total": len(TOOLS),
        "free": len(free_tools()),
        "pro_preview": len(pro_tools()),
    }


def validate_inventory():
    """Raise a useful error if the public catalog is internally inconsistent."""
    group_ids = {group["id"] for group in GROUPS}
    if len(TOOLS) != 13:
        raise ValueError("The public tools inventory must contain exactly 13 tools")
    if len({tool["slug"] for tool in TOOLS}) != len(TOOLS):
        raise ValueError("Tool slugs must be unique")
    if len({tool["route"] for tool in TOOLS}) != len(TOOLS):
        raise ValueError("Tool routes must be unique")
    if {tool["group"] for tool in TOOLS} != group_ids:
        raise ValueError("Every visible hub group must have at least one tool")
    if len(free_tools()) != 12 or len(pro_tools()) != 1:
        raise ValueError("The hub must expose 12 Free tools and one Pro preview")
    for tool in TOOLS:
        if not tool["route"].startswith("/"):
            raise ValueError(f"Tool route is not root-relative: {tool['route']}")
        if not all(tool.get(key) for key in ("name", "tagline", "description", "cta")):
            raise ValueError(f"Tool metadata is incomplete: {tool['slug']}")
    return True


validate_inventory()
