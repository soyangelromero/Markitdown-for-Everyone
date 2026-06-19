"""Global pytest fixtures for the markitdown_pollinations test suite."""

import pytest

from markitdown_pollinations.i18n import set_language


@pytest.fixture(autouse=True)
def _reset_language():
    """Reset i18n language to English before every test.

    T9b added system-language detection to main(), which sets the global
    _current_language to the detected locale (e.g. "es" on Spanish Windows).
    Converter and validation tests assert English strings from _(), so every
    test must start with a clean "en" state to avoid leaking the detected
    language across test modules.
    """
    set_language("en")
