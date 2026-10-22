@echo off
title Workplace Safety - Starting...

echo Starting Workplace Safety System...
echo.

:: Start backend
echo [1/2] Starting backend server...
cd /d "%~dp0backend"
call venv\Scripts\activate.bat
start "Backend" cmd /k "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 >nul

:: Start frontend
echo [2/2] Starting frontend...
cd /d "%~dp0frontend"
start "Frontend" cmd /k "npm run dev"

echo.
echo ============================================
echo   App is starting!
echo   Open your browser at: http://localhost:5173
echo   Backend API running at: http://localhost:8000
echo ============================================
echo.
echo Close the two terminal windows to stop the app.
pause
