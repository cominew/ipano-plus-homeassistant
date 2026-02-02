# Contributing to iPano Plus Home Assistant Integration

Thank you for considering contributing. A few guidelines to make PRs easier to review:

1. Fork the repository and create a feature branch.
2. Keep PRs small and focused.
3. Add clear description and testing steps in the PR.
4. Run linting (flake8 / black) and include formatting consistency.
5. Use debug logs for network-related fixes.
6. If adding features, update docs in `docs/README.md` and `custom_components/ipano_plus/README.md`.

Testing
- Install the integration locally in Home Assistant under `config/custom_components/ipano_plus/` and restart HA.
- Use `logger` debug configuration to view integration logs.

License & Code of Conduct
- By contributing you agree to license your contributions under the MIT license.
