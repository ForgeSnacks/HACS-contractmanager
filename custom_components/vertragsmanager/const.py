"""Konstanten für Vertragsmanager."""

DOMAIN = "vertragsmanager"

CONF_NAME = "name"
CONF_CATEGORY = "category"
CONF_PROVIDER = "provider"
CONF_COST = "cost"
CONF_CYCLE = "cycle"
CONF_START_DATE = "start_date"
CONF_NOTICE_DAYS = "notice_days"
CONF_DURATION_MONTHS = "duration_months"
CONF_AUTO_RENEW = "auto_renew"

CONF_CONTRACT_NUMBER = "contract_number"
CONF_CUSTOMER_NUMBER = "customer_number"
CONF_NOTICE_PERIOD_TEXT = "notice_period_text"
CONF_PAYMENT_DAY = "payment_day"
CONF_NOTES = "notes"
CONF_PORTAL_URL = "portal_url"
CONF_EMAIL = "email"
CONF_PHONE = "phone"

CONF_SHOW_IN_SIDEBAR = "show_in_sidebar"
CONF_DEFAULT_PAGE = "default_page"

DEFAULT_SHOW_IN_SIDEBAR = True
DEFAULT_PAGE = "overview"

CATEGORIES = [
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

CYCLES = ["monatlich", "jährlich"]

PAGES = [
    {"label": "Übersicht", "value": "overview"},
    {"label": "Alle Verträge", "value": "contracts"},
    {"label": "Kosten", "value": "costs"},
    {"label": "Fristen", "value": "deadlines"},
    {"label": "Vertrag hinzufügen", "value": "add"}
]

PLATFORMS = ["sensor"]

PANEL_URL_PATH = "vertragsmanager"
PANEL_TITLE = "Vertragsmanager"
PANEL_ICON = "mdi:file-document-multiple-outline"
PANEL_COMPONENT_NAME = "custom"
PANEL_NAME = "vertragsmanager-panel"
PANEL_JS_URL = "/api/vertragsmanager/frontend/panel.js"
