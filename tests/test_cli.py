"""Tests for the command-line interface."""

from __future__ import annotations

import locale
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import markitdown_pollinations.cli as cli
import markitdown_pollinations.constants as constants
import markitdown_pollinations.models as models
from markitdown_pollinations import __version__
from markitdown_pollinations.constants import (
    EXIT_ERROR,
    EXIT_INTERRUPTED,
    EXIT_NO_OUTPUT,
    EXIT_OK,
    EXIT_USAGE,
)
from markitdown_pollinations.converter import ConversionResult

BASE_CONFIG = {
    "api_key": "sk_configured_key_123",
    "text_model": "openai",
    "vision_model": "openai",
    "language": "en",
}


@pytest.fixture(autouse=True)
def _offline_catalog(monkeypatch):
    """Never hit the network from CLI tests by default."""
    monkeypatch.setattr(cli.models, "fetch_catalog", lambda **kwargs: None)


@pytest.fixture
def configured(monkeypatch):
    """Patch config loading for an already-configured user."""
    monkeypatch.setattr(cli, "load_config", lambda: dict(BASE_CONFIG))
    monkeypatch.setattr(cli, "save_config", lambda config: True)
    monkeypatch.setattr(cli, "_stdout_is_tty", lambda: False)
    monkeypatch.setattr(cli, "_detect_system_language", lambda: "en")
    return dict(BASE_CONFIG)


@pytest.fixture
def unconfigured(monkeypatch):
    """Patch config loading for a user without an API key."""
    monkeypatch.setattr(
        cli,
        "load_config",
        lambda: {**BASE_CONFIG, "api_key": "", "language": ""},
    )
    monkeypatch.setattr(cli, "save_config", lambda config: True)
    monkeypatch.setattr(cli, "_stdout_is_tty", lambda: False)
    monkeypatch.setattr(cli, "_detect_system_language", lambda: "en")


@pytest.fixture
def temp_input(tmp_path):
    path = tmp_path / "input.txt"
    path.write_text("hello", encoding="utf-8")
    return str(path)


def _inputs(*values):
    return patch("builtins.input", side_effect=list(values))


def _password(value):
    return patch("getpass.getpass", return_value=value)


def _conversion_result(**kwargs) -> ConversionResult:
    defaults = {"success": True, "output_path": "out.md"}
    defaults.update(kwargs)
    return ConversionResult(**defaults)


def _catalog() -> models.ModelCatalog:
    return models.ModelCatalog(
        (
            models.ModelInfo(
                name="openai/gpt-5.4-nano",
                aliases=("openai", "openai-fast"),
                input_modalities=frozenset({"text", "image"}),
                paid_only=False,
            ),
            models.ModelInfo(
                name="z-ai/glm-5.2",
                aliases=("glm",),
                input_modalities=frozenset({"text"}),
                paid_only=True,
            ),
        )
    )


# ── Arguments, language and version ──────────────────────────────────────────


def test_parse_args_quick_convert_flags():
    args = cli.parse_args(
        [
            "file.pdf",
            "-o",
            "out.md",
            "-k",
            "key",
            "-m",
            "openai",
            "-y",
            "--non-interactive",
            "-q",
        ]
    )
    assert args.input_file == "file.pdf"
    assert args.output_file == "out.md"
    assert args.api_key == "key"
    assert args.model == "openai"
    assert args.yes is True
    assert args.non_interactive is True
    assert args.quiet is True


def test_parse_args_defaults():
    args = cli.parse_args(["file.pdf"])
    assert args.language is None
    assert args.yes is False
    assert args.non_interactive is False
    assert args.list_models is False


@pytest.mark.parametrize("language", ["en", "es"])
def test_parse_args_language_choices(language):
    assert cli.parse_args(["--language", language]).language == language


def test_parse_args_rejects_unknown_language():
    with pytest.raises(SystemExit):
        cli.parse_args(["--language", "fr"])


@pytest.mark.parametrize(
    "value",
    ["c", "C", "cancel", "cancelar", "b", "back", "volver", "s", "salir", "q", "quit", "exit"],
)
def test_is_cancel_input_accepts_shortcuts(value):
    assert cli._is_cancel_input(value) is True


@pytest.mark.parametrize("value", ["openai", "", "123", "salirr"])
def test_is_cancel_input_rejects_regular_text(value):
    assert cli._is_cancel_input(value) is False


