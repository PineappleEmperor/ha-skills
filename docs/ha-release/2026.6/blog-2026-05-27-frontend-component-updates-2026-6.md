# Frontend component updates in 2026.6

Fetched from https://developers.home-assistant.io/blog/2026/05/27/frontend-component-updates-2026.6
Copyright (c) Home Assistant contributors. The developer documentation repository publishes no licence; this copy is kept for reference and attribution only.
Modified: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. It keeps the article body and loses everything the markup carried — navigation and chrome, link targets, image alt text, table and list structure, and code formatting. No wording has been changed, added or reordered.

Frontend component updates in 2026.6

May 27, 2026 · 2 min read

Wendelin Peleska

Component updates​

ha-radio updates​

ha-radio was removed from our codebase, we use the webawesome based ha-radio-group with ha-radio-option now. No need for a ha-formfield around a ha-radio anymore and you can use the new CSS properties to customize the radio group and options.

New component specific tokens:

--ha-radio-group-required-marker

--ha-radio-group-required-marker-offset

--ha-radio-option-active-color

--ha-radio-option-heigh

--ha-radio-option-toggle-size

--ha-radio-option-border-width

--ha-radio-option-border-color

--ha-radio-option-border-color-hover

--ha-radio-option-background-color

--ha-radio-option-background-color-hover

--ha-radio-option-checked-background-color

--ha-radio-option-checked-icon-color

--ha-radio-option-checked-icon-scale

--ha-radio-option-control-margin

ha-drawer updates​

ha-drawer was updated to use the webawesome drawer component. The API is mostly the same it just uses now --ha-sidebar-width instead of --mdc-drawer-width

top bar​

ha-top-app-bar was removed entirely.

ha-top-app-bar-fixed was migrated from MWC to plain Lit.

ha-two-pane-top-app-bar-fixed was rewritten to extend the new implementation instead of Material base code.

ha-header-bar was rewritten from a Material top-app-bar styled wrapper to a native Lit component.

The --ha-top-app-bar-width token replaces --mdc-top-app-bar-width.

New decorators​

@consumeLocalize​

Following up on the context entry decorators introduced last release, we added a shortcut for the most common single-field read off internationalizationContext: the localize function.

Before:

@state()

@consume({ context: internationalizationContext, subscribe: true })

@transform<HomeAssistantInternationalization, LocalizeFunc>({

transformer: ({ localize }) => localize,

})

private _localize!: LocalizeFunc;

After:

@state()

@consumeLocalize()

private _localize!: LocalizeFunc;

Use @consumeLocalize() whenever a component only needs the localize function. For other single-field reads off internationalizationContext (e.g. locale, language), keep using @consume + @transform.
