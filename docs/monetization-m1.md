# Monetization M1: light ads on free tools, Pro ad-free

Status on 22 September 2026 (M1.1): **wired and verified on the four phase A
pilots (Distance Check, Tee Box, Plays Like, Bag Audit), held for readers.**
- The manual units are `8457096514` (after_result) and `1432433875` (lower).
- The owner added those four URLs to the Auto ads page exclusions. Live checks
  after that still found Auto ads on the pilots: an in-page unit on Distance
  Check and Tee Box, and an anchor on Tee Box. So `AUTO_ADS_EXCLUDED` stays
  `false`, and readers get no ad code on any tool page.
- In the owner's browser Google's consent message reports consent mode as not
  configured (`googlefc.getGoogleConsentModeValues()` returns 4 for every
  purpose), and GA4 still pings `gcs=G100` after an Accept. The Privacy &
  messaging consent-mode toggles are not in effect yet.
- Every other tool page loads the consent message and nothing else.

To release to readers:
1. In AdSense, check that each exclusion is the exact page URL
   `https://www.golfraw.com/tools-…`, "This page only".
2. Wait for it to apply. A QA browser (below) must show no
   `.google-auto-placed` element and no `ins[data-anchor-status]` on any
   pilot.
3. Set `AUTO_ADS_EXCLUDED = true`, bump `version` and `VER`, rewire, deploy.

QA without counting impressions: in a test browser set localStorage
`gr_adtest` to `1`. The module then adds `data-adtest="on"` to its units and
skips the `AUTO_ADS_EXCLUDED` hold (never the Pro or page checks). Never
click a live ad. Test with the tab in the foreground: AdSense requests
nothing in a background tab.

## Product decisions

- **Free tools carry light ads; GolfRaw Pro is ad-free.** No separate
  "remove ads" plan, no one-off ad-removal payment. GolfRaw is still learning
  how the tools are used; pricing stays as it is.
- **No Pro house ad yet.** Pro today is launch-monitor import and the Coach
  Report. That is too narrow to advertise beside an AdSense unit on every tool.
  Revisit when Pro has broader value.
- **No new ad network.** AdSense only, the account already in `ads.txt`.
- **Manual placements on tools, never Auto ads.** Auto ads scan the page and
  place ads where they predict performance. Google documents no way to keep
  them out of a form, and they add anchor and vignette formats. Tools are
  interactive, so they only get the two manual slots below.
- **Articles keep Auto ads** (in-page plus a mobile anchor, as observed live).
  The only change on articles is that a live Pro pass skips AdSense.

## How it works

- `lib/ads/tool-ads.js` is the one ads file for tool pages. It is wired by
  `scripts/wire_ads.py` as the managed `TOOL-ADS` block and replaces the old
  inline loader.
  - It loads Google's CMP (Funding Choices, "Privacy & messaging") on the
    first interaction or after 6s, as the rest of the site does.
  - Slots are `<div class="gr-ad-slot" data-gr-ad="after_result|lower">` in
    the page. Nothing renders and no ad code loads until the golfer has a
    result on screen.
  - Slot A sits inside the result container, after its share actions, so it
    appears with the result and hides with it.
  - Slot B sits low on the page, before the FAQ. It renders when the result
    container is first shown (`data-gr-ad-when`).
  - Each unit is requested once per page view; reopening or re-running a
    result never requests again.
  - The label is "Advertisements", one of the two labels Google allows, and
    the slot is a labelled complementary region. It never takes focus.
  - A 40px top margin and a rule keep a dead zone between the result's
    buttons and the ad.
  - The units are fixed rectangles (`data-ad-format="rectangle"`, no
    full-width), so a phone gets a 300x250-class ad rather than a full-screen
    one.
  - 318px of space (280px for the unit) is reserved when the slot renders,
    which happens within the click that produced the result, so the fill does
    not shift the page.
  - In the EEA, UK and Switzerland the slots wait for the answer to Google's
    consent message (TCF `tcloaded` or `useractioncomplete`, or
    `gdprApplies:false` elsewhere). While the message is open they take no
    space and load nothing. A visitor who never answers sees no ad and no gap.
  - Unfilled, blocked, failed or throwing: the slot collapses and the tool is
    untouched. So does a unit AdSense leaves silent for 12s. That clock counts
    only time with the slot on screen and the tab in the foreground, because
    AdSense holds units below the fold and requests nothing in a background
    tab.
