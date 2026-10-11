---
name: Clo
description: O mês como uma folha de folhinha de parede, em papel branco, tinta preta e o vermelho do limite, com a calopsita Clo de marca.
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
  paper-dark: "#131312"
  newsprint-dark: "#1f1f1d"
  newsprint-deep-dark: "#2a2a27"
  ink-dark: "#f3f2ed"
  ink-soft-dark: "#bebcb4"
  ink-faint-dark: "#97958d"
  rule-dark: "#2c2c29"
  rule-strong-dark: "#45443f"
  folhinha-red-dark: "#ff6b6f"
  person-1-blue-dark: "#3987e5"
  person-2-orange-dark: "#d95926"
  income-green-dark: "#57c27a"
  notice-yellow-dark: "#3a2f12"
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
  wordmark:
    fontFamily: "Folha, Arial Narrow, Roboto Condensed, sans-serif"
    fontSize: "26px"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "0.01em"
  day-number:
    fontFamily: "Folha, Arial Narrow, Roboto Condensed, sans-serif"
    fontSize: "28px"
    fontWeight: 800
    lineHeight: 0.9
  lead:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.5
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
  caption:
    fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
    fontSize: "11px"
    fontWeight: 650
    letterSpacing: "0.01em"
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
  theme-toggle:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink-soft}"
    rounded: "{rounded.sm}"
    size: "36px"
  theme-toggle-hover:
    textColor: "{colors.ink}"
  appearance-option:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "9px 16px"
    height: "44px"
  appearance-option-selected:
    backgroundColor: "{colors.newsprint}"
    textColor: "{colors.ink}"
  toast:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    rounded: "{rounded.none}"
    padding: "11px 14px"
  clo-mark:
    typography: "{typography.wordmark}"
    size: "32px"
  clo-perch:
    width: "52px"
    height: "58px"
---

# Design System: Clo

## Overview

**Creative North Star: "A Folhinha de Parede"**

The app is the Brazilian tear-off wall calendar hung by the kitchen door: a sheet of cold white paper, black ink, and the red the calendar reserves for days that matter. The month is the sheet. Its name is printed huge in an extra-condensed face, the weekdays run across in a solid ink band, and each day carries the money that left on it. You read the month at a glance, then tap a day to see what went out.

Density is that of a printed calendar or a newspaper page: many numbers, tightly set, held apart by 1px rules rather than boxes. A second layer of grey "jornal" newsprint carries hover, filters, logs and quiet surfaces. Nothing floats at rest; corners are square; the only heavy marks are ink rules under section heads. The system explicitly refuses the dashboard of rounded, shadowed cards with loose numbers in equal blocks.

Two colors belong to people, not to the system: Person 1 blue and Person 2 orange. They appear only as small square markers, bar segments, and stacked columns, always with the person's name beside them.

The app is named Clo, after its mascot: Clo, the couple's cockatiel, drawn flat and front-facing in the colors of the real bird. Her head is the brand mark. Whole, she appears only at a few fixed moments and keeps her colors inside her drawing; the folhinha world around her does not change.

**Key Characteristics:**
- Cold white paper, black ink, newsprint grey second layer; light and dark themes with the same roles, automatic or chosen per device.
- Extra-condensed "Folha" numerals for the month, headline values, section titles and day numbers; system sans with tabular numerals for everything else.
- Square corners (2px max), 1px hairline rules, 2-3px ink rules for heads, no card shadows.
- Red is the limit color, never decoration.
- Single-stroke SVG icons at 1.75 stroke.
- Clo, a flat filled cockatiel illustration, is the brand mark and the only full-color drawing; her colors never enter the UI.

## Colors

A near-monochrome paper-and-ink palette with one alarm red and two person colors that carry names. Every role has a dark-theme twin (the `-dark` tokens) used under `prefers-color-scheme: dark` unless the device chose Claro, or whenever the device chose Escuro.

### Primary
- **Calendar Ink** (`ink`; dark `ink-dark`): text, the weekday band, the primary button, the toast, the 3px rule under the sheet head, the selected-tab underline, the today frame, budget ticks on bars, focus outlines and checkbox accent. Ink is the system's voice; there is no brand hue.

### Secondary
- **Folhinha Red** (`folhinha-red`; dark `folhinha-red-dark`): the over-limit color. Day numbers and amounts above the daily pace, a category over its budget (with the alert icon), an overdue bill, the part of the budget meter past today's pace. It also marks failures and destruction: sync error indicator, import log errors, the danger button, the delete "x" on hover.

