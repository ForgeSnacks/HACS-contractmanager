"""Test configuration für pytest."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Fügt das Repo-Root zum Python-Pfad hinzu
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))
