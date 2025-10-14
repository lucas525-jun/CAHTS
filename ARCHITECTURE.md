# CAHTS Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                           USER BROWSER                               │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │              React Frontend (Port 5173)                     │    │
│  │  • Dashboard (Analytics & Stats)                            │    │
│  │  • Chats (Unified Message Interface)                        │    │
│  │  • Platform Settings                                        │    │
│  └────────────┬──────────────────────────────────┬─────────────┘    │
└───────────────┼──────────────────────────────────┼──────────────────┘
                │ HTTP/REST API                    │ WebSocket
                │                                  │
                ▼                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Django Backend (Port 8000)                       │
│                                                                       │
│  ┌──────────────────────┐  ┌──────────────────────────────────┐   │
│  │   REST API Endpoints │  │    WebSocket Server              │   │
│  │   (Django REST FW)   │  │    (Django Channels)             │   │
│  └──────────────────────┘  └──────────────────────────────────┘   │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Authentication Layer                             │  │
│  │              (JWT + Session)                                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  ┌──────────┐  │
│  │  accounts   │  │  platforms  │  │  messages  │  │ webhooks │  │
│  │  (Auth)     │  │  (OAuth)    │  │  (Sync)    │  │ (Events) │  │
│  └─────────────┘  └─────────────┘  └────────────┘  └──────────┘  │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    analytics                                 │   │
│  │              (Stats & Reporting)                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
└───────┬────────────────┬─────────────────────┬──────────────────────┘
        │                │                     │
        ▼                ▼                     ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐
│ PostgreSQL   │  │    Redis     │  │   Celery Workers         │
│   Database   │  │ (Cache + MQ) │  │ (Background Tasks)       │
│  Port: 5432  │  │  Port: 6379  │  │  • Message Sync          │
│              │  │              │  │  • Token Refresh         │
│  • Users     │  │  • Sessions  │  │  • Analytics Aggregation │
│  • Platforms │  │  • Channels  │  │                          │
│  • Messages  │  │  • Celery    │  │  Celery Beat             │
│  • Analytics │  │              │  │  (Scheduler)             │
└──────────────┘  └──────────────┘  └──────────────────────────┘
                                                  │
                                                  │ Tasks
                                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       External APIs                                  │
│                                                                       │
│  ┌────────────────┐  ┌──────────────────┐  ┌─────────────────┐    │
│  │   Instagram    │  │    Messenger     │  │    WhatsApp     │    │
│  │   Graph API    │  │    Graph API     │  │  Business API   │    │
│  │                │  │                  │  │                 │    │
│  │  OAuth 2.0     │  │    OAuth 2.0     │  │  Token Auth     │    │
│  │  Webhooks      │  │    Webhooks      │  │  Webhooks       │    │
│  └────────────────┘  └──────────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. User Authentication Flow

```
User → Frontend → POST /api/auth/login
                   ↓
                Backend validates credentials
                   ↓
                JWT tokens generated
                   ↓
                Tokens returned to frontend
                   ↓
                Frontend stores tokens
                   ↓
                All API requests include JWT
```

### 2. Platform Connection Flow (Instagram/Messenger)

```
User → Click "Connect Instagram"
       ↓
Frontend → GET /api/platforms/instagram/connect
           ↓
Backend → Redirect to Meta OAuth
          ↓
Meta → User authorizes app
       ↓
Meta → Callback: /api/platforms/callback?code=xxx
       ↓
Backend → Exchange code for access token
          ↓
Backend → Encrypt & store token in DB
          ↓
Backend → Trigger initial message sync (Celery)
          ↓
Frontend → Shows "Connected" status
```

### 3. Message Sync Flow

```
Celery Beat → Triggers sync task every 5 minutes
              ↓
Celery Worker → For each connected platform:
                ↓
                Fetch new messages from API
                ↓
                Store in database
                ↓
                Broadcast via WebSocket
                ↓
Frontend (WebSocket) → Receives new message event
                       ↓
                       Updates UI in real-time
```

### 4. Webhook Flow (Real-Time)

```
Instagram/Messenger/WhatsApp → Sends webhook event
                                ↓
Backend → POST /api/webhooks/{platform}
          ↓
Backend → Verifies webhook signature
          ↓
Backend → Logs event to WebhookLog
          ↓
Backend → Processes message
          ↓
Backend → Stores in database
          ↓
Backend → Broadcasts via WebSocket
          ↓
Frontend → Receives and displays immediately
```

### 5. Analytics Flow

