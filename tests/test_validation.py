"""Tests for the validation module."""

from __future__ import annotations

import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from markitdown_pollinations.i18n import set_language
from markitdown_pollinations.validation import (
    _mask_key,
    _validate_key_via_api,
    _warn_if_key_invalid,
)

KEY = "sk-test-key-12345"


def _make_http_error(code: int, body: bytes = b'{"error": {"message": "test error"}}'):
    """Construct an HTTPError whose body can be read by validation.py."""
    fp = MagicMock()
    fp.read.return_value = body
    return urllib.error.HTTPError("https://example.com", code, "error", MagicMock(), fp)


def _response(body: bytes) -> MagicMock:
    response = MagicMock()
    response.read.return_value = body
    response.__enter__.return_value = response
    return response


@patch("markitdown_pollinations.validation.urllib.request.urlopen")
def test_validate_key_via_api_402_returns_valid(mock_urlopen):
    """HTTP 402 (insufficient balance) returns 'valid' — key works, no balance."""
    mock_urlopen.side_effect = [
        _make_http_error(500, b"server error"),
        _make_http_error(402, b'{"error": {"message": "payment required"}}'),
    ]
    assert _validate_key_via_api(KEY) == "valid"
    assert mock_urlopen.call_count == 2


@patch("markitdown_pollinations.validation.urllib.request.urlopen")
def test_validate_key_via_api_timeout_returns_unknown(mock_urlopen):
    mock_urlopen.side_effect = [TimeoutError("timed out"), TimeoutError("timed out")]
    assert _validate_key_via_api(KEY) == "unknown"


@patch("markitdown_pollinations.validation.urllib.request.urlopen")
def test_validate_key_via_api_401_returns_invalid(mock_urlopen):
    mock_urlopen.side_effect = [_make_http_error(401)]
    assert _validate_key_via_api(KEY) == "invalid"


@patch("markitdown_pollinations.validation.urllib.request.urlopen")
def test_validate_key_via_api_successful_balance_returns_valid(mock_urlopen):
    mock_urlopen.return_value = _response(b'{"balance": 100}')
    assert _validate_key_via_api(KEY) == "valid"
    assert mock_urlopen.call_count == 1


@patch("markitdown_pollinations.validation.urllib.request.urlopen")
def test_validate_key_balance_without_balance_field_is_valid(mock_urlopen):
    mock_urlopen.return_value = _response(b'{"user": "angel"}')
    assert _validate_key_via_api(KEY) == "valid"


@patch("markitdown_pollinations.validation.urllib.request.urlopen")
def test_validate_key_balance_error_payload_falls_back_to_chat(mock_urlopen):
    mock_urlopen.side_effect = [
        _response(b'{"error": {"message": "nope"}}'),
        _response(b'{"choices": [{"message": {"content": "hi"}}]}'),
    ]
    assert _validate_key_via_api(KEY) == "valid"
    assert mock_urlopen.call_count == 2


@patch("markitdown_pollinations.validation.urllib.request.urlopen")
def test_validate_key_200_with_choices_returns_valid(mock_urlopen):
    mock_urlopen.side_effect = [
        _make_http_error(500, b"server error"),
        _response(b'{"choices": [{"message": {"content": "hi"}}]}'),
    ]
    assert _validate_key_via_api(KEY) == "valid"


@patch("markitdown_pollinations.validation.urllib.request.urlopen")
def test_validate_key_200_with_error_body_returns_unknown(mock_urlopen):
    mock_urlopen.side_effect = [
        _make_http_error(500, b"server error"),
        _response(b'{"error": {"message": "oops"}}'),
    ]
    assert _validate_key_via_api(KEY) == "unknown"


@patch("markitdown_pollinations.validation.urllib.request.urlopen")
def test_validate_key_200_with_non_json_returns_unknown(mock_urlopen, capsys):
    mock_urlopen.side_effect = [
        _make_http_error(500, b"server error"),
        _response(b"not json at all"),
    ]
    assert _validate_key_via_api(KEY) == "unknown"
    assert "non-JSON" in capsys.readouterr().err


@patch("markitdown_pollinations.validation.urllib.request.urlopen")
def test_balance_non_json_falls_back_to_chat(mock_urlopen):
    mock_urlopen.side_effect = [
        _response(b"not json"),
        _response(b'{"choices": []}'),
    ]
    assert _validate_key_via_api(KEY) == "valid"


@patch("markitdown_pollinations.validation.urllib.request.urlopen")
def test_connection_error_returns_unknown(mock_urlopen, capsys):
    mock_urlopen.side_effect = [
        urllib.error.URLError("offline"),
        urllib.error.URLError("offline"),
    ]
    assert _validate_key_via_api(KEY) == "unknown"
    assert "could not connect" in capsys.readouterr().err


@patch("markitdown_pollinations.validation.urllib.request.urlopen")
def test_chat_http_error_message_is_reported(mock_urlopen, capsys):
    mock_urlopen.side_effect = [
        _make_http_error(500, b"server error"),
        _make_http_error(400, b'{"error": {"message": "bad request"}}'),
    ]
    assert _validate_key_via_api(KEY) == "unknown"
    assert "bad request" in capsys.readouterr().err


@patch("markitdown_pollinations.validation.urllib.request.urlopen")
def test_spanish_warnings_are_translated(mock_urlopen, capsys):
    set_language("es")
    mock_urlopen.side_effect = [
        urllib.error.URLError("offline"),
        urllib.error.URLError("offline"),
    ]
    assert _validate_key_via_api(KEY) == "unknown"
    assert "Advertencia" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("api_key", "expected"),
    [
        ("plain-key", "usually start with 'sk_'"),
        ("sk_short", "too short"),
        ("sk_valid_key_123456", None),
    ],
)
def test_warn_if_key_invalid(api_key, expected, capsys):
    _warn_if_key_invalid(api_key)
    stderr = capsys.readouterr().err
    if expected is None:
        assert stderr == ""
    else:
        assert expected in stderr


def test_mask_key_short():
    assert _mask_key("short") == "****"


def test_mask_key_long():
    assert _mask_key("sk_abcdef123456") == "sk_a****3456"
