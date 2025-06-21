#!/bin/bash

echo "🚀 Starting Bimbo Hunter Production Environment"
echo "=============================================="
echo

# Function to handle cleanup when script is terminated
cleanup() {
    echo
    echo "🛑 Stopping all services..."
    kill $BACKEND_PID $PAIMON_PID 2>/dev/null
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
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo "✅ Virtual environment activated."
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

# Install/update Paimon dependencies
echo "📦 Checking Paimon dependencies..."
pip install -r p\(ai\)mon/requirements.txt > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Paimon dependencies up to date."
else
    echo "❌ Failed to install Paimon dependencies."
    exit 1
fi
echo

# Check if Paimon is configured
if [ ! -f "p(ai)mon/.env" ]; then
    echo "⚠️  Paimon .env file not found."
    echo "📝 Please configure Paimon:"
    echo "   cp p\(ai\)mon/.env.example p\(ai\)mon/.env"
    echo "   # Edit .env with your Discord bot token and Anthropic API key"
    echo
    read -p "Continue without Paimon? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Exiting. Please configure Paimon first."
        exit 1
    fi
    SKIP_PAIMON=true
else
    echo "✅ Paimon configuration found."
    SKIP_PAIMON=false
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

# Temporarily skip Paimon startup
echo "⏭️  Skipping Paimon startup (temporarily disabled)."
PAIMON_PID=""

echo
echo "🎉 Production environment is now running!"
echo "========================================"
echo "📍 Application URL: http://localhost:5000"
echo "🖥️  Backend API: http://localhost:5000/api"
echo "🤖 Paimon: Temporarily disabled"
echo
echo "📊 Services Status:"
echo "   ✅ Backend (PID: $BACKEND_PID)"
echo "   ⏭️  Paimon (temporarily disabled)"
echo
echo "📝 Logs:"
echo "   Backend: Check terminal output above"
echo "   Paimon: Check p(ai)mon directory for logs"
echo
echo "🛑 Press Ctrl+C to stop all services"
echo

# Wait for backend process to finish
wait $BACKEND_PID