def test_detect_system_language_spanish_locale(monkeypatch):
    monkeypatch.setattr(locale, "getlocale", lambda: ("es_ES", "UTF-8"))
    assert cli._detect_system_language() == "es"


def test_detect_system_language_windows_spanish_name(monkeypatch):
    monkeypatch.setattr(locale, "getlocale", lambda: ("Spanish_Colombia", "1252"))
    assert cli._detect_system_language() == "es"


def test_detect_system_language_english_name(monkeypatch):
    monkeypatch.setattr(locale, "getlocale", lambda: ("English_United States", "1252"))
    assert cli._detect_system_language() == "en"


def test_detect_system_language_falls_back_to_environment(monkeypatch):
    monkeypatch.setattr(locale, "getlocale", lambda: (None, None))
    for variable in ("LC_ALL", "LC_MESSAGES", "LANG", "LANGUAGE"):
        monkeypatch.delenv(variable, raising=False)
    monkeypatch.setenv("LANG", "es_CO.UTF-8")
    assert cli._detect_system_language() == "es"


def test_resolve_language_precedence(monkeypatch):
    monkeypatch.setattr(cli, "_detect_system_language", lambda: "es")
    assert cli._resolve_language("en", {"language": "es"}) == "en"
    assert cli._resolve_language(None, {"language": "es"}) == "es"
    assert cli._resolve_language(None, {"language": ""}) == "es"
    assert cli._resolve_language(None, {}) == "es"


def test_prescan_language():
    assert cli._prescan_language(["-l", "es", "file.pdf"]) == "es"
    assert cli._prescan_language(["--language=en"]) == "en"
    assert cli._prescan_language(["--language", "fr"]) is None
    assert cli._prescan_language(["file.pdf"]) is None


def test_help_is_localized_from_saved_language(configured, monkeypatch, capsys):
    monkeypatch.setattr(cli, "load_config", lambda: {**BASE_CONFIG, "language": "es"})
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["--help"])
    assert excinfo.value.code == 0
    assert "Idioma de la interfaz" in capsys.readouterr().out


def test_version_uses_single_source(configured, capsys):
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["--version"])
    assert excinfo.value.code == 0
    assert f"Markitdown-for-everyone {__version__}" in capsys.readouterr().out


def test_saved_language_is_used_at_startup(configured, monkeypatch, capsys):
    monkeypatch.setattr(cli, "load_config", lambda: {**BASE_CONFIG, "language": "es"})
    with _inputs("5"):
        assert cli.main([]) == EXIT_OK
    assert "por Angel Romero" in capsys.readouterr().out


def test_cli_language_overrides_saved_language(configured, monkeypatch, capsys):
    monkeypatch.setattr(cli, "load_config", lambda: {**BASE_CONFIG, "language": "es"})
    with _inputs("5"):
        assert cli.main(["--language", "en"]) == EXIT_OK
    assert "by Angel Romero" in capsys.readouterr().out


def test_quiet_suppresses_banner(configured, capsys):
    with _inputs("5"):
        assert cli.main(["--quiet"]) == EXIT_OK
    output = capsys.readouterr().out
    assert "Angel Romero" not in output
    assert "Goodbye" in output


# ── Prompts ──────────────────────────────────────────────────────────────────


def test_prompt_for_api_key_keeps_current(monkeypatch):
    monkeypatch.setattr(cli.getpass, "getpass", lambda prompt: "")
    assert cli._prompt_for_api_key("sk_existing_123456") == "sk_existing_123456"


def test_prompt_for_api_key_cancel(monkeypatch):
    monkeypatch.setattr(cli.getpass, "getpass", lambda prompt: "c")
    assert cli._prompt_for_api_key("") is None


def test_prompt_for_api_key_requires_value_when_empty(monkeypatch, capsys):
    monkeypatch.setattr(cli.getpass, "getpass", lambda prompt: "   ")
    assert cli._prompt_for_api_key("") is None
    assert "required" in capsys.readouterr().err


def test_prompt_for_api_key_marks_environment_source(monkeypatch):
    prompts: list[str] = []

    def fake_getpass(prompt):
        prompts.append(prompt)
        return ""

    monkeypatch.setattr(cli.getpass, "getpass", fake_getpass)
    assert cli._prompt_for_api_key("sk_env_key_123456", from_env=True) == "sk_env_key_123456"
    assert "from environment" in prompts[0]


