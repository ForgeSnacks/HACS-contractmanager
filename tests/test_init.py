"""Tests für __init__ (Integration Setup)."""
from __future__ import annotations

from custom_components.vertragsmanager.const import (
    DOMAIN,
    PANEL_URL_PATH,
    PANEL_TITLE,
    PANEL_ICON,
    PANEL_NAME,
    PANEL_JS_URL,
    PLATFORMS,
)
from custom_components.vertragsmanager.exceptions import (
    VertragsmanagerError,
    VertragsmanagerInvalidDateError,
    VertragsmanagerContractCreationError,
)


def test_domain_constant() -> None:
    """Test DOMAIN constant."""
    assert DOMAIN == "vertragsmanager"


def test_platforms() -> None:
    """Test PLATFORMS list."""
    assert "sensor" in PLATFORMS


def test_panel_constants() -> None:
    """Test panel constants."""
    assert PANEL_URL_PATH == "vertragsmanager"
    assert PANEL_TITLE == "Vertragsmanager"
    assert PANEL_NAME == "vertragsmanager-panel"
    assert "/api/vertragsmanager/frontend/panel.js" in PANEL_JS_URL


def test_exception_hierarchy() -> None:
    """Test exception hierarchy."""
    assert issubclass(VertragsmanagerInvalidDateError, VertragsmanagerError)
    assert issubclass(VertragsmanagerContractCreationError, VertragsmanagerError)


def test_imports() -> None:
    """Test that main module can be imported."""
    from custom_components.vertragsmanager import (
        CREATE_CONTRACT_SCHEMA,
        SERVICE_CREATE_CONTRACT,
        STATIC_FRONTEND_PATH,
    )
    assert SERVICE_CREATE_CONTRACT == "create_contract"
    assert STATIC_FRONTEND_PATH == "/api/vertragsmanager/frontend"
    assert CREATE_CONTRACT_SCHEMA is not None
