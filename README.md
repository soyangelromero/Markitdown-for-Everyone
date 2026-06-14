# Markitdown-for-everyone

A simple command-line tool by **Angel Romero** ([github.com/soyangelromero](https://github.com/soyangelromero)) that converts PDFs, images, documents, and other files into Markdown using the Pollinations API.

## What it does

- Converts PDF, Word, PowerPoint, Excel, images, audio, HTML, CSV, JSON, XML, EPUB, and ZIP files to Markdown.
- Describes images automatically when you use a vision-capable model.
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

pip install -r requirements.txt
# or: pip install -e .
```

## First run

Just run the program:

```bash
python markitdown_for_everyone.py
```

On the first run it will ask you for:

1. Your Pollinations API key.
2. A model for text documents (recommended: `openai`).
3. A model for images (recommended: `openai`).

Your choices are saved to `config.json` and you will not need to enter them again.

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

Pick a number, enter the file path, and the program does the rest.

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
-h, --help             Show help message
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
├── cli.py                       # Command-line interface with menu
├── config.py                    # Settings load/save
├── constants.py                 # API URL, vision models, and recommendations
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
