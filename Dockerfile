# Use Node.js base image for frontend build
# Build timestamp: 2025-04-20-20-00
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy all frontend files
COPY frontend/ ./

# Install frontend dependencies and build
RUN npm install --legacy-peer-deps
RUN chmod +x node_modules/.bin/*
RUN npm run build

# Use Python base image for backend
FROM python:3.10-slim

# Create and set working directory
RUN mkdir -p /app
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy built frontend from frontend-builder stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Copy application code
COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 8080

# Start the application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
