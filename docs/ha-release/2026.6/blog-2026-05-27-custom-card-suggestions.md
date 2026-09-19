# Custom card suggestions in the card picker

Fetched from https://developers.home-assistant.io/blog/2026/05/27/custom-card-suggestions
Copyright (c) Home Assistant contributors. The developer documentation repository publishes no licence; this copy is kept for reference and attribution only.
Modified only in format: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. The wording is the author's, unaltered.

Custom card suggestions in the card picker

May 27, 2026 · One min read

Paul Bottein

As of Home Assistant 2026.6, custom cards can show up as suggestions in the card picker. When a user selects an entity, custom cards that opt in are listed under a Community section, below the built-in suggestions.

To opt in, add a getEntitySuggestion function to your window.customCards entry. It receives the hass object and the selected entity id, and returns a suggestion (or null if the entity is not supported):

window.customCards.push({

type: "my-card",

name: "My Card",

getEntitySuggestion: (hass, entityId) => {

if (entityId.split(".")[0] !== "light") {

return null;

}

return {

config: { type: "custom:my-card", entity: entityId },

};

},

});

You can also return an array of suggestions to offer several variants, each with its own label.

Only suggest your card when it makes sense for the entity. Check the domain, device class, or supported features with the hass object, and return null otherwise. Suggesting your card for every entity makes the picker noisy.

See the custom card documentation for the full reference.
