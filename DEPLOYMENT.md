# Production Deployment Plan - ePOM

The application has been prepared for production deployment. The frontend and backend are now integrated into a single deployable package served by the Flask backend.

## 🚀 Deployment steps

1.  **Environment Variables**:
    Ensure the following environment variables are set in your production host (e.g., Render, Railway, Vercel):
    - `DATABASE_URL`: Your production database URL (SQLite, MySQL, PostgreSQL, etc.). If not provided, it will fallback to SQLite.
    - `JWT_SECRET_KEY`: A strong, unique secret key for JWT authentication.
    - `FLASK_ENV`: Set to `production`.

2.  **Deployment Platform**:
    - **Render/Railway**: Simply connect your GitHub repository. The `Procfile` is already configured to start the application using Gunicorn.
    - **Manual VPS**:
        1. Install Python 3.10+
        2. Install requirements: `pip install -r backend/requirements.txt`
        3. Start the server: `gunicorn --chdir backend "app:app" -b 0.0.0.0:8000`

## 🛠 Completed Tasks

- [x] **Frontend Build**: Fixed TypeScript errors and generated production-ready assets in `frontend/dist`.
- [x] **Backend Integration**: Configured `backend/app.py` to serve the frontend from `frontend/dist` for all non-API routes.
- [x] **Production Server**: Added `gunicorn` to `backend/requirements.txt` for high-performance serving.
- [x] **Flexible Configuration**: Removed hardcoded SQLite overrides to allow for environment-based database configuration.
- [x] **Application Entry Point**: Created a `Procfile` for platforms that support it.

## 📁 Key Files Modified

- [backend/app.py](file:///c:/dev/web_apps/epom/backend/app.py): Updated Flask initialization and added a catch-all route for the frontend.
- [backend/requirements.txt](file:///c:/dev/web_apps/epom/backend/requirements.txt): Added `gunicorn`.
- [frontend/src/App.tsx](file:///c:/dev/web_apps/epom/frontend/src/App.tsx): Fixed unused variable errors preventing the build.
- [Procfile](file:///c:/dev/web_apps/epom/Procfile): Added deployment entry point.
