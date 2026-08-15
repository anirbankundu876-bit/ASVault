@echo off
title ASVault v2 — Build EXE
echo ============================================
echo   Building ASVault v2 Single EXE
echo ============================================
echo.

python -m pip install pyinstaller --quiet

echo Building...
pyinstaller ASVault_v2.spec --clean

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed. Check output above.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Build Complete!
echo ============================================
echo.
echo Your EXE is at: dist\ASVault_v2.exe
echo Share just that one file — no other files needed!
echo.
pause
