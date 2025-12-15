# Environment Variables Template for Render Deployment

## Copy these to your Render Dashboard → Environment Variables

### Database Configuration
```
DATABASE_URL=postgresql://username:password@host:port/database_name
```
Example:
```
DATABASE_URL=postgresql://user123:securepass@db.render.com:5432/patient_monitoring
```

### Security
```
SECRET_KEY=your-super-secret-key-generate-a-random-string-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Application Settings
```
DEBUG=false
ENVIRONMENT=production
APP_NAME=Remote Patient Monitoring Platform
APP_VERSION=1.0.0
```

### CORS Configuration
```
CORS_ORIGINS=https://your-frontend-domain.com,https://www.your-domain.com
```

### Redis Configuration (if using Celery)
```
REDIS_URL=redis://:password@redis-host:6379/0
```

### Alert Thresholds
```
HEART_RATE_ALERT_THRESHOLD_LOW=40
HEART_RATE_ALERT_THRESHOLD_HIGH=120
BLOOD_PRESSURE_SYSTOLIC_HIGH=140
BLOOD_PRESSURE_DIASTOLIC_HIGH=90
BLOOD_OXYGEN_LOW=92
TEMPERATURE_HIGH=38.0
```

## How to Generate SECRET_KEY

In Python terminal:
```python
import secrets
print(secrets.token_urlsafe(32))
```

Output example:
```
-qr8sXNx4pY_1-kL9mZw2aB3cD4eF5gH6iJ7kL8mN9oP0
```

## Steps to Add to Render

1. Go to your Render Web Service Dashboard
2. Click "Environment" tab
3. Click "Add Environment Variable"
4. Fill in each Key-Value pair
5. Click "Save Changes"
6. Service will redeploy automatically

## Security Notes

⚠️ **IMPORTANT:**
- Never commit real credentials to Git
- Use `.env` file locally (already in .gitignore)
- Regenerate SECRET_KEY for production
- Keep DATABASE_URL secure
- Use HTTPS for all frontend origins
- Always set DEBUG=false in production

## Database Connection Examples

### PostgreSQL on Render
```
DATABASE_URL=postgresql://user:pass@dpg-xxxxx.render.com/dbname
```

### PostgreSQL on AWS RDS
```
DATABASE_URL=postgresql://user:pass@rds-instance.xxxxx.amazonaws.com:5432/dbname
```

### PostgreSQL on Neon
```
DATABASE_URL=postgresql://user:pass@host.neon.tech/dbname?sslmode=require
```

### PostgreSQL Local (for testing)
```
DATABASE_URL=postgresql://localhost/patient_monitoring
```

## Verification

After deployment, verify variables are set:
1. Go to Service Logs
2. Should see successful startup messages
3. Check `/docs` endpoint loads without errors

## Troubleshooting

If app won't start:
- Check DATABASE_URL is correct
- Verify SECRET_KEY is set
- Ensure DEBUG=false
- Check CORS_ORIGINS includes your domain

If database migrations fail:
- Verify DATABASE_URL has correct credentials
- Check database exists and is accessible
- View logs for specific error message