```
Celery Beat → Triggers analytics task hourly
              ↓
Celery Worker → Aggregates message data
                ↓
                Groups by date, platform
                ↓
                Stores in analytics table
                ↓
Frontend → GET /api/analytics/daily
           ↓
Backend → Returns aggregated data
          ↓
Frontend → Renders charts and stats
```

---

## Component Responsibilities

### Frontend (React)

**Purpose**: User interface and user experience

**Responsibilities**:
- Display dashboard with analytics
- Show unified chat interface
- Handle platform connections
- Manage authentication state
- Real-time updates via WebSocket
- Form validation
- Error handling

**Key Technologies**:
- React 18.3 (UI library)
- TypeScript (Type safety)
- Vite (Build tool)
- TanStack Query (API state management)
- Radix UI + Tailwind (UI components)
- WebSocket API (Real-time)

---

### Backend (Django)

**Purpose**: Business logic, data management, API server

**Responsibilities**:
- User authentication and authorization
- Platform OAuth integration
- Message storage and retrieval
- Webhook processing
- Real-time WebSocket connections
- Background task coordination
- API endpoint serving

**Key Technologies**:
- Django 5.0 (Web framework)
- Django REST Framework (API)
- Django Channels (WebSocket)
- Celery (Background tasks)
- PostgreSQL (Database)
- Redis (Cache + Message broker)

---

### Database (PostgreSQL)

**Purpose**: Persistent data storage

**Responsibilities**:
- Store user accounts
- Store platform connections & tokens
- Store messages and conversations
- Store analytics data
- Store webhook logs

**Key Features**:
- ACID compliance
- Complex queries
- Foreign key relationships
- Indexes for performance
- JSONB for metadata

---

### Cache/Broker (Redis)

**Purpose**: Caching and message queuing

**Responsibilities**:
- Cache frequently accessed data
- Django Channels layer (WebSocket)
- Celery message broker
- Celery result backend
- Session storage (optional)

**Key Features**:
- In-memory storage
- Pub/Sub messaging
- Data structures (lists, sets, hashes)
- Persistence (AOF)

---

### Background Workers (Celery)

**Purpose**: Asynchronous task processing

**Responsibilities**:
- Periodic message synchronization
- Token refresh
- Analytics aggregation
- Email notifications (future)
- Heavy computations

**Key Tasks**:
- `sync_all_platforms` - Every 5 minutes
- `aggregate_daily_analytics` - Every hour
- `refresh_expired_tokens` - Daily
- `send_message_async` - On demand

---

## Security Architecture

### Authentication & Authorization

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                           │
│                                                               │
│  1. Frontend                                                 │
│     • JWT stored in localStorage/sessionStorage             │
│     • Token included in Authorization header                │
│     • Auto-refresh on expiry                                │
│                                                               │
│  2. Backend                                                  │
│     • JWT verification on every request                     │
│     • Permission checks per endpoint                        │
│     • Rate limiting (future)                                │
│                                                               │
│  3. Database                                                 │
│     • Encrypted platform tokens (Fernet)                    │
│     • Password hashing (PBKDF2)                             │
│     • Row-level security (future)                           │
│                                                               │
│  4. External APIs                                            │
│     • OAuth 2.0 for Instagram/Messenger                     │
│     • Bearer token for WhatsApp                             │
│     • Webhook signature verification                        │
│     • HTTPS only                                            │
└─────────────────────────────────────────────────────────────┘
```

### Data Encryption

1. **At Rest**:
   - Platform access tokens encrypted with Fernet
   - User passwords hashed with PBKDF2
   - Database encryption (PostgreSQL TDE in production)

2. **In Transit**:
   - HTTPS for all API requests
   - WSS for WebSocket connections
   - TLS for database connections

3. **Secrets Management**:
   - Environment variables for secrets
   - No secrets in code
   - Separate .env files per environment

---

## Scaling Strategy

### Horizontal Scaling

```
┌─────────────────────────────────────────────────────────────┐
│                  Load Balancer (Nginx)                       │
└────────┬──────────────────┬──────────────────┬──────────────┘
         │                  │                  │
         ▼                  ▼                  ▼
    ┌─────────┐       ┌─────────┐       ┌─────────┐
    │Backend 1│       │Backend 2│       │Backend 3│
    └────┬────┘       └────┬────┘       └────┬────┘
         │                 │                  │
         └─────────────────┼──────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  PostgreSQL     │
                  │  (Read Replicas)│
                  └─────────────────┘
                           │
         ┌─────────────────┼──────────────────┐
         │                 │                  │
         ▼                 ▼                  ▼
    ┌─────────┐       ┌─────────┐       ┌─────────┐
    │Celery W1│       │Celery W2│       │Celery W3│
    └─────────┘       └─────────┘       └─────────┘
