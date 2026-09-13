"""Curated Phase 4 links between public tools and supporting guides.

This is a link inventory, not a CTA system.  Each entry describes one
contextual body link that must exist in the rendered source page.  Keeping the
map declarative makes coverage, route validity, and duplicate-pair checks
repeatable as the article and tool collections grow.
"""


def _link(source, target, anchor, direction):
    return {
        "source": source,
        "target": target,
        "anchor": anchor,
        "direction": direction,
    }


CONTEXTUAL_LINKS = (
    # Tool -> supporting guide
    _link("/tools-bag-audit", "/golf-clubs-for-beginners", "starter bag", "tool_to_guide"),
    _link("/tools-bag-audit", "/how-long-do-golf-clubs-last", "club lifespan guide", "tool_to_guide"),
    _link("/tools-standing-order", "/news-2026-golf-club-distances-guide", "realistic golf club distance chart", "tool_to_guide"),
    _link("/tools-standing-order", "/swing-speed-guide", "swing-speed guide", "tool_to_guide"),
    _link("/tools-tendency-engine", "/golf-swing-analysis-apps", "swing-analysis apps", "tool_to_guide"),
    _link("/tools-tendency-engine", "/news-2026-raw-golf-honest-practice-guide", "honest practice guide", "tool_to_guide"),
    _link("/tools-field-reader", "/news-2026-the-renaissance-club-course-guide", "course-fit example", "tool_to_guide"),
    _link("/tools-plays-like", "/news-2026-golf-club-distances-guide", "golf club distance chart", "tool_to_guide"),
    _link("/tools-plays-like", "/news-2026-the-renaissance-club-course-guide", "wind and course-conditions guide", "tool_to_guide"),
    _link("/tools-tee-box-check", "/guides-playing-golf-in-your-fifties-distance-loss", "distance-loss guide", "tool_to_guide"),
    _link("/tools-tee-box-check", "/news-2026-golf-club-distances-guide", "club-distance guide", "tool_to_guide"),
    _link("/tools-round-autopsy", "/news-2026-raw-golf-honest-practice-guide", "honest practice guide", "tool_to_guide"),
    _link("/tools-round-autopsy", "/golf-swing-drills", "golf swing drills", "tool_to_guide"),
    _link("/tools-handicap-detector", "/amateur-tournament-guide", "first amateur tournament guide", "tool_to_guide"),
    _link("/tools-handicap-detector", "/charity-golf-scrambles-access-guide", "charity scramble guide", "tool_to_guide"),
    _link("/tools-settle-up-calculator", "/guides-how-to-play-in-a-golf-pro-am-costs-etiquette", "pro-am format guide", "tool_to_guide"),
    _link("/tools-settle-up-calculator", "/charity-golf-scrambles-access-guide", "charity scramble guide", "tool_to_guide"),
    _link("/tools-gimme-audit", "/guides-the-three-feet-that-decide-whether-you-three-putt", "three-putt guide", "tool_to_guide"),
    _link("/tools-the-grudge-match", "/amateur-tournament-guide", "first amateur tournament guide", "tool_to_guide"),
    _link("/tools-the-grudge-match", "/guides-how-to-play-in-a-golf-pro-am-costs-etiquette", "pro-am guide", "tool_to_guide"),
    _link("/tools-tilt-meter", "/news-2026-raw-golf-honest-practice-guide", "raw golf practice guide", "tool_to_guide"),
    _link("/tools-tilt-meter", "/amateur-tournament-guide", "tournament-pressure guide", "tool_to_guide"),
    _link("/tools-coach-report", "/news-2026-golf-club-distances-guide", "realistic club-distance chart", "tool_to_guide"),
    _link("/tools-coach-report", "/golf-swing-analysis-apps", "swing-analysis app guide", "tool_to_guide"),

    # Guide -> matching tool
    _link("/golf-clubs-for-beginners", "/tools-bag-audit", "audit your bag", "guide_to_tool"),
    _link("/how-long-do-golf-clubs-last", "/tools-bag-audit", "audit your set", "guide_to_tool"),
    _link("/news-2026-golf-club-distances-guide", "/tools-standing-order", "log your own carry distances", "guide_to_tool"),
    _link("/news-2026-golf-club-distances-guide", "/tools-coach-report", "Coach Report", "guide_to_tool"),
    _link("/swing-speed-guide", "/tools-standing-order", "measure your repeatable carry", "guide_to_tool"),
    _link("/golf-swing-analysis-apps", "/tools-tendency-engine", "track repeated miss patterns", "guide_to_tool"),
    _link("/golf-swing-drills", "/tools-round-autopsy", "measure where your shots go", "guide_to_tool"),
    _link("/swing-guide", "/tools-tendency-engine", "find the miss pattern", "guide_to_tool"),
    _link("/news-2026-raw-golf-honest-practice-guide", "/tools-standing-order", "range-session logger", "guide_to_tool"),
    _link("/news-2026-raw-golf-honest-practice-guide", "/tools-round-autopsy", "round diagnosis", "guide_to_tool"),
    _link("/news-2026-raw-golf-honest-practice-guide", "/tools-tendency-engine", "track a pattern", "guide_to_tool"),
    _link("/news-2026-raw-golf-honest-practice-guide", "/tools-tilt-meter", "measure the cost of a blow-up", "guide_to_tool"),
    _link("/guides-playing-golf-in-your-fifties-distance-loss", "/tools-tee-box-check", "Tee Box Reality Check", "guide_to_tool"),
    _link("/guides-the-three-feet-that-decide-whether-you-three-putt", "/tools-gimme-audit", "Gimme Audit", "guide_to_tool"),
    _link("/amateur-tournament-guide", "/tools-handicap-detector", "WHS handicap check", "guide_to_tool"),
    _link("/amateur-tournament-guide", "/tools-the-grudge-match", "fair match simulator", "guide_to_tool"),
    _link("/amateur-tournament-guide", "/tools-tilt-meter", "Tilt Meter", "guide_to_tool"),
    _link("/guides-how-to-play-in-a-golf-pro-am-costs-etiquette", "/tools-settle-up-calculator", "settle the side bets", "guide_to_tool"),
    _link("/guides-how-to-play-in-a-golf-pro-am-costs-etiquette", "/tools-the-grudge-match", "fair match simulator", "guide_to_tool"),
    _link("/charity-golf-scrambles-access-guide", "/tools-settle-up-calculator", "settle group bets", "guide_to_tool"),
    _link("/charity-golf-scrambles-access-guide", "/tools-handicap-detector", "handicap check", "guide_to_tool"),
    _link("/news-2026-the-renaissance-club-course-guide", "/tools-field-reader", "course-fit model", "guide_to_tool"),
    _link("/news-2026-the-renaissance-club-course-guide", "/tools-plays-like", "Plays Like Calculator", "guide_to_tool"),
)


def links_from(source):
    """Return the curated links originating at ``source``."""
    return tuple(link for link in CONTEXTUAL_LINKS if link["source"] == source)


def links_to(target):
    """Return the curated links pointing at ``target``."""
    return tuple(link for link in CONTEXTUAL_LINKS if link["target"] == target)
