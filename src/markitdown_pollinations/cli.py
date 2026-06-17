"""Command-line interface for Markitdown-for-everyone."""

from __future__ import annotations

import argparse
import getpass
import itertools
import os
import sys
import threading
import time
from pathlib import Path

from markitdown_pollinations import __version__
from markitdown_pollinations.config import Config, load_config, save_config
from markitdown_pollinations.constants import (
    IMAGE_EXTENSIONS,
    RECOMMENDED_TEXT_MODELS,
    RECOMMENDED_VISION_MODELS,
    VISION_MODELS,
    Colors,
    _color,
)
from markitdown_pollinations.converter import ConversionResult, convert_file
from markitdown_pollinations.validation import (
    _mask_key,
    _validate_key_via_api,
    _warn_if_key_invalid,
)


def _enable_ansi_windows() -> None:
    """Enable ANSI escape sequences on Windows terminals."""
    if os.name != "nt":
        return
    try:
        import ctypes

        kernel = ctypes.windll.kernel32
        handle = kernel.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint32()
        kernel.GetConsoleMode(handle, ctypes.byref(mode))
        mode.value |= 0x0004  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
        kernel.SetConsoleMode(handle, mode)
    except Exception:
        pass


def _clear_screen() -> None:
    """Clear the terminal screen using ANSI escape sequences.

    Does nothing if the NO_CLEAR environment variable is set, so users who
    prefer inline output (e.g. in CI or logs) can disable clearing.
    """
    if os.environ.get("NO_CLEAR"):
        return
    # Clear screen and move cursor to top-left. This avoids spawning a shell
    # via os.system("cls"/"clear") and works on any ANSI-capable terminal.
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
    print(f"  by {_color('Angel Romero', Colors.BOLD)} - https://github.com/soyangelromero")
    print(f"  v{__version__}\n")


_CANCEL_INPUT = ("c", "cancel", "b", "back")


def _is_cancel_input(value: str) -> bool:
    """Return True if the user typed a cancel/back command."""
    return value.strip().lower() in _CANCEL_INPUT


def _prompt_for_api_key(current_key: str) -> str | None:
    """Prompt for an API key (warns on format, validates via network).

    The key is read without echoing characters. If the user presses Enter
    without typing anything, the existing key is kept. Type 'c', 'cancel',
    'b', or 'back' to abort this screen. Returns the key if one was entered,
    None if the user cancelled, or None if the user entered an empty
    value when no existing key is available (after printing a warning).
    """
    if current_key:
        prompt = f"Pollinations API key [{_mask_key(current_key)}]: "
    else:
        prompt = "Pollinations API key: "

    try:
        api_key = getpass.getpass(prompt).strip()
    except EOFError:
        return None

    if _is_cancel_input(api_key):
        return None

    # Keep the current key if the user just pressed Enter.
    if not api_key and current_key:
        return current_key

    if not api_key:
        print(_color("An API key is required.", Colors.RED), file=sys.stderr)
        return None
    _warn_if_key_invalid(api_key)
    return api_key


def _prompt(text: str, default: str = "") -> str:
    """Prompt the user for input and return a stripped value."""
    prompt = f"{text} [{default}]: " if default else f"{text}: "
    value = input(prompt).strip()
    return value if value else default


def _model_for_file(config: Config, input_file: str) -> str:
    """Choose the right model based on the file type."""
    ext = Path(input_file).suffix.lower()
    if ext in IMAGE_EXTENSIONS:
        return config.get("vision_model", "openai")
    return config.get("text_model", "openai")


def _is_first_run(config: Config) -> bool:
    """Return True if the user has not configured the app yet."""
    return not config.get("api_key", "").strip()


