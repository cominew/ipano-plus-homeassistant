# Troubleshooting — iPano Plus Integration

This document helps you gather information, perform common troubleshooting steps, and prepare useful data to include when opening an issue. It also provides step-by-step instructions to capture logs and raw TCP messages if needed.

---

## Quick checks

1. Verify device network reachability
   - Ping the panel IP:
     - Windows: `ping 192.168.2.120`
     - Linux/Mac: `ping -c 4 192.168.2.120`
   - Test port connectivity (TCP 3124):
     - Windows PowerShell: `Test-NetConnection -ComputerName 192.168.2.120 -Port 3124`
     - Linux/Mac: `telnet 192.168.2.120 3124` or `nc -vz 192.168.2.120 3124`

2. Confirm correct IP and port in integration config
   - Default port is `3124`. If the panel was reconfigured, update the integration entry in Settings → Devices & Services.

3. Ensure only one process is accessing the panel
   - The panel’s TCP service typically allows a single client — make sure you don’t have another tool connected.

---

## Enable debug logging (Home Assistant)

Add or update your `configuration.yaml` to include:

```yaml
logger:
  default: info
  logs:
    custom_components.ipano_plus: debug
```

Then restart Home Assistant. Watch the logs in Supervisor → System → Logs or Configuration → Logs (or the HA log file depending on install type).

When filing an issue, include the debug log lines around the failure (timestamp ± 10–20 lines) and remove any sensitive data (IPs are OK — avoid posting private credentials).

---

## Useful log snippets to collect

When reporting issues, include:
- The error or exception traceback (copy the full trace).
- Recent debug messages from `custom_components.ipano_plus`.
- The integration startup sequence log (shows connection attempt and handshake).
- Any JSON messages shown in the logs (they show what the panel sent and how the bridge parsed them).

Example useful excerpt (paste actual lines in the issue):
```
2026-02-03 12:31:22 DEBUG (MainThread) [custom_components.ipano_plus.bridge] Connecting to 192.168.2.120:3124
2026-02-03 12:31:22 DEBUG (MainThread) [custom_components.ipano_plus.bridge] Connected — sending initial queries
2026-02-03 12:31:22 DEBUG (MainThread) [custom_components.ipano_plus.bridge] Received raw: {"type":"button","id":1,"action":"pressed"}
```

---

## Capturing raw TCP messages

If the integration’s debug logs are not sufficient, capture raw TCP messages:

Option A (Linux/macOS):
- Use netcat:
  ```
  nc -l 9999 > capture.log
  ```
  Point the panel temporarily to send to a test listener, or use tcpdump:
  ```
  sudo tcpdump -i eth0 host 192.168.2.120 and port 3124 -w capture.pcap
  ```

Option B (Windows):
- Use `Wireshark` to capture traffic on the interface and filter `ip.addr == 192.168.2.120 && tcp.port == 3124`. Export the relevant packet bytes or the ASCII stream.

Important: do not post PCAP files with private network captures publicly. If you must share, redact sensitive data and share only the minimal required ASCII JSON messages.

---

## Common problems & solutions

1. Connection refused / timeout
   - Panel may be offline or configured to a different port. Reboot the panel or check its network settings.
   - Confirm no firewall on your network blocks the connection.

2. JSON parse errors
   - Some panels might send slight variations in JSON (missing fields / different keys). Enable debug logs and paste the exact raw message so maintainers can adapt parsing.

3. Duplicate or missing entities after install
   - Remove integration entry and re-add (Settings → Devices & Services → remove the ipano entry, then Add Integration again).
   - If entities remain orphaned, check entities for "disabled" states or clean up via Developer Tools.

4. Services not appearing in Developer Tools → Services
   - Ensure `services.yaml` exists in `custom_components/ipano_plus/` and the integration is loaded. Restart Home Assistant.

---

## What to include in a GitHub issue

When opening an issue please provide:
- HA version and installation type (Core, Supervised, OS)
- Integration version (release tag or commit SHA)
- Panel model and firmware (if known)
- Minimal reproduction steps
- Debug log excerpt for `custom_components.ipano_plus`
- Any captured raw JSON messages (if available)
- Description of expected vs actual behavior

Example issue template excerpt (follow this when filing):
```
Home Assistant version: 2026.1.0
Integration version: v1.0.0 (commit 6d48977)
Panel model: PD680 (iPano Plus 6")
Problem: Buttons do not generate events when pressed.
Steps to reproduce:
1. Install integration via HACS
2. Add integration and wait for entities to appear
3. Press physical button
Debug logs (attached):
- paste log excerpt here
Raw messages (optional):
{"type":"button","id":1,"action":"pressed"}
```

---

## When to ask for help

Open an issue when:
- You cannot connect after verifying IP/port and network reachability.
- You see repeated JSON parsing errors in debug logs.
- The integration crashes or fails to load.
- You want help interpreting raw panel messages.

Before opening an issue, search existing issues — there may already be a solution.

---

## Support channels

- Preferred: GitHub Issues on this repository — include logs and data as described above.
- Community: Home Assistant forums or HACS discussions for general help (but post core bugs here).