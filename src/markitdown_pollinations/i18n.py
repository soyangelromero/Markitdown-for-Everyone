"""Internationalization support for MarkItDown for Everyone.

Translation data lives in a plain dictionary to keep the project dependency-free
and easy to review. Any missing key falls back to English, and an unknown key is
returned as-is so broken lookups are visible instead of crashing.
"""

from __future__ import annotations

LANGUAGES: tuple[str, ...] = ("en", "es")

_current_language: str = "en"


def set_language(lang: str) -> None:
    """Set the current language for all subsequent translation lookups."""
    global _current_language
    _current_language = lang if lang in LANGUAGES else "en"


def get_language() -> str:
    """Return the language currently in use."""
    return _current_language


def _(key: str) -> str:
    """Return the translated string for *key* in the current language.

    Falls back to English when the key is missing from the selected language
    or from the English dictionary itself.
    """
    return TRANSLATIONS.get(_current_language, {}).get(key, TRANSLATIONS["en"].get(key, key))


# ── Translation data ──────────────────────────────────────────────────────────

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        # CLI / argparse
        "cli_description": (
            "Convert PDFs, images, documents and other files to Markdown using "
            "the Pollinations API."
        ),
        "input_file_help": "File to convert (if omitted, the interactive menu opens)",
        "output_help": "Output Markdown file (default: input.md)",
        "api_key_help": "Pollinations API key (or set POLLINATIONS_API_KEY)",
        "model_help": "Model to use (default: from config or openai)",
        "language_flag_help": "Interface language (en/es)",
        "configure_help": "Open the configuration menu",
        "list_models_help": "Show the recommended models and exit",
        "yes_help": "Overwrite existing output without asking",
        "non_interactive_help": "Never prompt; fail if input is required",
        "quiet_help": "Suppress the banner and progress spinner",
        "verbose_help": "Show informational messages",
        "debug_help": "Show debug messages",
        # Language selector
        "language_title": "--- Language / Idioma ---",
        "language_prompt": "Select your language / Seleccione su idioma",
        "language_en": "English",
        "language_es": "Español",
        "invalid_option": "Invalid option. Please try again / Opción inválida. Intente de nuevo",
        # Config flow — wizard
        "welcome_title": "Welcome to Markitdown-for-everyone!",
        "setup_intro": "Let's set up the program so you can start converting files.",
        "model_for_text": "Model for text documents (PDF, Word, Excel, etc.)",
        "model_for_images": "Model for images (JPG, PNG, etc.)",
        # Config flow — menu
        "model_for_text_short": "Model for text documents",
        "model_for_images_short": "Model for images",
        "config_saved": "Configuration saved successfully.",
        "config_updated": "Configuration updated.",
        "config_cancelled": "Configuration cancelled.",
        "enter_model_name": "Enter the model name",
        "other_model": "Other (type manually)",
        "cancel_back": "c/b. Cancel/Back",
        # Config flow — common
        "validating_key": "Validating API key...",
        "provide_valid_key": "Please provide a valid API key to continue.",
        "key_validation_offline": (
            "Warning: could not verify the API key (network issue). Continuing anyway."
        ),
        "error_save_config": "Error: could not save the configuration.",
        "api_key_required_warn": "An API key is required.",
        "api_key_required_exit": "An API key is required to use the program.",
        "api_key_required_for_images": (
            "Error: an API key is required to convert images. Run --configure or set "
            "POLLINATIONS_API_KEY."
        ),
        "api_key_from_env": "from environment",
        "keyless_note": (
            "Note: no API key configured; OCR and vision features are unavailable, "
            "but text-based formats can still be converted."
        ),
        # Main menu
        "menu_title": "--- Menu ---",
        "menu_convert_pdf": "1. Convert PDF to Markdown",
        "menu_convert_image": "2. Convert Image to Markdown",
        "menu_convert_document": "3. Convert Document to Markdown",
        "menu_configure": "4. Configure language, API key and models",
        "menu_exit": "5. Exit",
        "goodbye": "Goodbye!",
        "invalid_menu_option": "Invalid option. Please try again.",
        "choose_option": "\nChoose an option: ",
        # Conversion screen
        "convert_title": "--- Convert {kind} to Markdown ---",
        "ask_file": "File path",
        "ask_output": "Output file",
        "overwrite_confirm": "'{path}' already exists. Overwrite? (y/N): ",
        "cancelled": "Cancelled.",
        "overwrite_cancelled": "Overwrite cancelled.",
        "converting": "Converting {input} -> {output} using model {model}...",
        "spinner_text": "Converting... ",
        "file_kind_pdf": "PDF",
        "file_kind_image": "Image",
        "file_kind_document": "Document",
        "not_vision_info": (
            "Note: '{model}' is not in the known vision models list. "
            "Image conversion may be limited."
        ),
        "conversion_cancelled": "Conversion cancelled.",
        "error_prefix": "Error: {message}",
        "done": "Done: {output}",
        "warning_prefix": "Warning: {warning}",
        "no_text_found": "No text found — retrying with vision model '{model}'...",
        "run_configure": "Run: markitdown-for-everyone --configure",
        "output_same_as_input": ("Error: the output path must be different from the input file."),
        "no_output_empty": "No content was produced; no file was written.",
        "non_interactive_stdin": "Error: interactive input is required but stdin is closed.",
        "non_interactive_input_required": (
            "Error: no input file was given and --non-interactive is enabled."
        ),
        "non_interactive_overwrite": (
            "Error: output file '{path}' already exists; pass --yes to overwrite it."
        ),
        # API key validation
        "key_valid_balance": "API key is valid. Balance: {balance} pollen",
        "key_valid": "API key is valid.",
        "key_invalid": "Invalid API key. Get your key at https://enter.pollinations.ai",
        "key_verified": "API key verified successfully.",
        "key_insufficient_balance": (
            "Warning: insufficient pollen balance. Your key is valid, but you will need to "
            "top up at https://enter.pollinations.ai before converting files."
        ),
        "key_connection_error": (
            "Warning: could not connect to the Pollinations API to validate the key. "
            "Check your internet connection."
        ),
        "key_format_warning": (
            "Warning: API keys usually start with 'sk_'. "
            "Get your key at https://enter.pollinations.ai"
        ),
        "key_short_warning": (
            "Warning: the API key seems too short. Get your key at https://enter.pollinations.ai"
        ),
        "validation_nonjson_response": ("non-JSON response from the chat completions endpoint"),
        "validation_no_choices": "no 'choices' field in the chat completions response",
        # Converter — retries and errors
        "retry_waiting": "Retrying in {delay}s (attempt {attempt}/{max_retries})...",
        "conn_error_fatal": "Connection error. Please check your internet connection.",
        "auth_error": "Invalid API key. Get your key at https://enter.pollinations.ai",
        "permission_error": (
            "Permission denied for model '{model}'. Check the permissions of your API key."
        ),
        "insufficient_balance_error": (
            "Insufficient pollen balance. Top up at https://enter.pollinations.ai"
        ),
        "model_not_found": "Model '{model}' not found.",
        "rate_limit": "Rate limit exceeded: {error}",
        "api_status_error": "API error ({code}): {detail}",
        "api_error": "API error: {detail}",
        "unknown_api_error": "Unknown API error",
        "unsupported_format": "Unsupported file format: {ext}",
        "conversion_failed": "Conversion failed: {error}",
        "missing_dep": "Missing dependency: {error}",
        "unexpected_error": "Unexpected error: {error}",
        "write_error": "Could not write output file: {error}",
        "conversion_empty_warning": "Conversion produced no content.",
        "llm_prompt_image": (
            "Describe this image in detail, including any text, objects, and context."
        ),
        "llm_prompt_ocr": (
            "Extract all text from this document image, preserving tables, lists and "
            "reading order. Return only the extracted text."
        ),
        # Model catalog labels
        "models_title": "Recommended models (live catalog when available):",
        "models_offline": "Live catalog unavailable; showing the built-in list.",
        "model_tag_vision": "vision",
        "model_tag_paid": "paid",
        "model_unknown_warning": (
            "Warning: model '{model}' was not found in the live catalog; trying anyway."
        ),
        "model_not_vision_warning": (
            "Warning: '{model}' does not accept image input; results may be poor."
        ),
        # Config module — warnings / errors
        "config_warn_not_dict": "Warning: config file is not a dict, using defaults",
        "config_warn_invalid_json": "Warning: config file contains invalid JSON: {error}",
        "config_warn_cannot_read": "Warning: could not read config file: {error}",
        "config_warn_invalid_values": (
            "Warning: invalid value for '{key}' in config; using the default"
        ),
        "config_error_save": "Error: could not save config file: {error}",
        # Prompts / labels
        "api_key_prompt": "Pollinations API key",
        "recommended": "Recommended:",
        "select": "Select: ",
        "file_not_found": "File not found: {path}",
        "by": "by",
        "press_enter_continue": "Press Enter to continue...",
    },
    "es": {
        # CLI / argparse
        "cli_description": (
            "Convierte PDFs, imágenes, documentos y otros archivos a Markdown "
            "usando la API de Pollinations."
        ),
        "input_file_help": "Archivo a convertir (si se omite, se abre el menú interactivo)",
        "output_help": "Archivo Markdown de salida (por defecto: entrada.md)",
        "api_key_help": "Clave API de Pollinations (o define POLLINATIONS_API_KEY)",
        "model_help": "Modelo a usar (por defecto: el de la configuración u openai)",
        "language_flag_help": "Idioma de la interfaz (en/es)",
        "configure_help": "Abrir el menú de configuración",
        "list_models_help": "Mostrar los modelos recomendados y salir",
        "yes_help": "Sobrescribir la salida existente sin preguntar",
        "non_interactive_help": "No preguntar nunca; fallar si se requiere entrada",
        "quiet_help": "Ocultar el banner y el indicador de progreso",
        "verbose_help": "Mostrar mensajes informativos",
        "debug_help": "Mostrar mensajes de depuración",
        # Language selector
        "language_title": "--- Idioma / Language ---",
        "language_prompt": "Seleccione su idioma / Select your language",
        "language_en": "Inglés",
        "language_es": "Español",
        "invalid_option": "Opción inválida. Intente de nuevo / Invalid option. Please try again",
        # Config flow — wizard
        "welcome_title": "¡Bienvenido a Markitdown-for-everyone!",
        "setup_intro": "Configuremos el programa para que puedas empezar a convertir archivos.",
        "model_for_text": "Modelo para documentos de texto (PDF, Word, Excel, etc.)",
        "model_for_images": "Modelo para imágenes (JPG, PNG, etc.)",
        # Config flow — menu
        "model_for_text_short": "Modelo para documentos de texto",
        "model_for_images_short": "Modelo para imágenes",
        "config_saved": "Configuración guardada exitosamente.",
        "config_updated": "Configuración actualizada.",
        "config_cancelled": "Configuración cancelada.",
        "enter_model_name": "Ingrese el nombre del modelo",
        "other_model": "Otro (escriba manualmente)",
        "cancel_back": "c/s. Cancelar/Volver",
        # Config flow — common
        "validating_key": "Validando clave API...",
        "provide_valid_key": "Por favor proporcione una clave API válida para continuar.",
        "key_validation_offline": (
            "Advertencia: no se pudo verificar la clave API (problema de red). "
            "Continuando de todos modos."
        ),
        "error_save_config": "Error: no se pudo guardar la configuración.",
        "api_key_required_warn": "Se requiere una clave API.",
        "api_key_required_exit": "Se requiere una clave API para usar el programa.",
        "api_key_required_for_images": (
            "Error: se requiere una clave API para convertir imágenes. "
            "Ejecute --configure o defina POLLINATIONS_API_KEY."
        ),
        "api_key_from_env": "desde el entorno",
        "keyless_note": (
            "Nota: no hay clave API configurada; las funciones de OCR y visión no están "
            "disponibles, pero los formatos de texto se pueden convertir igualmente."
        ),
        # Main menu
        "menu_title": "--- Menú ---",
        "menu_convert_pdf": "1. Convertir PDF a Markdown",
        "menu_convert_image": "2. Convertir Imagen a Markdown",
        "menu_convert_document": "3. Convertir Documento a Markdown",
        "menu_configure": "4. Configurar idioma, clave API y modelos",
        "menu_exit": "5. Salir",
        "goodbye": "¡Hasta luego!",
        "invalid_menu_option": "Opción inválida. Intente de nuevo.",
        "choose_option": "\nElija una opción: ",
        # Conversion screen
        "convert_title": "--- Convertir {kind} a Markdown ---",
        "ask_file": "Ruta del archivo",
        "ask_output": "Archivo de salida",
        "overwrite_confirm": "'{path}' ya existe. ¿Sobrescribir? (s/N): ",
        "cancelled": "Cancelado.",
        "overwrite_cancelled": "Sobrescritura cancelada.",
        "converting": "Convirtiendo {input} -> {output} usando modelo {model}...",
        "spinner_text": "Convirtiendo... ",
        "file_kind_pdf": "PDF",
        "file_kind_image": "Imagen",
        "file_kind_document": "Documento",
        "not_vision_info": (
            "Nota: '{model}' no está en la lista de modelos de visión conocidos. "
            "La conversión de imágenes puede ser limitada."
        ),
        "conversion_cancelled": "Conversión cancelada.",
        "error_prefix": "Error: {message}",
        "done": "Listo: {output}",
        "warning_prefix": "Advertencia: {warning}",
        "no_text_found": "No se encontró texto — reintentando con modelo de visión '{model}'...",
        "run_configure": "Ejecute: markitdown-for-everyone --configure",
        "output_same_as_input": (
            "Error: la ruta de salida debe ser distinta del archivo de entrada."
        ),
        "no_output_empty": "No se produjo contenido; no se escribió ningún archivo.",
        "non_interactive_stdin": (
            "Error: se requiere entrada interactiva pero la entrada estándar está cerrada."
        ),
        "non_interactive_input_required": (
            "Error: no se indicó un archivo y --non-interactive está activo."
        ),
        "non_interactive_overwrite": (
            "Error: el archivo de salida '{path}' ya existe; use --yes para sobrescribirlo."
        ),
        # API key validation
        "key_valid_balance": "Clave API válida. Saldo: {balance} pollen",
        "key_valid": "Clave API válida.",
        "key_invalid": "Clave API inválida. Obtenga su clave en https://enter.pollinations.ai",
        "key_verified": "Clave API verificada exitosamente.",
        "key_insufficient_balance": (
            "Advertencia: saldo de pollen insuficiente. Su clave es válida, "
            "pero deberá recargar en https://enter.pollinations.ai antes de convertir archivos."
        ),
        "key_connection_error": (
            "Advertencia: no se pudo conectar con la API de Pollinations "
            "para validar la clave. Verifique su conexión a internet."
        ),
        "key_format_warning": (
            "Advertencia: las claves API normalmente empiezan con 'sk_'. "
            "Obtenga su clave en https://enter.pollinations.ai"
        ),
        "key_short_warning": (
            "Advertencia: la clave API parece demasiado corta. "
            "Obtenga su clave en https://enter.pollinations.ai"
        ),
        "validation_nonjson_response": ("respuesta no JSON del endpoint de chat completions"),
        "validation_no_choices": (
            "la respuesta de chat completions no contiene el campo 'choices'"
        ),
        # Converter — retries and errors
        "retry_waiting": "Reintentando en {delay}s (intento {attempt}/{max_retries})...",
        "conn_error_fatal": "Error de conexión. Verifique su conexión a internet.",
        "auth_error": "Clave API inválida. Obtenga su clave en https://enter.pollinations.ai",
        "permission_error": (
            "Permiso denegado para el modelo '{model}'. Verifique los permisos de su clave API."
        ),
        "insufficient_balance_error": (
            "Saldo de pollen insuficiente. Recargue en https://enter.pollinations.ai"
        ),
        "model_not_found": "Modelo '{model}' no encontrado.",
        "rate_limit": "Límite de velocidad excedido: {error}",
        "api_status_error": "Error de API ({code}): {detail}",
        "api_error": "Error de API: {detail}",
        "unknown_api_error": "Error de API desconocido",
        "unsupported_format": "Formato de archivo no soportado: {ext}",
        "conversion_failed": "Conversión fallida: {error}",
        "missing_dep": "Dependencia faltante: {error}",
        "unexpected_error": "Error inesperado: {error}",
        "write_error": "No se pudo escribir el archivo de salida: {error}",
        "conversion_empty_warning": "La conversión no produjo contenido.",
        "llm_prompt_image": (
            "Describe esta imagen en detalle, incluyendo cualquier texto, objetos y contexto."
        ),
        "llm_prompt_ocr": (
            "Extrae todo el texto de esta imagen de documento, preservando tablas, "
            "listas y orden de lectura. Devuelve solo el texto extraído."
        ),
        # Model catalog labels
        "models_title": "Modelos recomendados (catálogo en vivo cuando está disponible):",
        "models_offline": "Catálogo en vivo no disponible; mostrando la lista integrada.",
        "model_tag_vision": "visión",
        "model_tag_paid": "de pago",
        "model_unknown_warning": (
            "Advertencia: el modelo '{model}' no aparece en el catálogo en vivo; "
            "se intentará de todos modos."
        ),
        "model_not_vision_warning": (
            "Advertencia: '{model}' no acepta imágenes como entrada; "
            "los resultados pueden ser pobres."
        ),
        # Config module — warnings / errors
        "config_warn_not_dict": (
            "Advertencia: el archivo de configuración no es un diccionario, "
            "usando valores por defecto"
        ),
        "config_warn_invalid_json": (
            "Advertencia: el archivo de configuración contiene JSON inválido: {error}"
        ),
        "config_warn_cannot_read": (
            "Advertencia: no se pudo leer el archivo de configuración: {error}"
        ),
        "config_warn_invalid_values": (
            "Advertencia: valor inválido para '{key}' en la configuración; "
            "usando el valor por defecto"
        ),
        "config_error_save": "Error: no se pudo guardar el archivo de configuración: {error}",
        # Prompts / labels
        "api_key_prompt": "Clave de API de Pollinations",
        "recommended": "Recomendados:",
        "select": "Seleccione: ",
        "file_not_found": "Archivo no encontrado: {path}",
        "by": "por",
        "press_enter_continue": "Presione Enter para continuar...",
    },
}
