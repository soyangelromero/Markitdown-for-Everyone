"""Command-line interface for MarkItDown for Everyone."""

from __future__ import annotations

import argparse
import getpass
import itertools
import logging
import os
import sys
import threading
import time
from collections.abc import Sequence
from pathlib import Path
from types import TracebackType

from markitdown_pollinations import __version__, models
from markitdown_pollinations.config import (
    DEFAULT_CONFIG,
    RuntimeConfig,
    load_config,
    save_config,
)
from markitdown_pollinations.constants import (
    EXIT_ERROR,
    EXIT_INTERRUPTED,
    EXIT_NO_OUTPUT,
    EXIT_OK,
    EXIT_USAGE,
    IMAGE_EXTENSIONS,
    OCR_EXTENSIONS,
    RECOMMENDED_TEXT_MODELS,
    RECOMMENDED_VISION_MODELS,
    VISION_MODELS,
    Colors,
    _color,
)
from markitdown_pollinations.converter import ConversionResult, convert_file
from markitdown_pollinations.i18n import LANGUAGES, _, set_language
from markitdown_pollinations.validation import (
    _mask_key,
    _validate_key_via_api,
    _warn_if_key_invalid,
)

logger = logging.getLogger("markitdown_pollinations")

_CANCEL_INPUT = frozenset(
    {"c", "cancel", "cancelar", "b", "back", "volver", "s", "salir", "q", "quit", "exit"}
)


class NonInteractiveError(RuntimeError):
    """Raised when interactive input is required but stdin is unavailable."""


def _is_cancel_input(value: str) -> bool:
    """Return True if the user typed a cancel/back command."""
    return value.strip().lower() in _CANCEL_INPUT


def _read_input(prompt: str) -> str:
    """Read from stdin, translating EOF into a friendly non-interactive error."""
    try:
        return input(prompt)
    except EOFError as exc:
        raise NonInteractiveError from exc


def _read_secret(prompt: str) -> str:
    """Read a hidden value, translating EOF into a non-interactive error."""
    try:
        return getpass.getpass(prompt)
    except EOFError as exc:
        raise NonInteractiveError from exc


def _stdout_is_tty() -> bool:
    """Return True when stdout is an interactive terminal."""
    try:
        return bool(sys.stdout.isatty())
    except (AttributeError, ValueError):
        return False


def _enable_ansi_windows() -> None:
    """Enable ANSI escape sequences on Windows terminals (best effort)."""
    if os.name != "nt" or not _stdout_is_tty():
        return
    try:
        import ctypes

        windll = getattr(ctypes, "windll", None)
        if windll is None:
            return
        kernel = windll.kernel32
        handle = kernel.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint32()
        kernel.GetConsoleMode(handle, ctypes.byref(mode))
        mode.value |= 0x0004  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
        kernel.SetConsoleMode(handle, mode)
    except (AttributeError, OSError):
        return


def _clear_screen() -> None:
    """Clear the terminal, unless disabled or stdout is not a TTY."""
    if os.environ.get("NO_CLEAR") or not _stdout_is_tty():
        return
    print("\033[2J\033[H", end="")


def print_banner() -> None:
    """Print the program banner."""
    art = r"""
 __  __            _    _ _      _                            __
|  \/  | __ _ _ __| | _(_) |_ __| | _____      ___ __        / _| ___  _ __
| |\/| |/ _` | '__| |/ / | __/ _` |/ _ \ \ /\ / / '_ \ _____| |_ / _ \| '__|
| |  | | (_| | |  |   <| | || (_| | (_) \ V  V /| | | |_____|  _| (_) | |
|_|  |_|\__,_|_|  |_|\_\_|\__\__,_|\___/ \_/\_/ |_| |_|     |_|  \___/|_|
       _____
      | ____|_   _____ _ __ _   _  ___  _ __   ___
 _____|  _| \ \ / / _ \ '__| | | |/ _ \| '_ \ / _ \
|_____| |___ \ V /  __/ |  | |_| | (_) | | | |  __/
      |_____| \_/ \___|_|   \__, |\___/|_| |_|\___|
                            |___/
"""
    print(_color(art, Colors.CYAN))
    print(f"  {_('by')} {_color('Angel Romero', Colors.BOLD)} - https://github.com/soyangelromero")
    print(f"  v{__version__}\n")


# ── Language handling ────────────────────────────────────────────────────────


def _supported_language(value: str | None) -> str | None:
    if value is None:
        return None
    candidate = value.strip().lower()
    return candidate if candidate in LANGUAGES else None


