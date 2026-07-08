"""Tests für Sensor Entities."""
from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_registry import EntityRegistry

from custom_components.vertragsmanager.const import DOMAIN
from custom_components.vertragsmanager.coordinator import (
    VertragsmanagerCoordinator,
    VertragsmanagerData,
    VertragData,
)


async def test_vertrag_sensor_entity(hass: HomeAssistant) -> None:
    """Test VertragSensorEntity."""
    coordinator = VertragsmanagerCoordinator(hass)

    contract_data = {
        "name": "Testvertrag",
        "category": "Handy",
        "provider": "TestProvider",
        "cost": 29.99,
        "cycle": "monatlich",
        "start_date": "2024-01-01",
        "notice_days": 30,
        "duration_months": 12,
        "auto_renew": True,
    }

    coordinator.update_contract("entry_123", contract_data)
    coordinator.async_refresh()

    # Setup entity
    from custom_components.vertragsmanager.sensor import VertragSensorEntity

    entity = VertragSensorEntity(coordinator, "entry_123")

    # Test properties
    assert entity.name == "Testvertrag"
    assert entity.native_unit_of_measurement == "Tage"

    # Test attributes
    attrs = entity.extra_state_attributes
    assert attrs is not None
    assert attrs["kategorie"] == "Handy"
    assert attrs["anbieter"] == "TestProvider"
    assert attrs["monatliche_kosten"] == 29.99


async def test_gesamtkosten_sensor_entity(hass: HomeAssistant) -> None:
    """Test GesamtkostenSensorEntity."""
    coordinator = VertragsmanagerCoordinator(hass)

    coordinator.update_contract(
        "entry_1",
        {
            "name": "Vertrag 1",
            "category": "Handy",
            "provider": "Provider1",
            "cost": 29.99,
            "cycle": "monatlich",
            "start_date": "2024-01-01",
            "notice_days": 30,
            "duration_months": 12,
            "auto_renew": True,
        },
    )

    coordinator.update_contract(
        "entry_2",
        {
            "name": "Vertrag 2",
            "category": "Strom",
            "provider": "Provider2",
            "cost": 360.0,
            "cycle": "jährlich",
            "start_date": "2024-01-01",
            "notice_days": 30,
            "duration_months": 12,
            "auto_renew": True,
        },
    )

    coordinator.async_refresh()

    from custom_components.vertragsmanager.sensor import GesamtkostenSensorEntity

    entity = GesamtkostenSensorEntity(coordinator)

    assert entity.native_value == 59.99
    assert entity.native_unit_of_measurement == "EUR"

    attrs = entity.extra_state_attributes
    assert attrs["anzahl_verträge"] == 2
