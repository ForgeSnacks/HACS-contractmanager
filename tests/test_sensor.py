"""Tests für Sensor Entities - basic validation."""
from __future__ import annotations

from custom_components.vertragsmanager.sensor import (
    GesamtkostenSensorEntity,
    VertragLaufzeitSensorEntity,
    VertragPreisProMonatSensorEntity,
    VertragBereitsGezahltSensorEntity,
    VertragNochZuZahlenSensorEntity,
)


def test_sensor_classes_exist() -> None:
    """Test that sensor classes exist."""
    assert VertragLaufzeitSensorEntity is not None
    assert VertragPreisProMonatSensorEntity is not None
    assert VertragBereitsGezahltSensorEntity is not None
    assert VertragNochZuZahlenSensorEntity is not None
    assert GesamtkostenSensorEntity is not None


def test_sensor_imports() -> None:
    """Test sensor module imports."""
    from custom_components.vertragsmanager import sensor  # noqa: F401
    assert True
