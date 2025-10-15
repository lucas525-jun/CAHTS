# chats - Cross-Platform Chat Aggregation System
## Comprehensive Project Plan

### Project Overview
A unified dashboard for managing Instagram, Messenger, and WhatsApp messages with real-time synchronization, analytics, and multi-platform authentication.

---

## 1. Current State Analysis

### Existing Frontend (React + Vite + TypeScript)
- **Framework**: React 18.3 with Vite
- **UI Library**: Radix UI + Tailwind CSS (shadcn/ui components)
- **State Management**: TanStack Query
- **Routing**: React Router v6
- **Current Pages**:
  - Dashboard: Shows message statistics and weekly volume charts
  - Chats: Unified chat interface with platform filtering
  - Components: PlatformSelector, MessageList, StatsPanel, Navigation

### Current Limitations
- Using mock data (`@/data/mockData`)
- No backend integration
- No authentication system
- No real-time message sync
- No API endpoints

---

## 2. Architecture Design

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│              (React + Vite + TypeScript)                     │
│                    Port: 5173 (dev)                          │
└──────────────────┬──────────────────────────────────────────┘
                   │ REST API + WebSocket
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                      Django Backend                          │
│           (Django REST Framework + Channels)                 │
│                    Port: 8000                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  • REST API Endpoints                                │  │
│  │  • OAuth 2.0 Authentication                          │  │
│  │  • Webhook Handlers                                  │  │
│  │  • WebSocket Server (Django Channels)               │  │
│  │  • Background Tasks (Celery)                         │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┬──────────────┐
        ▼                     ▼              ▼
