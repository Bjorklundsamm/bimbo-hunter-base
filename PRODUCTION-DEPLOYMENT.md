# Production Deployment Guide

This guide explains how to build and deploy the Bimbo Hunter application in production mode.

## ✅ Status: Successfully Deployed!

The production build is working and has been tested successfully. The React frontend and Flask backend are integrated into a single server running on port 5000.

## Quick Start

### Option 1: Using the deployment scripts (Recommended)
- **Windows**: Double-click `deploy-production.bat`
- **Linux/Mac**: Run `./deploy-production.sh`

### Option 2: Manual deployment
1. Build the frontend: `npm run build`
2. Start the production server: `npm run start-production`

## What happens in production mode

1. **Frontend Build**: The React application is compiled into optimized static files in `client/build/`
2. **Single Server**: Only the Flask backend runs, serving both the API and the React frontend
3. **Static File Serving**: All static assets (CSS, JS, images) are served directly by Flask
4. **SPA Routing**: All non-API routes are handled by React Router

## Server Details

- **URL**: http://localhost:5000
- **API Endpoints**: http://localhost:5000/api/*
- **Frontend**: All other routes serve the React application

## File Structure in Production

```
client/build/           # React production build
├── static/            # CSS, JS, and other assets
├── thumbnails/        # Character thumbnails
├── Portraits/         # Character portraits
├── frames/           # Rarity frames
├── How To/           # Tutorial images
└── index.html        # Main React app entry point
```

## Differences from Development Mode

| Aspect | Development | Production |
|--------|-------------|------------|
| Servers | 2 (React dev server + Flask) | 1 (Flask only) |
| Port | Frontend: 3000, Backend: 5000 | Single: 5000 |
| Hot Reload | Yes | No |
| Optimization | No | Yes (minified, compressed) |
| Debug Mode | Yes | No |

## Troubleshooting

### Build Fails
- Ensure all dependencies are installed: `cd client && npm install`
- Check for TypeScript/ESLint errors in the build output

### Server Won't Start
- Check if port 5000 is available
- Ensure Python dependencies are installed: `pip install -r requirements.txt`
- Check the terminal output for specific error messages

### Static Files Not Loading
- Verify the build directory exists: `client/build/`
- Check file permissions
- Look for 404 errors in browser developer tools

## Performance Notes

- The production build is optimized for performance with minified code
- Images are automatically resized and compressed when uploaded
- Static files are served directly by Flask (consider nginx for high-traffic scenarios)
