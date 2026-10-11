---
name: Finanças do Casal
description: O mês como uma folha de folhinha de parede, em papel branco, tinta preta e o vermelho do limite.
colors:
  paper: "#ffffff"
  newsprint: "#f0efeb"
  newsprint-deep: "#e6e5e0"
  ink: "#151514"
  ink-soft: "#53524d"
  ink-faint: "#74726b"
  rule: "#e2e1dc"
  rule-strong: "#c4c2ba"
  folhinha-red: "#c4122f"
  person-1-blue: "#2a78d6"
  person-2-orange: "#eb6834"
  income-green: "#17733a"
  notice-yellow: "#fff2cc"
typography:
  display:
    fontFamily: "Folha, Arial Narrow, Roboto Condensed, sans-serif"
    fontSize: "88px"
    fontWeight: 800
    lineHeight: 0.8
    letterSpacing: "-0.005em"
  headline:
    fontFamily: "Folha, Arial Narrow, Roboto Condensed, sans-serif"
    fontSize: "68px"
    fontWeight: 800
    lineHeight: 0.9
    letterSpacing: "-0.005em"
    fontFeature: "lnum"
  title:
    fontFamily: "Folha, Arial Narrow, Roboto Condensed, sans-serif"
    fontSize: "26px"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "0.005em"
  day-number:
    fontFamily: "Folha, Arial Narrow, Roboto Condensed, sans-serif"
    fontSize: "28px"
    fontWeight: 800
    lineHeight: 0.9
  body:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.5
    fontFeature: "tnum"
  label:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.4
rounded:
  none: "0px"
  hair: "1px"
  sm: "2px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
  page: "32px"
  block: "44px"
  column: "56px"
components:
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    rounded: "{rounded.sm}"
    padding: "7px 14px"
    height: "40px"
  button-primary-hover:
    backgroundColor: "{colors.ink-soft}"
    textColor: "{colors.paper}"
  button-secondary:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "7px 14px"
    height: "40px"
  button-secondary-hover:
    backgroundColor: "{colors.newsprint}"
  button-danger:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.folhinha-red}"
    rounded: "{rounded.sm}"
    padding: "7px 14px"
    height: "40px"
  input-text:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "7px 10px"
    height: "40px"
  tab:
    textColor: "{colors.ink-soft}"
    typography: "{typography.body}"
    height: "56px"
    padding: "0 12px"
  tab-selected:
    textColor: "{colors.ink}"
  weekday-band:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
  day-cell:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.day-number}"
    rounded: "{rounded.none}"
    padding: "7px 7px 11px"
    height: "74px"
  day-cell-hover:
    backgroundColor: "{colors.newsprint}"
  day-cell-over-pace:
    textColor: "{colors.folhinha-red}"
  mini-folha:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    width: "62px"
  filter-bar:
    backgroundColor: "{colors.newsprint}"
    padding: "12px"
---

# Design System: Finanças do Casal

## Overview

**Creative North Star: "A Folhinha de Parede"**

The app is the Brazilian tear-off wall calendar hung by the kitchen door: a sheet of cold white paper, black ink, and the red the calendar reserves for days that matter. The month is the sheet. Its name is printed huge in an extra-condensed face, the weekdays run across in a solid ink band, and each day carries the money that left on it. You read the month at a glance, then tap a day to see what went out.

Density is that of a printed calendar or a newspaper page: many numbers, tightly set, held apart by 1px rules rather than boxes. A second layer of grey "jornal" newsprint carries hover, filters, logs and quiet surfaces. Nothing floats at rest; corners are square; the only heavy marks are ink rules under section heads. The system explicitly refuses the dashboard of rounded, shadowed cards with loose numbers in equal blocks.

Two colors belong to people, not to the system: Person 1 blue and Person 2 orange. They appear only as small square markers, bar segments, and stacked columns, always with the person's name beside them.

**Key Characteristics:**
- Cold white paper, black ink, newsprint grey second layer; light and dark themes with the same roles.
- Extra-condensed "Folha" numerals for the month, headline values, section titles and day numbers; system sans with tabular numerals for everything else.
- Square corners (2px max), 1px hairline rules, 2-3px ink rules for heads, no card shadows.
- Red is the limit color, never decoration.
- Single-stroke SVG icons at 1.75 stroke.

## Colors

A near-monochrome paper-and-ink palette with one alarm red and two person colors that carry names.

### Primary
- **Calendar Ink** (`ink`): text, the weekday band, the primary button, the 3px rule under the sheet head, the selected-tab underline, the today frame, budget ticks on bars, focus outlines and checkbox accent. Ink is the system's voice; there is no brand hue.

### Secondary
- **Folhinha Red** (`folhinha-red`): the over-limit color. Day numbers and amounts above the daily pace, a category over its budget (with the alert icon), an overdue bill, the part of the budget meter past today's pace. It also marks failures and destruction: sync error indicator, import log errors, the danger button, the delete "x" on hover. Dark theme: #ff6b6f.

