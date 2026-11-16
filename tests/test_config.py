"""Tests for the config module."""

from __future__ import annotations

import json

import pytest

import markitdown_pollinations.config as config_module

DEFAULT = {
    "api_key": "",
    "text_model": "openai",
    "vision_model": "openai",
    "language": "",
}


@pytest.fixture
def isolated_config(monkeypatch, tmp_path):
    """Redirect CONFIG_FILE to a temporary path."""
    config_path = tmp_path / "config.json"
    monkeypatch.setattr(config_module, "CONFIG_FILE", config_path)
    return config_path


def _write(config_path, payload: object) -> None:
    config_path.write_text(json.dumps(payload), encoding="utf-8")


def test_load_config_returns_defaults_when_missing(isolated_config):
    assert config_module.load_config() == DEFAULT


def test_default_language_means_auto_detect():
    assert DEFAULT["language"] == ""


def test_load_config_returns_defaults_on_invalid_json(isolated_config, capsys):
    isolated_config.write_text("not valid json", encoding="utf-8")
    assert config_module.load_config() == DEFAULT
    assert "invalid JSON" in capsys.readouterr().err


def test_load_config_returns_defaults_when_not_a_dict(isolated_config, capsys):
    isolated_config.write_text("[1, 2, 3]", encoding="utf-8")
    assert config_module.load_config() == DEFAULT
    assert "not a dict" in capsys.readouterr().err


def test_load_config_merges_partial_file(isolated_config):
    _write(isolated_config, {"api_key": "sk_partial"})
    result = config_module.load_config()
    assert result["api_key"] == "sk_partial"
    assert result["text_model"] == "openai"
    assert result["language"] == ""


def test_load_config_ignores_invalid_values(isolated_config, capsys):
    _write(
        isolated_config,
        {
            "api_key": 123,
            "text_model": "  ",
            "vision_model": "claude",
            "language": "fr",
        },
    )
    result = config_module.load_config()
    assert result["api_key"] == ""
    assert result["text_model"] == "openai"
    assert result["vision_model"] == "claude"
    assert result["language"] == ""
    stderr = capsys.readouterr().err
    assert stderr.count("invalid value") == 3


def test_load_config_env_key_sets_marker(isolated_config, monkeypatch):
    _write(isolated_config, {"api_key": "file_key", "language": "es"})
    monkeypatch.setenv("POLLINATIONS_API_KEY", "env_key")
    result = config_module.load_config()
    assert result["api_key"] == "env_key"
    assert result["api_key_from_env"] is True
    assert result["language"] == "es"


def test_load_config_ignores_empty_env_key(isolated_config, monkeypatch):
    _write(isolated_config, {"api_key": "file_key"})
    monkeypatch.setenv("POLLINATIONS_API_KEY", "   ")
    result = config_module.load_config()
    assert result["api_key"] == "file_key"
    assert "api_key_from_env" not in result


def test_save_config_does_not_persist_env_key(isolated_config, monkeypatch):
    monkeypatch.setenv("POLLINATIONS_API_KEY", "env_key")
    config = config_module.load_config()
    assert config_module.save_config(config) is True
    stored = json.loads(isolated_config.read_text(encoding="utf-8"))
    assert stored["api_key"] == ""
    assert "api_key_from_env" not in stored


def test_save_config_preserves_disk_key_when_env_overrides(isolated_config, monkeypatch):
    _write(isolated_config, {"api_key": "file_key", "language": "es"})
    monkeypatch.setenv("POLLINATIONS_API_KEY", "env_key")
    config = config_module.load_config()
    assert config_module.save_config(config) is True
    stored = json.loads(isolated_config.read_text(encoding="utf-8"))
    assert stored["api_key"] == "file_key"
    assert stored["language"] == "es"


def test_save_config_persists_explicit_key(isolated_config):
    config = {
        "api_key": "sk_new",
        "text_model": "glm",
        "vision_model": "gemini",
        "language": "es",
    }
    assert config_module.save_config(config) is True
    assert config_module.load_config() == config


def test_save_config_ignores_runtime_only_marker(isolated_config):
    config = {
        "api_key": "sk_new",
        "text_model": "openai",
        "vision_model": "openai",
        "language": "en",
        "api_key_from_env": False,
        "unknown_key": "ignored",
    }
    assert config_module.save_config(config) is True
    stored = json.loads(isolated_config.read_text(encoding="utf-8"))
    assert stored == {
        "api_key": "sk_new",
        "text_model": "openai",
        "vision_model": "openai",
        "language": "en",
    }


def test_save_config_returns_false_on_replace_error(isolated_config, monkeypatch):
    def broken_replace(src, dst):
        raise OSError("disk full")

    monkeypatch.setattr(config_module.os, "replace", broken_replace)
    result = config_module.save_config(
        {"api_key": "sk_x", "text_model": "openai", "vision_model": "openai", "language": "en"}
    )
    assert result is False
    assert not isolated_config.exists()
    # The temporary file is cleaned up.
    assert not list(isolated_config.parent.glob(".config-*.json"))


def test_save_config_sets_owner_only_permissions(isolated_config, monkeypatch):
    chmod_calls: list[tuple[str, int]] = []

    def fake_chmod(path, mode):
        chmod_calls.append((str(path), mode))

    monkeypatch.setattr(config_module, "_is_windows", lambda: False)
    monkeypatch.setattr(config_module.os, "chmod", fake_chmod)

    assert (
        config_module.save_config(
            {"api_key": "sk_x", "text_model": "openai", "vision_model": "openai", "language": "en"}
        )
        is True
    )
    assert [mode for _, mode in chmod_calls] == [0o600]


def test_save_config_skips_chmod_on_windows(isolated_config, monkeypatch):
    chmod_calls: list[tuple[str, int]] = []

    def fake_chmod(path, mode):
        chmod_calls.append((str(path), mode))

    monkeypatch.setattr(config_module, "_is_windows", lambda: True)
    monkeypatch.setattr(config_module.os, "chmod", fake_chmod)

    assert (
        config_module.save_config(
            {"api_key": "sk_x", "text_model": "openai", "vision_model": "openai", "language": "en"}
        )
        is True
    )
    assert chmod_calls == []


def test_save_config_handles_missing_parent(isolated_config, monkeypatch, tmp_path):
    nested = tmp_path / "deep" / "nested" / "config.json"
    monkeypatch.setattr(config_module, "CONFIG_FILE", nested)
    assert (
        config_module.save_config(
            {"api_key": "", "text_model": "openai", "vision_model": "openai", "language": ""}
        )
        is True
    )
    assert nested.is_file()
