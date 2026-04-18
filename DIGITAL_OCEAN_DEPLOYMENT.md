# DigitalOcean Deployment Guide for e-POM

## Overview
Deploy the e-POM application to DigitalOcean App Platform with PostgreSQL database.

## Prerequisites
- DigitalOcean account
- GitHub repository with the e-POM code
- Domain name (optional)

## Step 1: Set Up DigitalOcean Database

1. **Create PostgreSQL Database**
   - Go to DigitalOcean Dashboard
   - Click "Create" > "Databases" > "PostgreSQL"
   - Choose:
     - **Database Cluster**: PostgreSQL (latest version)
     - **Region**: Closest to your users
     - **Plan**: Basic (or higher for production)
     - **Node Size**: 1 vCPU, 1 GB RAM (minimum)
     - **Storage**: 10 GB (minimum)
     - **Database Name**: `epom_db`
     - **User**: `epom_user`
   - Click "Create Database Cluster"

2. **Get Database Connection Details**
   - Once created, click on the database
   - Go to "Connection" tab
   - Copy the **Connection String** (looks like: `postgresql://epom_user:password@host:port/epom_db`)

## Step 2: Deploy App to DigitalOcean

1. **Create New App**
   - Go to DigitalOcean Dashboard
   - Click "Create" > "Apps" > "From Source"
   - Connect your GitHub repository
   - Select the `epom` repository
   - Choose the `main` branch

2. **Configure App Settings**
   - **App Name**: `epom-app`
   - **Region**: Same as your database
   - **Plan**: Basic (or higher for production)
   - **Build Command**: `cd frontend && npm install && npm run build && cd ..`
   - **Run Command**: `gunicorn "app:app"`
   - **HTTP Port**: `8080`

3. **Set Environment Variables**
   - Go to "Components" > "Settings" > "Environment Variables"
   - Add these variables:
     ```
     DATABASE_URL=postgresql://epom_user:password@host:port/epom_db
     JWT_SECRET_KEY=your-super-secret-jwt-key-here
     FLASK_ENV=production
     NODE_ENV=production
     ```

4. **Add Database Connection**
   - Go to "Components" > "Settings" > "Components"
   - Click "Add Component" > "Database"
   - Select your PostgreSQL database
   - This will automatically add the `DATABASE_URL` environment variable

## Step 3: Update App Configuration

The app is already configured for DigitalOcean deployment. Key files:

### `.do/app.yaml` (Create this file)
```yaml
name: epom-app
services:
- name: web
  source_dir: /
  github:
    repo: amadoujawo1/epom
    branch: main
  run_command: gunicorn "app:app"
  environment_slug: python-3.10
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: FLASK_ENV
    value: production
  - key: JWT_SECRET_KEY
    value: your-super-secret-jwt-key-here
  http_port: 8080
  routes:
  - path: /
```

### `Procfile` (Already exists)
```
web: gunicorn "app:app"
```

### `requirements.txt` (Already exists)
```
flask
flask-cors
flask-sqlalchemy
cryptography
flask-jwt-extended
python-dotenv
bcrypt
gunicorn
pymysql
psycopg2-binary
```

## Step 4: Deploy and Test

1. **Deploy the App**
   - Click "Create Resources"
   - Wait for deployment to complete (2-5 minutes)

2. **Test the Application**
   - Visit the provided URL
   - Test login with:
     - Username: `admin`
     - Password: `admin123`

3. **Verify Database**
   - Check DigitalOcean database dashboard
   - Verify tables were created automatically

## Step 5: Configure Custom Domain (Optional)

1. **Add Domain**
   - Go to App Settings > Networking
   - Click "Add Domain"
   - Enter your domain name

2. **Update DNS**
   - DigitalOcean will provide DNS records
   - Add these to your domain registrar

## Environment Variables

### Required Variables
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Strong secret key for JWT tokens
- `FLASK_ENV`: Set to `production`

### Optional Variables
- `NODE_ENV`: Set to `production`
- `ENCRYPTION_KEY`: Custom encryption key (32 bytes)

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify DATABASE_URL is correct
   - Check database is running
   - Ensure firewall allows connections

2. **Build Failed**
   - Check frontend build works locally
   - Verify all dependencies in requirements.txt
   - Check for syntax errors

3. **App Not Starting**
   - Check Procfile format
   - Verify gunicorn command
   - Check application logs

### Debug Commands

```bash
# Check app logs
doctl apps logs <app-id>

# Check database connection
curl https://your-app-url.digitaloceanapp.com/api/test-db

# Force database setup
curl -X POST https://your-app-url.digitaloceanapp.com/api/setup-database
```

## Production Considerations

### Security
- Use strong JWT_SECRET_KEY
- Enable HTTPS (automatic on DigitalOcean)
- Set up database firewall
- Monitor app logs

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

- **App Platform**: $5-20/month (Basic plan)
- **PostgreSQL**: $15-50/month (Basic plan)
- **Total**: $20-70/month

## Support

- DigitalOcean Documentation: https://docs.digitalocean.com
- App Platform Guide: https://docs.digitalocean.com/products/app-platform
- PostgreSQL Guide: https://docs.digitalocean.com/products/databases/postgresql
