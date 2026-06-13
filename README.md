# MarkItDown + Pollinations GUI

A simple desktop app that converts PDFs, images, documents, and other files into Markdown using the Pollinations API.

## What it does

- Converts PDF, Word, PowerPoint, Excel, images, audio, HTML, CSV, JSON, XML, EPUB, and ZIP files to Markdown.
- Describes images automatically when you use a vision-capable model.
- Validates your model in the background so the UI never freezes.
- Lets you cancel a conversion if you change your mind.
- Saves your API key and preferred model locally so you do not have to enter them every time.

## Requirements

- Python 3.10+
- A free Pollinations API key from [enter.pollinations.ai](https://enter.pollinations.ai)

## Quick start

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

python pollinations_gui.py
```

## First run

1. Launch the app. A settings dialog opens automatically.
2. Paste your Pollinations API key.
3. Pick a model (default is `openai`).
4. Click **Validate & Save**.
5. Your settings are saved to `config.json` and the dialog will not bother you again.

## Converting a file

1. Click **Browse...** next to **File to convert** and pick a file.
2. The app suggests an output name, or click **Browse...** next to **Save as** to choose your own.
3. Click **Convert**.
4. Watch the progress bar and log. Click **Cancel** anytime to stop.

## Running tests

```bash
python -m pytest
```

## Project structure

```
pollinations_gui.py              # Entry point
pyproject.toml                   # Project metadata
requirements.txt                 # Dependencies
src/markitdown_pollinations/     # App code
├── config.py                    # Settings load/save
├── constants.py                 # Supported formats, vision models
├── converter.py                 # File conversion logic
├── gui.py                       # Tkinter interface
└── pollinations_client.py       # Pollinations API client
tests/                           # pytest unit tests
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

## Security note

Your API key is stored in plain text in `config.json` in the project root. That file is already listed in `.gitignore`, so it will not be committed by accident. Keep it private, and run `chmod 600 config.json` on Linux or macOS if you want to restrict access.

## License

MIT License. See [LICENSE](LICENSE) for details.

## Credits

- [MarkItDown](https://github.com/microsoft/markitdown) by Microsoft
- [Pollinations AI](https://pollinations.ai)
