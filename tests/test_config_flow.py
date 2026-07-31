"""Tests für Config Flow - basic validation."""
from __future__ import annotations

from custom_components.vertragsmanager.const import (
    CATEGORIES,
    CONF_AUTO_RENEW,
    CONF_CATEGORY,
    CONF_COST,
    CONF_CYCLE,
    CONF_DURATION_MONTHS,
    CONF_NAME,
    CONF_NOTICE_DAYS,
    CONF_PROVIDER,
    CONF_START_DATE,
    CYCLES,
    DOMAIN,
)


def test_domain_constant() -> None:
    """Test DOMAIN constant."""
    assert DOMAIN == "vertragsmanager"


def test_categories_defined() -> None:
    """Test that categories list is non-empty and contains expected values."""
    assert len(CATEGORIES) > 0
    assert "Handy" in CATEGORIES
    assert "Sonstiges" in CATEGORIES


def test_cycles_defined() -> None:
    """Test that cycles list has expected values."""
    assert "monatlich" in CYCLES
    assert "jährlich" in CYCLES


def test_user_schema_fields() -> None:
    """Test that the user schema builder produces expected fields."""
    from custom_components.vertragsmanager.config_flow import _build_user_schema

    schema = _build_user_schema()
    schema_keys = {str(k) for k in schema.schema.keys()}
    assert CONF_NAME in schema_keys
    assert CONF_CATEGORY in schema_keys
    assert CONF_PROVIDER in schema_keys
    assert CONF_COST in schema_keys
    assert CONF_CYCLE in schema_keys
    assert CONF_START_DATE in schema_keys
    assert CONF_NOTICE_DAYS in schema_keys
    assert CONF_DURATION_MONTHS in schema_keys
    assert CONF_AUTO_RENEW in schema_keys


def test_options_schema_fields() -> None:
    """Test that the options schema builder produces expected fields."""
    from custom_components.vertragsmanager.config_flow import _build_options_schema

    current = {CONF_NAME: "Test", CONF_CATEGORY: "Handy", CONF_PROVIDER: "P",
               CONF_COST: 10.0, CONF_CYCLE: "monatlich", CONF_START_DATE: "2024-01-01",
               CONF_NOTICE_DAYS: 30, CONF_DURATION_MONTHS: 12, CONF_AUTO_RENEW: True}
    schema = _build_options_schema(current)
    schema_keys = {str(k) for k in schema.schema.keys()}
    assert CONF_CATEGORY in schema_keys
    assert CONF_PROVIDER in schema_keys
    assert CONF_COST in schema_keys
    assert CONF_CYCLE in schema_keys
    assert CONF_START_DATE in schema_keys
    assert CONF_NOTICE_DAYS in schema_keys
    assert CONF_DURATION_MONTHS in schema_keys
    assert CONF_AUTO_RENEW in schema_keys


def test_imports() -> None:
    """Test that modules can be imported."""
    from custom_components.vertragsmanager import config_flow  # noqa: F401
    assert True