def test_ask_file_retries_then_cancels(capsys):
    with _inputs("missing.txt", "cancel"):
        assert cli._ask_file("File path") is None
    assert "File not found" in capsys.readouterr().err


def test_ask_output_rejects_input_path(temp_input):
    with _inputs(temp_input, ""):
        output = cli._ask_output(temp_input)
    assert output is not None
    assert output != temp_input
    assert output.endswith(".md")


def test_confirm_overwrite_cases(tmp_path):
    missing = tmp_path / "missing.md"
    assert cli._confirm_overwrite(str(missing)) is True

    existing = tmp_path / "existing.md"
    existing.write_text("old", encoding="utf-8")
    with _inputs("y"):
        assert cli._confirm_overwrite(str(existing)) is True
    with _inputs("n"):
        assert cli._confirm_overwrite(str(existing)) is False
    assert cli._confirm_overwrite(str(existing), assume_yes=True) is True
    with pytest.raises(cli.NonInteractiveError):
        cli._confirm_overwrite(str(existing), non_interactive=True)


def test_ask_model_selects_recommendation(monkeypatch, capsys):
    monkeypatch.setattr(cli.models, "fetch_catalog", lambda **kwargs: _catalog())
    with _inputs("1"):
        assert cli._ask_model("Model", ["openai", "glm"], "openai") == "openai"
    assert "(vision)" in capsys.readouterr().out


def test_ask_model_other_warns_unknown(monkeypatch, capsys):
    monkeypatch.setattr(cli.models, "fetch_catalog", lambda **kwargs: _catalog())
    with _inputs("0", "mystery-model"):
        assert cli._ask_model("Model", ["openai"], "openai") == "mystery-model"
    assert "not found in the live catalog" in capsys.readouterr().err


def test_ask_model_warns_non_vision(monkeypatch, capsys):
    monkeypatch.setattr(cli.models, "fetch_catalog", lambda **kwargs: _catalog())
    with _inputs("1"):
        assert cli._ask_model("Model", ["glm"], "glm", vision=True) == "glm"
    assert "does not accept image input" in capsys.readouterr().err


def test_ask_model_cancel(monkeypatch):
    monkeypatch.setattr(cli.models, "fetch_catalog", lambda **kwargs: None)
    with _inputs("c"):
        assert cli._ask_model("Model", ["openai"], "openai") is None


def test_ask_model_invalid_then_valid(monkeypatch):
    monkeypatch.setattr(cli.models, "fetch_catalog", lambda **kwargs: None)
    with _inputs("99", "1"):
        assert cli._ask_model("Model", ["openai"], "openai") == "openai"


# ── Configuration flows ──────────────────────────────────────────────────────


def test_configure_updates_models(configured, monkeypatch):
    saved: list[dict] = []
    monkeypatch.setattr(cli, "_validate_key_via_api", lambda key: "valid")
    monkeypatch.setattr(cli, "save_config", lambda config: saved.append(dict(config)) or True)
    with _inputs("1", "1", "2"), _password("sk_new_key_123456"):
        assert cli.main(["--configure"]) == EXIT_OK

    final = saved[-1]
    assert final["api_key"] == "sk_new_key_123456"
    assert final["text_model"] == "openai"
    assert final["vision_model"] == "openai-large"
    assert final["language"] == "en"


def test_configure_continues_when_validation_is_offline(configured, monkeypatch, capsys):
    saved: list[dict] = []
    monkeypatch.setattr(cli, "_validate_key_via_api", lambda key: "unknown")
    monkeypatch.setattr(cli, "save_config", lambda config: saved.append(dict(config)) or True)
    with _inputs("1", "1", "1"), _password("sk_new_key_123456"):
        assert cli.main(["--configure"]) == EXIT_OK
    assert saved
    assert "could not verify" in capsys.readouterr().out


def test_configure_cancel_at_key_prompt(unconfigured, monkeypatch, capsys):
    monkeypatch.setattr(cli, "_validate_key_via_api", lambda key: "valid")
    with _inputs("1"), _password("c"):
        assert cli.main(["--configure"]) == EXIT_OK
    assert "required to use the program" in capsys.readouterr().err


def test_configure_cancel_at_language_selector(configured, capsys):
    with _inputs("c"):
        assert cli.main(["--configure"]) == EXIT_OK
    assert "required to use the program" in capsys.readouterr().err


