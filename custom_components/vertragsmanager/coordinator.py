"""DataUpdateCoordinator für Vertragsmanager."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

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


@dataclass
class VertragData:
    """Daten eines Vertrags."""

    entry_id: str
    name: str
    category: str
    provider: str
    cost: float
    cycle: str
    start_date: str
    notice_days: int
    duration_months: int
    auto_renew: bool
    contract_number: str = ""
    customer_number: str = ""
    notice_period_text: str = ""
    payment_day: str = ""
    notes: str = ""
    portal_url: str = ""
    email: str = ""
    phone: str = ""

    @property
    def monthly_cost(self) -> float:
        """Berechnet monatliche Kosten."""
        cost = self.cost
        if self.cycle == "jährlich":
            cost = cost / 12
        return round(cost, 2)


def _add_months(source: date, months: int) -> date:
    """Addiert Monate zu einem Datum."""
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
    """Berechnet nächstes Verlängerungsdatum."""
    renewal = _add_months(start, duration_months)
    while renewal < today:
        renewal = _add_months(renewal, duration_months)
    return renewal


def _calc_deadline(renewal: date, notice_days: int) -> date:
    """Berechnet Kündigungsfrist-Datum."""
    return renewal - timedelta(days=notice_days)


@dataclass
class VertragsmanagerData:
    """Gesamtdaten des Vertragsmanagers."""

    contracts: dict[str, VertragData] = field(default_factory=dict)

    @property
    def total_monthly_cost(self) -> float:
        """Summe aller monatlichen Kosten."""
        return round(sum(c.monthly_cost for c in self.contracts.values()), 2)

    @property
    def contract_count(self) -> int:
        """Anzahl der Verträge."""
        return len(self.contracts)

    def get_contract(self, entry_id: str) -> VertragData | None:
        """Holt einen Vertrag per ID."""
        return self.contracts.get(entry_id)

    def get_sorted_contracts(
        self, today: date
    ) -> list[tuple[VertragData, date, date]]:
        """
        Gibt alle Verträge sortiert nach Kündigungsfrist zurück.
        Return: List of (VertragData, renewal_date, deadline_date)
        """
        result: list[tuple[VertragData, date, date]] = []
        for contract in self.contracts.values():
            start = date.fromisoformat(contract.start_date)
            renewal = _calc_next_renewal(start, contract.duration_months, today)
            deadline = _calc_deadline(renewal, contract.notice_days)
            result.append((contract, renewal, deadline))
        return sorted(result, key=lambda x: x[2])


class VertragsmanagerCoordinator(DataUpdateCoordinator[VertragsmanagerData]):
    """Coordinator für alle Vertragsdaten."""

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(
            hass,
            name=DOMAIN,
            update_interval=None,
        )
        self.data = VertragsmanagerData()

    def update_contract(self, entry_id: str, data: dict[str, Any]) -> None:
        """Aktualisiert oder fügt einen Vertrag hinzu."""
        from typing import Any

        contract = VertragData(
            entry_id=entry_id,
            name=data[CONF_NAME],
            category=data[CONF_CATEGORY],
            provider=data[CONF_PROVIDER],
            cost=data[CONF_COST],
            cycle=data[CONF_CYCLE],
            start_date=data[CONF_START_DATE],
            notice_days=data[CONF_NOTICE_DAYS],
            duration_months=data[CONF_DURATION_MONTHS],
            auto_renew=data[CONF_AUTO_RENEW],
            contract_number=data.get(CONF_CONTRACT_NUMBER, ""),
            customer_number=data.get(CONF_CUSTOMER_NUMBER, ""),
            notice_period_text=data.get(CONF_NOTICE_PERIOD_TEXT, ""),
            payment_day=data.get(CONF_PAYMENT_DAY, ""),
            notes=data.get(CONF_NOTES, ""),
            portal_url=data.get(CONF_PORTAL_URL, ""),
            email=data.get(CONF_EMAIL, ""),
            phone=data.get(CONF_PHONE, ""),
        )
        self.data.contracts[entry_id] = contract

    def remove_contract(self, entry_id: str) -> None:
        """Entfernt einen Vertrag."""
        self.data.contracts.pop(entry_id, None)

    def async_refresh(self) -> None:
        """Triggert manuelles Refresh."""
        self.async_set_updated_data(self.data)
