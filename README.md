# Markitdown-for-everyone

A simple command-line tool that converts PDFs, images, documents, and other files into Markdown using the Pollinations API.

## What it does

- Converts PDF, Word, PowerPoint, Excel, images, audio, HTML, CSV, JSON, XML, EPUB, and ZIP files to Markdown.
- Describes images automatically when you use a vision-capable model.
- **Scanned PDFs** (no selectable text) are automatically OCR'd page by page using your vision model.
- Saves your API key and preferred models locally so you do not have to enter them every time.
- Easy interactive menu: just run the program and pick an option.

## Requirements

- Python 3.10+
- A free Pollinations API key from [enter.pollinations.ai](https://enter.pollinations.ai)

## Installation

```bash
git clone https://github.com/soyangelromero/markitdown_pollinations.git
cd markitdown_pollinations
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -e .
# Dependencies only (you must also run pip install -e . or set PYTHONPATH=src for the entry script to find the package):
# pip install -r requirements.txt
```

## First run

Just run the program:

```bash
python markitdown_for_everyone.py
```

On the first run it will ask you for:

1. Your Pollinations API key (characters are hidden while typing).
2. A model for text documents (recommended: `openai`).
3. A model for images (recommended: `openai`).

Type `c`, `cancel`, `b`, or `back` at any prompt to go back without saving changes.

Your choices are saved to a `config.json` file in your user config directory (`platformdirs`), and you will not need to enter them again.

**Config file location:**
- Windows: `%LOCALAPPDATA%\AngelRomero\markitdown-for-everyone\config.json`
- macOS: `~/Library/Application Support/markitdown-for-everyone/config.json`
- Linux: `~/.config/markitdown-for-everyone/config.json`

If you prefer not to save your API key to disk, set the `POLLINATIONS_API_KEY` environment variable before running the program. The program uses that value instead of the key in `config.json`.

```bash
# Windows PowerShell
$env:POLLINATIONS_API_KEY = "sk_..."

# Windows CMD
set POLLINATIONS_API_KEY=sk_...

# macOS/Linux
export POLLINATIONS_API_KEY=sk_...

python markitdown_for_everyone.py
```

## Using the menu

After the first run, running the program shows a simple menu:

```
--- Menu ---
1. Convert PDF to Markdown
2. Convert Image to Markdown
3. Convert Document to Markdown
4. Configure API key and models
5. Exit
```

Pick a number, enter the file path, and the program does the rest. If the output file already exists, the program asks before overwriting.

## Quick conversion (advanced)

If you already know the file you want, you can convert it directly:

```bash
python markitdown_for_everyone.py input.pdf
```

Specify output and model only when you need to:

```bash
python markitdown_for_everyone.py input.pdf -o output.md -m openai
```

## Options

```
FILE                   File to convert (if omitted, the menu opens)
-o, --output FILE      Output Markdown file (default: input.md)
-k, --api-key KEY      Pollinations API key
-m, --model MODEL      Model to use (default: from config)
    --configure        Open the configuration menu
    --version          Show version and exit
-h, --help             Show help message
```

## Environment variables

| Variable | Purpose |
|---|---|
| `POLLINATIONS_API_KEY` | Use this API key instead of the one saved in `config.json`. Useful for CI or shared machines. |
| `NO_CLEAR` | Set to any value to stop the program from clearing the terminal screen. |
| `NO_COLOR` | Set to any value to disable ANSI colors in the output. |

```bash
# Use an API key without saving it to disk
export POLLINATIONS_API_KEY=sk_...

# Keep output inline (no screen clearing)
export NO_CLEAR=1

# Disable colors
export NO_COLOR=1
```

## Examples

```bash
# Open the interactive menu
python markitdown_for_everyone.py

# Convert a PDF directly
python markitdown_for_everyone.py report.pdf

# Convert an image
python markitdown_for_everyone.py photo.png -o photo.md

# Override the saved API key for one run
python markitdown_for_everyone.py notes.docx -k ANOTHER_KEY -o notes.md

# Change settings
python markitdown_for_everyone.py --configure
```

## Models

For images, the program suggests these vision models:

- `openai` (recommended)
- `openai-large`
- `qwen-vision`, `qwen-vision-pro`
- `gemini`, `gemini-large`
- `claude`, `claude-large`

For text-only files, recommended models are:

- `openai`
- `glm`
- `openai-fast`
- `mistral`
- `deepseek`

## Troubleshooting

| Error | What to do |
|---|---|
| Invalid API key | Double-check your key at [enter.pollinations.ai](https://enter.pollinations.ai) |
| Model not found | Check the spelling or try `openai`, `glm`, `gemini`, or `claude` |
| Model does not support images | Switch to a vision model from the list above |
| Connection error | Make sure you are online |
| Empty output from a PDF | The PDF may be scanned (no selectable text). The program automatically retries with your vision model to OCR each page. If it still fails, try a different vision model in the configuration menu. |
| Slow conversion | Large files and busy API servers take longer |
| Ctrl+C | Pressing Ctrl+C cancels the current operation cleanly |
| Cancelling a prompt | Type `c`, `cancel`, `b`, or `back` and press Enter to go back |

## Running tests

```bash
python -m pytest
```

## Project structure

```
markitdown_for_everyone.py       # Entry point
pyproject.toml                   # Project metadata
requirements.txt                 # Dependencies
src/markitdown_pollinations/     # App code
├── __init__.py                  # Package metadata
├── cli.py                       # Command-line interface with menu
├── config.py                    # Settings load/save
├── constants.py                 # API URL, vision models, and recommendations
├── converter.py                 # File conversion logic
├── i18n.py                      # Internationalization (EN/ES)
├── pollinations_client.py       # Pollinations API client
└── validation.py                # API key validation
tests/                           # pytest unit tests
```

## Security note

Your API key is stored in plain text in `config.json` in your user config directory (see above). Because the file lives outside the project directory, it is never committed by git. On Linux and macOS the program tries to set the file permissions to `600` (owner-only read/write) when it saves the configuration.

To avoid storing the key on disk at all, use the `POLLINATIONS_API_KEY` environment variable. When this variable is set, the program uses it instead of any key saved in `config.json`.

**Note:** Passing your API key via the `-k` / `--api-key` flag exposes it in the process list and shell history. Use the environment variable instead on shared or multi-user systems.

Keep your config file private, and run `chmod 600` on it (Linux or macOS) if you want to restrict access.

Storing the API key in the system keyring (Credential Manager / Keychain / Secret Service) is planned for a future release.

## License

MIT License. See [LICENSE](LICENSE) for details.

## Credits

- [MarkItDown](https://github.com/microsoft/markitdown) by Microsoft
- [Pollinations AI](https://pollinations.ai)
