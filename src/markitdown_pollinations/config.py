"""Configuration module with robust load/save for markitdown_pollinations."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TypedDict

from platformdirs import user_config_dir


class Config(TypedDict):
    """Configuration type hint."""
    api_key: str
    text_model: str
    vision_model: str


CONFIG_FILE = Path(user_config_dir("markitdown-for-everyone", "AngelRomero")) / "config.json"

DEFAULT_CONFIG: Config = {
    "api_key": "",
    "text_model": "openai",
    "vision_model": "openai",
}


def load_config() -> Config:
    """Load configuration from config.json or return defaults.

    The ``POLLINATIONS_API_KEY`` environment variable, if set, overrides the
    API key stored in the config file so users can avoid persisting secrets
    to disk.

    Returns DEFAULT_CONFIG if file is missing, unreadable, or invalid JSON.
    Prints a warning message on any error.
    """
    env_key = os.environ.get("POLLINATIONS_API_KEY", "").strip()
    if env_key:
        config = DEFAULT_CONFIG.copy()
        config["api_key"] = env_key
        return config

    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            config = json.load(f)
            if not isinstance(config, dict):
                print("Warning: Config file is not a dict, using defaults")
                return DEFAULT_CONFIG.copy()
            merged = {**DEFAULT_CONFIG, **config}
            return merged
    except json.JSONDecodeError as e:
        print(f"Warning: Config file contains invalid JSON: {e}")
        return DEFAULT_CONFIG.copy()
    except (IOError, OSError) as e:
        print(f"Warning: Could not read config file: {e}")
        return DEFAULT_CONFIG.copy()


def save_config(config: Config) -> bool:
    """Save configuration to config.json.

    On Unix-like systems the file permissions are set to 0o600 so only the
    owner can read the API key. On Windows this step is skipped gracefully.

    Args:
        config: Configuration dictionary to save.

    Returns:
        True on success, False on failure.
        Does not raise exceptions.
    """
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        # Restrict permissions on Unix-like systems. Best-effort on Windows.
        if os.name != "nt":
            try:
                os.chmod(CONFIG_FILE, 0o600)
            except (OSError, AttributeError):
                pass
        return True
    except (IOError, OSError) as e:
        print(f"Error: Could not save config file: {e}")
        return False