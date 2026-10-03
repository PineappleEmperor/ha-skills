# Frontend component updates in 2026.7

Fetched from https://developers.home-assistant.io/blog/2026/06/23/frontend-component-updates-2026.7
Copyright (c) Home Assistant contributors. The developer documentation repository publishes no licence; this copy is kept for reference and attribution only.
Modified: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. It keeps the article body and loses everything the markup carried — navigation and chrome, link targets, image alt text, table and list structure, and code formatting. No wording has been changed, added or reordered.

Frontend component updates in 2026.7

June 23, 2026 · 3 min read

Jan-Philipp Benecke

Component updates​

Component sizes use Web Awesome names​

ha-button, ha-button-toggle-group, and ha-slider now use the short Web Awesome size names.

For ha-button, use:

<ha-button size="s">Save</ha-button>

Supported values are xs, s, m, l, and xl.

For ha-button-toggle-group, use s or m:

<ha-button-toggle-group size="s" .buttons=${buttons}></ha-button-toggle-group>

ha-slider uses s or m.

If your custom card or editor still uses small, medium, or large on these components, migrate them to short values like s, m, or l.

Virtualized lists​

We added two list components for large data sets:

ha-list-virtualized

ha-list-selectable-virtualized

Use these when a picker or dialog can render enough rows to affect scrolling or initial render time. The virtualized list renders only the visible rows while keeping the roving-tabindex keyboard navigation from ha-list-base.

Rows expose accessibility metadata with aria-setsize and aria-posinset, so assistive technologies still get the full list position even though only part of the list is in the DOM.

For selectable lists, render ha-list-item-option rows.

Context and editor infrastructure​

Dirty state tracking​

Dialogs and editors now have shared dirty-state infrastructure:

DirtyStateProviderMixin

dirtyStateContext

isDirtyState

isEffectiveDirtyState

Use DirtyStateProviderMixin for new dialogs or editors that need to block scrim close, enable Save only after edits, or coordinate dirty state with child components.

class MyDialog extends DirtyStateProviderMixin<MyState>()(LitElement) {

public openDialog() {

this._initDirtyTracking({ type: "shallow" }, this._state);

}

private _stateChanged(state: MyState) {

this._updateDirtyState(state);

}

}

isDirtyState is the raw comparison and is usually right for enabling Save. isEffectiveDirtyState can ignore equivalent config output, for example when an editor normalizes an explicit default back to the same effective config.

Related context​

Pages and editors can now publish related context for nearby pickers:

relatedContext

fireRelatedContext

fireEntityRelatedContext

When a card editor, badge editor, automation trace page, or similar surface knows the current entity, device, or area, it can provide that context. Entity pickers and add-element searches can then prioritize related entities, devices, and areas.

fireEntityRelatedContext(this, "light.kitchen");

Clear the context with undefined when the editor no longer has a related item.

Narrow viewport context​

narrowViewportContext exposes whether the main Home Assistant viewport is in the narrow layout.

Components that only need narrow-layout state can consume this context instead of receiving narrow through several layers of properties.

@consume({ context: narrowViewportContext, subscribe: true })

private _narrow!: boolean;

Lovelace updates​

Strategy regeneration control​

Lovelace strategies can now avoid unnecessary regeneration.

Strategies may declare registryDependencies to use the default reference-change check for only the registries they depend on:

static registryDependencies = ["entities", "areas"] as const;

For custom logic, implement shouldRegenerate():

static shouldRegenerate(config, oldHomeAssistant, newHomeAssistant) {

return oldHomeAssistant.entities !== newHomeAssistant.entities;

}

If neither is provided, strategies keep the previous default behavior and regenerate on changes to entities, devices, areas, or floors.
