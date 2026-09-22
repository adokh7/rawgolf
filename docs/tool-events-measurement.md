# Tool events: the first 28 days

Instrumentation shipped 21 Sep 2026. Measure 22 Sep – 19 Oct 2026 (28 full
days). No baseline exists yet; every number below is filled in from GA4 after
the window closes, not estimated before it.

## Before reading any number (GA4 admin, one-time)

1. **Register event-scoped custom dimensions** (Admin → Custom definitions),
   parameter name = dimension name: `tool_id`, `tool_name`, `input_mode`,
   `share_method`, `from_tool`, `to_tool`, `placement`, `error_code`,
   `view_type`, `tool_access`, `anchor_type`, `game_type`, `scoring_mode`, `round_length`,
   `detail_mode`. Until they exist the events arrive
   but cannot be broken down. They are not retroactive, so do this first.
   `game_type` (`skins`, `nassau`, `skins_nassau`) and `scoring_mode` (`gross`, `net`) only appear on
   The Settle Up's `tool_completed`, never with a name, score, handicap, stake or balance.
   `anchor_type` only appears on The Distance Check's `tool_completed`:
   `driver_carry`, `iron_carry`, `swing_speed` or `handicap_band`.
   `round_length` (`nine`, `eighteen`) and `detail_mode` (`quick`, `detailed`) only appear on
   The Round Card's `tool_completed`, never with a score, course, date, hole or history count.
2. **Keep test traffic out.** Events sent from `localhost`, or with
   `localStorage.gr_track_debug = '1'`, carry `debug_mode`. Activate the
   Developer traffic data filter, or filter every report to
   hostname = `www.golfraw.com`.
3. `page_path` maps onto GA4's built-in page path; no dimension is needed.

## Counting rules the events follow

- One `tool_viewed` per page load (`view_type = shared_result` when someone opens
  a shared Coach Report link; exclude those from tool funnels).
- `tool_started` and `tool_completed` fire at most once per `input_mode` per page
  view. Recalculating, live re-renders and Save-reruns do not add completions.
