# CAHTS Production Deployment Guide

## Prerequisites

1. **Server Requirements**:
   - Ubuntu/Debian Linux server
   - Docker and Docker Compose installed
   - Ports 80 and 443 open in firewall
   - At least 2GB RAM, 20GB disk space

2. **Domain Configuration**:
   - `chats.forecommerce.co` → Your server IP (Frontend)
   - `chats.api.forecommerce.co` → Your server IP (Backend API)

## DNS Configuration

Configure your DNS records to point to your server:

```
Type    Name                        Value           TTL
A       chats.forecommerce.co       YOUR_SERVER_IP  300
A       chats.api.forecommerce.co   YOUR_SERVER_IP  300
```

Verify DNS propagation:
```bash
dig chats.forecommerce.co
dig chats.api.forecommerce.co
```

## SSL Certificates

### Current Status
Self-signed SSL certificates have been generated for testing. These will show security warnings in browsers.

### Get Production SSL Certificates (Let's Encrypt)

**Option 1: Manual Certbot**
```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot

# Obtain certificates
sudo certbot certonly --standalone -d chats.forecommerce.co
sudo certbot certonly --standalone -d chats.api.forecommerce.co

# Copy to project directory
sudo cp /etc/letsencrypt/live/chats.forecommerce.co/fullchain.pem ./nginx/ssl/chats.forecommerce.co/
sudo cp /etc/letsencrypt/live/chats.forecommerce.co/privkey.pem ./nginx/ssl/chats.forecommerce.co/
sudo cp /etc/letsencrypt/live/chats.api.forecommerce.co/fullchain.pem ./nginx/ssl/chats.api.forecommerce.co/
sudo cp /etc/letsencrypt/live/chats.api.forecommerce.co/privkey.pem ./nginx/ssl/chats.api.forecommerce.co/

# Set permissions
chmod 644 ./nginx/ssl/*/fullchain.pem
chmod 600 ./nginx/ssl/*/privkey.pem
```

**Option 2: Using Certbot Docker**
```bash
# Stop nginx temporarily
docker-compose -f docker-compose.prod.yml stop nginx

# Run certbot
docker run -it --rm \
  -v $(pwd)/nginx/ssl:/etc/letsencrypt \
  -p 80:80 -p 443:443 \
  certbot/certbot certonly --standalone \
  --email your-email@example.com \
  --agree-tos \
  -d chats.forecommerce.co \
  -d chats.api.forecommerce.co

# Restart nginx
docker-compose -f docker-compose.prod.yml start nginx
```

## Environment Configuration

### 1. Backend Environment
Edit `backend/.env`:
```bash
# Production settings
DEBUG=False
SECRET_KEY=your-very-secure-random-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,backend,chats.api.forecommerce.co

# Database
DATABASE_URL=postgresql://chats:CHANGE_THIS_PASSWORD@db:5432/chats_db

# Redis
REDIS_URL=redis://:CHANGE_THIS_PASSWORD@redis:6379/0
CELERY_BROKER_URL=redis://:CHANGE_THIS_PASSWORD@redis:6379/0
CELERY_RESULT_BACKEND=redis://:CHANGE_THIS_PASSWORD@redis:6379/0

# Meta/Facebook
META_APP_ID=your-meta-app-id
META_APP_SECRET=your-meta-app-secret
META_REDIRECT_URI=https://chats.forecommerce.co/oauth/callback

# WhatsApp
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
WHATSAPP_BUSINESS_ACCOUNT_ID=your-business-account-id
WHATSAPP_ACCESS_TOKEN=your-whatsapp-access-token

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ALLOWED_ORIGINS=https://chats.forecommerce.co

# Encryption Key (generate new one!)
# python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=your-generated-encryption-key

# Webhook
WEBHOOK_VERIFY_TOKEN=your-webhook-verify-token
```

### 2. Frontend Environment
Edit `frontend/.env`:
```bash
VITE_API_URL=https://chats.api.forecommerce.co/api
VITE_WS_URL=wss://chats.api.forecommerce.co/ws
```

### 3. Docker Compose Environment
Create `.env` file in project root for docker-compose:
```bash
# PostgreSQL
POSTGRES_DB=chats_db
POSTGRES_USER=chats
POSTGRES_PASSWORD=CHANGE_THIS_PASSWORD

# Redis
REDIS_PASSWORD=CHANGE_THIS_PASSWORD
```

## Deployment Steps

### 1. Build and Start Services
```bash
cd /home/admin/Documents/Project/CAHTS

# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 2. Initialize Database
```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser

# Collect static files (already done on startup, but can run manually)
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

