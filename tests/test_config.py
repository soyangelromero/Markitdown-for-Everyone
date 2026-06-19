"""Tests for the config module."""

from unittest.mock import mock_open, patch

import pytest

from markitdown_pollinations.config import load_config, save_config

DEFAULT = {
    "api_key": "",
    "text_model": "openai",
    "vision_model": "openai",
    "language": "en",
}


@pytest.fixture
def isolated_config(monkeypatch, tmp_path):
    """Redirect CONFIG_FILE to a temporary path."""
    config_path = tmp_path / "config.json"
    monkeypatch.setattr("markitdown_pollinations.config.CONFIG_FILE", config_path)
    return config_path


def test_load_config_returns_defaults_when_missing(isolated_config):
    assert load_config() == DEFAULT


def test_load_config_returns_defaults_on_invalid_json(isolated_config):
    isolated_config.write_text("not valid json", encoding="utf-8")
    assert load_config() == DEFAULT


def test_load_config_returns_defaults_when_not_a_dict(isolated_config):
    isolated_config.write_text("[1, 2, 3]", encoding="utf-8")
    assert load_config() == DEFAULT


def test_save_and_load_config_round_trip(isolated_config):
    config = {
        "api_key": "sk_test",
        "text_model": "claude",
        "vision_model": "openai-large",
        "language": "en",
    }
    assert save_config(config) is True
    assert load_config() == config


def test_load_config_returns_valid_config(isolated_config):
    isolated_config.write_text(
        '{"api_key": "pk_test", "text_model": "gemini", "vision_model": "gemini-large"}',
        encoding="utf-8",
    )
    expected = DEFAULT.copy()
    expected.update({"api_key": "pk_test", "text_model": "gemini", "vision_model": "gemini-large"})
    assert load_config() == expected


def test_load_config_env_key_preserves_file_settings(isolated_config, monkeypatch):
    """POLLINATIONS_API_KEY overrides api_key but preserves file settings."""
    config_json = (
        '{"api_key": "file_key", "text_model": "gemini",'
        '"vision_model": "gemini-large", "language": "es"}'
    )
    isolated_config.write_text(config_json, encoding="utf-8")
    monkeypatch.setenv("POLLINATIONS_API_KEY", "env_key")
    result = load_config()
    assert result["api_key"] == "env_key"
    assert result["text_model"] == "gemini"
    assert result["vision_model"] == "gemini-large"
    assert result["language"] == "es"


def test_load_config_env_key_with_no_file_returns_defaults(isolated_config, monkeypatch):
    """When env var is set but no config file exists, return defaults with api_key overridden."""
    monkeypatch.setenv("POLLINATIONS_API_KEY", "env_key")
    result = load_config()
    assert result["api_key"] == "env_key"
    assert result["text_model"] == "openai"
    assert result["vision_model"] == "openai"
    assert result["language"] == "en"


def test_load_config_ignores_empty_env_api_key(isolated_config, monkeypatch):
    isolated_config.write_text(
        '{"api_key": "file_key", "text_model": "openai", "vision_model": "openai"}',
        encoding="utf-8",
    )
    monkeypatch.setenv("POLLINATIONS_API_KEY", "   ")
    expected = DEFAULT.copy()
    expected["api_key"] = "file_key"
    assert load_config() == expected


def test_load_config_fills_missing_keys_with_defaults(isolated_config):
    """Test that load_config() merges loaded JSON with DEFAULT_CONFIG to fill missing keys."""
    isolated_config.write_text(
        '{"api_key": "pk_partial"}',
        encoding="utf-8",
    )
    result = load_config()
    assert result["api_key"] == "pk_partial"
    assert result["text_model"] == "openai"
    assert result["vision_model"] == "openai"
    assert result["language"] == "en"


def test_save_config_returns_false_on_write_error(isolated_config):
    with patch("builtins.open", mock_open()) as mocked:
        mocked.return_value.write.side_effect = OSError("permission denied")
        assert (
            save_config({"api_key": "x", "text_model": "y", "vision_model": "z", "language": "en"})
            is False
        )  # noqa: E501


def test_save_config_sets_unix_permissions(isolated_config, monkeypatch):
    chmod_calls = []

    def fake_chmod(path, mode):
        chmod_calls.append((str(path), mode))

    monkeypatch.setattr("os.chmod", fake_chmod)
    monkeypatch.setattr("os.name", "posix")

    assert (
        save_config(
            {
                "api_key": "sk_test",
                "text_model": "openai",
                "vision_model": "openai",
                "language": "en",
            }
        )  # noqa: E501
        is True
    )
    assert len(chmod_calls) == 1
    assert chmod_calls[0][1] == 0o600


def test_save_config_skips_chmod_on_windows(isolated_config, monkeypatch):
    chmod_calls = []

    def fake_chmod(path, mode):
        chmod_calls.append((str(path), mode))

    monkeypatch.setattr("os.chmod", fake_chmod)
    monkeypatch.setattr("os.name", "nt")

    assert (
        save_config(
            {
                "api_key": "sk_test",
                "text_model": "openai",
                "vision_model": "openai",
                "language": "en",
            }
        )  # noqa: E501
        is True
    )
    assert len(chmod_calls) == 0
