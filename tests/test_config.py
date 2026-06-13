"""Tests for the config module."""

from unittest.mock import mock_open, patch

import pytest

from markitdown_pollinations.config import load_config, save_config


@pytest.fixture
def isolated_config(monkeypatch, tmp_path):
    """Redirect CONFIG_FILE to a temporary path."""
    config_path = tmp_path / "config.json"
    monkeypatch.setattr(
        "markitdown_pollinations.config.CONFIG_FILE", config_path
    )
    return config_path


def test_load_config_returns_defaults_when_missing(isolated_config):
    assert load_config() == {"api_key": "", "model": "openai"}


def test_load_config_returns_defaults_on_invalid_json(isolated_config):
    isolated_config.write_text("not valid json", encoding="utf-8")
    assert load_config() == {"api_key": "", "model": "openai"}


def test_load_config_returns_defaults_when_not_a_dict(isolated_config):
    isolated_config.write_text("[1, 2, 3]", encoding="utf-8")
    assert load_config() == {"api_key": "", "model": "openai"}


def test_save_and_load_config_round_trip(isolated_config):
    config = {"api_key": "sk_test", "model": "claude"}
    assert save_config(config) is True
    assert load_config() == config


def test_load_config_returns_valid_config(isolated_config):
    isolated_config.write_text(
        '{"api_key": "pk_test", "model": "gemini"}', encoding="utf-8"
    )
    assert load_config() == {"api_key": "pk_test", "model": "gemini"}


def test_save_config_returns_false_on_write_error(isolated_config):
    with patch("builtins.open", mock_open()) as mocked:
        mocked.return_value.write.side_effect = OSError("permission denied")
        assert save_config({"api_key": "x", "model": "y"}) is False
