@echo off
REM Start Backend API Server
echo Starting Petrol Price Forecasting Backend API...
echo.

cd /d "%~dp0"
python backend\app.py

pause
