"""
Main window layout - 4-panel CustomTkinter UI
Layout:
  Top:    [File Browser | Chat Panel | Code Viewer]
  Bottom: [Terminal — full width]
"""

import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path
import threading

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ASVaultUI:
    """Main UI with 4-panel layout"""

    def __init__(self, app):
        self.app = app
        self.setup_main_window()
        self.create_layout()
        self.setup_bindings()
        self.add_welcome_message()

    def setup_main_window(self):
        self.root = ctk.CTk()
        self.root.title("ASVault v2 — Agentic Coding Assistant")
        self.root.geometry("1400x900")
        self.root.minsize(1100, 700)

        # Row 0 = top panels (expandable), Row 1 = terminal (fixed height)
        self.root.grid_rowconfigure(0, weight=3)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def create_layout(self):
        # ── Top container (3 columns) ──────────────────────────────────
        top = ctk.CTkFrame(self.root, fg_color="transparent")
        top.grid(row=0, column=0, sticky="nsew", padx=4, pady=(4, 2))
        top.grid_rowconfigure(0, weight=1)
        top.grid_columnconfigure(0, weight=1)   # file browser
        top.grid_columnconfigure(1, weight=2)   # chat
        top.grid_columnconfigure(2, weight=2)   # code viewer

        self._create_file_browser(top)
        self._create_chat_panel(top)
        self._create_code_viewer(top)

        # ── Terminal (full-width bottom) ───────────────────────────────
        self._create_terminal(self.root)

    # ──────────────────────────────────────────────────────────────────
    # FILE BROWSER
    # ──────────────────────────────────────────────────────────────────
    def _create_file_browser(self, parent):
        frame = ctk.CTkFrame(parent, corner_radius=8)
        frame.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Header
        hdr = ctk.CTkFrame(frame, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 2))
        ctk.CTkLabel(hdr, text="📁 Files", font=("Arial", 12, "bold")).pack(side="left")
        ctk.CTkButton(
            hdr, text="Open", width=60, height=26,
            command=self.open_folder
        ).pack(side="right")

        # File tree
        self.file_tree = ctk.CTkTextbox(frame, font=("Consolas", 10), activate_scrollbars=True)
        self.file_tree.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)
        self.file_tree.bind("<Button-1>", self._on_file_click)

        self.current_directory = Path.cwd()
        self._refresh_file_browser()

    def _refresh_file_browser(self):
        self.file_tree.delete("1.0", "end")
        try:
            items = sorted(self.current_directory.iterdir(),
                           key=lambda x: (not x.is_dir(), x.name.lower()))
            for item in items:
                if item.name.startswith("."):
                    continue
                icon = "📂 " if item.is_dir() else "📄 "
                suffix = "/" if item.is_dir() else ""
                self.file_tree.insert("end", f"{icon}{item.name}{suffix}\n")
        except PermissionError:
            self.file_tree.insert("end", "Permission denied\n")

    def _on_file_click(self, event):
        idx = self.file_tree.index(f"@{event.x},{event.y}")
        line = self.file_tree.get(f"{idx} linestart", f"{idx} lineend").strip()
        if not line:
            return
        # Strip emoji prefix
        name = line[2:].rstrip("/").strip()
        filepath = self.current_directory / name
        if filepath.exists() and filepath.is_file():
            self._load_file_in_viewer(filepath)

    def open_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.current_directory = Path(folder)
            self._refresh_file_browser()
            # Update file_io working directory
            self.app.file_io.set_working_directory(folder)
            self.app.file_manager.set_directory(folder)

    # ──────────────────────────────────────────────────────────────────
    # CHAT PANEL
    # ──────────────────────────────────────────────────────────────────
    def _create_chat_panel(self, parent):
        frame = ctk.CTkFrame(parent, corner_radius=8)
        frame.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_rowconfigure(2, weight=0)
        frame.grid_columnconfigure(0, weight=1)

        # Status bar
        self.model_status = ctk.CTkLabel(
            frame, text="⏳ Model loading...",
            font=("Arial", 10), text_color="orange"
        )
        self.model_status.grid(row=0, column=0, sticky="w", padx=8, pady=(6, 0))

        # Chat display
        self.chat_display = ctk.CTkTextbox(
            frame, wrap="word", font=("Consolas", 11), state="normal",
            activate_scrollbars=True
        )
        self.chat_display.grid(row=1, column=0, sticky="nsew", padx=6, pady=4)

        # Input row
        input_frame = ctk.CTkFrame(frame, fg_color="transparent")
        input_frame.grid(row=2, column=0, sticky="ew", padx=6, pady=(0, 6))
        input_frame.grid_columnconfigure(0, weight=1)

        self.message_input = ctk.CTkTextbox(
            input_frame, height=70, wrap="word", font=("Consolas", 11)
        )
        self.message_input.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        btn_col = ctk.CTkFrame(input_frame, fg_color="transparent", width=90)
        btn_col.grid(row=0, column=1, sticky="ns")

        self.send_button = ctk.CTkButton(
            btn_col, text="Send", height=32, command=self.send_message
        )
        self.send_button.pack(fill="x", pady=(0, 4))

        ctk.CTkButton(
            btn_col, text="Clear", height=32,
            fg_color="#555", hover_color="#444",
            command=self.clear_chat
        ).pack(fill="x")

        self.message_input.bind("<Control-Return>", lambda e: self.send_message())

    # ──────────────────────────────────────────────────────────────────
    # CODE VIEWER
    # ──────────────────────────────────────────────────────────────────
    def _create_code_viewer(self, parent):
        frame = ctk.CTkFrame(parent, corner_radius=8)
        frame.grid(row=0, column=2, sticky="nsew", padx=4, pady=4)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Header
        hdr = ctk.CTkFrame(frame, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 2))

        self.file_name_label = ctk.CTkLabel(
            hdr, text="No file selected", font=("Arial", 11, "bold")
        )
        self.file_name_label.pack(side="left")

        ctk.CTkButton(
            hdr, text="💾 Save", width=70, height=26,
            command=self.save_file
        ).pack(side="right")

        # Code text box
        self.code_viewer = ctk.CTkTextbox(
            frame, font=("Consolas", 11), wrap="none", activate_scrollbars=True
        )
        self.code_viewer.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)

    def _load_file_in_viewer(self, filepath: Path):
        try:
            content = filepath.read_text(encoding="utf-8")
            self.code_viewer.delete("1.0", "end")
            self.code_viewer.insert("1.0", content)
            self.file_name_label.configure(text=filepath.name)
            self._current_file_path = filepath
        except Exception as e:
            self.code_viewer.delete("1.0", "end")
            self.code_viewer.insert("1.0", f"Error loading file: {e}")

    def save_file(self):
        if hasattr(self, "_current_file_path") and self._current_file_path:
            content = self.code_viewer.get("1.0", "end-1c")
            self._current_file_path.write_text(content, encoding="utf-8")
            self._add_message("System", f"✅ Saved: {self._current_file_path.name}")

    # ──────────────────────────────────────────────────────────────────
    # TERMINAL (full-width bottom)
    # ──────────────────────────────────────────────────────────────────
    def _create_terminal(self, parent):
        frame = ctk.CTkFrame(parent, corner_radius=8)
        frame.grid(row=1, column=0, sticky="nsew", padx=4, pady=(2, 4))
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Header
        hdr = ctk.CTkFrame(frame, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 0))
        ctk.CTkLabel(hdr, text="⚡ Terminal", font=("Arial", 11, "bold")).pack(side="left")
        ctk.CTkButton(
            hdr, text="Clear", width=60, height=24,
            fg_color="#555", hover_color="#444",
            command=lambda: self.app.terminal.clear()
        ).pack(side="right")

        self.terminal_widget = ctk.CTkTextbox(
            frame, font=("Consolas", 10), height=160, activate_scrollbars=True
        )
        self.terminal_widget.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)

        # Connect terminal module to widget
        self.app.terminal.set_widget(self.terminal_widget)

    # ──────────────────────────────────────────────────────────────────
    # CHAT LOGIC
    # ──────────────────────────────────────────────────────────────────
    def add_welcome_message(self):
        welcome = (
            "╔══════════════════════════════════════════╗\n"
            "║     ASVault v2 — AI Coding Assistant      ║\n"
            "╚══════════════════════════════════════════╝\n\n"
            "I can help you:\n"
            "  • Write, edit, and debug code\n"
            "  • Create and manage files & folders\n"
            "  • Search your project\n"
            "  • Run terminal commands\n\n"
            "Open a folder on the left to get started.\n"
            "Press Ctrl+Enter to send a message.\n"
        )
        self._add_message("ASVault", welcome)

    def _add_message(self, sender: str, message: str):
        """Append a message to chat display (thread-safe via root.after)"""
        def _insert():
            self.chat_display.configure(state="normal")
            color = "#4EC9B0" if sender == "ASVault" else \
                    "#569CD6" if sender == "You" else "#858585"
            self.chat_display.insert("end", f"\n[{sender}]\n")
            self.chat_display.insert("end", f"{message}\n")
            self.chat_display.insert("end", "─" * 60 + "\n")
            self.chat_display.see("end")
        self.root.after(0, _insert)

    def send_message(self):
        message = self.message_input.get("1.0", "end-1c").strip()
        if not message:
            return

        self.message_input.delete("1.0", "end")
        self._add_message("You", message)
        self.send_button.configure(state="disabled", text="...")

        def worker():
            try:
                response = self.app.send_message(message)
                self._add_message("ASVault", response)
                # Refresh file browser in case files were created
                self.root.after(200, self._refresh_file_browser)
            except Exception as e:
                self._add_message("Error", str(e))
            finally:
                self.root.after(0, lambda: self.send_button.configure(
                    state="normal", text="Send"
                ))

        threading.Thread(target=worker, daemon=True).start()

    def clear_chat(self):
        self.chat_display.delete("1.0", "end")
        self.add_welcome_message()

    # ──────────────────────────────────────────────────────────────────
    # MISC
    # ──────────────────────────────────────────────────────────────────
    def setup_bindings(self):
        self.root.bind("<Control-o>", lambda e: self.open_folder())
        self.root.bind("<Control-s>", lambda e: self.save_file())

    def update_model_status(self, status: str, color: str = "orange"):
        self.model_status.configure(text=f"🤖 {status}", text_color=color)
