"""Constants for MarkItDown Pollinations GUI."""

# Pollinations API base URL
POLLINATIONS_BASE_URL = "https://gen.pollinations.ai/v1"

# Models with vision capability (can process images)
VISION_MODELS = {
    "openai", "openai-large", "qwen-vision", "qwen-vision-pro",
    "gemini", "gemini-large", "claude", "claude-large"
}

# Supported image extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}

# File types for tkinter filedialog
SUPPORTED_FILETYPES = [
    ("All supported", "*.pdf *.docx *.pptx *.xlsx *.xls *.jpg *.jpeg *.png *.gif *.bmp *.webp *.tiff *.wav *.mp3 *.html *.csv *.json *.xml *.epub *.zip"),
    ("PDF", "*.pdf"),
    ("Word", "*.docx"),
    ("PowerPoint", "*.pptx"),
    ("Excel", "*.xlsx *.xls"),
    ("Images", "*.jpg *.jpeg *.png *.gif *.bmp *.webp *.tiff"),
    ("Audio", "*.wav *.mp3"),
    ("Archives", "*.zip"),
    ("All files", "*.*"),
]