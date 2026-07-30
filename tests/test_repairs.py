"""Tests für Repairs."""
from __future__ import annotations

from custom_components.vertragsmanager.const import DOMAIN
from custom_components.vertragsmanager.repairs import async_process_repairs


def test_repairs_imports() -> None:
    """Test that repairs module can be imported."""
    from custom_components.vertragsmanager import repairs  # noqa: F401
    assert True


def test_repairs_function_exists() -> None:
    """Test that the required repairs function exists."""
    assert callable(async_process_repairs)


def test_repairs_domain_constant() -> None:
    """Test DOMAIN constant used in repairs."""
    assert DOMAIN == "vertragsmanager"