def test_configure_keeps_env_key_marker(monkeypatch):
    saved: list[dict] = []
    config = {
        **BASE_CONFIG,
        "api_key": "env_key",
        "api_key_from_env": True,
    }
    monkeypatch.setattr(cli, "load_config", lambda: dict(config))
    monkeypatch.setattr(cli, "_stdout_is_tty", lambda: False)
    monkeypatch.setattr(cli, "_detect_system_language", lambda: "en")
    monkeypatch.setattr(cli, "_validate_key_via_api", lambda key: "valid")
    monkeypatch.setattr(cli, "save_config", lambda value: saved.append(dict(value)) or True)

    with _inputs("1", "1", "1"), _password(""):
        assert cli.main(["--configure"]) == EXIT_OK

    final = saved[-1]
    assert final["api_key"] == "env_key"
    assert final["api_key_from_env"] is True


def test_configure_new_key_clears_env_marker(monkeypatch):
    saved: list[dict] = []
    config = {**BASE_CONFIG, "api_key": "env_key", "api_key_from_env": True}
    monkeypatch.setattr(cli, "load_config", lambda: dict(config))
    monkeypatch.setattr(cli, "_stdout_is_tty", lambda: False)
    monkeypatch.setattr(cli, "_detect_system_language", lambda: "en")
    monkeypatch.setattr(cli, "_validate_key_via_api", lambda key: "valid")
    monkeypatch.setattr(cli, "save_config", lambda value: saved.append(dict(value)) or True)

    with _inputs("1", "1", "1"), _password("sk_manual_key_123456"):
        assert cli.main(["--configure"]) == EXIT_OK

    final = saved[-1]
    assert final["api_key"] == "sk_manual_key_123456"
    assert "api_key_from_env" not in final


def test_first_run_wizard_on_menu(monkeypatch):
    saved: list[dict] = []
    monkeypatch.setattr(
        cli,
        "load_config",
        lambda: {**BASE_CONFIG, "api_key": "", "language": ""},
    )
    monkeypatch.setattr(cli, "_stdout_is_tty", lambda: False)
    monkeypatch.setattr(cli, "_detect_system_language", lambda: "en")
    monkeypatch.setattr(cli, "_validate_key_via_api", lambda key: "valid")
    monkeypatch.setattr(cli, "save_config", lambda config: saved.append(dict(config)) or True)

    with _inputs("1", "1", "1", "5"), _password("sk_first_run_123456"):
        assert cli.main([]) == EXIT_OK

    assert saved[-1]["api_key"] == "sk_first_run_123456"


def test_non_interactive_configure_is_rejected(configured):
    with patch("builtins.input", side_effect=AssertionError("input must not be called")):
        assert cli.main(["--configure", "--non-interactive"]) == EXIT_USAGE


# ── Menu ─────────────────────────────────────────────────────────────────────


def test_menu_quit(configured, capsys):
    with _inputs("5"):
        assert cli.main([]) == EXIT_OK
    assert "Goodbye" in capsys.readouterr().out


def test_menu_convert_document(configured, temp_input, monkeypatch):
    monkeypatch.setattr(cli, "convert_file", lambda *args: _conversion_result())
    with _inputs("3", temp_input, "", "", "5"):
        assert cli.main([]) == EXIT_OK


def test_menu_convert_image_without_key(tmp_path, monkeypatch, capsys):
    image = tmp_path / "image.png"
    image.write_text("not-really-an-image", encoding="utf-8")
    convert = MagicMock()
    monkeypatch.setattr(cli, "convert_file", convert)
    config = {**BASE_CONFIG, "api_key": ""}

    with _inputs(str(image), ""):
        code = cli.convert_menu_option(config, "Image")

    assert code == EXIT_ERROR
    convert.assert_not_called()
    assert "API key is required to convert images" in capsys.readouterr().err


def test_menu_option_four_changes_language(configured, monkeypatch):
    saved: list[dict] = []
    monkeypatch.setattr(cli, "save_config", lambda config: saved.append(dict(config)) or True)
    with _inputs("4", "2", "c", "", "5"), _password("c"):
        assert cli.main([]) == EXIT_OK
    assert any(config.get("language") == "es" for config in saved)


def test_menu_invalid_option(configured, capsys):
    with _inputs("9", "", "5"):
        assert cli.main([]) == EXIT_OK
    assert "Invalid option" in capsys.readouterr().out