### 3. Verify Services
```bash
# Check all containers are running
docker-compose -f docker-compose.prod.yml ps

# Test backend API
curl https://chats.api.forecommerce.co/api/

# Test frontend
curl https://chats.forecommerce.co/
```

## Service Management

### Start Services
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Stop Services
```bash
docker-compose -f docker-compose.prod.yml down
```

### Restart Specific Service
```bash
docker-compose -f docker-compose.prod.yml restart backend
docker-compose -f docker-compose.prod.yml restart nginx
```

### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f nginx
docker-compose -f docker-compose.prod.yml logs -f celery
```

### Execute Commands in Container
```bash
# Django shell
docker-compose -f docker-compose.prod.yml exec backend python manage.py shell

# Database shell
docker-compose -f docker-compose.prod.yml exec backend python manage.py dbshell

# Bash shell
docker-compose -f docker-compose.prod.yml exec backend bash
```

## SSL Certificate Renewal

Let's Encrypt certificates expire after 90 days. Set up auto-renewal:

```bash
# Test renewal
sudo certbot renew --dry-run

# Add to crontab
sudo crontab -e
```

Add this line for automatic renewal twice daily:
```
0 0,12 * * * certbot renew --quiet --post-hook "cd /home/admin/Documents/Project/CAHTS && docker-compose -f docker-compose.prod.yml restart nginx"
```

## Monitoring

### Check System Resources
```bash
# Container resource usage
docker stats

# Disk usage
docker system df
```

### Application Health
```bash
# Check backend health
curl https://chats.api.forecommerce.co/api/health/

# Check websocket
wscat -c wss://chats.api.forecommerce.co/ws/
```

## Backup

### Database Backup
```bash
# Create backup
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U chats chats_db > backup_$(date +%Y%m%d).sql

# Restore backup
docker-compose -f docker-compose.prod.yml exec -T db psql -U chats chats_db < backup_20251015.sql
```

### Full Backup
```bash
# Backup volumes
docker run --rm \
  -v chats_postgres_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/postgres_data_$(date +%Y%m%d).tar.gz -C /data .

docker run --rm \
  -v chats_redis_data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/redis_data_$(date +%Y%m%d).tar.gz -C /data .
```

## Troubleshooting

### Nginx Won't Start
```bash
# Check nginx configuration
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Check logs
docker-compose -f docker-compose.prod.yml logs nginx
```

### Backend Connection Issues
```bash
# Check if backend is running
docker-compose -f docker-compose.prod.yml ps backend

# Check backend logs
docker-compose -f docker-compose.prod.yml logs backend

# Test database connection
docker-compose -f docker-compose.prod.yml exec backend python manage.py dbshell
```

### WebSocket Not Working
```bash
# Check redis connection
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping

# Check channels layer
docker-compose -f docker-compose.prod.yml exec backend python manage.py shell
>>> from channels.layers import get_channel_layer
>>> channel_layer = get_channel_layer()
>>> await channel_layer.send("test", {"type": "test.message"})
```

### Celery Tasks Not Running
```bash
# Check celery worker
docker-compose -f docker-compose.prod.yml logs celery

# Check celery beat
docker-compose -f docker-compose.prod.yml logs celery-beat

# Restart celery
docker-compose -f docker-compose.prod.yml restart celery celery-beat
```

## Security Checklist

- [ ] Changed all default passwords in `.env` files
- [ ] Set `DEBUG=False` in backend `.env`
- [ ] Generated new `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Generated `ENCRYPTION_KEY` using Fernet
- [ ] Configured proper SSL certificates (not self-signed)
- [ ] Configured firewall to only allow ports 80, 443, and 22
- [ ] Set up regular database backups
- [ ] Configured Meta/Facebook app with correct OAuth redirect URI
- [ ] Set up monitoring and alerts
- [ ] Reviewed and updated `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`

## Meta/Facebook App Configuration

1. Go to https://developers.facebook.com/apps/
2. Create or select your app
3. Add Instagram and Messenger products
4. Configure OAuth redirect URI:
   - Add: `https://chats.forecommerce.co/oauth/callback`
5. Set up webhook callback URL:
   - URL: `https://chats.api.forecommerce.co/api/webhooks/meta/`
   - Verify token: (use value from `WEBHOOK_VERIFY_TOKEN` in `.env`)
6. Subscribe to webhook events:
   - messages
   - messaging_postbacks
   - message_deliveries
   - message_reads

## Support

For issues or questions:
- Check logs: `docker-compose -f docker-compose.prod.yml logs -f`
- Review Django debug.log: `docker-compose -f docker-compose.prod.yml exec backend tail -f debug.log`
- Check nginx error log: `docker-compose -f docker-compose.prod.yml exec nginx tail -f /var/log/nginx/error.log`
