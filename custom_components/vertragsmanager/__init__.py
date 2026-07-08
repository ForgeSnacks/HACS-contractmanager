"""Vertragsmanager Integration für Home Assistant."""
from __future__ import annotations

from datetime import date

import voluptuous as vol

from homeassistant.components import frontend
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import (
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
    DEFAULT_PAGE,
    DEFAULT_SHOW_IN_SIDEBAR,
    DOMAIN,
    PANEL_ICON,
    PANEL_NAME,
    PANEL_TITLE,
    PANEL_URL_PATH,
    PLATFORMS,
)

SERVICE_CREATE_CONTRACT = "create_contract"


CREATE_CONTRACT_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_CATEGORY): cv.string,
        vol.Required(CONF_PROVIDER): cv.string,
        vol.Required(CONF_COST): vol.Coerce(float),
        vol.Required(CONF_CYCLE): cv.string,
        vol.Required(CONF_START_DATE): cv.string,
        vol.Required(CONF_NOTICE_DAYS): vol.Coerce(int),
        vol.Required(CONF_DURATION_MONTHS): vol.Coerce(int),
        vol.Required(CONF_AUTO_RENEW, default=True): cv.boolean,
        vol.Optional(CONF_CONTRACT_NUMBER, default=""): cv.string,
        vol.Optional(CONF_CUSTOMER_NUMBER, default=""): cv.string,
        vol.Optional(CONF_NOTICE_PERIOD_TEXT, default=""): cv.string,
        vol.Optional(CONF_PAYMENT_DAY, default=""): cv.string,
        vol.Optional(CONF_NOTES, default=""): cv.string,
        vol.Optional(CONF_PORTAL_URL, default=""): cv.string,
        vol.Optional(CONF_EMAIL, default=""): cv.string,
        vol.Optional(CONF_PHONE, default=""): cv.string,
    }
)


async def _register_panel(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Registriert das Frontend-Panel."""
    options = entry.options or {}
    show_in_sidebar = options.get(CONF_SHOW_IN_SIDEBAR, DEFAULT_SHOW_IN_SIDEBAR)
    default_page = options.get(CONF_DEFAULT_PAGE, DEFAULT_PAGE)

    frontend.async_register_built_in_panel(
        hass,
        component_name="custom",
        sidebar_title=PANEL_TITLE if show_in_sidebar else None,
        sidebar_icon=PANEL_ICON if show_in_sidebar else None,
        frontend_url_path=PANEL_URL_PATH,
        config={
            "_panel_custom": {
                "name": PANEL_NAME,
                "embed_iframe": False,
                "trust_external": False,
                "js_url": f"/api/vertragsmanager/panel.js?page={default_page}",
            }
        },
        require_admin=False,
    )


async def _unregister_panel(hass: HomeAssistant) -> None:
    """Versucht vorhandenes Panel zu entfernen."""
    panels = hass.data.get("frontend_panels")
    if panels and PANEL_URL_PATH in panels:
        panels.pop(PANEL_URL_PATH, None)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up Vertragsmanager."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a Vertragsmanager config entry (= ein Vertrag)."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_listener))

    if not hass.services.has_service(DOMAIN, SERVICE_CREATE_CONTRACT):
        async def handle_create_contract(call: ServiceCall) -> None:
            data = dict(call.data)
            date.fromisoformat(data[CONF_START_DATE])

            await hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": "user"},
                data=data,
            )

        hass.services.async_register(
            DOMAIN,
            SERVICE_CREATE_CONTRACT,
            handle_create_contract,
            schema=CREATE_CONTRACT_SCHEMA,
        )

    if not hass.data.get(f"{DOMAIN}_panel_registered"):
        await _register_panel(hass, entry)
        hass.data[f"{DOMAIN}_panel_registered"] = True

    return True


async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Bei Optionsänderung neu laden."""
    await _unregister_panel(hass)
    hass.data[f"{DOMAIN}_panel_registered"] = False
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Config entry entladen."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    if not hass.config_entries.async_entries(DOMAIN):
        if hass.services.has_service(DOMAIN, SERVICE_CREATE_CONTRACT):
            hass.services.async_remove(DOMAIN, SERVICE_CREATE_CONTRACT)
        await _unregister_panel(hass)
        hass.data[f"{DOMAIN}_panel_registered"] = False

    return unload_ok
