# GolfRaw Premium Tools Redesign

## Scope

Replace the incumbent brutalist visual treatment across every `tools-*.html` interactive tool and the shared Locker drawer. Preserve all calculations, JavaScript behavior, storage, URLs, SEO copy, structured data, and editorial language.

## Product Mode

Operate. The golfer must complete an analysis task quickly on a phone or desktop, understand state immediately, and trust that the result and saved data are unchanged.

## Direction: Tour Intelligence

The interface should feel like a tournament analysis desk distilled for a committed amateur: warm off-white canvas, crisp elevated white work surfaces, deep tournament green as the dominant action color, quiet zinc borders, compact numerical labels, and confident editorial headings. It rejects heavy black frames, blocky inverted section bars, square controls, and ornamental dashboard chrome.

### Visual System

- Canvas: warm zinc off-white with white elevated cards.
- Primary: `#0F392B`; deeper `#0A2A20` for high-emphasis result surfaces.
- Text: near-black warm zinc; secondary text must retain accessible contrast.
- Status: emerald for gains/success, amber for caution, restrained red only for destructive or negative states.
- Borders: 1px zinc lines; radii 12–20px; soft shadows used only to clarify elevation.
- Typography: preserve self-hosted Archivo and IBM Plex Mono. Archivo provides tight editorial hierarchy; IBM Plex Mono is reserved for measurements, ranks, and compact labels.
- Motion: 160–240ms state transitions, tactile pressed transforms, no decorative entrance animation, and complete reduced-motion support.

### Challenger Raises

- Ghost states: inactive segments remain visible and intentionally designed instead of disappearing.
- Billing hierarchy: importance is communicated with scale and spacing before color.
- Responsive integrity: layouts recompose at mobile breakpoints while controls remain at least 44px.

## Shared Architecture

Add a versioned shared stylesheet loaded after the existing embedded styles on every interactive tool page. It owns global tokens, page shell, cards, forms, buttons, explainers, tables, status surfaces, mobile safe-area behavior, and route-specific selectors. Existing embedded styles remain as behavioral fallback and to minimize risk; the shared layer intentionally overrides only presentation.

Update the Locker drawer's injected CSS to use the same tokens and component character. Keep its focus trap, dialog semantics, storage wiring, and import/export behavior unchanged.

Update the two generator scripts for the Tendency Engine and Field Reader so future regeneration preserves the shared stylesheet link and route refinements.

## Priority Surface Behavior

### Tendency Engine

- Present the 18-hole tracker as a focused score-entry workspace.
- Convert hole indicators and shot options into rounded tactile tap cards with clear selected, completed, disabled, hover, focus, and pressed states.
- Keep all questions and values unchanged.
- Turn the final “See my tendencies” action region into a sticky blurred mobile action bar without obscuring content or safe areas.
- Refine result tiles and charts into clean analytical cards with non-color status cues.

### Field Reader

- Treat the course summary as the analysis header and the weights as compact control cards.
- Improve range input affordance and live numeric feedback while preserving the model.
- Render rankings as premium list cards with decisive rank, fit score, explanation, and pick state.
- Keep four-pick limits and all calculations unchanged.

### Locker

- Replace the brutalist floating launcher with a refined pill and the drawer with a softly elevated sheet.
- Group profile, bag, scoring, and data controls into scannable cards.
- Preserve 44px targets, focus return, Escape close, focus trap, safe areas, and reduced-motion behavior.

## Dense Content

Existing explanatory copy and FAQ text must not change. Explanatory sections become visually scannable through cards, badges, spacing, and native `<details>` accordions where already present. No content is deleted or rewritten.

## Accessibility and Responsive Requirements

- Preserve semantic landmarks, labels, `aria-pressed`, dialog semantics, and live regions.
- Visible `:focus-visible` treatment on every interactive control.
- 44px minimum actionable targets with at least 8px spacing where controls are adjacent.
- No horizontal page overflow at 320, 375, 768, 1024, or 1440px.
- Sticky UI must respect `env(safe-area-inset-bottom)` and never cover the focused field or final content.
- Color never carries a result or selection alone.

## Verification

- Validate all changed HTML and generator output.
- Run available project tests and syntax checks for JavaScript and Python.
- Serve locally and capture desktop and mobile screenshots for the Tendency Engine, Field Reader, and representative shared-tool surface, plus the Locker open state.
- Exercise primary interactions: hole selection, score options, progress, result action, Field Reader sliders/picks, Locker open/close/profile controls.
- Run the production/deployment checks, the Impeccable detector once, and a final visual review.

## Direction Contract

- THESIS: A tour analysis desk for amateurs; reject framed brutalism and generic card-grid decoration.
- OWN-WORLD: Warm zinc canvas, tournament green actions, white elevated work surfaces, quiet borders, editorial Archivo, numerical Plex Mono.
- STORY: Enter quickly, see state clearly, understand the result, keep it privately.
- FIRST VIEWPORT: Compact editorial intro hands off immediately to one dominant analysis workspace and its obvious primary action.
- FORM: Premium sports analytics operate surface; brief-pinned canon; seed `9a45384d`.
- FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.
