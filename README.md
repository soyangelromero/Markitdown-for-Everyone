# Markitdown-for-everyone

A simple command-line tool by **Angel Romero** ([github.com/soyangelromero](https://github.com/soyangelromero)) that converts PDFs, images, documents, and other files into Markdown using the Pollinations API.

## What it does

- Converts PDF, Word, PowerPoint, Excel, images, audio, HTML, CSV, JSON, XML, EPUB, and ZIP files to Markdown.
- Describes images automatically when you use a vision-capable model.
- Saves your API key and preferred model locally so you do not have to enter them every time.

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

pip install -r requirements.txt
# or: pip install -e .
```

## First run

Configure your API key and default model once:

```bash
python markitdown_for_everyone.py --configure -k YOUR_API_KEY -m openai
```

Your settings are saved to `config.json` and you will not need to pass them again.

## Usage

Convert a file:

```bash
python markitdown_for_everyone.py input.pdf
```

Specify output and model:

```bash
python markitdown_for_everyone.py input.pdf -o output.md -m openai
```

## Options

```
-i, --input FILE       File to convert (required)
-o, --output FILE      Output Markdown file (default: input.md)
-k, --api-key KEY      Pollinations API key
-m, --model MODEL      Model to use (default: openai)
    --configure        Save API key and model to config.json
-h, --help             Show help message
```

## Examples

```bash
# Convert a PDF
python markitdown_for_everyone.py report.pdf

# Convert an image with a vision model
python markitdown_for_everyone.py photo.png -m openai -o photo.md

# Override the saved API key for one run
python markitdown_for_everyone.py notes.docx -k ANOTHER_KEY -o notes.md
```

## Models

For images, use one of these vision models:

- `openai` (recommended)
- `openai-large`
- `qwen-vision`, `qwen-vision-pro`
- `gemini`, `gemini-large`
- `claude`, `claude-large`

For text-only files, any Pollinations model works, such as `glm`, `openai-fast`, `mistral`, or `deepseek`.

## Troubleshooting

| Error | What to do |
|---|---|
| Invalid API key | Double-check your key at [enter.pollinations.ai](https://enter.pollinations.ai) |
| Model not found | Check the spelling or try `openai`, `glm`, `gemini`, or `claude` |
| Model does not support images | Switch to a vision model from the list above |
| Connection error | Make sure you are online |
| Slow conversion | Large files and busy API servers take longer |

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
├── cli.py                       # Command-line interface
├── config.py                    # Settings load/save
├── constants.py                 # API URL and vision models
├── converter.py                 # File conversion logic
└── pollinations_client.py       # Pollinations API client
tests/                           # pytest unit tests
```

## Security note

Your API key is stored in plain text in `config.json` in the project root. That file is already listed in `.gitignore`, so it will not be committed by accident. Keep it private, and run `chmod 600 config.json` on Linux or macOS if you want to restrict access.

## License

MIT License. See [LICENSE](LICENSE) for details.

## Credits

- [MarkItDown](https://github.com/microsoft/markitdown) by Microsoft
- [Pollinations AI](https://pollinations.ai)
