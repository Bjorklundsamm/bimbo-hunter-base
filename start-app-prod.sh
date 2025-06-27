#!/bin/bash

echo "🚀 Starting Bimbo Hunter Production Environment"
echo "=============================================="
echo

# Function to handle cleanup when script is terminated
cleanup() {
    echo
    echo "🛑 Stopping all services..."
    kill $BACKEND_PID 2>/dev/null
    echo "✅ All services stopped."
    exit 0
}

# Set up trap to catch termination signals
trap cleanup SIGINT SIGTERM

# Check if production build exists
if [ ! -d "client/build" ]; then
    echo "❌ Production build not found. Building React app..."
    cd client && npm run build && cd ..
    if [ $? -ne 0 ]; then
        echo "❌ Failed to build React app. Exiting."
        exit 1
    fi
    echo "✅ React app built successfully."
    echo
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not detected. Activating..."
    # Check for Windows (Scripts) or Unix (bin) activation script
    if [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
        echo "✅ Virtual environment activated (Windows)."
    elif [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo "✅ Virtual environment activated (Unix)."
    else
        echo "❌ Virtual environment not found. Please create one with: python -m venv venv"
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



# Initialize database
echo "🗄️  Initializing database..."
python -c "from database import init_db; init_db()" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Database initialized."
else
    echo "❌ Failed to initialize database."
    exit 1
fi
echo

# Start the backend server (production mode)
echo "🖥️  Starting Python backend (production mode)..."
python app.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start."
    exit 1
fi
echo "✅ Backend started successfully (PID: $BACKEND_PID)"



echo
echo "🎉 Production environment is now running!"
echo "========================================"
echo "📍 Application URL: http://localhost:5000"
echo "🖥️  Backend API: http://localhost:5000/api"

echo
echo "📊 Services Status:"
echo "   ✅ Backend (PID: $BACKEND_PID)"
echo
echo "📝 Logs:"
echo "   Backend: Check terminal output above"
echo
echo "🛑 Press Ctrl+C to stop all services"
echo

# Wait for processes to finish
wait $BACKEND_PID
