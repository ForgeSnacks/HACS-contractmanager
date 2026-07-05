"""Config Flow für Vertragsmanager."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CATEGORIES,
    CONF_AUTO_RENEW,
    CONF_CATEGORY,
    CONF_COST,
    CONF_CYCLE,
    CONF_DURATION_MONTHS,
    CONF_NAME,
    CONF_NOTICE_DAYS,
    CONF_PROVIDER,
    CONF_START_DATE,
    CYCLES,
    DOMAIN,
)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): str,
        vol.Required(CONF_CATEGORY, default=CATEGORIES[-1]): vol.In(CATEGORIES),
        vol.Required(CONF_PROVIDER): str,
        vol.Required(CONF_COST): vol.Coerce(float),
        vol.Required(CONF_CYCLE, default=CYCLES[0]): vol.In(CYCLES),
        vol.Required(CONF_START_DATE): str,
        vol.Required(CONF_NOTICE_DAYS, default=30): vol.Coerce(int),
        vol.Required(CONF_DURATION_MONTHS, default=12): vol.Coerce(int),
        vol.Required(CONF_AUTO_RENEW, default=True): bool,
    }
)


class VertragsmanagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow: legt einen neuen Vertrag an."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                from datetime import date

                date.fromisoformat(user_input[CONF_START_DATE])
            except ValueError:
                errors["base"] = "invalid_date"

            if not errors:
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return VertragsmanagerOptionsFlow(config_entry)


class VertragsmanagerOptionsFlow(config_entries.OptionsFlow):
    """Erlaubt das Bearbeiten eines bestehenden Vertrags."""

    def __init__(self, config_entry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        current = {**self.config_entry.data, **self.config_entry.options}

        schema = vol.Schema(
            {
                vol.Required(CONF_CATEGORY, default=current.get(CONF_CATEGORY)): vol.In(CATEGORIES),
                vol.Required(CONF_PROVIDER, default=current.get(CONF_PROVIDER)): str,
                vol.Required(CONF_COST, default=current.get(CONF_COST)): vol.Coerce(float),
                vol.Required(CONF_CYCLE, default=current.get(CONF_CYCLE)): vol.In(CYCLES),
                vol.Required(CONF_START_DATE, default=current.get(CONF_START_DATE)): str,
                vol.Required(CONF_NOTICE_DAYS, default=current.get(CONF_NOTICE_DAYS)): vol.Coerce(int),
                vol.Required(CONF_DURATION_MONTHS, default=current.get(CONF_DURATION_MONTHS)): vol.Coerce(int),
                vol.Required(CONF_AUTO_RENEW, default=current.get(CONF_AUTO_RENEW)): bool,
            }
        )

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(step_id="init", data_schema=schema)
