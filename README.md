<p align="center">
  <img src="./logo.svg" alt="iPano Plus logo" width="160" />
</p>

# iPano Plus Home Assistant Integration

[![Add to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Cominew&repository=ipano-plus-homeassistant&category=integration)
[![Release](https://img.shields.io/github/v/release/Cominew/ipano-plus-homeassistant)](https://github.com/Cominew/ipano-plus-homeassistant/releases)
[![License](https://img.shields.io/github/license/Cominew/ipano-plus-homeassistant)](LICENSE)

A free integration for iPano Plus 6‑inch in‑wall touch panels (PD680 series).

Overview
- Exposes physical buttons as binary sensors and events
- Control backlights (set, pulse, fade, breathing)
- Relay switches (1–6 depending on base)
- Proximity sensor and screen wake control
- UI config flow and Home Assistant services

Installation
- Via HACS (recommended): Add repository in HACS (Integration category) using the badge above.
- Manual: Copy `custom_components/ipano_plus/` into `config/custom_components/` and restart Home Assistant.

Documentation
- Full documentation: docs/README.md

Screenshots
- (Add screenshots to ./screenshots/ and reference them here)
<p float="left">
  <img src="./screenshots/01-dashboard.png" width="420" alt="Dashboard placeholder" />
  <img src="./screenshots/02-services.png" width="420" alt="Services placeholder" />
</p>

License
- MIT — see LICENSE