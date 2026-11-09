# Auth providers now opt in to multi-factor authentication

Fetched from https://contributors.home-assistant.io/blog/2026/10/19/auth-providers-opt-in-mfa/
Copyright (c) Home Assistant contributors. home-assistant/contributors.home-assistant.io publishes no licence; this copy is kept for reference and attribution only.
Modified: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. It keeps the article body and loses everything the markup carried — navigation and chrome, link targets, image alt text, table and list structure, and code formatting. No wording has been changed, added or reordered.

Blog

Auth providers now opt in to multi-factor authentication

Josef ZweckOctober 19, 2026·1 min read

Core and integrations

As of Home Assistant Core 2026.11, a login flow only asks for a second factor when it extends the new MfaLoginFlow. The auth manager no longer adds the MFA steps to every provider, and AuthProvider.support_mfa is removed.

What to do

Only relevant if your custom integration patches in its own auth provider.

Note

Custom auth providers are not supported.

If you change nothing, your provider silently stops asking for a second factor, even if it never overrode support_mfa.

To ask for an enabled second factor, extend MfaLoginFlow. After validating the first factor, return await self.async_finish(flow_result) instead of calling self.async_create_entry(data=flow_result) directly, which bypasses the MFA check. If you override async_finish, return await super().async_finish(flow_result) so the MFA check still runs.

For example, change your login flow's base class:

Python

from homeassistant.auth.providers import MfaLoginFlow

class MyLoginFlow(MfaLoginFlow[MyAuthProvider]):
...

If your provider overrides support_mfa, remove the property. If it returned True, extend MfaLoginFlow as shown above, or your provider stops asking for a second factor. If it returned False, keep extending LoginFlow.
