# chats Setup Guide

Complete step-by-step guide to set up the chats project.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Meta Developer Setup](#meta-developer-setup)
3. [WhatsApp Business Setup](#whatsapp-business-setup)
4. [Local Development Setup](#local-development-setup)
5. [Docker Setup](#docker-setup)
6. [Database Setup](#database-setup)
7. [Testing the Setup](#testing-the-setup)
8. [Troubleshooting](#troubleshooting)

---

## 1. Prerequisites

### Required Software

- **Docker**: Version 24.0 or higher
- **Docker Compose**: Version 2.0 or higher
- **Git**: For cloning the repository
- **Node.js**: Version 20 or higher (optional, for local dev)
- **Python**: Version 3.11 or higher (optional, for local dev)

### Installation

#### On Ubuntu/Debian:

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt-get install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

#### On macOS:

```bash
# Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop

# Verify installation
docker --version
docker compose version
```

#### On Windows:

1. Download Docker Desktop from https://www.docker.com/products/docker-desktop
2. Run the installer
3. Restart your computer
4. Verify installation in PowerShell:

```powershell
docker --version
docker compose version
```

---

## 2. Meta Developer Setup

### Create Meta App

1. **Go to Meta for Developers**
   - Visit: https://developers.facebook.com/
   - Click "Get Started" or "My Apps"

2. **Create New App**
   - Click "Create App"
   - Select "Business" type
   - Enter app name (e.g., "chats Integration")
   - Enter contact email
   - Click "Create App"

3. **Add Products**
   - Click "Add Product"
   - Add **Instagram**
   - Add **Messenger**
   - Add **WhatsApp** (if available)

### Configure Instagram

1. **Instagram Settings**
   - Go to Instagram > Settings
   - Note your App ID and App Secret
   - Add OAuth Redirect URI: `http://localhost:8000/api/platforms/callback`

2. **Instagram Permissions**
   - Request these permissions:
     - `instagram_basic`
     - `instagram_manage_messages`
     - `pages_show_list`
     - `pages_messaging`

3. **Configure Webhooks**
   - Go to Instagram > Webhooks
   - Callback URL: `https://your-domain.com/api/webhooks/instagram`
   - Verify Token: (use value from your `.env` file)
   - Subscribe to fields:
     - `messages`
     - `messaging_seen`

### Configure Messenger

1. **Messenger Settings**
   - Go to Messenger > Settings
   - Note your Page Access Token

2. **Messenger Permissions**
   - Request these permissions:
     - `pages_messaging`
     - `pages_manage_metadata`
     - `pages_show_list`

3. **Configure Webhooks**
   - Go to Messenger > Webhooks
   - Callback URL: `https://your-domain.com/api/webhooks/messenger`
   - Verify Token: (use value from your `.env` file)
   - Subscribe to fields:
     - `messages`
     - `messaging_reads`

### Get Credentials

After setup, collect these values:

```
META_APP_ID=your-app-id-here
META_APP_SECRET=your-app-secret-here
```

---

## 3. WhatsApp Business Setup

### Create WhatsApp Business Account

1. **Go to WhatsApp Business**
   - Visit: https://business.facebook.com/wa/manage/home/
   - Click "Get Started"

2. **Create Business Account**
   - Enter business name
   - Complete verification

3. **Set Up Phone Number**
   - Add a phone number
   - Verify the phone number
   - Note the **Phone Number ID**

4. **Get Access Token**
   - Go to API Setup
   - Generate a permanent access token
   - Note the **Business Account ID** and **Access Token**

5. **Configure Webhooks**
   - Webhook URL: `https://your-domain.com/api/webhooks/whatsapp`
   - Verify Token: (use value from your `.env` file)
   - Subscribe to:
     - `messages`
     - `message_status`

### Get Credentials

After setup, collect these values:

```
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
WHATSAPP_BUSINESS_ACCOUNT_ID=your-business-account-id
WHATSAPP_ACCESS_TOKEN=your-permanent-access-token
```

---

## 4. Local Development Setup

### Clone Repository

```bash
git clone <repository-url>
cd chats
```

### Configure Backend Environment

1. **Copy example environment file:**

```bash
cp backend/.env.example backend/.env
```

2. **Edit `backend/.env`:**

```bash
nano backend/.env  # or use your preferred editor
```

3. **Update the following values:**

```env
# Django Settings
SECRET_KEY=generate-a-random-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,backend

# Database (use these for Docker setup)
DATABASE_URL=postgresql://chats:chats_password@db:5432/chats_db

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Meta API (from Step 2)
META_APP_ID=your-meta-app-id
META_APP_SECRET=your-meta-app-secret
META_REDIRECT_URI=http://localhost:8000/api/platforms/callback

# WhatsApp (from Step 3)
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
WHATSAPP_BUSINESS_ACCOUNT_ID=your-business-account-id
WHATSAPP_ACCESS_TOKEN=your-whatsapp-access-token

# JWT
JWT_SECRET_KEY=generate-a-random-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Encryption Key (generate with command below)
ENCRYPTION_KEY=

# Webhook
WEBHOOK_VERIFY_TOKEN=generate-a-random-webhook-token
```

4. **Generate Encryption Key:**

```bash
# Run this command and copy the output to ENCRYPTION_KEY in .env
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Configure Frontend Environment

1. **Copy example environment file:**

```bash
cp frontend/.env.example frontend/.env
```

2. **Edit `frontend/.env`:**

```env
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws
```

---

## 5. Docker Setup

### Build and Start Services

```bash
# Build and start all services
docker-compose up -d

# This will start:
# - PostgreSQL database (port 5432)
# - Redis (port 6379)
# - Django backend (port 8000)
# - React frontend (port 5173)
# - Celery worker
# - Celery beat
```

### Verify Services are Running

```bash
# Check all services
docker-compose ps

# Expected output:
# NAME                  STATUS    PORTS
# chats_backend         Up        0.0.0.0:8000->8000/tcp
# chats_celery          Up
# chats_celery_beat     Up
# chats_db              Up        0.0.0.0:5432->5432/tcp
# chats_frontend        Up        0.0.0.0:5173->5173/tcp
# chats_redis           Up        0.0.0.0:6379->6379/tcp
```

### View Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f celery
```

---

## 6. Database Setup

### Run Migrations

```bash
# Run database migrations
docker-compose exec backend python manage.py migrate
```

### Create Superuser

```bash
# Create admin user
docker-compose exec backend python manage.py createsuperuser

# Enter email and password when prompted
```

### Verify Database Connection

```bash
# Connect to PostgreSQL
docker-compose exec db psql -U chats -d chats_db

# List tables
\dt

# Exit
\q
```

---

## 7. Testing the Setup

### Access Applications

1. **Frontend**: http://localhost:5173
2. **Backend API**: http://localhost:8000/api
3. **Admin Panel**: http://localhost:8000/admin

### Test Backend API

```bash
# Test health endpoint
curl http://localhost:8000/api/auth/me

# Should return 401 Unauthorized (expected without token)
```

### Test Frontend

1. Open browser to http://localhost:5173
2. You should see the chats dashboard
3. Navigate to different pages (Dashboard, Chats)

### Test Redis

```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Test Redis
127.0.0.1:6379> ping
PONG

# Exit
127.0.0.1:6379> exit
```

### Test Celery

```bash
# View Celery worker logs
docker-compose logs -f celery

# You should see:
# [tasks]
#   . apps.messages.tasks.sync_all_platforms
#   . apps.analytics.tasks.aggregate_daily_analytics
```

---

## 8. Troubleshooting

### Backend Won't Start

**Problem**: Backend container exits immediately

**Solution**:
```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Database not ready - wait for db health check
# 2. Missing dependencies - rebuild: docker-compose build backend
# 3. Migration errors - check DATABASE_URL in .env
```

### Database Connection Error

**Problem**: Cannot connect to database

**Solution**:
```bash
# Ensure database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Verify DATABASE_URL in backend/.env
# Should be: postgresql://chats:chats_password@db:5432/chats_db
```

### Frontend Build Error

**Problem**: Frontend won't build or start

**Solution**:
```bash
# Rebuild frontend without cache
docker-compose build frontend --no-cache

# Or delete node_modules and rebuild
docker-compose down
rm -rf frontend/node_modules
docker-compose up -d --build
```

### Redis Connection Error

**Problem**: Cannot connect to Redis

**Solution**:
```bash
# Check Redis status
docker-compose ps redis

# Restart Redis
docker-compose restart redis

# Verify REDIS_URL in backend/.env
# Should be: redis://redis:6379/0
```

### Port Already in Use

**Problem**: Port 5432, 6379, 8000, or 5173 already in use

**Solution**:
```bash
# Find process using port (example for 8000)
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>

# Or change port in docker-compose.yml
```

### Permission Denied

**Problem**: Permission denied errors when running Docker

**Solution**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and log back in
# Or use sudo with docker-compose commands
sudo docker-compose up -d
```

### Webhook Not Receiving Events

**Problem**: Meta webhooks not triggering

**Solution**:
1. Ensure your server is publicly accessible
2. Use ngrok for local testing:
   ```bash
   ngrok http 8000
   # Use ngrok URL in Meta webhook settings
   ```
3. Verify webhook token matches `.env` file
4. Check webhook subscriptions in Meta app

---

## Next Steps

1. **Configure Webhooks**: Set up public URL using ngrok or deploy to production
2. **Test Platform Connections**: Connect Instagram, Messenger, and WhatsApp accounts
3. **Send Test Messages**: Send messages from connected platforms
4. **Monitor Logs**: Watch backend logs for webhook events
5. **Customize**: Modify frontend components and backend logic as needed

For detailed implementation phases, see `PROJECT_PLAN.md`.

---

## Additional Resources

- **Django Documentation**: https://docs.djangoproject.com/
- **React Documentation**: https://react.dev/
- **Meta Graph API**: https://developers.facebook.com/docs/graph-api
- **WhatsApp Business API**: https://developers.facebook.com/docs/whatsapp
- **Docker Documentation**: https://docs.docker.com/

---

## Support

If you encounter issues not covered in this guide:

1. Check `PROJECT_PLAN.md` for architecture details
2. Review Docker logs: `docker-compose logs -f`
3. Open an issue on GitHub