def _detect_system_language() -> str:
    """Detect the system language, returning 'es' for Spanish locales."""
    import locale

    location: str | None = None
    try:
        location = locale.getlocale()[0]
    except (AttributeError, ValueError):
        location = None

    if not location:
        for variable in ("LC_ALL", "LC_MESSAGES", "LANG", "LANGUAGE"):
            raw = os.environ.get(variable, "").strip()
            if raw:
                location = raw.split(":")[0].split(".")[0]
                break

    if not location:
        return "en"
    # Windows reports names such as "Spanish_Colombia" or "English_United States".
    lowered = location.lower()
    return "es" if lowered.startswith(("es", "spanish")) else "en"


def _resolve_language(cli_language: str | None, config: RuntimeConfig) -> str:
    """Resolve language precedence: CLI flag > saved config > system locale."""
    explicit = _supported_language(cli_language)
    if explicit is not None:
        return explicit
    saved = _supported_language(config.get("language", ""))
    if saved is not None:
        return saved
    return _detect_system_language()


def _prescan_language(argv: Sequence[str]) -> str | None:
    """Find a --language value before argparse runs, so --help is localized."""
    tokens = list(argv)
    for index, token in enumerate(tokens):
        if token in ("-l", "--language") and index + 1 < len(tokens):
            return _supported_language(tokens[index + 1])
        if token.startswith("--language="):
            return _supported_language(token.split("=", 1)[1])
    return None


def _select_language(default: str = "en") -> str | None:
    """Show the language selector; return None when cancelled."""
    print(_color(f"\n{_('language_title')}", Colors.CYAN))
    print(_("language_prompt"))
    en_marker = "*" if default == "en" else " "
    es_marker = "*" if default == "es" else " "
    print(f"  1. {en_marker} {_('language_en')}")
    print(f"  2. {es_marker} {_('language_es')}")
    print(f"  {_('cancel_back')}")
    while True:
        choice = _read_input(_("select")).strip()
        if _is_cancel_input(choice):
            return None
        if choice == "1":
            return "en"
        if choice == "2":
            return "es"
        print(_color(_("invalid_option"), Colors.YELLOW))


# ── Prompts ──────────────────────────────────────────────────────────────────


def _prompt(text: str, default: str = "") -> str:
    """Prompt for a value, returning the default when the input is empty."""
    label = f"{text} [{default}]: " if default else f"{text}: "
    value = _read_input(label).strip()
    return value or default


def _prompt_for_api_key(current_key: str, *, from_env: bool = False) -> str | None:
    """Prompt for an API key; keep the current one on empty input."""
    prompt = _("api_key_prompt")
    if current_key:
        details = _mask_key(current_key)
        if from_env:
            details = f"{details}, {_('api_key_from_env')}"
        prompt += f" [{details}]"
    prompt += ": "

    api_key = _read_secret(prompt).strip()
    if _is_cancel_input(api_key):
        return None
    if not api_key:
        if current_key:
            return current_key
        print(_color(_("api_key_required_warn"), Colors.RED), file=sys.stderr)
        return None
    _warn_if_key_invalid(api_key)
    return api_key


def _warn_about_model(
    model: str,
    catalog: models.ModelCatalog | None,
    *,
    vision: bool,
) -> None:
    """Warn about unknown models or models without image support."""
    if catalog is None:
        return
    info = catalog.find(model)
    if info is None:
        print(
            _color(_("model_unknown_warning").format(model=model), Colors.YELLOW),
            file=sys.stderr,
        )
    elif vision and not info.accepts_images:
        print(
            _color(_("model_not_vision_warning").format(model=model), Colors.YELLOW),
            file=sys.stderr,
        )


def _ask_model(
    prompt: str,
    recommendations: Sequence[str],
    default: str,
    *,
    vision: bool = False,
) -> str | None:
    """Ask the user to pick or type a model; return None when cancelled."""
    catalog = models.fetch_catalog()
    options = list(recommendations)
    if catalog is not None:
        known = catalog.filter_known(options)
        if known:
            options = list(known)

    print(_color(f"\n{prompt}", Colors.CYAN))
    print(_("recommended"))
    for index, model in enumerate(options, start=1):
        marker = "*" if model == default else " "
        label = catalog.annotate(model) if catalog is not None else model
        print(f"  {index}. {marker} {label}")
    print(f"  0. {_('other_model')}")
    print(f"  {_('cancel_back')}")

    while True:
        choice = _read_input(_("select")).strip()
        if _is_cancel_input(choice):
            return None
        if choice == "0":
            typed = _prompt(_("enter_model_name"), default=default).strip()
            if _is_cancel_input(typed):
                return None
            selected = typed or default
            _warn_about_model(selected, catalog, vision=vision)
            return selected
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(options):
                selected = options[index - 1]
                _warn_about_model(selected, catalog, vision=vision)
                return selected
        print(_color(_("invalid_menu_option"), Colors.YELLOW))


