@echo off
REM Start Scheduler Service
echo Starting Petrol Price Forecasting Scheduler...
echo.

cd /d "%~dp0"
python scheduler\scheduler_app.py

pause
