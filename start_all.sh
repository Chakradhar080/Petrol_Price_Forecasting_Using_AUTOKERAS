#!/bin/bash
# Start Both Backend and Frontend (Linux/Mac)

echo "============================================================"
echo "  Petrol Price Forecasting System - Full Stack Launcher"
echo "============================================================"
echo ""
echo "Starting Backend API and Frontend Dashboard..."
echo ""

# Get script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Start Backend in background
echo "[1/2] Starting Backend API on http://localhost:5000"
python backend/app.py &
BACKEND_PID=$!

# Wait 3 seconds for backend to start
sleep 3

# Start Frontend
echo "[2/2] Starting Frontend Dashboard on http://localhost:3000"
cd frontend
npm start &
FRONTEND_PID=$!

echo ""
echo "============================================================"
echo "  Both services are running!"
echo "============================================================"
echo ""
echo "  Backend API:  http://localhost:5000  (PID: $BACKEND_PID)"
echo "  Frontend:     http://localhost:3000  (PID: $FRONTEND_PID)"
echo ""
echo "  Press Ctrl+C to stop both services"
echo "============================================================"

# Wait for user interrupt
wait
