"""Allow running the CLI with ``python -m markitdown_pollinations``."""

from __future__ import annotations

from markitdown_pollinations.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