- **Pro:** the pass `lib/pro/pro.js` keeps in `localStorage`
  (`golfraw_pro_pass`, `v1.<payload>.<sig>`, `exp` in seconds). A pass with a
  future `exp` means no slots and no adsbygoogle.js, on tools and on articles.
  The browser cannot verify the signature, and does not need to: a forged pass
  only removes ads for its forger, like an ad blocker. Pro features remain
  server-verified.
- **Switches** (top of `tool-ads.js`):
  - `UNITS`: the two ad unit ids. Empty means off.
  - `AUTO_ADS_EXCLUDED`: `false`. Set it to `true` only once a QA browser
    shows no Auto ads on every `PAGES` slug. Exclude a page in AdSense before
    adding it to `PAGES`.
  - `PAGES`: the rollout list. Phase A is the four pilots.
  - A localhost-only test switch (`gr_ads_test` in localStorage) points the
    module at `tests/fixtures/adsbygoogle-stub.js`. It is ignored on the live
    domain.

## Consent

| Item | Status |
|---|---|
| CMP for EEA, UK and Switzerland ads | **Correct.** Google's own European regulations message, Google-certified (CMP id 300), IAB TCF. Verified live: TC string present, `gdpr=1&gdpr_consent=…` on ad requests, a refusal serves limited ads. |
| AdSense and consent | **Correct.** AdSense reads the TC string itself. |
| GA4 and consent | **Fixed in code, and needs the Privacy & messaging toggles.** Before this change GA4 had no Consent Mode and set `_ga` cookies even after a refusal. Every GA4 page now sets defaults (denied for the EEA, UK and Switzerland, granted elsewhere, `wait_for_update: 500`) before gtag.js. |
| Google Ads tags | None on the site. |

Google policy requirement versus legal interpretation:
- A certified TCF CMP for ads in the EEA, UK and Switzerland is a Google
  requirement, and it is met.
- Whether analytics cookies need prior consent is a legal question. The code
  now matches what the privacy page promised. This is not legal advice.

Until "Enable consent mode for analytics purposes" is on, GA4 in those regions
sends cookieless pings only, and those users drop out of standard reports.

## Placement map

| Tool | Slot 1 | Slot 2 | Class | Phase |
|---|---|---|---|---|
| Distance Check | after the result card (below the Bag Audit hand-off and the copy button) | before the FAQ | A | A |
| Tee Box | after the result's share bar | before the FAQ | A | A |
| Plays Like | after the result's share bar | before the FAQ | A | A |
| Bag Audit | after the result's share bar | after the explainer, before "The Rest Of The Suite" | A | A |
| Gimme Audit | after the result's share bar | after the explainer, before the suite links | A | B |
| Handicap Lie Detector | after the result | after the explainer, before the FAQ | A | B |
| Tilt Meter | after the result | after the explainer, before the suite links | A | B |
| Settle Up | after "How we got there", which follows who-pays-whom and the share bar | none: the page is the result and the FAQ | B | B |
| Round Card | after the result card, below save and share | none: frequent users should not scroll past two ads to reach their rounds | B | B |
| Tendency Engine | after the results panel, never in the hole stepper | none | B | B |
| Grudge Match | after the simulation panel, never among the sliders | none | B | B |
| Standing Order | none: it is a live logger tapped mid-session | after the explainer, before the FAQ | B | B |
| Field Reader | none: live sliders and a live ranking | after the explainer, before the FAQ | B | B |
| Coach Report | none | none | C (the Pro product surface) | never |
| Round Autopsy | none | none | C (legacy, points to the Round Card) | never |

