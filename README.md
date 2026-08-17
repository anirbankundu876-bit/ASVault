# ASVault v2

A desktop AI coding assistant built with Python and CustomTkinter. Runs fully offline with local GGUF models, or online via API keys (OpenAI, Anthropic, Gemini). Distributed as a single-file EXE via PyInstaller.

🔗 **Website:** https://asvault-six.vercel.app/

## Overview

ASVault gives you a 4-panel coding assistant GUI — file browser, chat, code viewer, and terminal — all in one window. The AI can act directly on your files and terminal using structured XML tags, making it agentic rather than just conversational.

## Features

- **Offline-first** — runs 100% locally with GGUF models via `llama-cpp-python`, no internet required
- **Also supports online models** — OpenAI, Anthropic, and Gemini via API keys
- **Agentic actions** — the AI can create, edit, delete, and search files, and run terminal commands directly
- **4-panel layout** — file tree, chat, syntax-highlighted code viewer, and embedded terminal, all visible at once
- **GPU acceleration** — CUDA support via `llama-cpp-python` (abetlen's prebuilt wheels)
- **One-click setup** — `install.bat` installs dependencies and creates required folders
- **Single EXE build** — `build_exe.bat` produces a standalone `dist/ASVault_v2.exe`

## Architecture

| File | Purpose |
|---|---|
| `main.py` | Entry point — orchestrates all modules, background model loading |
| `ui.py` | 4-panel CustomTkinter GUI: File Browser / Chat / Code Viewer (top), Terminal (bottom) |
| `chat_engine.py` | Conversation history, prompt building, XML tag parsing |
| `action_executor.py` | Dispatches parsed tags to file/terminal handlers |
| `model_manager.py` | Loads local GGUF (llama-cpp) or API models, with lazy imports |
| `file_io.py` | Core file ops — create/read/edit/delete/search files, create/move/copy folders |
| `file_manager.py` | Directory browsing, file/content search, context file selection for the AI |
| `terminal.py` | Embedded terminal widget with command history, `cd` support, 30s timeout |
| `code_viewer.py` | Syntax-highlighted viewer (Python/JS/HTML/CSS/JSON/MD) with zoom |

## Action Tags

The AI executes actions through structured tags in its responses:

```xml
<create_file path="file.py">content</create_file>
<edit_file path="file.py">search->replace</edit_file>
<read_file path="file.py"/>
<delete_file path="file.py"/>
<search_file path="file.py" pattern="term"/>
<create_folder path="folder"/>
<run_command>python test.py</run_command>
```

## Setup & Usage

```bash
# Setup — installs deps, creates models/ config/ workspace/
install.bat

# Run from source — place a .gguf model in models/ first
python main.py

# Build a standalone EXE
build_exe.bat        # outputs dist/ASVault_v2.exe
```

## Configuration

- `config/settings.json` — UI/theme, model parameters (context length, temperature, GPU layers)
- `keys.json` (gitignored) — API keys for OpenAI/Anthropic/Gemini, only needed for online models
- Local models are auto-detected from the `models/` folder

**Note:** `keys.json` is gitignored — never commit real API keys to this repo.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Contributing

Issues and pull requests are welcome. All changes go through review before merging.
