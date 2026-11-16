# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.1] — 2026-11-16

### Added

- First PyPI release: `markitdown-for-everyone==0.4.1` published via Trusted Publishing
  (<https://pypi.org/project/markitdown-for-everyone/>).

### Fixed

- Specific API error messages (401 invalid key, 402 insufficient pollen, 403
  permission, 429 rate limit) were lost when MarkItDown wrapped the original
  exception in `FileConversionException`. The stored attempt chain is now
  inspected, so users see the actionable message again.

## [0.4.0] — 2026-11-16

A maintenance and usability release: fixes the known bugs from the 0.3.1 review, updates
dependencies and packaging, and adds CI and documentation.

### Added

- Live model catalog: recommendations are checked against the public Pollinations catalog and
  tagged as `vision` / `paid`; offline use falls back to the built-in list.
- `--list-models` to inspect recommendations without converting.
- `--yes` and `--non-interactive` flags for scripted use, with stable exit codes documented
  in the README.
- `-q/--quiet` to hide the banner and spinner.
- Keyless conversion for text-based formats (`.txt`, `.md`, `.csv`, `.json`, `.html`, ...);
  an API key is only required for images.
- `FORCE_COLOR` support and automatic no-color/no-spinner behavior when stdout is not a TTY.
- `python -m markitdown_pollinations` entry point (`__main__.py`).
- Localized LLM prompts (image description vs. OCR extraction) that follow the interface
  language.
- Retries now also cover HTTP 5xx and 429, honoring `Retry-After`.
- Specific messages for HTTP 402 (insufficient pollen) and 403 (model permission).
- GitHub Actions CI (lint + tests on Ubuntu/Windows/macOS), pre-commit hooks, Dependabot and
  issue/PR templates.
- `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md` and a Spanish README (`README.es.md`).

### Changed

- Language precedence is now: `--language` → saved preference → system locale. In 0.3.1 the
  saved preference was ignored at startup.
- Configuration is validated on load (types, language values, non-empty models) and written
  atomically with owner-only permissions on POSIX.
- Dependency set narrowed to the MarkItDown extras actually used, updated to
  `markitdown>=0.1.9,<0.2.0` and `markitdown-ocr>=0.1.2,<0.2.0`; redundant direct `numpy`
  dependency removed.
- The OpenAI client is created with `max_retries=0` so the application owns the retry loop
  (no nested attempts).
- `--configure` no longer dead-ends when the API key cannot be verified offline; it warns and
  continues.
- Version is single-sourced from `markitdown_pollinations.__version__`; packaging metadata
  (license, authors, URLs, classifiers) is complete.
- The `markitdown-for-everyone` console script is documented; the entry point remains.
- Exit codes: `0` success/cancel, `1` error, `2` usage/non-interactive, `3` no output,
  `130` interrupted.

### Fixed

- `POLLINATIONS_API_KEY` was written to `config.json` when configuring; it is now never
  persisted (the previously stored key is preserved instead).
- Saved language preference was ignored at startup.
- Closed stdin caused an unhandled `EOFError` traceback in quick-convert and menu flows.
- The Spanish cancel hint (`c/s`) did not accept `s`; cancel tokens now include
  `s`, `salir`, `volver` and `q`.
- README clone URL pointed to a non-existent repository name.
- `--output` could point to the input file, silently overwriting the source.
- Vision fallback re-ran the conversion with the same model when text and vision models were
  equal; it is now skipped.
- Whitespace-only conversion results were treated as non-empty; they now produce no file.
- Markdown output used CRLF on Windows; output is now always written with `\n`.
- `locale.getdefaultlocale()` deprecation (removal in Python 3.15) replaced with
  `locale.getlocale()` plus environment/Windows-name handling.
- Removed three unused translation keys and moved hardcoded English warnings into i18n.
- `python -m markitdown_pollinations` failed with "No module named ... `__main__`".
- `LICENSE` now includes the copyright holder.

### Removed

- Dead `ConversionResult.cancelled` field and the unreachable exit-130 branch it fed.
- Redundant direct `numpy` dependency and the overly broad `markitdown[all]` extra set.

## [0.3.1] — 2026-06-19

Last 0.3.x snapshot before the 0.4.0 maintenance release. It added the `--language` flag,
`--verbose`/`--debug` logging, bilingual UI, scanned-PDF OCR via `markitdown-ocr`, atomic
config handling, retries, and a `ruff`/`mypy`/`pytest`-clean codebase.
