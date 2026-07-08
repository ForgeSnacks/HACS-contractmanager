"""Tests für Config Flow."""
from __future__ import annotations

from homeassistant import data_entry_flow
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.vertragsmanager.const import DOMAIN


async def test_config_flow_success(hass: HomeAssistant) -> None:
    """Test successful config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "user"},
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "name": "Testvertrag",
            "category": "Handy",
            "provider": "TestProvider",
            "cost": 29.99,
            "cycle": "monatlich",
            "start_date": "2024-01-01",
            "notice_days": 30,
            "duration_months": 12,
            "auto_renew": True,
        },
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Testvertrag"
    assert result["data"]["name"] == "Testvertrag"


async def test_config_flow_invalid_date(hass: HomeAssistant) -> None:
    """Test invalid date in config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "user"},
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "name": "Testvertrag",
            "category": "Handy",
            "provider": "TestProvider",
            "cost": 29.99,
            "cycle": "monatlich",
            "start_date": "invalid-date",
            "notice_days": 30,
            "duration_months": 12,
            "auto_renew": True,
        },
    )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "invalid_date"