```

### Caching Strategy

1. **Application Cache** (Redis)
   - User sessions
   - Platform connection status
   - Frequently accessed conversations

2. **Database Query Cache**
   - Message list queries
   - Analytics aggregations

3. **CDN Cache** (Future)
   - Static frontend assets
   - Media files

---

## Monitoring & Observability

### Logging

```
Application Logs → Django Logging
                   ↓
                File + Console
                   ↓
            (Future: ELK Stack)
```

### Metrics (Future)

- Request count & latency
- Error rates
- Database query performance
- Celery task queue length
- WebSocket connections

### Alerts (Future)

- High error rate
- Database connection issues
- Failed Celery tasks
- API rate limit warnings

---

## Deployment Architecture

### Development

```
docker-compose.yml
├── db (PostgreSQL)
├── redis
├── backend (Django - auto-reload)
├── frontend (Vite dev server - hot reload)
├── celery (worker)
└── celery-beat (scheduler)
```

### Production

```
docker-compose.prod.yml
├── db (PostgreSQL)
├── redis (password-protected)
├── backend (Daphne - no auto-reload)
├── frontend (Nginx - optimized build)
├── celery (multiple workers)
├── celery-beat (scheduler)
└── nginx (reverse proxy + SSL)
```

---

## API Structure

### RESTful Endpoints

```
/api/auth/
  POST   /register              # User registration
  POST   /login                 # User login
  POST   /logout                # User logout
  POST   /refresh               # Refresh JWT token
  GET    /me                    # Current user info

/api/platforms/
  GET    /                      # List connected platforms
  POST   /instagram/connect     # Connect Instagram
  POST   /messenger/connect     # Connect Messenger
  POST   /whatsapp/connect      # Connect WhatsApp
  DELETE /{id}                  # Disconnect platform
  POST   /{id}/sync             # Manual sync

/api/messages/
  GET    /                      # List messages (paginated)
  GET    /{id}                  # Message details
  POST   /                      # Send message
  PATCH  /{id}/read             # Mark as read

/api/conversations/
  GET    /                      # List conversations
  GET    /{id}/messages         # Messages in conversation

/api/analytics/
  GET    /daily                 # Daily analytics
  GET    /platform              # Platform breakdown
  GET    /stats                 # Quick stats
  GET    /export                # Export data (CSV/PDF)

/api/webhooks/
  POST   /instagram             # Instagram webhook
  POST   /messenger             # Messenger webhook
  POST   /whatsapp              # WhatsApp webhook
  GET    /{platform}            # Webhook verification
```

### WebSocket Endpoints

```
/ws/messages/                   # Real-time message updates

Events (Client → Server):
  - authenticate               # Authenticate connection
  - subscribe_messages         # Subscribe to updates
  - mark_read                  # Mark message as read

Events (Server → Client):
  - new_message                # New message received
  - message_read               # Message read status updated
  - platform_connected         # Platform connected
  - sync_started               # Sync started
  - sync_completed             # Sync completed
```

---

## Database Schema Overview

```
users
├── id (UUID, PK)
├── email (unique)
├── password_hash
└── created_at

platform_accounts
├── id (UUID, PK)
├── user_id (FK)
├── platform (enum)
├── access_token (encrypted)
├── token_expires_at
└── is_active

messages
├── id (UUID, PK)
├── platform_account_id (FK)
├── platform_message_id (unique)
├── sender_name
├── content
├── is_incoming
├── is_read
└── received_at

conversations
├── id (UUID, PK)
├── platform_account_id (FK)
├── participant_name
├── last_message_at
└── unread_count

analytics
├── id (UUID, PK)
├── user_id (FK)
├── date
├── platform
└── total_messages

webhook_logs
├── id (UUID, PK)
├── platform
├── payload (jsonb)
├── processed
└── created_at
```

---

## Development Workflow

```
1. Developer makes changes
   ↓
2. Docker detects file changes
   ↓
3. Backend/Frontend auto-reloads
   ↓
4. Test changes in browser
   ↓
5. Commit to git
   ↓
6. Build production images
   ↓
7. Deploy to server
   ↓
8. Run migrations
   ↓
9. Restart services
```

---

This architecture is designed to be:
- **Scalable**: Can handle increasing load
- **Maintainable**: Clear separation of concerns
- **Secure**: Multiple layers of security
- **Observable**: Logging and monitoring built-in
- **Resilient**: Fault-tolerant with retry logic