# ── Quick conversion ─────────────────────────────────────────────────────────


def test_quick_convert_success(configured, temp_input, monkeypatch):
    convert = MagicMock(return_value=_conversion_result())
    monkeypatch.setattr(cli, "convert_file", convert)

    assert cli.main([temp_input]) == EXIT_OK
    args = convert.call_args.args
    assert args[0] == temp_input
    assert args[1] == str(Path(temp_input).with_suffix(".md"))
    assert args[2] == BASE_CONFIG["api_key"]
    assert args[3] == "openai"


def test_quick_convert_without_key_allows_text_formats(unconfigured, temp_input, monkeypatch):
    convert = MagicMock(return_value=_conversion_result())
    monkeypatch.setattr(cli, "convert_file", convert)

    assert cli.main([temp_input]) == EXIT_OK
    assert convert.call_args.args[2] is None


def test_quick_convert_image_requires_key(unconfigured, tmp_path, monkeypatch, capsys):
    image = tmp_path / "photo.png"
    image.write_text("x", encoding="utf-8")
    convert = MagicMock()
    monkeypatch.setattr(cli, "convert_file", convert)

    assert cli.main([str(image)]) == EXIT_ERROR
    convert.assert_not_called()
    assert "API key is required to convert images" in capsys.readouterr().err


def test_quick_convert_missing_file(configured, capsys):
    assert cli.main(["does-not-exist.txt"]) == EXIT_USAGE
    assert "File not found" in capsys.readouterr().err


def test_quick_convert_rejects_output_same_as_input(configured, temp_input, monkeypatch, capsys):
    convert = MagicMock()
    monkeypatch.setattr(cli, "convert_file", convert)

    assert cli.main([temp_input, "-o", temp_input]) == EXIT_USAGE
    convert.assert_not_called()
    assert "different from" in capsys.readouterr().err


def test_quick_convert_non_interactive_overwrite_requires_yes(
    configured, temp_input, monkeypatch, capsys
):
    output = Path(temp_input).with_suffix(".md")
    output.write_text("old", encoding="utf-8")
    convert = MagicMock()
    monkeypatch.setattr(cli, "convert_file", convert)

    assert cli.main([temp_input, "--non-interactive"]) == EXIT_USAGE
    convert.assert_not_called()
    assert "--yes" in capsys.readouterr().err


def test_quick_convert_overwrite_with_yes(configured, temp_input, monkeypatch):
    output = Path(temp_input).with_suffix(".md")
    output.write_text("old", encoding="utf-8")
    convert = MagicMock(return_value=_conversion_result())
    monkeypatch.setattr(cli, "convert_file", convert)

    assert cli.main([temp_input, "--yes"]) == EXIT_OK
    convert.assert_called_once()


def test_quick_convert_overwrite_declined(configured, temp_input, monkeypatch, capsys):
    output = Path(temp_input).with_suffix(".md")
    output.write_text("old", encoding="utf-8")
    convert = MagicMock()
    monkeypatch.setattr(cli, "convert_file", convert)

    with _inputs("n"):
        assert cli.main([temp_input]) == EXIT_OK
    convert.assert_not_called()
    assert "Overwrite cancelled" in capsys.readouterr().out


def test_quick_convert_failure_exit_code(configured, temp_input, monkeypatch):
    monkeypatch.setattr(
        cli,
        "convert_file",
        lambda *args: ConversionResult(success=False, message="boom"),
    )
    assert cli.main([temp_input]) == EXIT_ERROR


def test_quick_convert_no_output_exit_code(configured, temp_input, monkeypatch):
    monkeypatch.setattr(
        cli,
        "convert_file",
        lambda *args: ConversionResult(success=True, warning="empty"),
    )
    assert cli.main([temp_input]) == EXIT_NO_OUTPUT


def test_vision_fallback_retries_with_different_model(configured, tmp_path, monkeypatch, capsys):
    source = tmp_path / "input.txt"
    source.write_text("hi", encoding="utf-8")
    convert = MagicMock(
        side_effect=[
            ConversionResult(success=True, warning="empty"),
            ConversionResult(success=True, output_path="out.md"),
        ]
    )
    monkeypatch.setattr(cli, "convert_file", convert)

    code = cli._run_conversion(str(source), "out.md", "key", "text-model", "vision-model")
    assert code == EXIT_OK
    assert convert.call_count == 2
    assert convert.call_args.args[3] == "vision-model"
    assert "retrying with vision model" in capsys.readouterr().out


