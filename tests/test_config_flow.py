"""Tests für Config Flow - basic validation."""
from __future__ import annotations

from custom_components.vertragsmanager.const import DOMAIN


def test_domain_constant() -> None:
    """Test DOMAIN constant."""
    assert DOMAIN == "vertragsmanager"


def test_imports() -> None:
    """Test that modules can be imported."""
    from custom_components.vertragsmanager import config_flow, coordinator, sensor  # noqa: F401
    assert True
