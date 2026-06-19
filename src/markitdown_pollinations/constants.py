"""Constants for MarkItDown Pollinations."""

import os

from markitdown_pollinations import __version__

# Pollinations API base URL
POLLINATIONS_BASE_URL = "https://gen.pollinations.ai/v1"

# Models with vision capability (can process images)
VISION_MODELS = {
    "openai",
    "openai-large",
    "qwen-vision",
    "qwen-vision-pro",
    "gemini",
    "gemini-large",
    "claude",
    "claude-large",
}

# Supported image extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}

# Recommended models for text-only conversions
RECOMMENDED_TEXT_MODELS = ["openai", "glm", "openai-fast", "mistral", "deepseek"]

# Recommended models for image/vision conversions
RECOMMENDED_VISION_MODELS = [
    "openai",
    "openai-large",
    "qwen-vision",
    "qwen-vision-pro",
    "gemini",
    "gemini-large",
    "claude",
    "claude-large",
]

# Validation endpoints and parameters for API-key checks
POLLINATIONS_BALANCE_URL = "https://gen.pollinations.ai/account/balance"
POLLINATIONS_CHAT_URL = "https://gen.pollinations.ai/v1/chat/completions"
VALIDATION_PROMPT = "hello"
VALIDATION_MODEL = "openai"
VALIDATION_MAX_TOKENS = 2
VALIDATION_TIMEOUT_SECONDS = 10.0
CONVERSION_TIMEOUT_SECONDS = 120.0
VALIDATION_USER_AGENT = f"Markitdown-for-everyone/{__version__}"


class Colors:
    """ANSI color codes."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    MAGENTA = "\033[35m"


_NO_COLOR: bool | None = None


def _reset_no_color_cache() -> None:
    """Reset the NO_COLOR cache — for use by tests after monkeypatch.setenv."""
    global _NO_COLOR  # noqa: PLW0603 — intentional module-level state
    _NO_COLOR = None


def _color(text: str, color: str) -> str:
    """Wrap text in ANSI color codes if NO_COLOR is not set."""
    global _NO_COLOR  # noqa: PLW0603 — intentional module-level state
    if _NO_COLOR is None:
        _NO_COLOR = bool(os.environ.get("NO_COLOR"))
    if _NO_COLOR:
        return text
    return f"{color}{text}{Colors.RESET}"
