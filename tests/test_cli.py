"""Tests for the command-line interface."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from markitdown_pollinations.cli import main, parse_args


@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary text file."""
    path = tmp_path / "input.txt"
    path.write_text("hello", encoding="utf-8")
    return str(path)


@pytest.fixture
def configured_config():
    """Return a fully configured config dictionary."""
    return {
        "api_key": "test-key",
        "text_model": "openai",
        "vision_model": "openai",
    }


def test_parse_args_positional_input():
    args = parse_args(["file.pdf", "-o", "out.md", "-k", "key", "-m", "openai"])
    assert args.input_file == "file.pdf"
    assert args.output_file == "out.md"
    assert args.api_key == "key"
    assert args.model == "openai"


@patch("markitdown_pollinations.cli.convert_file")
@patch("markitdown_pollinations.cli.load_config")
def test_quick_convert_success(mock_load_config, mock_convert_file, temp_file):
    mock_load_config.return_value = {
        "api_key": "key",
        "text_model": "openai",
        "vision_model": "openai",
    }
    result = MagicMock()
    result.success = True
    result.cancelled = False
    result.output_path = temp_file.replace(".txt", ".md")
    result.warning = ""
    mock_convert_file.return_value = result

    code = main([temp_file])

    assert code == 0
    mock_convert_file.assert_called_once()


@patch("markitdown_pollinations.cli.load_config")
def test_quick_convert_missing_api_key(mock_load_config, temp_file):
    mock_load_config.return_value = {
        "api_key": "",
        "text_model": "openai",
        "vision_model": "openai",
    }

    code = main([temp_file])

    assert code == 1


@patch("builtins.input")
@patch("markitdown_pollinations.cli.save_config")
@patch("markitdown_pollinations.cli.load_config")
def test_setup_wizard_first_run(
    mock_load_config, mock_save_config, mock_input
):
    mock_load_config.return_value = {
        "api_key": "",
        "text_model": "openai",
        "vision_model": "openai",
    }
    mock_input.side_effect = [
        "secret-key",  # api key
        "1",  # text model -> openai
        "1",  # vision model -> openai
    ]
    mock_save_config.return_value = True

    # Open configure explicitly; since config is empty, wizard runs
    code = main(["--configure"])

    assert code == 0
    mock_save_config.assert_called_once_with(
        {"api_key": "secret-key", "text_model": "openai", "vision_model": "openai"}
    )


@patch("builtins.input")
@patch("markitdown_pollinations.cli.save_config")
@patch("markitdown_pollinations.cli.load_config")
def test_configure_menu_updates_settings(
    mock_load_config, mock_save_config, mock_input
):
    mock_load_config.return_value = {
        "api_key": "old-key",
        "text_model": "glm",
        "vision_model": "gemini",
    }
    mock_input.side_effect = [
        "new-key",  # api key
        "1",  # text model -> openai
        "2",  # vision model -> openai-large
    ]
    mock_save_config.return_value = True

    code = main(["--configure"])

    assert code == 0
    mock_save_config.assert_called_once_with(
        {
            "api_key": "new-key",
            "text_model": "openai",
            "vision_model": "openai-large",
        }
    )


@patch("builtins.input")
@patch("markitdown_pollinations.cli.convert_file")
@patch("markitdown_pollinations.cli.load_config")
def test_menu_convert_document(
    mock_load_config, mock_convert_file, mock_input, temp_file
):
    mock_load_config.return_value = {
        "api_key": "key",
        "text_model": "openai",
        "vision_model": "openai",
    }
    # Choose option 3 (document), provide file path, accept default output, then quit
    mock_input.side_effect = ["3", temp_file, "", "5"]
    result = MagicMock()
    result.success = True
    result.cancelled = False
    result.output_path = temp_file.replace(".txt", ".md")
    result.warning = ""
    mock_convert_file.return_value = result

    code = main([])

    assert code == 0
    mock_convert_file.assert_called_once()


@patch("builtins.input")
@patch("markitdown_pollinations.cli.load_config")
def test_menu_quit(mock_load_config, mock_input):
    mock_load_config.return_value = {
        "api_key": "key",
        "text_model": "openai",
        "vision_model": "openai",
    }
    mock_input.side_effect = ["5"]

    code = main([])

    assert code == 0
