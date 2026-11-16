"""Global pytest fixtures for the markitdown_pollinations test suite."""

from __future__ import annotations

import pytest

from markitdown_pollinations import i18n, models
from markitdown_pollinations.constants import _reset_color_cache


@pytest.fixture(autouse=True)
def _reset_global_state(monkeypatch):
    """Reset language, caches and environment overrides before every test."""
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.delenv("FORCE_COLOR", raising=False)
    monkeypatch.delenv("POLLINATIONS_API_KEY", raising=False)
    i18n.set_language("en")
    _reset_color_cache()
    models.clear_cache()
    yield
