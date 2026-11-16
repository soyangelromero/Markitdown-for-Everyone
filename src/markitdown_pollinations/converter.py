"""File conversion using MarkItDown and the Pollinations API."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from markitdown import (
    FileConversionException,
    MarkItDown,
    MissingDependencyException,
    UnsupportedFormatException,
)
from openai import (
    APIConnectionError,
    APIError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
)

from markitdown_pollinations.constants import (
    IMAGE_EXTENSIONS,
    MAX_RETRIES,
    MAX_RETRY_AFTER_SECONDS,
    RETRY_DELAYS,
)
from markitdown_pollinations.i18n import _
from markitdown_pollinations.pollinations_client import create_client

logger = logging.getLogger("markitdown_pollinations")


@dataclass(frozen=True)
class ConversionResult:
    """Result of a conversion attempt."""

    success: bool
    message: str = ""
    warning: str = ""
    output_path: str | None = None


@dataclass(frozen=True)
class _Failure:
    """Classified failure, including whether it is worth retrying."""

    message: str
    retryable: bool = False
    retry_after: float | None = None


@dataclass(frozen=True)
class _Context:
    """File/model context used to classify exceptions."""

    model: str
    suffix: str


def convert_file(
    input_file: str,
    output_file: str,
    api_key: str | None,
    model: str,
) -> ConversionResult:
    """Convert ``input_file`` to Markdown and write it to ``output_file``.

    Args:
        input_file: Path to the file to convert.
        output_file: Path where the Markdown output will be written.
        api_key: Pollinations API key, or None for local-only conversions.
        model: Model name used for image descriptions and OCR.

    Returns:
        ConversionResult describing the outcome.
    """
    context = _Context(model=model, suffix=Path(input_file).suffix.lower())

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            converter = _build_converter(input_file, api_key, model)
            converted = converter.convert(input_file)
        except Exception as exc:
            failure = _classify_exception(exc, context)
            if not failure.retryable or attempt == MAX_RETRIES:
                return ConversionResult(success=False, message=failure.message)
            delay = failure.retry_after
            if delay is None:
                delay = RETRY_DELAYS[min(attempt - 1, len(RETRY_DELAYS) - 1)]
            logger.info(
                _("retry_waiting").format(
                    delay=f"{delay:.1f}",
                    attempt=attempt,
                    max_retries=MAX_RETRIES,
                )
            )
            time.sleep(delay)
            continue

        content = converted.markdown or ""
        if not content.strip():
            return ConversionResult(
                success=True,
                warning=_("conversion_empty_warning"),
            )

        write_error = _write_output(output_file, content)
        if write_error is not None:
            return ConversionResult(success=False, message=write_error)
        return ConversionResult(success=True, output_path=output_file)

    # Defensive: the loop either returns or retries until MAX_RETRIES.
    return ConversionResult(
        success=False,
        message=_("unexpected_error").format(error="retry loop exhausted"),
    )


def _build_converter(input_file: str, api_key: str | None, model: str) -> MarkItDown:
    """Build a MarkItDown instance, with or without an LLM client."""
    if not api_key:
        # Plugins may load, but OCR/vision are silently skipped without a client.
        return MarkItDown(enable_plugins=True)

    prompt_key = (
        "llm_prompt_image"
        if Path(input_file).suffix.lower() in IMAGE_EXTENSIONS
        else "llm_prompt_ocr"
    )
    return MarkItDown(
        enable_plugins=True,
        llm_client=create_client(api_key),
        llm_model=model,
        llm_prompt=_(prompt_key),
    )


def _write_output(output_file: str, content: str) -> str | None:
    """Write *content* to *output_file*; return an error message on failure."""
    try:
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    except OSError as exc:
        return _("write_error").format(error=exc)
    return None


def _exception_detail(exc: Exception) -> str:
    """Return a readable detail string for an API exception."""
    detail = getattr(exc, "message", None) or str(exc)
    cleaned = str(detail).strip()
    return cleaned or _("unknown_api_error")


def _retry_after_seconds(exc: Exception) -> float | None:
    """Extract and clamp a Retry-After header from an API error, if present."""
    response = getattr(exc, "response", None)
    headers = getattr(response, "headers", None)
    if headers is None:
        return None
    raw = headers.get("retry-after")
    try:
        seconds = float(raw)
    except (TypeError, ValueError):
        return None
    return min(max(seconds, 0.0), MAX_RETRY_AFTER_SECONDS)


_Handler = Callable[[Exception, _Context], _Failure | None]


def _classify_connection(exc: Exception, context: _Context) -> _Failure | None:
    if isinstance(exc, (APIConnectionError, APITimeoutError)):
        return _Failure(_("conn_error_fatal"), retryable=True)
    return None


def _classify_auth(exc: Exception, context: _Context) -> _Failure | None:
    if isinstance(exc, AuthenticationError):
        return _Failure(_("auth_error"))
    if isinstance(exc, PermissionDeniedError):
        return _Failure(_("permission_error").format(model=context.model))
    return None


def _classify_rate_limit(exc: Exception, context: _Context) -> _Failure | None:
    if isinstance(exc, RateLimitError):
        return _Failure(
            _("rate_limit").format(error=_exception_detail(exc)),
            retryable=True,
            retry_after=_retry_after_seconds(exc),
        )
    return None


def _classify_not_found(exc: Exception, context: _Context) -> _Failure | None:
    if isinstance(exc, NotFoundError):
        return _Failure(_("model_not_found").format(model=context.model))
    return None


def _classify_http_status(exc: Exception, context: _Context) -> _Failure | None:
    if not isinstance(exc, APIStatusError):
        return None
    if exc.status_code == 402:
        return _Failure(_("insufficient_balance_error"))
    if exc.status_code == 403:
        return _Failure(_("permission_error").format(model=context.model))
    detail = _exception_detail(exc)
    message = _("api_status_error").format(code=exc.status_code, detail=detail)
    return _Failure(message, retryable=exc.status_code >= 500)


def _classify_api_error(exc: Exception, context: _Context) -> _Failure | None:
    if isinstance(exc, APIError):
        return _Failure(_("api_error").format(detail=_exception_detail(exc)))
    return None


def _classify_conversion_error(exc: Exception, context: _Context) -> _Failure | None:
    if isinstance(exc, MissingDependencyException):
        return _Failure(_("missing_dep").format(error=exc))
    if isinstance(exc, UnsupportedFormatException):
        return _Failure(_("unsupported_format").format(ext=context.suffix))
    if isinstance(exc, FileConversionException):
        return _Failure(_("conversion_failed").format(error=exc))
    return None


_HANDLERS: tuple[_Handler, ...] = (
    _classify_connection,
    _classify_auth,
    _classify_rate_limit,
    _classify_not_found,
    _classify_http_status,
    _classify_api_error,
    _classify_conversion_error,
)


def _classify_exception(exc: Exception, context: _Context) -> _Failure:
    """Map an exception to a user-facing message and retry policy."""
    for handler in _HANDLERS:
        failure = handler(exc, context)
        if failure is not None:
            return failure
    return _Failure(_("unexpected_error").format(error=exc))
