@echo off
REM Snippet Tool Launcher - Runs from root directory
setlocal enabledelayedexpansion

REM Change to script directory to ensure correct working directory
cd /d "%~dp0"

REM Check if venv exists
if not exist venv\Scripts\python.exe (
    echo.
    echo ERROR: Virtual environment not set up
    echo.
    echo You must run setup_venv.bat first to set up your environment
    echo.
    echo This is a one-time setup that will:
    echo   - Create a Python 3.11 virtual environment
    echo   - Install all dependencies (PyQt5, torch, easyocr, etc.)
    echo.
    echo After setup, run this script again.
    echo.
    pause
    exit /b 1
)

REM UTF-8 encoding for Windows console
set PYTHONIOENCODING=utf-8

REM PyTorch CPU settings for optimal performance
set OMP_NUM_THREADS=1
set MKL_THREADING_LAYER=GNU

REM Set GUI-specific environment variables
set QT_QPA_PLATFORM_PLUGIN_PATH=
set QT_DEBUG_PLUGINS=0

REM Activate virtual environment
call venv\Scripts\activate.bat

echo ========================================
echo Snippet Tool - Shrinkflation Analyzer
echo ========================================
echo.
echo Starting application...
echo Working directory: %CD%
echo.
echo NOTE: The application window will appear shortly
echo       (OCR initialization takes 10-15 seconds first time)
echo.

REM Run from root directory where main.py is located
REM Using -u for unbuffered output and to avoid hanging
python -u main.py

if errorlevel 1 (
    echo.
    echo ERROR: Application failed to start
    echo.
    echo Troubleshooting:
    echo - Ensure setup_venv.bat was run successfully
    echo - Check that main.py exists in current directory
    echo - If OCR errors occur, check your internet connection
    echo.
    echo For more help, check: SETUP_INSTRUCTIONS.md
    echo.
)
pause
