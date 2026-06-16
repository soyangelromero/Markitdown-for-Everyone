"""File conversion using MarkItDown + Pollinations API."""

from __future__ import annotations


from dataclasses import dataclass
import time
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

from markitdown_pollinations.pollinations_client import create_client


MAX_RETRIES = 3
RETRY_DELAYS = [1, 2, 4]


@dataclass
class ConversionResult:
    """Result of a conversion attempt."""

    success: bool
    cancelled: bool = False
    message: str = ""
    warning: str = ""
    output_path: str | None = None


def convert_file(
    input_file: str,
    output_file: str,
    api_key: str,
    model: str,
) -> ConversionResult:
    """
    Convert ``input_file`` to Markdown and write it to ``output_file``.

    Args:
        input_file: Path to the file to convert.
        output_file: Path where the Markdown output will be written.
        api_key: Pollinations API key.
        model: Model name to use for vision/image descriptions.

    Returns:
        ConversionResult describing the outcome.
    """
    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            client = create_client(api_key)
            md = MarkItDown(
                llm_client=client,
                llm_model=model,
                llm_prompt="Describe this image in detail, including any text, objects, and context.",
            )

            result = md.convert(input_file)

            content = result.markdown

            if not content:
                warning = "Conversion succeeded but produced no content."
            else:
                warning = ""

            try:
                Path(output_file).write_text(content, encoding="utf-8")
            except (IOError, OSError) as e:
                return ConversionResult(
                    success=False,
                    message=f"Could not write output file: {e}",
                )

            return ConversionResult(
                success=True,
                output_path=output_file,
                warning=warning,
            )

        except (AuthenticationError, PermissionDeniedError):
            return ConversionResult(
                success=False,
                message="Invalid API key. Get your key at https://enter.pollinations.ai",
            )

        except (APIConnectionError, APITimeoutError) as e:
            last_error = e
            if attempt < MAX_RETRIES:
                delay = RETRY_DELAYS[attempt - 1]
                print(f"Connection error (attempt {attempt}/{MAX_RETRIES}). Retrying in {delay}s...")
                time.sleep(delay)
            else:
                return ConversionResult(
                    success=False,
                    message="Connection error. Please check your internet connection.",
                )

        except NotFoundError:
            return ConversionResult(
                success=False,
                message=f"Model '{model}' not found.",
            )

        except RateLimitError as e:
            return ConversionResult(
                success=False,
                message=f"Rate limit exceeded: {e}",
            )

        except APIStatusError as e:
            detail = getattr(e, "message", str(e)) or "Unknown API error"
            return ConversionResult(
                success=False,
                message=f"API error ({e.status_code}): {detail}",
            )

        except APIError as e:
            detail = getattr(e, "message", str(e)) or "Unknown API error"
            return ConversionResult(
                success=False,
                message=f"API error: {detail}",
            )

        except UnsupportedFormatException:
            return ConversionResult(
                success=False,
                message=f"Unsupported file format: {Path(input_file).suffix}",
            )

        except FileConversionException as e:
            return ConversionResult(
                success=False,
                message=f"Conversion failed: {e}",
            )

        except MissingDependencyException as e:
            return ConversionResult(
                success=False,
                message=f"Missing dependency: {e}",
            )

        except Exception as e:  # noqa: BLE001 - last-resort safety net
            return ConversionResult(
                success=False,
                message=f"Unexpected error: {e}",
            )

    # This should never be reached, but safety net
    return ConversionResult(
        success=False,
        message=f"Unexpected error after {MAX_RETRIES} retries: {last_error}",
    )
