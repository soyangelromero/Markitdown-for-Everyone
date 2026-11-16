"""Generate the README demo GIF and preview image.

The animation is built from output captured from real CLI runs (0.4.1):
version, a scanned-PDF OCR conversion and the live model list. It is only a
reproducible marketing asset, not a test.

Run from the repository root:

    python scripts/generate_demo.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

WIDTH, HEIGHT = 1000, 560
BACKGROUND = (13, 17, 23)
TITLE_BAR = (22, 27, 34)
FOREGROUND = (230, 237, 243)
GREEN = (63, 185, 80)
CYAN = (88, 166, 255)
YELLOW = (210, 153, 34)
MAGENTA = (188, 140, 255)
MUTED = (139, 148, 158)
BORDER = (48, 54, 61)

FONT_SIZE = 20
LINE_HEIGHT = 30
PADDING = 24


def _font(size: int = FONT_SIZE) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "consola.ttf",
        "CascadiaMono.ttf",
        "DejaVuSansMono.ttf",
        "LiberationMono-Regular.ttf",
    ]
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def _terminal_frame(lines: list[tuple[str, tuple[int, int, int]]]) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((0, 0, WIDTH - 1, 46), radius=10, fill=TITLE_BAR)
    for index, color in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
        draw.ellipse((20 + index * 26, 15, 36 + index * 26, 31), fill=color)
    title = "markitdown-for-everyone — demo"
    font = _font(17)
    draw.text(((WIDTH - draw.textlength(title, font=font)) / 2, 12), title, fill=MUTED, font=font)

    y = 70
    for text, color in lines:
        draw.text((PADDING, y), text, fill=color, font=_font())
        y += LINE_HEIGHT
    return image


def _prompt(command: str) -> tuple[str, tuple[int, int, int]]:
    return f"$ {command}", FOREGROUND


def build_frames() -> list[tuple[Image.Image, int]]:
    version_lines = [
        _prompt("markitdown-for-everyone --version"),
        ("Markitdown-for-everyone 0.4.1", MUTED),
    ]
    scan_lines = [
        _prompt("markitdown-for-everyone scanned.pdf --yes"),
        ("- Converting... scanned.pdf -> scanned.md", CYAN),
        ("  OCR: page 1/1  ·  model: openai", MUTED),
    ]
    done_lines = [
        _prompt("markitdown-for-everyone scanned.pdf --yes"),
        ("\u2714 Done: scanned.md", GREEN),
        ("", FOREGROUND),
        ("  *[Image OCR]", YELLOW),
        ("  Clean clone 0.4.1", FOREGROUND),
        ("  [End OCR]*", YELLOW),
    ]
    models_lines = [
        _prompt("markitdown-for-everyone --list-models"),
        ("Model for text documents:", CYAN),
        ("  - openai (vision)", FOREGROUND),
        ("  - openai-fast (vision)", FOREGROUND),
        ("  - deepseek", FOREGROUND),
        ("  - mistral (vision, paid)", MUTED),
        ("  - glm (paid)", MUTED),
    ]
    finish_lines = [
        _prompt("markitdown-for-everyone report.pdf -o report.md"),
        ("\u2714 Done: report.md", GREEN),
        ("", FOREGROUND),
        ("Free Pollinations API  \u00b7  OCR for scanned PDFs", MAGENTA),
        ("English / Espa\u00f1ol  \u00b7  No GPU  \u00b7  MIT", MAGENTA),
    ]

    frames: list[tuple[Image.Image, int]] = [
        (_terminal_frame(version_lines), 1100),
        (_terminal_frame([*scan_lines[:2], ("  /", CYAN)]), 500),
        (_terminal_frame([*scan_lines[:2], ("  -", CYAN)]), 500),
        (_terminal_frame([*scan_lines[:2], ("  \\", CYAN)]), 500),
        (_terminal_frame(done_lines), 2600),
        (_terminal_frame(models_lines), 2300),
        (_terminal_frame(finish_lines), 2600),
    ]
    return frames


def main() -> None:
    DOCS.mkdir(exist_ok=True)
    frames = build_frames()
    images = [frame for frame, _ in frames]
    durations = [duration for _, duration in frames]

    gif_path = DOCS / "demo.gif"
    images[0].save(
        gif_path,
        save_all=True,
        append_images=images[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )
    images[-1].save(DOCS / "demo.png")
    size_kb = gif_path.stat().st_size / 1024
    print(f"wrote {gif_path.relative_to(ROOT)} ({size_kb:.1f} KiB)")
    print(f"wrote {(DOCS / 'demo.png').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
