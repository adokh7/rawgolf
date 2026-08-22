---
name: GolfRaw Tour Intelligence
description: Premium, blunt-edged golf analytics from The Tournament Desk.
colors:
  tournament-forest: "#0f392b"
  tournament-forest-strong: "#0a2a20"
  tournament-forest-soft: "#e7f0eb"
  warm-zinc-canvas: "#f7f7f5"
  card-white: "#ffffff"
  editorial-ink: "#181c1a"
  measured-grey: "#626a66"
  quiet-line: "#e4e4e1"
  quiet-line-strong: "#d3d5d1"
  positive: "#16724b"
  positive-soft: "#e7f6ee"
  caution: "#a85f06"
  caution-soft: "#fff4dd"
  negative: "#b43b31"
  negative-soft: "#fff0ed"
  focus: "#2e8b67"
typography:
  display:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "clamp(34px, 5vw, 60px)"
    fontWeight: 800
    lineHeight: 0.96
    letterSpacing: "-0.04em"
  headline:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "clamp(22px, 3vw, 30px)"
    fontWeight: 800
    lineHeight: 1.08
    letterSpacing: "-0.025em"
  title:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "18px"
    fontWeight: 900
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  body:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.6
  control:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 600
    lineHeight: 1.2
  label:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "11px"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "0.08em"
  measure:
    fontFamily: "IBM Plex Mono, ui-monospace, monospace"
    fontSize: "12px"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "0.065em"
rounded:
  control: "10px"
  option: "12px"
  container: "14px"
  surface: "18px"
  drawer: "20px"
  pill: "999px"
spacing:
  xs: "8px"
  sm: "10px"
  md: "12px"
  lg: "16px"
  xl: "18px"
  xxl: "24px"
  xxxl: "30px"
components:
  button-primary:
    backgroundColor: "{colors.tournament-forest}"
    textColor: "{colors.card-white}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "0 18px"
    height: "46px"
  button-primary-hover:
    backgroundColor: "{colors.tournament-forest-strong}"
    textColor: "{colors.card-white}"
    rounded: "{rounded.pill}"
  button-ghost:
    backgroundColor: "{colors.card-white}"
    textColor: "{colors.tournament-forest-strong}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "0 18px"
    height: "46px"
  input:
    backgroundColor: "{colors.card-white}"
    textColor: "{colors.editorial-ink}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "11px 13px"
    height: "48px"
  card:
    backgroundColor: "{colors.card-white}"
    textColor: "{colors.editorial-ink}"
    rounded: "{rounded.surface}"
    padding: "clamp(20px, 3vw, 30px)"
  option-selected:
    backgroundColor: "{colors.tournament-forest}"
    textColor: "{colors.card-white}"
    rounded: "{rounded.option}"
    height: "54px"
---

# Design System: GolfRaw Tour Intelligence

## Overview

**Creative North Star: "The Tournament Desk"**

GolfRaw should feel like the working desk behind a serious tournament broadcast: composed, fast to scan, and close to the numbers. A warm zinc canvas and white working surfaces keep the interface editorial; tournament forest green carries authority without turning every screen into branding.

The voice is blunt, but the interface is disciplined. Tactile controls, restrained lift, and compact mono measurements make dense golf data feel usable on the course and credible after the round. Avoid the old brutalist weight: one-pixel lines, tonal separation, and selective elevation replace heavy borders.

**Key Characteristics:**

- Tournament forest reserved for action, selection, and decisive result fields.
- Warm neutral canvas, clean white work surfaces, and quiet zinc dividers.
- Archivo-led editorial hierarchy with IBM Plex Mono for steps and measurements.
- Thumb-ready controls, restrained radii, crisp status color, and soft elevation.

## Colors

The palette is tournament green against warm zinc paper, with status colors used as factual signals rather than decoration.

### Primary