def _ask_file(prompt: str) -> str | None:
    """Prompt for an existing file path; return None when cancelled."""
    while True:
        path = _read_input(f"{prompt} ({_('cancel_back')}): ").strip().strip('"')
        if _is_cancel_input(path):
            return None
        if Path(path).is_file():
            return path
        print(_color(_("file_not_found").format(path=path), Colors.RED), file=sys.stderr)


def _same_path(first: str, second: str) -> bool:
    """Return True when two paths refer to the same file."""
    try:
        return Path(first).resolve() == Path(second).resolve()
    except OSError:
        return os.path.abspath(first) == os.path.abspath(second)


def _ask_output(input_file: str) -> str | None:
    """Prompt for an output path with a sensible default and safe validation."""
    default = str(Path(input_file).with_suffix(".md"))
    while True:
        path = _prompt(_("ask_output"), default=default).strip().strip('"')
        if _is_cancel_input(path):
            return None
        path = path or default
        if _same_path(input_file, path):
            print(_color(_("output_same_as_input"), Colors.RED), file=sys.stderr)
            continue
        return path


def _confirm_overwrite(
    path: str, *, assume_yes: bool = False, non_interactive: bool = False
) -> bool:
    """Ask before overwriting an existing file."""
    if not Path(path).exists() or assume_yes:
        return True
    if non_interactive:
        raise NonInteractiveError(_("non_interactive_overwrite").format(path=path))
    answer = (
        _read_input(_color(_("overwrite_confirm").format(path=path), Colors.YELLOW)).strip().lower()
    )
    return answer in ("y", "yes", "s", "sí")


def _pause() -> None:
    """Wait for the user to press Enter (ignored when stdin is closed)."""
    try:
        input(_color(_("press_enter_continue"), Colors.CYAN))
    except EOFError:
        pass


# ── Configuration flows ──────────────────────────────────────────────────────


def _configure_flow(
    config: RuntimeConfig,
    *,
    header: str,
    welcome: str,
    text_prompt: str,
    vision_prompt: str,
    success_message: str,
) -> RuntimeConfig:
    """Shared configuration flow used by the wizard and the settings menu."""
    original: RuntimeConfig = config.copy()

    while True:
        print(_color(f"\n{header}", Colors.CYAN))
        if welcome:
            print(_color(welcome, Colors.GREEN))

        api_key = _prompt_for_api_key(
            config.get("api_key", ""),
            from_env=bool(config.get("api_key_from_env")),
        )
        if api_key is None:
            print(_color(f"\n{_('config_cancelled')}", Colors.YELLOW))
            return original

        print(_color(_("validating_key"), Colors.CYAN))
        result = _validate_key_via_api(api_key)
        if result == "valid":
            break
        if result == "invalid":
            print(_color(_("provide_valid_key"), Colors.YELLOW))
            _pause()
            continue
        # "unknown" usually means a network issue; continue rather than dead-end.
        print(_color(_("key_validation_offline"), Colors.YELLOW))
        break

    text_model = _ask_model(
        text_prompt,
        RECOMMENDED_TEXT_MODELS,
        config.get("text_model", DEFAULT_CONFIG["text_model"]),
    )
    if text_model is None:
        print(_color(f"\n{_('config_cancelled')}", Colors.YELLOW))
        return original

    vision_model = _ask_model(
        vision_prompt,
        RECOMMENDED_VISION_MODELS,
        config.get("vision_model", DEFAULT_CONFIG["vision_model"]),
        vision=True,
    )
    if vision_model is None:
        print(_color(f"\n{_('config_cancelled')}", Colors.YELLOW))
        return original

    new_config: RuntimeConfig = config.copy()
    new_config["api_key"] = api_key
    new_config["text_model"] = text_model
    new_config["vision_model"] = vision_model
    new_config["language"] = _resolve_language(None, config)

    key_from_env = bool(config.get("api_key_from_env")) and api_key == config.get("api_key", "")
    if key_from_env:
        new_config["api_key_from_env"] = True
    else:
        new_config.pop("api_key_from_env", None)

    if save_config(new_config):
        print(_color(f"\n{success_message}", Colors.GREEN))
    else:
        print(_color(f"\n{_('error_save_config')}", Colors.RED), file=sys.stderr)
    return new_config


