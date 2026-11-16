"""Live model catalog for Pollinations.

The public catalog at ``/models`` exposes canonical ``publisher/model`` IDs,
aliases, accepted input modalities and whether a model requires paid pollen.
The CLI uses it to label recommendations and to warn about invalid selections.

Network failures are never fatal: ``fetch_catalog()`` returns ``None`` and the
caller falls back to the built-in recommendations.
"""

from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.request
from collections.abc import Sequence
from dataclasses import dataclass

from markitdown_pollinations.constants import (
    MODELS_TIMEOUT_SECONDS,
    POLLINATIONS_MODELS_URL,
    VALIDATION_USER_AGENT,
)
from markitdown_pollinations.i18n import _

logger = logging.getLogger("markitdown_pollinations")

_CACHE_TTL_SECONDS = 300.0
_catalog_cache: tuple[float, ModelCatalog] | None = None


@dataclass(frozen=True)
class ModelInfo:
    """A single model from the live catalog."""

    name: str
    aliases: tuple[str, ...]
    input_modalities: frozenset[str]
    paid_only: bool

    @property
    def accepts_images(self) -> bool:
        """Whether the model accepts image input."""
        return "image" in self.input_modalities


@dataclass(frozen=True)
class ModelCatalog:
    """Immutable snapshot of the Pollinations model catalog."""

    models: tuple[ModelInfo, ...]

    def find(self, model: str) -> ModelInfo | None:
        """Find a model by canonical name or alias (case-insensitive)."""
        needle = model.strip().lower()
        if not needle:
            return None
        for info in self.models:
            if info.name.lower() == needle:
                return info
            if any(alias.lower() == needle for alias in info.aliases):
                return info
        return None

    def is_paid(self, model: str) -> bool | None:
        """Return whether *model* requires paid pollen, or None if unknown."""
        info = self.find(model)
        return info.paid_only if info is not None else None

    def accepts_images(self, model: str) -> bool | None:
        """Return whether *model* accepts images, or None if unknown."""
        info = self.find(model)
        return info.accepts_images if info is not None else None

    def filter_known(self, models: Sequence[str]) -> tuple[str, ...]:
        """Return only the entries that exist in the catalog."""
        return tuple(model for model in models if self.find(model) is not None)

    def tags(self, model: str) -> tuple[str, ...]:
        """Return human-readable capability tags for *model*."""
        info = self.find(model)
        if info is None:
            return ()
        tags: list[str] = []
        if info.accepts_images:
            tags.append(_("model_tag_vision"))
        if info.paid_only:
            tags.append(_("model_tag_paid"))
        return tuple(tags)

    def annotate(self, model: str) -> str:
        """Return *model* with its capability tags, e.g. ``openai (vision)``."""
        tags = self.tags(model)
        return f"{model} ({', '.join(tags)})" if tags else model


def clear_cache() -> None:
    """Clear the in-memory catalog cache (used by tests and after errors)."""
    global _catalog_cache
    _catalog_cache = None


def _parse_model(item: object) -> ModelInfo | None:
    """Parse one catalog entry, returning None when it is malformed."""
    if not isinstance(item, dict):
        return None
    name = item.get("name")
    if not isinstance(name, str) or not name.strip():
        return None
    raw_aliases = item.get("aliases")
    aliases = (
        tuple(alias for alias in raw_aliases if isinstance(alias, str))
        if isinstance(raw_aliases, list)
        else ()
    )
    raw_modalities = item.get("input_modalities")
    modalities = (
        frozenset(value for value in raw_modalities if isinstance(value, str))
        if isinstance(raw_modalities, list)
        else frozenset()
    )
    return ModelInfo(
        name=name.strip(),
        aliases=aliases,
        input_modalities=modalities,
        paid_only=bool(item.get("paid_only", False)),
    )


def fetch_catalog(
    *, timeout: float = MODELS_TIMEOUT_SECONDS, use_cache: bool = True
) -> ModelCatalog | None:
    """Fetch the public model catalog, returning None when unavailable."""
    global _catalog_cache
    now = time.monotonic()
    if use_cache and _catalog_cache is not None:
        fetched_at, cached = _catalog_cache
        if now - fetched_at < _CACHE_TTL_SECONDS:
            return cached

    request = urllib.request.Request(
        POLLINATIONS_MODELS_URL,
        headers={"User-Agent": VALIDATION_USER_AGENT, "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
        data: object = json.loads(body)
    except (OSError, ValueError) as exc:
        logger.debug("model catalog unavailable: %s", exc)
        return None

    if not isinstance(data, list):
        logger.debug("model catalog returned an unexpected payload")
        return None

    models = tuple(info for item in data if (info := _parse_model(item)) is not None)
    if not models:
        return None
    catalog = ModelCatalog(models=models)
    _catalog_cache = (now, catalog)
    return catalog
