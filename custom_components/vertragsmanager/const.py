"""Konstanten für Vertragsmanager."""
from typing import Final

DOMAIN: Final = "vertragsmanager"

CONF_NAME: Final = "name"
CONF_CATEGORY: Final = "category"
CONF_PROVIDER: Final = "provider"
CONF_COST: Final = "cost"
CONF_CYCLE: Final = "cycle"
CONF_START_DATE: Final = "start_date"
CONF_NOTICE_DAYS: Final = "notice_days"
CONF_DURATION_MONTHS: Final = "duration_months"
CONF_AUTO_RENEW: Final = "auto_renew"

CONF_CONTRACT_NUMBER: Final = "contract_number"
CONF_CUSTOMER_NUMBER: Final = "customer_number"
CONF_NOTICE_PERIOD_TEXT: Final = "notice_period_text"
CONF_PAYMENT_DAY: Final = "payment_day"
CONF_NOTES: Final = "notes"
CONF_PORTAL_URL: Final = "portal_url"
CONF_EMAIL: Final = "email"
CONF_PHONE: Final = "phone"

CONF_SHOW_IN_SIDEBAR: Final = "show_in_sidebar"
CONF_DEFAULT_PAGE: Final = "default_page"

DEFAULT_SHOW_IN_SIDEBAR: Final = True
DEFAULT_PAGE: Final = "overview"

CATEGORIES: Final[list[str]] = [
    "Handy",
    "Strom",
    "Gas",
    "Internet",
    "Miete",
    "Versicherung",
    "Streaming",
    "Fitness",
    "Software",
    "Sonstiges",
]

CYCLES: Final[list[str]] = ["monatlich", "jährlich"]

PAGES: Final[list[dict[str, str]]] = [
    {"label": "Übersicht", "value": "overview"},
    {"label": "Alle Verträge", "value": "contracts"},
    {"label": "Kosten", "value": "costs"},
    {"label": "Fristen", "value": "deadlines"},
    {"label": "Vertrag hinzufügen", "value": "add"}
]

PLATFORMS: Final[list[str]] = ["sensor"]

PANEL_URL_PATH: Final = "vertragsmanager"
PANEL_TITLE: Final = "Vertragsmanager"
PANEL_ICON: Final = "mdi:file-document-multiple-outline"
PANEL_COMPONENT_NAME: Final = "custom"
PANEL_NAME: Final = "vertragsmanager-panel"
PANEL_JS_URL: Final = "/api/vertragsmanager/frontend/panel.js"
