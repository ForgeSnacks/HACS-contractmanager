"""Sensoren für Vertragsmanager."""
from __future__ import annotations

from datetime import date, timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_AUTO_RENEW,
    CONF_CATEGORY,
    CONF_CONTRACT_NUMBER,
    CONF_COST,
    CONF_CUSTOMER_NUMBER,
    CONF_CYCLE,
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
    CONF_START_DATE,
    DOMAIN,
)

SUMMARY_UNIQUE_ID = "vertragsmanager_gesamtkosten"


def _add_months(source: date, months: int) -> date:
    month = source.month - 1 + months
    year = source.year + month // 12
    month = month % 12 + 1
    day = min(
        source.day,
        [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
         31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1],
    )
    return date(year, month, day)


def _calc_next_renewal(start: date, duration_months: int, today: date) -> date:
    renewal = _add_months(start, duration_months)
    while renewal < today:
        renewal = _add_months(renewal, duration_months)
    return renewal


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Sensor für diesen Vertrag anlegen + Gesamtkosten-Sensor aktualisieren/anlegen."""
    data = {**entry.data, **entry.options}
    async_add_entities([VertragSensor(entry, data)])

    hass.data.setdefault(DOMAIN + "_summary_added", False)
    if not hass.data[DOMAIN + "_summary_added"]:
        async_add_entities([GesamtkostenSensor(hass)])
        hass.data[DOMAIN + "_summary_added"] = True


class VertragSensor(SensorEntity):
    """Repräsentiert einen einzelnen Vertrag."""

    _attr_icon = "mdi:file-document-outline"
    _attr_native_unit_of_measurement = "Tage"

    def __init__(self, entry: ConfigEntry, data: dict) -> None:
        self._entry = entry
        self._data = data
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}"
        self._attr_name = data[CONF_NAME]

    @property
    def native_value(self):
        today = date.today()
        start = date.fromisoformat(self._data[CONF_START_DATE])
        renewal = _calc_next_renewal(start, int(self._data[CONF_DURATION_MONTHS]), today)
        deadline = renewal - timedelta(days=int(self._data[CONF_NOTICE_DAYS]))
        return (deadline - today).days

    @property
    def extra_state_attributes(self):
        today = date.today()
        start = date.fromisoformat(self._data[CONF_START_DATE])
        renewal = _calc_next_renewal(start, int(self._data[CONF_DURATION_MONTHS]), today)
        deadline = renewal - timedelta(days=int(self._data[CONF_NOTICE_DAYS]))
        monthly_cost = float(self._data[CONF_COST])
        if self._data[CONF_CYCLE] == "jährlich":
            monthly_cost = monthly_cost / 12
        return {
            "kategorie": self._data.get(CONF_CATEGORY),
            "anbieter": self._data.get(CONF_PROVIDER),
            "kosten": self._data.get(CONF_COST),
            "zyklus": self._data.get(CONF_CYCLE),
            "monatliche_kosten": round(monthly_cost, 2),
            "vertragsstart": self._data.get(CONF_START_DATE),
            "kündigungsfrist_tage": self._data.get(CONF_NOTICE_DAYS),
            "laufzeit_monate": self._data.get(CONF_DURATION_MONTHS),
            "nächste_verlängerung": renewal.isoformat(),
            "kündigungsfrist_datum": deadline.isoformat(),
            "automatische_verlängerung": self._data.get(CONF_AUTO_RENEW),
            "vertragsnummer": self._data.get(CONF_CONTRACT_NUMBER),
            "kundennummer": self._data.get(CONF_CUSTOMER_NUMBER),
            "kündigungsfrist_text": self._data.get(CONF_NOTICE_PERIOD_TEXT),
            "abbuchungstag": self._data.get(CONF_PAYMENT_DAY),
            "notizen": self._data.get(CONF_NOTES),
            "portal_url": self._data.get(CONF_PORTAL_URL),
            "email": self._data.get(CONF_EMAIL),
            "telefon": self._data.get(CONF_PHONE),
        }


class GesamtkostenSensor(SensorEntity):
    """Aggregiert die monatlichen Kosten aller Verträge."""

    _attr_icon = "mdi:cash-multiple"
    _attr_native_unit_of_measurement = "EUR"
    _attr_name = "Vertragsmanager Gesamtkosten"

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._attr_unique_id = SUMMARY_UNIQUE_ID

    @property
    def native_value(self):
        total = 0.0
        for entry in self._hass.config_entries.async_entries(DOMAIN):
            data = {**entry.data, **entry.options}
            if not data:
                continue
            cost = float(data.get(CONF_COST, 0))
            if data.get(CONF_CYCLE) == "jährlich":
                cost = cost / 12
            total += cost
        return round(total, 2)

    @property
    def extra_state_attributes(self):
        verträge = []
        for entry in self._hass.config_entries.async_entries(DOMAIN):
            data = {**entry.data, **entry.options}
            if data:
                verträge.append(data.get(CONF_NAME))
        return {"anzahl_verträge": len(verträge), "verträge": verträge}


