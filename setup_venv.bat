@echo off
REM Snippet Tool - Virtual Environment Setup
REM Run this once after extracting the app to any computer
REM This script will:
REM   1. Detect Python 3.11 (required for stable ML environment)
REM   2. Create venv with Python 3.11
REM   3. Install all dependencies from requirements.txt

setlocal enabledelayedexpansion

echo ========================================
echo Snippet Tool - Environment Setup
echo ========================================
echo.

REM Check if Python 3.11 is available
echo Detecting Python 3.11...
py -3.11 --version >nul 2>&1

if errorlevel 1 (
    echo ERROR: Python 3.11 is not installed or not in PATH
    echo.
    echo This app requires Python 3.11 for stable ML/OCR functionality
    echo Please install Python 3.11 from python.org
    echo.
    pause
    exit /b 1
)

echo Python 3.11 found. Proceeding with setup...
echo.

REM Remove old venv if it exists
if exist venv (
    echo Removing old virtual environment...
    rmdir /s /q venv >nul 2>&1
    echo Done.
)

REM Create new venv with Python 3.11
echo Creating virtual environment with Python 3.11...
py -3.11 -m venv venv

if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Virtual environment created.
echo.

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

REM Install requirements
echo Installing dependencies from requirements.txt...
echo This may take a few minutes (torch is large)...
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Your environment is now ready to use:
echo   - Python 3.11
echo   - PyQt5 (GUI)
echo   - torch 2.0.0 (ML backend)
echo   - easyocr (OCR/price detection)
echo   - All dependencies pinned for stability
echo.
echo To run the app:
echo   run_snippet_tool.bat
echo.
pause
