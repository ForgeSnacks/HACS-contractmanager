"""Tests für Diagnostics."""
from __future__ import annotations


def test_diagnostics_imports() -> None:
    """Test that diagnostics module can be imported."""
    from custom_components.vertragsmanager import diagnostics  # noqa: F401
    assert True


def test_diagnostics_function_exists() -> None:
    """Test that the required diagnostics function exists."""
    from custom_components.vertragsmanager.diagnostics import (
        async_get_config_entry_diagnostics,
    )
    assert callable(async_get_config_entry_diagnostics)