def _ask_model(prompt: str, recommendations: list[str], default: str) -> str | None:
    """Ask the user to pick or type a model.

    Type 'c', 'cancel', 'b', or 'back' to abort this screen.
    """
    print(_color(f"\n{prompt}", Colors.CYAN))
    print("Recommended:")
    for idx, model in enumerate(recommendations, start=1):
        marker = "*" if model == default else " "
        print(f"  {idx}. {marker} {model}")
    print("  0. Other (type manually)")
    print("  c/b. Cancel/Back")

    while True:
        choice = input("Select: ").strip()
        if _is_cancel_input(choice):
            return None
        if choice == "0":
            model = _prompt("Enter the model name", default=default).strip()
            if _is_cancel_input(model):
                return None
            return model or default
        if choice.isdigit() and 1 <= int(choice) <= len(recommendations):
            return recommendations[int(choice) - 1]
        print(_color("Invalid option. Please try again.", Colors.YELLOW))


def _configure_flow(
    config: Config,
    header: str,
    welcome: str,
    text_prompt: str,
    vision_prompt: str,
    success_message: str,
) -> Config:
    """Shared configuration flow used by the wizard and settings menu.

    Validates the API key, asks for text and vision models, and saves the
    configuration. Returns the original config unchanged if the user cancels.

    This intentionally does not clear the screen: the banner stays visible at
    the top and sub-screens print their content below it.
    """
    original_config = config.copy()

    while True:
        print(_color(f"\n{header}", Colors.CYAN))
        if welcome:
            print(_color(welcome, Colors.GREEN))

        api_key = _prompt_for_api_key(config.get("api_key", ""))
        if api_key is None:
            print(_color("\nConfiguration cancelled.", Colors.YELLOW))
            return original_config

        print(_color("Validating API key...", Colors.CYAN))
        result = _validate_key_via_api(api_key)
        if result == "valid":
            break
        if result == "invalid":
            print(
                _color(
                    "Please provide a valid API key to continue.",
                    Colors.YELLOW,
                )
            )
        _pause("Press Enter to try again...")

    text_model = _ask_model(
        text_prompt,
        RECOMMENDED_TEXT_MODELS,
        config.get("text_model", "openai"),
    )
    if text_model is None:
        print(_color("\nConfiguration cancelled.", Colors.YELLOW))
        return original_config

    vision_model = _ask_model(
        vision_prompt,
        RECOMMENDED_VISION_MODELS,
        config.get("vision_model", "openai"),
    )
    if vision_model is None:
        print(_color("\nConfiguration cancelled.", Colors.YELLOW))
        return original_config

    new_config: Config = config.copy()
    new_config["api_key"] = api_key
    new_config["text_model"] = text_model
    new_config["vision_model"] = vision_model

    if save_config(new_config):
        print(_color(f"\n{success_message}", Colors.GREEN))
    else:
        print(_color("\nError: could not save the configuration.", Colors.RED), file=sys.stderr)

    return new_config


def setup_wizard(config: Config) -> Config:
    """Run the first-time configuration wizard."""
    return _configure_flow(
        config,
        header="Welcome to Markitdown-for-everyone!",
        welcome="Let's set up the program so you can start converting files.",
        text_prompt="Model for text documents (PDF, Word, Excel, etc.)",
        vision_prompt="Model for images (JPG, PNG, etc.)",
        success_message="Configuration saved successfully.",
    )


def configure_menu(config: Config) -> Config:
    """Show the configuration menu and update settings."""
    return _configure_flow(
        config,
        header="--- Configuration ---",
        welcome="",
        text_prompt="Model for text documents",
        vision_prompt="Model for images",
        success_message="Configuration updated.",
    )


def _ask_file(prompt: str) -> str | None:
    """Prompt for a file path and validate that it exists.

    Type 'c', 'cancel', 'b', or 'back' to abort this screen.
    """
    while True:
        path = input(f"{prompt} (or 'c'/'b' to cancel/back): ").strip().strip('"')
        if _is_cancel_input(path):
            return None
        if Path(path).is_file():
            return path
        print(_color(f"File not found: {path}", Colors.RED), file=sys.stderr)


