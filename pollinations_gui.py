"""
MarkItDown + Pollinations API — GUI
Graphical interface for converting files to Markdown using Pollinations API.
"""

import json
import os
import threading
from pathlib import Path
from tkinter import (
    Tk, Frame, Label, Entry, Button, Text,
    filedialog, messagebox, StringVar, Toplevel
)
from tkinter.ttk import Progressbar

from openai import OpenAI
from markitdown import MarkItDown

CONFIG_FILE = Path(__file__).parent / "config.json"
POLLINATIONS_BASE_URL = "https://gen.pollinations.ai/v1"

# Known models with vision capability
VISION_MODELS = {
    "openai", "openai-large", "qwen-vision", "qwen-vision-pro",
    "gemini", "gemini-large", "claude", "claude-large"
}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}


def load_config():
    """Load configuration from config.json or return defaults."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, encoding="utf-8") as f:
                config = json.load(f)
                # Validate config structure
                if not isinstance(config, dict):
                    return {"api_key": "", "model": "openai"}
                return config
        except (json.JSONDecodeError, IOError, OSError) as e:
            # Corrupted or unreadable config file
            print(f"Warning: Could not load config file: {e}")
            pass
    return {"api_key": "", "model": "openai"}


def save_config(config):
    """Save configuration to config.json."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except (IOError, OSError) as e:
        print(f"Error: Could not save config file: {e}")
        return False


def is_image_file(filepath):
    """Check if the file is an image based on its extension."""
    return Path(filepath).suffix.lower() in IMAGE_EXTENSIONS


def validate_model(api_key, model_name):
    """
    Validate that the model exists in Pollinations.
    Returns: (bool, str) where str is an error message on failure.
    """
    try:
        client = OpenAI(base_url=POLLINATIONS_BASE_URL, api_key=api_key)
        models = client.models.list()

        model_ids = [m.id for m in models.data]

        if model_name not in model_ids:
            available = ", ".join(sorted(model_ids)[:10])
            if len(model_ids) > 10:
                available += f"... and {len(model_ids) - 10} more"
            return False, f"Model '{model_name}' not found.\n\nAvailable models: {available}"

        return True, ""

    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            return False, "Invalid API key. Get your key at https://enter.pollinations.ai"
        elif "connection" in error_msg.lower() or "network" in error_msg.lower():
            return False, "Connection error. Please check your internet connection."
        else:
            return False, f"Error validating model: {error_msg}"


class ConfigDialog(Toplevel):
    """Modal dialog for configuring API key and model."""

    def __init__(self, parent, current_config):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("520x300")
        self.resizable(False, False)
        self.configure(padx=20, pady=15)
        self.transient(parent)
        self.grab_set()

        self.result = None
        self.api_key_var = StringVar(value=current_config.get("api_key", ""))
        self.model_var = StringVar(value=current_config.get("model", "openai"))

        self._build_ui()
        self.wait_window()

    def _build_ui(self):
        Label(
            self,
            text="Pollinations API Settings",
            font=("Segoe UI", 14, "bold"),
        ).pack(pady=(0, 15))

        # API Key
        Label(self, text="API Key:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        Label(
            self,
            text="Get your key at: https://enter.pollinations.ai",
            font=("Segoe UI", 8),
            foreground="#666",
        ).pack(anchor="w", pady=(0, 3))

        api_entry = Entry(self, textvariable=self.api_key_var, font=("Segoe UI", 9), show="•")
        api_entry.pack(fill="x", pady=(0, 15))
        api_entry.focus_set()

        # Model
        Label(self, text="Image model:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        Label(
            self,
            text="With vision: openai, openai-large, qwen-vision, gemini, claude",
            font=("Segoe UI", 8),
            foreground="#666",
        ).pack(anchor="w", pady=(0, 3))

        Entry(self, textvariable=self.model_var, font=("Segoe UI", 9)).pack(fill="x", pady=(0, 20))

        # Buttons
        btn_frame = Frame(self)
        btn_frame.pack(fill="x")

        Button(
            btn_frame,
            text="Cancel",
            command=self._cancel,
            width=10,
            font=("Segoe UI", 9),
        ).pack(side="right", padx=(8, 0))

        Button(
            btn_frame,
            text="Validate & Save",
            command=self._save,
            width=15,
            font=("Segoe UI", 9, "bold"),
            bg="#2563eb",
            fg="white",
        ).pack(side="right")

        self.bind("<Return>", lambda e: self._save())
        self.bind("<Escape>", lambda e: self._cancel())

    def _save(self):
        api_key = self.api_key_var.get().strip()
        model = self.model_var.get().strip()

        if not api_key:
            messagebox.showwarning("Warning", "API Key cannot be empty.", parent=self)
            return

        if not model:
            messagebox.showwarning("Warning", "Model cannot be empty.", parent=self)
            return

        # Validate model against API
        self.configure(cursor="wait")
        self.update()

        valid, error_msg = validate_model(api_key, model)

        self.configure(cursor="")

        if not valid:
            messagebox.showerror("Validation Error", error_msg, parent=self)
            return

        self.result = {"api_key": api_key, "model": model}
        self.destroy()

    def _cancel(self):
        self.destroy()


