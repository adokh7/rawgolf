#!/usr/bin/env python3
"""Publish GolfRaw's 3-wood versus 3-hybrid equipment guide."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

try:
    from scripts.article_header import finalize_article_template_metadata, replace_article_header
except ModuleNotFoundError:  # direct execution from the scripts directory
    from article_header import finalize_article_template_metadata, replace_article_header


ROOT = Path(__file__).resolve().parents[1]
SLUG = "3-wood-vs-3-hybrid"
OUTPUT = ROOT / f"{SLUG}.html"
REGISTRY = ROOT / "articles.json"
TEMPLATE = ROOT / "article-template.html"

TITLE = "3-Wood vs 3-Hybrid: Distance, Forgiveness and Which One Belongs in Your Bag"
DESCRIPTION = (
    "A 3-wood offers maximum distance from tees and clean fairways, while a 3-hybrid "
    "offers launch and versatility from rough. Here is how to test, gap, and choose."
)
CANONICAL = f"https://www.golfraw.com/{SLUG}"
H1 = TITLE
STANDFIRST = (
    "A 3-wood is usually the better choice for maximum distance from a tee or clean "
    "fairway lie, while a 3-hybrid is usually easier to launch, control and use from "
    "rough. Carry both only if they produce distinct carry gaps and serve different "
    "shots; the numbers on the soles do not make them redundant."
)
HERO = "/public/3-wood-vs-3-hybrid-distance-forgiveness-comparison.webp"
HERO_ALT = "Side by side comparison of a 3 wood and a 3 hybrid clubhead resting on fairway turf"
ROUGH_IMAGE = "/public/golf-hybrid-out-of-rough-lie-versatility.webp"
ROUGH_ALT = "Golfer addressing the ball with a 3 hybrid out of rough grass on the course"
READING_TIME = "10 min read"

REGISTRY_RECORD = {
    "canonical": f"/{SLUG}",
    "alias_of": "",
    "slug": SLUG,
    "url": f"/{SLUG}",
    "title": TITLE,
    "excerpt": DESCRIPTION,
    "category": ["GUIDES", "EQUIPMENT", "CLUB FITTING", "3-WOOD", "3-HYBRID"],
    "date": "2026-09-21",
    "image": HERO,
    "keywords": (
        "3 wood vs 3 hybrid, 3 wood or 3 hybrid, 3 hybrid vs 3 wood distance, "
        "which is easier to hit, golf club gapping, fairway wood from rough, "
        "3 wood for high handicapper, golf club fitting"
    ),
    "category_source": "editorial",
    "section": "GUIDES",
    "reading_time": READING_TIME,
}

ARTICLE_CSS = """
  <style id="3wood-hybrid-guide-article">
    .article-body a{text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:3px}
    .article-body a:hover{color:var(--flag)}
    .article-body a:focus-visible,.tag-row a:focus-visible,.aside-item:focus-visible,.rel-card:focus-visible{outline:3px solid var(--flag);outline-offset:3px}
    .comparison-note{margin:34px 0;padding:24px 26px;background:var(--white);border:2px solid var(--ink);border-top:4px solid var(--flag)}
    .comparison-note h2{margin:0 0 12px;padding:0;border:0;font-size:18px;text-transform:uppercase}
    .comparison-note p{margin:0}
    .table-container{overflow-x:auto;margin:28px 0 36px;border:2px solid var(--ink);background:var(--white)}
    .table-container table{width:100%;min-width:680px;border-collapse:collapse;font-size:15px;line-height:1.45}
    .table-container th,.table-container td{padding:13px 14px;border-bottom:1px solid #cbd5e1;text-align:left;vertical-align:top}
    .table-container th{background:var(--ink);color:#fff;font-family:var(--gr-meta,Inter,system-ui,sans-serif);font-size:10px;letter-spacing:.1em;text-transform:uppercase}
    .table-container tr:last-child td{border-bottom:0}
    .in-article-figure{margin:30px 0 36px;padding:12px;background:var(--white);border:2px solid var(--ink)}
    .in-article-figure img{width:100%;height:auto;aspect-ratio:1672 / 941;object-fit:cover}
    .in-article-figure figcaption{margin:10px 4px 2px;padding:0}
    .sources{margin:42px 0 0;padding:24px 26px;background:var(--white);border:1px solid #cbd5e1}
    .sources h2{margin:0 0 14px;padding:0;border:0;font-size:20px}
    .sources ol{margin:0;padding-left:20px;font-size:15px}
    .sources li{margin:0 0 12px}
    .provenance{margin-top:28px;padding-top:24px;border-top:1px solid #94a3b8;color:var(--grey);font-size:15px}
    .provenance p{margin:0 0 12px}
    @media(max-width:700px){.comparison-note,.sources{padding:20px}.table-container{margin-left:-2px;margin-right:-2px}.in-article-figure{margin-left:0;margin-right:0}}
    @media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.guide-card,.rel-card,.aside-item{transition:none}}
  </style>
"""


ARTICLE_SCHEMA = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": "Article",
            "@id": f"{CANONICAL}#article",
            "headline": H1,
            "description": DESCRIPTION,
            "articleSection": "Guides",
            "keywords": REGISTRY_RECORD["keywords"],
            "inLanguage": "en",
            "image": {
                "@type": "ImageObject",
                "url": f"https://www.golfraw.com{HERO}",
                "contentUrl": f"https://www.golfraw.com{HERO}",
                "width": 1672,
                "height": 941,
                "caption": HERO_ALT,
            },
            "datePublished": "2026-09-21",
            "dateModified": "2026-09-21",
            "author": {
                "@type": "Organization",
                "@id": "https://www.golfraw.com/about#editorial",
                "name": "GolfRaw Editorial",
                "url": "https://www.golfraw.com/about",
            },
            "publisher": {"@id": "https://www.golfraw.com#organization"},
            "mainEntityOfPage": CANONICAL,
        },
        {
            "@type": "Organization",
            "@id": "https://www.golfraw.com#organization",
            "name": "GolfRaw",
            "url": "https://www.golfraw.com/",
            "logo": {
                "@type": "ImageObject",
                "url": "https://www.golfraw.com/icon-512.png",
                "width": 512,
                "height": 512,
            },
        },
        {
            "@type": "BreadcrumbList",
            "@id": f"{CANONICAL}#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.golfraw.com/"},
                {"@type": "ListItem", "position": 2, "name": "Guides", "item": "https://www.golfraw.com/guides"},
                {"@type": "ListItem", "position": 3, "name": H1, "item": CANONICAL},
            ],
        },
    ],
}


def replace_meta(source: str, pattern: str, value: str, *, attribute: str = "content") -> str:
    escaped = html.escape(value, quote=True)
    regex = re.compile(
        rf'(<meta\s+{attribute}=["\']{re.escape(pattern)}["\']\s+content=["\'])[^"\']*(["\'])',
        re.I,
    )
    updated, count = regex.subn(rf"\g<1>{escaped}\g<2>", source, count=1)
    if count != 1:
        raise ValueError(f"missing metadata field: {pattern}")
    return updated


def ensure_registry() -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    articles = data.setdefault("articles", [])
    existing = next((item for item in articles if item.get("slug") == SLUG), None)
    if existing is None:
        articles.insert(0, REGISTRY_RECORD)
    else:
        existing.update(REGISTRY_RECORD)
    data["count"] = sum(not item.get("alias_of") for item in articles)
    categories = data.setdefault("categories", [])
    for value in REGISTRY_RECORD["category"]:
        if value not in categories:
            categories.append(value)
    data["categories"] = list(dict.fromkeys(categories))
    sections = data.setdefault("sections", [])
    if REGISTRY_RECORD["section"] not in sections:
        sections.append(REGISTRY_RECORD["section"])
    data["sections"] = list(dict.fromkeys(sections))
    REGISTRY.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_body() -> str:
    return f'''<div class="article-body">
          <p><b>THE SHORT ANSWER:</b> A 3-wood is usually the better choice for maximum distance from a tee or clean fairway lie, while a 3-hybrid is usually easier to launch, control and use from rough. Carry both only if they produce distinct carry gaps and serve different shots; the numbers on the soles do not make them redundant.</p>

          <h2>What is the actual difference between a 3-wood and a 3-hybrid?</h2>
          <p>A 3-wood normally has less loft, a longer shaft and a larger head than a 3-hybrid. Those design differences give the 3-wood more potential speed and distance, while the shorter hybrid is generally easier to control and use from varied lies.</p>
          <p>Stock length gaps calculated from <a href="https://www.taylormadegolf.com/Qi4D-Fairway/DW-TC448.html?lang=en_US" target="_blank" rel="nofollow noopener">TaylorMade</a>, <a href="https://mediacenter.titleist.com/en-US/217758-titleist-launches-new-tsr-fairway-metals/" target="_blank" rel="nofollow noopener">Titleist</a> and <a href="https://ping.com/en-us/golf-clubs/fairways/g440-lst-fairway" target="_blank" rel="nofollow noopener">PING</a> specifications accessed in September 2026.</p>
          <p>Current stock specifications illustrate the difference:</p>
          <ul>
            <li>The TaylorMade Qi4D fairway is listed at 15 degrees and 43.25 inches, while the <a href="https://www.taylormadegolf.com/Qi4D-3-Rescue/N8402707.html?lang=en_US" target="_blank" rel="nofollow noopener">Qi4D 3 Rescue</a> is 19 degrees and 40.75 inches.</li>
            <li>Current Titleist specifications show 15 degrees and 43 inches for the fairway wood against 19 degrees and 40.5 inches for one 3-hybrid configuration.</li>
            <li>PING lists its G440 3-wood at 15 degrees and 43 inches and its <a href="https://ping.com/en-us/golf-clubs/hybrids/g440-hybrid" target="_blank" rel="nofollow noopener">G440 3-hybrid</a> at 20 degrees and 40.25 inches.</li>
          </ul>
          <p>The stock length gaps are 2.5, 2.5 and 2.75 inches respectively.</p>
          <p>Those are examples, not universal standards. Adjustable hosels, custom shafts, high-launch heads and previous model generations can change the measurements. The consistent point is the architecture: the 3-wood asks the golfer to control a longer club with less loft.</p>
          <p>The number 3 causes most of the confusion. A 3-hybrid is generally designed to replace a long iron or sit near a high-lofted fairway wood, not to reproduce the full job of a 3-wood. <a href="https://www.callawaygolf.com/golf-guides/fairway-wood-buying-guide.html" target="_blank" rel="nofollow noopener">Modern fairway wood guidance</a> likewise distinguishes the longer, larger fairway wood from the more compact and versatile hybrid.</p>

          <h2>Which club is better from the tee, fairway and rough?</h2>
          <p>The same golfer may assign each club a different job depending on the lie. The 3-wood has the advantage when the job is maximum distance from a clean lie. The 3-hybrid has the advantage when control, uneven ground or grass around the ball makes the shorter build more useful.</p>

          <h3>Which club is better off the tee?</h3>
          <p>A 3-wood makes sense as a driver alternative when it produces a clearly shorter but still useful tee shot with a playable pattern. It can also be the correct club when driver distance would bring a bunker, penalty area or narrowing fairway into play.</p>
          <p>A 3-hybrid gives up potential distance but may suit a hole that demands a specific carry rather than maximum yardage. Do not assume the hybrid is automatically straighter. Compare the actual left-to-right pattern, because a shorter club can still be a poor tee option if its common miss is a hard hook or block.</p>

          <h3>Which club is better from a clean fairway?</h3>
          <p>The 3-wood wins only if the golfer can launch it from the ground often enough to use the extra speed. A low shot that runs a long way on a firm practice range may look impressive, but it is not the same as a carry number that clears a front bunker and lands on a green.</p>
          <p>The 3-hybrid is the safer choice when its median strike launches higher, carries farther than the golfer's poor 3-wood strikes and leaves a tighter pattern. The club that travels farthest on one perfect swing is not necessarily the club that owns the shot.</p>

          <h3>Which club is better from rough or an uneven lie?</h3>
          <p>A 3-hybrid usually has the practical edge from light rough because its shorter shaft and compact head are easier to manage around grass. That does not make a low-loft hybrid a magic escape club. From deep rough, the sensible shot may be a more lofted iron that returns the ball to safety.</p>
          <figure class="in-article-figure">
            <img src="{ROUGH_IMAGE}" alt="{html.escape(ROUGH_ALT, quote=True)}" width="1672" height="941" loading="lazy" decoding="async">
            <figcaption>A shorter hybrid can be the more useful long club when grass changes the strike.</figcaption>
          </figure>
          <p>The hybrid also tends to be easier from a hanging, downhill or sidehill lie because the golfer stands closer to the ball. A 3-wood remains possible from a clean, sitting-up lie, but the size of the head can become a liability when grass sits between the face and ball.</p>

          <h2>How much farther should a 3-wood go than a 3-hybrid?</h2>
          <p>There is no honest universal yardage gap between a 3-wood and 3-hybrid. The 3-wood should earn its place by producing a meaningful carry advantage without turning the normal miss into a recovery shot.</p>
          <div class="table-container">
            <table>
              <caption class="sr-only">3-wood versus 3-hybrid test results and likely bag decisions</caption>
              <thead><tr><th scope="col">Your test result</th><th scope="col">What it usually means</th><th scope="col">Likely bag decision</th></tr></thead>
              <tbody>
                <tr><td>The 3-wood carries clearly farther and keeps a playable pattern</td><td>The clubs perform different top-end jobs</td><td>Both may fit</td></tr>
                <tr><td>Median carry is similar but the hybrid pattern is tighter</td><td>The clubs overlap despite different labels</td><td>The hybrid has the stronger case</td></tr>
                <tr><td>The 3-wood wins only on its best one or two strikes</td><td>Its paper distance is not regularly usable</td><td>Keep it only for a proven tee-shot role</td></tr>
                <tr><td>The hybrid carries farther from the ground</td><td>The 3-wood is not launching or being struck well enough</td><td>Test more loft or reconsider the slot</td></tr>
              </tbody>
            </table>
          </div>
          <p>Compare carry, not total distance. Roll changes with turf firmness, slope and weather. Carry answers the question that matters when a shot must clear water, sand or rough.</p>
          <p>Use the median of the session rather than the single longest ball. Then record how often each club produces a severe miss, such as a top, heavy strike or shot far enough offline to change the next decision. A club that adds distance but doubles those failures may not have added a usable shot.</p>

          <h2>How should swing speed change the choice?</h2>
          <p>Swing speed affects the answer because a low-lofted 3-wood needs enough speed and reliable contact to create useful launch. Swing speed is not, by itself, a reason to carry or remove either club.</p>
          <p>A golfer with less speed should watch the ball flight. If the 3-wood launches low, lands flat and gains most of its distance through roll, a higher-lofted fairway wood or hybrid may create more usable carry. More loft can produce more distance when the lower-lofted club never gets into an effective flight window.</p>
          <p>A faster golfer is more likely to create clear separation between the clubs, but speed introduces another test: dispersion. Extra ball speed has little value if the longer shaft produces a much wider pattern or a miss that reaches hazards the hybrid avoids.</p>
          <p>Tour equipment trends are a poor shortcut for an amateur bag. GolfRaw's examination of <a href="/why-pros-are-ditching-hybrids">why some professionals move away from hybrids</a> concerns elite speed, flight control and preferred shot shape, not a command for other golfers to copy the same setup.</p>

          <h2>Which club is easier for a higher-handicap golfer?</h2>
          <p>A 3-hybrid is usually easier for a higher-handicap golfer to use from the ground, but a 3-wood can still earn a place as a tee club. Handicap alone cannot decide the slot because two golfers with the same index may have completely different speed, launch and strike patterns.</p>
          <p>Judge the 3-wood on three questions:</p>
          <ol>
            <li>Can it get airborne from the fairway without requiring a perfect lie?</li>
            <li>Does it provide a dependable tee shot that the driver and hybrid do not already cover?</li>
            <li>Does the typical miss still advance the ball safely?</li>
          </ol>
          <p>If the answer is no to all three, the club is luggage. If the 3-wood is reliable from a tee but poor from the ground, label it honestly as a tee club and judge whether that one job justifies the slot.</p>
          <p>The hybrid deserves the same scrutiny. Some golfers dislike the look, strike it left or produce too little separation from the next iron. Easier in theory does not outrank the player's actual pattern.</p>

          <h2>Can a 3-wood and 3-hybrid both belong in the same bag?</h2>
          <p>Yes. A 3-wood and 3-hybrid belong together when each covers a distinct carry, trajectory or lie, rather than duplicating the same comfortable range shot.</p>
          <p>The <a href="https://www.usga.org/content/usga/home-page/custom-search-pages/rules/2019-golf-rules-and-interpretations/fr-rule-4.html" target="_blank" rel="nofollow noopener">USGA's Rule 4.1b</a> limits a player to 14 clubs during a round, so every long-club overlap consumes a slot that could cover another distance or shot.</p>
          <div class="comparison-note" role="note" aria-label="Suggested club roles">
            <h2>A useful division of labor</h2>
            <ul>
              <li><strong>3-wood:</strong> maximum fairway-club carry, a driver alternative or a second shot into a reachable par 5.</li>
              <li><strong>3-hybrid:</strong> long approaches, light rough, uneven lies or a controlled tee shot to a defined landing area.</li>
              <li><strong>Both:</strong> clear carry separation plus different lie or trajectory coverage.</li>
              <li><strong>Neither:</strong> another wood, hybrid or long iron already performs those jobs more consistently.</li>
            </ul>
          </div>
          <p>GolfRaw's <a href="/tools-bag-audit">Bag Audit</a> uses carry, usage and trust to expose overlaps. For adjacent clubs, it treats less than eight yards as potential redundancy, 10 to 15 yards as a useful target and more than 20 yards as a possible hole. Those are audit flags, not laws of ball flight, but they force the correct question: what does each club add?</p>

          <h2>How do you test both clubs without fooling yourself?</h2>
          <p>Test both clubs with the same ball, target and conditions, then compare median carry, dispersion and severe-miss frequency from the lies that matter. Do not buy or remove a club based on five warm range balls or the longest shot of the session.</p>
          <ol>
            <li><strong>Inspect the clubs first:</strong> Clean the faces, check the grips and make sure an obvious equipment problem is not distorting the comparison. Before replacing an older club, check <a href="/how-long-do-golf-clubs-last">whether the club itself is actually worn out</a>.</li>
            <li><strong>Create the same test for both:</strong> Use one ball model and one target line. Alternate clubs rather than hitting every 3-wood first and every hybrid after fatigue or rhythm changes.</li>
            <li><strong>Test the jobs you expect them to perform:</strong> Hit a repeatable set from a low tee, a clean fairway lie and light rough. Eight to 10 shots per lie is enough to reveal a pattern without turning the session into an endurance test.</li>
            <li><strong>Keep the ugly shots in the record:</strong> Tag obvious tops, chunks and major directional misses instead of deleting them. The failure rate is part of the club's performance.</li>
            <li><strong>Compare five outputs:</strong> Record median carry, left-to-right spread, short-to-long spread, severe misses and subjective confidence. A launch monitor helps, but marked targets and honest observation can still reveal which pattern is usable.</li>
            <li><strong>Assign a job before assigning a slot:</strong> Write one sentence for each club: what shot is this club carried to hit? If both sentences describe the same lie, distance and trajectory, the bag probably contains an overlap.</li>
            <li><strong>Repeat the test on the course before selling either club:</strong> Range mats can hide poor turf interaction, while range balls and wind can distort distance. The final decision belongs to normal shots under normal pressure.</li>
          </ol>

          <h2>What else do golfers ask about 3-wood vs 3-hybrid?</h2>
          <h3>Why do PGA players not use hybrids?</h3>
          <p>PGA Tour players do use hybrids, but some elite players prefer high-lofted fairway woods or utility irons because those clubs fit their speed, preferred flight and shot-shaping needs. That choice should not be copied automatically. Amateur delivery, rough height, typical misses and required landing angle can produce a different answer.</p>

          <h3>What hybrid is equivalent to a three wood?</h3>
          <p>No numbered hybrid is automatically equivalent to a 3-wood. A typical 3-hybrid has more loft and a shorter shaft, so it normally fills a shorter carry slot. A very low-loft hybrid may approach a particular golfer's 3-wood distance, but equivalence should be established with measured carry, not the club number.</p>

          <h3>Is a hybrid better than a 3 wood?</h3>
          <p>A hybrid is better when it produces the required carry with a tighter strike pattern or must handle rough and uneven lies. A 3-wood is better when maximum distance from a tee or clean fairway matters and the golfer launches it consistently. Neither club is better without a defined shot.</p>

          <h3>Should a high handicapper use a 3 wood?</h3>
          <p>A high-handicap golfer should use a 3-wood only when it has a dependable job, often as a tee alternative or a long club from clean lies. If it launches low, is rarely used or produces frequent tops and heavy strikes, a hybrid or higher-lofted wood is likely to be more useful.</p>

          <h2>Which club should you put in the bag?</h2>
          <p>Choose the club that produces the missing shot, not the club whose label looks correct. The 3-wood should provide dependable top-end distance; the 3-hybrid should provide useful control and lie coverage.</p>
          <ul>
            <li>Choose the <strong>3-wood</strong> when it creates a clear carry advantage and a playable tee or fairway pattern.</li>
            <li>Choose the <strong>3-hybrid</strong> when it reaches the required distance more consistently and handles more of the lies faced during a round.</li>
            <li>Carry <strong>both</strong> when the carry gaps are distinct and the shot descriptions are different.</li>
          </ul>
          <p>If the answer is still hidden by optimistic yardages, run the <a href="/tools-bag-audit">free Bag Audit</a> with normal-day carry numbers, usage and trust. The unused or overlapping slot usually exposes itself.</p>

          <section class="sources" aria-labelledby="sources-label">
            <h2 id="sources-label">Sources and specification notes</h2>
            <ol>
              <li><a href="https://www.taylormadegolf.com/Qi4D-Fairway/DW-TC448.html?lang=en_US" target="_blank" rel="nofollow noopener">TaylorMade Qi4D Fairway specifications</a>, accessed September 2026.</li>
              <li><a href="https://www.taylormadegolf.com/Qi4D-3-Rescue/N8402707.html?lang=en_US" target="_blank" rel="nofollow noopener">TaylorMade Qi4D 3 Rescue specifications</a>, accessed September 2026.</li>
              <li><a href="https://ping.com/en-us/golf-clubs/fairways/g440-lst-fairway" target="_blank" rel="nofollow noopener">PING G440 fairway specifications</a> and <a href="https://ping.com/en-us/golf-clubs/hybrids/g440-hybrid" target="_blank" rel="nofollow noopener">G440 hybrid specifications</a>, accessed September 2026.</li>
              <li><a href="https://www.titleist.com/golf-clubs/hybrid-golf-clubs/ts2" target="_blank" rel="nofollow noopener">Titleist TS hybrid specifications</a> and <a href="https://mediacenter.titleist.com/en-US/217758-titleist-launches-new-tsr-fairway-metals/" target="_blank" rel="nofollow noopener">Titleist fairway-metal specifications</a>, accessed September 2026.</li>
              <li><a href="https://www.callawaygolf.com/golf-guides/fairway-wood-buying-guide.html" target="_blank" rel="nofollow noopener">Callaway fairway wood buying guide</a>, accessed September 2026.</li>
              <li><a href="https://www.usga.org/content/usga/home-page/custom-search-pages/rules/2019-golf-rules-and-interpretations/fr-rule-4.html" target="_blank" rel="nofollow noopener">USGA Rule 4.1b: limit of 14 clubs</a>, accessed September 2026.</li>
            </ol>
          </section>

          <div class="provenance">
            <p><strong>How we reported this.</strong> GolfRaw compared manufacturer specifications with the practical jobs golfers ask these clubs to perform. The bag decision belongs to measured carry, dispersion, strike quality and lie coverage, not the number stamped on the sole.</p>
            <p><strong>Author.</strong> <a href="/about">GolfRaw Editorial</a>.</p>
            <p><strong>Published.</strong> <time datetime="2026-09-21">21 September 2026</time>.</p>
            <p><strong>Last updated.</strong> <time datetime="2026-09-21">21 September 2026</time>. <a href="/corrections">Corrections policy</a>.</p>
          </div>

          <nav class="tag-row" aria-label="Article tags">
            <a href="/guides">Guides</a><a href="/guides">Equipment</a><a href="/why-pros-are-ditching-hybrids">Hybrids</a><a href="/tools-bag-audit">Bag Audit</a>
          </nav>
        </div>'''


def build() -> None:
    ensure_registry()
    source = TEMPLATE.read_text(encoding="utf-8")
    source = replace_meta(source, "description", DESCRIPTION, attribute="name")
    source = re.sub(r"<title>.*?</title>", f"<title>{html.escape(TITLE)}</title>", source, count=1, flags=re.I | re.S)
    source = re.sub(r'(<link\s+rel=["\']canonical["\']\s+href=["\'])[^"\']*(["\'])', rf"\g<1>{CANONICAL}\g<2>", source, count=1, flags=re.I)
    source = replace_meta(source, "og:title", TITLE, attribute="property")
    source = replace_meta(source, "og:description", DESCRIPTION, attribute="property")
    source = replace_meta(source, "og:url", CANONICAL, attribute="property")
    source = replace_meta(source, "og:image", f"https://www.golfraw.com{HERO}", attribute="property")
    source = replace_meta(source, "og:image:width", "1672", attribute="property")
    source = replace_meta(source, "og:image:height", "941", attribute="property")
    source = replace_meta(source, "twitter:title", TITLE, attribute="name")
    source = replace_meta(source, "twitter:description", DESCRIPTION, attribute="name")
    source = replace_meta(source, "twitter:image", f"https://www.golfraw.com{HERO}", attribute="name")
    source = replace_meta(source, "robots", "index, follow, max-image-preview:large", attribute="name")
    source = replace_meta(source, "og:image:alt", HERO_ALT, attribute="property")
    source = replace_meta(source, "article:published_time", "2026-09-21", attribute="property")
    source = replace_meta(source, "article:modified_time", "2026-09-21", attribute="property")
    source = replace_meta(source, "article:section", "Guides", attribute="property")
    source = re.sub(
        r'(<meta\s+property=["\']article:author["\']\s+content=["\'])[^"\']*(["\'])',
        r"\g<1>GolfRaw Editorial\g<2>", source, count=1, flags=re.I,
    )
    source = replace_article_header(source, H1, STANDFIRST)
    source = re.sub(
        r'<nav class="crumbs".*?</nav>',
        '<nav class="crumbs" aria-label="Breadcrumb">\n'
        '          <a href="/">GolfRaw</a> / <a href="/guides">Guides</a> / '
        '<span>3-Wood vs 3-Hybrid</span>\n        </nav>',
        source, count=1, flags=re.I | re.S,
    )
    source = re.sub(
        r'<span class="cat">.*?</span>',
        '<span class="cat">Guides · Equipment &amp; Club Fitting</span>',
        source, count=1, flags=re.I | re.S,
    )
    source = re.sub(
        r'<div class="byline">.*?</div>',
        '<div class="byline">\n'
        '            <span>BY <b><a href="/about">GolfRaw Editorial</a></b></span>\n'
        '            <span>PUBLISHED <b>MON 21 SEP 2026</b></span>\n'
        '            <span class="live-upd">UPDATED 21 SEP 2026</span>\n'
        f'            <span><b>{READING_TIME.upper()}</b></span>\n'
        '          </div>',
        source, count=1, flags=re.I | re.S,
    )
    source = re.sub(
        r'<figure class="lead-img">.*?</figure>',
        f'''<figure class="lead-img">
          <img src="{HERO}" alt="{html.escape(HERO_ALT, quote=True)}" width="1672" height="941" fetchpriority="high" decoding="async">
          <figcaption>3-WOOD OR 3-HYBRID: THE RIGHT ANSWER DEPENDS ON THE SHOT. PHOTO: GOLFRAW</figcaption>
        </figure>''',
        source, count=1, flags=re.I | re.S,
    )

    body = build_body()
    body_start = source.index('<div class="article-body">')
    article_end = source.index('      </article>', body_start)
    source = source[:body_start] + body + "\n" + source[article_end:]

    aside_start = source.index('      <aside class="article-aside"')
    aside_end = source.index('      </aside>', aside_start) + len('      </aside>')
    aside = '''      <aside class="article-aside" aria-label="Related equipment coverage">
        <div class="aside-box">
          <div class="ab-head">Equipment &amp; club fitting</div>
          <a class="aside-item" href="/why-pros-are-ditching-hybrids"><span class="mono">GUIDE · HYBRIDS</span>Why pros are ditching hybrids</a>
          <a class="aside-item" href="/how-long-do-golf-clubs-last"><span class="mono">GEAR · WEAR</span>How long do golf clubs last?</a>
          <a class="aside-item" href="/tools-bag-audit"><span class="mono">FREE TOOL · BAG</span>Run GolfRaw's Bag Audit</a>
        </div>
      </aside>'''
    source = source[:aside_start] + aside + source[aside_end:]

    related_marker = '    <!-- ============ RELATED ============ -->'
    related_start = source.index(related_marker)
    related_end = source.index('  <!-- START NEWSLETTER SECTION -->', related_start)
    related = '''    <!-- ============ RELATED ============ -->
    <section class="related" aria-labelledby="related-heading">
      <div class="wrap">
        <h2 id="related-heading">Keep Reading <span class="idx">/ EQUIPMENT</span></h2>
        <div class="rel-grid">
          <a class="rel-card" href="/why-pros-are-ditching-hybrids"><div class="cat">Hybrid Guide</div><h3>Why Pros Are Ditching Hybrids, and Why You Shouldn't</h3><div class="d">TOUR EQUIPMENT · GOLFRAW</div></a>
          <a class="rel-card" href="/how-long-do-golf-clubs-last"><div class="cat">Club Wear</div><h3>How Long Do Golf Clubs Last?</h3><div class="d">EQUIPMENT · GOLFRAW</div></a>
          <a class="rel-card" href="/tools-bag-audit"><div class="cat">Free Tool</div><h3>GolfRaw's Bag Audit</h3><div class="d">CLUB GAPPING · GOLFRAW</div></a>
        </div>
      </div>
    </section>

'''
    source = source[:related_start] + related + source[related_end:]

    source = source.replace('</head>', ARTICLE_CSS + '\n</head>', 1)
    source = source.replace(
        '<!-- ============ STRUCTURED DATA (NewsArticle) ============ -->',
        '<!-- ============ STRUCTURED DATA (Article) ============ -->',
        1,
    )
    source = re.sub(
        r'<script type="application/ld\+json">.*?</script>',
        '<script type="application/ld+json">\n' + json.dumps(ARTICLE_SCHEMA, ensure_ascii=False, indent=2) + '\n</script>',
        source, count=1, flags=re.I | re.S,
    )
    source = finalize_article_template_metadata(source, OUTPUT)
    source = "\n".join(line.rstrip() for line in source.splitlines()) + "\n"
    OUTPUT.write_text(source, encoding="utf-8")
    print(f"published {OUTPUT}")


if __name__ == "__main__":
    build()
