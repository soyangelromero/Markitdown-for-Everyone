# Publishing to PyPI

**Status:** published ✅ — `markitdown-for-everyone==0.4.1` is live at
<https://pypi.org/project/markitdown-for-everyone/>.

Publishing uses **PyPI Trusted Publishing (OIDC)**: no API token is stored in the repository or
in GitHub secrets. The pending publisher was registered on PyPI with:

| Field | Value |
|---|---|
| PyPI project name | `markitdown-for-everyone` |
| Owner | `soyangelromero` |
| Repository | `Markitdown-for-Everyone` |
| Workflow | `publish.yml` |
| Environment | `pypi` |

The GitHub environment `pypi` exists in the repository settings. It is intentionally not
protected with required reviewers, so the workflow runs unattended.

## Publishing a new version

1. Bump `__version__` in `src/markitdown_pollinations/__init__.py` (single source of truth).
2. Move the `[Unreleased]` entries in `CHANGELOG.md` to the new version and date.
3. Run the local quality gate:
   `ruff check . && ruff format --check . && mypy src && pytest -q --cov`.
4. Commit, tag `vX.Y.Z`, push the tag (`git push origin vX.Y.Z`).
5. Create the GitHub release: it triggers the **Publish to PyPI** workflow automatically
   (`.github/workflows/publish.yml` has the `release: published` trigger enabled).
   You can also run it manually from **Actions → Publish to PyPI → Run workflow**.
6. Attach the build artifacts to the release for convenience:
   `python -m build && gh release upload vX.Y.Z dist/* --clobber`.
7. Verify:

   ```bash
   uvx markitdown-for-everyone --version
   # or
   pipx install markitdown-for-everyone
   ```

> PyPI does not allow re-uploading the same version. If a release fails after upload, bump the
> patch version instead of trying to overwrite it.

## Manual fallback (API token)

Only if Trusted Publishing is unavailable:

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine upload dist/*
# user: __token__
# password: pypi-AgEI...
```

## Checklist for the README after a release

- [ ] PyPI badge shows the new version (it is dynamic).
- [ ] Install one-liners use `uvx markitdown-for-everyone` / `pipx install markitdown-for-everyone`.
- [ ] GitHub release has the matching tag, notes and assets.
- [ ] `docs/releases/vX.Y.Z.md` notes are consistent with `CHANGELOG.md`.
