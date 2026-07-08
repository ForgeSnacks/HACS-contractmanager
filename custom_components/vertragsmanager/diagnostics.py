"""Diagnostics für Vertragsmanager."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data.coordinator

    return {
        "entry": {
            "entry_id": entry.entry_id,
            "title": entry.title,
            "data": dict(entry.data),
            "options": dict(entry.options),
        },
        "coordinator_data": {
            "contract_count": coordinator.data.contract_count,
            "total_monthly_cost": coordinator.data.total_monthly_cost,
            "contracts": [
                {
                    "entry_id": c.entry_id,
                    "name": c.name,
                    "category": c.category,
                    "provider": c.provider,
                    "monthly_cost": c.monthly_cost,
                }
                for c in coordinator.data.contracts.values()
            ],
        },
    }
