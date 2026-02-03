# iPano Plus Home Assistant Integration

<div align="center">

[![GitHub release](https://img.shields.io/github/release/Cominew/ipano-plus-homeassistant.svg)](https://github.com/Cominew/ipano-plus-homeassistant/releases)
[![GitHub license](https://img.shields.io/github/license/Cominew/ipano-plus-homeassistant)](LICENSE)
[![HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Cominew&repository=ipano-plus-homeassistant&category=integration)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-Yes-green.svg)](https://github.com/Cominew/ipano-plus-homeassistant/commits/main)
[![GitHub issues](https://img.shields.io/github/issues/Cominew/ipano-plus-homeassistant)](https://github.com/Cominew/ipano-plus-homeassistant/issues)
[![GitHub stars](https://img.shields.io/github/stars/Cominew/ipano-plus-homeassistant)](https://github.com/Cominew/ipano-plus-homeassistant/stargazers)

</div>

Control your 6-inch iPano Plus wall touchscreen panels with Home Assistant.

## Overview

- Exposes physical buttons as binary sensors and fires events for presses
- Reads and controls button backlights (set, pulse, fade, breathing)
- Exposes relays as switches (1–2 typical; up to 6 if using dual base)
- Proximity/motion sensor and screen wake control
- UI config flow and Home Assistant services

## Installation

### Option 1 — Install via HACS (Recommended)
Click the badge below to open HACS and add the repository:

[![Add to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Cominew&repository=ipano-plus-homeassistant&category=integration)

1. Open HACS → Integrations
2. Click the badge above (or Add custom repository) → Repository URL: `https://github.com/Cominew/ipano-plus-homeassistant`
3. Category: Integration → Install
4. Restart Home Assistant

### Option 2 — Manual installation via HACS custom repo
1. In HACS → Integrations → 3‑dot menu → Custom repositories
2. Add `https://github.com/Cominew/ipano-plus-homeassistant` as an Integration
3. Install the integration from HACS
4. Restart Home Assistant

### Option 3 — Manual installation (no HACS)
1. Download the [latest release](https://github.com/Cominew/ipano-plus-homeassistant/releases)
2. Copy `custom_components/ipano_plus/` to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

1. Settings → Devices & Services → Add Integration
2. Search for `iPano Plus` and select it
3. Provide the panel IP (default: `192.168.2.120`) and port (default: `3124`)

## Entities created (examples)

Note: actual entity_ids may vary depending on your Home Assistant entity naming and slugification. Check Developer Tools → States for the exact entity_ids after adding the integration.

- Buttons (binary sensors)
  - Example: `binary_sensor.iPano_Button_1` (display name: `iPano Button 1`)
  - Up to 4 buttons for the 6" panel

- Relays (switches)
  - Example: `switch.iPano_Relay_1`, `switch.iPano_Relay_2` (up to 6 on dual base)

- Proximity sensor
  - Example: `binary_sensor.iPano_Proximity`

- Backlight sensors (optional, as sensors showing backlight state)
  - Example: `sensor.iPano_Backlight_1` ... `sensor.iPano_Backlight_4`

If you want canonical entity_ids in this README, install the integration and copy the exact IDs shown in Developer Tools → States, then update this doc.

## Services

The integration registers several helper services under the `ipano_plus` domain:

- `ipano_plus.wake_screen` — Wake the panel screen
- `ipano_plus.set_backlight` — Set one button backlight
- `ipano_plus.set_all_backlights` — Set all backlights
- `ipano_plus.pulse_backlight` — Pulse backlight effect
- `ipano_plus.fade_backlight` — Fade backlight effect
- `ipano_plus.breathing_backlight` — Breathing backlight effect
- `ipano_plus.control_relay` — Control a relay (on/off)

### Service examples (Developer Tools → Services)

```yaml
# Set button 1 backlight to white
service: ipano_plus.set_backlight
data:
  button: 1
  color: "white"

# Set all buttons to yellow
service: ipano_plus.set_all_backlights
data:
  color: "yellow"

# Wake the screen
service: ipano_plus.wake_screen

# Pulse button 2 three times
service: ipano_plus.pulse_backlight
data:
  button: 2
  color: "white"
  times: 3
  duration: 0.5

# Set relay 1 ON
service: ipano_plus.control_relay
data:
  relay: 1
  state: "on"
```

## Troubleshooting

- If integration fails to connect:
  - Verify IP and port are correct and that the panel is reachable on the network (ping / telnet).
  - Enable debug logging in `configuration.yaml`:
    ```yaml
    logger:
      default: info
      logs:
        custom_components.ipano_plus: debug
    ```
  - Restart Home Assistant and check Logs for detailed messages.

- Check Developer Tools → Events and listen for `ipano_button_pressed` to verify button events are firing.

## Compatibility & Requirements

- Home Assistant 2024.x or newer recommended
- No external Python packages required (integration uses core HA APIs)
- Tested with iPano Plus 6" (PD680) panels

## Contributing

See `CONTRIBUTING.md` for how to contribute, run linting, and submit PRs.

## License

MIT — see `LICENSE`.
