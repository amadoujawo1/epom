# Production Deployment Guide - ePOM

## Quick Start Options

### 1. Render (Recommended - Free Tier)
**Steps:**
1. Push your code to GitHub
2. Go to [render.com](https://render.com) and sign up
3. Click "New" -> "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name**: `epom-app`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r backend/requirements.txt && cd frontend && npm install && npm run build`
   - **Start Command**: `gunicorn --chdir backend "app:app"`
   - **Instance Type**: Free (starts at $0/month)

6. Add Environment Variables:
   ```
   DATABASE_URL=mysql+pymysql://user:password@your-host/epom_db
   JWT_SECRET_KEY=your-super-secret-jwt-key-generate-one
   FLASK_ENV=production
   ```

### 2. Railway (Very Easy)
**Steps:**
1. Go to [railway.app](https://railway.app)
2. Click "Deploy from GitHub repo"
3. Select your repository
4. Railway auto-detects from Procfile
5. Add environment variables in dashboard

### 3. Vercel (Serverless)
**Steps:**
1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel --prod`
3. Set environment variables in Vercel dashboard

### 4. Manual VPS (Full Control)
**Prerequisites:**
- Ubuntu 20.04+ or CentOS 8+
- Domain name (optional)

**Deployment Script:**
```bash
# Clone your repo
git clone <your-repo-url>
cd epom

# Run deployment script
chmod +x deploy.sh
./deploy.sh
```

**Or manual steps:**
```bash
# Install Python and dependencies
sudo apt update
sudo apt install python3 python3-pip nginx

# Install app dependencies
pip install -r backend/requirements.txt

# Build frontend
cd frontend
npm install
npm run build
cd ..

# Set environment variables
export DATABASE_URL="mysql+pymysql://user:password@localhost/epom_db"
export JWT_SECRET_KEY="your-secret-key"
export FLASK_ENV="production"

# Start with Gunicorn
gunicorn --chdir backend "app:app" -b 0.0.0.0:8000
```

## Environment Variables Required

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection | `mysql+pymysql://user:pass@host/db` |
| `JWT_SECRET_KEY` | JWT authentication secret | `super-secret-random-string` |
| `FLASK_ENV` | Environment mode | `production` |
| `ENCRYPTION_KEY` | Data encryption key | `32-character-secret-key` |

## Database Setup

### MySQL (Recommended for Production)
```sql
CREATE DATABASE epom_db;
CREATE USER 'epom_user'@'%' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON epom_db.* TO 'epom_user'@'%';
FLUSH PRIVILEGES;
```

### PostgreSQL (Alternative)
```sql
CREATE DATABASE epom_db;
CREATE USER epom_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE epom_db TO epom_user;
```

### SQLite (Simple/Development)
- No setup needed
- Automatically creates `epom_dev.db`

## SSL/HTTPS Setup

### With Let's Encrypt (Free SSL)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### With Cloudflare (Free)
1. Sign up for Cloudflare
2. Add your domain
3. Change nameservers to Cloudflare
4. Enable "Flexible SSL" in Cloudflare dashboard

## Performance Optimization

### Gunicorn Settings
```bash
gunicorn --chdir backend "app:app" \
  -b 0.0.0.0:8000 \
  --workers 4 \
  --worker-class gevent \
  --max-requests 1000 \
  --max-requests-jitter 100
```

### Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoring & Logging

### Application Monitoring
- Use [Sentry](https://sentry.io) for error tracking
- Use [Logtail](https://betterstack.com/logtail) for logs
- Set up Uptime monitoring with [UptimeRobot](https://uptimerobot.com)

### Health Checks
Your app includes `/api/health` endpoint for monitoring services.

## Security Checklist

- [ ] Set strong JWT_SECRET_KEY
- [ ] Use HTTPS in production
- [ ] Configure database firewall
- [ ] Set up regular backups
- [ ] Monitor access logs
- [ ] Update dependencies regularly

## Backup Strategy

### Database Backup (MySQL)
```bash
# Daily backup
mysqldump -u user -p epom_db > backup_$(date +%Y%m%d).sql

# Automated backup script
0 2 * * * /usr/bin/mysqldump -u user -ppassword epom_db > /backups/epom_$(date +\%Y\%m\%d).sql
```

### File Backup
- Backup `instance/` folder (contains SQLite database if used)
- Backup any uploaded files in `uploads/` directory

## Troubleshooting

### Common Issues
1. **Database Connection**: Ensure DATABASE_URL is correct
2. **Port Issues**: Make sure port 8000 is open
3. **Build Failures**: Check frontend build with `npm run build`
4. **Permission Errors**: Use proper file permissions

### Logs Location
- Application logs: Check platform logs (Render/Railway)
- Nginx logs: `/var/log/nginx/`
- Gunicorn logs: Console output or configured log file

## Support

For deployment issues:
1. Check platform-specific documentation
2. Review application logs
3. Test with `curl http://localhost:8000/api/health`
4. Verify environment variables

---

**Your app is production-ready! Choose the deployment option that best fits your needs.**