### Tertiary
- **Person 1 Blue** (`person-1-blue`) and **Person 2 Orange** (`person-2-orange`): who paid. Square 10px markers, day-cell bar segments, category bar segments, stacked monthly columns, card-limit fill. Dark theme: #3987e5 and #d95926. Chosen to pass colorblind checks in both themes.
- **Income Green** (`income-green`): money coming in (entries in Transações, "entrou" text). Dark theme: #57c27a.

### Neutral
- **Cold Paper** (`paper`): page background, inputs, secondary buttons, mini-folha body. Dark: #131312.
- **Jornal** (`newsprint`): hover fill, filter bar, import log rows, code blocks, category track, selected person chip. Dark: #1f1f1d.
- **Jornal Deep** (`newsprint-deep`): budget meter and card-limit track, selected day, button pressed. Dark: #2a2a27.
- **Soft Ink** (`ink-soft`): secondary text, inactive tabs, notes, sub-labels. Dark: #bebcb4.
- **Faint Ink** (`ink-faint`): the year in the sheet head, future day numbers, placeholders, struck-through excluded amounts, the budget-end tick. Dark: #97958d.
- **Hairline** (`rule`): every 1px row and cell divider. Dark: #2c2c29.
- **Strong Hairline** (`rule-strong`): input and button borders, dashed drop zone, link underline. Dark: #45443f.
- **Notice Yellow** (`notice-yellow`): the background of an inline notice. Dark: #3a2f12.

### Named Rules
**The Red Means Limit Rule.** Red appears only where something passed a limit or failed: over pace, over budget, overdue, sync or import error, destructive action. Never as an accent, a heading, a link, or a brand mark. A screen within budget shows no red at all.

**The Name Beside the Color Rule.** Person blue and orange never stand alone: every marker, bar, or column has the person's name in a legend or label beside it.

**The Ink, Not Hue Rule.** Emphasis and selection are made in ink (weight, an ink rule, an inset ink frame), not with a new color.

## Typography

**Display Font:** Folha = Sofia Sans Extra Condensed 600/800 (SIL OFL 1.1), embedded as subset woff2 (with Arial Narrow, Roboto Condensed, sans-serif)
**Body Font:** system-ui stack (-apple-system, Segoe UI, Roboto, sans-serif)

**Character:** Wall-calendar numerals against plain newspaper body text. The condensed face does the shouting in uppercase and big figures; the system face does the reading, always with tabular numerals for money.

### Hierarchy
- **Display** (Folha 800, 88px desktop / 58px phone / 50px under 380px, line-height 0.8, uppercase): the sheet head only: month and year ("OUTUBRO 2026", year in faint ink) or the tab name.
- **Headline** (Folha 800, 68px / 52px phone, 0.9, lining figures): the main budget figure; bill value at 60px, per-person totals at 40px, empty-state titles at 40px.
- **Title** (Folha 800, 26px, 1.0, uppercase): block titles ("POR CATEGORIA"), with an optional 13px system-face note set beside them; sub-titles at 19px; card-owner names at 30px.
- **Day number** (Folha 800, 28px / 22px phone, 0.9): calendar cell numbers; future days drop to 600 in faint ink; holiday short names in Folha 600 at 13px.
- **Body** (system 400, 15px, 1.5; strong at 650): text, list rows at 14px, category names; prose capped at 72ch.
- **Label** (system 400, 12-13px): notes, legends, table heads (12px 600), day-cell amounts (12px tabular), column captions.

### Named Rules
**The Folha for Figures Rule.** The condensed face is for the month, headline amounts, block titles, day numbers and the mini-folha date. Body copy, buttons and form labels stay in the system face.

**The Tabular Money Rule.** Every currency amount outside the Folha headlines uses tabular numerals and does not wrap.

## Layout

A single centered column (max 1180px, 32px side padding; 16px on phone) under a sticky top bar (56px; 48px on phone). Each tab opens with the sheet head: the display title on the left, square month arrows on the right, closed by a 3px ink rule and 32px of space.

Resumo is a two-column grid (about 1.12fr / 1fr, 56px gutter): budget figure, meter and the month sheet on the left, categories, per-person and last-six-months on the right. Cartão and Importar use equal two columns at the same 56px gutter. Blocks are separated by 44px. Below 960px everything stacks to one column; on phone, Resumo's "maiores gastos" list moves to the end.

At 760px and below, the tabs become a fixed bottom bar of five equal cells (62px, icon over 11.5px label, safe-area aware), the selected tab marked by a 3px ink bar at its top edge. The calendar cells shrink to 58px and transaction rows reflow into a three-line grid (description and value, who, category and split).

Rhythm steps actually used: 4, 8, 12, 16, 24, 32, 44, 56px.

## Elevation & Depth

