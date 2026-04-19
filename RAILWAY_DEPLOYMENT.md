# Railway Deployment Guide for e-POM

## Overview
Deploy the e-POM application to Railway with PostgreSQL database.

## Prerequisites
- Railway account
- GitHub repository with e-POM code
- Railway CLI (optional but recommended)

## Step 1: Set Up Railway PostgreSQL Database

1. **Create PostgreSQL Database**
   - Go to Railway Dashboard
   - Click "New Project" → "Provision PostgreSQL"
   - Choose:
     - **Database Name**: `epom-db`
     - **Region**: Closest to your users
     - **Plan**: Free (for testing) or Pro (for production)
   - Click "Add PostgreSQL"

2. **Get Database Connection Details**
   - Once created, click on the database
   - Go to "Connect" tab
   - Copy the **Connection String** (looks like: `postgresql://postgres:password@host.railway.app:5432/railway`)

## Step 2: Deploy App to Railway

### Method 1: Using Railway CLI (Recommended)

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Deploy from GitHub**
   ```bash
   cd c:/dev/web_apps/epom
   railway up
   ```
   - Follow prompts to connect your GitHub repository
   - Select `epom` repository
   - Choose `main` branch

### Method 2: Using Railway Dashboard

1. **Create New Project**
   - Go to Railway Dashboard
   - Click "New Project" → "Deploy from GitHub repo"
   - Connect your GitHub account
   - Select `amadoujawo1/epom` repository
   - Choose `main` branch

2. **Configure Build Settings**
   - **Build Command**: `cd frontend && npm install && npm run build && cd ..`
   - **Start Command**: `gunicorn "app:app"`
   - **Port**: `8080`

3. **Create railway.toml file** (if not already exists)
   - Create `railway.toml` in root directory with:
   ```toml
   [build]
   builder = "NIXPACKS"
   
   [[build.env]]
   name = "NODE_VERSION"
   value = "18"
   
   [[build.env]]
   name = "PYTHON_VERSION"
   value = "3.10"
   ```

## Step 3: Configure Environment Variables

1. **Set Database URL**
   - In your Railway project → "Variables" → "New Variable"
   - Add:
     ```
     DATABASE_URL=postgresql://postgres:password@host.railway.app:5432/railway
     JWT_SECRET_KEY=your-super-secret-jwt-key-here
     FLASK_ENV=production
     ```

2. **Verify Variables**
   - Make sure `DATABASE_URL` starts with `postgresql://`
   - Ensure `JWT_SECRET_KEY` is a strong random string

## Step 4: Deploy and Test

1. **Trigger Deployment**
   - If using CLI: `railway up`
   - If using Dashboard: Click "Deploy"

2. **Wait for Deployment**
   - Railway will build and deploy (2-5 minutes)
   - Check deployment logs for any errors

3. **Test the Application**
   - Visit your Railway URL (provided in dashboard)
   - Test login with:
     - Username: `admin`
     - Password: `admin123`

4. **Initialize Database**
   - If login fails, visit: `https://your-app-url.railway.app/api/setup-database`
   - This will create tables and admin user

## Step 5: Verify Deployment

1. **Check Logs**
   - Go to Railway Dashboard → Your Project → "Logs"
   - Look for:
     - "🏠 Forcing SQLite database (bypassing environment variables)"
     - "✅ Tables created with metadata!"
     - "✅ Admin user created!"

2. **Check Database**
   - Go to Railway Dashboard → Your Database
   - Verify tables were created
   - Check for `users` table

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify `DATABASE_URL` is correct
   - Check database is running
   - Ensure proper PostgreSQL format

2. **Build Failed**
   - Check frontend build works locally
   - Verify all dependencies in requirements.txt
   - Check for syntax errors

3. **Login Failed**
   - Visit `/api/setup-database` to create tables
   - Check admin user was created
   - Verify JWT_SECRET_KEY is set

4. **App Not Starting**
   - Check Procfile format
   - Verify gunicorn command
   - Check application logs

### Debug Commands

```bash
# Check Railway logs
railway logs

# Check environment variables
railway variables

# Trigger manual database setup
curl -X POST https://your-app-url.railway.app/api/setup-database

# Test database connection
curl https://your-app-url.railway.app/api/test-db
```

## Current App Configuration

### Database Logic
- **Local Development**: SQLite (`sqlite:///epom_dev.db`)
- **Railway Deployment**: PostgreSQL (from `DATABASE_URL` environment variable)

### Key Files
- `app.py`: Main Flask application
- `models.py`: SQLAlchemy database models
- `requirements.txt`: Python dependencies
- `Procfile`: Railway start command
- `.env`: Local environment variables

### Environment Variables Required
```
DATABASE_URL=postgresql://user:password@host:port/dbname
JWT_SECRET_KEY=your-secret-key
FLASK_ENV=production
```

## Production Considerations

### Security
- Use strong JWT_SECRET_KEY
- Enable HTTPS (automatic on Railway)
- Monitor app logs
- Set up database backups

### Performance
- Scale up database if needed
- Add CDN for static assets
- Enable caching
- Monitor resource usage

### Backups
- Enable automatic database backups
- Regular app data backups
- Disaster recovery plan

## Cost Estimate

- **App Platform**: Free tier (starts at $0/month)
- **PostgreSQL**: Free tier (starts at $0/month)
- **Total**: $0/month for testing, $5-20/month for production

## Support

- Railway Documentation: https://docs.railway.app
- Railway CLI: https://docs.railway.app/develop/cli
- PostgreSQL Guide: https://docs.railway.app/guides/postgresql
