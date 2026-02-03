---
name: Bug report
about: Create a report to help us improve the iPano Plus integration
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Install and configure the integration
2. Perform the action that causes the issue
3. Observe the behavior

**Expected behavior**
What you expected to happen.

**Environment (please complete the following information):**
- Home Assistant version:
- Integration version (release or commit SHA):
- Panel model (e.g. PD680):
- Network setup (VLANs, proxies, etc.) if relevant

**Logs**
Please add relevant debug logs for `custom_components.ipano_plus`. Enable debug logging like this:

```yaml
logger:
  default: info
  logs:
    custom_components.ipano_plus: debug
```

Paste the relevant log excerpt and any raw JSON messages from the panel here.

**Additional context**
Add any other context about the problem here, such as config snippet, automations, or screenshots.