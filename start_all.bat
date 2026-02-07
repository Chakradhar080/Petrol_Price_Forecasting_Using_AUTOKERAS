@echo off
REM Start Both Backend and Frontend
echo ============================================================
echo   Petrol Price Forecasting System - Full Stack Launcher
echo ============================================================
echo.
echo Starting Backend API and Frontend Dashboard...
echo.

cd /d "%~dp0"

REM Start Backend in new window
echo [1/2] Starting Backend API on http://localhost:5000
start "Backend API" cmd /k "python backend\app.py"

REM Wait 3 seconds for backend to start
timeout /t 3 /nobreak >nul

REM Start Frontend in new window
echo [2/2] Starting Frontend Dashboard on http://localhost:3000
start "Frontend Dashboard" cmd /k "cd frontend && npm start"

echo.
echo ============================================================
echo   Both services are starting in separate windows!
echo ============================================================
echo.
echo   Backend API:  http://localhost:5000
echo   Frontend:     http://localhost:3000
echo.
echo   Press any key to close this launcher window...
echo   (The services will continue running in their own windows)
echo ============================================================
pause >nul
