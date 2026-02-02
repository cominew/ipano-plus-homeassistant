"""The iPano Plus integration for Home Assistant."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .bridge import iPanoBridge
from .services import async_setup_services

DOMAIN = "ipano_plus"
PLATFORMS = ["sensor", "binary_sensor", "switch"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up iPano Plus from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Create and store bridge (pass hass and the entry.data dict)
    bridge = iPanoBridge(hass, entry.data)
    hass.data[DOMAIN][entry.entry_id] = bridge

    # Start the bridge connection
    await bridge.async_start()

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Set up services (only once per integration)
    if "_services_setup" not in hass.data[DOMAIN]:
        await async_setup_services(hass)
        hass.data[DOMAIN]["_services_setup"] = True

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Clean up bridge connection
        bridge = hass.data[DOMAIN].pop(entry.entry_id)
        # Use the public async_stop method defined on the bridge
        await bridge.async_stop()

    return unload_ok
