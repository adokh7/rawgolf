"""Managed GEO citation notes for the small set of source-ready GolfRaw pages."""

from html import escape


CITATION_UPGRADES = {
    "/news-2026-golf-club-distances-guide": {
        "id": "club-gapping-method",
        "entity": "FlightScope",
        "placement": "after",
        "placement_anchor": "<h2>How to Measure and Build Your Own Golf Club Distance Chart</h2>",
        "methodology": (
            "FlightScope's published gapping guidance describes a repeatable workflow: hit multiple normal shots with each club, remove outliers, and compare carry gaps. GolfRaw uses that source to support the measurement method, not the exact reference yardages in the chart above. The chart is GolfRaw's editorial range; the Standing Order is the site's own browser tool for recording a player's numbers."
        ),
        "freshness": (
            "Reporting context: the linked FlightScope guidance was published on 21 August 2023; individual carry numbers should be refreshed when a player's swing or equipment changes."
        ),
        "sources": [
            {
                "name": "FlightScope: Master the Carry Distance Gapping Between your Clubs",
                "url": "https://flightscope.com/blogs/blogs/master-the-carry-distance-gapping-between-your-clubs",
                "role": "Official gapping guidance.",
            }
        ],
    },
    "/guides-playing-golf-in-your-fifties-distance-loss": {
        "id": "tee-selection-evidence",
        "entity": "USGA",
        "placement": "after",
        "placement_anchor": "<h3>What distance should I use when choosing tees?</h3>",
        "methodology": (
            "The USGA's 2023 Sporting Insights report is the source for the age-band tee-shot totals above. Its Golfer Experience page links the 7-Iron Tee Selector. GolfRaw's conclusion is an interpretation of those sources: choose tees from measured carry, then test the choice over three rounds. The report's group means include roll, so they describe a population, not a personal carry target."
        ),
        "freshness": (
            "Reporting context: the linked study is from 2023, while the tee decision should be revisited after a meaningful change in health, swing, or equipment."
        ),
        "sources": [
            {
                "name": "USGA: Sporting Insights Report on Golfer Experience",
                "url": "https://www.usga.org/content/dam/usga/images/course-care/GolferExperience/Sporting_Insights_Report_USGA_Golfer_Experience_2023_Stage%201_August%202023.pdf",
                "role": "Age-band tee-shot data.",
            },
            {
                "name": "USGA: Golfer Experience Information",
                "url": "https://www.usga.org/content/usga/home-page/course-care/golfer-experience/golfer-experience-information.html",
                "role": "7-Iron Tee Selector source.",
            },
        ],
    },
    "/guides-the-three-feet-that-decide-whether-you-three-putt": {
        "id": "three-putt-data-context",
        "entity": "Shot Scope",
        "placement": "after",
        "placement_anchor": "<h3>At what distance does a three-putt become likely?</h3>",
        "methodology": (
            "Shot Scope's official data guide supplies the handicap-level three-putt context used in this article. It is source data, not a current universal cutoff. The 29- and 28-foot putting-precipice figures are the benchmark cited in this article; GolfRaw's analysis turns that context into a practice focus on first-putt proximity."
        ),
        "freshness": (
            "Reporting context: the linked data guide is historical source context, so these skill-band figures are presented as benchmarks rather than a current population estimate."
        ),
        "sources": [
            {
                "name": "Shot Scope: How To Use Data To Improve",
                "url": "https://shotscope.com/ebook/How_To_Use_Data_To_Improve.pdf",
                "role": "Official putting-data guide.",
            }
        ],
    },
    "/how-long-do-golf-clubs-last": {
        "id": "equipment-reporting-method",
        "entity": "Titleist Vokey R&D",
        "placement": "after",
        "placement_anchor": '<div class="raw-verdict">',
        "methodology": (
            "GolfRaw separates controlled manufacturer testing from independent equipment reporting. Titleist Vokey R&amp;D supports the wedge-wear figures; Golf Monthly's equipment-team survey is a real-world check, not a controlled test; Golf Digest supplies additional equipment reporting. The replacement advice is GolfRaw's synthesis, and the page's 5 September 2026 update date is the freshness boundary for this review."
        ),
        "freshness": (
            "Reporting context: this review was updated on 5 September 2026; product prices, availability, and equipment recommendations can change."
        ),
        "sources": [
            {
                "name": "Titleist Team Titleist: Inspect Wedges for Groove Wear and Spin Loss",
                "url": "https://www.titleist.com/teamtitleist/team-titleist/f/golf-clubs/66539/how-do-i-inspect-my-wedges-for-groove-wear-and-spin-loss/348556",
                "role": "Manufacturer wedge-wear testing context.",
            },
            {
                "name": "Golf Monthly: The 9 Oldest Clubs The Team Still Use Today",
                "url": "https://www.golfmonthly.com/features/the-9-oldest-clubs-the-golf-monthly-team-still-use-today",
                "role": "Independent real-world equipment reporting.",
            },
            {
                "name": "Golf Digest: Tour Pros Seem To Wear Out Their Woods",
                "url": "https://www.golfdigest.com/story/tour-pros-seem-to-wear-out-their-woods-should-i-be-concerned-about-mine",
                "role": "Additional equipment reporting context.",
            },
        ],
    },
}


def render_citation_block(route, config):
    """Render one auditable, source-linked note for a configured article."""
    source_items = "\n".join(
        (
            "    <li><a href=\"{url}\" target=\"_blank\" rel=\"noopener noreferrer\">{name}</a> "
            "<span>{role}</span></li>"
        ).format(
            url=escape(source["url"], quote=True),
            name=source["name"],
            role=source["role"],
        )
        for source in config["sources"]
    )
    return (
        f'<!-- GEO-CITATION:START route={route} id={config["id"]} -->\n'
        '<aside class="geo-citation" data-geo-citation="true" role="note" aria-label="Source and methodology">\n'
        f'  <p class="geo-citation__method">{config["methodology"]}</p>\n'
        f'  <p class="geo-citation__freshness"><strong>Reporting context:</strong> {config["freshness"].removeprefix("Reporting context: ")}</p>\n'
        '  <p class="geo-citation__source-label"><strong>Source:</strong> Named primary or originating sources for the claims above.</p>\n'
        f'  <ul class="geo-citation__sources">\n{source_items}\n  </ul>\n'
        '</aside>\n'
        '<!-- GEO-CITATION:END -->'
    )


def check_citation_catalog(root):
    """Return validation errors for local pages managed by this catalog."""
    errors = []
    for route, config in CITATION_UPGRADES.items():
        page_path = root / f"{route.lstrip('/')}.html"
        if not page_path.exists():
            errors.append(f"missing page: {route}")
            continue
        page = page_path.read_text()
        block = render_citation_block(route, config)
        if page.count(block) != 1:
            errors.append(f"citation block count is not one: {route}")
        if page.count('/public/geo-citation.css?v=1') != 1:
            errors.append(f"stylesheet count is not one: {route}")
        if config["placement_anchor"] not in page:
            errors.append(f"placement anchor missing: {route}")
        elif config["placement"] == "after" and page.index(block) < page.index(config["placement_anchor"]):
            errors.append(f"citation block is before its anchor: {route}")
    return errors


if __name__ == "__main__":
    from pathlib import Path

    problems = check_citation_catalog(Path(__file__).resolve().parents[1])
    if problems:
        raise SystemExit("\n".join(problems))
    print(f"GEO citation catalog OK: {len(CITATION_UPGRADES)} pages")
