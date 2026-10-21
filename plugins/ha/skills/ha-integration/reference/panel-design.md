# How a custom panel looks

Read this when changing a panel's CSS or markup — sizing, typography, colour, spacing or layout.

**Every colour, size, space and duration is a Home Assistant theme variable or `--ha-` token,
never a value chosen by eye; an `--ha-` token carries its listed value as a fallback.**

## Contents

1. Styling a panel
2. Step 1: Take every colour from a theme variable
3. Step 2: Take type, spacing and radius from the `--ha-` tokens
4. Step 3: Size targets, icons and thumbnails
5. Step 4: Time motion with the duration tokens
6. Step 5: Sort a list by an intrinsic property
7. Step 6: Keep the change to presentation
8. Cases
9. Disclosure arrows and expand indicators — Step 3
10. Pixel-art thumbnails — Step 3

## Styling a panel

### Step 1: Take every colour from a theme variable

So the panel follows the user's theme and its dark mode:

```css
color: var(--primary-text-color, #141414);
color: var(--secondary-text-color, #5e5e5e);      /* captions, hints, inactive */
background: var(--card-background-color, #fff);
background: var(--primary-background-color);
border-color: var(--divider-color);
background: var(--primary-color);                 /* HA primary */
color: var(--accent-color);                       /* HA accent */
```

| Rule | Value |
|---|---|
| where each row was read | the theming page, the *Color* and *Accessibility* foundation pages, and *Supported theme variables* on the `frontend` integration page — each in the Panel design row of `SKILL.md` |
| text, background, divider, primary and accent | the theme variables above, which user themes set; the theming page's own component uses `--primary-text-color` and `--card-background-color` |
| a status colour — a danger, warning or success fill or border — and the focus ring | the semantic `--ha-color-*` token for that purpose; text on a quiet or normal fill takes the matching `--ha-color-on-*` token |
| a colour pair outside the token system | its contrast checked in the light and the dark theme: 4.5:1 for text, 3:1 for a control's edge or an icon |
| a variable a user's theme is supported to override | `primary-color`, `accent-color` and the `state-*` colours; any other may change between releases |

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| a palette token, `--ha-color-primary-40` say | the semantic token for the purpose | a palette token names a shade, not a purpose, so dark mode cannot retarget it | https://contributors.home-assistant.io/design/foundations/color/index.md |
| a colour with no variable | the theme variable | a bare value ignores the user's theme and dark mode | https://contributors.home-assistant.io/frontend/architecture/theming/index.md |

Define a small `:host` block mapping panel-local names (`--<domain>-primary`,
`--<domain>-outline`) to these once, then reference those — one place to retune.

### Step 2: Take type, spacing and radius from the `--ha-` tokens

| Rule | Value |
|---|---|
| where each row was read | the *Typography* and *Spacing* foundation pages, in the Panel design row of `SKILL.md`; the body size, `typography.globals.ts` in the frontend, https://raw.githubusercontent.com/home-assistant/frontend/dev/src/resources/theme/typography.globals.ts |
| font size | a `--ha-font-size-*` token, `xs` to `5xl`; the scale is adjusted as a whole, so a pixel size falls out of step |
| body text | `--ha-font-size-m`, the size the frontend sets on `html` |
| font weight | `--ha-font-weight-normal` for body text, `-medium` for actions such as button labels, `-bold` for headings |
| line height | `--ha-line-height-condensed` for headings and single lines, `-normal` for running text |
| padding, margin and gap | a `--ha-space-*` token, `1` to `20` in steps of 4px: the small steps inside a component, the larger between components |
| corner radius | a `--ha-border-radius-*` token: the larger ones for cards and dialogs, `pill` for buttons and chips |
| the fallback | each `--ha-` token's `var()` carries the value its foundation page lists — `var(--ha-space-4, 16px)` — since an older frontend lacks the token |
| a section header, including a collapsible group's | `--ha-font-size-xl` or larger, at the heading weight — this skill's choice, since the Typography page gives sizes no roles |

| anti-pattern | use instead | why (one clause) | reference |
|---|---|---|---|
| a pixel size, or a Material 3 size, typed into the CSS | the `--ha-` token, with its listed value as the fallback | the scale is adjusted as a whole, and a typed size falls out of step with it | https://contributors.home-assistant.io/design/foundations/typography/index.md |

### Step 3: Size targets, icons and thumbnails

| Rule | Value |
|---|---|
| where each row was read | *Target size*, *Keyboard*, *Labels and accessible names* and *Focus* on the *Accessibility* foundation page, in the Panel design row of `SKILL.md` |
| an icon button | `ha-icon-button`, 48×48 by default, with a `label`, which is its only accessible name and its tooltip |
| a button | 40px high by default |
| any pointer target | 24×24 at the least — the floor, not the goal |
| a control of your own | a native element or an `ha-*` component; a `<div>` with a `click` listener cannot be reached by keyboard |
| a focus ring | on `:focus-visible`, and never removed without a visible one in its place |

### Step 4: Time motion with the duration tokens

| Rule | Value |
|---|---|
| where each row was read | the *Motion* foundation page, in the Panel design row of `SKILL.md` |
| a transition | `--ha-animation-duration-fast`, `-normal` or `-slow`, with its milliseconds as the fallback; reduced motion sets every token to 1ms, so the transition follows it unaided — where the frontend has the tokens, since the fallback ignores reduced motion |
| an animation the tokens do not time, a loop say | its own `@media (prefers-reduced-motion: reduce)` block |

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
  tokens in Step 2, not nudged a pixel at a time.
- Render logic stays in the Python backend; the panel stays presentation.

## Cases

### Disclosure arrows and expand indicators — Step 3

- Use a **24px icon**, not a 12px text glyph (`▸`).
- In HA, prefer `<ha-icon icon="mdi:chevron-right">` (it inherits `--mdc-icon-size`, default
  24px) or an inline 24px SVG.
- A text caret can't hit 24px crisply and ignores theme icon sizing.
- Rotate 90° on expand, timed with `--ha-animation-duration-fast` (Step 4); colour `--secondary-text-color`.
- The whole header row is the click target (not just the arrow).

```css
.chev { --mdc-icon-size: 24px; color: var(--secondary-text-color); transition: transform var(--ha-animation-duration-fast, 150ms); }
.chev.open { transform: rotate(90deg); }
```

### Pixel-art thumbnails — Step 3

- Scale up with `image-rendering: pixelated` — an 8×8 icon at 64×64 is a clean 8× and
  stays crisp.
- Match related thumbnail heights so a grid aligns.