┌───────────────┐   ┌──────────────┐   ┌──────────┐
│  PostgreSQL   │   │    Redis     │   │  Meta    │
│   Database    │   │   (Cache +   │   │  Graph   │
│   Port: 5432  │   │   Channels)  │   │   API    │
│               │   │  Port: 6379  │   │          │
└───────────────┘   └──────────────┘   └──────────┘
```

---

## 3. Technology Stack

### Backend
- **Framework**: Django 5.0+
- **API**: Django REST Framework 3.14+
- **WebSocket**: Django Channels 4.0+
- **Task Queue**: Celery 5.3+
- **API Integration**: requests, python-social-auth
- **Database ORM**: Django ORM

### Frontend (Existing)
- **Framework**: React 18.3
- **Build Tool**: Vite 5.4
- **UI**: Radix UI + Tailwind CSS
- **HTTP Client**: TanStack Query + Axios/Fetch
- **WebSocket**: WebSocket API or Socket.io-client

### Infrastructure
- **Database**: PostgreSQL 15+
- **Cache & Message Broker**: Redis 7+
- **Container**: Docker + Docker Compose
- **Reverse Proxy**: Nginx (optional, for production)

### External APIs
- **Instagram**: Meta Graph API v18+
- **Messenger**: Meta Graph API v18+
- **WhatsApp**: WhatsApp Business API (Cloud API)

---

## 4. Database Schema Design

### Tables/Models

#### 1. User
```python
- id (UUID, primary key)
- email (string, unique)
- username (string, unique)
- password_hash (string)
- created_at (timestamp)
- updated_at (timestamp)
```

#### 2. PlatformAccount
```python
- id (UUID, primary key)
- user_id (foreign key -> User)
- platform (enum: instagram, messenger, whatsapp)
- platform_user_id (string)
- platform_username (string)
- access_token (encrypted text)
- refresh_token (encrypted text, nullable)
- token_expires_at (timestamp, nullable)
- is_active (boolean)
- connected_at (timestamp)
- last_synced_at (timestamp)
```

#### 3. Message
```python
- id (UUID, primary key)
- platform_account_id (foreign key -> PlatformAccount)
- platform_message_id (string, unique)
- sender_id (string)
- sender_name (string)
- recipient_id (string)
- content (text)
- message_type (enum: text, image, video, audio, file)
- media_url (string, nullable)
- is_incoming (boolean)
- is_read (boolean)
- received_at (timestamp)
- created_at (timestamp)
- metadata (jsonb)
```

#### 4. Conversation
```python
- id (UUID, primary key)
- platform_account_id (foreign key -> PlatformAccount)
- platform_conversation_id (string)
- participant_id (string)
- participant_name (string)
- last_message_at (timestamp)
- unread_count (integer)
- is_archived (boolean)
- created_at (timestamp)
```

#### 5. Analytics
```python
- id (UUID, primary key)
- user_id (foreign key -> User)
- date (date)
- platform (enum: instagram, messenger, whatsapp)
- total_messages (integer)
- incoming_messages (integer)
- outgoing_messages (integer)
- unique_conversations (integer)
- created_at (timestamp)
```

#### 6. WebhookLog
```python
- id (UUID, primary key)
- platform (enum: instagram, messenger, whatsapp)
- event_type (string)
- payload (jsonb)
- processed (boolean)
- processed_at (timestamp, nullable)
- error_message (text, nullable)
- created_at (timestamp)
```

---

## 5. API Endpoints Design

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Refresh JWT token
- `GET /api/auth/me` - Get current user

### Platform Connections
- `GET /api/platforms/` - List connected platforms
- `POST /api/platforms/instagram/connect` - Initiate Instagram OAuth
- `POST /api/platforms/messenger/connect` - Initiate Messenger OAuth
- `POST /api/platforms/whatsapp/connect` - Connect WhatsApp Business
- `DELETE /api/platforms/{platform_id}` - Disconnect platform
- `POST /api/platforms/{platform_id}/sync` - Manually trigger sync

### Messages
- `GET /api/messages/` - List all messages (with filters)
- `GET /api/messages/{id}` - Get specific message
- `POST /api/messages/` - Send a message
- `PATCH /api/messages/{id}/read` - Mark as read
- `GET /api/conversations/` - List conversations
- `GET /api/conversations/{id}/messages` - Get messages in conversation

### Analytics
- `GET /api/analytics/daily` - Daily message volume
- `GET /api/analytics/platform` - Platform-wise breakdown
- `GET /api/analytics/export` - Export analytics (CSV/PDF)
- `GET /api/analytics/stats` - Quick stats (today's counts)

### Webhooks (Meta)
- `POST /api/webhooks/instagram` - Instagram webhook
- `POST /api/webhooks/messenger` - Messenger webhook
- `POST /api/webhooks/whatsapp` - WhatsApp webhook
- `GET /api/webhooks/{platform}` - Webhook verification

---

## 6. Real-Time Architecture (WebSocket)

### WebSocket Events

#### Client → Server
- `authenticate` - Authenticate WebSocket connection
- `subscribe_messages` - Subscribe to message updates
- `mark_read` - Mark message as read

#### Server → Client
- `new_message` - New message received
- `message_read` - Message read status updated
- `platform_connected` - New platform connected
- `platform_disconnected` - Platform disconnected
- `sync_started` - Sync process started
- `sync_completed` - Sync process completed

### WebSocket URL
```
ws://localhost:8000/ws/messages/
```

---

## 7. Meta API Integration

### Instagram Integration
- **OAuth Flow**: Authorization Code Flow
- **Permissions**: `instagram_basic`, `instagram_manage_messages`
- **Endpoints**:
  - GET `/me/conversations`
  - GET `/{conversation_id}/messages`
  - POST `/{conversation_id}/messages`
- **Webhooks**: `messages`, `messaging_seen`

### Messenger Integration
- **OAuth Flow**: Authorization Code Flow
- **Permissions**: `pages_messaging`, `pages_manage_metadata`
- **Endpoints**:
  - GET `/{page_id}/conversations`
  - GET `/{conversation_id}/messages`
  - POST `/me/messages`
- **Webhooks**: `messages`, `messaging_reads`

### WhatsApp Integration
- **Auth**: Permanent Access Token (Business API)
- **Setup**: Phone Number ID, WhatsApp Business Account ID
- **Endpoints**:
  - POST `/{phone_number_id}/messages`
  - GET `/{phone_number_id}/messages`
- **Webhooks**: `messages`, `message_status`

---

## 8. Docker Infrastructure

### Services

#### 1. frontend (React + Vite)
```yaml
- Build: Node 20 Alpine
- Port: 5173:5173 (dev), 80:80 (prod)
- Volumes: ./frontend:/app
- Environment: VITE_API_URL, VITE_WS_URL
```

#### 2. backend (Django)
```yaml
- Build: Python 3.11 Slim
- Port: 8000:8000
- Volumes: ./backend:/app
- Environment: DATABASE_URL, REDIS_URL, SECRET_KEY, META_APP_ID, META_APP_SECRET
- Depends: db, redis
```

#### 3. db (PostgreSQL)
```yaml
- Image: postgres:15-alpine
- Port: 5432:5432
- Volumes: postgres_data:/var/lib/postgresql/data
- Environment: POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
```

#### 4. redis
```yaml
- Image: redis:7-alpine
- Port: 6379:6379
- Volumes: redis_data:/data
```

#### 5. celery (Background Tasks)
```yaml
- Build: Same as backend
- Command: celery -A config worker -l info
- Depends: backend, redis
```

#### 6. celery-beat (Scheduled Tasks)
```yaml
- Build: Same as backend
- Command: celery -A config beat -l info
- Depends: backend, redis
```

---

## 9. Environment Variables

### Backend (.env)
```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://chats:chats_password@db:5432/chats_db

