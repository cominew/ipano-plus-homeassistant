# iPano Plus (integration)

Short README for the iPano Plus Home Assistant integration.

Quick summary
- Exposes 4 physical buttons (binary sensors + events), 4 backlight sensors, 2–6 relays (switches), and a proximity sensor.
- Communicates with the panel over TCP (default port 3124).
- Provides services to wake the screen, control backlights and relays, and run backlight effects.

Install
- Install via HACS if available, or copy `custom_components/ipano_plus/` to your HA config and restart.

Add the integration
1. Settings → Devices & Services → Add Integration → Search `iPano Plus`
2. Enter IP and port (3124)
