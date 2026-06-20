"""Internationalization support for Markitdown-for-everyone."""

from __future__ import annotations

_current_language: str = "en"


def set_language(lang: str) -> None:
    """Set the current language for all subsequent translation lookups."""
    global _current_language  # noqa: PLW0603  — intentional module-level state
    _current_language = lang


def _(key: str) -> str:
    """Return the translated string for *key* in the current language.

    Falls back to English when the key is missing from the selected language
    or from the English dictionary itself.
    """
    return TRANSLATIONS.get(_current_language, {}).get(key, TRANSLATIONS["en"].get(key, key))


# ── Translation data ──────────────────────────────────────────────────────────

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
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
        "press_enter_retry": "Press Enter to try again...",
        "error_save_config": "Error: could not save the configuration.",
        "api_key_required_warn": "An API key is required.",
        "api_key_required_exit": "An API key is required to use the program.",
        # Main menu
        "menu_title": "--- Menu ---",
        "menu_convert_pdf": "1. Convert PDF to Markdown",
        "menu_convert_image": "2. Convert Image to Markdown",
        "menu_convert_document": "3. Convert Document to Markdown",
        "menu_configure": "4. Configure API key and models",
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
        "converting": "Converting {input} -> {output} using model {model}...",
        "spinner_text": "Converting... ",
        "file_kind_pdf": "PDF",
        "file_kind_image": "Image",
        "file_kind_document": "Document",
        "not_vision_warning": (
            "Warning: '{model}' is not a vision model. Images may not convert correctly."
        ),
        "conversion_cancelled": "Conversion cancelled.",
        "error_prefix": "Error: {message}",
        "done": "Done: {output}",
        "warning_prefix": "Warning: {warning}",
        "no_text_found": "No text found — retrying with vision model '{model}'...",
        "api_key_not_configured": "Error: API key not configured.",
        "run_configure": "Run: python markitdown_for_everyone.py --configure",
        # API key validation
        "key_valid_balance": "API key is valid. Balance: {balance} pollen",
        "key_valid": "API key is valid.",
        "key_invalid": "Invalid API key. Get your key at https://enter.pollinations.ai",
        "key_verified": "API key verified successfully.",
        "key_insufficient_balance": (
            "Warning: Insufficient pollen balance. Your key is valid, but you will need to "
            "top up at https://enter.pollinations.ai before converting files."
        ),
        "key_connection_error": (
            "Warning: Could not connect to Pollinations API to validate the key. "
            "Check your internet connection."
        ),
        "key_format_warning": (
            "Warning: API keys usually start with 'sk_' or 'sk-'. "
            "Get your key at https://enter.pollinations.ai"
        ),
        "key_short_warning": (
            "Warning: The API key seems too short. Get your key at https://enter.pollinations.ai"
        ),
        # Converter — printed messages
        "conn_error_retry": (
            "Connection error (attempt {attempt}/{max_retries}). Retrying in {delay}s..."
        ),
        # Converter — result messages
        "write_error": "Could not write output file: {error}",
        "auth_error": "Invalid API key. Get your key at https://enter.pollinations.ai",
        "conn_error_fatal": "Connection error. Please check your internet connection.",
        "model_not_found": "Model '{model}' not found.",
        "rate_limit": "Rate limit exceeded: {error}",
        "api_status_error": "API error ({code}): {detail}",
        "api_error": "API error: {detail}",
        "unsupported_format": "Unsupported file format: {ext}",
        "conversion_failed": "Conversion failed: {error}",
        "missing_dep": "Missing dependency: {error}",
        "unexpected_error": "Unexpected error: {error}",
        # Config module — warnings / errors
        "config_warn_not_dict": "Warning: Config file is not a dict, using defaults",
        "config_warn_invalid_json": "Warning: Config file contains invalid JSON: {error}",
        "config_warn_cannot_read": "Warning: Could not read config file: {error}",
        "config_error_save": "Error: Could not save config file: {error}",
        # Prompts / labels
        "api_key_prompt": "Pollinations API key",
        "recommended": "Recommended:",
        "select": "Select: ",
        "file_not_found": "File not found: {path}",
        "by": "by",
        # Misc
        "press_enter_continue": "Press Enter to continue...",
        "conversion_empty_warning": "Conversion succeeded but produced no content.",
        # New keys
        "overwrite_cancelled": "Overwrite cancelled.",
        "no_output_empty": "No content was produced; no file was written.",
        "not_vision_info": (
            "Note: '{model}' is not in the known vision models list. "
            "Image conversion may be limited."
        ),
        "language_flag_help": "Interface language (en/es)",
        "verbose_help": "Show informational messages",
        "debug_help": "Show debug messages",
        "language_detected": "Detected system language: {lang}",
    },
    "es": {
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
        "press_enter_retry": "Presione Enter para intentar de nuevo...",
        "error_save_config": "Error: no se pudo guardar la configuración.",
        "api_key_required_warn": "Se requiere una clave API.",
        "api_key_required_exit": "Se requiere una clave API para usar el programa.",
        # Main menu
        "menu_title": "--- Menú ---",
        "menu_convert_pdf": "1. Convertir PDF a Markdown",
        "menu_convert_image": "2. Convertir Imagen a Markdown",
        "menu_convert_document": "3. Convertir Documento a Markdown",
        "menu_configure": "4. Configurar clave API y modelos",
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
        "converting": "Convirtiendo {input} -> {output} usando modelo {model}...",
        "spinner_text": "Convirtiendo... ",
        "file_kind_pdf": "PDF",
        "file_kind_image": "Imagen",
        "file_kind_document": "Documento",
        "not_vision_warning": (
            "Advertencia: '{model}' no es un modelo de visión. "
            "Es posible que las imágenes no se conviertan correctamente."
        ),
        "conversion_cancelled": "Conversión cancelada.",
        "error_prefix": "Error: {message}",
        "done": "Listo: {output}",
        "warning_prefix": "Advertencia: {warning}",
        "no_text_found": "No se encontró texto — reintentando con modelo de visión '{model}'...",
        "api_key_not_configured": "Error: Clave API no configurada.",
        "run_configure": "Ejecute: python markitdown_for_everyone.py --configure",
        # API key validation
        "key_valid_balance": "Clave API válida. Saldo: {balance} pollen",
        "key_valid": "Clave API válida.",
        "key_invalid": "Clave API inválida. Obtenga su clave en https://enter.pollinations.ai",
        "key_verified": "Clave API verificada exitosamente.",
        "key_insufficient_balance": (
            "Advertencia: Saldo de pollen insuficiente. Su clave es válida, "
            "pero deberá recargar en https://enter.pollinations.ai antes de convertir archivos."
        ),
        "key_connection_error": (
            "Advertencia: No se pudo conectar con la API de Pollinations "
            "para validar la clave. Verifique su conexión a internet."
        ),
        "key_format_warning": (
            "Advertencia: Las claves API normalmente empiezan con 'sk_' o 'sk-'. "
            "Obtenga su clave en https://enter.pollinations.ai"
        ),
        "key_short_warning": (
            "Advertencia: La clave API parece demasiado corta. "
            "Obtenga su clave en https://enter.pollinations.ai"
        ),
        # Converter — printed messages
        "conn_error_retry": (
            "Error de conexión (intento {attempt}/{max_retries}). Reintentando en {delay}s..."
        ),
        # Converter — result messages
        "write_error": "No se pudo escribir el archivo de salida: {error}",
        "auth_error": "Clave API inválida. Obtenga su clave en https://enter.pollinations.ai",
        "conn_error_fatal": "Error de conexión. Verifique su conexión a internet.",
        "model_not_found": "Modelo '{model}' no encontrado.",
        "rate_limit": "Límite de velocidad excedido: {error}",
        "api_status_error": "Error de API ({code}): {detail}",
        "api_error": "Error de API: {detail}",
        "unsupported_format": "Formato de archivo no soportado: {ext}",
        "conversion_failed": "Conversión fallida: {error}",
        "missing_dep": "Dependencia faltante: {error}",
        "unexpected_error": "Error inesperado: {error}",
        # Config module — warnings / errors
        "config_warn_not_dict": (
            "Advertencia: El archivo de configuración no es un diccionario, "
            "usando valores por defecto"
        ),
        "config_warn_invalid_json": (
            "Advertencia: El archivo de configuración contiene JSON inválido: {error}"
        ),
        "config_warn_cannot_read": (
            "Advertencia: No se pudo leer el archivo de configuración: {error}"
        ),
        "config_error_save": "Error: No se pudo guardar el archivo de configuración: {error}",
        # Prompts / labels
        "api_key_prompt": "Clave de API de Pollinations",
        "recommended": "Recomendados:",
        "select": "Seleccione: ",
        "file_not_found": "Archivo no encontrado: {path}",
        "by": "por",
        # Misc
        "press_enter_continue": "Presione Enter para continuar...",
        "conversion_empty_warning": "La conversión se completó pero no produjo contenido.",
        # New keys
        "overwrite_cancelled": "Sobrescritura cancelada.",
        "no_output_empty": "No se produjo contenido; no se escribió ningún archivo.",
        "not_vision_info": (
            "Nota: '{model}' no está en la lista de modelos de visión conocidos. "
            "La conversión de imágenes puede ser limitada."
        ),
        "language_flag_help": "Idioma de la interfaz (en/es)",
        "verbose_help": "Mostrar mensajes informativos",
        "debug_help": "Mostrar mensajes de depuración",
        "language_detected": "Idioma del sistema detectado: {lang}",
    },
}
