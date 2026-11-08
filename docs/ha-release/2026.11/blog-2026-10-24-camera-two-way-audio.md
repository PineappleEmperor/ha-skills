# Two-way audio for camera entities

Fetched from https://contributors.home-assistant.io/blog/2026/10/24/camera-two-way-audio/
Copyright (c) Home Assistant contributors. home-assistant/contributors.home-assistant.io publishes no licence; this copy is kept for reference and attribution only.
Modified: converted from HTML to plain text by `scripts/fetch_ha_sources.py`. It keeps the article body and loses everything the markup carried — navigation and chrome, link targets, image alt text, table and list structure, and code formatting. No wording has been changed, added or reordered.

Blog

Two-way audio for camera entities

Robert ReschOctober 24, 2026·1 min read

Core and integrations

Many cameras and doorbells have a speaker, so you can talk to whoever is standing at the door. As of Home Assistant Core 2026.11, camera entities can declare that they support two-way audio. Users can then talk through the camera while they watch its live stream.

Two-way audio starts as a preview feature in Home Assistant Labs. Users turn it on under Settings > System > Labs.

What your integration needs

Set the new camera_entity_capabilities property to a CameraEntityCapabilities instance with two_way_audio as True. This property defaults to CameraEntityCapabilities(), where two_way_audio is False.

Only declare two-way audio when the camera can actually receive audio over the stream Home Assistant uses. For example, the Reolink integration declares it only when the camera supports two-way audio and Home Assistant streams from it over RTSP (home-assistant/core#184716).

Example:

Python

from homeassistant.components.camera import (
Camera,
CameraEntityCapabilities,
CameraEntityFeature,
)

class MyCamera(Camera):
"""A doorbell camera with a speaker."""

_attr_supported_features = CameraEntityFeature.STREAM

def __init__(self, device: MyDevice) -> None:
"""Initialize the camera."""
super().__init__()
self._device = device
self._attr_camera_entity_capabilities = CameraEntityCapabilities(
two_way_audio=device.supports_two_way_audio and device.protocol == "rtsp"
)

When the frontend gets two-way audio

Your entity declares what the camera can do. The camera platform decides what the frontend gets. It reports two-way audio only when all of these hold:

Your entity declares two-way audio.

The camera streams over WebRTC, natively or through a WebRTC provider like go2rtc. Two-way audio is not available over HLS.

The user turned on the Two-way audio preview feature in Labs.

Browsers only give access to the microphone over a secure connection. For now, two-way audio only works when Home Assistant is opened over HTTPS.

More information

The camera entity documentation describes two-way audio, and the Labs documentation explains how preview features work.
