"""API key validation via Pollinations endpoints."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from typing import Literal

from markitdown_pollinations.constants import (
    POLLINATIONS_BALANCE_URL,
    POLLINATIONS_CHAT_URL,
    VALIDATION_MAX_TOKENS,
    VALIDATION_MODEL,
    VALIDATION_PROMPT,
    VALIDATION_TIMEOUT_SECONDS,
    VALIDATION_USER_AGENT,
    Colors,
    _color,
)
from markitdown_pollinations.i18n import _

_KeyValidationResult = Literal["valid", "invalid", "unknown"]


def _warn(message: str) -> None:
    print(_color(message, Colors.YELLOW), file=sys.stderr)


def _warn_if_key_invalid(api_key: str) -> None:
    """Print a warning if the API key format looks wrong (local check, no network)."""
    if not api_key.startswith("sk_"):
        _warn(_("key_format_warning"))
    elif len(api_key) < 12:
        _warn(_("key_short_warning"))


def _mask_key(api_key: str) -> str:
    """Return a masked representation of an API key for display."""
    if len(api_key) < 12:
        return "****"
    return f"{api_key[:4]}****{api_key[-4:]}"


def _decode_body(body: bytes) -> str:
    return body.decode("utf-8", errors="replace")


def _http_error_message(exc: urllib.error.HTTPError) -> str:
    """Extract a readable message from an HTTP error body."""
    try:
        parsed: object = json.loads(_decode_body(exc.read()))
    except json.JSONDecodeError:
        return f"HTTP {exc.code}"
    if isinstance(parsed, dict):
        error = parsed.get("error")
        if isinstance(error, dict):
            message = error.get("message")
            if isinstance(message, str) and message:
                return message
    return f"HTTP {exc.code}"


def _balance_headers(api_key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {api_key}", "User-Agent": VALIDATION_USER_AGENT}


def _check_balance(api_key: str) -> _KeyValidationResult | None:
    """Check the key against the free balance endpoint.

    Returns None when the check is inconclusive and the caller should fall back
    to a minimal chat completion request.
    """
    request = urllib.request.Request(
        POLLINATIONS_BALANCE_URL,
        headers=_balance_headers(api_key),
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=VALIDATION_TIMEOUT_SECONDS) as response:
            body = _decode_body(response.read())
    except urllib.error.HTTPError as exc:
        if exc.code == 401:
            _warn(_("key_invalid"))
            return "invalid"
        return None
    except (urllib.error.URLError, TimeoutError, OSError):
        return None

    try:
        data: object = json.loads(body)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict) or "error" in data:
        return None

    balance = data.get("balance")
    if balance is None:
        print(_color(_("key_valid"), Colors.GREEN))
    else:
        print(_color(_("key_valid_balance").format(balance=balance), Colors.GREEN))
    return "valid"


def _check_chat(api_key: str) -> _KeyValidationResult:
    """Validate the key with a minimal chat completion request."""
    payload = json.dumps(
        {
            "model": VALIDATION_MODEL,
            "messages": [{"role": "user", "content": VALIDATION_PROMPT}],
            "max_tokens": VALIDATION_MAX_TOKENS,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        POLLINATIONS_CHAT_URL,
        data=payload,
        headers={
            **_balance_headers(api_key),
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=VALIDATION_TIMEOUT_SECONDS) as response:
            body = _decode_body(response.read())
    except urllib.error.HTTPError as exc:
        if exc.code == 401:
            _warn(_("key_invalid"))
            return "invalid"
        if exc.code == 402:
            print(_color(_("key_insufficient_balance"), Colors.YELLOW))
            return "valid"
        _warn(_("warning_prefix").format(warning=_http_error_message(exc)))
        return "unknown"
    except (urllib.error.URLError, TimeoutError, OSError):
        _warn(_("key_connection_error"))
        return "unknown"

    try:
        data: object = json.loads(body)
    except json.JSONDecodeError:
        _warn(_("warning_prefix").format(warning=_("validation_nonjson_response")))
        return "unknown"
    if not isinstance(data, dict) or "choices" not in data:
        _warn(_("warning_prefix").format(warning=_("validation_no_choices")))
        return "unknown"

    print(_color(_("key_verified"), Colors.GREEN))
    return "valid"


def _validate_key_via_api(api_key: str) -> _KeyValidationResult:
    """Validate the API key without consuming pollen when possible.

    First tries the free ``/account/balance`` endpoint. If that check is
    inconclusive (network issue, non-JSON body, unexpected status), falls back
    to a tiny chat completion call ("hello" with ``max_tokens=2``).

    Returns:
        "valid" if the key is accepted, "invalid" if the API rejects it, or
        "unknown" when the check could not complete (e.g. network issue).
    """
    balance_result = _check_balance(api_key)
    if balance_result is not None:
        return balance_result
    return _check_chat(api_key)
