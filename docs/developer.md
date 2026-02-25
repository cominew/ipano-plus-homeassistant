# Developer Notes — iPano Plus Integration

This page is for maintainers and contributors. It covers local development workflow, testing tips, linting, recommended structure, and notes about the device protocol.

---

## Repository layout (important paths)

- `custom_components/ipano_plus/` — integration code (manifest.json, bridge.py, config_flow.py, sensors, services, translations).
- `docs/` — user documentation (what is rendered by HACS if `.hacs.json` points to `docs/README.md`).
- `tests/` — unit tests (if/when added).
- `.github/` — issue & PR templates, GitHub Actions workflows.

---

## Local development & testing

1. Clone the repository and create a feature branch:
   ```bash
   git checkout -b feature/my-change
   ```

2. Install dependencies (if local scripts require tools — minimal for HA integr.)
   - The integration uses only core HA APIs; no additional pip packages required for runtime.

3. Testing in a local Home Assistant
   - Copy the `custom_components/ipano_plus/` folder to your Home Assistant `config/custom_components/`.
   - Restart Home Assistant.
   - Use `logger` debug to capture messages:
     ```yaml
     logger:
       default: info
       logs:
         custom_components.ipano_plus: debug
     ```
   - Check Developer Tools → Logs for debug messages and raw JSON.

4. Iterating on code
   - After changes, restart HA to load new code (or use the `reload` dev helper for translations / services when applicable).
   - Keep changes small and test each change in isolation.

---

## Running linters & formatting

Recommended tools:
- black (formatter)
- flake8 (style & lint)
- isort (imports sorting)
- mypy (optional, for type checking)

Example commands (if you have a Python dev environment):
```bash
python -m pip install black flake8 isort
black .
flake8
```

Add a `pre-commit` configuration if you want automatic checks on commit.

---

## Tests

- Add unit tests in `tests/` using pytest.
- To test async code in Home Assistant, use the HA test helpers and pytest fixtures (see Home Assistant developer docs).
- Example: create tests for parsing incoming messages and for the bridge reconnect logic.

---

## Protocol notes (for maintainers)

- Communication: newline-delimited JSON messages over TCP (default port 3124).
- Typical message types:
  - Button events: `{ "type": "button", "id": 1, "action": "pressed" }`
  - Backlight updates: `{ "type": "backlight", "id": 2, "color": "white" }`
  - Relay state changes: `{ "type": "relay", "id": 1, "state": "on" }`
  - Proximity: `{ "type": "proximity", "state": true }`

- Bridge responsibilities:
  - Maintain a TCP connection with heartbeat and automatic reconnect.
  - Parse newline-delimited JSON safely and handle malformed messages.
  - Dispatch parsed events to HA entities and event bus.
  - Provide services to send commands to the panel and confirm responses.

---

## Error handling & robustness

- Always guard JSON parsing with try/except and log raw messages for debugging.
- Implement a reconnection back-off strategy if the panel drops the connection repeatedly.
- When sending commands, validate replies (if panel echoes or sends acknowledgements).

---

## Configuration & translations

- `manifest.json` must declare `config_flow: true` for UI setup.
- `strings.json` and `translations/en.json` contain the UI strings for the config flow and the integration.
- Update translations when adding new config options or services.

---

## Release process

1. Merge feature PR into `main` (use squash and merge for small PRs).
2. Update `CHANGELOG.md` with a short entry.
3. Tag a release:
   ```bash
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   ```
4. Draft a GitHub release and copy release notes (used by HACS to show versions).

For HACS compatibility, create a release tag for users to select/install versions.

---

## Contribution workflow (recommended)

- Fork → feature branch → open PR into `main`.
- Use descriptive commit messages (conventional commits recommended: feat, fix, chore, docs).
- Provide tests or testing steps in the PR description.
- Request reviews and address comments; once approved, merge and delete the branch.

---

## Helpful developer utilities

- `tcpdump` / `wireshark` — capture raw traffic for debugging (do not share sensitive captures publicly).
- `netcat` / `nc` — quick TCP send/receive for manual protocol tests.
- Minimal Python REPL to craft and examine sample JSON messages.

---

## Contact & support for maintainers

- Use GitHub discussions or issues for design decisions that affect users.
- Keep docs up to date for public-facing changes.
