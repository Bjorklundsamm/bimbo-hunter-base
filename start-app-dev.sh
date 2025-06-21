#!/bin/bash

echo "Starting Bimbo Hunter application with Paimon..."
echo

# Function to handle cleanup when script is terminated
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID $PAIMON_PID 2>/dev/null
    exit 0
}

# Set up trap to catch termination signals
trap cleanup SIGINT SIGTERM

# Start the backend server
echo "Starting Python backend..."
python app.py &
BACKEND_PID=$!

# Wait a moment for the backend to initialize
sleep 2

# Start Paimon Discord bot
echo "Starting Paimon Discord bot..."
(cd "p(ai)mon" && python start_paimon.py) &
PAIMON_PID=$!

# Wait a moment for Paimon to initialize
sleep 2

# Start the frontend
echo "Starting React frontend..."
(cd client && npm start) &
FRONTEND_PID=$!

echo
echo "All servers are now running:"
echo "  - Backend API (Python)"
echo "  - Paimon Discord Bot"
echo "  - Frontend (React)"
echo "Press Ctrl+C to stop all servers."

# Wait for all processes to finish
wait $BACKEND_PID $FRONTEND_PID $PAIMON_PID
