"""Config Flow für Vertragsmanager."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

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


def _build_user_schema(user_input=None):
    user_input = user_input or {}

    return vol.Schema(
        {
            vol.Required(
                CONF_NAME,
                default=user_input.get(CONF_NAME, vol.UNDEFINED),
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.TEXT,
                )
            ),
            vol.Required(
                CONF_CATEGORY,
                default=user_input.get(CONF_CATEGORY, CATEGORIES[-1]),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=CATEGORIES,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_PROVIDER,
                default=user_input.get(CONF_PROVIDER, vol.UNDEFINED),
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.TEXT,
                )
            ),
            vol.Required(
                CONF_COST,
                default=user_input.get(CONF_COST, vol.UNDEFINED),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    step=0.01,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_CYCLE,
                default=user_input.get(CONF_CYCLE, CYCLES[0]),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=CYCLES,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_START_DATE,
                default=user_input.get(CONF_START_DATE, vol.UNDEFINED),
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.DATE,
                )
            ),
            vol.Required(
                CONF_NOTICE_DAYS,
                default=user_input.get(CONF_NOTICE_DAYS, 30),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_DURATION_MONTHS,
                default=user_input.get(CONF_DURATION_MONTHS, 12),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_AUTO_RENEW,
                default=user_input.get(CONF_AUTO_RENEW, True),
            ): selector.BooleanSelector()
        }
    )


def _build_options_schema(current: dict):
    return vol.Schema(
        {
            vol.Required(
                CONF_CATEGORY,
                default=current.get(CONF_CATEGORY, CATEGORIES[-1]),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=CATEGORIES,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_PROVIDER,
                default=current.get(CONF_PROVIDER, vol.UNDEFINED),
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.TEXT,
                )
            ),
            vol.Required(
                CONF_COST,
                default=current.get(CONF_COST, vol.UNDEFINED),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    step=0.01,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_CYCLE,
                default=current.get(CONF_CYCLE, CYCLES[0]),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=CYCLES,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_START_DATE,
                default=current.get(CONF_START_DATE, vol.UNDEFINED),
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.DATE,
                )
            ),
            vol.Required(
                CONF_NOTICE_DAYS,
                default=current.get(CONF_NOTICE_DAYS, 30),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_DURATION_MONTHS,
                default=current.get(CONF_DURATION_MONTHS, 12),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_AUTO_RENEW,
                default=current.get(CONF_AUTO_RENEW, True),
            ): selector.BooleanSelector()
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
            step_id="user",
            data_schema=_build_user_schema(user_input),
            errors=errors,
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
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                from datetime import date

                date.fromisoformat(user_input[CONF_START_DATE])
            except ValueError:
                errors["base"] = "invalid_date"

            if not errors:
                return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=_build_options_schema(current if user_input is None else user_input),
            errors=errors,
        )