def setup_wizard(config: RuntimeConfig) -> RuntimeConfig:
    """Run the first-time configuration wizard."""
    return _configure_flow(
        config,
        header=_("welcome_title"),
        welcome=_("setup_intro"),
        text_prompt=_("model_for_text"),
        vision_prompt=_("model_for_images"),
        success_message=_("config_saved"),
    )


def configure_menu(config: RuntimeConfig) -> RuntimeConfig:
    """Show the configuration menu and update settings."""
    return _configure_flow(
        config,
        header=_("menu_configure"),
        welcome="",
        text_prompt=_("model_for_text_short"),
        vision_prompt=_("model_for_images_short"),
        success_message=_("config_updated"),
    )


def _choose_and_save_language(config: RuntimeConfig) -> RuntimeConfig | None:
    """Show the language selector, persist the choice and apply it."""
    chosen = _select_language(default=_resolve_language(None, config))
    if chosen is None:
        return None
    config["language"] = chosen
    set_language(chosen)
    save_config(config)
    return config


def _needs_setup(config: RuntimeConfig) -> bool:
    """Return True when no API key is configured."""
    return not config.get("api_key", "").strip()


# ── Conversion ───────────────────────────────────────────────────────────────


class _Spinner:
    """Small ASCII spinner that only animates on an interactive terminal."""

    def __init__(self, *, enabled: bool) -> None:
        self.enabled = enabled
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def _spin(self) -> None:
        for frame in itertools.cycle("-\\|/"):
            if self._stop.is_set():
                break
            sys.stdout.write(f"\r{frame} {_('spinner_text')}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * 30 + "\r")
        sys.stdout.flush()

    def __enter__(self) -> _Spinner:
        if self.enabled:
            self._thread = threading.Thread(target=self._spin)
            self._thread.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._thread is None:
            return
        self._stop.set()
        self._thread.join()


def _model_for_file(config: RuntimeConfig, input_file: str) -> str:
    """Choose the right model based on the file type."""
    if Path(input_file).suffix.lower() in IMAGE_EXTENSIONS:
        return config.get("vision_model", DEFAULT_CONFIG["vision_model"]) or "openai"
    return config.get("text_model", DEFAULT_CONFIG["text_model"]) or "openai"


def _needs_vision_retry(
    result: ConversionResult, suffix: str, model: str, vision_model: str
) -> bool:
    """Return True when an empty non-image conversion should retry with vision."""
    return bool(
        result.success
        and result.warning
        and vision_model != model
        and suffix not in IMAGE_EXTENSIONS
    )


def _report_result(result: ConversionResult) -> int:
    """Print the conversion outcome and return the corresponding exit code."""
    if not result.success:
        print(
            _color(_("error_prefix").format(message=result.message), Colors.RED),
            file=sys.stderr,
        )
        return EXIT_ERROR
    if result.output_path is None:
        print(_color(_("no_output_empty"), Colors.YELLOW), file=sys.stderr)
        return EXIT_NO_OUTPUT
    print(_color(_("done").format(output=result.output_path), Colors.GREEN))
    if result.warning:
        print(_color(_("warning_prefix").format(warning=result.warning), Colors.YELLOW))
    return EXIT_OK


def _run_conversion(
    input_file: str,
    output_file: str,
    api_key: str | None,
    model: str,
    vision_model: str | None,
    *,
    quiet: bool = False,
) -> int:
    """Run a conversion, retrying with the vision model when useful."""
    suffix = Path(input_file).suffix.lower()
    if suffix in IMAGE_EXTENSIONS and model not in VISION_MODELS:
        print(
            _color(_("not_vision_info").format(model=model), Colors.CYAN),
            file=sys.stderr,
        )

    logger.info(_("converting").format(input=input_file, output=output_file, model=model))
    spinner_enabled = not quiet and _stdout_is_tty()

    with _Spinner(enabled=spinner_enabled):
        result = convert_file(input_file, output_file, api_key, model)

    if vision_model is not None and _needs_vision_retry(result, suffix, model, vision_model):
        print(_color(_("no_text_found").format(model=vision_model), Colors.YELLOW))
        with _Spinner(enabled=spinner_enabled):
            vision_result = convert_file(input_file, output_file, api_key, vision_model)
        if vision_result.success and not vision_result.warning:
            result = vision_result

    return _report_result(result)


def convert_menu_option(config: RuntimeConfig, file_kind: str) -> int:
    """Handle a conversion option from the main menu."""
    kind = _("file_kind_" + file_kind.lower())
    print(_color(_("convert_title").format(kind=kind), Colors.CYAN))
    input_file = _ask_file(_("ask_file"))
    if input_file is None:
        print(_color(_("cancelled"), Colors.YELLOW))
        return EXIT_OK
    output_file = _ask_output(input_file)
    if output_file is None:
        print(_color(_("cancelled"), Colors.YELLOW))
        return EXIT_OK
    if not _confirm_overwrite(output_file):
        print(_color(_("overwrite_cancelled"), Colors.YELLOW))
        return EXIT_OK

    suffix = Path(input_file).suffix.lower()
    api_key = (config.get("api_key", "") or "").strip() or None
    if api_key is None and suffix in IMAGE_EXTENSIONS:
        print(_color(_("api_key_required_for_images"), Colors.RED), file=sys.stderr)
        print(_("run_configure"), file=sys.stderr)
        return EXIT_ERROR
    if api_key is None and suffix in OCR_EXTENSIONS:
        print(_color(_("keyless_note"), Colors.YELLOW), file=sys.stderr)

    model = _model_for_file(config, input_file)
    vision_model = config.get("vision_model") if api_key else None
    return _run_conversion(input_file, output_file, api_key, model, vision_model)


def show_menu(config: RuntimeConfig) -> int:
    """Display the interactive menu and handle choices."""
    while True:
        print(_color(f"\n{_('menu_title')}", Colors.CYAN))
        print(_("menu_convert_pdf"))
        print(_("menu_convert_image"))
        print(_("menu_convert_document"))
        print(_("menu_configure"))
        print(_("menu_exit"))

        choice = _read_input(_("choose_option")).strip()

        if choice == "5":
            print(_color(f"\n{_('goodbye')}", Colors.GREEN))
            return EXIT_OK
        if choice in ("1", "2", "3"):
            kinds = {"1": "PDF", "2": "Image", "3": "Document"}
            convert_menu_option(config, kinds[choice])
            _pause()
            continue
        if choice == "4":
            updated = _choose_and_save_language(config)
            if updated is not None:
                config = configure_menu(updated)
            continue
        print(_color(_("invalid_menu_option"), Colors.YELLOW))
        _pause()


# ── Quick conversion mode ────────────────────────────────────────────────────


def quick_convert(args: argparse.Namespace, config: RuntimeConfig) -> int:
    """Run a quick conversion from command-line arguments."""
    input_file = args.input_file
    if not input_file or not Path(input_file).is_file():
        message = _("file_not_found").format(path=input_file)
        print(_color(_("error_prefix").format(message=message), Colors.RED), file=sys.stderr)
        return EXIT_USAGE

    suffix = Path(input_file).suffix.lower()
    api_key = ((args.api_key or config.get("api_key", "")) or "").strip() or None
    if api_key is None and suffix in IMAGE_EXTENSIONS:
        print(_color(_("api_key_required_for_images"), Colors.RED), file=sys.stderr)
        print(_("run_configure"), file=sys.stderr)
        return EXIT_ERROR

    model = (args.model or _model_for_file(config, input_file)).strip() or "openai"
    output_file = args.output_file or str(Path(input_file).with_suffix(".md"))
    if _same_path(input_file, output_file):
        print(_color(_("output_same_as_input"), Colors.RED), file=sys.stderr)
        return EXIT_USAGE
    try:
        overwrite = _confirm_overwrite(
            output_file,
            assume_yes=bool(args.yes),
            non_interactive=bool(args.non_interactive),
        )
    except NonInteractiveError as exc:
        message = str(exc) or _("non_interactive_stdin")
        print(_color(message, Colors.RED), file=sys.stderr)
        return EXIT_USAGE
    if not overwrite:
        print(_color(_("overwrite_cancelled"), Colors.YELLOW))
        return EXIT_OK

    if api_key is None and suffix in OCR_EXTENSIONS:
        print(_color(_("keyless_note"), Colors.YELLOW), file=sys.stderr)

    vision_model = config.get("vision_model") if api_key else None
    return _run_conversion(input_file, output_file, api_key, model, vision_model)


def _list_models() -> int:
    """Print the recommended models with capability/price tags."""
    catalog = models.fetch_catalog()
    print(_color(f"\n{_('models_title')}", Colors.CYAN))
    if catalog is None:
        print(_("models_offline"))
    sections = (
        (_("model_for_text_short"), RECOMMENDED_TEXT_MODELS),
        (_("model_for_images_short"), RECOMMENDED_VISION_MODELS),
    )
    for label, recommendations in sections:
        print(f"\n{label}:")
        for model in recommendations:
            tags = catalog.tags(model) if catalog is not None else ()
            suffix = f" ({', '.join(tags)})" if tags else ""
            print(f"  - {model}{suffix}")
    return EXIT_OK


# ── Entry point ──────────────────────────────────────────────────────────────


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="markitdown-for-everyone",
        description=_("cli_description"),
    )
    parser.add_argument("input_file", nargs="?", help=_("input_file_help"))
    parser.add_argument("-o", "--output", dest="output_file", help=_("output_help"))
    parser.add_argument("-k", "--api-key", dest="api_key", help=_("api_key_help"))
    parser.add_argument("-m", "--model", dest="model", help=_("model_help"))
    parser.add_argument("--configure", action="store_true", help=_("configure_help"))
    parser.add_argument("--list-models", action="store_true", help=_("list_models_help"))
    parser.add_argument("-y", "--yes", action="store_true", help=_("yes_help"))
    parser.add_argument("--non-interactive", action="store_true", help=_("non_interactive_help"))
    parser.add_argument("-q", "--quiet", action="store_true", help=_("quiet_help"))
    parser.add_argument(
        "-l",
        "--language",
        choices=list(LANGUAGES),
        default=None,
        help=_("language_flag_help"),
    )
    parser.add_argument("-v", "--verbose", action="store_true", help=_("verbose_help"))
    parser.add_argument("-d", "--debug", action="store_true", help=_("debug_help"))
    parser.add_argument(
        "--version",
        action="version",
        version=f"Markitdown-for-everyone {__version__}",
    )
    return parser.parse_args(argv)


