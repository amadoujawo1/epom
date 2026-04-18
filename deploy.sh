#!/bin/bash
# Production Deployment Script for e-POM

echo "Deploying e-POM to production..."

# Install dependencies
pip install -r backend/requirements.txt

# Build frontend
cd frontend
npm install
npm run build
cd ..

# Set environment variables (replace with your values)
export DATABASE_URL="mysql+pymysql://user:password@localhost/epom_db"
export JWT_SECRET_KEY="your-super-secret-jwt-key-here"
export FLASK_ENV="production"

# Start the application
gunicorn --chdir backend "app:app" -b 0.0.0.0:8000 --workers 4
