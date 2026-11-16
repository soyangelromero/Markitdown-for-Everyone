# Contributing

Thanks for your interest in improving Markitdown-for-Everyone.

## Development setup

Requires Python 3.10+.

```bash
git clone https://github.com/soyangelromero/Markitdown-for-Everyone.git
cd Markitdown-for-Everyone
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install               # optional but recommended
```

## Before opening a pull request

Run the same checks as CI:

```bash
ruff check .
ruff format --check .
mypy src
pytest -q --cov
```

All four must pass and coverage must stay at or above 85 % (`fail_under` is configured in
`pyproject.toml`).

## Guidelines

- Keep changes focused; one logical change per pull request.
- Add or update tests for every behavior change. Bug fixes should include a regression test.
- User-facing strings must be added to **both** `en` and `es` dictionaries in
  `src/markitdown_pollinations/i18n.py`. `tests/test_i18n.py` enforces key parity and catches
  dead or missing keys.
- Never commit API keys, tokens, personal paths, generated `config.json` files or conversion
  outputs.
- Update `CHANGELOG.md` under `[Unreleased]` for user-visible changes.
- Keep documentation in sync: `README.md` and `README.es.md`.
- Follow the existing style: type hints, `from __future__ import annotations`, no unnecessary
  dependencies.

## Commit messages

Conventional Commits are appreciated, for example:

```text
fix(cli): honor saved language at startup
feat(models): tag paid models in the selector
docs: document the non-interactive flags
```

## Reporting bugs

Use the GitHub issue template and include:

- Operating system and Python version.
- The command you ran.
- The output with `--verbose` or `--debug` (remove API keys).
- Whether the problem happens without an API key for local-only formats.

For security issues, follow [SECURITY.md](SECURITY.md) instead of opening a public issue.

## License

By contributing you agree that your contributions are licensed under the MIT License.
