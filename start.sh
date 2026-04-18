#!/bin/bash
# Railway startup script with database initialization

echo "Starting e-POM application..."

# Initialize database first
python init_db.py

# Start the application
gunicorn "app:app"
