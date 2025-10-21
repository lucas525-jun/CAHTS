# WhatsApp Messaging Guide

## Overview

Your CAHTS application now supports full WhatsApp Business messaging! This guide explains how to use it.

## What's Working

✅ **WhatsApp Connection** - Successfully connected
✅ **Message Sending** - Backend fully supports sending messages
✅ **Message Receiving** - Via webhooks (real-time)
✅ **Conversations UI** - Frontend displays WhatsApp conversations
✅ **WebSocket** - Fixed for real-time updates

## Quick Start

### 1. Verify WebSocket Connection

After logging in, open your browser's Developer Tools (F12) and check the Console:

You should see:
```
🔌 Connecting to WebSocket...
  User ID: [your-user-id]
  Token length: [number]
  Token preview: [first 20 chars]...
✅ WebSocket connected successfully!
```

If you see `❌ No access token found`, refresh the page and login again.

### 2. Test WhatsApp Connection

Run the test script:

```bash
docker-compose -f docker-compose.prod.yml exec backend python test_whatsapp.py
```

This will show:
- ✅ WhatsApp credentials validation
- 📱 Phone number and business account info
- 📊 Quality rating
- 💬 Existing conversations (if any)

### 3. Start Using WhatsApp

**Option A: Wait for Incoming Message (Recommended)**

1. Send a message TO your WhatsApp Business number from your personal phone
2. The webhook will automatically:
   - Create a conversation
   - Store the message
   - Show it in your CAHTS dashboard
3. Go to the "Chats" page - you'll see the conversation
4. Click on it to view and reply!

**Option B: Create Test Conversation**

If you want to test immediately:

1. Run the test script:
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend python test_whatsapp.py
   ```

2. Select option `3` to create a test conversation

3. Enter a phone number (with country code, e.g., +1234567890)

4. Go to your CAHTS app → Chats page

5. You'll see the test conversation - click it to send a message!

⚠️ **Warning:** Test messages will send REAL WhatsApp messages to the number you provide!

## How to Send Messages

### Via UI (Recommended)

1. **Go to Chats Page**
   - Navigate to `/chats` in your app
   - You'll see all conversations (Instagram, Messenger, WhatsApp)

2. **Filter by WhatsApp (Optional)**
   - Use the platform filter to show only WhatsApp conversations

3. **Click on a Conversation**
   - This opens the conversation detail page
   - You'll see the message history

4. **Type and Send**
   - Use the message composer at the bottom
   - Type your message
   - Press Send or hit Enter
   - The message will be sent via WhatsApp Business API

5. **Real-time Updates**
   - When you receive a reply, it will appear instantly (via WebSocket)
   - You'll get a toast notification

### Via Test Script

```bash
docker-compose -f docker-compose.prod.yml exec backend python test_whatsapp.py
```

Select option `2` to send a test message:
- Choose a conversation
- Type your message
- It will be sent immediately

### Via API

```bash
# Get your conversation ID
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/messages/conversations/

# Send a message
curl -X POST \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello from API!",
    "message_type": "text"
  }' \
  http://localhost:8000/api/messages/conversations/CONVERSATION_ID/send-message/
```

## Supported Message Types

### Text Messages (✅ Fully Supported)

```javascript
{
  "content": "Your message here",
  "message_type": "text"
}
```

### Media Messages (✅ Supported)

```javascript
// Image
{
  "content": "Check this out!",  // Optional caption
  "message_type": "image",
  "media_url": "https://example.com/image.jpg"
}

// Video
{
  "content": "Watch this",
  "message_type": "video",
  "media_url": "https://example.com/video.mp4"
}

// Document
{
  "content": "Here's the file",
  "message_type": "file",
  "media_url": "https://example.com/document.pdf"
}

// Audio
{
  "message_type": "audio",
  "media_url": "https://example.com/audio.mp3"
}
```

## Troubleshooting

### Problem: No Conversations Showing

**Cause:** No one has messaged your WhatsApp Business number yet.

**Solutions:**
1. Send a message TO your Business number from another phone
2. Create a test conversation (see Option B above)

### Problem: Message Not Sending

**Check:**
1. Is WhatsApp connection active?
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend python test_whatsapp.py
   # Select option 4 to recheck connection
   ```

2. Are credentials valid?
   - The script will show if credentials are expired or invalid

3. Check backend logs:
   ```bash
   docker-compose -f docker-compose.prod.yml logs backend | grep -i whatsapp
   ```

