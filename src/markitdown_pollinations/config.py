"""Configuration module with robust load/save for markitdown_pollinations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict


class Config(TypedDict):
    """Configuration type hint."""
    api_key: str
    model: str


CONFIG_FILE = Path(__file__).resolve().parents[2] / "config.json"

DEFAULT_CONFIG: Config = {"api_key": "", "model": "openai"}


def load_config() -> Config:
    """Load configuration from config.json or return defaults.

    Returns DEFAULT_CONFIG if file is missing, unreadable, or invalid JSON.
    Prints a warning message on any error.
    """
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            config = json.load(f)
            if not isinstance(config, dict):
                print("Warning: Config file is not a dict, using defaults")
                return DEFAULT_CONFIG.copy()
            return config  # type: ignore[return-value]
    except json.JSONDecodeError as e:
        print(f"Warning: Config file contains invalid JSON: {e}")
        return DEFAULT_CONFIG.copy()
    except (IOError, OSError) as e:
        print(f"Warning: Could not read config file: {e}")
        return DEFAULT_CONFIG.copy()


def save_config(config: Config) -> bool:
    """Save configuration to config.json.

    Args:
        config: Configuration dictionary to save.

    Returns:
        True on success, False on failure.
        Does not raise exceptions.
    """
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except (IOError, OSError) as e:
        print(f"Error: Could not save config file: {e}")
        return False