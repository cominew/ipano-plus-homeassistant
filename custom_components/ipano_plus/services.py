"""Services for iPano Plus."""
import logging
import asyncio
import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SERVICE_WAKE_SCREEN = "wake_screen"
SERVICE_SET_BACKLIGHT = "set_backlight"
SERVICE_SET_ALL_BACKLIGHTS = "set_all_backlights"
SERVICE_PULSE_BACKLIGHT = "pulse_backlight"
SERVICE_FADE_BACKLIGHT = "fade_backlight"
SERVICE_BREATHING_BACKLIGHT = "breathing_backlight"
SERVICE_CONTROL_RELAY = "control_relay"

SERVICE_SCHEMA_SET_BACKLIGHT = vol.Schema(
    {vol.Required("button"): vol.All(vol.Coerce(int), vol.Range(min=1, max=4)), vol.Required("color"): vol.In(["off", "white", "yellow"])}
)

SERVICE_SCHEMA_SET_ALL_BACKLIGHTS = vol.Schema({vol.Required("color"): vol.In(["off", "white", "yellow"])})
SERVICE_SCHEMA_WAKE_SCREEN = vol.Schema({})
SERVICE_SCHEMA_PULSE_BACKLIGHT = vol.Schema(
    {
        vol.Required("button"): vol.All(vol.Coerce(int), vol.Range(min=1, max=4)),
        vol.Optional("color", default="white"): vol.In(["white", "yellow"]),
        vol.Optional("times", default=1): vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
        vol.Optional("duration", default=0.5): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=5.0)),
    }
)
SERVICE_SCHEMA_FADE_BACKLIGHT = vol.Schema(
    {
        vol.Required("button"): vol.All(vol.Coerce(int), vol.Range(min=1, max=4)),
        vol.Optional("from_color", default="white"): vol.In(["white", "yellow"]),
        vol.Optional("to_color", default="off"): vol.In(["off", "white", "yellow"]),
        vol.Optional("duration", default=2.0): vol.All(vol.Coerce(float), vol.Range(min=0.5, max=10.0)),
    }
)
SERVICE_SCHEMA_BREATHING_BACKLIGHT = vol.Schema(
    {
        vol.Required("button"): vol.All(vol.Coerce(int), vol.Range(min=1, max=4)),
        vol.Optional("color", default="white"): vol.In(["white", "yellow"]),
        vol.Optional("cycles", default=3): vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
        vol.Optional("breath_duration", default=4.0): vol.All(vol.Coerce(float), vol.Range(min=1.0, max=10.0)),
    }
)
SERVICE_SCHEMA_CONTROL_RELAY = vol.Schema({vol.Required("relay"): vol.All(vol.Coerce(int), vol.Range(min=1, max=6)), vol.Required("state"): vol.In(["on", "off"])})


