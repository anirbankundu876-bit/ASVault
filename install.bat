@echo off
title ASVault v2 — Setup
echo ============================================
echo   ASVault v2 Setup
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.10+ from https://python.org
    echo Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

echo [OK] Python found
echo.

:: Install core packages
echo Installing packages...
python -m pip install --upgrade pip
python -m pip install customtkinter pillow openai anthropic google-generativeai requests python-dotenv

echo.
echo ============================================
echo   Installing llama-cpp-python (GPU build)
echo ============================================
python -m pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu122

if errorlevel 1 (
    echo.
    echo [WARN] GPU build failed, falling back to CPU build...
    python -m pip install llama-cpp-python
)

:: Create folders
if not exist models mkdir models
if not exist config mkdir config
if not exist workspace mkdir workspace

echo.
echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo Place your .gguf model file in the models\ folder
echo Then run: python main.py
echo.
pause
