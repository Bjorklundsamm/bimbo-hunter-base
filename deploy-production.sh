#!/bin/bash

# Production deployment script for Bimbo Hunter
echo "🚀 Starting production deployment..."

# Step 1: Build the React frontend
echo "📦 Building React frontend..."
cd client
npm run build
if [ $? -ne 0 ]; then
    echo "❌ Frontend build failed!"
    exit 1
fi
cd ..

echo "✅ Frontend build completed successfully!"

# Step 2: Start the production server
echo "🌐 Starting production server..."
echo "📍 Server will be available at: http://localhost:5000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

python app.py
