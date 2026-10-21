# Frontend component updates in 2026.8

Fetched from https://contributors.home-assistant.io/blog/2026/07/31/frontend-component-updates-2026.8/
Copyright (c) Home Assistant contributors. home-assistant/contributors.home-assistant.io publishes no licence; this copy is kept for reference and attribution only.
Modified: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. It keeps the article body and loses everything the markup carried — navigation and chrome, link targets, image alt text, table and list structure, and code formatting. No wording has been changed, added or reordered.

Blog

Frontend component updates in 2026.8

Jan-Philipp BeneckeJuly 31, 2026·3 min read

Frontend

Component updates

ha-split-panel

We added ha-split-panel, a Home Assistant wrapper around the Web Awesome split panel component.

Use it when a Home Assistant page, dialog, or tool needs a resizable two-pane layout. Custom card authors can use Home Assistant frontend components, but internal Home Assistant UI APIs may change.

HTML

<ha-split-panel position="40" snap="50%">
<div slot="start">Editor</div>
<div slot="end">Preview</div>
</ha-split-panel>

New component-specific tokens:

CSS

--ha-split-panel-divider-width
--ha-split-panel-divider-hit-area
--ha-split-panel-min
--ha-split-panel-max
--ha-split-panel-grip-display

ha-tile-info updates

ha-tile-info gained more layout controls for custom cards and tile-like surfaces.

New component-specific tokens:

CSS

--ha-tile-info-gap
--ha-tile-info-min-height
--ha-tile-info-primary-min-height
--ha-tile-info-primary-line-clamp

Use --ha-tile-info-primary-line-clamp when the primary text should wrap to more than one line, and use the min-height tokens to keep rows aligned when some tiles have secondary text and others do not.

Form and selector updates

Conditional ha-form fields

ha-form schemas now support conditional field visibility with visible.

TypeScript

[
{
name: "advanced",
selector: { boolean: {} },
},
{
name: "advanced_name",
visible: { field: "advanced", value: true },
selector: { text: {} },
},
]

Supported operators are:

TypeScript

"eq"
"not_eq"
"in"
"not_in"
"exists"
"not_exists"

You can also combine conditions with and, or, and not.

Hidden fields are not rendered and are skipped during validation, so use visible instead of custom frontend-only hiding logic when a form field depends on another value.

Selector additions

The text selector now supports HTML pattern validation:

TypeScript

{
text: {
pattern: "[a-z0-9_]+",
validation_message: "Use lowercase letters, numbers, and underscores",
},
}

This works for both single-value and multiple-value text selectors.

Entity selectors can now filter by properties of the entity's device:

TypeScript

{
entity: {
filter: {
domain: "sensor",
device: {
manufacturer: "Home Assistant",
model: "Connect ZBT-1",
},
},
},
}

A new ui_clock_date_format selector was also added for the clock card date format editor.

Lovelace updates

state_color is moving to color

The entities and glance cards now support color as the replacement for state_color.

Before:

YAML

type: entities
state_color: true
entities:
- light.kitchen

After:

YAML

type: entities
color: state
entities:
- light.kitchen

Use color: state for the old state_color: true behavior, and color: none for state_color: false.

Custom panels and apps

Safe-area handling

Custom panels and add-on app iframes now get safe-area padding by default, so content stays clear of notches, status bars, and home indicators.

Custom panels that already handle safe areas themselves can opt out:

YAML

panel_custom:
- name: my-panel
module_url: /local/my-panel.js
handle_safe_area: true

For iframe-based custom panels, Home Assistant forwards the resolved safe-area values into the iframe document as CSS variables:

CSS

--safe-area-inset-top
--safe-area-inset-right
--safe-area-inset-bottom
--safe-area-inset-left

Add-on app iframes can also opt into managing the safe area themselves when subscribing to Home Assistant properties:

JavaScript

window.parent.postMessage(
{
type: "home-assistant/subscribe-properties",
handleSafeArea: true,
},
"*"
);

The properties message then includes safeAreaInsets.

Context and editor infrastructure

Global dirty state

DirtyStateProviderMixin now also publishes a global dirty state.

When any connected dirty-state provider has unsaved changes, window.isDirtyState is set and Home Assistant fires a dirty-state-changed event.

TypeScript

window.addEventListener("dirty-state-changed", (ev) => {
console.log(ev.detail.isDirty);
});

This is useful for shared infrastructure that needs to avoid disrupting active editors or dialogs with unsaved changes.
