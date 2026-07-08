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
    """Sensoren für diesen Vertrag anlegen + Gesamtkosten-Sensor."""
    coordinator: VertragsmanagerCoordinator = entry.runtime_data.coordinator

    # Alle Sensoren für diesen Vertrag
    async_add_entities([
        VertragLaufzeitSensorEntity(coordinator, entry.entry_id),
        VertragPreisProMonatSensorEntity(coordinator, entry.entry_id),
        VertragBereitsGezahltSensorEntity(coordinator, entry.entry_id),
        VertragNochZuZahlenSensorEntity(coordinator, entry.entry_id),
    ])

    # Gesamtkosten-Sensor nur einmal hinzufügen
    summary_key = f"{DOMAIN}_summary_added"
    if not hass.data.get(summary_key):
        async_add_entities([GesamtkostenSensorEntity(coordinator)])
        hass.data[summary_key] = True


class VertragLaufzeitSensorEntity(CoordinatorEntity, SensorEntity):
    """Repräsentiert die verbleibende Kündigungsfrist in Tagen."""

    _attr_icon = "mdi:file-document-outline"
    _attr_native_unit_of_measurement = "Tage"
    _attr_translation_key = "vertrag"

    def __init__(self, coordinator: VertragsmanagerCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_unique_id = f"{DOMAIN}_{entry_id}"

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
        return f"{contract.name} Kündigungsfrist" if contract else "Vertrag"

    @property
    def device_info(self) -> DeviceInfo:
        """Gibt Device-Info für diesen Vertrag zurück."""
        return _get_device_info(self.coordinator, self._entry_id)

    @property
    def extra_state_attributes(self) -> dict | None:
        return _get_contract_attributes(self._contract)


class VertragPreisProMonatSensorEntity(CoordinatorEntity, SensorEntity):
    """Repräsentiert die monatlichen Kosten des Vertrags."""

    _attr_icon = "mdi:cash-multiple"
    _attr_native_unit_of_measurement = "EUR"
    _attr_translation_key = "vertrag"

    def __init__(self, coordinator: VertragsmanagerCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_monatskosten"

    @property
    def _contract(self) -> VertragData | None:
        coordinator: VertragsmanagerCoordinator = self.coordinator
        return coordinator.data.get_contract(self._entry_id)

    @property
    def native_value(self) -> float | None:
        contract = self._contract
        if not contract:
            return None
        return contract.monthly_cost

    @property
    def name(self) -> str:
        contract = self._contract
        return f"{contract.name} monatlich" if contract else "Vertrag"

    @property
    def device_info(self) -> DeviceInfo:
        return _get_device_info(self.coordinator, self._entry_id)

    @property
    def extra_state_attributes(self) -> dict | None:
        return _get_contract_attributes(self._contract)


class VertragBereitsGezahltSensorEntity(CoordinatorEntity, SensorEntity):
    """Berechnet bereits gezahlte Kosten seit Vertragsbeginn."""

    _attr_icon = "mdi:cash-check"
    _attr_native_unit_of_measurement = "EUR"
    _attr_translation_key = "vertrag"

    def __init__(self, coordinator: VertragsmanagerCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_bereits_gezahlt"

    @property
    def _contract(self) -> VertragData | None:
        coordinator: VertragsmanagerCoordinator = self.coordinator
        return coordinator.data.get_contract(self._entry_id)

    @property
    def native_value(self) -> float | None:
        contract = self._contract
        if not contract:
            return None
        
        today = date.today()
        start = date.fromisoformat(contract.start_date)
        
        # Bereite bereits verstrichene Monate
        months_passed = (today.year - start.year) * 12 + (today.month - start.month)
        
        # Wenn Tag im aktuellen Monat noch nicht erreicht, ein Monat weniger
        if today.day < start.day:
            months_passed -= 1
        
        # Nicht weniger als 0
        months_passed = max(0, months_passed)
        
        # Kosten berechnen
        return round(months_passed * contract.monthly_cost, 2)

    @property
    def name(self) -> str:
        contract = self._contract
        return f"{contract.name} bereits gezahlt" if contract else "Vertrag"

    @property
    def device_info(self) -> DeviceInfo:
        return _get_device_info(self.coordinator, self._entry_id)

    @property
    def extra_state_attributes(self) -> dict | None:
        return _get_contract_attributes(self._contract)


class VertragNochZuZahlenSensorEntity(CoordinatorEntity, SensorEntity):
    """Berechnet noch zu zahlende Kosten bis Ende der Mindestvertragslaufzeit."""

    _attr_icon = "mdi:cash-minus"
    _attr_native_unit_of_measurement = "EUR"
    _attr_translation_key = "vertrag"

    def __init__(self, coordinator: VertragsmanagerCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_noch_zu_zahlen"

    @property
    def _contract(self) -> VertragData | None:
        coordinator: VertragsmanagerCoordinator = self.coordinator
        return coordinator.data.get_contract(self._entry_id)

    @property
    def native_value(self) -> float | None:
        contract = self._contract
        if not contract:
            return None
        
        today = date.today()
        start = date.fromisoformat(contract.start_date)
        
        # Nächstes Verlängerungsdatum
        renewal = _calc_next_renewal(start, contract.duration_months, today)
        
        # Monate bis zur Verlängerung
        months_until_renewal = (renewal.year - today.year) * 12 + (renewal.month - today.month)
        
        # Wenn Tag im aktuellen Monat noch nicht erreicht, ein Monat weniger
        if renewal.day < today.day:
            months_until_renewal -= 1
        
        # Nicht weniger als 0
        months_until_renewal = max(0, months_until_renewal)
        
        # Kosten berechnen
        return round(months_until_renewal * contract.monthly_cost, 2)

    @property
    def name(self) -> str:
        contract = self._contract
        return f"{contract.name} noch zu zahlen" if contract else "Vertrag"

    @property
    def device_info(self) -> DeviceInfo:
        return _get_device_info(self.coordinator, self._entry_id)

    @property
    def extra_state_attributes(self) -> dict | None:
        return _get_contract_attributes(self._contract)


def _get_device_info(coordinator: VertragsmanagerCoordinator, entry_id: str) -> DeviceInfo:
    """Hilfsfunktion für Device-Info."""
    contract = coordinator.data.get_contract(entry_id)
    
    if not contract:
        return DeviceInfo(identifiers={(DOMAIN, entry_id)})

    # configuration_url muss vollständige URL sein
    hass = coordinator.hass
    base_url = hass.config.external_url or hass.config.internal_url
    config_url = f"{base_url}/vertragsmanager" if base_url else None

    # Seriennummer kürzen
    serial = contract.contract_number[:20] if contract.contract_number and len(contract.contract_number) > 20 else contract.contract_number

    return DeviceInfo(
        identifiers={(DOMAIN, entry_id)},
        name=contract.name,
        manufacturer=contract.provider,
        model=contract.category,
        serial_number=serial or None,
        sw_version="0.7.0",
        configuration_url=config_url,
    )


def _get_contract_attributes(contract: VertragData | None) -> dict | None:
    """Hilfsfunktion für Attribute ohne Umlaute."""
    if not contract:
        return None

    today = date.today()
    start = date.fromisoformat(contract.start_date)
    renewal = _calc_next_renewal(start, contract.duration_months, today)
    deadline = _calc_deadline(renewal, contract.notice_days)

    return {
        "category": contract.category,
        "provider": contract.provider,
        "cost": contract.cost,
        "cycle": contract.cycle,
        "monthly_cost": contract.monthly_cost,
        "start_date": contract.start_date,
        "notice_days": contract.notice_days,
        "duration_months": contract.duration_months,
        "next_renewal": renewal.isoformat(),
        "deadline_date": deadline.isoformat(),
        "auto_renew": contract.auto_renew,
        "contract_number": contract.contract_number,
        "customer_number": contract.customer_number,
        "notice_period_text": contract.notice_period_text,
        "payment_day": contract.payment_day,
        "notes": contract.notes,
        "portal_url": contract.portal_url,
        "email": contract.email,
        "phone": contract.phone,
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