def _configure_logging(args: argparse.Namespace) -> None:
    """Configure logging from the verbosity flags."""
    if args.debug:
        level = logging.DEBUG
    elif args.verbose:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(
        level=level,
        stream=sys.stderr,
        format="%(levelname)s: %(message)s",
        force=True,
    )


def _non_interactive_error() -> int:
    print(
        _color(_("non_interactive_input_required"), Colors.RED),
        file=sys.stderr,
    )
    return EXIT_USAGE


def _cancel_exit() -> int:
    print(
        _color(f"\n{_('api_key_required_exit')}", Colors.YELLOW),
        file=sys.stderr,
    )
    return EXIT_OK


def _run_configure(config: RuntimeConfig) -> int:
    """Run the --configure flow and return an exit code."""
    updated = _choose_and_save_language(config)
    if updated is None:
        return _cancel_exit()
    config = setup_wizard(updated) if _needs_setup(updated) else configure_menu(updated)
    if _needs_setup(config):
        return _cancel_exit()
    return EXIT_OK


def _dispatch(args: argparse.Namespace, config: RuntimeConfig) -> int:
    """Run the mode selected by the parsed arguments."""
    if args.list_models:
        return _list_models()
    if args.configure:
        if args.non_interactive:
            return _non_interactive_error()
        return _run_configure(config)
    if args.input_file:
        return quick_convert(args, config)
    if args.non_interactive:
        return _non_interactive_error()
    if _needs_setup(config):
        updated = _choose_and_save_language(config)
        if updated is None:
            return _cancel_exit()
        config = setup_wizard(updated)
        if _needs_setup(config):
            return _cancel_exit()
    return show_menu(config)


def main(argv: list[str] | None = None) -> int:
    """Entry point for the CLI."""
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    try:
        _enable_ansi_windows()
        config = load_config()
        # Set the language before argparse so --help is localized too.
        set_language(_resolve_language(_prescan_language(raw_argv), config))
        args = parse_args(raw_argv)
        if args.language:
            set_language(args.language)
        _configure_logging(args)
        if not args.quiet:
            _clear_screen()
            print_banner()
        return _dispatch(args, config)
    except NonInteractiveError as exc:
        message = str(exc) or _("non_interactive_stdin")
        print(_color(message, Colors.RED), file=sys.stderr)
        return EXIT_USAGE
    except KeyboardInterrupt:
        print(_color(f"\n{_('conversion_cancelled')}", Colors.YELLOW))
        return EXIT_INTERRUPTED
    except BrokenPipeError:
        return EXIT_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
