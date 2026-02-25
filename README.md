<img width="454" height="235" alt="banner" src="https://github.com/user-attachments/assets/48db0dac-c173-4efd-9b14-0ca00f12b0c0" />

# iPano Plus Home Assistant Integration

<div align="center">

[![GitHub release](https://img.shields.io/github/release/Cominew/ipano-plus-homeassistant.svg)](https://github.com/Cominew/ipano-plus-homeassistant/releases)
[![GitHub license](https://img.shields.io/github/license/Cominew/ipano-plus-homeassistant)](LICENSE)
[![HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Cominew&repository=ipano-plus-homeassistant&category=integration)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-Yes-green.svg)](https://github.com/Cominew/ipano-plus-homeassistant/commits/main)
[![GitHub issues](https://img.shields.io/github/issues/Cominew/ipano-plus-homeassistant)](https://github.com/Cominew/ipano-plus-homeassistant/issues)
[![GitHub stars](https://img.shields.io/github/stars/Cominew/ipano-plus-homeassistant)](https://github.com/Cominew/ipano-plus-homeassistant/stargazers)

</div>

Totally free Home Assistant integration for the **iPano Plus 6-inch in-wall touch panel (PD680)**.

This integration connects Home Assistant to the panel’s TCP service (default port **3124**) to expose buttons, relays, proximity sensor, and backlight effects.

---

## Features

- Persistent TCP bridge with heartbeat + reconnect
- Button presses as binary sensors + HA events
- Backlight control (set / pulse / fade / breathing)
- Relay switches (1–2 standard, up to 6 dual-base)
- Proximity sensor + screen wake control
- UI config flow setup
- Developer-friendly logs and dispatcher signals

---

## Integration Demo (Video)

https://youtu.be/Y6cJNZzwoJM

---

## Installation

### Option 1 — HACS (Recommended)
1. Open HACS → Integrations
2. Add repository:
   ```
   https://github.com/Cominew/ipano-plus-homeassistant
   ```
3. Category → Integration → Install
4. Restart Home Assistant

---

### Option 2 — Manual Install
1. Download latest release
2. Copy:

```
custom_components/ipano_plus/
```

to:

```
config/custom_components/
```

3. Restart Home Assistant

---

## Getting Started

1. Settings → Devices & Services  
2. Add Integration → **iPano Plus**  
3. Enter panel IP + port (default **3124**)

---

## Entities Created

After setup:

**Buttons**
- iPano Button 1–4 (binary sensors)

**Relays**
- Relay 1–2 (up to 6 on dual base)

**Sensors**
- Proximity sensor
- Backlight 1–4 (values: 0=off,1=white,2=yellow,3=both)

Entity IDs include config entry ID → check:
Settings → Devices → iPano → Entities

---

## Services (`ipano_plus`)

- `wake_screen`
- `set_backlight`
- `set_all_backlights`
- `pulse_backlight`
- `fade_backlight`
- `breathing_backlight`
- `control_relay`

Example:

```yaml
service: ipano_plus.set_backlight
data:
  button: 1
  color: white
```

---

## Events

The integration fires:

- `ipano_button_pressed`
- `ipano_relay_changed`
- `ipano_proximity_detected`

Listen via:
Developer Tools → Events

---

## Troubleshooting

If connection fails:

- Verify IP + port reachable
- Enable debug logging:

```yaml
logger:
  default: info
  logs:
    custom_components.ipano_plus: debug
```

Restart Home Assistant and check logs.

---

## Compatibility

- Home Assistant **2024.x+**
- No external Python packages required
- Tested on iPano Plus 6" (PD680)

---

## Contributing

See `CONTRIBUTING.md`.

---

## License

MIT