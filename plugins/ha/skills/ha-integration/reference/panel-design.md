# How a custom panel looks

Read this when changing a panel's CSS or markup — sizing, typography, colour, spacing or
layout. How the panel is built and served is `reference/panels.md`.

**Every size, colour and space comes from HA's theme properties or the Material 3 scale,
never from a value chosen by eye.**

## Contents

1. Styling a panel
2. Step 1: Fetch before deciding sizes or tokens
3. Step 2: Take every colour from a theme property
4. Step 3: Take type and spacing from the scale
5. Step 4: Size targets, icons and thumbnails
6. Step 5: Sort a list by an intrinsic property
7. Step 6: Keep the change to presentation
8. Cases
9. Disclosure arrows and expand indicators — Step 4
10. Pixel-art thumbnails — Step 4

## Styling a panel

### Step 1: Fetch before deciding sizes or tokens

Don't guess one from memory. When each source is due a re-check is the panel design sources
row of `reference/freshness.md`.

- Material 3 type scale: https://m3.material.io/styles/typography/type-scale-tokens
- Material 3 states/touch targets: https://m3.material.io/foundations/interaction/states/overview
- HA theme CSS custom properties, as the frontend defines them: https://github.com/home-assistant/frontend/tree/dev/src/resources/theme — `color/color.globals.ts` holds the colour variables (`--primary-text-color`, `--primary-color`, `--divider-color`, …), `typography.globals.ts` the type ones
- The variables a user's theme may override: https://www.home-assistant.io/integrations/frontend/#supported-theme-variables

### Step 2: Take every colour from a theme property

So the panel follows the user's theme and its dark mode. With sane fallbacks:

```css
color: var(--primary-text-color, #1c1b1f);
color: var(--secondary-text-color, #49454f);      /* captions, hints, inactive */
background: var(--card-background-color, #fff);
background: var(--primary-background-color);
border-color: var(--divider-color);
accent:  var(--primary-color);                     /* HA accent */
border-radius: var(--ha-card-border-radius, 12px);
```

Define a small `:host` token block mapping panel-local names (`--<domain>-primary`,
`--<domain>-outline`) to HA vars once, then reference those — one place to retune.

### Step 3: Take type and spacing from the scale

Pick by role.

| Token | Value | Use |
|---|---|---|
| Headline small | 24 / 32 / 400 | Page/screen title |
| **Title large** | **22 / 28 / 400** | **Section headers** (the big collapsible groups) |
| Title medium | 16 / 24 / 500 | Sub-section / card title |
| Body large | 16 / 24 / 400 | Primary text, inputs |
| Body medium | 14 / 20 / 400 | Secondary text |
| Label large | 14 / 20 / 500 | Buttons |
| Label medium | 12 / 16 / 500 | Badges, chips |
| Label small | 11 / 16 / 500 | Dense captions only |

| Rule | Value |
|---|---|
| a section header, including a collapsible group's | title-large at 22, never 13–16px |
| line-height against stock M3 | tighten it, since HA renders denser |
| the header-to-body ratio | ≥ 1.4×, whatever the line-height |
| spacing | a consistent step — 4/8/12/16/20/24 |

### Step 4: Size targets, icons and thumbnails

- Minimum interactive target **48×48** (M3). The visual icon can be smaller (24), but
  padding makes the hit area 48.
- Icon buttons: 40 visual / 48 hit min.

### Step 5: Sort a list by an intrinsic property

| Rule | Value |
|---|---|
| the sort key | an intrinsic property — size, type, name — never backend insertion order |
| the order of keys | kind first where kinds exist, then a numeric dimension, then name |
| a sort a reader would not guess | stated in a hint beside the list |

### Step 6: Keep the change to presentation

One Lit/TS source file builds to a committed bundle the integration serves. When to rebuild
it, and what CI does about a stale one, is *Step 1: Build the bundle and commit it* in
`reference/panels.md`. What follows is only what a design change must not break.

- Existing class names (section title, disclosure arrow, thumbnail) get retuned against the
  scale in Step 3, not nudged a pixel at a time.
- Render logic stays in the Python backend; the panel stays presentation.

## Cases

### Disclosure arrows and expand indicators — Step 4

- Use a **24px icon**, not a 12px text glyph (`▸`).
- In HA, prefer `<ha-icon icon="mdi:chevron-right">` (it inherits `--mdc-icon-size`, default
  24px) or an inline 24px SVG.
- A text caret can't hit 24px crisply and ignores theme icon sizing.
- Rotate 90° on expand with a `transform .15s` transition; colour `--secondary-text-color`.
- The whole header row is the click target (not just the arrow).

```css
.chev { --mdc-icon-size: 24px; color: var(--secondary-text-color); transition: transform .15s; }
.chev.open { transform: rotate(90deg); }
```

### Pixel-art thumbnails — Step 4

- Scale up with `image-rendering: pixelated` — an 8×8 icon at 64×64 is a clean 8× and
  stays crisp.
- Match related thumbnail heights so a grid aligns.
