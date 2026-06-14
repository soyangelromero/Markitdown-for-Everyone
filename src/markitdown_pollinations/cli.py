"""Command-line interface for Markitdown-for-everyone."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from markitdown_pollinations import __version__
from markitdown_pollinations.config import load_config, save_config
from markitdown_pollinations.constants import IMAGE_EXTENSIONS, VISION_MODELS
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


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="markitdown-for-everyone",
        description="Convert files to Markdown using the Pollinations API.",
    )
    parser.add_argument(
        "-i",
        "--input",
        dest="input_file",
        help="File to convert",
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
        help="Model to use (default: openai)",
    )
    parser.add_argument(
        "--configure",
        action="store_true",
        help="Save API key and model to config.json",
    )
    return parser.parse_args(argv)


def _default_output(input_path: str) -> str:
    """Generate default output path from input path."""
    return str(Path(input_path).with_suffix(".md"))


def _resolve_inputs(
    args: argparse.Namespace,
    config: dict,
) -> tuple[str, str, str]:
    """Resolve and validate API key, model, and input file."""
    api_key = (args.api_key or config.get("api_key", "")).strip()
    model = (args.model or config.get("model", "openai")).strip()

    if args.configure:
        if not api_key:
            print(_color("Error: API key is required to configure.", Colors.RED))
            print("Usage: markitdown-for-everyone --configure -k YOUR_API_KEY [-m MODEL]")
            sys.exit(1)
        return api_key, model, ""

    if not api_key:
        print(_color("Error: API key is required.", Colors.RED))
        print("Run with --configure to save your key, or pass -k/--api-key.")
        sys.exit(1)

    if not args.input_file:
        print(_color("Error: Input file is required.", Colors.RED))
        print("Usage: markitdown-for-everyone -i INPUT_FILE [-o OUTPUT_FILE] [-m MODEL]")
        sys.exit(1)

    input_file = args.input_file
    if not Path(input_file).is_file():
        print(_color(f"Error: File not found: {input_file}", Colors.RED))
        sys.exit(1)

    ext = Path(input_file).suffix.lower()
    if ext in IMAGE_EXTENSIONS and model not in VISION_MODELS:
        print(
            _color(
                f"Warning: '{model}' is not a vision model. Image descriptions may fail. "
                "Try one of: openai, gemini, claude, qwen-vision.",
                Colors.YELLOW,
            )
        )

    return api_key, model, input_file


def main(argv: list[str] | None = None) -> int:
    """Entry point for the CLI."""
    _enable_ansi_windows()
    args = parse_args(argv)
    print_banner()

    config = load_config()
    api_key, model, input_file = _resolve_inputs(args, config)

    if args.configure:
        ok, msg = validate_model(api_key, model)
        if not ok:
            print(_color(f"Configuration failed: {msg}", Colors.RED))
            return 1
        if save_config({"api_key": api_key, "model": model}):
            print(_color("Configuration saved successfully.", Colors.GREEN))
            return 0
        return 1

    output_file = args.output_file or _default_output(input_file)
    print(
        f"Converting {_color(input_file, Colors.CYAN)} "
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


if __name__ == "__main__":
    raise SystemExit(main())