def _ask_output(input_file: str) -> str | None:
    """Prompt for an output path with a sensible default.

    Type 'c', 'cancel', 'b', or 'back' to abort this screen.
    """
    default = str(Path(input_file).with_suffix(".md"))
    path = _prompt("Output file", default=default).strip().strip('"')
    if _is_cancel_input(path):
        return None
    return path or default


def _confirm_overwrite(path: str) -> bool:
    """Ask the user before overwriting an existing file."""
    if not Path(path).exists():
        return True
    answer = (
        input(
            _color(
                f"'{path}' already exists. Overwrite? (y/N): ",
                Colors.YELLOW,
            )
        )
        .strip()
        .lower()
    )
    return answer in ("y", "yes")


def _run_conversion(
    input_file: str,
    output_file: str,
    api_key: str,
    model: str,
    vision_model: str | None = None,
) -> int:
    """Run a single conversion and print the result.

    If the conversion produces empty content for a non-image file (e.g. a
    scanned PDF with no selectable text) and a *vision_model* is provided,
    the function automatically retries with that vision model.
    """
    ext = Path(input_file).suffix.lower()
    if ext in IMAGE_EXTENSIONS and model not in VISION_MODELS:
        print(
            _color(
                f"Warning: '{model}' is not a vision model. Images may not convert correctly.",
                Colors.YELLOW,
            ),
            file=sys.stderr,
        )

    print(
        f"\nConverting {_color(input_file, Colors.CYAN)} "
        f"-> {_color(output_file, Colors.CYAN)} "
        f"using model {_color(model, Colors.CYAN)}..."
    )

    # Spinner for conversion
    spinner_frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    stop_spinner = threading.Event()
    no_color = bool(os.environ.get("NO_COLOR"))

    def spin():
        for frame in itertools.cycle(spinner_frames):
            if stop_spinner.is_set():
                break
            if no_color:
                sys.stdout.write("\rConverting... ")
            else:
                sys.stdout.write(f"\r{frame} Converting... ")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * 30 + "\r")
        sys.stdout.flush()

    def _run(which_model: str) -> ConversionResult:
        stop_spinner.clear()
        spinner_thread = threading.Thread(target=spin)
        spinner_thread.start()
        try:
            return convert_file(input_file, output_file, api_key, which_model)
        finally:
            stop_spinner.set()
            spinner_thread.join()

    result = _run(model)

    # Empty content on a non-image file?  Retry with the vision model.
    if (
        result.success
        and result.warning
        and vision_model is not None
        and vision_model != model
        and ext not in IMAGE_EXTENSIONS
    ):
        print(
            _color(
                "\nNo text found — retrying with vision model "
                f"'{vision_model}'...",
                Colors.YELLOW,
            ),
        )
        vision_result = _run(vision_model)
        if vision_result.success and not vision_result.warning:
            result = vision_result

    if result.cancelled:
        print(_color("Conversion cancelled.", Colors.YELLOW))
        return 130

    if not result.success:
        print(_color(f"Error: {result.message}", Colors.RED), file=sys.stderr)
        return 1

    print(_color(f"Done: {result.output_path}", Colors.GREEN))
    if result.warning:
        print(_color(f"Warning: {result.warning}", Colors.YELLOW))
    return 0


def convert_menu_option(config: Config, file_kind: str) -> int:
    """Handle a conversion option from the main menu."""
    print(_color(f"\n--- Convert {file_kind} to Markdown ---", Colors.CYAN))
    input_file = _ask_file("File path")
    if input_file is None:
        print(_color("Cancelled.", Colors.YELLOW))
        return 0
    output_file = _ask_output(input_file)
    if output_file is None:
        print(_color("Cancelled.", Colors.YELLOW))
        return 0
    if not _confirm_overwrite(output_file):
        print(_color("Cancelled.", Colors.YELLOW))
        return 0
    model = _model_for_file(config, input_file)
    api_key = config.get("api_key", "")
    if not api_key:
        print(_color("Error: API key not configured.", Colors.RED), file=sys.stderr)
        print("Run: python markitdown_for_everyone.py --configure", file=sys.stderr)
        return 1
    return _run_conversion(
        input_file, output_file, api_key, model,
        vision_model=config.get("vision_model"),
    )


