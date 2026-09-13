# GolfRaw backlink and digital PR system

This is an earned-link workflow, not a link-volume campaign. The public destination is [`/press`](../../press.html). The verified asset registry lives in [`linkable-assets.json`](linkable-assets.json), and the working queue is [`prospect-tracker.csv`](prospect-tracker.csv).

## What is genuinely linkable

Start with a page that gives a reader something they can use, check, or understand better:

- The 13-tool portfolio at [`/tools`](../../tools.html), including 12 Free tools and the Coach Report Pro preview.
- The Standing Order's median carry, 80% shot band, and gap analysis at [`/tools-standing-order`](../../tools-standing-order.html).
- The public rating method at [`/ratings-manual`](../../ratings-manual.html).
- The dated, visible error ledger at [`/corrections`](../../corrections.html).
- The editorial background and funding disclosure at [`/about`](../../about.html).
- The current public Pro and Coach Report surfaces at [`/pro`](../../pro.html) and [`/tools-coach-report`](../../tools-coach-report.html).
- Evergreen guides only when the page answers the prospect's actual question. The registry records the approved examples.

The asset registry is the claim boundary. If a pitch needs a statistic, customer result, survey, aggregate tool output, named expert, or first-hand test that is not recorded there or on the linked page, stop and verify it before writing.

## Prospect categories

| Category | Look for | Best GolfRaw fit |
| --- | --- | --- |
| Golf media | Reporters, editors, resource pages, explainers, and tool roundups | Fresh tournament context, useful calculators, methodology, corrections transparency |
| Golf newsletters | Curated weekly links, instruction newsletters, independent golf writers | A short reference readers can use immediately |
| Equipment publications | Club testing, gapping, fitting, launch-monitor, and buying-guide coverage | Standing Order, Coach Report preview, swing-speed and equipment guides |
| Amateur golf organizations | Clubs, leagues, federations, university programs, and tournament organizers | Tournament rules guide, beginner resources, free tools |
| Data/sports journalists | Sports data, ratings, analytics, media standards, and methodology writers | Ratings manual, disclosed calculation methods, corrections ledger |
| Course/travel publications | Course guides, trip planning, beginner and destination resources | Beginner guide, tournament/rules guide, equipment and tee-time references |

Do not treat a homepage, thin affiliate page, inactive author, unrelated forum, paid placement, or direct competitor as a qualified prospect without a specific editorial reason.

## Qualification and research

Build a list of 20 to 40 real people or editorial pages, not a database dump. Before adding a prospect, read the author's last five relevant pieces, record the publication and beat, check the author's bio and current activity, and record the exact source URL for the contact path. Never guess an email address.

Use queries such as:

- `golf club gapping resources`
- `golf tools roundup`
- `golf ratings methodology`
- `golf corrections transparency`
- `amateur golf tournament rules guide`
- `launch monitor CSV golf coach`
- `golf newsletter equipment guide`

Score journalist fit from 1 to 10 using beat match 3x, reach 2x, engagement 2x, and recency 1x. Tier 1 prospects receive a fully custom pitch. Tier 2 prospects receive a lightly customized pitch. Skip Tier 3 unless the story is unusually strong.

## Earned-link angles

1. **Useful tool reference:** A journalist is already explaining a problem such as gapping, tee choice, handicap maths, or round review. Offer the relevant free tool as a practical reader resource.
2. **Calculation transparency:** The Standing Order explains why it uses a median, how the 80% band works, and where the five-shot minimum matters. Offer it as a reference for an article about range data or club fitting.
3. **Methodology reference:** The Ratings Manual is a citable explanation of weighted player ratings and the boundary between data and judgment.
4. **Corrections case study:** The Corrections Log can support a story about reader fact-checking or how small publishers record mistakes. Pitch the practice, not a claim that GolfRaw is perfect.
5. **Coach handover workflow:** The public Pro and Coach Report pages show how launch-monitor CSV input and a one-page report fit into a coach or fitter workflow. Do not mention history sync or advanced modelling unless a later page verifies them.
6. **Guide update:** Suggest a specific existing guide only when the prospect has a related article that needs a reference, update, or practical companion.

The information gain must be clear: the proposed link should add a calculation, method, reference, or usable tool that the reader would not get from the prospect's existing paragraph alone.

## Humanized outreach drafts

Do not send these unchanged. Replace every bracket, mention the journalist's actual recent work, and keep the final pitch under 150 words.

### Resource or list inclusion

**Subject:** A free gapping reference for [article]

Hi [name],

I read your piece on [specific article]. The section on [specific point] made me think of a useful companion for readers who want to check their own numbers.

GolfRaw's Standing Order logs five to ten carries per club, reports the median, shows an 80% shot band, and flags gaps or overlaps. The page also explains its thresholds, so readers can see what the calculation means.

If you keep a resources section or update the piece, here it is: https://www.golfraw.com/tools-standing-order

No need to reply if it is not a fit.

[name]

### Method or transparency reference

**Subject:** A public golf ratings method worth citing

Hi [name],

Your recent [article/newsletter] looked at [specific beat]. One public reference may help with the methodology side: GolfRaw publishes its player-rating method, including the weighted components, the role of judgment, and the rule that a rating locks at publication.

The method is here: https://www.golfraw.com/ratings-manual

If your piece covers how sports ratings are built, this gives readers something concrete to inspect. The site also keeps a dated corrections ledger, which is here: https://www.golfraw.com/corrections

Best,

[name]

### Coach, fitter, or equipment angle

**Subject:** A golf data handover your readers can inspect

Hi [name],

I saw your coverage of [specific equipment or fitting topic]. GolfRaw has a public page showing its current Coach Report preview and a related Standing Order workflow. The useful part is the handover: launch-monitor CSV input and a one-page report built from numbers already on the device.

The public references are here: https://www.golfraw.com/pro and https://www.golfraw.com/tools-coach-report

If you cover coach or fitter workflows, they may be useful as a concrete example. I am happy to answer questions through contact@golfraw.com.

[name]

## Tracker rules

Use one row per target. `target` is the exact page, journalist, newsletter, or organization. `contact_or_source` and `contact_path` must be based on a source URL recorded in `source_url`. `linked_asset` must match an `id` in the asset registry. `status` should use a small controlled set such as `unresearched`, `qualified`, `ready`, `sent`, `replied`, `placed`, `declined`, or `closed`.

Record the response verbatim only when useful, and capture the acquired link or mention separately from the placement URL. A follow-up is allowed on day 3 and day 7 only when there is new information. After day 7, close the row until there is a genuinely new story.

Never use paid-link schemes, link exchanges, PBNs, mass directory submissions, fake experts, invented contacts, or generic blasts. Do not send a pitch until the journalist, beat, source URL, linked asset, and reason for the email are all filled in.
