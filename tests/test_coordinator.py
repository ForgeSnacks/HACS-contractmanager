"""Tests für Coordinator."""
from __future__ import annotations

from datetime import date

from custom_components.vertragsmanager.coordinator import (
    VertragData,
    VertragsmanagerCoordinator,
    VertragsmanagerData,
    _add_months,
    _calc_deadline,
    _calc_next_renewal,
)


def test_coordinator_data_structure() -> None:
    """Test coordinator data structure."""
    data = VertragsmanagerData()
    assert data.contracts == {}
    assert data.total_monthly_cost == 0.0
    assert data.contract_count == 0


def test_vertrag_data_monthly_cost_monthly() -> None:
    """Test monthly cost calculation for monthly cycle."""
    contract = VertragData(
        entry_id="test_id",
        name="Test",
        category="Handy",
        provider="Provider",
        cost=29.99,
        cycle="monatlich",
        start_date="2024-01-01",
        notice_days=30,
        duration_months=12,
        auto_renew=True,
    )
    assert contract.monthly_cost == 29.99


def test_vertrag_data_monthly_cost_yearly() -> None:
    """Test monthly cost calculation for yearly cycle."""
    contract = VertragData(
        entry_id="test_id",
        name="Test",
        category="Strom",
        provider="Provider",
        cost=360.0,
        cycle="jährlich",
        start_date="2024-01-01",
        notice_days=30,
        duration_months=12,
        auto_renew=True,
    )
    assert contract.monthly_cost == 30.0


def test_coordinator_update_contract() -> None:
    """Test updating contract in coordinator (mocked hass)."""
    # Mock hass object
    hass_mock = type("HomeAssistantMock", (), {"data": {}})()
    coordinator = VertragsmanagerCoordinator(hass_mock)  # type: ignore

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
