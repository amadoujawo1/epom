#!/bin/bash
# Build script for Render deployment

echo "Starting build process..."

# Install Python dependencies
pip install -r requirements.txt

# Build frontend
echo "Building frontend..."
cd frontend
npm install
npm run build
cd ..

echo "Build completed successfully!"
