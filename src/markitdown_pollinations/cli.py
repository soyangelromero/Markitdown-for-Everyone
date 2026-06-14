"""Command-line interface for Markitdown-for-everyone."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from markitdown_pollinations import __version__
from markitdown_pollinations.config import Config, load_config, save_config
from markitdown_pollinations.constants import (
    IMAGE_EXTENSIONS,
    RECOMMENDED_TEXT_MODELS,
    RECOMMENDED_VISION_MODELS,
    VISION_MODELS,
)
from markitdown_pollinations.converter import ConversionResult, convert_file
from markitdown_pollinations.pollinations_client import validate_model


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


class Colors:
    """ANSI color codes."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    MAGENTA = "\033[35m"


def _color(text: str, color: str) -> str:
    """Wrap text in ANSI color codes if NO_COLOR is not set."""
    if os.environ.get("NO_COLOR"):
        return text
    return f"{color}{text}{Colors.RESET}"


def print_banner() -> None:
    """Print the program banner."""
    banner = f"""
{_color("  __  __            _  _    _         _                  _    ", Colors.CYAN)}
{_color(" |  \\/  | __ _ _ __| || |__| |_  ___ | |_ __ _ _ _  __ _| |___", Colors.CYAN)}
{_color(" | |\\/| |/ _` | '_ \\ __ / _` |/ _ \\|  _/ _` | ' \\/ _` | (_-<", Colors.CYAN)}
{_color(" |_|  |_|\\__,_| .__/|_||\\__,_|\\___/ \\__\\__,_|_||_\\__,_|_/__/", Colors.CYAN)}
{_color("              |_|                                             ", Colors.CYAN)}
  {_color("Markitdown-for-everyone", Colors.BOLD)} {__version__}
  by {_color("Angel Romero", Colors.BOLD)} — https://github.com/soyangelromero
"""
    print(banner)


def _prompt(text: str, default: str = "") -> str:
    """Prompt the user for input and return a stripped value."""
    prompt = f"{text} [{default}]: " if default else f"{text}: "
    value = input(prompt).strip()
    return value if value else default


def _prompt_choice(options: list[str], prompt_text: str) -> str:
    """Prompt the user to pick one of the listed options."""
    print(_color(prompt_text, Colors.CYAN))
    for idx, option in enumerate(options, start=1):
        print(f"  {idx}. {option}")
    while True:
        choice = input("Choose an option: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print(_color("Invalid option. Please try again.", Colors.YELLOW))


def _model_for_file(config: Config, input_file: str) -> str:
    """Choose the right model based on the file type."""
    ext = Path(input_file).suffix.lower()
    if ext in IMAGE_EXTENSIONS:
        return config.get("vision_model", "openai")
    return config.get("text_model", "openai")


def _is_first_run(config: Config) -> bool:
    """Return True if the user has not configured the app yet."""
    return not config.get("api_key", "").strip()


def _ask_model(prompt: str, recommendations: list[str], default: str) -> str:
    """Ask the user to pick or type a model."""
    print(_color(f"\n{prompt}", Colors.CYAN))
    print("Recommended:")
    for idx, model in enumerate(recommendations, start=1):
        marker = "*" if model == default else " "
        print(f"  {idx}. {marker} {model}")
    print("  0. Other (type manually)")

    while True:
        choice = input("Select: ").strip()
        if choice == "0":
            return _prompt("Enter the model name", default=default).strip() or default
        if choice.isdigit() and 1 <= int(choice) <= len(recommendations):
            return recommendations[int(choice) - 1]
        print(_color("Invalid option. Please try again.", Colors.YELLOW))


def setup_wizard(config: Config) -> Config:
    """Run the first-time configuration wizard."""
    print(_color("\nWelcome to Markitdown-for-everyone!", Colors.GREEN))
    print("Let's set up the program so you can start converting files.\n")

    api_key = _prompt(
        "Enter your Pollinations API key",
        default=config.get("api_key", ""),
    ).strip()

    text_model = _ask_model(
        "Model for text documents (PDF, Word, Excel, etc.)",
        RECOMMENDED_TEXT_MODELS,
        config.get("text_model", "openai"),
    )

    vision_model = _ask_model(
        "Model for images (JPG, PNG, etc.)",
        RECOMMENDED_VISION_MODELS,
        config.get("vision_model", "openai"),
    )

    new_config: Config = {
        "api_key": api_key,
        "text_model": text_model,
        "vision_model": vision_model,
    }

    ok, msg = validate_model(api_key, text_model)
    if not ok:
        print(_color(f"\nCould not validate the text model: {msg}", Colors.YELLOW))
        print("The configuration will be saved anyway.")

    if save_config(new_config):
        print(_color("\nConfiguration saved successfully.", Colors.GREEN))
    else:
        print(_color("\nError: could not save the configuration.", Colors.RED))

    return new_config


def configure_menu(config: Config) -> Config:
    """Show the configuration menu and update settings."""
    print(_color("\n--- Configuration ---", Colors.CYAN))

    api_key = _prompt(
        "Pollinations API key",
        default=config.get("api_key", ""),
    ).strip()

    text_model = _ask_model(
        "Model for text documents",
        RECOMMENDED_TEXT_MODELS,
        config.get("text_model", "openai"),
    )

    vision_model = _ask_model(
        "Model for images",
        RECOMMENDED_VISION_MODELS,
        config.get("vision_model", "openai"),
    )

    new_config: Config = {
        "api_key": api_key,
        "text_model": text_model,
        "vision_model": vision_model,
    }

    ok, msg = validate_model(api_key, text_model)
    if not ok:
        print(_color(f"\nCould not validate the text model: {msg}", Colors.YELLOW))

    if save_config(new_config):
        print(_color("\nConfiguration updated.", Colors.GREEN))
    else:
        print(_color("\nError: could not save the configuration.", Colors.RED))

    return new_config


def _ask_file(prompt: str) -> str:
    """Prompt for a file path and validate that it exists."""
    while True:
        path = input(f"{prompt}: ").strip().strip('"')
        if Path(path).is_file():
            return path
        print(_color(f"File not found: {path}", Colors.RED))


def _ask_output(input_file: str) -> str:
    """Prompt for an output path with a sensible default."""
    default = str(Path(input_file).with_suffix(".md"))
    path = _prompt("Output file", default=default).strip().strip('"')
    return path or default


def _run_conversion(input_file: str, output_file: str, api_key: str, model: str) -> int:
    """Run a single conversion and print the result."""
    ext = Path(input_file).suffix.lower()
    if ext in IMAGE_EXTENSIONS and model not in VISION_MODELS:
        print(
            _color(
                f"Warning: '{model}' is not a vision model. "
                "Images may not convert correctly.",
                Colors.YELLOW,
            )
        )

    print(
        f"\nConverting {_color(input_file, Colors.CYAN)} "
        f"→ {_color(output_file, Colors.CYAN)} "
        f"using model {_color(model, Colors.CYAN)}..."
    )

    result: ConversionResult = convert_file(input_file, output_file, api_key, model)

    if result.cancelled:
        print(_color("Conversion cancelled.", Colors.YELLOW))
        return 130

    if not result.success:
        print(_color(f"Error: {result.message}", Colors.RED))
        return 1

    print(_color(f"Done: {result.output_path}", Colors.GREEN))
    if result.warning:
        print(_color(f"Warning: {result.warning}", Colors.YELLOW))
    return 0


def convert_menu_option(config: Config, file_kind: str) -> int:
    """Handle a conversion option from the main menu."""
    print(_color(f"\n--- Convert {file_kind} to Markdown ---", Colors.CYAN))
    input_file = _ask_file("File path")
    output_file = _ask_output(input_file)
    model = _model_for_file(config, input_file)
    return _run_conversion(input_file, output_file, config["api_key"], model)


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

        if choice == "1":
            convert_menu_option(config, "PDF")
        elif choice == "2":
            convert_menu_option(config, "Image")
        elif choice == "3":
            convert_menu_option(config, "Document")
        elif choice == "4":
            config = configure_menu(config)
        elif choice == "5":
            print(_color("\nGoodbye!", Colors.GREEN))
            return 0
        else:
            print(_color("Invalid option. Please try again.", Colors.YELLOW))


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
    return parser.parse_args(argv)


def quick_convert(args: argparse.Namespace, config: Config) -> int:
    """Run a quick conversion from command-line arguments."""
    api_key = (args.api_key or config.get("api_key", "")).strip()
    if not api_key:
        print(_color("Error: API key not configured.", Colors.RED))
        print("Run: python markitdown_for_everyone.py --configure")
        return 1

    input_file = args.input_file
    if not input_file or not Path(input_file).is_file():
        print(_color(f"Error: file not found: {input_file}", Colors.RED))
        return 1

    model = (args.model or _model_for_file(config, input_file)).strip()
    output_file = args.output_file or str(Path(input_file).with_suffix(".md"))
    return _run_conversion(input_file, output_file, api_key, model)


def main(argv: list[str] | None = None) -> int:
    """Entry point for the CLI."""
    _enable_ansi_windows()
    args = parse_args(argv)
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

    return show_menu(config)


if __name__ == "__main__":
    raise SystemExit(main())
