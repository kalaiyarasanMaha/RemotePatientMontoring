# Render Deployment Guide

## Issue Fixed
The deployment error `ModuleNotFoundError: No module named 'app'` occurred because Render was trying to run `uvicorn main:app` from the project root, but the `app` module wasn't in the Python path.

## Solution
Created the following files to fix the deployment:

### 1. **main.py** (Root Level)
- Entry point for Render deployment
- Adds the current directory to Python path
- Imports and exposes the FastAPI app

### 2. **render.yaml**
- Render deployment configuration
- Specifies Python 3.12 runtime
- Sets up database connection
- Configures environment variables

### 3. **build.sh**
- Build script that runs during deployment
- Installs dependencies
- Runs database migrations

## Deployment Steps

### Step 1: Push Code to GitHub
```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### Step 2: Create a Render Account
Visit https://render.com and sign up

### Step 3: Connect GitHub Repository
1. Go to Render Dashboard
2. Click "New" → "Web Service"
3. Select "Build and deploy from a Git repository"
4. Connect your GitHub account
5. Select the `RemotePatientMontoring` repository

### Step 4: Configure Web Service
1. **Name**: `patient-monitoring-platform`
2. **Environment**: Select your runtime
3. **Build Command**: `pip install -r requirements.txt && alembic upgrade head`
4. **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Instance Type**: Select appropriate plan
6. **Region**: Choose preferred region (e.g., Oregon)

### Step 5: Add Environment Variables
In Render Dashboard → Environment tab, add:

```
DATABASE_URL = your_postgresql_url
SECRET_KEY = your_secret_key
DEBUG = false
ENVIRONMENT = production
CORS_ORIGINS = https://your-frontend-domain.com
REDIS_URL = your_redis_url (if using Redis)
```

### Step 6: Add PostgreSQL Database (Optional)
If you want Render to manage the database:
1. Click "New" → "PostgreSQL"
2. Set database name: `patient_monitoring`
3. Copy the connection string to DATABASE_URL

### Step 7: Deploy
Click "Deploy" button. Render will:
1. Clone your repository
2. Install dependencies from requirements.txt
3. Run build.sh script
4. Start the FastAPI application
5. Assign a public URL

## Important Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host/dbname` |
| `SECRET_KEY` | JWT signing key (change this!) | Generate a secure random string |
| `DEBUG` | Debug mode | `false` (always for production) |
| `CORS_ORIGINS` | Allowed frontend origins | `https://yourapp.com` |
| `REDIS_URL` | Redis connection (for Celery tasks) | `redis://:password@host:port/0` |

## Database Setup

### Option 1: Use Render's PostgreSQL
- Create PostgreSQL instance in Render
- Connection string auto-populated
- Alembic runs automatically on deploy

### Option 2: Use External Database
- Set `DATABASE_URL` environment variable
- Make sure migrations are applied:
  ```bash
  alembic upgrade head
  ```

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'app'"
✅ **Fixed** - The root `main.py` file now handles this

### Error: "Database connection failed"
- Verify DATABASE_URL is correct
- Check database is accessible from Render's IP
- Ensure SSL mode matches your database requirements

### Error: "Port not found"
- Use `$PORT` environment variable (already in render.yaml)
- Don't hardcode port numbers

### Application starts but routes don't work
- Check CORS_ORIGINS includes your frontend domain
- Verify API endpoints are properly registered in app/main.py

## Monitoring & Logs

Access logs in Render Dashboard:
1. Select your service
2. Go to "Logs" tab
3. Real-time logs display here

## Health Check
Test your deployment with:
```bash
curl https://your-app-name.onrender.com/docs
```

Should return Swagger UI documentation if app is running correctly.

## Database Migrations on Production

To run migrations on Render:

### Option 1: During Build (Automatic)
Migrations run automatically via build.sh during each deploy

### Option 2: Manual Migration
SSH into Render instance and run:
```bash
alembic upgrade head
```

## Performance Tips

1. **Set WEB_CONCURRENCY**: Render auto-configures based on CPU
2. **Use Connection Pooling**: SQLAlchemy pooling is configured
3. **Cache Responses**: Add appropriate Cache-Control headers
4. **Monitor Database**: Check query performance in logs

## Security Checklist

- [ ] Change `SECRET_KEY` to a secure random value
- [ ] Set `DEBUG = false` in production
- [ ] Update CORS_ORIGINS to your domain only
- [ ] Use HTTPS (Render provides free SSL)
- [ ] Secure your database credentials
- [ ] Use environment variables for all secrets
- [ ] Enable database SSL/TLS connections

## Need Help?

- Render Docs: https://render.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- SQLAlchemy Docs: https://docs.sqlalchemy.org
- Alembic Docs: https://alembic.sqlalchemy.org