Never:
- inside a form or input panel, or between an input and its button;
- inside a scorecard or its entry;
- inside who-pays-whom;
- over or inside a result;
- as a popup, a modal, an interstitial, or a sticky mobile ad.

## Measurement plan

Revenue comes from AdSense, product health from GA4. Nothing about ads is sent
to GA4: no ad events, no earnings, no client ids.

- **Guardrails,** per tool page from GA4 tool events, pilots against the
  non-pilot tools over the same weeks:
  - start rate: `tool_started / tool_viewed`
  - completion rate: `tool_completed / tool_started`
  - share rate: `result_shared / tool_completed`
  - related-tool click rate: `related_tool_clicked / tool_completed`
  - returning users per tool page, from GA4's aggregate new or returning
    dimension
- **Core Web Vitals:** Search Console's Core Web Vitals report and CrUX for
  the tool URLs, plus the lab probe below.
- **Monetization:** AdSense by ad unit (`after_result`, `lower`): page RPM,
  impression RPM, Active View viewability, impressions per page view. A URL
  channel per pilot page is optional.
- **Fail rule:** after at least two weeks and 200 views on a pilot page, a
  placement fails if any of these hold, whatever the RPM:
  - completion, share or related-tool click rate falls more than 10% (relative)
    against the control tools;
  - CLS at p75 rises above 0.1;
  - LCP at p75 worsens by more than 10%.
- **Baseline:** there is no stable one.
  - Tool events started on 21 September 2026 and the custom dimensions are not
    registered.
  - GA4 is not connected to the Supermetrics account used here.
  - The consent defaults shipped at the same time also move EEA, UK and Swiss
    numbers.
  - So compare pilots with control tools over the same period, not before
    with after.
  - The lab baseline is below.

### Lab baseline (live, 375px, before ads)

| Page | LCP | CLS | Requests | JS files / KB | Ad requests |
|---|---|---|---|---|---|
| Distance Check | 468 ms | 0 | 15 | 8 / 36 | 0 |
| Tee Box | n/a (pane hidden) | 0 | 21 | 13 / 117 | 0 |
| Bag Audit | n/a | 0 | 20 | 12 / 113 | 0 |
| Plays Like | n/a | 0 | 21 | 12 / 114 | 0 |

Measured in the in-app browser. Tee Box, Bag Audit and Plays Like include the
consent script, which loads after 6s. Distance Check did not load it because
generated tools had no loader; every tool page now does.

## Activating phase A (steps 1 to 3 done by the owner on 22 September 2026)

1. **AdSense → Privacy & messaging → European regulations → Settings:** turn
   on "Enable consent mode for analytics purposes" and "Enable consent mode
   for advertising purposes".
2. **AdSense → Ads → By site → golfraw.com → Page exclusions:** add every
   `/tools-*` URL, "This page only". Also turn off "Allow Google to optimize
   existing ads" in the same Auto ads settings; it only touches manual units,
   and articles have none.
3. **AdSense → Ads → By ad unit → Display ads:** create two responsive units,
   "GolfRaw tools: after result" and "GolfRaw tools: lower". Copy their ids
   (`data-ad-slot`).
4. In `lib/ads/tool-ads.js`:
   - set `UNITS` to those ids (done);
   - once step 5 shows no Auto ads, set `AUTO_ADS_EXCLUDED = true`;
   - bump `version` and `VER` in `scripts/wire_ads.py`;
   - run `python3 scripts/wire_ads.py`, then deploy.
5. Validate live without clicking any ad:
   - one adsbygoogle.js request;
   - `ads?…slotname=` requests only after a result;
   - no `google-auto-placed` elements or anchor on tool pages;
   - Pro pass: no requests.
6. After two to four weeks against the fail rule, extend `PAGES` and add
   phase B markup per the map.
