# iPano Plus Home Assistant Integration

Totally free Home Assistant integration for the iPano Plus 6‑inch in‑wall touch panel (PD680 / Plus 6‑inch).

This integration connects Home Assistant to the panel's TCP service (default port 3124) to expose buttons, backlights, relays and the proximity sensor, and to provide services for backlight effects and screen control.

Badges
- HACS (if you add this repository to HACS)
- License: MIT

Quick links
- Docs (for HACS): docs/README.md
- Integration folder: custom_components/ipano_plus/

## Features
- Persistent TCP bridge with heartbeat and reconnect
- Button presses exposed as binary sensors and HA bus events
- Per-button backlight sensors and services (set, pulse, fade, breathing)
- Relay switches (1–2 for single base, up to 6 for dual base)
- Proximity sensor (binary sensor) and screen wake control
- UI config flow for easy setup
- Developer-friendly: logs, dispatcher signals, clear service definitions

## Installation

### Via HACS (recommended)
1. Add the repository to HACS (Integration category).
2. Install **iPano Plus** from HACS.
3. Restart Home Assistant.
4. Add the integration via **Settings → Devices & Services → Add Integration → iPano Plus**.

> Note: To appear in HACS, a repository must have proper HACS metadata (this repo contains `.hacs.json` and `info.md`).

### Manual installation
1. Download the latest release from this repository.
2. Copy the `custom_components/ipano_plus/` folder into your Home Assistant `config/custom_components/` directory.
3. Restart Home Assistant.
4. Add the integration through **Settings → Devices & Services → Add Integration → iPano Plus** and enter the panel IP and port.

## Getting started
1. After installation, go to **Settings → Devices & Services**.
2. Click **Add Integration** and search for **iPano Plus**.
3. Complete the config flow: provide the panel IP (and optional friendly name). Default port: `3124`.

## Entities
After setup you will see entities for:
- Binary sensors: iPano Button 1 … Button 4
- Binary sensor: iPano Proximity
- Switches: iPano Relay 1 … Relay 2 (or up to 6 on dual-base panels)
- Sensors: iPano Backlight 1 … Backlight 4 (values: 0=off, 1=white, 2=yellow, 3=both)

Exact entity ids include the config entry id (unique per installed device). See Settings → Devices → select your iPano → Entities.

## Services (domain: `ipano_plus`)
- `ipano_plus.wake_screen`
- `ipano_plus.set_backlight` — `{ "button": 1, "color": "white" }`
- `ipano_plus.set_all_backlights` — `{ "color": "yellow" }`
- `ipano_plus.pulse_backlight` — `{ "button": 2, "color": "white", "times": 3, "duration": 0.5 }`
- `ipano_plus.fade_backlight`
- `ipano_plus.breathing_backlight`
- `ipano_plus.control_relay` — `{ "relay": 1, "state": "on" }`

See `custom_components/ipano_plus/services.yaml` for UI descriptions.

## Events
The integration fires these HA bus events:
- `ipano_button_pressed` — payload includes `button`, `action`, `repeat_count`, `key_code`, `timestamp`
- `ipano_relay_changed` — payload includes `relay`, `state`, `timestamp`
- `ipano_proximity_detected` — payload includes `detected`, `timestamp`

Use Developer Tools → Events to listen and to build automations.

## Troubleshooting
- If the integration won't add, verify network reachability from your Home Assistant host to the panel (port 3124).
- Enable debug logging for detailed messages:
  ```yaml
  logger:
    default: info
    logs:
      custom_components.ipano_plus: debug