"""Tests for the live model catalog helper."""

from __future__ import annotations

import json
import urllib.error

import pytest

import markitdown_pollinations.models as models_module
from markitdown_pollinations.i18n import set_language


class _FakeResponse:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return self._payload

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *args: object) -> bool:
        return False


SAMPLE = [
    {
        "name": "openai/gpt-5.4-nano",
        "aliases": ["gpt-5.4-nano", "openai"],
        "input_modalities": ["text", "image"],
        "paid_only": False,
    },
    {
        "name": "z-ai/glm-5.2",
        "aliases": ["glm"],
        "input_modalities": ["text"],
        "paid_only": True,
    },
    {"bad": "entry"},
    {"name": "", "aliases": []},
    {
        "name": "broken/types",
        "aliases": "not-a-list",
        "input_modalities": "text",
        "paid_only": True,
    },
]


@pytest.fixture
def catalog(monkeypatch):
    calls: list[dict[str, object]] = []

    def fake_urlopen(request, timeout=0):
        calls.append({"url": getattr(request, "full_url", ""), "timeout": timeout})
        return _FakeResponse(json.dumps(SAMPLE).encode("utf-8"))

    monkeypatch.setattr(models_module.urllib.request, "urlopen", fake_urlopen)
    result = models_module.fetch_catalog(use_cache=False)
    assert result is not None
    return result, calls


def test_fetch_catalog_parses_models(catalog):
    result, _ = catalog
    openai = result.find("openai")
    assert openai is not None
    assert openai.name == "openai/gpt-5.4-nano"
    assert openai.accepts_images is True
    assert openai.paid_only is False

    glm = result.find("glm")
    assert glm is not None
    assert glm.accepts_images is False
    assert glm.paid_only is True


def test_fetch_catalog_skips_malformed_entries(catalog):
    result, _ = catalog
    assert len(result.models) == 3
    assert result.find("") is None
    broken = result.find("broken/types")
    assert broken is not None
    assert broken.aliases == ()
    assert broken.input_modalities == frozenset()


def test_fetch_catalog_returns_none_on_invalid_json(monkeypatch):
    def fake_urlopen(request, timeout=0):
        return _FakeResponse(b"not json")

    monkeypatch.setattr(models_module.urllib.request, "urlopen", fake_urlopen)
    assert models_module.fetch_catalog(use_cache=False) is None


def test_fetch_catalog_returns_none_on_network_error(monkeypatch):
    def fake_urlopen(request, timeout=0):
        raise urllib.error.URLError("down")

    monkeypatch.setattr(models_module.urllib.request, "urlopen", fake_urlopen)
    assert models_module.fetch_catalog(use_cache=False) is None


def test_fetch_catalog_returns_none_for_non_list_payload(monkeypatch):
    def fake_urlopen(request, timeout=0):
        return _FakeResponse(b'{"models": []}')

    monkeypatch.setattr(models_module.urllib.request, "urlopen", fake_urlopen)
    assert models_module.fetch_catalog(use_cache=False) is None


def test_fetch_catalog_uses_cache(monkeypatch):
    calls = 0

    def fake_urlopen(request, timeout=0):
        nonlocal calls
        calls += 1
        return _FakeResponse(json.dumps(SAMPLE).encode("utf-8"))

    monkeypatch.setattr(models_module.urllib.request, "urlopen", fake_urlopen)
    first = models_module.fetch_catalog()
    second = models_module.fetch_catalog()
    assert first is not None
    assert first is second
    assert calls == 1

    models_module.fetch_catalog(use_cache=False)
    assert calls == 2


def test_clear_cache_forces_refetch(monkeypatch):
    calls = 0

    def fake_urlopen(request, timeout=0):
        nonlocal calls
        calls += 1
        return _FakeResponse(json.dumps(SAMPLE).encode("utf-8"))

    monkeypatch.setattr(models_module.urllib.request, "urlopen", fake_urlopen)
    models_module.fetch_catalog()
    models_module.clear_cache()
    models_module.fetch_catalog()
    assert calls == 2


def test_find_is_case_insensitive(catalog):
    result, _ = catalog
    assert result.find("OPENAI") is not None
    assert result.find("  glm  ") is not None
    assert result.find("does-not-exist") is None


def test_is_paid_and_accepts_images(catalog):
    result, _ = catalog
    assert result.is_paid("openai") is False
    assert result.is_paid("glm") is True
    assert result.is_paid("unknown") is None
    assert result.accepts_images("openai") is True
    assert result.accepts_images("glm") is False
    assert result.accepts_images("unknown") is None


def test_filter_known_preserves_order(catalog):
    result, _ = catalog
    assert result.filter_known(["glm", "nope", "openai"]) == ("glm", "openai")


def test_tags_and_annotate_english(catalog):
    result, _ = catalog
    assert result.tags("openai") == ("vision",)
    assert result.tags("glm") == ("paid",)
    assert result.annotate("openai") == "openai (vision)"
    assert result.annotate("glm") == "glm (paid)"
    assert result.annotate("unknown") == "unknown"


def test_tags_and_annotate_spanish(catalog):
    result, _ = catalog
    set_language("es")
    assert result.tags("openai") == ("visión",)
    assert result.annotate("glm") == "glm (de pago)"
