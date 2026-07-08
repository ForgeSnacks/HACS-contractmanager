"""Repairs für Vertragsmanager."""
from __future__ import annotations

from datetime import date

from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir

from .const import DOMAIN
from .coordinator import VertragsmanagerData


async def async_process_repairs(hass: HomeAssistant, data: VertragsmanagerData) -> None:
    """Process and create repair issues for contracts with issues."""
    issue_registry = ir.async_get(hass)
    today = date.today()

    for contract in data.contracts.values():
        issues: list[str] = []

        # Check for invalid dates
        try:
            start = date.fromisoformat(contract.start_date)
            if start > today:
                issues.append("start_date_in_future")
        except ValueError:
            issues.append("invalid_start_date")

        # Check for negative notice days
        if contract.notice_days < 0:
            issues.append("negative_notice_days")

        # Check for invalid duration
        if contract.duration_months <= 0:
            issues.append("invalid_duration")

        # Create or remove issues
        for issue in issues:
            issue_id = f"{contract.entry_id}_{issue}"
            ir.async_get_or_create(
                domain=DOMAIN,
                issue_id=issue_id,
                severity=ir.IssueSeverity.WARNING,
                translation_key=issue,
                translation_placeholders={
                    "contract_name": contract.name,
                },
            )

        # Remove resolved issues
        existing_issues = list(ir.async_get(hass).issues.keys())
        for issue_key in existing_issues:
            if issue_key[0] == DOMAIN and issue_key[1].startswith(f"{contract.entry_id}_"):
                issue_id = issue_key[1]
                if issue_id not in [f"{contract.entry_id}_{i}" for i in issues]:
                    ir.async_delete_issue(hass, DOMAIN, issue_id)
