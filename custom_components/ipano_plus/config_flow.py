"""Config flow for iPano Plus."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME

from .const import DOMAIN
from .bridge import iPanoBridge


class iPanoPlusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for iPano Plus."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                bridge = iPanoBridge(self.hass, user_input)
                if await bridge.test_connection():
                    await bridge.async_stop()
                    return self.async_create_entry(
                        title=f"iPano Plus {user_input.get(CONF_HOST)}",
                        data={
                            CONF_HOST: user_input.get(CONF_HOST),
                            CONF_PORT: user_input.get(CONF_PORT),
                            CONF_NAME: user_input.get(CONF_NAME, "iPano Plus"),
                        },
                    )
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default="192.168.2.120"): str,
                    vol.Required(CONF_PORT, default=3124): int,
                    vol.Optional(CONF_NAME, default="iPano Plus"): str,
                }
            ),
            errors=errors,
        )
