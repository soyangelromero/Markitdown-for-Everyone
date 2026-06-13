"""Pollinations API client with model validation."""

from __future__ import annotations

import threading
from typing import Callable

from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AuthenticationError,
    NotFoundError,
    OpenAI,
    PermissionDeniedError,
)

from markitdown_pollinations.constants import POLLINATIONS_BASE_URL


def create_client(api_key: str) -> OpenAI:
    """Create an OpenAI client configured for Pollinations."""
    return OpenAI(base_url=POLLINATIONS_BASE_URL, api_key=api_key)


def validate_model(api_key: str, model_name: str) -> tuple[bool, str]:
    """
    Validate that the model exists in Pollinations.

    Returns:
        (success, message) where message is empty on success or an error
        description on failure.
    """
    try:
        client = create_client(api_key)
        models = client.models.list()
        model_ids = [m.id for m in models.data]

        if model_name not in model_ids:
            available = ", ".join(sorted(model_ids)[:10])
            if len(model_ids) > 10:
                available += f"... and {len(model_ids) - 10} more"
            return False, f"Model '{model_name}' not found.\n\nAvailable models: {available}"

        return True, ""

    except (AuthenticationError, PermissionDeniedError):
        return False, "Invalid API key. Get your key at https://enter.pollinations.ai"

    except (APIConnectionError, APITimeoutError):
        return False, "Connection error. Please check your internet connection."

    except NotFoundError as e:
        return False, f"Model '{model_name}' not found. Error: {e}"

    except APIError as e:
        return False, f"Error validating model: {e}"

    except Exception as e:  # noqa: BLE001 - last-resort safety net
        return False, f"Unexpected error validating model: {e}"


class ModelValidationThread(threading.Thread):
    """
    Background thread for model validation.

    Calls ``validate_model`` and invokes ``on_result`` with the outcome.
    """

    def __init__(
        self,
        api_key: str,
        model_name: str,
        on_result: Callable[[bool, str], None],
    ) -> None:
        super().__init__(daemon=True)
        self.api_key = api_key
        self.model_name = model_name
        self.on_result = on_result

    def run(self) -> None:
        success, message = validate_model(self.api_key, self.model_name)
        self.on_result(success, message)
