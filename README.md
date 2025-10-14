# CAHTS - Cross-Platform Chat Aggregation System

A unified dashboard for managing Instagram, Messenger, and WhatsApp messages with real-time synchronization, analytics, and multi-platform authentication.

## Features

- **Unified Chat Interface**: Single dashboard to view messages from Instagram, Messenger, and WhatsApp
- **Multi-Platform Authentication**: OAuth 2.0 for Instagram & Messenger, API tokens for WhatsApp
- **Real-Time Sync**: WebSocket-based real-time message updates
- **Analytics Dashboard**: Daily/weekly message volume with platform breakdown
- **Message Management**: Read/unread status, conversation threads
- **Export Functionality**: Export analytics to CSV/PDF
- **Dockerized**: Complete Docker setup for easy deployment

## Tech Stack

### Backend
- Django 5.0 + Django REST Framework
- Django Channels (WebSocket support)
- Celery (Background tasks)
- PostgreSQL 15
- Redis 7

### Frontend
- React 18.3 + TypeScript
- Vite 5.4
- TanStack Query
- Radix UI + Tailwind CSS

### Infrastructure
- Docker + Docker Compose
- Nginx (Production)

## Project Structure

```
CAHTS/
├── backend/                    # Django backend
│   ├── config/                 # Django settings and configuration
│   ├── apps/
│   │   ├── accounts/           # User authentication
│   │   ├── platforms/          # Platform connections (IG, WA, Messenger)
│   │   ├── messages/           # Message handling and WebSocket
│   │   ├── analytics/          # Analytics and reporting
│   │   └── webhooks/           # Meta webhook handlers
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/         # UI components
│   │   ├── pages/              # Page components
│   │   ├── types/              # TypeScript types
│   │   └── App.tsx
│   ├── package.json
│   ├── Dockerfile
│   └── .env
├── docker-compose.yml          # Development setup
├── docker-compose.prod.yml     # Production setup
└── PROJECT_PLAN.md             # Detailed project plan
```

## Prerequisites

- Docker 24+ and Docker Compose 2+
- Meta Developer Account (for Instagram & Messenger)
- WhatsApp Business API Access
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd CAHTS
```

### 2. Configure Environment Variables

#### Backend Configuration

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and update the following:

```env
# Meta API Credentials
META_APP_ID=your-meta-app-id
META_APP_SECRET=your-meta-app-secret

# WhatsApp Configuration
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
WHATSAPP_BUSINESS_ACCOUNT_ID=your-business-account-id
WHATSAPP_ACCESS_TOKEN=your-whatsapp-access-token

# Generate encryption key with:
# python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=your-encryption-key

# Change these in production
SECRET_KEY=your-secure-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
WEBHOOK_VERIFY_TOKEN=your-webhook-verify-token
```

#### Frontend Configuration

```bash
cp frontend/.env.example frontend/.env
```

The default values should work for development:

```env
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws
```

### 3. Start Services with Docker

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 4. Initialize Database

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser
```

### 5. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api
- **Admin Panel**: http://localhost:8000/admin

## Development Setup

### Backend (Local)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Frontend (Local)

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Meta API Setup

### 1. Create Meta App

1. Go to https://developers.facebook.com/
2. Create a new app
3. Add Instagram, Messenger, and WhatsApp products
4. Configure app settings

### 2. Configure OAuth Redirect URI

Add to your Meta app settings:
```
http://localhost:8000/api/platforms/callback
```

### 3. Configure Webhooks

#### Instagram & Messenger Webhooks

1. Go to your app's Webhooks settings
2. Add callback URL: `http://your-domain.com/api/webhooks/instagram`
3. Add verify token from your `.env` file
4. Subscribe to: `messages`, `messaging_seen`

#### WhatsApp Webhooks

1. Go to WhatsApp settings
2. Add callback URL: `http://your-domain.com/api/webhooks/whatsapp`
3. Add verify token from your `.env` file
4. Subscribe to: `messages`, `message_status`

## Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f [service_name]

# Restart a service
docker-compose restart [service_name]

# Rebuild services
docker-compose up -d --build

# Execute command in container
docker-compose exec backend python manage.py [command]

# Access database
docker-compose exec db psql -U cahts -d cahts_db

# Access Redis CLI
docker-compose exec redis redis-cli
```

## Production Deployment

### 1. Update Environment Variables

- Set `DEBUG=False` in `backend/.env`
- Update `ALLOWED_HOSTS`
- Set strong `SECRET_KEY` and `JWT_SECRET_KEY`
- Update `CORS_ALLOWED_ORIGINS`
- Configure SSL certificates

### 2. Use Production Docker Compose

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Configure Domain and SSL

1. Point your domain to your server
2. Set up SSL certificates (Let's Encrypt recommended)
3. Update nginx configuration

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user

### Platform Connections
- `GET /api/platforms/` - List connected platforms
- `POST /api/platforms/instagram/connect` - Connect Instagram
- `POST /api/platforms/messenger/connect` - Connect Messenger
- `POST /api/platforms/whatsapp/connect` - Connect WhatsApp
- `DELETE /api/platforms/{id}` - Disconnect platform

### Messages
- `GET /api/messages/` - List messages
- `GET /api/messages/{id}` - Get message details
- `POST /api/messages/` - Send message
- `PATCH /api/messages/{id}/read` - Mark as read

### Analytics
- `GET /api/analytics/daily` - Daily analytics
- `GET /api/analytics/platform` - Platform breakdown
- `GET /api/analytics/export` - Export data

## WebSocket Connection

Connect to WebSocket for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/messages/');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('New message:', data);
};
```

## Troubleshooting

### Backend not starting

```bash
# Check logs
docker-compose logs backend

# Ensure database is ready
docker-compose exec db pg_isready -U cahts

# Run migrations manually
docker-compose exec backend python manage.py migrate
```

### Frontend not building

```bash
# Clear node_modules
rm -rf frontend/node_modules
docker-compose build frontend --no-cache
```

### WebSocket connection issues

- Ensure Redis is running: `docker-compose ps redis`
- Check Channels configuration in settings
- Verify CORS settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions:
- GitHub Issues: [Repository Issues URL]
- Documentation: See `PROJECT_PLAN.md` for detailed architecture

## Roadmap

- [ ] Complete Phase 1: Infrastructure Setup
- [ ] Complete Phase 2: Authentication & Platform Connection
- [ ] Complete Phase 3: Webhook Integration
- [ ] Complete Phase 4: Message Sync & Real-Time
- [ ] Complete Phase 5: API Endpoints & Frontend Integration
- [ ] Complete Phase 6: Analytics & Export
- [ ] Complete Phase 7: Testing & Deployment

See `PROJECT_PLAN.md` for detailed implementation phases.
