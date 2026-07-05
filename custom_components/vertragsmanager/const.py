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

CATEGORIES = [
    "Handy",
    "Strom",
    "Gas",
    "Internet",
    "Miete",
    "Versicherung",
    "Streaming",
    "Sonstiges",
]

CYCLES = ["monatlich", "jährlich"]

PLATFORMS = ["sensor"]
