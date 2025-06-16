@echo off
REM Production deployment script for Bimbo Hunter
echo 🚀 Starting production deployment...

REM Step 1: Build the React frontend
echo 📦 Building React frontend...
cd client
call npm run build
if %errorlevel% neq 0 (
    echo ❌ Frontend build failed!
    pause
    exit /b 1
)
cd ..

echo ✅ Frontend build completed successfully!

REM Step 2: Start the production server
echo 🌐 Starting production server...
echo 📍 Server will be available at: http://localhost:5000
echo 🛑 Press Ctrl+C to stop the server
echo.
echo ✅ Production build deployment successful!
echo 🚀 Opening browser...
start http://localhost:5000

python app.py
pause
