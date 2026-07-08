"""Sensoren für Vertragsmanager."""
from __future__ import annotations

from datetime import date

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_NAME,
    DOMAIN,
)
from .coordinator import (
    VertragData,
    VertragsmanagerCoordinator,
    _calc_deadline,
    _calc_next_renewal,
)

SUMMARY_UNIQUE_ID = "vertragsmanager_gesamtkosten"


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Sensor für diesen Vertrag anlegen + Gesamtkosten-Sensor."""
    coordinator: VertragsmanagerCoordinator = entry.runtime_data.coordinator

    async_add_entities([VertragSensorEntity(coordinator, entry.entry_id)])

    # Gesamtkosten-Sensor nur einmal hinzufügen
    summary_key = f"{DOMAIN}_summary_added"
    if not hass.data.get(summary_key):
        async_add_entities([GesamtkostenSensorEntity(coordinator)])
        hass.data[summary_key] = True


class VertragSensorEntity(CoordinatorEntity, SensorEntity):
    """Repräsentiert einen einzelnen Vertrag."""

    _attr_icon = "mdi:file-document-outline"
    _attr_native_unit_of_measurement = "Tage"

    def __init__(self, coordinator: VertragsmanagerCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_unique_id = f"{DOMAIN}_{entry_id}"
        self._attr_translation_key = "vertrag"

    @property
    def _contract(self) -> VertragData | None:
        coordinator: VertragsmanagerCoordinator = self.coordinator
        return coordinator.data.get_contract(self._entry_id)

    @property
    def native_value(self) -> int | None:
        contract = self._contract
        if not contract:
            return None
        today = date.today()
        start = date.fromisoformat(contract.start_date)
        renewal = _calc_next_renewal(start, contract.duration_months, today)
        deadline = _calc_deadline(renewal, contract.notice_days)
        return (deadline - today).days

    @property
    def name(self) -> str:
        contract = self._contract
        return contract.name if contract else "Vertrag"

    @property
    def device_info(self) -> DeviceInfo:
        """Gibt Device-Info für diesen Vertrag zurück."""
        contract = self._contract
        if not contract:
            return DeviceInfo(identifiers={(DOMAIN, self._entry_id)})

        # configuration_url muss vollständige URL sein
        hass = self.coordinator.hass
        base_url = hass.config.external_url or hass.config.internal_url
        config_url = f"{base_url}/vertragsmanager" if base_url else None

        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name=contract.name,
            manufacturer=contract.provider,
            model=contract.category,
            serial_number=contract.contract_number or self._entry_id,
            sw_version="0.7.0",
            configuration_url=config_url,
        )

    @property
    def extra_state_attributes(self) -> dict | None:
        contract = self._contract
        if not contract:
            return None

        today = date.today()
        start = date.fromisoformat(contract.start_date)
        renewal = _calc_next_renewal(start, contract.duration_months, today)
        deadline = _calc_deadline(renewal, contract.notice_days)

        return {
            "kategorie": contract.category,
            "anbieter": contract.provider,
            "kosten": contract.cost,
            "zyklus": contract.cycle,
            "monatliche_kosten": contract.monthly_cost,
            "vertragsstart": contract.start_date,
            "kündigungsfrist_tage": contract.notice_days,
            "laufzeit_monate": contract.duration_months,
            "nächste_verlängerung": renewal.isoformat(),
            "kündigungsfrist_datum": deadline.isoformat(),
            "automatische_verlängerung": contract.auto_renew,
            "vertragsnummer": contract.contract_number,
            "kundennummer": contract.customer_number,
            "kündigungsfrist_text": contract.notice_period_text,
            "abbuchungstag": contract.payment_day,
            "notizen": contract.notes,
            "portal_url": contract.portal_url,
            "email": contract.email,
            "telefon": contract.phone,
        }


class GesamtkostenSensorEntity(CoordinatorEntity, SensorEntity):
    """Aggregiert die monatlichen Kosten aller Verträge."""

    _attr_icon = "mdi:cash-multiple"
    _attr_native_unit_of_measurement = "EUR"
    _attr_name = "Vertragsmanager Gesamtkosten"
    _attr_unique_id = SUMMARY_UNIQUE_ID

    def __init__(self, coordinator: VertragsmanagerCoordinator) -> None:
        super().__init__(coordinator)

    @property
    def native_value(self) -> float:
        coordinator: VertragsmanagerCoordinator = self.coordinator
        return coordinator.data.total_monthly_cost

    @property
    def extra_state_attributes(self) -> dict:
        coordinator: VertragsmanagerCoordinator = self.coordinator
        return {
            "anzahl_verträge": coordinator.data.contract_count,
            "verträge": [c.name for c in coordinator.data.contracts.values()],
        }
