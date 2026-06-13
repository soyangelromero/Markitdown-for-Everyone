"""Tkinter GUI for MarkItDown + Pollinations."""

from __future__ import annotations

import os
import threading
from pathlib import Path
from tkinter import (
    Button,
    Entry,
    Frame,
    Label,
    StringVar,
    Text,
    Toplevel,
    filedialog,
    messagebox,
)
from tkinter.ttk import Progressbar

from markitdown_pollinations.config import load_config, save_config
from markitdown_pollinations.constants import IMAGE_EXTENSIONS, SUPPORTED_FILETYPES, VISION_MODELS
from markitdown_pollinations.converter import convert_file
from markitdown_pollinations.pollinations_client import ModelValidationThread


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
        self._validation_thread: ModelValidationThread | None = None

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

        self.cancel_btn = Button(
            btn_frame,
            text="Cancel",
            command=self._cancel,
            width=10,
            font=("Segoe UI", 9),
        )
        self.cancel_btn.pack(side="right", padx=(8, 0))

        self.save_btn = Button(
            btn_frame,
            text="Validate & Save",
            command=self._save,
            width=15,
            font=("Segoe UI", 9, "bold"),
            bg="#2563eb",
            fg="white",
        )
        self.save_btn.pack(side="right")

        self.bind("<Return>", lambda e: self._save())
        self.bind("<Escape>", lambda e: self._cancel())

    def _set_validating(self, validating: bool):
        if validating:
            self.save_btn.configure(state="disabled", text="Validating…")
            self.configure(cursor="wait")
        else:
            self.save_btn.configure(state="normal", text="Validate & Save")
            self.configure(cursor="")

    def _save(self):
        api_key = self.api_key_var.get().strip()
        model = self.model_var.get().strip()

        if not api_key:
            messagebox.showwarning("Warning", "API Key cannot be empty.", parent=self)
            return

        if not model:
            messagebox.showwarning("Warning", "Model cannot be empty.", parent=self)
            return

        self._set_validating(True)

        def on_result(success: bool, message: str):
            try:
                self.after(0, self._handle_validation_result, success, message)
            except RuntimeError:
                # Dialog was closed while validation was running.
                pass

        self._validation_thread = ModelValidationThread(api_key, model, on_result)
        self._validation_thread.start()

    def _handle_validation_result(self, success: bool, message: str):
        try:
            exists = self.winfo_exists()
        except RuntimeError:
            exists = False
        if not exists:
            return
        self._set_validating(False)
        if not success:
            messagebox.showerror("Validation Error", message, parent=self)
            return

        self.result = {"api_key": self.api_key_var.get().strip(), "model": self.model_var.get().strip()}
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

        self._cancel_event: threading.Event | None = None
        self._conversion_thread: threading.Thread | None = None

        self._build_ui()

        if not self.config.get("api_key"):
            self._open_config()

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

        # --- Convert / Cancel buttons ---
        btn_frame = Frame(self.root)
        btn_frame.pack(fill="x", pady=(5, 10))

        self.cancel_btn = Button(
            btn_frame,
            text="Cancel",
            command=self._cancel_conversion,
            font=("Segoe UI", 11, "bold"),
            bg="#dc2626",
            fg="white",
            activebackground="#b91c1c",
            activeforeground="white",
            height=2,
            state="disabled",
        )
        self.cancel_btn.pack(fill="x", pady=(0, 5))

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
            if not save_config(self.config):
                messagebox.showerror(
                    "Save Error",
                    "Could not save settings to config.json.",
                    parent=self.root,
                )
                return
            self.config_label.configure(text=f"Model: {self.config.get('model', 'openai')}")
            self._log(f"Settings updated. Model: {self.config['model']}")

    def _browse_input(self):
        """Open file dialog to select an input file."""
        path = filedialog.askopenfilename(
            title="Select file",
            filetypes=SUPPORTED_FILETYPES,
        )
        if path:
            self.input_path.set(path)
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

        if Path(input_file).suffix.lower() in IMAGE_EXTENSIONS:
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
        self.cancel_btn.configure(state="normal")
        self.progress.start(10)
        self._log(f"Converting: {os.path.basename(input_file)}")

        self._cancel_event = threading.Event()
        self._conversion_thread = threading.Thread(
            target=self._do_conversion,
            args=(input_file, output_file),
            daemon=True,
        )
        self._conversion_thread.start()

    def _cancel_conversion(self):
        """Signal the running conversion to cancel."""
        if self._cancel_event is not None:
            self._cancel_event.set()
            self._log("Cancelling…")
            self.cancel_btn.configure(state="disabled")

    def _do_conversion(self, input_file, output_file):
        """Run the actual conversion in a background thread."""
        result = convert_file(
            input_file,
            output_file,
            self.config["api_key"],
            self.config.get("model", "openai"),
            cancel_event=self._cancel_event,
        )

        if result.cancelled:
            self.root.after(0, self._log, "Conversion cancelled.")
        elif not result.success:
            self.root.after(0, self._log, f"Error: {result.message}")
            self.root.after(0, lambda: messagebox.showerror("Conversion error", result.message))
        else:
            self.root.after(0, self._log, f"Done. Saved to: {result.output_path}")
            if result.warning:
                self.root.after(0, self._log, f"Warning: {result.warning}")
            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Conversion complete",
                    f"File saved successfully:\n{result.output_path}",
                ),
            )

        self.root.after(0, self._reset_ui)

    def _reset_ui(self):
        """Reset the UI after conversion completes or fails."""
        self.progress.stop()
        self.convert_btn.configure(state="normal", text="Convert")
        self.cancel_btn.configure(state="disabled")
        self._cancel_event = None
        self._conversion_thread = None


def main():
    from tkinter import Tk

    root = Tk()
    MarkItDownApp(root)
    root.mainloop()
