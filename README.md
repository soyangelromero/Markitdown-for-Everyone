# Markitdown-for-everyone

A simple command-line tool that converts PDFs, images, documents, and other files into Markdown using the Pollinations API.

`Python 3.10+ · v0.3.1 · MIT License`

## Features

- Converts PDF, Word, PowerPoint, Excel, images, audio, HTML, CSV, JSON, XML, EPUB, and ZIP to Markdown.
- Describes images automatically with vision-capable models.
- **Scanned PDFs** are auto-OCR'd page by page using your vision model.
- Bilingual interface: **English / Spanish**, with automatic system-language detection.
- Saves your API key and preferred models locally — enter them once.

## Quick start

```bash
git clone https://github.com/soyangelromero/markitdown_pollinations.git
cd markitdown_pollinations
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -e .
```

Get a free API key at [enter.pollinations.ai](https://enter.pollinations.ai), then run:

```bash
python markitdown_for_everyone.py
```

On the first run you'll be asked for your API key (hidden while typing), a text model, and a vision model. Your choices are saved to `config.json` in your user config directory (`platformdirs`); you won't need to enter them again. Type `c`, `cancel`, `b`, or `back` at any prompt to go back.

## Usage

Open the interactive menu:

```bash
python markitdown_for_everyone.py
```

Convert a file directly:

```bash
python markitdown_for_everyone.py report.pdf -o report.md -m openai
```

### Options

| Flag | Description |
|---|---|
| `FILE` | File to convert (if omitted, the interactive menu opens) |
| `-o, --output FILE` | Output Markdown file (default: `input.md`) |
| `-k, --api-key KEY` | Pollinations API key |
| `-m, --model MODEL` | Model to use (default: from config or `openai`) |
| `-l, --language {en,es}` | Interface language (default: auto-detected from system) |
| `-v, --verbose` | Info-level logging to stderr |
| `-d, --debug` | Debug-level logging to stderr |
| `--configure` | Open the configuration menu |
| `--version` | Show version and exit |
| `-h, --help` | Show help message |

### Environment variables

| Variable | Purpose |
|---|---|
| `POLLINATIONS_API_KEY` | Use this key instead of the one in `config.json` — useful for CI or shared machines. |
| `NO_CLEAR` | Disable terminal screen clearing. |
| `NO_COLOR` | Disable ANSI colors in the output. |

## Models

Recommended defaults: `openai` for text, `openai` for images. Vision alternatives include `openai-large`, `qwen-vision`, `qwen-vision-pro`, `gemini`, and `claude`. Run `--configure` to change your saved models at any time.

## Security

Your API key is stored in plain text in `config.json` (outside the project directory, so never committed by git). On Linux and macOS the file is set to `600` permissions. Use the `POLLINATIONS_API_KEY` environment variable to avoid storing the key on disk. Note that passing the key via `-k`/`--api-key` exposes it in the process list and shell history — prefer the environment variable on shared systems. Keyring integration (Credential Manager / Keychain / Secret Service) is planned for a future release.

## License

MIT License. See [LICENSE](LICENSE).

## Credits

- [MarkItDown](https://github.com/microsoft/markitdown) by Microsoft
- [Pollinations AI](https://pollinations.ai)