async def async_setup_services(hass: HomeAssistant):
    """Set up services for iPano Plus."""

    async def handle_wake_screen(call: ServiceCall):
        _LOGGER.info("Wake screen service called")
        if DOMAIN not in hass.data or not hass.data[DOMAIN]:
            _LOGGER.error("No iPano Plus devices configured")
            return
        for entry_id, bridge in hass.data[DOMAIN].items():
            if hasattr(bridge, "async_wake_screen"):
                await bridge.async_wake_screen()

    async def handle_set_backlight(call: ServiceCall):
        button = call.data.get("button")
        color = call.data.get("color")
        _LOGGER.debug(f"Set backlight service: button={button}, color={color}")
        if DOMAIN not in hass.data or not hass.data[DOMAIN]:
            _LOGGER.error("No iPano Plus devices configured")
            return
        for entry_id, bridge in hass.data[DOMAIN].items():
            if hasattr(bridge, "async_set_backlight"):
                await bridge.async_set_backlight(button, color)

    async def handle_set_all_backlights(call: ServiceCall):
        color = call.data.get("color")
        _LOGGER.debug(f"Set all backlights: color={color}")
        if DOMAIN not in hass.data or not hass.data[DOMAIN]:
            _LOGGER.error("No iPano Plus devices configured")
            return
        for entry_id, bridge in hass.data[DOMAIN].items():
            if hasattr(bridge, "async_set_all_backlights"):
                await bridge.async_set_all_backlights(color)
            else:
                for btn in range(1, 5):
                    await bridge.async_set_backlight(btn, color)

    async def handle_pulse_backlight(call: ServiceCall):
        button = call.data.get("button")
        color = call.data.get("color", "white")
        times = call.data.get("times", 1)
        duration = call.data.get("duration", 0.5)
        _LOGGER.info(f"Pulsing button {button} backlight {times} times")
        if DOMAIN not in hass.data or not hass.data[DOMAIN]:
            _LOGGER.error("No iPano Plus devices configured")
            return
        for entry_id, bridge in hass.data[DOMAIN].items():
            if hasattr(bridge, "async_set_backlight"):
                for _ in range(times):
                    await bridge.async_set_backlight(button, color)
                    await asyncio.sleep(duration)
                    await bridge.async_set_backlight(button, "off")
                    await asyncio.sleep(duration)

    async def handle_fade_backlight(call: ServiceCall):
        button = call.data.get("button")
        from_color = call.data.get("from_color", "white")
        to_color = call.data.get("to_color", "off")
        duration = call.data.get("duration", 2.0)
        _LOGGER.info(f"Fading button {button} from {from_color} to {to_color}")
        if DOMAIN not in hass.data or not hass.data[DOMAIN]:
            _LOGGER.error("No iPano Plus devices configured")
            return
        for entry_id, bridge in hass.data[DOMAIN].items():
            if hasattr(bridge, "async_set_backlight"):
                await bridge.async_set_backlight(button, from_color)
                if to_color == "off":
                    await asyncio.sleep(duration)
                    await bridge.async_set_backlight(button, "off")
                else:
                    await asyncio.sleep(duration / 2)
                    await bridge.async_set_backlight(button, to_color)

    async def handle_breathing_backlight(call: ServiceCall):
        button = call.data.get("button")
        color = call.data.get("color", "white")
        cycles = call.data.get("cycles", 3)
        breath_duration = call.data.get("breath_duration", 4.0)
        _LOGGER.info(f"Breathing effect on button {button}")
        if DOMAIN not in hass.data or not hass.data[DOMAIN]:
            _LOGGER.error("No iPano Plus devices configured")
            return
        for entry_id, bridge in hass.data[DOMAIN].items():
            if hasattr(bridge, "async_set_backlight"):
                for _ in range(cycles):
                    for i in range(5):
                        await bridge.async_set_backlight(button, color)
                        await asyncio.sleep(breath_duration / 10)
                        await bridge.async_set_backlight(button, "off")
                        await asyncio.sleep(breath_duration / 10)

    async def handle_control_relay(call: ServiceCall):
        relay = call.data.get("relay")
        state = call.data.get("state")
        _LOGGER.info(f"Control relay {relay} -> {state}")
        if DOMAIN not in hass.data or not hass.data[DOMAIN]:
            _LOGGER.error("No iPano Plus devices configured")
            return
        for entry_id, bridge in hass.data[DOMAIN].items():
            if hasattr(bridge, "async_control_relay"):
                await bridge.async_control_relay(relay, state == "on")

    hass.services.async_register(DOMAIN, SERVICE_WAKE_SCREEN, handle_wake_screen, SERVICE_SCHEMA_WAKE_SCREEN)
    hass.services.async_register(DOMAIN, SERVICE_SET_BACKLIGHT, handle_set_backlight, SERVICE_SCHEMA_SET_BACKLIGHT)
    hass.services.async_register(DOMAIN, SERVICE_SET_ALL_BACKLIGHTS, handle_set_all_backlights, SERVICE_SCHEMA_SET_ALL_BACKLIGHTS)
    hass.services.async_register(DOMAIN, SERVICE_PULSE_BACKLIGHT, handle_pulse_backlight, SERVICE_SCHEMA_PULSE_BACKLIGHT)
    hass.services.async_register(DOMAIN, SERVICE_FADE_BACKLIGHT, handle_fade_backlight, SERVICE_SCHEMA_FADE_BACKLIGHT)
    hass.services.async_register(DOMAIN, SERVICE_BREATHING_BACKLIGHT, handle_breathing_backlight, SERVICE_SCHEMA_BREATHING_BACKLIGHT)
    hass.services.async_register(DOMAIN, SERVICE_CONTROL_RELAY, handle_control_relay, SERVICE_SCHEMA_CONTROL_RELAY)

    _LOGGER.info("iPano Plus services registered")
