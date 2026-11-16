"""Tests for the converter module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from markitdown import (
    FileConversionException,
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

from markitdown_pollinations.converter import convert_file
from markitdown_pollinations.i18n import _, set_language


def _make_input(tmp_path: Path, suffix: str = ".txt") -> Path:
    path = tmp_path / f"input{suffix}"
    path.write_text("content", encoding="utf-8")
    return path


def _converted(markdown: str = "Converted text") -> MagicMock:
    result = MagicMock()
    result.markdown = markdown
    return result


def _authentication_error() -> AuthenticationError:
    return AuthenticationError("unauthorized", response=MagicMock(), body=None)


def _permission_error() -> PermissionDeniedError:
    return PermissionDeniedError("forbidden", response=MagicMock(), body=None)


def _not_found_error() -> NotFoundError:
    return NotFoundError("not found", response=MagicMock(), body=None)


def _status_error(code: int, headers: dict[str, str] | None = None) -> APIStatusError:
    response = MagicMock()
    response.status_code = code
    response.headers = headers or {}
    return APIStatusError("boom", response=response, body=None)


def _rate_limit_error(headers: dict[str, str] | None = None) -> RateLimitError:
    response = MagicMock()
    response.status_code = 429
    response.headers = headers or {}
    return RateLimitError("rate limited", response=response, body=None)


def test_convert_success(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.MarkItDown") as mock_md:
        mock_md.return_value.convert.return_value = _converted("line1\nline2\n")
        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is True
    assert result.output_path == str(output_file)
    assert output_file.read_bytes() == b"line1\nline2\n"


def test_convert_creates_parent_directories(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "nested" / "deep" / "output.md"

    with patch("markitdown_pollinations.converter.MarkItDown") as mock_md:
        mock_md.return_value.convert.return_value = _converted()
        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is True
    assert output_file.is_file()


@pytest.mark.parametrize("markdown", ["", "\n\n", "   \n\t"])
def test_convert_empty_content_warns_and_writes_nothing(tmp_path, markdown):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.MarkItDown") as mock_md:
        mock_md.return_value.convert.return_value = _converted(markdown)
        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is True
    assert result.output_path is None
    assert "no content" in result.warning.lower()
    assert not output_file.exists()


def test_convert_unsupported_format(tmp_path):
    input_file = tmp_path / "input.xyz"
    input_file.write_text("content", encoding="utf-8")
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.MarkItDown") as mock_md:
        mock_md.return_value.convert.side_effect = UnsupportedFormatException("bad")
        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is False
    assert "Unsupported" in result.message
    assert ".xyz" in result.message


def test_convert_file_conversion_exception(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.MarkItDown") as mock_md:
        mock_md.return_value.convert.side_effect = FileConversionException("failed")
        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is False
    assert "Conversion failed" in result.message


def test_convert_missing_dependency(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.MarkItDown") as mock_md:
        mock_md.return_value.convert.side_effect = MissingDependencyException("pdf")
        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is False
    assert "Missing dependency" in result.message


def test_convert_authentication_error(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.create_client") as mock_create:
        mock_create.side_effect = _authentication_error()
        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is False
    assert "Invalid API key" in result.message
    assert mock_create.call_count == 1


def test_convert_permission_denied_error(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.create_client") as mock_create:
        mock_create.side_effect = _permission_error()
        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is False
    assert "Permission denied" in result.message
    assert "openai" in result.message


def test_convert_insufficient_balance_error(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.create_client") as mock_create:
        mock_create.side_effect = _status_error(402)
        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is False
    assert "Insufficient pollen" in result.message


def test_convert_not_found_error(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.create_client") as mock_create:
        mock_create.side_effect = _not_found_error()
        result = convert_file(str(input_file), str(output_file), "key", "mystery-model")

    assert result.success is False
    assert "mystery-model" in result.message


def test_convert_rate_limit_retries_with_retry_after(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.time.sleep") as mock_sleep:
        with patch("markitdown_pollinations.converter.create_client") as mock_create:
            mock_create.side_effect = [
                _rate_limit_error({"retry-after": "0.5"}),
                _rate_limit_error({"retry-after": "0.5"}),
                _rate_limit_error({"retry-after": "0.5"}),
            ]
            result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is False
    assert "Rate limit" in result.message
    assert mock_create.call_count == 3
    assert [call.args[0] for call in mock_sleep.call_args_list] == [0.5, 0.5]


def test_convert_retries_on_server_error(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.time.sleep") as mock_sleep:
        with patch("markitdown_pollinations.converter.create_client") as mock_create:
            mock_create.side_effect = [_status_error(503), _status_error(503), _status_error(503)]
            result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is False
    assert "API error (503)" in result.message
    assert mock_create.call_count == 3
    assert mock_sleep.call_count == 2


def test_convert_connection_error_retries_until_success(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.time.sleep") as mock_sleep:
        with patch("markitdown_pollinations.converter.create_client") as mock_create:
            mock_create.side_effect = [
                APIConnectionError(request=MagicMock()),
                APITimeoutError(request=MagicMock()),
                MagicMock(),
            ]
            with patch("markitdown_pollinations.converter.MarkItDown") as mock_md:
                mock_md.return_value.convert.return_value = _converted()
                result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is True
    assert mock_create.call_count == 3
    assert [call.args[0] for call in mock_sleep.call_args_list] == [1.0, 2.0]


def test_convert_connection_error_exhausted(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.time.sleep"):
        with patch("markitdown_pollinations.converter.create_client") as mock_create:
            mock_create.side_effect = [
                APIConnectionError(request=MagicMock()),
                APIConnectionError(request=MagicMock()),
                APIConnectionError(request=MagicMock()),
            ]
            result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is False
    assert "Connection error" in result.message


def test_convert_generic_api_error(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.create_client") as mock_create:
        mock_create.side_effect = APIError("boom", request=MagicMock(), body=None)
        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is False
    assert "API error" in result.message


def test_convert_unexpected_error(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.MarkItDown") as mock_md:
        mock_md.side_effect = RuntimeError("boom")
        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is False
    assert "Unexpected error" in result.message


def test_convert_write_error(tmp_path):
    input_file = _make_input(tmp_path)
    blocker = tmp_path / "blocker"
    blocker.write_text("x", encoding="utf-8")
    output_file = blocker / "output.md"

    with patch("markitdown_pollinations.converter.MarkItDown") as mock_md:
        mock_md.return_value.convert.return_value = _converted()
        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is False
    assert "Could not write" in result.message


def test_convert_without_api_key_skips_llm(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.MarkItDown") as mock_md:
        mock_md.return_value.convert.return_value = _converted()
        result = convert_file(str(input_file), str(output_file), None, "openai")

    assert result.success is True
    mock_md.assert_called_once_with(enable_plugins=True)


def test_convert_uses_ocr_prompt_for_documents(tmp_path):
    input_file = _make_input(tmp_path, ".pdf")
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.create_client"):
        with patch("markitdown_pollinations.converter.MarkItDown") as mock_md:
            mock_md.return_value.convert.return_value = _converted()
            convert_file(str(input_file), str(output_file), "key", "openai")

    assert mock_md.call_args.kwargs["llm_prompt"] == _("llm_prompt_ocr")


def test_convert_uses_image_prompt_for_images(tmp_path):
    input_file = _make_input(tmp_path, ".png")
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.create_client"):
        with patch("markitdown_pollinations.converter.MarkItDown") as mock_md:
            mock_md.return_value.convert.return_value = _converted()
            convert_file(str(input_file), str(output_file), "key", "openai")

    assert mock_md.call_args.kwargs["llm_prompt"] == _("llm_prompt_image")


def test_convert_uses_spanish_prompt(tmp_path):
    set_language("es")
    input_file = _make_input(tmp_path, ".png")
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.create_client"):
        with patch("markitdown_pollinations.converter.MarkItDown") as mock_md:
            mock_md.return_value.convert.return_value = _converted()
            convert_file(str(input_file), str(output_file), "key", "openai")

    prompt = mock_md.call_args.kwargs["llm_prompt"]
    assert prompt.startswith("Describe esta imagen")


def _wrapped(exc: Exception) -> FileConversionException:
    """Build a MarkItDown wrapper that keeps *exc* in its attempts list."""
    from types import SimpleNamespace

    return FileConversionException(
        "file conversion failed",
        attempts=[SimpleNamespace(exc_info=(type(exc), exc, None))],
    )


def test_nested_authentication_error_uses_specific_message(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.MarkItDown") as mock_md:
        mock_md.return_value.convert.side_effect = _wrapped(_authentication_error())
        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is False
    assert "Invalid API key" in result.message


def test_nested_insufficient_balance_uses_specific_message(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.MarkItDown") as mock_md:
        mock_md.return_value.convert.side_effect = _wrapped(_status_error(402))
        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is False
    assert "Insufficient pollen" in result.message


def test_nested_connection_error_retries(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.time.sleep"):
        with patch("markitdown_pollinations.converter.MarkItDown") as mock_md:
            mock_md.return_value.convert.side_effect = [
                _wrapped(APIConnectionError(request=MagicMock())),
                _converted(),
            ]
            result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is True
    assert mock_md.return_value.convert.call_count == 2


def test_nested_unknown_error_falls_back_to_conversion_failed(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.MarkItDown") as mock_md:
        mock_md.return_value.convert.side_effect = _wrapped(ValueError("boom"))
        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is False
    assert "Conversion failed" in result.message
