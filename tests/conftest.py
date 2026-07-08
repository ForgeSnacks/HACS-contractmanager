"""Test configuration für pytest."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

# Fügt das Repo-Root zum Python-Pfad hinzu
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))


@pytest.fixture(autouse=True)
def verify_imports() -> None:
    """Stellt sicher, dass Module importierbar sind."""
    from custom_components.vertragsmanager import const  # noqa: F401
