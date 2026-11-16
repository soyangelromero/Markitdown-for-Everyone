"""Shared constants for MarkItDown for Everyone."""

from __future__ import annotations

import os
import sys

from markitdown_pollinations import __version__

# Pollinations API endpoints (OpenAI-compatible).
POLLINATIONS_BASE_URL = "https://gen.pollinations.ai/v1"
POLLINATIONS_MODELS_URL = "https://gen.pollinations.ai/models"
POLLINATIONS_BALANCE_URL = "https://gen.pollinations.ai/account/balance"
POLLINATIONS_CHAT_URL = "https://gen.pollinations.ai/v1/chat/completions"

# Models with vision capability (accept image input).
VISION_MODELS: frozenset[str] = frozenset(
    {
        "openai",
        "openai-large",
        "openai-fast",
        "qwen-vision",
        "qwen-vision-pro",
        "gemini",
        "gemini-large",
        "claude",
        "claude-large",
    }
)

# Supported image extensions.
IMAGE_EXTENSIONS: frozenset[str] = frozenset(
    {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}
)

# Formats where the optional LLM (vision/OCR) is useful but not required to read text.
OCR_EXTENSIONS: frozenset[str] = frozenset({".pdf", ".docx", ".pptx", ".xlsx", ".xls"})

# Recommended models for text-only conversions.
RECOMMENDED_TEXT_MODELS: tuple[str, ...] = (
    "openai",
    "openai-fast",
    "deepseek",
    "mistral",
    "glm",
)

# Recommended models for image/vision conversions.
RECOMMENDED_VISION_MODELS: tuple[str, ...] = (
    "openai",
    "openai-large",
    "gemini",
    "gemini-large",
    "claude",
    "claude-large",
    "qwen-vision",
    "qwen-vision-pro",
)

# Validation endpoints and parameters for API-key checks.
VALIDATION_PROMPT = "hello"
VALIDATION_MODEL = "openai"
VALIDATION_MAX_TOKENS = 2
VALIDATION_TIMEOUT_SECONDS = 10.0
CONVERSION_TIMEOUT_SECONDS = 120.0
MODELS_TIMEOUT_SECONDS = 6.0
VALIDATION_USER_AGENT = f"Markitdown-for-everyone/{__version__}"

# Retry policy. The OpenAI client is configured with max_retries=0 so that the
# application owns the retry loop (no nested retries).
MAX_RETRIES = 3
RETRY_DELAYS: tuple[float, ...] = (1.0, 2.0)
MAX_RETRY_AFTER_SECONDS = 30.0

# Process exit codes (documented in README.md).
EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2
EXIT_NO_OUTPUT = 3
EXIT_INTERRUPTED = 130


class Colors:
    """ANSI color codes."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    MAGENTA = "\033[35m"


_color_cache: bool | None = None


def _reset_color_cache() -> None:
    """Reset the color cache — for tests and for runtime environment changes."""
    global _color_cache
    _color_cache = None


def _color_enabled() -> bool:
    """Return True when ANSI colors should be emitted.

    Honors ``NO_COLOR`` (disable) and ``FORCE_COLOR`` (enable); otherwise colors
    are only used when stdout is a TTY, so redirected output stays clean.
    """
    global _color_cache
    if _color_cache is None:
        if os.environ.get("NO_COLOR"):
            _color_cache = False
        elif os.environ.get("FORCE_COLOR"):
            _color_cache = True
        else:
            try:
                _color_cache = bool(sys.stdout.isatty())
            except (AttributeError, ValueError):
                _color_cache = False
    return _color_cache


def _color(text: str, color: str) -> str:
    """Wrap text in ANSI color codes when colors are enabled."""
    if not _color_enabled():
        return text
    return f"{color}{text}{Colors.RESET}"
