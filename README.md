# MarkItDown + Pollinations GUI

A graphical desktop application for converting files (PDF, images, documents) to Markdown using the Pollinations API as an AI backend.

## Features

- **Intuitive GUI** built with tkinter
- **Converts multiple formats**: PDF, Word, PowerPoint, Excel, images, audio, HTML, CSV, JSON, XML, EPUB, ZIP
- **Automatic image descriptions** using AI models with vision capability
- **Persistent configuration**: remembers your API key and preferred model
- **Model validation**: checks that the model exists before using it
- **Smart warnings**: alerts you when trying to convert images with a non-vision model
- **Robust error handling**: clear, descriptive error messages

## Requirements

- Python 3.10 or higher
- A Pollinations API key (free at [enter.pollinations.ai](https://enter.pollinations.ai))

## Installation

### 1. Clone the repository

```bash
git clone <your-repository>
cd markitdown-pollinations
```

### 2. Create a virtual environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Run the application

```bash
python pollinations_gui.py
```

### First run

1. On first launch, a settings dialog will open
2. Enter your **API key** from Pollinations (get one free at [enter.pollinations.ai](https://enter.pollinations.ai))
3. Enter the **model** you want to use (default: `openai`)
4. Click **"Validate & Save"**
5. The configuration is saved to `config.json` and won't be asked again

### Convert files

1. Click **"Browse…"** next to "File to convert"
2. Select the file you want to convert
3. Click **"Browse…"** next to "Save as" (or use the auto-suggested filename)
4. Click **"Convert"**
5. Wait for the conversion to finish (progress is shown in the bar and log)

## Available Models

### Vision models (for images)

These models can describe image content:

- `openai` — GPT-4o (recommended)
- `openai-large` — Higher quality GPT-4o
- `qwen-vision` — Qwen with vision
- `qwen-vision-pro` — Enhanced Qwen vision
- `gemini` — Google Gemini
- `gemini-large` — Higher quality Gemini
- `claude` — Anthropic Claude
- `claude-large` — Higher quality Claude

### Text-only models

These models are great for text but **do not support images**:

- `glm` — GLM 5.1 (excellent for text)
- `openai-fast` — GPT-4o mini (fast)
- `mistral` — Mistral AI
- `deepseek` — DeepSeek
- And many more...

**Note:** If you try to convert an image with a non-vision model, the app will warn you and suggest compatible models.

## Project Structure

```
markitdown-pollinations/
├── pollinations_gui.py      # Main application
├── requirements.txt         # Dependencies
├── README.md               # This documentation
├── .gitignore              # Git ignore rules
├── config.json             # User settings (gitignored)
└── LICENSE                 # MIT License
```

## Troubleshooting

### Error: "Invalid API key"

- Verify your API key is correct
- Get a new key at [enter.pollinations.ai](https://enter.pollinations.ai)
- Keys start with `sk_` (server-side) or `pk_` (client-side)

### Error: "Model not found"

- Check that the model name is spelled correctly
- Check the list of available models in the Pollinations API
- Common models: `openai`, `glm`, `gemini`, `claude`

### Error: "Model does not support images"

- Use a vision model: `openai`, `openai-large`, `qwen-vision`, `gemini`, or `claude`
- The `glm` model is excellent for text but has no vision capability

### Error: "Connection error"

- Check your internet connection
- The Pollinations API requires connectivity for model validation and file conversion

### Conversion is slow

- Large files (multi-page PDFs, high-resolution images) may take longer
- Speed depends on your internet connection and Pollinations API load

## Security

### API Key Storage

Your Pollinations API key is stored in `config.json` in plaintext. This is standard practice for local development tools, but please note:

- **Never commit `config.json` to version control** (it's already in `.gitignore`)
- **Keep your API key private** — don't share it or expose it in public repositories
- **Use environment variables** for production deployments instead of config files
- **Rotate your API key** if you suspect it has been compromised

### File Permissions

On Linux/Mac, you can restrict access to your config file:

```bash
chmod 600 config.json
```

This ensures only your user account can read the file.

## Advanced Configuration

### Change model or API key

1. Click the **"⚙ Settings"** button in the main window
2. Modify the API key or model
3. Click **"Validate & Save"**

### Edit configuration manually

Settings are stored in `config.json`:

```json
{
  "api_key": "sk_your_api_key_here",
  "model": "openai"
}
```

**Note:** This file is automatically ignored by Git (see `.gitignore`).

## Contributing

Contributions are welcome. Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Credits

- **[MarkItDown](https://github.com/microsoft/markitdown)** — Microsoft's library for converting files to Markdown
- **[Pollinations AI](https://pollinations.ai)** — AI API with multiple models

## Contact

For issues or suggestions, please open an issue on the GitHub repository.