### Tertiary
- **Person 1 Blue** (`person-1-blue`; dark `person-1-blue-dark`) and **Person 2 Orange** (`person-2-orange`; dark `person-2-orange-dark`): who paid. Square 10px markers, day-cell bar segments, category bar segments, stacked monthly columns, card-limit fill. Chosen to pass colorblind checks in both themes.
- **Income Green** (`income-green`; dark `income-green-dark`): money coming in (entries in Transações, "entrou" text).

### Neutral
- **Cold Paper** (`paper`; dark `paper-dark`): page background, inputs, secondary buttons, the theme toggle, mini-folha body. The browser `theme-color` follows the visible theme with these two values.
- **Jornal** (`newsprint`; dark `newsprint-dark`): hover fill, filter bar, import log rows, code blocks, category track, selected person chip and selected appearance option.
- **Jornal Deep** (`newsprint-deep`; dark `newsprint-deep-dark`): budget meter and card-limit track, selected day, button pressed.
- **Soft Ink** (`ink-soft`; dark `ink-soft-dark`): secondary text, inactive tabs, the theme toggle icon at rest, notes, sub-labels.
- **Faint Ink** (`ink-faint`; dark `ink-faint-dark`): the year in the sheet head, future day numbers, placeholders, struck-through excluded amounts, the budget-end tick.
- **Hairline** (`rule`; dark `rule-dark`): every 1px row and cell divider, and the border of the quiet top-bar controls (sync pill, theme toggle).
- **Strong Hairline** (`rule-strong`; dark `rule-strong-dark`): input and button borders, top-bar control borders on hover, dashed drop zone, link underline.
- **Notice Yellow** (`notice-yellow`; dark `notice-yellow-dark`): the background of an inline notice.

