# ASVault v2 — AI Coding Assistant

A desktop AI coding assistant. Double-click to run. Works offline with local GGUF models or online with API keys.

## Quick Start

### Option A — Run from source
1. Double-click `install.bat` (installs everything automatically)
2. Drop your `.gguf` model file into the `models/` folder
3. Run: `python main.py`

### Option B — Build a single .exe
1. Run `install.bat` first
2. Double-click `build_exe.bat`
3. Your EXE will be at `dist/ASVault_v2.exe` — share just that file!

## Adding Online Models (Optional)
Edit `keys.json` and add your API keys:
```json
{
  "openai": "sk-...",
  "anthropic": "sk-ant-...",
  "gemini": "AIza..."
}
```

## Folder Structure
```
ASVault_v2/
├── main.py              # Entry point
├── ui.py                # 4-panel GUI
├── chat_engine.py       # AI chat + tag parsing
├── action_executor.py   # Executes AI actions
├── model_manager.py     # Local + API model support
├── file_manager.py      # File browser logic
├── file_io.py           # File operations
├── code_viewer.py       # Syntax highlighted viewer
├── terminal.py          # Embedded terminal
├── config.py            # Settings
├── keys.json            # API keys (gitignored)
├── models/              # Place .gguf files here
├── install.bat          # One-click setup
└── build_exe.bat        # One-click EXE builder
```
