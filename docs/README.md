
# iPano Plus — Documentation

This documentation covers installation, configuration, services, example automations, developer notes, and troubleshooting for the iPano Plus Home Assistant integration.

---

## Overview

iPano Plus integration provides:
- Binary sensors and events for physical buttons
- Backlight state sensors and services to control color/effects
- Relay switches (control and state)
- Proximity/motion sensor
- Screen wake service and additional utility services
- UI config flow for easy setup

Designed for the 6‑inch iPano Plus (PD680) panel and similar variants.

---

## Requirements

- Home Assistant 2024.x or newer recommended.
- No external Python packages required — integration uses core Home Assistant APIs.
- Panel TCP service enabled and reachable on the local network (default port 3124).

---

## Installation

Option A — HACS (recommended)
1. In Home Assistant open HACS → Integrations.
2. Click ⋯ → Custom repositories → Add repository:
   - Repository: `https://github.com/Cominew/ipano-plus-homeassistant`
   - Category: Integration
3. Install from HACS and restart Home Assistant.

Option B — Manual
1. Download the latest release ZIP from GitHub Releases.
2. Extract and copy the folder `custom_components/ipano_plus/` into your Home Assistant `config/custom_components/`.
3. Restart Home Assistant.

---

## Configuration (Config Flow)

1. Settings → Devices & Services → Add Integration
2. Search and choose "iPano Plus"
3. Enter:
   - Host / IP: e.g. `192.168.2.120`
   - Port: default `3124`
   - Name: optional device friendly name
4. The integration will attempt a quick TCP connection to validate the device and then create the entry.

If the quick test fails, check network connectivity and ensure the panel's TCP service is enabled.

---

## Entities & Events

Entities created:
- Buttons (binary_sensor) — up to 4 for the 6" panel
- Backlight sensors (sensor) — show current backlight mode for each button
- Relays (switch) — 1–2 typical, supports up to 6 on some bases
- Proximity (binary_sensor) — motion-like entity
- Custom events on the HA event bus (topic: `ipano_button_pressed`, `ipano_relay_changed`, `ipano_proximity_detected`)

Events carry payloads with:
- device name, button id/name, action (pressed/released), timestamp, repeat_count, key_code, etc.

Use Developer Tools → Events → Listen to `ipano_button_pressed` while pressing a physical button on the panel to observe payloads.

---

## Services (full details)

All services are registered under the `ipano_plus` domain.

- `wake_screen` — wakes the panel display
  - no data

- `set_backlight` — set a single button backlight
  - data:
    - `button` (int: 1–4)
    - `color` (string: "off", "white", "yellow", "both" if supported)

- `set_all_backlights` — set all backlights at once
  - data:
    - `color` (string)

- `pulse_backlight` — pulse a backlight on/off repeatedly
  - data:
    - `button` (int)
    - `color` (string)
    - `times` (int)
    - `duration` (float seconds per on/off)

- `fade_backlight` — fade from one color to another (approximate)
  - data:
    - `button`, `from_color`, `to_color`, `duration`

- `breathing_backlight` — breathing/cycling effect
  - data: `button`, `color`, `cycles`, `breath_duration`

- `control_relay` — control a relay
  - data:
    - `relay` (int: 1..N)
    - `state` ("on" / "off")

Service examples:
```yaml
# Wake the display
service: ipano_plus.wake_screen

# Set button 3 to yellow
service: ipano_plus.set_backlight
data:
  button: 3
  color: "yellow"

# Toggle relay 1
service: ipano_plus.control_relay
data:
  relay: 1
  state: "on"

