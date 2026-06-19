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


def _warn_if_key_invalid(api_key: str) -> None:
    """Print a warning if the API key format looks wrong (local check, no network)."""
    valid_prefix = api_key.startswith(("sk_", "sk-"))
    if not valid_prefix:
        print(
            _color(_("key_format_warning"), Colors.YELLOW),
            file=sys.stderr,
        )
    elif len(api_key) < 12:
        print(
            _color(_("key_short_warning"), Colors.YELLOW),
            file=sys.stderr,
        )


def _validate_key_via_api(api_key: str) -> _KeyValidationResult:
    """Validate the API key without consuming pollen if possible.

    First tries the free /account/balance endpoint. If that fails for reasons
    other than an invalid key, falls back to a tiny chat completion call
    ("hello" with max_tokens=2).

    Returns:
        "valid" if the key is accepted, "invalid" if the API rejects it, or
        "unknown" when the check could not complete (e.g. network issue).
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": VALIDATION_USER_AGENT,
    }

    # 1. Try the free balance endpoint first.
    try:
        req = urllib.request.Request(
            POLLINATIONS_BALANCE_URL,
            headers=headers,
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=VALIDATION_TIMEOUT_SECONDS) as resp:
            body = resp.read().decode()
            try:
                data = json.loads(body)
                balance = data.get("balance")
                if balance is not None:
                    print(
                        _color(
                            _("key_valid_balance").format(balance=balance),
                            Colors.GREEN,
                        )
                    )
                else:
                    print(_color(_("key_valid"), Colors.GREEN))
                return "valid"
            except json.JSONDecodeError:
                pass  # Non-JSON response; fall through to chat completion.

    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            msg = json.loads(body).get("error", {}).get("message", f"HTTP {e.code}")
        except json.JSONDecodeError:
            msg = f"HTTP {e.code}"

        if e.code == 401:
            print(
                _color(_("key_invalid"), Colors.YELLOW),
                file=sys.stderr,
            )
            return "invalid"
        # Any other error (403, 500, etc.) falls through to chat completion.
    except (urllib.error.URLError, TimeoutError, OSError):
        pass  # Network issue; fall through to chat completion.

    # 2. Fallback: minimal chat completion.
    payload = json.dumps(
        {
            "model": VALIDATION_MODEL,
            "messages": [{"role": "user", "content": VALIDATION_PROMPT}],
            "max_tokens": VALIDATION_MAX_TOKENS,
        }
    ).encode("utf-8")

    try:
        req = urllib.request.Request(
            POLLINATIONS_CHAT_URL,
            data=payload,
            headers={
                **headers,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=VALIDATION_TIMEOUT_SECONDS) as resp:
            body = resp.read().decode()
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                print(
                    _color(
                        _("warning_prefix").format(warning="non-JSON response from chat endpoint"),
                        Colors.YELLOW,
                    ),
                    file=sys.stderr,
                )
                return "unknown"
            if "choices" not in data:
                print(
                    _color(
                        _("warning_prefix").format(warning="no 'choices' in chat response"),
                        Colors.YELLOW,
                    ),
                    file=sys.stderr,
                )
                return "unknown"
            print(_color(_("key_verified"), Colors.GREEN))
            return "valid"

    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            msg = json.loads(body).get("error", {}).get("message", f"HTTP {e.code}")
        except json.JSONDecodeError:
            msg = f"HTTP {e.code}"

        if e.code == 401:
            print(
                _color(_("key_invalid"), Colors.YELLOW),
                file=sys.stderr,
            )
            return "invalid"
        if e.code == 402:
            print(
                _color(_("key_insufficient_balance"), Colors.YELLOW),
                file=sys.stderr,
            )
            return "valid"
        print(_color(_("warning_prefix").format(warning=msg), Colors.YELLOW), file=sys.stderr)
        return "unknown"

    except (urllib.error.URLError, TimeoutError, OSError):
        print(
            _color(_("key_connection_error"), Colors.YELLOW),
            file=sys.stderr,
        )
        return "unknown"


def _mask_key(api_key: str) -> str:
    """Return a masked representation of an API key for display."""
    if len(api_key) < 12:
        return "****"
    prefix = api_key[:4]
    suffix = api_key[-4:]
    return f"{prefix}****{suffix}"