class MarkItDownApp:
    """Main application window."""

    def __init__(self, root):
        self.root = root
        self.root.title("MarkItDown + Pollinations")
        self.root.geometry("700x520")
        self.root.resizable(True, True)
        self.root.configure(padx=20, pady=15)

        self.config = load_config()
        self.input_path = StringVar()
        self.output_path = StringVar()

        # Prompt for configuration if missing or incomplete
        if not self.config.get("api_key"):
            self._open_config()

        self._build_ui()

    def _build_ui(self):
        # --- Title ---
        title = Label(
            self.root,
            text="MarkItDown + Pollinations API",
            font=("Segoe UI", 16, "bold"),
        )
        title.pack(pady=(0, 5))

        subtitle = Label(
            self.root,
            text="Convert files to Markdown with AI-powered image descriptions",
            font=("Segoe UI", 9),
            foreground="#666",
        )
        subtitle.pack(pady=(0, 10))

        # --- Settings button ---
        config_frame = Frame(self.root)
        config_frame.pack(fill="x", pady=(0, 10))

        self.config_label = Label(
            config_frame,
            text=f"Model: {self.config.get('model', 'openai')}",
            font=("Segoe UI", 9),
            foreground="#2563eb",
        )
        self.config_label.pack(side="left")

        Button(
            config_frame,
            text="⚙ Settings",
            command=self._open_config,
            font=("Segoe UI", 9),
            width=12,
        ).pack(side="right")

        # --- Input file ---
        input_frame = Frame(self.root)
        input_frame.pack(fill="x", pady=(0, 10))

        Label(input_frame, text="File to convert:", font=("Segoe UI", 10, "bold")).pack(
            anchor="w"
        )

        input_row = Frame(input_frame)
        input_row.pack(fill="x", pady=(3, 0))

        Entry(input_row, textvariable=self.input_path, font=("Segoe UI", 9)).pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        Button(
            input_row,
            text="Browse…",
            command=self._browse_input,
            width=10,
            font=("Segoe UI", 9),
        ).pack(side="right")

        # --- Output file ---
        output_frame = Frame(self.root)
        output_frame.pack(fill="x", pady=(0, 10))

        Label(output_frame, text="Save as:", font=("Segoe UI", 10, "bold")).pack(
            anchor="w"
        )

        output_row = Frame(output_frame)
        output_row.pack(fill="x", pady=(3, 0))

        Entry(output_row, textvariable=self.output_path, font=("Segoe UI", 9)).pack(
            side="left", fill="x", expand=True, padx=(0, 8)
        )
        Button(
            output_row,
            text="Browse…",
            command=self._browse_output,
            width=10,
            font=("Segoe UI", 9),
        ).pack(side="right")

        # --- Convert button ---
        btn_frame = Frame(self.root)
        btn_frame.pack(fill="x", pady=(5, 10))

        self.convert_btn = Button(
            btn_frame,
            text="Convert",
            command=self._start_conversion,
            font=("Segoe UI", 11, "bold"),
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            height=2,
        )
        self.convert_btn.pack(fill="x")

        # --- Progress bar ---
        self.progress = Progressbar(self.root, mode="indeterminate")
        self.progress.pack(fill="x", pady=(0, 5))

        # --- Log ---
        log_frame = Frame(self.root)
        log_frame.pack(fill="both", expand=True)

        Label(log_frame, text="Status:", font=("Segoe UI", 10, "bold")).pack(anchor="w")

        self.log_text = Text(
            log_frame,
            height=8,
            font=("Consolas", 9),
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white",
            state="disabled",
            wrap="word",
        )
        self.log_text.pack(fill="both", expand=True, pady=(3, 0))

    def _log(self, msg):
        """Append a message to the log text widget."""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _open_config(self):
        """Open the settings dialog and save changes."""
        dialog = ConfigDialog(self.root, self.config)
        if dialog.result:
            self.config = dialog.result
            save_config(self.config)
            self.config_label.configure(text=f"Model: {self.config.get('model', 'openai')}")
            self._log(f"Settings updated. Model: {self.config['model']}")

    def _browse_input(self):
        """Open file dialog to select an input file."""
        path = filedialog.askopenfilename(
            title="Select file",
            filetypes=[
                ("All supported", "*.pdf *.docx *.pptx *.xlsx *.xls *.jpg *.jpeg *.png *.gif *.bmp *.webp *.wav *.mp3 *.html *.csv *.json *.xml *.epub *.zip"),
                ("PDF", "*.pdf"),
                ("Word", "*.docx"),
                ("PowerPoint", "*.pptx"),
                ("Excel", "*.xlsx *.xls"),
                ("Images", "*.jpg *.jpeg *.png *.gif *.bmp *.webp"),
                ("Audio", "*.wav *.mp3"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self.input_path.set(path)
            # Auto-suggest output filename
            stem = Path(path).stem
            suggested = str(Path(path).parent / f"{stem}.md")
            self.output_path.set(suggested)

    def _browse_output(self):
        """Open file dialog to select output location."""
        path = filedialog.asksaveasfilename(
            title="Save as",
            defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("Text", "*.txt"), ("All", "*.*")],
        )
        if path:
            self.output_path.set(path)

    def _start_conversion(self):
        """Validate inputs and start the conversion in a background thread."""
        input_file = self.input_path.get().strip()
        output_file = self.output_path.get().strip()

        if not input_file:
            messagebox.showwarning("Warning", "Please select a file to convert.")
            return
        if not os.path.isfile(input_file):
            messagebox.showerror("Error", f"File not found:\n{input_file}")
            return
        if not output_file:
            messagebox.showwarning("Warning", "Please select where to save the result.")
            return
        if not self.config.get("api_key"):
            messagebox.showerror(
                "Error",
                "API Key not configured.\nClick 'Settings' to add it.",
            )
            return

        # Warn if converting an image with a non-vision model
        if is_image_file(input_file):
            model = self.config.get("model", "")
            if model not in VISION_MODELS:
                result = messagebox.askyesno(
                    "Warning: Model without vision",
                    f"Model '{model}' does not support images.\n\n"
                    f"Recommended models with vision:\n"
                    f"• openai\n"
                    f"• openai-large\n"
                    f"• qwen-vision\n"
                    f"• gemini\n"
                    f"• claude\n\n"
                    f"Do you want to continue anyway?",
                )
                if not result:
                    return

        self.convert_btn.configure(state="disabled", text="Converting…")
        self.progress.start(10)
        self._log(f"Converting: {os.path.basename(input_file)}")

        thread = threading.Thread(target=self._do_conversion, args=(input_file, output_file))
        thread.daemon = True
        thread.start()

    def _do_conversion(self, input_file, output_file):
        """Run the actual conversion in a background thread."""
        try:
            client = OpenAI(
                base_url=POLLINATIONS_BASE_URL,
                api_key=self.config["api_key"],
            )

            md = MarkItDown(
                llm_client=client,
                llm_model=self.config.get("model", "openai"),
                llm_prompt="Describe this image in detail, including any text, objects, and context.",
            )

            result = md.convert(input_file)

            # Write output with error handling
            try:
                Path(output_file).write_text(result.text_content, encoding="utf-8")
            except (IOError, OSError, PermissionError) as e:
                self.root.after(0, self._log, f"Error: Could not write output file: {e}")
                self.root.after(
                    0,
                    lambda: messagebox.showerror(
                        "Write Error",
                        f"Could not write to:\n{output_file}\n\nError: {e}",
                    ),
                )
                return

            self.root.after(0, self._log, f"Done. Saved to: {output_file}")
            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Conversion complete",
                    f"File saved successfully:\n{output_file}",
                ),
            )

        except Exception as e:
            error_msg = str(e)

            # Improve error messages based on error type
            if "401" in error_msg or "Unauthorized" in error_msg:
                error_msg = "Invalid API key. Get your key at https://enter.pollinations.ai"
            elif "connection" in error_msg.lower() or "network" in error_msg.lower():
                error_msg = "Connection error. Please check your internet connection."
            elif "does not support image input" in error_msg:
                error_msg = (
                    f"Model '{self.config.get('model')}' does not support images. "
                    f"Use: openai, openai-large, qwen-vision, gemini, or claude"
                )

            self.root.after(0, self._log, f"Error: {error_msg}")
            self.root.after(0, lambda: messagebox.showerror("Conversion error", error_msg))

        finally:
            self.root.after(0, self._reset_ui)

    def _reset_ui(self):
        """Reset the UI after conversion completes or fails."""
        self.progress.stop()
        self.convert_btn.configure(state="normal", text="Convert")


def main():
    root = Tk()
    MarkItDownApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
