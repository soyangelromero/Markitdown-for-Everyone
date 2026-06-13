"""Tests for the Pollinations client module."""

from unittest.mock import MagicMock, patch

import pytest
from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AuthenticationError,
    NotFoundError,
    PermissionDeniedError,
)

from markitdown_pollinations.pollinations_client import (
    ModelValidationThread,
    create_client,
    validate_model,
)
from markitdown_pollinations.constants import POLLINATIONS_BASE_URL


def test_create_client_uses_pollinations_base_url():
    client = create_client("test-key")
    assert str(client.base_url).rstrip("/") == POLLINATIONS_BASE_URL.rstrip("/")
    assert client.api_key == "test-key"


def test_validate_model_success():
    with patch("markitdown_pollinations.pollinations_client.OpenAI") as MockClient:
        instance = MagicMock()
        instance.models.list.return_value = MagicMock(
            data=[MagicMock(id="openai"), MagicMock(id="glm")]
        )
        MockClient.return_value = instance

        ok, msg = validate_model("key", "openai")
        assert ok is True
        assert msg == ""


def test_validate_model_not_found():
    with patch("markitdown_pollinations.pollinations_client.OpenAI") as MockClient:
        instance = MagicMock()
        instance.models.list.return_value = MagicMock(data=[MagicMock(id="glm")])
        MockClient.return_value = instance

        ok, msg = validate_model("key", "openai")
        assert ok is False
        assert "not found" in msg.lower()
        assert "glm" in msg


@pytest.mark.parametrize(
    "exc_class",
    [AuthenticationError, PermissionDeniedError],
)
def test_validate_model_invalid_api_key(exc_class):
    with patch("markitdown_pollinations.pollinations_client.OpenAI") as MockClient:
        instance = MagicMock()
        instance.models.list.side_effect = exc_class(
            "unauthorized", response=MagicMock(), body=None
        )
        MockClient.return_value = instance

        ok, msg = validate_model("bad-key", "openai")
        assert ok is False
        assert "Invalid API key" in msg


@pytest.mark.parametrize(
    "exc_class",
    [APIConnectionError, APITimeoutError],
)
def test_validate_model_connection_error(exc_class):
    with patch("markitdown_pollinations.pollinations_client.OpenAI") as MockClient:
        instance = MagicMock()
        instance.models.list.side_effect = exc_class(request=MagicMock())
        MockClient.return_value = instance

        ok, msg = validate_model("key", "openai")
        assert ok is False
        assert "Connection error" in msg


def test_validate_model_not_found_error():
    with patch("markitdown_pollinations.pollinations_client.OpenAI") as MockClient:
        instance = MagicMock()
        instance.models.list.side_effect = NotFoundError(
            "not found", response=MagicMock(), body=None
        )
        MockClient.return_value = instance

        ok, msg = validate_model("key", "openai")
        assert ok is False
        assert "not found" in msg.lower()


def test_validate_model_generic_api_error():
    with patch("markitdown_pollinations.pollinations_client.OpenAI") as MockClient:
        instance = MagicMock()
        instance.models.list.side_effect = APIError(
            "boom", request=MagicMock(), body=None
        )
        MockClient.return_value = instance

        ok, msg = validate_model("key", "openai")
        assert ok is False
        assert "Error validating model" in msg


def test_model_validation_thread_calls_callback():
    results = []

    def callback(ok, msg):
        results.append((ok, msg))

    with patch(
        "markitdown_pollinations.pollinations_client.validate_model"
    ) as mock_validate:
        mock_validate.return_value = (True, "")
        thread = ModelValidationThread("key", "openai", callback)
        thread.start()
        thread.join(timeout=2)

    assert results == [(True, "")]
