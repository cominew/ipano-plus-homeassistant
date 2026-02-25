# Example Automations & Scripts

This page contains copy-paste ready Home Assistant automation examples and small scripts that demonstrate typical uses of the iPano Plus integration (button triggers, backlight effects, relay control, and more). Use these as templates and adapt entity IDs and service parameters for your setup.

---

## Table of contents

- [Button press → Toggle a light](#button-press--toggle-a-light)  
- [Button press → Call script with conditions](#button-press--call-script-with-conditions)  
- [Pulse backlight as welcome when a person arrives](#pulse-backlight-as-welcome-when-a-person-arrives)  
- [Use relay to trigger an external device](#use-relay-to-trigger-an-external-device)  
- [Complex: long-press vs short-press behavior](#complex-long-press-vs-short-press-behavior)  
- [Script: Flash backlights in sequence](#script-flash-backlights-in-sequence)  

---

## Button press → Toggle a light

Trigger an automation when a button on the panel is pressed, and toggle a light.

```yaml
alias: iPano Button 1 → Toggle Living Room Light
description: Toggle light when iPano Button 1 is pressed
trigger:
  - platform: event
    event_type: ipano_button_pressed
    event_data:
      button: button_1
      action: pressed
action:
  - service: light.toggle
    target:
      entity_id: light.living_room
mode: single
```

Notes:
- `event_type` is `ipano_button_pressed`. The `event_data` keys may differ depending on how the integration emits them — confirm exact event payload in Developer Tools → Events.

---

## Button press → Call script with conditions

Call a script only if the relay is currently off.

```yaml
alias: iPano Button 2 → Conditional Action
trigger:
  - platform: event
    event_type: ipano_button_pressed
    event_data:
      button: button_2
      action: pressed
condition:
  - condition: state
    entity_id: switch.ipano_plus_relay_1
    state: "off"
action:
  - service: script.turn_on
    target:
      entity_id: script.turn_on_tv
mode: single
```

---

## Pulse backlight as welcome when a person arrives

Use the pulse backlight service to draw attention when someone arrives.

```yaml
alias: Welcome — Pulse iPano Backlight
trigger:
  - platform: state
    entity_id: person.you
    to: "home"
action:
  - service: ipano_plus.pulse_backlight
    data:
      button: 1
      color: "white"
      times: 3
      duration: 0.4
mode: single
```

---

## Use relay to trigger an external device

Turn on a relay for 10 seconds to pulse power to an external device.

```yaml
alias: Pulse Relay 1 For 10s
trigger:
  - platform: event
    event_type: ipano_button_pressed
    event_data:
      button: button_3
      action: pressed
action:
  - service: ipano_plus.control_relay
    data:
      relay: 1
      state: "on"
  - delay:
      seconds: 10
  - service: ipano_plus.control_relay
    data:
      relay: 1
      state: "off"
mode: single
```

Important: Carefully test hardware interactions before using them in production (avoid powering high-current devices directly through relays that are not rated for them).

---

## Complex: long-press vs short-press behavior

If your integration emits a `repeat_count` or `action` field, you can implement short-press vs long-press. Adjust to your event payload.

```yaml
alias: iPano Button 4 Short / Long Press
trigger:
  - platform: event
    event_type: ipano_button_pressed
    event_data:
      button: button_4
action:
  - choose:
      - conditions:
          - condition: template
            value_template: "{{ trigger.event.data.action == 'long_press' or trigger.event.data.repeat_count | int >= 3 }}"
        sequence:
          - service: light.turn_on
            target:
              entity_id: light.accent
          - service: ipano_plus.pulse_backlight
            data:
              button: 4
              color: "white"
              times: 4
              duration: 0.2
    default:
      - service: input_boolean.toggle
        target:
          entity_id: input_boolean.short_press_toggle
mode: single
```

---

## Script: Flash backlights in sequence

A reusable script showing how to flash each button backlight in sequence.

```yaml
alias: ipano_flash_sequence
sequence:
  - repeat:
      count: 3
      sequence:
        - service: ipano_plus.set_backlight
          data:
            button: 1
            color: "white"
        - delay: 0.15
        - service: ipano_plus.set_backlight
          data:
            button: 2
            color: "white"
        - delay: 0.15
        - service: ipano_plus.set_backlight
          data:
            button: 3
            color: "white"
        - delay: 0.15
        - service: ipano_plus.set_backlight
          data:
            button: 4
            color: "white"
        - delay: 0.15
        - service: ipano_plus.set_all_backlights
          data:
            color: "off"
mode: single
```

---

## Tips & best practices

- Always confirm the exact `event` payload and `entity_id` naming in Developer Tools on your Home Assistant instance — different HA versions or translations may change slugification.
- Use short-lived automations for single responsibilities (maintainability).
- Test hardware-related automations with safe devices (e.g., lights) first before controlling critical hardware.
- Use a `script` for shared sequences to avoid duplicating logic across automations.

---
