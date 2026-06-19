"""Pollinations API client with model validation."""

from __future__ import annotations

from openai import OpenAI

from markitdown_pollinations.constants import CONVERSION_TIMEOUT_SECONDS, POLLINATIONS_BASE_URL


def create_client(api_key: str) -> OpenAI:
    """Create an OpenAI client configured for Pollinations."""
    return OpenAI(
        base_url=POLLINATIONS_BASE_URL,
        api_key=api_key,
        timeout=CONVERSION_TIMEOUT_SECONDS,
    )
