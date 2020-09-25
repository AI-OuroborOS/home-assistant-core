"""Config flow for Govee LED strips integration."""

import logging

from govee_api_laggat import Govee

from homeassistant import config_entries, core, exceptions

from .const import CONF_API_KEY, DATA_SCHEMA, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect.

    Return info that you want to store in the config entry.y the user.
    """
    hub = await Govee.create(data[CONF_API_KEY])

    _, error = await hub.get_devices()
    if error:
        raise CannotConnect(error)

    # Return info that you want to store in the config entry.
    return data


@config_entries.HANDLERS.register(DOMAIN)
class GoveeFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Govee LED strips."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                return self.async_create_entry(title=DOMAIN, data=info)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception as ex:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception: %s", ex)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""

    def __init__(self, message, *args, **kwargs):
        """Create cannot connect error."""
        super().__init__(*args, **kwargs)
        self._message = message

    @property
    def message(self):
        """Get the message why the connection failed."""
        return self._message