def _pause(message: str = "Press Enter to continue...") -> None:
    """Wait for the user to press Enter."""
    try:
        input(_color(message, Colors.CYAN))
    except EOFError:
        pass


def show_menu(config: Config) -> int:
    """Display the interactive menu and handle choices."""
    while True:
        print(_color("\n--- Menu ---", Colors.CYAN))
        print("1. Convert PDF to Markdown")
        print("2. Convert Image to Markdown")
        print("3. Convert Document to Markdown")
        print("4. Configure API key and models")
        print("5. Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "5":
            print(_color("\nGoodbye!", Colors.GREEN))
            return 0
        if choice == "1":
            convert_menu_option(config, "PDF")
        elif choice == "2":
            convert_menu_option(config, "Image")
        elif choice == "3":
            convert_menu_option(config, "Document")
        elif choice == "4":
            config = configure_menu(config)
        else:
            print(_color("Invalid option. Please try again.", Colors.YELLOW))
            _pause()
            continue

        _pause()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for quick conversion mode."""
    parser = argparse.ArgumentParser(
        prog="markitdown-for-everyone",
        description="Convert files to Markdown using the Pollinations API.",
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        help="File to convert (if omitted, the interactive menu opens)",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_file",
        help="Output Markdown file (default: input.md)",
    )
    parser.add_argument(
        "-k",
        "--api-key",
        dest="api_key",
        help="Pollinations API key",
    )
    parser.add_argument(
        "-m",
        "--model",
        dest="model",
        help="Model to use (default: from config or openai)",
    )
    parser.add_argument(
        "--configure",
        action="store_true",
        help="Open the configuration menu",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"Markitdown-for-everyone {__version__}",
    )
    return parser.parse_args(argv)


def quick_convert(args: argparse.Namespace, config: Config) -> int:
    """Run a quick conversion from command-line arguments."""
    api_key = (args.api_key or config.get("api_key", "")).strip()
    if not api_key:
        print(_color("Error: API key not configured.", Colors.RED), file=sys.stderr)
        print("Run: python markitdown_for_everyone.py --configure", file=sys.stderr)
        return 1

    input_file = args.input_file
    if not input_file or not Path(input_file).is_file():
        print(_color(f"Error: file not found: {input_file}", Colors.RED), file=sys.stderr)
        return 1

    model = (args.model or _model_for_file(config, input_file)).strip()
    output_file = args.output_file or str(Path(input_file).with_suffix(".md"))
    if not _confirm_overwrite(output_file):
        print(_color("Conversion cancelled.", Colors.YELLOW))
        return 0
    return _run_conversion(
        input_file, output_file, api_key, model,
        vision_model=config.get("vision_model"),
    )


def main(argv: list[str] | None = None) -> int:
    """Entry point for the CLI."""
    try:
        _enable_ansi_windows()
        args = parse_args(argv)
        # Clear once at startup so the banner appears at the top of the
        # terminal. Sub-screens never clear again; they append below the banner
        # to avoid the repeated full-screen redraw effect.
        _clear_screen()
        print_banner()

        config = load_config()

        if args.configure:
            if _is_first_run(config):
                config = setup_wizard(config)
            else:
                config = configure_menu(config)
            return 0

        if args.input_file:
            return quick_convert(args, config)

        if _is_first_run(config):
            config = setup_wizard(config)
            if _is_first_run(config):
                print(
                    _color(
                        "\nAn API key is required to use the program.",
                        Colors.YELLOW,
                    ),
                    file=sys.stderr,
                )
                return 0

        return show_menu(config)
    except KeyboardInterrupt:
        print(_color("\nOperation cancelled by user.", Colors.YELLOW))
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
