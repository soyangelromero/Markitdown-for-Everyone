# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| 0.4.x | ✅ |
| 0.3.x and older | ❌ |

## Reporting a vulnerability

Please **do not** open a public issue for security problems. Use GitHub's private security
advisory flow:

<https://github.com/soyangelromero/Markitdown-for-Everyone/security/advisories/new>

Include the affected version, a reproduction, and the impact you expect. You will receive a
response as soon as possible, and a coordinated disclosure date will be agreed upon.

## Scope and known design decisions

- **Local secrets.** The API key is stored in plain text in `config.json` under the user
  config directory. On Linux/macOS the file is written atomically with `0600` permissions.
  On Windows the file relies on the ACLs of the user profile. Keyring integration is on the
  roadmap.
- **Environment override.** A key provided through `POLLINATIONS_API_KEY` is never written to
  disk; saving settings preserves any previously stored key.
- **`--api-key` exposure.** Passing the key as a flag exposes it to the process list and shell
  history. Use the environment variable or the interactive configuration instead.
- **Network behavior.** The key is sent only as `Authorization: Bearer ...` to
  `gen.pollinations.ai`; it is never placed in a URL. File contents (images, document pages)
  are sent to the selected model provider when OCR or image description is used. Do not
  convert confidential documents through third-party models you do not trust.
- **No telemetry.** The application does not collect analytics or send data anywhere besides
  the Pollinations endpoints needed for conversion and key validation.
- **Output files.** Markdown is written to the path you choose; the tool refuses to write over
  the input file.

## Dependency security

Dependabot is enabled for pip and GitHub Actions. Run `pip install -e ".[dev]"` to get the
pinned tool versions declared in `pyproject.toml`.
