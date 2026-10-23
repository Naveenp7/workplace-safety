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
    echo.
    echo Please download and install Python 3.11 from:
    echo   https://www.python.org/downloads/
    echo.
    echo IMPORTANT: During install, tick "Add Python to PATH"!
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

call venv\Scripts\activate.bat

:: Install dlib separately first (prebuilt binary - no C++ compiler needed)
echo.
echo [Step 1/3] Installing dlib (face detection library)...
pip install dlib --only-binary=:all: --quiet 2>nul

if errorlevel 1 (
    echo.
    echo [WARNING] Could not install prebuilt dlib.
    echo Trying alternative method...
    echo.
    pip install dlib --quiet 2>nul
    if errorlevel 1 (
        echo.
        echo ============================================
        echo   DLIB INSTALL FAILED - ACTION REQUIRED
        echo ============================================
        echo.
        echo dlib needs "Visual Studio C++ Build Tools" to compile.
        echo.
        echo Steps to fix:
        echo   1. Go to: https://visualstudio.microsoft.com/visual-cpp-build-tools/
        echo   2. Download and run "vs_buildtools.exe"
        echo   3. In the installer, select "Desktop development with C++"
        echo   4. Click Install (it may take 5-10 minutes)
        echo   5. Restart your computer
        echo   6. Run setup.bat again
        echo.
        pause
        exit /b 1
    )
)
echo [OK] dlib installed.

:: Install remaining packages
echo.
echo [Step 2/3] Installing all other backend packages...
pip install -r requirements.txt --quiet

if errorlevel 1 (
    echo.
    echo [ERROR] Backend installation failed. See above for details.
    pause
    exit /b 1
)

echo [OK] Backend ready.

:: Setup frontend
echo.
echo [Step 3/3] Setting up frontend...
cd /d "%~dp0frontend"

where node >nul 2>&1
if errorlevel 1 (
    echo.
    echo [WARNING] Node.js not found. Frontend won't work.
    echo Download Node.js LTS from: https://nodejs.org/
    echo Then run setup.bat again.
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
