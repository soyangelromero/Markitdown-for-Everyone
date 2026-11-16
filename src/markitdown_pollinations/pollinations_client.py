"""Pollinations API client factory."""

from __future__ import annotations

from openai import OpenAI

from markitdown_pollinations.constants import (
    CONVERSION_TIMEOUT_SECONDS,
    POLLINATIONS_BASE_URL,
    VALIDATION_USER_AGENT,
)


def create_client(api_key: str) -> OpenAI:
    """Create an OpenAI-compatible client configured for Pollinations.

    ``max_retries=0`` is intentional: the application owns the retry loop so
    retries are not nested (which could otherwise multiply request attempts).
    """
    return OpenAI(
        base_url=POLLINATIONS_BASE_URL,
        api_key=api_key,
        timeout=CONVERSION_TIMEOUT_SECONDS,
        max_retries=0,
        default_headers={"User-Agent": VALIDATION_USER_AGENT},
    )