### Illustration only (Clo)
These live inside the three Clo SVG symbols and nowhere else. They are not UI tokens and stay the same in both themes.
- **Face and crest** (#f4d84f), **cheeks** (#e8873a), **beak and feet** (#f2bf72), **eyes** (#1b1b1d).
- **Body** (#6b6c6f), **belly** (#85868a), **wings** (#4a4b50), **wing bar** (#eef2f1).

### Named Rules
**The Red Means Limit Rule.** Red appears only where something passed a limit or failed: over pace, over budget, overdue, sync or import error, destructive action. Never as an accent, a heading, a link, or a brand mark. A screen within budget shows no red at all.

**The Name Beside the Color Rule.** Person blue and orange never stand alone: every marker, bar, or column has the person's name in a legend or label beside it.

**The Ink, Not Hue Rule.** Emphasis and selection are made in ink (weight, an ink rule, an inset ink frame), not with a new color.

**The Feathers Stay in the Drawing Rule.** Clo's yellow, orange and greys exist only inside her illustration. No text, fill, border, chart or state ever borrows them; the cockatiel yellow is not a brand hue.

## Typography

**Display Font:** Folha = Sofia Sans Extra Condensed 600/800 (SIL OFL 1.1), embedded as subset woff2 (with Arial Narrow, Roboto Condensed, sans-serif)
**Body Font:** system-ui stack (-apple-system, Segoe UI, Roboto, sans-serif)

**Character:** Wall-calendar numerals against plain newspaper body text. The condensed face does the shouting in uppercase and big figures; the system face does the reading, always with tabular numerals for money.

### Hierarchy
- **Display** (Folha 800, 88px desktop / 58px phone / 50px under 380px, line-height 0.8, uppercase): the sheet head only: month and year ("OUTUBRO 2026", year in faint ink) or the tab name.
- **Headline** (Folha 800, 68px / 52px phone, 0.9, lining figures): the main budget figure; bill value at 60px (52px phone), per-person totals at 40px (34px phone), empty-state titles at 40px.
- **Title** (Folha 800, 26px, 1.0, uppercase): block titles ("POR CATEGORIA"), with an optional 13px system-face note set beside them; sub-titles at 19px; card-owner names and the mini-folha day at 30px (23px in the small mini-folha).
- **Wordmark** (Folha 800, 26px, 1.0, 0.01em): the name "Clo" in the top bar, beside Clo's head, in its natural case.
- **Day number** (Folha 800, 28px / 22px phone, 0.9): calendar cell numbers; future days drop to 600 in faint ink; holiday short names in Folha 600 at 13px (11.5px phone).
- **Lead** (system 400, 16px, 1.5): the budget sentence under the headline figure and the tapped day's heading (at 650).
- **Body** (system 400, 15px, 1.5; strong at 650): text, list rows at 14px, category names; the drop-zone call at 17px; prose capped at 72ch.
- **Label** (system 400, 12-13px): notes, legends, table heads (12px 600), the sync pill (12px 500), day-cell amounts (12px tabular; 11px phone, 10px under 380px), column captions.
- **Caption** (system 650-700, 11px): mini-folha header strips (uppercase, 0.03em; 10px in the small mini-folha), the month under the mini-folha day, status tags; the phone tab-bar labels at 11.5px.

### Named Rules
**The Folha for Figures Rule.** The condensed face is for the month, headline amounts, block titles, day numbers, the mini-folha date and the "Clo" wordmark. Body copy, buttons and form labels stay in the system face.

**The Tabular Money Rule.** Every currency amount outside the Folha headlines uses tabular numerals and does not wrap.

## Layout

A single centered column (max 1180px, 32px side padding; 16px on phone) under a sticky top bar (56px; 52px on phone). The top bar carries, left to right, the Clo mark (head plus wordmark, 10px apart), the tabs, the sync pill when present, and the theme toggle at the far right. Each tab opens with the sheet head: the display title on the left, square month arrows on the right, closed by a 3px ink rule and 32px of space.

Resumo is a two-column grid (about 1.12fr / 1fr, 56px gutter): budget figure, meter and the month sheet on the left, categories, per-person and last-six-months on the right. Cartão and Importar use equal two columns at the same 56px gutter. Blocks are separated by 44px. Below 960px everything stacks to one column; on phone, Resumo's "maiores gastos" list moves to the end. When Clo stands on the budget meter, the meter takes 72px of top margin to hold her.

At 760px and below, the tabs become a fixed bottom bar of five equal cells (62px, icon over 11.5px label, safe-area aware), the selected tab marked by a 3px ink bar at its top edge. The calendar cells shrink to 58px and transaction rows reflow into a three-line grid (description and value, who, category and split). Configurar's appearance options become three equal columns.

Rhythm steps actually used: 4, 8, 12, 16, 24, 32, 44, 56px.

## Elevation & Depth

Flat. Depth is made with paper layers (paper, jornal, jornal deep) and ink rules, never with card shadows. The only shadow is a soft lift for floating, transient elements: the hover tooltip and the toast. Selection inside the sheet uses inset ink, not lift: today gets a 2px inset ink frame, the tapped day a 4px ink bar along its top over jornal deep. On the budget meter, Clo stands at layer 1 and the pace tick is layered above her feet at layer 2, so the tick is never hidden.

### Shadow Vocabulary
- **Loose sheet** (`box-shadow: 0 6px 24px rgba(21,21,20,.16)`; dark `rgba(0,0,0,.5)`): tooltip and toast only.

### Named Rules
**The Paper Doesn't Float Rule.** Content surfaces sit on the page with no shadow. A shadow means "this is transient and on top," and nothing else gets it.

## Shapes

Square paper. Corners are 0 on sheets, cells, tracks, tiles and the toast; 2px on interactive controls (buttons, inputs, chips, the sync pill, the theme toggle, appearance options); 1px on the person markers. Separation is by line weight: 1px hairlines between rows and cells, a 1px ink rule on top of lists, 2px ink rules under day groups, card heads and totals, 3px under the sheet head. Dashed borders mean "not settled yet": the 1px dashed "pendente" tag and the 2px dashed file drop zone.

The one rounded silhouette in the system is Clo herself: a round head, oval body and wings, a triangular beak. Her curves belong to the illustration and do not license rounded UI.

## Components

### Buttons
Plain printed controls, firm and quiet.
- **Shape:** nearly square (2px), 40px minimum height, 7px 14px padding, weight 550.
- **Primary:** ink fill with paper text; hover lightens to soft ink.
- **Secondary:** paper with a strong-hairline border; hover jornal fill with faint-ink border; pressed jornal deep.
- **Danger:** red text on paper, red border on hover.
- **Icon buttons:** month arrows are 44px squares (40px phone); the delete "x" is a 32px borderless target that turns red on hover.
- **Theme toggle:** a 36px square (44px on phone) at the right of the top bar, paper with a hairline border and a soft-ink icon; hover takes a strong-hairline border and ink. It shows the moon when the light theme is visible and the sun when the dark theme is visible, and flips the device to the other one.
- **Focus:** 2px ink outline, 2px offset. Disabled at 45% opacity.

### Chips (person choice, appearance)
- **Style:** 44px tall labels with a strong-hairline border, 2px corners, the person marker and name inside.
- **State:** checked gets an ink border plus 1px inset ink, jornal fill, weight 650.
- **Appearance row:** Configurar → Aparência reuses the same chip as a radio group: Automático, Claro, Escuro, 9px 16px padding (three equal columns on phone), with a note that the choice applies to this device only.

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

### Toast
An ink strip with paper text (11px 14px padding, 14px text, square), centered 24px above the bottom, lifted by the loose-sheet shadow. Clo's head (22px) leads every message.

### The Month Sheet (signature)
A seven-column calendar: an ink weekday band (D S T Q Q S S in Folha 800, paper text), then hairline cells (74px; 58px phone) with the day number top-left, the day's spend at the bottom in 12px tabular, and a 3px bar split by who paid. Future days are faint and inert; days over the daily pace print number and amount in red; national holidays print their short name in the cell. Tapping a day lists its transactions below under a 2px ink rule, with a 220ms rise.

### Mini-folha (signature)
A small tear-off date tile: 1px ink border, an ink header strip with the 11px uppercase label (month or "FECHA"/"VENCE"), a Folha 800 day number, and the month underneath. 62px for Cartão closing/due dates, 44px as the date header of each Transações day group.

### Budget Meter
A 12px jornal-deep track: ink fill up to today's pace, red fill for the portion past it, a 2px ink pace tick haloed in paper and a faint-ink budget-end tick. Clo stands on the track at the point spending reached (clamped to 5-95% of its width): calm within the pace, alert once past it. Category rows reuse the meter at 8px on jornal with person-colored segments and an ink budget tick, without Clo.

### Clo (signature)
The mascot, a flat, front-facing cockatiel drawn as filled SVG shapes in the illustration-only colors. Three symbols, one sprite:
- **Head** (`clo-cabeca`, 64 grid): the brand mark at 32px beside the wordmark, the favicon, the 180px home-screen PNG (white ground), and the 22px toast lead.
- **Calm** (`clo-inteira`, 64x72 grid): small crest, folded wings, feet. On the budget meter within pace (52x58px) and in the empty states: the empty Resumo at 120x135px beside the message (88x99px stacked above it on phone), the empty Transações list at 52x58px beside its line.
- **Alert** (`clo-alerta`, 64x72 grid): crest fanned high, wings lifted. Only on the budget meter once spending passes the pace; the red fill and the "acima" words still carry the meaning, Clo only echoes it. A tooltip names her state.

She appears in these placements and no others. She is decorative (`aria-hidden`); every state she shows is also said in words.

### Icons
Single-stroke SVG sprite on a 24px grid, stroke 1.75, round caps and joins, `currentColor`; 18px default, 15px inline, 22px in the phone tab bar. The theme toggle uses the sun and moon from the same sprite. Clo is an illustration, not an icon, and is the only filled drawing.

## Do's and Don'ts

### Do:
- **Do** open every tab with the sheet head: Folha 800 uppercase title, closed by a 3px ink rule.
- **Do** separate rows and cells with 1px hairlines and mark heads and totals with 2px ink rules.
- **Do** reserve red for over-limit, overdue, error and destructive states, and pair it with the alert icon or explicit words ("acima", "venceu").
- **Do** set every money amount in tabular numerals; reserve Folha for headline figures and day numbers.
- **Do** put the person's name beside every blue or orange mark.
- **Do** use jornal for hover and quiet surfaces, and inset ink for selection.
- **Do** keep corners at 0 for surfaces and 2px for controls.
- **Do** use Clo's head as the brand mark (top bar, favicon, home-screen icon, toast) and the whole Clo only on the budget meter and in empty states.
- **Do** keep light and dark as the same roles, applied before first paint from the device's saved choice, with `theme-color` following the visible theme.

### Don't:
- **Don't** build rounded, shadowed dashboard cards or equal blocks of loose numbers.
- **Don't** use red as an accent, heading color, link color or decoration.
- **Don't** add shadows to anything that sits on the page; the soft lift is for tooltip and toast only.
- **Don't** introduce a brand hue; emphasis is ink.
- **Don't** let Clo's colors leave her drawing, and don't add new Clo poses or placements beyond the three symbols and the placements above.
- **Don't** make Clo the only carrier of a state; the numbers and words lead, she follows.
- **Don't** use cream or warm paper; the page is cold white.
- **Don't** use emoji or icon fonts; icons are the single-stroke SVG sprite.
