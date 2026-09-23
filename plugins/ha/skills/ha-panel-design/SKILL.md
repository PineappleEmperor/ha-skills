---
name: ha-panel-design
description: Use when changing how a Home Assistant custom panel looks — a Lit/TS panel web component, its built bundle, or any CSS/markup affecting sizing, typography, colour, spacing, or layout. Reach for it on symptoms too: a panel that looks foreign next to HA's own pages, text that does not scale, hardcoded hex colours that break in dark mode, or tap targets too small on a tablet. NOT for integration backend Python, Lovelace cards, or YAML dashboards. Invoke before changing panel CSS/markup; re-invoke after /compact.
---

# HA Custom Panel Design

**Every size, colour and space comes from HA's theme properties or the Material 3 scale,
never from a value chosen by eye.**

## Fetch before deciding sizes or tokens

Don't guess one from memory:

- Material 3 type scale: https://m3.material.io/styles/typography/type-scale-tokens
- Material 3 states/touch targets: https://m3.material.io/foundations/interaction/states/overview
- HA theme CSS custom properties, as the frontend defines them: https://github.com/home-assistant/frontend/tree/dev/src/resources/theme — `color/color.globals.ts` holds the colour variables (`--primary-text-color`, `--primary-color`, `--divider-color`, …), `typography.globals.ts` the type ones
- The variables a user's theme may override: https://www.home-assistant.io/integrations/frontend/#supported-theme-variables

When each source is due a re-check is the panel-design row of
`ha-integration/reference/freshness.md`.

---

## The core rule: tokens over literals

Take every colour from HA's theme custom properties, so the panel follows the user's theme
and its dark mode, and every `font-size` from the Material 3 type scale.

### HA theme custom properties to use (with sane fallbacks)

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

---

## Material 3 type scale (use these, pick by role)

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

---

## Disclosure arrows / expand indicators

- Use a **24px icon**, not a 12px text glyph (`▸`). In HA, prefer `<ha-icon icon="mdi:chevron-right">`
  (it inherits `--mdc-icon-size`, default 24px) or an inline 24px SVG. A text caret can't hit
  24px crisply and ignores theme icon sizing.
- Rotate 90° on expand with a `transform .15s` transition; colour `--secondary-text-color`.
- The whole header row is the click target (not just the arrow).

```css
.chev { --mdc-icon-size: 24px; color: var(--secondary-text-color); transition: transform .15s; }
.chev.open { transform: rotate(90deg); }
```

---

## Touch targets & icon buttons

- Minimum interactive target **48×48** (M3). Visual icon can be smaller (24), but padding makes
  the hit area 48. Icon buttons: 40 visual / 48 hit min.
- Thumbnails for pixel art: scale up with `image-rendering: pixelated` — an 8×8 icon at 64×64 is
  a clean 8× and stays crisp. Match related thumbnail heights so a grid aligns.

---

## Lists & sorting

| Rule | Value |
|---|---|
| the sort key | an intrinsic property — size, type, name — never backend insertion order |
| the order of keys | kind first where kinds exist, then a numeric dimension, then name |
| a sort a reader would not guess | stated in a hint beside the list |

---

## Panels built from a source bundle

The full contract for shipping a panel from an integration is
`ha-integration/reference/panels.md`. What follows is only what a design change must not
break.

- One Lit/TS source file builds to a committed bundle the integration serves; rebuild and
  commit it in the same PR as the source change. What CI does about a stale one is
  ha-panel-ci's README. The built file is display-only — never hand-edit it.
- Existing class names (section title, disclosure arrow, thumbnail) get retuned against the
  scale above, not nudged a pixel at a time.
- Render logic stays in the Python backend; the panel stays presentation.