# Redis
REDIS_URL=redis://redis:6379/0

# Meta API
META_APP_ID=your-meta-app-id
META_APP_SECRET=your-meta-app-secret
META_REDIRECT_URI=http://localhost:8000/api/platforms/callback

# WhatsApp
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
WHATSAPP_BUSINESS_ACCOUNT_ID=your-business-account-id

# JWT
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws
```

---

## 10. Implementation Phases

### Phase 1: Infrastructure Setup (Current)
- [x] Analyze existing frontend
- [ ] Create Django project structure
- [ ] Set up Docker Compose
- [ ] Configure PostgreSQL and Redis
- [ ] Create Django models
- [ ] Set up Django REST Framework
- [ ] Configure Django Channels

### Phase 2: Authentication & Platform Connection
- [ ] Implement user authentication (JWT)
- [ ] Create OAuth flow for Instagram
- [ ] Create OAuth flow for Messenger
- [ ] Implement WhatsApp token management
- [ ] Create platform disconnect functionality
- [ ] Update frontend auth pages

### Phase 3: Webhook Integration
- [ ] Set up webhook endpoints
- [ ] Implement webhook verification
- [ ] Create Instagram webhook handler
- [ ] Create Messenger webhook handler
- [ ] Create WhatsApp webhook handler
- [ ] Set up webhook logging

### Phase 4: Message Sync & Real-Time
- [ ] Implement initial message fetch
- [ ] Create background sync tasks (Celery)
- [ ] Set up WebSocket connection
- [ ] Implement real-time message push
- [ ] Update frontend to use WebSocket
- [ ] Add message read/unread status

### Phase 5: API Endpoints & Frontend Integration
- [ ] Create REST API endpoints
- [ ] Implement message filtering
- [ ] Create conversation endpoints
- [ ] Update frontend services
- [ ] Replace mock data with API calls
- [ ] Add error handling and loading states

### Phase 6: Analytics & Export
- [ ] Implement analytics aggregation
- [ ] Create daily analytics task
- [ ] Build export functionality (CSV)
- [ ] Build export functionality (PDF)
- [ ] Update frontend analytics views
- [ ] Add export UI

### Phase 7: Testing & Deployment
- [ ] Write unit tests (backend)
- [ ] Write integration tests
- [ ] Test Docker deployment
- [ ] Create production Docker config
- [ ] Set up environment for production
- [ ] Documentation and deployment guide

---

## 11. Security Considerations

1. **Token Encryption**: Encrypt platform access tokens in database
2. **JWT Security**: Short-lived access tokens, refresh token rotation
3. **Webhook Verification**: Verify Meta webhook signatures
4. **CORS**: Restrict origins in production
5. **Rate Limiting**: Implement rate limiting on API endpoints
6. **Input Validation**: Validate all user inputs
7. **SQL Injection**: Use Django ORM parameterized queries
8. **XSS Protection**: Sanitize user-generated content
9. **Environment Variables**: Never commit secrets to git
10. **HTTPS**: Use HTTPS in production

---

## 12. Monitoring & Logging

1. **Application Logs**: Django logging configuration
2. **Webhook Logs**: Store all webhook payloads for debugging
3. **Error Tracking**: Integrate Sentry (optional)
4. **Performance Monitoring**: Django Debug Toolbar (dev)
5. **Database Monitoring**: pg_stat_statements
6. **Redis Monitoring**: Redis CLI monitoring

---

## 13. Future Enhancements

1. Message search functionality
2. Media file storage (S3/MinIO)
3. Conversation archiving
4. Message templates
5. Auto-replies and chatbots
6. Team collaboration (multiple users)
7. Role-based access control
8. Mobile app (React Native)
9. Email notifications
10. Advanced analytics and reporting

---

## 14. Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js 20+ (for local frontend dev)
- Python 3.11+ (for local backend dev)
- Meta Developer Account
- WhatsApp Business API access

### Quick Start
```bash
# Clone repository
git clone <repo-url>
cd chats

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit .env files with your credentials

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Access application
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# Admin: http://localhost:8000/admin
```

---

## 15. Project Timeline Estimate

- **Phase 1**: 1-2 days
- **Phase 2**: 3-4 days
- **Phase 3**: 2-3 days
- **Phase 4**: 3-4 days
- **Phase 5**: 2-3 days
- **Phase 6**: 2-3 days
- **Phase 7**: 2-3 days

**Total Estimated Time**: 15-22 days (3-4 weeks)

---

## Contact & Support

For issues or questions, please refer to:
- Meta Graph API Docs: https://developers.facebook.com/docs/graph-api
- WhatsApp Business API: https://developers.facebook.com/docs/whatsapp
- Django Channels: https://channels.readthedocs.io/