- `input_mode`: `manual` (the golfer's own data), `sample` (a sample button),
  `import` (a CSV import, or the Coach Report's data from other tools).
- `result_shared` counts only after a completion in the same page view, and only
  once the copy, download, native share or print actually went through.

## Per-tool metrics

"Real" means `input_mode` is `manual` or `import`. Report sample separately.

| Metric | Formula |
|---|---|
| Views | count(`tool_viewed`, view_type = tool) |
| Starts | count(`tool_started`, real) |
| Completions | count(`tool_completed`, real) |
| Start rate (per view) | Starts / Views |
| Completion rate (per start) | Completions / Starts |
| Share rate (shares per completion) | count(`result_shared`) / count(`tool_completed`, all modes). Can exceed 100%: one result can be shared twice. |
| Sharing completers (bounded) | users with ≥1 `result_shared` / users with ≥1 `tool_completed` |
| Related-tool click rate (per completion) | count(`related_tool_clicked`, from_tool = tool) / count(`tool_completed`, all modes) |
| Related-tool click rate (per view) | count(`related_tool_clicked`, from_tool = tool) / Views. Use this for suite links, which show before any result. |
| Sample reliance | count(`tool_completed`, sample) / count(`tool_completed`, all modes) |
| Error rate (per view) | count(`tool_error`) / Views, broken down by `error_code` |

Always state the denominator next to a rate. None of these is a "conversion
rate".

## Funnels (GA4 Explore → Funnel exploration)

- **Tool funnel:** `tool_viewed` → `tool_started` → `tool_completed` →
  `result_shared`, filtered to one `tool_id`. Run it twice: real modes, then
  sample.
- **Cross-tool funnel (same session, indirectly followed):** `tool_completed`
  (tool_id = X) → `related_tool_clicked` (from_tool = X) → `tool_started`
  (tool_id = Y) → `tool_completed` (tool_id = Y). The best-instrumented pair is
  Gimme Audit → Handicap Lie Detector (`placement = result_chain`).
- **Return use:** users with `tool_completed` in 2+ sessions (repeat use), and
  sessions with `tool_started` for 2+ distinct `tool_id` values (multi-tool
  sessions). These use GA4's own anonymous client id. GolfRaw keeps no counters
  of its own.
- **Future Pro funnel:** `round_logged` → repeated rounds → `pro_preview_viewed`
  → waitlist or purchase. These event names are reserved in the helper and fire
  nowhere yet.

## What each tool counts as start, complete and share

| Tool | Start | Complete | Share | Related |
|---|---|---|---|---|
| Settle Up | setup, rules or a score edit; Settle up | Settle up with a complete, valid card (sends `game_type`, `scoring_mode`) | copy summary, native share (not counted if cancelled), PNG | none in body |
| Tee Box | carry/score/yards edit or preset chip | Check my tees / Enter | copy, PNG, native share | Distance Check (`input_distance_check`) |
| Plays Like | condition edit, chip or toggle | What does it play / Enter | copy, PNG, native share | Distance Check (`result_distance_check`) |
| Bag Audit | club edit; Load a typical bag (sample) | Audit the bag | copy, PNG, native share | Rest of the Suite links |
| Handicap Lie Detector | claim or round edit, Add a round | Run the lie detector | copy, PNG, native share | none |
| Round Card | setup or card edit; Open it here on a Round Autopsy card (import) | What cost me this round with every hole scored (sends `round_length`, `detail_mode`) | copy summary, native share (not counted if cancelled), print | Tendency Engine (`result_patterns`) |
| Round Autopsy (off the hub, still live) | setup or card edit | Run the autopsy | PNG, native share | Round Card (`legacy_notice`) |
| Tilt Meter | hole edit; Load a sample meltdown (sample) | Run / Enter on hole 18 | copy, PNG, native share | Round Card (`legacy_notice`); Rest of the Suite links |
| Gimme Audit | score, tier or bucket edit; Load a typical round (sample) | What did I actually shoot | copy, PNG, native share | Handicap chain; suite links |
| Grudge Match | handicap, slider, format, swap; Load a typical argument (sample, auto-runs) | first simulation shown (live reruns deduped) | copy, PNG, native share | none |
| Standing Order | first logged shot; CSV import applied (import) | See the gaps, or auto after import | print | Build the coach report |
| Tendency Engine | a hole tap or course name | See my tendencies / Next on 18, with ≥1 finished round (not the render on load) | none | Round Card; Handicap handover link |
| Field Reader | slider, surface or pick | first re-rank after an edit (not the ranking on load) | none | none |
| Coach Report | form edit or Build (import) | Build with at least one data source | print, copy share link | none |
| Distance Check | unit, anchor, number, band or group edit; Show my distances | Show my distances with a valid number or band (Enter too) | copy | Bag Audit, Tee Box, Standing Order |

## Read with care

- Consent refusals and blockers remove events and page views together, so rates
  hold up better than raw counts.
- Field Reader re-ranks live, so its start and completion are nearly the same
  event. Judge it on start rate and return use instead.
- Grudge Match runs on valid defaults, so a Run with no edits counts as manual.
- Coach Report builds with no source data count as a start, not a completion.
  That gap is itself the signal to watch.
- Tendency Engine needs 18 holes before anything completes, so expect a low
  completion rate and read return use alongside it.
- Units are not measured. The yards/metres, °F/°C and mph/km/h switches carry
  `data-gr-ignore`, so they are neither a start nor an event, and no unit
  label is sent: GA4's country report already answers "who uses metres"
  closely enough, and nothing about the tools would change on the answer.
- The Round Card sends `round_length` and `detail_mode` on the first completion
  of a page view. `detailed` means putts or penalties were entered on at least
  60% of the holes. The quick/detailed split is the number to watch: it says
  whether golfers will give more than a score.
- The Distance Check sends `anchor_type` on the first completion of a page view
  only. A golfer who runs a 7-iron carry and then a handicap band counts once,
  as `iron_carry`. Read the split as "what golfers start from", not every run.
- Don't compare rates across tools until each has at least 100 views in the
  window.
