#!/usr/bin/env python3
"""
Force Railway Complete Rebuild
This script makes significant changes to force Railway to rebuild everything
"""

import os
import subprocess

def update_railway_toml():
    """Update railway.toml with new build configuration"""
    content = """[build]
builder = "DOCKERFILE"

# Force complete rebuild - ROLES FIX
# Build timestamp: 2025-04-25T19:00:00Z
# Issue: Railway serving cached frontend with old roles
# Solution: Complete rebuild with new configuration

[deploy]
healthcheckPath = "/api/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
"""
    
    with open('railway.toml', 'w') as f:
        f.write(content)
    print("✅ Updated railway.toml with new build configuration")

def update_dockerfile():
    """Update Dockerfile with cache-busting changes"""
    content = """# Use Node.js base image for frontend build
# Build timestamp: 2025-04-25-19-00 - ROLES FIX REBUILD
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy all frontend files
COPY frontend/ ./

# Clear any existing cache
RUN rm -rf node_modules/.cache || true
RUN rm -rf dist || true

# Install frontend dependencies and build
RUN npm install --legacy-peer-deps --no-cache
RUN chmod +x node_modules/.bin/*
RUN npm run build

# Use Python base image for backend
FROM python:3.10-slim

# Create and set working directory
RUN mkdir -p /app
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
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
"""
    
    with open('Dockerfile', 'w') as f:
        f.write(content)
    print("✅ Updated Dockerfile with cache-busting and production optimizations")

def update_vite_config():
    """Update Vite config to ensure production build"""
    content = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    // Force rebuild by changing build config
    minify: 'terser',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: undefined
      }
    }
  },
  server: {
    host: true,
    port: 5173,
    proxy: process.env.NODE_ENV === 'production' ? undefined : {
      '/api': {
        target: 'http://127.0.0.1:5007',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  define: {
    __APP_VERSION__: '"2025-04-25-19-00-ROLES-FIX"'
  }
})
"""
    
    with open('frontend/vite.config.ts', 'w') as f:
        f.write(content)
    print("✅ Updated Vite config with production build optimizations")

def main():
    print("🔥 Forcing Railway Complete Rebuild for Roles Fix")
    print("=" * 60)
    
    # Update configuration files
    update_railway_toml()
    update_dockerfile()
    update_vite_config()
    
    print("\n📋 Changes Made:")
    print("1. Updated railway.toml with new deployment configuration")
    print("2. Updated Dockerfile with cache-busting and --no-cache flags")
    print("3. Updated Vite config with production build optimizations")
    print("4. Added build timestamps and version identifiers")
    
    print("\n🚀 Next Steps:")
    print("1. Git add, commit, and push changes")
    print("2. Railway will perform complete rebuild")
    print("3. Frontend should serve latest role definitions")
    
    # Git commands
    print("\n🔧 Executing Git commands...")
    
    try:
        subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
        print("✅ Git add completed")
        
        subprocess.run(['git', 'commit', '-m', 'FORCE COMPLETE RAILWAY REBUILD - Roles fix with cache-busting'], 
                      check=True, capture_output=True)
        print("✅ Git commit completed")
        
        subprocess.run(['git', 'push', 'origin', 'main'], check=True, capture_output=True)
        print("✅ Git push completed")
        
        print("\n🎯 Railway will now perform complete rebuild.")
        print("⏱️  Wait 2-3 minutes for deployment to complete.")
        print("🔄 Then test the roles dropdown on Railway.")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git command failed: {e}")

if __name__ == "__main__":
    main()