- **Tournament Forest** (#0f392b): Primary actions, selected controls, progress, and brand accents.
- **Deep Leaderboard Forest** (#0a2a20): Hero fields, verdict surfaces, table headers, and primary hover states.
- **Practice Green Wash** (#e7f0eb): Selected-adjacent states, navigation hovers, badges, and quiet green emphasis.

### Neutral

- **Warm Zinc Canvas** (#f7f7f5): Page background and translucent header base.
- **Card White** (#ffffff): Forms, cards, controls, and drawer work surfaces.
- **Editorial Ink** (#181c1a): Default copy and high-emphasis labels.
- **Measured Grey** (#626a66): Supporting copy, hints, and secondary labels.
- **Quiet Line / Strong Quiet Line** (#e4e4e1 / #d3d5d1): Structural dividers and control boundaries.

### Status

- **Positive** (#16724b) with **Positive Wash** (#e7f6ee): Confirmed success and favorable analysis.
- **Caution** (#a85f06) with **Caution Wash** (#fff4dd): Warnings and uncertain outcomes.
- **Negative** (#b43b31) with **Negative Wash** (#fff0ed): Errors, destructive actions, and unfavorable analysis.
- **Focus Green** (#2e8b67): Visible focus outlines and field focus rings.

### Named Rules

**The Scoreboard Rule.** Green marks what matters now: an action, a selection, progress, or the verdict. Do not wash whole screens in accent color.

## Typography

**Display Font:** Archivo (with system-ui fallback)

**Body Font:** Archivo (with system-ui fallback)

**Label/Mono Font:** IBM Plex Mono (with ui-monospace fallback)

**Character:** Archivo supplies blunt editorial authority without sacrificing tool clarity. IBM Plex Mono makes hole numbers, measurements, step markers, and compact metadata feel measured rather than ornamental.

### Hierarchy

- **Display** (800, clamp(34px, 5vw, 60px), 0.96): Short hero statements, balanced and capped near 13 characters per line.
- **Headline** (800, clamp(22px, 3vw, 30px), 1.08): Panel and answer headings with tight tracking.
- **Title** (900, 18px, 1.2): Drawer and compact surface titles.
- **Body** (400, 16px, 1.6): Explanations and analysis; long reading measures stay near 68–74ch.
- **Label** (800, 11–12px, 0.055–0.1em): Uppercase actions, section labels, and navigation.
- **Measure** (600, 10–12px): Numeric values, steps, and tabular golf data.

### Named Rules

**The Numbers Earn Mono Rule.** Use IBM Plex Mono only where sequence, measurement, or tabular comparison benefits from it; prose and actions stay Archivo.

## Layout

Content sits in the host page's bounded `.wrap`, with responsive inline padding of `clamp(18px, 4vw, 32px)` and 16px below 760px. Tool work surfaces lead the document order, followed by answer and supporting editorial blocks. Primary tool widths stay deliberately focused: 700px for the Tendency Engine and 760px for the Field Reader.

Spacing follows an 8–30px working rhythm. Panels use 20–30px responsive padding, 24px separation, and dense control groups at 7–12px. At 760px navigation becomes a 44px-target menu, panels tighten, and primary action bars may become sticky above the safe area. At 480px multi-column options simplify and action rows stack full width; the Locker becomes edge-to-edge below 420px.

## Elevation & Depth

Depth is layered, not theatrical. White cards sit on the warm canvas with a quiet one-pixel border and low ambient shadow; hoverable working surfaces may rise one step. Forest verdict fields gain stronger depth, while inputs use only a slight inset. Frosted header, sticky action, launcher, and Locker surfaces use blur because they physically overlay content.

### Shadow Vocabulary

- **Surface Low** (`0 1px 2px rgba(16, 24, 20, .04), 0 8px 24px rgba(16, 24, 20, .04)`): Default panels, cards, and compact data surfaces.
- **Surface Raised** (`0 2px 4px rgba(16, 24, 20, .05), 0 16px 36px rgba(16, 24, 20, .08)`): Hovered panels and decisive result surfaces.
- **Locker Float** (`0 24px 70px rgba(9, 24, 18, .24)`): The modal Locker drawer only.

### Named Rules

**The Quiet Lift Rule.** Borders establish structure; shadow communicates working depth or overlay state, never decoration.

## Shapes

The system uses 10px controls, 12px tactile options, 14px data containers, 18px primary surfaces, and a 20px floating drawer. Pills are reserved for actions, filters, navigation, badges, and values; content cards remain softly rectangular. Borders are one pixel and low contrast. The circular rings in the hero are atmospheric geometry, not a reusable card motif.

## Components

### Buttons

- **Shape:** 46px minimum-height pill with 18px horizontal padding; compact actions may be 42px, never below the practical touch floor.
- **Primary:** Tournament Forest with white 800-weight uppercase label and a subtle grounded shadow.
- **Hover / Focus:** Deep Leaderboard Forest with a small shadow increase; 3px Focus Green outline; active state shifts 1px and scales to 0.99.
- **Ghost / Danger:** White with a quiet border; ghost hovers to Practice Green Wash, while danger uses Negative text and becomes solid Negative on hover.

### Chips

- **Style:** Pill silhouette, 44px target for interactive filters, white or quiet neutral at rest.
- **State:** Selected chips invert to Tournament Forest and white; noninteractive facts stay muted and lightly bordered.

### Cards / Containers

- **Corner Style:** 14px for compact data and 18px for primary work surfaces.
- **Background:** Card White or near-white `#fbfbfa`; forest is reserved for verdict and course-context cards.
- **Shadow Strategy:** Surface Low at rest, Surface Raised only when the card is interactive.
- **Border:** One-pixel Quiet Line; selected cards use a restrained green border and pale green fill.
- **Internal Padding:** 14–16px for rows and data cards; responsive 20–30px for panels.

### Inputs / Fields

- **Style:** 48px minimum-height white field, Strong Quiet Line stroke, 10px radius, 15px/600 Archivo.
- **Focus:** Focus Green border plus a 4px translucent ring; `:focus-visible` receives the global 3px outline.
- **Error / Disabled:** Errors use Negative Wash and a muted red border; disabled controls use zinc fill and reduced contrast.

### Navigation

The editorial header is a translucent warm-canvas layer with blur and a quiet bottom line. Desktop links are compact 11px labels in pill hover fields; mobile links become stacked 44px targets beneath a 64px header. The round 46px burger is a tactile bordered control with low elevation.

### Tendency Choice

Hole steps are 44px square controls. Answer options are 54px tactile rectangles with a 12px radius; hover introduces a pale green field and selected state becomes solid Tournament Forest. Preserve the immediate press response and clear `aria-pressed` state.

### Locker Drawer

The Locker floats 10px from the viewport edge at up to 430px wide, with a 20px radius, frosted white header, warm canvas body, and strong modal shadow. Its launcher is a 50px frosted pill. On phones below 420px the drawer becomes full-screen and square to the viewport.

## Do's and Don'ts

### Do:

- **Do** make the next action and current selection obvious with Tournament Forest.
- **Do** keep one-pixel lines quiet and let spacing carry most of the hierarchy.
- **Do** preserve 44–54px touch targets, visible focus, safe-area spacing, and reduced-motion behavior.
- **Do** use status washes as precise analytical feedback and pair color with text.
- **Do** keep factual measurements tabular and compact with IBM Plex Mono.

### Don't:

- **Don't** revive heavy black borders, raw brutalist boxes, or high-contrast divider grids.
- **Don't** use green as ambient decoration across every card; its rarity gives it authority.
- **Don't** add decorative gradients, glass effects on ordinary content cards, or oversized rounded containers.
- **Don't** animate data for spectacle; movement should confirm ranking, press, selection, or overlay state.
- **Don't** let the visual polish soften GolfRaw's blunt editorial copy.
