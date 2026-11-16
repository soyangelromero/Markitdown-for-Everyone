"""Tests for the Pollinations client factory."""

from markitdown_pollinations.constants import (
    CONVERSION_TIMEOUT_SECONDS,
    POLLINATIONS_BASE_URL,
    VALIDATION_USER_AGENT,
)
from markitdown_pollinations.pollinations_client import create_client


def test_create_client_uses_pollinations_base_url():
    client = create_client("test-key")
    assert str(client.base_url).rstrip("/") == POLLINATIONS_BASE_URL.rstrip("/")
    assert client.api_key == "test-key"
    assert float(client.timeout) == CONVERSION_TIMEOUT_SECONDS


def test_create_client_disables_nested_retries():
    """The application owns the retry loop; the SDK must not retry too."""
    client = create_client("test-key")
    assert client.max_retries == 0


def test_create_client_sets_user_agent():
    client = create_client("test-key")
    assert client.default_headers["User-Agent"] == VALIDATION_USER_AGENT
