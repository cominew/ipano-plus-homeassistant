"""Switch platform for iPano Plus."""
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN, SIGNAL_RELAY_UPDATE

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up iPano Plus switches from config entry."""
    _LOGGER.debug("Setting up iPano switches")

    # Try to get the bridge for live state
    bridge = hass.data.get(DOMAIN, {}).get(config_entry.entry_id)

    switches = [
        iPanoRelaySwitch(config_entry, bridge, "Relay 1", 1),
        iPanoRelaySwitch(config_entry, bridge, "Relay 2", 2),
    ]

    async_add_entities(switches)


class iPanoRelaySwitch(SwitchEntity):
    """Representation of an iPano relay."""

    def __init__(self, config_entry, bridge, name, relay_num):
        self._config_entry = config_entry
        self._bridge = bridge
        self._attr_name = f"iPano {name}"
        self._attr_unique_id = f"{config_entry.entry_id}_relay_{relay_num}"
        self._attr_is_on = False
        self._relay_num = relay_num
        self._bridge_relay_index = relay_num - 1
        self._available = True
        self._dispatcher_unsub = None

    async def async_added_to_hass(self) -> None:
        """Register dispatcher for relay updates."""
        self._dispatcher_unsub = async_dispatcher_connect(
            self.hass, SIGNAL_RELAY_UPDATE, self._handle_relay_update
        )

        # initialize from bridge
        if self._bridge and hasattr(self._bridge, "relay_states"):
            self._attr_is_on = self._bridge.relay_states.get(self._bridge_relay_index, False)
            self.async_write_ha_state()
            _LOGGER.debug(f"Initial state for relay {self._relay_num}: {self._attr_is_on}")

    @callback
    def _handle_relay_update(self, relay_states):
        val = relay_states.get(self._bridge_relay_index, False)
        if self._attr_is_on != val:
            self._attr_is_on = val
            self.async_write_ha_state()
            _LOGGER.debug(f"Relay {self._relay_num} updated to {self._attr_is_on}")

    @property
    def device_info(self):
        return {
            "identifiers": {("ipano", self._config_entry.entry_id)},
            "name": self._config_entry.data.get("name", "iPano Plus"),
            "manufacturer": "iPano",
            "model": "Plus 6-inch",
        }

    @property
    def available(self) -> bool:
        return self._available

    async def async_turn_on(self, **kwargs):
        _LOGGER.info(f"Turning relay {self._relay_num} ON")
        if self._bridge:
            await self._bridge.async_control_relay(self._relay_num, True)
        else:
            _LOGGER.warning(f"No bridge available for relay {self._relay_num}")

    async def async_turn_off(self, **kwargs):
        _LOGGER.info(f"Turning relay {self._relay_num} OFF")
        if self._bridge:
            await self._bridge.async_control_relay(self._relay_num, False)
        else:
            _LOGGER.warning(f"No bridge available for relay {self._relay_num}")

    async def async_will_remove_from_hass(self):
        if self._dispatcher_unsub:
            self._dispatcher_unsub()
