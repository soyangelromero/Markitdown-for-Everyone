"""Constants for MarkItDown Pollinations."""

# Pollinations API base URL
POLLINATIONS_BASE_URL = "https://gen.pollinations.ai/v1"

# Models with vision capability (can process images)
VISION_MODELS = {
    "openai", "openai-large", "qwen-vision", "qwen-vision-pro",
    "gemini", "gemini-large", "claude", "claude-large"
}

# Supported image extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}

# Recommended models for text-only conversions
RECOMMENDED_TEXT_MODELS = ["openai", "glm", "openai-fast", "mistral", "deepseek"]

# Recommended models for image/vision conversions
RECOMMENDED_VISION_MODELS = [
    "openai",
    "openai-large",
    "qwen-vision",
    "qwen-vision-pro",
    "gemini",
    "gemini-large",
    "claude",
    "claude-large",
]

# Validation endpoints and parameters for API-key checks
POLLINATIONS_BALANCE_URL = "https://gen.pollinations.ai/account/balance"
POLLINATIONS_CHAT_URL = "https://gen.pollinations.ai/v1/chat/completions"
VALIDATION_PROMPT = "hello"
VALIDATION_MODEL = "openai"
VALIDATION_MAX_TOKENS = 2
VALIDATION_TIMEOUT_SECONDS = 10.0
VALIDATION_USER_AGENT = "Markitdown-for-everyone/0.3.0"