def test_vision_fallback_skipped_for_same_model(configured, tmp_path, monkeypatch):
    source = tmp_path / "input.txt"
    source.write_text("hi", encoding="utf-8")
    convert = MagicMock(return_value=ConversionResult(success=True, warning="empty"))
    monkeypatch.setattr(cli, "convert_file", convert)

    code = cli._run_conversion(str(source), "out.md", "key", "openai", "openai")
    assert code == EXIT_NO_OUTPUT
    assert convert.call_count == 1


def test_vision_fallback_skipped_for_images(configured, tmp_path, monkeypatch):
    source = tmp_path / "input.png"
    source.write_text("hi", encoding="utf-8")
    convert = MagicMock(return_value=ConversionResult(success=True, warning="empty"))
    monkeypatch.setattr(cli, "convert_file", convert)

    code = cli._run_conversion(str(source), "out.md", "key", "openai", "claude")
    assert code == EXIT_NO_OUTPUT
    assert convert.call_count == 1


# ── Non-interactive input, interrupts and terminal behaviour ─────────────────


def test_main_eof_returns_usage(configured, capsys):
    with patch("builtins.input", side_effect=EOFError):
        assert cli.main([]) == EXIT_USAGE
    assert "stdin is closed" in capsys.readouterr().err


def test_quick_convert_eof_at_overwrite_returns_usage(configured, temp_input, capsys):
    output = Path(temp_input).with_suffix(".md")
    output.write_text("old", encoding="utf-8")
    with patch("builtins.input", side_effect=EOFError):
        assert cli.main([temp_input]) == EXIT_USAGE
    assert "interactive input" in capsys.readouterr().err


def test_keyboard_interrupt_returns_130(configured):
    with patch("builtins.input", side_effect=KeyboardInterrupt):
        assert cli.main([]) == EXIT_INTERRUPTED


def test_keyboard_interrupt_during_conversion_returns_130(configured, temp_input, monkeypatch):
    monkeypatch.setattr(cli, "convert_file", MagicMock(side_effect=KeyboardInterrupt))
    assert cli.main([temp_input]) == EXIT_INTERRUPTED


def test_main_non_interactive_without_input(configured, capsys):
    assert cli.main(["--non-interactive"]) == EXIT_USAGE
    assert "non-interactive" in capsys.readouterr().err


def test_clear_screen_respects_tty_and_no_clear(monkeypatch, capsys):
    monkeypatch.setattr(cli, "_stdout_is_tty", lambda: False)
    cli._clear_screen()
    assert capsys.readouterr().out == ""

    monkeypatch.setattr(cli, "_stdout_is_tty", lambda: True)
    cli._clear_screen()
    assert capsys.readouterr().out == "\033[2J\033[H"

    monkeypatch.setenv("NO_CLEAR", "1")
    cli._clear_screen()
    assert capsys.readouterr().out == ""


def test_color_helpers(monkeypatch):
    monkeypatch.setattr(constants, "_color_cache", True)
    assert constants._color("hello", "\033[31m") == "\033[31mhello\033[0m"

    monkeypatch.setattr(constants, "_color_cache", False)
    assert constants._color("hello", "\033[31m") == "hello"


def test_spinner_disabled_is_silent(capsys):
    with cli._Spinner(enabled=False):
        pass
    assert capsys.readouterr().out == ""


def test_list_models_offline(configured, capsys):
    assert cli.main(["--list-models"]) == EXIT_OK
    output = capsys.readouterr().out
    assert "built-in list" in output
    assert "openai" in output


def test_list_models_with_catalog(configured, monkeypatch, capsys):
    monkeypatch.setattr(cli.models, "fetch_catalog", lambda **kwargs: _catalog())
    assert cli.main(["--list-models"]) == EXIT_OK
    assert "openai (vision)" in capsys.readouterr().out


def test_module_entrypoint_version():
    repo_root = Path(__file__).resolve().parents[1]
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(repo_root / "src")
    process = subprocess.run(
        [sys.executable, "-m", "markitdown_pollinations", "--version"],
        cwd=repo_root,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert process.returncode == 0
    assert __version__ in process.stdout


def test_cancel_exit_returns_ok():
    assert cli._cancel_exit() == EXIT_OK
