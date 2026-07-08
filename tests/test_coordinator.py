"""Tests für Coordinator."""
from __future__ import annotations

from datetime import date

from homeassistant.core import HomeAssistant

from custom_components.vertragsmanager.coordinator import (
    VertragData,
    VertragsmanagerCoordinator,
    _add_months,
    _calc_deadline,
    _calc_next_renewal,
    VertragsmanagerData,
)


async def test_coordinator_add_contract(hass: HomeAssistant) -> None:
    """Test adding contract to coordinator."""
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
        "contract_number": "12345",
    }

    coordinator.update_contract("entry_123", contract_data)

    contract = coordinator.data.get_contract("entry_123")
    assert contract is not None
    assert contract.name == "Testvertrag"
    assert contract.monthly_cost == 29.99


async def test_coordinator_total_cost(hass: HomeAssistant) -> None:
    """Test total monthly cost calculation."""
    coordinator = VertragsmanagerCoordinator(hass)

    # Add two contracts
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

    assert coordinator.data.total_monthly_cost == 59.99  # 29.99 + 30.00


def test_add_months() -> None:
    """Test month addition."""
    start = date(2024, 1, 15)
    result = _add_months(start, 12)
    assert result == date(2025, 1, 15)


def test_calc_next_renewal() -> None:
    """Test renewal calculation."""
    start = date(2024, 1, 1)
    today = date(2026, 7, 8)
    renewal = _calc_next_renewal(start, 12, today)
    assert renewal == date(2027, 1, 1)


def test_calc_deadline() -> None:
    """Test deadline calculation."""
    renewal = date(2027, 1, 1)
    deadline = _calc_deadline(renewal, 30)
    assert deadline == date(2026, 12, 2)
