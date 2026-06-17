"""Tests for the validation module."""

from __future__ import annotations

import inspect
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

from markitdown_pollinations.validation import _validate_key_via_api


def _make_http_error(code: int, msg: str = "error") -> HTTPError:
    """Construct an HTTPError with the required 5 arguments.

    The fp argument must support .read() returning bytes — validation.py calls
    e.read().decode() to parse the error body.
    """
    fp = MagicMock()
    fp.read.return_value = b'{"error": {"message": "test error"}}'
    return HTTPError("https://example.com", code, msg, MagicMock(), fp)


@patch("urllib.request.urlopen")
def test_validate_key_via_api_402_returns_valid(mock_urlopen):
    """HTTP 402 (insufficient balance) returns 'valid' — key works, just no balance."""
    # First call (balance endpoint) raises 500 → fall through to chat.
    # Second call (chat endpoint) raises 402 → return "valid".
    mock_urlopen.side_effect = [
        _make_http_error(500, "Server Error"),
        _make_http_error(402, "Payment Required"),
    ]

    result = _validate_key_via_api("sk-test-key-12345")

    assert result == "valid"
    assert mock_urlopen.call_count == 2


@patch("urllib.request.urlopen")
def test_validate_key_via_api_timeout_returns_unknown(mock_urlopen):
    """Network timeout on both endpoints returns 'unknown'."""
    mock_urlopen.side_effect = [TimeoutError("timed out"), TimeoutError("timed out")]

    result = _validate_key_via_api("sk-test-key-12345")

    assert result == "unknown"


@patch("urllib.request.urlopen")
def test_validate_key_via_api_401_returns_invalid(mock_urlopen):
    """HTTP 401 (unauthorized) returns 'invalid'."""
    mock_urlopen.side_effect = [_make_http_error(401, "Unauthorized")]

    result = _validate_key_via_api("sk-test-key-12345")

    assert result == "invalid"


@patch("urllib.request.urlopen")
def test_validate_key_via_api_successful_balance_returns_valid(mock_urlopen):
    """A successful balance endpoint response with balance returns 'valid'."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = b'{"balance": 100}'
    mock_resp.status = 200
    mock_urlopen.return_value.__enter__.return_value = mock_resp

    result = _validate_key_via_api("sk-test-key-12345")

    assert result == "valid"


def test_no_unicode_arrow_in_validation_output():
    """Regression test: no Unicode arrow (→, U+2192) in validation.py user-facing strings.

    A previous version used the Unicode arrow character in user-facing strings,
    which broke on terminals without Unicode support. This test ensures no such
    characters are reintroduced in validation.py (which got user-facing warning
    strings after T4 extracted it from cli.py).
    """
    import markitdown_pollinations.validation as validation_module

    source = inspect.getsource(validation_module)
    lines = source.splitlines()
    violations = []
    for lineno, line in enumerate(lines, start=1):
        # Check lines that produce user-visible output.
        if ("print(" in line or 'f"' in line or "f'" in line) and (
            "\\u2192" in line or "\u2192" in line
        ):
            violations.append(f"line {lineno}: {line.strip()}")

    assert not violations, "Non-ASCII or \\u2192 found in validation.py:\n" + "\n".join(violations)
