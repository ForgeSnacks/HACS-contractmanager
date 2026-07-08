"""Vertragsmanager Integration für Home Assistant."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import voluptuous as vol

from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
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
    PANEL_COMPONENT_NAME,
    PANEL_ICON,
    PANEL_JS_URL,
    PANEL_NAME,
    PANEL_TITLE,
    PANEL_URL_PATH,
    PLATFORMS,
)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

SERVICE_CREATE_CONTRACT = "create_contract"
STATIC_FRONTEND_PATH = "/api/vertragsmanager/frontend"
STATIC_REGISTERED_KEY = f"{DOMAIN}_static_registered"
PANEL_REGISTERED_KEY = f"{DOMAIN}_panel_registered"

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


async def _ensure_static_path(hass: HomeAssistant) -> None:
    """Statische Frontend-Dateien registrieren."""
    if hass.data.get(STATIC_REGISTERED_KEY):
        return

    frontend_dir = Path(__file__).parent / "frontend"

    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                STATIC_FRONTEND_PATH,
                str(frontend_dir),
                cache_headers=False,
            )
        ]
    )

    hass.data[STATIC_REGISTERED_KEY] = True


def _remove_panel_if_exists(hass: HomeAssistant) -> None:
    """Bereits vorhandenes Panel entfernen."""
    panels = hass.data.get("frontend_panels")
    if panels and PANEL_URL_PATH in panels:
        panels.pop(PANEL_URL_PATH, None)


async def _register_panel(hass: HomeAssistant) -> None:
    """Panel anhand des ersten Config Entries registrieren."""
    entries = hass.config_entries.async_entries(DOMAIN)
    if not entries:
        return

    primary_entry = entries[0]
    options = primary_entry.options or {}
    show_in_sidebar = options.get(CONF_SHOW_IN_SIDEBAR, DEFAULT_SHOW_IN_SIDEBAR)
    default_page = options.get(CONF_DEFAULT_PAGE, DEFAULT_PAGE)

    _remove_panel_if_exists(hass)

    frontend.async_register_built_in_panel(
        hass,
        component_name=PANEL_COMPONENT_NAME,
        sidebar_title=PANEL_TITLE if show_in_sidebar else None,
        sidebar_icon=PANEL_ICON if show_in_sidebar else None,
        frontend_url_path=PANEL_URL_PATH,
        config={
            "_panel_custom": {
                "name": PANEL_NAME,
                "embed_iframe": False,
                "trust_external": False,
                "js_url": f"{PANEL_JS_URL}?v=0.5.0&page={default_page}",
            }
        },
        require_admin=False,
    )

    hass.data[PANEL_REGISTERED_KEY] = True


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Globale Initialisierung."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Ein Vertrags-Config-Entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {**entry.data, **entry.options}

    await _ensure_static_path(hass)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_listener))

    if not hass.services.has_service(DOMAIN, SERVICE_CREATE_CONTRACT):

        async def handle_create_contract(call: ServiceCall) -> None:
            data = dict(call.data)
            date.fromisoformat(data[CONF_START_DATE])

            result = await hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": "user"},
                data=data,
            )

            if result["type"] != "create_entry":
                raise ValueError(f"Vertrag konnte nicht angelegt werden: {result}")

        hass.services.async_register(
            DOMAIN,
            SERVICE_CREATE_CONTRACT,
            handle_create_contract,
            schema=CREATE_CONTRACT_SCHEMA,
        )

    await _register_panel(hass)
    return True


async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Bei Optionen: Entry neu laden und Panel neu registrieren."""
    await hass.config_entries.async_reload(entry.entry_id)
    await _register_panel(hass)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Entry entladen."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    remaining = hass.config_entries.async_entries(DOMAIN)

    if not remaining:
        if hass.services.has_service(DOMAIN, SERVICE_CREATE_CONTRACT):
            hass.services.async_remove(DOMAIN, SERVICE_CREATE_CONTRACT)
        _remove_panel_if_exists(hass)
        hass.data[PANEL_REGISTERED_KEY] = False
    else:
        await _register_panel(hass)

    return unload_ok

