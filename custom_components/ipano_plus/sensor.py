"""Sensor platform for iPano Plus."""
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN, SIGNAL_BACKLIGHT_UPDATE

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up iPano Plus sensors from config entry."""
    _LOGGER.debug("Setting up iPano sensors")
    sensors = [
        iPanoBacklightSensor(config_entry, "Backlight 1", 1),
        iPanoBacklightSensor(config_entry, "Backlight 2", 2),
        iPanoBacklightSensor(config_entry, "Backlight 3", 3),
        iPanoBacklightSensor(config_entry, "Backlight 4", 4),
    ]
    async_add_entities(sensors)


class iPanoBacklightSensor(SensorEntity):
    """Representation of iPano button backlight."""

    def __init__(self, config_entry, name, button_num):
        self._config_entry = config_entry
        self._attr_name = f"iPano {name}"
        self._attr_unique_id = f"{config_entry.entry_id}_backlight_{button_num}"
        self._attr_native_value = 0
        self._button_num = button_num
        self._dispatcher_unsub = None

    @property
    def device_info(self):
        return {
            "identifiers": {("ipano", self._config_entry.entry_id)},
            "name": self._config_entry.data.get("name", "iPano Plus"),
            "manufacturer": "iPano",
            "model": "Plus 6-inch",
        }

    async def async_added_to_hass(self) -> None:
        """Register dispatcher for backlight updates."""
        self._dispatcher_unsub = async_dispatcher_connect(
            self.hass, SIGNAL_BACKLIGHT_UPDATE, self._handle_backlight_update
        )

        bridge = self.hass.data.get(DOMAIN, {}).get(self._config_entry.entry_id)
        if bridge and hasattr(bridge, "backlight_states"):
            self._attr_native_value = bridge.backlight_states.get(self._button_num - 1, 0)

    @callback
    def _handle_backlight_update(self, backlight_states):
        val = backlight_states.get(self._button_num - 1, 0)
        self._attr_native_value = val
        self.async_write_ha_state()

    async def async_will_remove_from_hass(self):
        if self._dispatcher_unsub:
            self._dispatcher_unsub()
