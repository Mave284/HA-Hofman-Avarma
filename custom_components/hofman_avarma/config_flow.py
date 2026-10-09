"""Config flow for the AVARMA heat pump."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
)

from .api import AvarmaClient, AvarmaConnectionError, AvarmaDeviceError
from .const import (
    CONF_FRAMER,
    CONF_SCAN_INTERVAL,
    CONF_SLAVE,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE,
    DOMAIN,
    FRAMER_RTU_OVER_TCP,
    FRAMER_TCP,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)
from .registers import BLOCK_STATUS

_LOGGER = logging.getLogger(__name__)


def _user_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=defaults.get(CONF_HOST, "")): TextSelector(),
            vol.Required(CONF_PORT, default=defaults.get(CONF_PORT, DEFAULT_PORT)): NumberSelector(
                NumberSelectorConfig(min=1, max=65535, mode=NumberSelectorMode.BOX)
            ),
            vol.Required(CONF_SLAVE, default=defaults.get(CONF_SLAVE, DEFAULT_SLAVE)): NumberSelector(
                NumberSelectorConfig(min=1, max=247, mode=NumberSelectorMode.BOX)
            ),
            vol.Required(CONF_FRAMER, default=defaults.get(CONF_FRAMER, FRAMER_TCP)): SelectSelector(
                SelectSelectorConfig(
                    options=[FRAMER_TCP, FRAMER_RTU_OVER_TCP],
                    mode=SelectSelectorMode.LIST,
                    translation_key=CONF_FRAMER,
                )
            ),
        }
    )


async def _validate(data: dict[str, Any]) -> None:
    """Try to read the status block once."""
    client = AvarmaClient(data[CONF_HOST], data[CONF_PORT], data[CONF_SLAVE], data[CONF_FRAMER])
    try:
        await client.read_registers(BLOCK_STATUS[0], 4)
    finally:
        await client.close()


class AvarmaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            user_input[CONF_HOST] = user_input[CONF_HOST].strip()
            user_input[CONF_PORT] = int(user_input[CONF_PORT])
            user_input[CONF_SLAVE] = int(user_input[CONF_SLAVE])
            await self.async_set_unique_id(
                f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}:{user_input[CONF_SLAVE]}"
            )
            self._abort_if_unique_id_configured()
            try:
                await _validate(user_input)
            except AvarmaConnectionError as err:
                _LOGGER.debug("Connection test failed: %s", err)
                errors["base"] = "cannot_connect"
            except AvarmaDeviceError as err:
                _LOGGER.debug("Unexpected Modbus answer: %s", err)
                errors["base"] = "invalid_response"
            except Exception:
                _LOGGER.exception("Unexpected error during connection test")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=f"AVARMA ({user_input[CONF_HOST]})", data=user_input
                )
        return self.async_show_form(
            step_id="user",
            data_schema=_user_schema(user_input or {}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry) -> AvarmaOptionsFlow:
        return AvarmaOptionsFlow()


class AvarmaOptionsFlow(OptionsFlow):
    """Polling interval."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            user_input[CONF_SCAN_INTERVAL] = int(user_input[CONF_SCAN_INTERVAL])
            return self.async_create_entry(data=user_input)
        current = self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SCAN_INTERVAL, default=current): NumberSelector(
                        NumberSelectorConfig(
                            min=MIN_SCAN_INTERVAL,
                            max=MAX_SCAN_INTERVAL,
                            unit_of_measurement="s",
                            mode=NumberSelectorMode.BOX,
                        )
                    )
                }
            ),
        )
