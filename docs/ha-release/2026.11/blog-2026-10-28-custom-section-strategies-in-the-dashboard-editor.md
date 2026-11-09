# Custom section strategies in the dashboard editor

Fetched from https://contributors.home-assistant.io/blog/2026/10/28/custom-section-strategies-in-the-dashboard-editor/
Copyright (c) Home Assistant contributors. home-assistant/contributors.home-assistant.io publishes no licence; this copy is kept for reference and attribution only.
Modified: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. It keeps the article body and loses everything the markup carried — navigation and chrome, link targets, image alt text, table and list structure, and code formatting. No wording has been changed, added or reordered.

Blog

Custom section strategies in the dashboard editor

Paul BotteinOctober 28, 2026·1 min read

Frontend

As of Home Assistant 2026.11, custom section strategies can be registered, like custom dashboard strategies. Users then find them in the dashboard editor, and add them without writing any YAML.

A section strategy generates one section of a sections view from what is in the home, and keeps it up to date.

What users see

When users create a section in a sections view, Home Assistant asks if they want a manual section, an automatic section, or a section they copied. Automatic section lists the built-in section strategies, and the registered ones under Community sections. Each one shows a live preview. Picking one opens the section editor.

Register your section strategy

Push an entry to window.customStrategies, with strategyType: "section":

JavaScript

window.customStrategies = window.customStrategies || [];
window.customStrategies.push({
type: "my-domain",
strategyType: "section",
name: "My domain section",
description: "Shows all the entities of one domain.",
});

Show a preview

Add a static getStubConfig(hass) that returns the configuration your section starts with. Home Assistant uses it to render the preview, and as the configuration of the new section. Without it, the tile has no preview.

JavaScript

class MyDomainSectionStrategy extends HTMLElement {
static getStubConfig(hass) {
return { type: "custom:my-domain", domain: "light" };
}

static async generate(config, hass) {
// ...
}
}

customElements.define(
"ll-strategy-section-my-domain",
MyDomainSectionStrategy
);

Add an editor

Right after picking your section, users land in the section editor. Add a static getConfigElement() so they get a visual editor for your options. Without it, they only get the YAML editor.

Take a look at the updated custom strategies documentation for more details.
