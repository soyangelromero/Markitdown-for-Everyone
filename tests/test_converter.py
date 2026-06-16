"""Tests for the converter module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
)
from markitdown import (
    FileConversionException,
    MissingDependencyException,
    UnsupportedFormatException,
)

from markitdown_pollinations.converter import convert_file


def _make_input(tmp_path: Path, suffix: str = ".txt") -> Path:
    path = tmp_path / f"input{suffix}"
    path.write_text("content", encoding="utf-8")
    return path


def test_convert_success(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.MarkItDown") as MockMD:
        mock_result = MagicMock()
        mock_result.markdown = "Converted text"
        MockMD.return_value.convert.return_value = mock_result

        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is True
    assert result.output_path == str(output_file)
    assert output_file.read_text(encoding="utf-8") == "Converted text"


def test_convert_empty_content_warning(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.MarkItDown") as MockMD:
        mock_result = MagicMock()
        mock_result.markdown = ""
        MockMD.return_value.convert.return_value = mock_result

        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is True
    assert "no content" in result.warning.lower()


def test_convert_unsupported_format(tmp_path):
    input_file = tmp_path / "input.xyz"
    input_file.write_text("content", encoding="utf-8")
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.MarkItDown") as MockMD:
        MockMD.return_value.convert.side_effect = UnsupportedFormatException("bad")

        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is False
    assert "Unsupported" in result.message


def test_convert_file_conversion_exception(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.MarkItDown") as MockMD:
        MockMD.return_value.convert.side_effect = FileConversionException("failed")

        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is False
    assert "Conversion failed" in result.message


def test_convert_missing_dependency(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.MarkItDown") as MockMD:
        MockMD.return_value.convert.side_effect = MissingDependencyException("pdf")

        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is False
    assert "Missing dependency" in result.message


def test_convert_authentication_error(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.create_client") as mock_create:
        mock_create.side_effect = AuthenticationError(
            "unauthorized", response=MagicMock(), body=None
        )

        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is False
    assert "Invalid API key" in result.message


def test_convert_connection_error(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.create_client") as mock_create:
        mock_create.side_effect = APIConnectionError(request=MagicMock())

        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is False
    assert "Connection error" in result.message


def test_convert_not_found_error(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.create_client") as mock_create:
        mock_create.side_effect = NotFoundError(
            "not found", response=MagicMock(), body=None
        )

        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is False
    assert "not found" in result.message.lower()


def test_convert_rate_limit_error(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.create_client") as mock_create:
        mock_create.side_effect = RateLimitError(
            "rate limited", response=MagicMock(), body=None
        )

        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is False
    assert "Rate limit" in result.message


def test_convert_generic_api_error(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.create_client") as mock_create:
        mock_create.side_effect = APIError("boom", request=MagicMock(), body=None)

        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is False
    assert "API error" in result.message


def test_convert_write_error(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "nested" / "output.md"

    with patch("markitdown_pollinations.converter.MarkItDown") as MockMD:
        mock_result = MagicMock()
        mock_result.markdown = "Converted text"
        MockMD.return_value.convert.return_value = mock_result

        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is False
    assert "Could not write" in result.message


def test_convert_retries_on_connection_error(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.time.sleep"):
        with patch("markitdown_pollinations.converter.create_client") as mock_create:
            mock_create.side_effect = [
                APIConnectionError(request=MagicMock()),
                APIConnectionError(request=MagicMock()),
                MagicMock(),
            ]

            with patch("markitdown_pollinations.converter.MarkItDown") as MockMD:
                mock_result = MagicMock()
                mock_result.markdown = "Converted text"
                MockMD.return_value.convert.return_value = mock_result

                result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is True
    assert mock_create.call_count == 3


def test_convert_retries_on_timeout_error(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.time.sleep"):
        with patch("markitdown_pollinations.converter.create_client") as mock_create:
            mock_create.side_effect = [
                APITimeoutError(request=MagicMock()),
                APITimeoutError(request=MagicMock()),
                MagicMock(),
            ]

            with patch("markitdown_pollinations.converter.MarkItDown") as MockMD:
                mock_result = MagicMock()
                mock_result.markdown = "Converted text"
                MockMD.return_value.convert.return_value = mock_result

                result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is True
    assert mock_create.call_count == 3


def test_convert_no_retry_on_auth_error(tmp_path):
    input_file = _make_input(tmp_path)
    output_file = tmp_path / "output.md"

    with patch("markitdown_pollinations.converter.create_client") as mock_create:
        mock_create.side_effect = AuthenticationError(
            "unauthorized", response=MagicMock(), body=None
        )

        result = convert_file(str(input_file), str(output_file), "key", "openai")

    assert result.success is False
    assert "Invalid API key" in result.message
    assert mock_create.call_count == 1
