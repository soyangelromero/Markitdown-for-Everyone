# Publishing to PyPI

The package is **not published on PyPI yet**. This document describes the steps to release it
so `pipx install markitdown-for-everyone` works without cloning the repository.

## Option A — Trusted Publishing (recommended, no token)

1. Create the project on PyPI if it does not exist yet (the first publish creates it, but the
   trusted publisher must be configured for a *pending* project):
   <https://pypi.org/manage/account/publishing/>
2. Add a trusted publisher with:
   - **PyPI project name:** `markitdown-for-everyone`
   - **Owner:** `soyangelromero`
   - **Repository:** `Markitdown-for-Everyone`
   - **Workflow name:** `publish.yml`
   - **Environment name:** `pypi`
3. Run the **Publish to PyPI** workflow manually from the Actions tab, or uncomment the
   `release` trigger in `.github/workflows/publish.yml` and publish a GitHub release.
4. The workflow builds the sdist/wheel and uploads them using OIDC; no secrets are stored.

## Option B — API token (manual)

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine upload dist/*
# user: __token__
# password: pypi-AgEI...
```

## After the first publish

- Update `README.md` / `README.es.md`: remove the "PyPI publication is pending" notes and
  replace the Git install one-liners with `pipx install markitdown-for-everyone` and
  `uvx markitdown-for-everyone`.
- Add the PyPI badge to both READMEs.
- Verify the release with `pipx install markitdown-for-everyone` in a clean environment.
- Create the next GitHub release and attach `dist/*.whl` and `dist/*.tar.gz` as assets
  (`gh release upload vX.Y.Z dist/*`).

## Versioning checklist

1. Bump `__version__` in `src/markitdown_pollinations/__init__.py` (single source of truth).
2. Move the `[Unreleased]` entries in `CHANGELOG.md` to the new version and date.
3. Run the local quality gate: `ruff check . && ruff format --check . && mypy src && pytest -q --cov`.
4. Commit, tag `vX.Y.Z`, push the tag (`git push origin vX.Y.Z`).
5. Create the GitHub release with notes and upload the wheel/sdist:
   `gh release create vX.Y.Z dist/* --title "vX.Y.Z" --notes-file CHANGELOG.md`.
