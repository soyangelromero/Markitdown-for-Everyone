"""Tests for the command-line interface."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from markitdown_pollinations.cli import (
    _ask_file,
    _ask_model,
    _ask_output,
    _clear_screen,
    _color,
    _confirm_overwrite,
    _is_cancel_input,
    _prompt_for_api_key,
    main,
    parse_args,
)
from markitdown_pollinations.constants import _reset_no_color_cache
from markitdown_pollinations.validation import _validate_key_via_api


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


@patch("builtins.input")
@patch("markitdown_pollinations.cli.load_config")
def test_quick_convert_missing_api_key(mock_load_config, mock_input, temp_file):
    mock_load_config.return_value = {
        "api_key": "",
        "text_model": "openai",
        "vision_model": "openai",
    }
    mock_input.return_value = "1"  # language selector -> English

    code = main([temp_file])

    assert code == 1


@patch("getpass.getpass")
@patch("builtins.input")
@patch("markitdown_pollinations.cli._clear_screen")
@patch("markitdown_pollinations.cli._validate_key_via_api")
@patch("markitdown_pollinations.cli.save_config")
@patch("markitdown_pollinations.cli.load_config")
def test_setup_wizard_first_run(
    mock_load_config, mock_save_config, mock_validate, mock_clear, mock_input, mock_getpass
):
    mock_load_config.return_value = {
        "api_key": "",
        "text_model": "openai",
        "vision_model": "openai",
    }
    mock_getpass.return_value = "sk-secret-key-123"
    mock_input.side_effect = [
        "1",  # language selector -> English
        "1",  # text model -> openai
        "1",  # vision model -> openai
    ]
    mock_save_config.return_value = True
    mock_validate.return_value = "valid"

    # Open configure explicitly; since config is empty, wizard runs
    code = main(["--configure"])

    assert code == 0
    mock_save_config.assert_called_once_with(
        {"api_key": "sk-secret-key-123", "text_model": "openai", "vision_model": "openai", "language": "en"}  # noqa: E501
    )


@patch("getpass.getpass")
@patch("builtins.input")
@patch("markitdown_pollinations.cli._clear_screen")
@patch("markitdown_pollinations.cli._validate_key_via_api")
@patch("markitdown_pollinations.cli.save_config")
@patch("markitdown_pollinations.cli.load_config")
def test_configure_menu_updates_settings(
    mock_load_config, mock_save_config, mock_validate, mock_clear, mock_input, mock_getpass
):
    mock_load_config.return_value = {
        "api_key": "old-key",
        "text_model": "glm",
        "vision_model": "gemini",
    }
    mock_getpass.return_value = "sk-new-key-12345"
    mock_input.side_effect = [
        "1",  # language selector -> English
        "1",  # text model -> openai
        "2",  # vision model -> openai-large
    ]
    mock_save_config.return_value = True
    mock_validate.return_value = "valid"

    code = main(["--configure"])

    assert code == 0
    mock_save_config.assert_called_once_with(
        {
            "api_key": "sk-new-key-12345",
            "text_model": "openai",
            "vision_model": "openai-large",
            "language": "en",
        }
    )


@patch("builtins.input")
@patch("markitdown_pollinations.cli._clear_screen")
@patch("markitdown_pollinations.cli.convert_file")
@patch("markitdown_pollinations.cli.load_config")
def test_menu_convert_document(
    mock_load_config, mock_convert_file, mock_clear, mock_input, temp_file
):
    mock_load_config.return_value = {
        "api_key": "key",
        "text_model": "openai",
        "vision_model": "openai",
    }
    # Choose option 3 (document), provide file path, accept default output,
    # press Enter to continue, then quit
    mock_input.side_effect = ["3", temp_file, "", "", "5"]
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
@patch("markitdown_pollinations.cli._clear_screen")
@patch("markitdown_pollinations.cli.load_config")
def test_menu_quit(mock_load_config, mock_clear, mock_input):
    mock_load_config.return_value = {
        "api_key": "key",
        "text_model": "openai",
        "vision_model": "openai",
    }
    mock_input.side_effect = ["5"]

    code = main([])

    assert code == 0


@patch("markitdown_pollinations.cli.load_config")
def test_version_flag(mock_load_config, capsys):
    """T5.1: --version exits 0 and prints the expected version string."""
    mock_load_config.return_value = {
        "api_key": "key",
        "text_model": "openai",
        "vision_model": "openai",
    }

    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "Markitdown-for-everyone 0.3.1" in captured.out


@pytest.mark.parametrize("value", ["b", "back", "B", "BACK"])
def test_is_cancel_input_detects_back_variants(value):
    """T5.2: _is_cancel_input returns True for back/cancel shortcuts."""
    assert _is_cancel_input(value) is True


@patch("urllib.request.urlopen")
def test_validate_key_via_api_non_json_balance_response(mock_urlopen):
    """T5.3: _validate_key_via_api handles non-JSON balance response gracefully."""
    # Balance endpoint returns non-JSON.
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"not json at all"
    mock_resp.status = 200
    mock_urlopen.return_value.__enter__.return_value = mock_resp

    # Should not raise; falls through to chat-completion or returns "unknown".
    result = _validate_key_via_api("sk-test-key")

    # Should fall through without raising.
    assert result in ("valid", "unknown")


def test_no_unicode_arrow_in_cli_output(capsys):
    """T5.4: No user-facing strings contain the Unicode arrow \\u2192.

    Regression test: a previous version used the Unicode arrow character (→, U+2192)
    in user-facing strings, which broke on terminals without Unicode support.
    This test ensures no such characters are reintroduced.
    After T4, validation.py also has user-facing strings — see
    test_no_unicode_arrow_in_validation_output in test_validation.py.
    """
    import inspect

    import markitdown_pollinations.cli as cli_module

    source = inspect.getsource(cli_module)
    lines = source.splitlines()
    violations = []
    for lineno, line in enumerate(lines, start=1):
        # Check lines that produce user-visible output.
        if ("print(" in line or 'f"' in line or "f'" in line) and (
            "\\u2192" in line or "→" in line
        ):
            violations.append(f"line {lineno}: {line.strip()}")

    assert not violations, "Non-ASCII or \\u2192 found in cli.py:\n" + "\n".join(violations)


@pytest.mark.parametrize("value", ["c", "C", "cancel", "CANCEL", "  Cancel  "])
def test_is_cancel_input_detects_cancel_variants(value):
    assert _is_cancel_input(value) is True


def test_is_cancel_input_rejects_regular_text():
    assert _is_cancel_input("openai") is False
    assert _is_cancel_input("") is False


@patch("getpass.getpass")
def test_prompt_for_api_key_returns_cancel_token(mock_getpass):
    mock_getpass.return_value = "c"
    assert _prompt_for_api_key("") is None


@patch("getpass.getpass")
def test_prompt_for_api_key_keeps_existing_key_on_empty_input(mock_getpass):
    mock_getpass.return_value = ""
    assert _prompt_for_api_key("sk-existing-key-123") == "sk-existing-key-123"


@patch("builtins.input")
def test_ask_file_returns_cancel_token(mock_input):
    mock_input.return_value = "cancel"
    assert _ask_file("File path") is None


@patch("builtins.input")
def test_ask_output_returns_cancel_token(mock_input):
    mock_input.return_value = "c"
    assert _ask_output("input.pdf") is None


@patch("builtins.input")
def test_ask_model_returns_cancel_token(mock_input):
    mock_input.return_value = "c"
    assert _ask_model("Pick a model", ["openai", "glm"], "openai") is None


@patch("builtins.input")
def test_confirm_overwrite_allows_existing_file_when_confirmed(mock_input, tmp_path):
    existing = tmp_path / "out.md"
    existing.write_text("old", encoding="utf-8")
    mock_input.return_value = "y"
    assert _confirm_overwrite(str(existing)) is True


@patch("builtins.input")
def test_confirm_overwrite_rejects_existing_file_by_default(mock_input, tmp_path):
    existing = tmp_path / "out.md"
    existing.write_text("old", encoding="utf-8")
    mock_input.return_value = "n"
    assert _confirm_overwrite(str(existing)) is False


def test_confirm_overwrite_returns_true_for_missing_file(tmp_path):
    missing = tmp_path / "does-not-exist.md"
    assert _confirm_overwrite(str(missing)) is True


def test_color_respects_no_color(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    _reset_no_color_cache()
    assert _color("hello", "\033[31m") == "hello"


def test_color_adds_ansi_when_no_color_not_set():
    _reset_no_color_cache()
    assert _color("hello", "\033[31m") == "\033[31mhello\033[0m"


def test_clear_screen_respects_no_clear(monkeypatch, capsys):
    monkeypatch.setenv("NO_CLEAR", "1")
    _clear_screen()
    captured = capsys.readouterr()
    assert captured.out == ""


def test_clear_screen_emits_ansi_escape_by_default(capsys):
    _clear_screen()
    captured = capsys.readouterr()
    assert captured.out == "\033[2J\033[H"


@patch("builtins.input")
@patch("markitdown_pollinations.cli._clear_screen")
@patch("markitdown_pollinations.cli.load_config")
def test_main_handles_keyboard_interrupt_gracefully(mock_load_config, mock_clear, mock_input):
    mock_load_config.return_value = {
        "api_key": "key",
        "text_model": "openai",
        "vision_model": "openai",
    }
    mock_input.side_effect = KeyboardInterrupt()

    code = main([])

    assert code == 130


@patch("builtins.input")
@patch("markitdown_pollinations.cli.convert_file")
@patch("markitdown_pollinations.cli.load_config")
def test_quick_convert_confirms_overwrite_and_cancels(
    mock_load_config, mock_convert_file, mock_input, temp_file
):
    mock_load_config.return_value = {
        "api_key": "key",
        "text_model": "openai",
        "vision_model": "openai",
    }
    # The first input answers the overwrite prompt (n), cancelling conversion.
    mock_input.return_value = "n"
    output_path = str(Path(temp_file).with_suffix(".md"))
    Path(output_path).write_text("old", encoding="utf-8")

    code = main([temp_file])

    assert code == 0
    mock_convert_file.assert_not_called()
