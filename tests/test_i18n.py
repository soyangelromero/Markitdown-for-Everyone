"""Tests that keep the translation dictionaries consistent."""

from __future__ import annotations

import pathlib
import re

from markitdown_pollinations import i18n

SOURCE_DIR = pathlib.Path(__file__).resolve().parents[1] / "src" / "markitdown_pollinations"

# Keys assembled dynamically at runtime, so they are not literal `_("...")` calls.
DYNAMIC_KEYS = {
    "file_kind_pdf",
    "file_kind_image",
    "file_kind_document",
    "llm_prompt_image",
    "llm_prompt_ocr",
}


def _source_text() -> str:
    parts = []
    for path in SOURCE_DIR.glob("*.py"):
        parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


def test_english_and_spanish_have_the_same_keys():
    english = set(i18n.TRANSLATIONS["en"])
    spanish = set(i18n.TRANSLATIONS["es"])
    assert english - spanish == set()
    assert spanish - english == set()


def test_no_empty_translations():
    for language, translations in i18n.TRANSLATIONS.items():
        empty = [key for key, value in translations.items() if not value.strip()]
        assert not empty, f"empty translations in {language}: {empty}"


def test_literal_keys_used_in_code_are_defined():
    used = set(re.findall(r"""_\(\s*["']([a-z0-9_]+)["']\s*\)""", _source_text()))
    undefined = used - set(i18n.TRANSLATIONS["en"])
    assert undefined == set(), f"undefined translation keys: {sorted(undefined)}"


def test_no_dead_translation_keys():
    used = set(re.findall(r"""_\(\s*["']([a-z0-9_]+)["']\s*\)""", _source_text()))
    dead = set(i18n.TRANSLATIONS["en"]) - used - DYNAMIC_KEYS
    assert dead == set(), f"unused translation keys: {sorted(dead)}"


def test_unknown_language_falls_back_to_english():
    i18n.set_language("fr")
    assert i18n.get_language() == "en"


def test_missing_key_returns_key():
    assert i18n._("this_key_does_not_exist") == "this_key_does_not_exist"


def test_known_key_is_translated():
    i18n.set_language("es")
    assert i18n._("goodbye") == "¡Hasta luego!"
