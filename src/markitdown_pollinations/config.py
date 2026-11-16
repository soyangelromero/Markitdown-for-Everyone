"""Configuration loading/saving for MarkItDown for Everyone.

The configuration lives in the platform-specific user config directory, never in
the repository. Saving is atomic and, on Unix, restricted to the owner (0600).

The API key can also come from the ``POLLINATIONS_API_KEY`` environment
variable. Keys that come from the environment are **never** written to disk.
"""

from __future__ import annotations

import contextlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import TypedDict, cast

from platformdirs import user_config_dir

from markitdown_pollinations.i18n import LANGUAGES, _

ENV_API_KEY = "POLLINATIONS_API_KEY"


class Config(TypedDict):
    """Configuration persisted to disk."""

    api_key: str
    text_model: str
    vision_model: str
    language: str


class RuntimeConfig(TypedDict, total=False):
    """Configuration as used at runtime.

    ``api_key_from_env`` is a runtime-only marker: it is never persisted.
    """

    api_key: str
    text_model: str
    vision_model: str
    language: str
    api_key_from_env: bool


CONFIG_FILE = Path(user_config_dir("markitdown-for-everyone", "AngelRomero")) / "config.json"

DEFAULT_CONFIG: Config = {
    "api_key": "",
    "text_model": "openai",
    "vision_model": "openai",
    "language": "",
}


def _default_values() -> dict[str, str]:
    """Return the default configuration as a plain mutable dict."""
    return {
        "api_key": DEFAULT_CONFIG["api_key"],
        "text_model": DEFAULT_CONFIG["text_model"],
        "vision_model": DEFAULT_CONFIG["vision_model"],
        "language": DEFAULT_CONFIG["language"],
    }


def _env_api_key() -> str:
    """Return the API key from the environment (empty when unset)."""
    return os.environ.get(ENV_API_KEY, "").strip()


def _warn_invalid_value(key: str) -> None:
    print(_("config_warn_invalid_values").format(key=key), file=sys.stderr)


def _sanitize_config(raw: object) -> dict[str, str]:
    """Validate a raw JSON object and return a complete config mapping.

    Invalid values are replaced with defaults and reported on stderr. Unknown
    keys are ignored, which keeps the file forward/backward compatible.
    """
    values: dict[str, str] = _default_values()
    if not isinstance(raw, dict):
        print(_("config_warn_not_dict"), file=sys.stderr)
        return values

    for key in ("api_key", "text_model", "vision_model", "language"):
        if key not in raw:
            continue
        value = raw[key]
        if not isinstance(value, str):
            _warn_invalid_value(key)
            continue
        cleaned = value.strip()
        if key in ("text_model", "vision_model"):
            if not cleaned:
                _warn_invalid_value(key)
                continue
        elif key == "language":
            cleaned = cleaned.lower()
            # Empty means "auto-detect"; anything else must be a known language.
            if cleaned and cleaned not in LANGUAGES:
                _warn_invalid_value(key)
                continue
        values[key] = cleaned
    return values


def load_config() -> RuntimeConfig:
    """Load the configuration, merging defaults and the environment override."""
    values: dict[str, str] = _default_values()

    if CONFIG_FILE.exists():
        try:
            raw: object = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(_("config_warn_invalid_json").format(error=exc), file=sys.stderr)
        except OSError as exc:
            print(_("config_warn_cannot_read").format(error=exc), file=sys.stderr)
        else:
            values = _sanitize_config(raw)

    config = cast(RuntimeConfig, values)
    env_key = _env_api_key()
    if env_key:
        config["api_key"] = env_key
        config["api_key_from_env"] = True
    return config


def _read_persisted_api_key() -> str:
    """Return the API key currently stored on disk (empty when unavailable)."""
    try:
        raw: object = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    if isinstance(raw, dict):
        value = raw.get("api_key")
        if isinstance(value, str):
            return value.strip()
    return ""


def _atomic_write(payload: dict[str, str]) -> None:
    """Write *payload* atomically with owner-only permissions on POSIX."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=".config-", suffix=".json", dir=str(CONFIG_FILE.parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        if os.name != "nt":
            os.chmod(tmp_path, 0o600)
        os.replace(tmp_path, CONFIG_FILE)
    except BaseException:
        with contextlib.suppress(OSError):
            tmp_path.unlink()
        raise


def save_config(config: RuntimeConfig) -> bool:
    """Persist the configuration.

    Keys that come from ``POLLINATIONS_API_KEY`` are not persisted: the key
    previously stored on disk (if any) is preserved instead.
    """
    payload: dict[str, str] = {
        "api_key": config.get("api_key", ""),
        "text_model": config.get("text_model", DEFAULT_CONFIG["text_model"]),
        "vision_model": config.get("vision_model", DEFAULT_CONFIG["vision_model"]),
        "language": config.get("language", DEFAULT_CONFIG["language"]),
    }
    if config.get("api_key_from_env"):
        payload["api_key"] = _read_persisted_api_key()

    try:
        _atomic_write(payload)
        return True
    except OSError as exc:
        print(_("config_error_save").format(error=exc), file=sys.stderr)
        return False
