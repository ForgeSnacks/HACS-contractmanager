"""Exceptions für Vertragsmanager."""
from __future__ import annotations


class VertragsmanagerError(Exception):
    """Basis-Exception für Vertragsmanager."""


class VertragsmanagerInvalidDateError(VertragsmanagerError):
    """Fehler bei ungültigem Datum."""


class VertragsmanagerContractCreationError(VertragsmanagerError):
    """Fehler bei Vertragserstellung."""
