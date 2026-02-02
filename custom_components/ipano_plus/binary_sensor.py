"""Binary sensor platform for iPano Plus."""
import logging
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN, SIGNAL_BUTTON_EVENT, SIGNAL_PROXIMITY_UPDATE

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up iPano Plus binary sensors from config entry."""
    _LOGGER.debug("Setting up iPano binary sensors")

    sensors = [
        iPanoButtonSensor(config_entry, "Button 1", "button_1"),
        iPanoButtonSensor(config_entry, "Button 2", "button_2"),
        iPanoButtonSensor(config_entry, "Button 3", "button_3"),
        iPanoButtonSensor(config_entry, "Button 4", "button_4"),
        iPanoProximitySensor(config_entry),
    ]

    async_add_entities(sensors)


class iPanoButtonSensor(BinarySensorEntity):
    """Representation of an iPano button."""

    _attr_device_class = BinarySensorDeviceClass.RUNNING
    _attr_should_poll = False

    def __init__(self, config_entry, name, button_id):
        self._config_entry = config_entry
        self._attr_name = f"iPano {name}"
        self._attr_unique_id = f"{config_entry.entry_id}_{button_id}"
        self._attr_is_on = False
        self._button_id = button_id
        self._repeat_count = 0
        self._dispatcher_unsub = None

    async def async_added_to_hass(self) -> None:
        """Register dispatcher callback for button events."""
        self._dispatcher_unsub = async_dispatcher_connect(
            self.hass, SIGNAL_BUTTON_EVENT, self._handle_button_event
        )

    @callback
    def _handle_button_event(self, event):
        """Handle button press/release event from dispatcher."""
        try:
            if event.get("button") == self._button_id:
                is_pressed = event.get("action") == "pressed"
                repeat_count = event.get("repeat_count", 0)
                self._attr_is_on = is_pressed
                self._repeat_count = repeat_count
                self._attr_extra_state_attributes = {
                    "repeat_count": repeat_count,
                    "button_id": self._button_id,
                    "last_event": event.get("timestamp"),
                }
                self.async_write_ha_state()
                _LOGGER.debug(f"Button {self._button_id} updated: {'pressed' if is_pressed else 'released'}")
        except Exception as e:
            _LOGGER.error(f"Error in button handler: {e}")

    @property
    def device_info(self):
        return {
            "identifiers": {("ipano", self._config_entry.entry_id)},
            "name": self._config_entry.data.get("name", "iPano Plus"),
            "manufacturer": "iPano",
            "model": "Plus 6-inch",
        }

    @property
    def extra_state_attributes(self):
        return {
            "repeat_count": self._repeat_count,
            "button_id": self._button_id,
        }

    async def async_will_remove_from_hass(self):
        if self._dispatcher_unsub:
            self._dispatcher_unsub()


class iPanoProximitySensor(BinarySensorEntity):
    """Representation of iPano proximity sensor."""

    _attr_device_class = BinarySensorDeviceClass.MOTION
    _attr_should_poll = False

    def __init__(self, config_entry):
        self._config_entry = config_entry
        self._attr_name = "iPano Proximity"
        self._attr_unique_id = f"{config_entry.entry_id}_proximity"
        self._attr_is_on = False
        self._dispatcher_unsub = None

    async def async_added_to_hass(self) -> None:
        """Register dispatcher for proximity updates."""
        self._dispatcher_unsub = async_dispatcher_connect(
            self.hass, SIGNAL_PROXIMITY_UPDATE, self._handle_proximity_event
        )

        # initialize from bridge if available
        bridge = self.hass.data.get(DOMAIN, {}).get(self._config_entry.entry_id)
        if bridge and hasattr(bridge, "proximity_state"):
            self._attr_is_on = bridge.proximity_state

    @callback
    def _handle_proximity_event(self, detected):
        self._attr_is_on = bool(detected)
        self.async_write_ha_state()
        _LOGGER.debug(f"Proximity updated: {self._attr_is_on}")

    @property
    def device_info(self):
        return {
            "identifiers": {("ipano", self._config_entry.entry_id)},
            "name": self._config_entry.data.get("name", "iPano Plus"),
            "manufacturer": "iPano",
            "model": "Plus 6-inch",
        }

    async def async_will_remove_from_hass(self):
        if self._dispatcher_unsub:
            self._dispatcher_unsub()
