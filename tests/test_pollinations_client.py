"""Tests for the Pollinations client module."""

from markitdown_pollinations.constants import CONVERSION_TIMEOUT_SECONDS, POLLINATIONS_BASE_URL
from markitdown_pollinations.pollinations_client import create_client


def test_create_client_uses_pollinations_base_url():
    client = create_client("test-key")
    assert str(client.base_url).rstrip("/") == POLLINATIONS_BASE_URL.rstrip("/")
    assert client.api_key == "test-key"
    assert float(client.timeout) == CONVERSION_TIMEOUT_SECONDS
