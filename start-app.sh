#!/bin/bash

echo "Starting Bimbo Hunter application..."
echo

# Function to handle cleanup when script is terminated
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
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

# Start the frontend
echo "Starting React frontend..."
cd client && npm start &
FRONTEND_PID=$!

echo
echo "Both servers are now running."
echo "Press Ctrl+C to stop both servers."

# Wait for both processes to finish
wait $BACKEND_PID $FRONTEND_PID
