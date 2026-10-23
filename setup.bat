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

:: Install dlib first (pinned to version with full Windows prebuilt wheels)
echo.
echo [Step 1/3] Installing dlib (face detection library)...
pip install dlib==19.24.2 --quiet

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
    echo   4. Click Install ^(it may take 5-10 minutes^)
    echo   5. Restart your computer
    echo   6. Run setup.bat again
    echo.
    pause
    exit /b 1
)

:: Verify dlib works properly with face_recognition
echo Verifying dlib installation...
python -c "import dlib; assert hasattr(dlib, 'face_recognition_model_v1'), 'dlib missing face recognition features'" 2>nul
if errorlevel 1 (
    echo.
    echo [ERROR] dlib installed but is missing face recognition features.
    echo Reinstalling correct version...
    pip uninstall dlib -y --quiet
    pip install dlib==19.24.2 --quiet
)

echo [OK] dlib installed and verified.

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