Flat. Depth is made with paper layers (paper, jornal, jornal deep) and ink rules, never with card shadows. The only shadow is a soft lift for floating, transient elements: the hover tooltip and the toast. Selection inside the sheet uses inset ink, not lift: today gets a 2px inset ink frame, the tapped day a 4px ink bar along its top over jornal deep.

### Shadow Vocabulary
- **Loose sheet** (`box-shadow: 0 6px 24px rgba(21,21,20,.16)`; dark `rgba(0,0,0,.5)`): tooltip and toast only.

### Named Rules
**The Paper Doesn't Float Rule.** Content surfaces sit on the page with no shadow. A shadow means "this is transient and on top," and nothing else gets it.

## Shapes

Square paper. Corners are 0 on sheets, cells, tracks and tiles; 2px on interactive controls (buttons, inputs, chips, the sync pill); 1px on the person markers. Separation is by line weight: 1px hairlines between rows and cells, a 1px ink rule on top of lists, 2px ink rules under day groups, card heads and totals, 3px under the sheet head. Dashed borders mean "not settled yet": the 1px dashed "pendente" tag and the 2px dashed file drop zone.

## Components

### Buttons
Plain printed controls, firm and quiet.
- **Shape:** nearly square (2px), 40px minimum height, 7px 14px padding, weight 550.
- **Primary:** ink fill with paper text; hover lightens to soft ink.
- **Secondary:** paper with a strong-hairline border; hover jornal fill with faint-ink border; pressed jornal deep.
- **Danger:** red text on paper, red border on hover.
- **Icon buttons:** month arrows are 44px squares (40px phone); the delete "x" is a 32px borderless target that turns red on hover.
- **Focus:** 2px ink outline, 2px offset. Disabled at 45% opacity.

### Chips (person choice)
- **Style:** 44px tall labels with a strong-hairline border, 2px corners, the person marker and name inside.
- **State:** checked gets an ink border plus 1px inset ink, jornal fill, weight 650.

### Cards / Containers
- **Corner Style:** square.
- **Background:** paper; quiet zones (filters, logs) in jornal.
- **Shadow Strategy:** none (see Elevation).
- **Border:** containers are mostly implied by rules; the person settings panel uses a hairline box with a 2px ink top.
- **Internal Padding:** 12-16px.

### Inputs / Fields
- **Style:** paper fill, strong-hairline border, 2px corners, 40px min height (36px inside transaction rows).
- **Focus:** ink border with a 2px ink outline at 0 offset. Checkboxes and radios take ink as accent.

### Navigation
- **Desktop:** text tabs with an icon in the top bar, soft ink at rest, ink and 650 when selected, a 3px ink underline sitting on the bar's bottom hairline.
- **Phone:** fixed bottom bar, see Layout.

### The Month Sheet (signature)
A seven-column calendar: an ink weekday band (D S T Q Q S S in Folha 800, paper text), then hairline cells (74px; 58px phone) with the day number top-left, the day's spend at the bottom in 12px tabular, and a 3px bar split by who paid. Future days are faint and inert; days over the daily pace print number and amount in red; national holidays print their short name in the cell. Tapping a day lists its transactions below under a 2px ink rule, with a 220ms rise.

### Mini-folha (signature)
A small tear-off date tile: 1px ink border, an ink header strip with the 11px uppercase label (month or "FECHA"/"VENCE"), a Folha 800 day number, and the month underneath. 62px for Cartão closing/due dates, 44px as the date header of each Transações day group.

### Budget Meter
A 12px jornal-deep track: ink fill up to today's pace, red fill for the portion past it, a 2px ink pace tick haloed in paper and a faint-ink budget-end tick. Category rows reuse it at 8px on jornal with person-colored segments and an ink budget tick.

### Icons
Single-stroke SVG sprite on a 24px grid, stroke 1.75, round caps and joins, `currentColor`; 18px default, 15px inline, 22px in the phone tab bar. The brand seal is a small filled ink calendar.

## Do's and Don'ts

### Do:
- **Do** open every tab with the sheet head: Folha 800 uppercase title, closed by a 3px ink rule.
- **Do** separate rows and cells with 1px hairlines and mark heads and totals with 2px ink rules.
- **Do** reserve red for over-limit, overdue, error and destructive states, and pair it with the alert icon or explicit words ("acima", "venceu").
- **Do** set every money amount in tabular numerals; reserve Folha for headline figures and day numbers.
- **Do** put the person's name beside every blue or orange mark.
- **Do** use jornal for hover and quiet surfaces, and inset ink for selection.
- **Do** keep corners at 0 for surfaces and 2px for controls.

### Don't:
- **Don't** build rounded, shadowed dashboard cards or equal blocks of loose numbers.
- **Don't** use red as an accent, heading color, link color or decoration.
- **Don't** add shadows to anything that sits on the page; the soft lift is for tooltip and toast only.
- **Don't** introduce a brand hue; emphasis is ink.
- **Don't** use cream or warm paper; the page is cold white.
- **Don't** use emoji or icon fonts; icons are the single-stroke SVG sprite.
