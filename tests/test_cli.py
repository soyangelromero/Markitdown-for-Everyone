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


def test_parse_args_all_flags():
    args = parse_args(["-i", "file.pdf", "-o", "out.md", "-k", "key", "-m", "openai"])
    assert args.input_file == "file.pdf"
    assert args.output_file == "out.md"
    assert args.api_key == "key"
    assert args.model == "openai"


def test_parse_args_configure():
    args = parse_args(["--configure", "-k", "key", "-m", "openai"])
    assert args.configure is True
    assert args.api_key == "key"
    assert args.model == "openai"


def test_main_without_api_key_exits(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["-i", "file.txt"])
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "API key is required" in captured.out


def test_main_without_input_exits(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["-k", "key"])
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "Input file is required" in captured.out


def test_main_input_not_found(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["-i", "does_not_exist.pdf", "-k", "key"])
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "File not found" in captured.out


@patch("markitdown_pollinations.cli.validate_model")
@patch("markitdown_pollinations.cli.save_config")
@patch("markitdown_pollinations.cli.load_config")
def test_configure_success(mock_load_config, mock_save_config, mock_validate_model):
    mock_load_config.return_value = {"api_key": "", "model": "openai"}
    mock_validate_model.return_value = (True, "")
    mock_save_config.return_value = True

    code = main(["--configure", "-k", "secret", "-m", "openai"])

    assert code == 0
    mock_validate_model.assert_called_once_with("secret", "openai")
    mock_save_config.assert_called_once_with({"api_key": "secret", "model": "openai"})


@patch("markitdown_pollinations.cli.validate_model")
@patch("markitdown_pollinations.cli.load_config")
def test_configure_validation_fails(mock_load_config, mock_validate_model):
    mock_load_config.return_value = {"api_key": "", "model": "openai"}
    mock_validate_model.return_value = (False, "bad key")

    code = main(["--configure", "-k", "secret", "-m", "openai"])

    assert code == 1


@patch("markitdown_pollinations.cli.convert_file")
@patch("markitdown_pollinations.cli.load_config")
def test_convert_success(mock_load_config, mock_convert_file, temp_file):
    mock_load_config.return_value = {"api_key": "key", "model": "openai"}
    result = MagicMock()
    result.success = True
    result.cancelled = False
    result.output_path = temp_file.replace(".txt", ".md")
    result.warning = ""
    mock_convert_file.return_value = result

    code = main(["-i", temp_file])

    assert code == 0
    mock_convert_file.assert_called_once()


@patch("markitdown_pollinations.cli.convert_file")
@patch("markitdown_pollinations.cli.load_config")
def test_convert_failure(mock_load_config, mock_convert_file, temp_file):
    mock_load_config.return_value = {"api_key": "key", "model": "openai"}
    result = MagicMock()
    result.success = False
    result.cancelled = False
    result.message = "Conversion failed"
    mock_convert_file.return_value = result

    code = main(["-i", temp_file])

    assert code == 1


@patch("markitdown_pollinations.cli.convert_file")
@patch("markitdown_pollinations.cli.load_config")
def test_image_with_non_vision_model_warns(
    mock_load_config, mock_convert_file, tmp_path
):
    image = tmp_path / "photo.png"
    image.write_bytes(b"fake-image")
    mock_load_config.return_value = {"api_key": "key", "model": "glm"}
    result = MagicMock()
    result.success = True
    result.cancelled = False
    result.output_path = str(tmp_path / "photo.md")
    result.warning = ""
    mock_convert_file.return_value = result

    with patch("markitdown_pollinations.cli.print") as mock_print:
        code = main(["-i", str(image)])

    assert code == 0
    warning_calls = [
        call for call in mock_print.call_args_list if "not a vision model" in str(call)
    ]
    assert len(warning_calls) == 1
