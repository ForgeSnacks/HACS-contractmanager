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
    CONF_CONTRACT_NUMBER,
    CONF_COST,
    CONF_CUSTOMER_NUMBER,
    CONF_CYCLE,
    CONF_DEFAULT_PAGE,
    CONF_DURATION_MONTHS,
    CONF_EMAIL,
    CONF_NAME,
    CONF_NOTES,
    CONF_NOTICE_DAYS,
    CONF_NOTICE_PERIOD_TEXT,
    CONF_PAYMENT_DAY,
    CONF_PHONE,
    CONF_PORTAL_URL,
    CONF_PROVIDER,
    CONF_SHOW_IN_SIDEBAR,
    CONF_START_DATE,
    CYCLES,
    DEFAULT_PAGE,
    DEFAULT_SHOW_IN_SIDEBAR,
    DOMAIN,
    PAGES,
)


def _build_user_schema(user_input=None):
    user_input = user_input or {}

    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=user_input.get(CONF_NAME, vol.UNDEFINED)): selector.TextSelector(),
            vol.Required(CONF_CATEGORY, default=user_input.get(CONF_CATEGORY, CATEGORIES[-1])): selector.SelectSelector(
                selector.SelectSelectorConfig(options=CATEGORIES, mode=selector.SelectSelectorMode.DROPDOWN)
            ),
            vol.Required(CONF_PROVIDER, default=user_input.get(CONF_PROVIDER, vol.UNDEFINED)): selector.TextSelector(),
            vol.Required(CONF_COST, default=user_input.get(CONF_COST, vol.UNDEFINED)): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, step=0.01, mode=selector.NumberSelectorMode.BOX)
            ),
            vol.Required(CONF_CYCLE, default=user_input.get(CONF_CYCLE, CYCLES[0])): selector.SelectSelector(
                selector.SelectSelectorConfig(options=CYCLES, mode=selector.SelectSelectorMode.DROPDOWN)
            ),
            vol.Required(CONF_START_DATE, default=user_input.get(CONF_START_DATE, vol.UNDEFINED)): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.DATE)
            ),
            vol.Required(CONF_NOTICE_DAYS, default=user_input.get(CONF_NOTICE_DAYS, 30)): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, step=1, mode=selector.NumberSelectorMode.BOX)
            ),
            vol.Required(CONF_DURATION_MONTHS, default=user_input.get(CONF_DURATION_MONTHS, 12)): selector.NumberSelector(
                selector.NumberSelectorConfig(min=1, step=1, mode=selector.NumberSelectorMode.BOX)
            ),
            vol.Required(CONF_AUTO_RENEW, default=user_input.get(CONF_AUTO_RENEW, True)): selector.BooleanSelector(),
            vol.Optional(CONF_CONTRACT_NUMBER, default=user_input.get(CONF_CONTRACT_NUMBER, "")): selector.TextSelector(),
            vol.Optional(CONF_CUSTOMER_NUMBER, default=user_input.get(CONF_CUSTOMER_NUMBER, "")): selector.TextSelector(),
            vol.Optional(CONF_NOTICE_PERIOD_TEXT, default=user_input.get(CONF_NOTICE_PERIOD_TEXT, "")): selector.TextSelector(),
            vol.Optional(CONF_PAYMENT_DAY, default=user_input.get(CONF_PAYMENT_DAY, "")): selector.TextSelector(),
            vol.Optional(CONF_NOTES, default=user_input.get(CONF_NOTES, "")): selector.TextSelector(
                selector.TextSelectorConfig(multiline=True)
            ),
            vol.Optional(CONF_PORTAL_URL, default=user_input.get(CONF_PORTAL_URL, "")): selector.TextSelector(),
            vol.Optional(CONF_EMAIL, default=user_input.get(CONF_EMAIL, "")): selector.TextSelector(),
            vol.Optional(CONF_PHONE, default=user_input.get(CONF_PHONE, "")): selector.TextSelector(),
        }
    )


def _build_options_schema(current):
    return vol.Schema(
        {
            vol.Required(
                CONF_SHOW_IN_SIDEBAR,
                default=current.get(CONF_SHOW_IN_SIDEBAR, DEFAULT_SHOW_IN_SIDEBAR),
            ): selector.BooleanSelector(),
            vol.Required(
                CONF_DEFAULT_PAGE,
                default=current.get(CONF_DEFAULT_PAGE, DEFAULT_PAGE),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=PAGES,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(CONF_CATEGORY, default=current.get(CONF_CATEGORY, CATEGORIES[-1])): selector.SelectSelector(
                selector.SelectSelectorConfig(options=CATEGORIES, mode=selector.SelectSelectorMode.DROPDOWN)
            ),
            vol.Required(CONF_PROVIDER, default=current.get(CONF_PROVIDER, vol.UNDEFINED)): selector.TextSelector(),
            vol.Required(CONF_COST, default=current.get(CONF_COST, vol.UNDEFINED)): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, step=0.01, mode=selector.NumberSelectorMode.BOX)
            ),
            vol.Required(CONF_CYCLE, default=current.get(CONF_CYCLE, CYCLES[0])): selector.SelectSelector(
                selector.SelectSelectorConfig(options=CYCLES, mode=selector.SelectSelectorMode.DROPDOWN)
            ),
            vol.Required(CONF_START_DATE, default=current.get(CONF_START_DATE, vol.UNDEFINED)): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.DATE)
            ),
            vol.Required(CONF_NOTICE_DAYS, default=current.get(CONF_NOTICE_DAYS, 30)): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, step=1, mode=selector.NumberSelectorMode.BOX)
            ),
            vol.Required(CONF_DURATION_MONTHS, default=current.get(CONF_DURATION_MONTHS, 12)): selector.NumberSelector(
                selector.NumberSelectorConfig(min=1, step=1, mode=selector.NumberSelectorMode.BOX)
            ),
            vol.Required(CONF_AUTO_RENEW, default=current.get(CONF_AUTO_RENEW, True)): selector.BooleanSelector(),
            vol.Optional(CONF_CONTRACT_NUMBER, default=current.get(CONF_CONTRACT_NUMBER, "")): selector.TextSelector(),
            vol.Optional(CONF_CUSTOMER_NUMBER, default=current.get(CONF_CUSTOMER_NUMBER, "")): selector.TextSelector(),
            vol.Optional(CONF_NOTICE_PERIOD_TEXT, default=current.get(CONF_NOTICE_PERIOD_TEXT, "")): selector.TextSelector(),
            vol.Optional(CONF_PAYMENT_DAY, default=current.get(CONF_PAYMENT_DAY, "")): selector.TextSelector(),
            vol.Optional(CONF_NOTES, default=current.get(CONF_NOTES, "")): selector.TextSelector(
                selector.TextSelectorConfig(multiline=True)
            ),
            vol.Optional(CONF_PORTAL_URL, default=current.get(CONF_PORTAL_URL, "")): selector.TextSelector(),
            vol.Optional(CONF_EMAIL, default=current.get(CONF_EMAIL, "")): selector.TextSelector(),
            vol.Optional(CONF_PHONE, default=current.get(CONF_PHONE, "")): selector.TextSelector(),
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
    """Erlaubt das Bearbeiten eines bestehenden Vertrags und der Panel-Optionen."""

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
