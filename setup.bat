@echo off
title Workplace Safety - Setup
echo ============================================
echo   Workplace Safety System - First-Time Setup
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please download and install Python 3.11 from:
    echo   https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during install!
    pause
    exit /b 1
)

echo [OK] Python found.
echo.

:: Create backend venv
echo Setting up backend...
cd /d "%~dp0backend"

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Installing backend packages (this may take a few minutes)...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet

if errorlevel 1 (
    echo.
    echo [ERROR] Backend installation failed. See above for details.
    pause
    exit /b 1
)

echo [OK] Backend ready.
echo.

:: Setup frontend
echo Setting up frontend...
cd /d "%~dp0frontend"

where node >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Node.js not found. Frontend won't work.
    echo Download from: https://nodejs.org/
) else (
    echo Installing frontend packages...
    call npm install --silent
    echo [OK] Frontend ready.
)

echo.
echo ============================================
echo   Setup complete! Run START.bat to launch.
echo ============================================
pause
