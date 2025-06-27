#!/bin/bash

echo "🚀 Starting Bimbo Hunter Development Environment"
echo "==============================================="
echo

# Function to handle cleanup when script is terminated
cleanup() {
    echo
    echo "🛑 Stopping all services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "✅ All services stopped."
    exit 0
}

# Set up trap to catch termination signals
trap cleanup SIGINT SIGTERM

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not detected. Activating..."
    # Prioritize Unix paths for Linux/EC2 compatibility
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo "✅ Virtual environment activated (Unix/Linux)."
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
        echo "✅ Virtual environment activated (Windows)."
    else
        echo "❌ Virtual environment not found. Please create one with: python3 -m venv venv"
        exit 1
    fi
    echo
fi

# Install/update Python dependencies
echo "📦 Checking Python dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Python dependencies up to date."
else
    echo "❌ Failed to install Python dependencies."
    exit 1
fi
echo

# Initialize database
echo "🗄️  Initializing database..."
python3 -c "from database import init_db; init_db()" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Database initialized."
else
    echo "❌ Failed to initialize database."
    exit 1
fi
echo

# Start the backend server
echo "🖥️  Starting Python backend..."
python3 app.py &
BACKEND_PID=$!

# Wait a moment for the backend to initialize
sleep 3

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start."
    exit 1
fi
echo "✅ Backend started successfully (PID: $BACKEND_PID)"

# Start the frontend
echo "🌐 Starting React frontend..."
(cd client && npm start) &
FRONTEND_PID=$!

echo
echo "🎉 Development environment is now running!"
echo "=========================================="
echo "📍 Frontend: http://localhost:3000"
echo "🖥️  Backend API: http://localhost:5000/api"
echo
echo "📊 Services Status:"
echo "   ✅ Backend (PID: $BACKEND_PID)"
echo "   ✅ Frontend (PID: $FRONTEND_PID)"
echo
echo "🛑 Press Ctrl+C to stop all services"
echo

# Wait for all processes to finish
wait $BACKEND_PID $FRONTEND_PID