### Problem: WebSocket Not Connecting

**Symptoms:**
- Messages don't appear in real-time
- Have to refresh to see new messages
- Console shows WebSocket errors

**Solutions:**

1. **Check for access token:**
   - Open browser DevTools → Console
   - Look for "❌ No access token found"
   - If present: Logout and login again

2. **Check WebSocket URL:**
   - Ensure `VITE_WS_URL` is set correctly in frontend/.env
   - Should be `ws://localhost:8000/ws` for local
   - Or `wss://your-domain.com/ws` for production

3. **Check backend logs:**
   ```bash
   docker-compose -f docker-compose.prod.yml logs backend | grep -i websocket
   ```

   Look for:
   - "WebSocket authenticated user" (good!)
   - "WebSocket no token provided" (need to re-login)
   - "WebSocket token error" (token might be expired)

### Problem: "Token Expired" or "Invalid Credentials"

**WhatsApp tokens can expire.** You have two options:

**Option 1: Use System User Token (Recommended)**

System User tokens don't expire:

1. Go to https://business.facebook.com/settings/system-users
2. Create/select a System User
3. Assign it to your WhatsApp Business Account
4. Generate a new token
5. Update in Settings page of CAHTS

**Option 2: Reconnect WhatsApp**

1. Go to Settings page
2. Disconnect WhatsApp
3. Connect again with fresh credentials

## Webhooks for Real-Time Messages

For real-time incoming messages (without manual sync), configure webhooks:

### 1. Configure Webhook URL

In Meta Developer Console:

1. Go to WhatsApp → Configuration
2. Set Callback URL: `https://your-domain.com/api/webhooks/whatsapp`
3. Set Verify Token: (copy from `WEBHOOK_VERIFY_TOKEN` in backend/.env)
4. Click "Verify and Save"

### 2. Subscribe to Events

Subscribe to these webhook fields:
- ✅ `messages` - For incoming messages
- ✅ `message_status` - For delivery receipts

### 3. Test Webhook

Send a message TO your WhatsApp Business number:
- Should appear instantly in your CAHTS app
- Check webhook logs:
  ```bash
  docker-compose -f docker-compose.prod.yml exec backend python manage.py shell
  ```
  ```python
  from apps.webhooks.models import WebhookLog
  logs = WebhookLog.objects.filter(platform='whatsapp').order_by('-created_at')[:5]
  for log in logs:
      print(f"{log.created_at}: {log.event_type} - Processed: {log.processed}")
  ```

## Message Sync

Even without webhooks, messages are synced periodically:

- **Frequency:** Every 2 minutes (configurable in settings.py)
- **What it does:** Fetches new messages from WhatsApp API
- **Manual sync:**
  ```bash
  docker-compose -f docker-compose.prod.yml exec backend python manage.py shell
  ```
  ```python
  from apps.messages.tasks import sync_whatsapp_messages
  from apps.platforms.models import PlatformAccount

  wa = PlatformAccount.objects.filter(platform='whatsapp').first()
  sync_whatsapp_messages.delay(str(wa.id))
  print("Sync task queued!")
  ```

## Tips

1. **Use System User Tokens** - They don't expire, perfect for production

2. **Test First** - Use the test script before sending real messages

3. **Monitor Logs** - Keep an eye on backend logs for errors
   ```bash
   docker-compose -f docker-compose.prod.yml logs -f backend
   ```

4. **Check Quality Rating** - WhatsApp monitors message quality
   - Run test script to see your current rating
   - Poor ratings can lead to restrictions

5. **Set Up Webhooks** - For the best real-time experience

## Need Help?

Check the logs:

```bash
# Backend logs
docker-compose -f docker-compose.prod.yml logs backend | tail -100

# Celery worker logs (for message sync)
docker-compose -f docker-compose.prod.yml logs celery | tail -100

# Frontend logs
docker-compose -f docker-compose.prod.yml logs frontend | tail -100
```

Run diagnostics:

```bash
# Full WhatsApp diagnostics
docker-compose -f docker-compose.prod.yml exec backend python test_whatsapp.py
```

## Summary

Your WhatsApp messaging is **fully functional**! The system can:

- ✅ Send text and media messages
- ✅ Receive messages via webhooks
- ✅ Display conversations in real-time
- ✅ Manage multiple conversations
- ✅ Track message status (sent/delivered/read)
- ✅ Sync messages periodically

Just make sure you have conversations first (either wait for incoming messages or create test ones)!
