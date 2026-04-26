# Use Node.js base image for frontend build
# Build timestamp: 2025-04-25-23-45 - FINAL-ROLLEDOWN-FIX
# Purpose: Fix rolldown native binding issue with Ubuntu base
FROM node:20 AS frontend-builder

WORKDIR /app/frontend

# Copy all frontend files
COPY frontend/ ./

# Install complete build environment for rolldown
RUN apt-get update && apt-get install -y \
    python3 \
    make \
    g++ \
    build-essential \
    libnss3-dev \
    libatk-bridge2.0-dev \
    libdrm2 \
    libxkbcommon-dev \
    libxcomposite-dev \
    libxdamage-dev \
    libxrandr-dev \
    libgbm-dev \
    libxss-dev \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for rolldown
ENV NODE_OPTIONS="--max-old-space-size=4096"
ENV npm_config_target_platform=linux
ENV npm_config_target_arch=x64
ENV npm_config_target_libc=libc

# Clear any existing cache aggressively
RUN rm -rf node_modules/.cache || true
RUN rm -rf dist || true
RUN rm -rf .vite || true
RUN rm -rf package-lock.json || true

# Install frontend dependencies with rolldown compatibility
RUN npm install --legacy-peer-deps --no-cache
RUN chmod +x node_modules/.bin/*

# Rebuild rolldown specifically if needed
RUN npm rebuild rolldown --no-cache || true

# Build with proper environment
RUN npm run build

# Add build timestamp to force changes
RUN echo "BUILD_TIMESTAMP=2025-04-25-23-45-FINAL-ROLLEDOWN-FIX" > /app/frontend/build-info.txt

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
ENV NODE_ENV=production

# Expose port
EXPOSE 8080

# Start the application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
