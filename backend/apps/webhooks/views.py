"""
Webhook handlers for Instagram, Messenger, and WhatsApp
"""
import json
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import WebhookLog
from apps.platforms.services import MetaAPIService, InstagramService, MessengerService, WhatsAppService
from apps.messages.services import MessageService

logger = logging.getLogger(__name__)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@csrf_exempt
def instagram_webhook(request):
    """
    Handle Instagram webhook events
    GET: Webhook verification
    POST: Webhook event processing
    """
    if request.method == 'GET':
        # Webhook verification
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        if mode == 'subscribe' and token == settings.WEBHOOK_VERIFY_TOKEN:
            logger.info('Instagram webhook verified successfully')
            return Response(int(challenge), content_type='text/plain')
        else:
            logger.warning('Instagram webhook verification failed')
            return Response('Verification failed', status=status.HTTP_403_FORBIDDEN)

    elif request.method == 'POST':
        # Get request body and signature
        body = request.body.decode('utf-8')
        signature = request.headers.get('X-Hub-Signature-256', '')

        # Verify signature
        meta_service = MetaAPIService()
        if not meta_service.verify_webhook_signature(body, signature):
            logger.warning('Instagram webhook signature verification failed')
            return Response('Invalid signature', status=status.HTTP_403_FORBIDDEN)

        try:
            # Parse event
            event_data = json.loads(body)

            # Log webhook event
            WebhookLog.objects.create(
                platform='instagram',
                event_type=event_data.get('object', 'unknown'),
                payload=event_data,
                headers=dict(request.headers),
                status='pending'
            )

            # Parse and process event
            instagram_service = InstagramService()
            parsed_event = instagram_service.parse_webhook_event(event_data)

            if parsed_event:
                logger.info(f'Instagram webhook event received: {parsed_event}')
                # Store message in database and broadcast via WebSocket
                MessageService.process_webhook_message('instagram', parsed_event)

            return Response({'status': 'success'})

        except Exception as e:
            logger.error(f'Error processing Instagram webhook: {e}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@csrf_exempt
def messenger_webhook(request):
    """
    Handle Messenger webhook events
    GET: Webhook verification
    POST: Webhook event processing
    """
    if request.method == 'GET':
        # Webhook verification
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        if mode == 'subscribe' and token == settings.WEBHOOK_VERIFY_TOKEN:
            logger.info('Messenger webhook verified successfully')
            return Response(int(challenge), content_type='text/plain')
        else:
            logger.warning('Messenger webhook verification failed')
            return Response('Verification failed', status=status.HTTP_403_FORBIDDEN)

    elif request.method == 'POST':
        # Get request body and signature
        body = request.body.decode('utf-8')
        signature = request.headers.get('X-Hub-Signature-256', '')

        # Verify signature
        meta_service = MetaAPIService()
        if not meta_service.verify_webhook_signature(body, signature):
            logger.warning('Messenger webhook signature verification failed')
            return Response('Invalid signature', status=status.HTTP_403_FORBIDDEN)

        try:
            # Parse event
            event_data = json.loads(body)

            # Log webhook event
            webhook_log = WebhookLog.objects.create(
                platform='messenger',
                event_type=event_data.get('object', 'unknown'),
                payload=event_data,
                headers=dict(request.headers),
                status='pending'
            )

            # Parse and process event
            messenger_service = MessengerService()
            parsed_event = messenger_service.parse_webhook_event(event_data)

            if parsed_event:
                logger.info(f'Messenger webhook event received: {parsed_event}')
                # Store message in database and broadcast via WebSocket
                MessageService.process_webhook_message('messenger', parsed_event)
                webhook_log.status = 'processed'
                webhook_log.save()

            return Response({'status': 'success'})

        except Exception as e:
            logger.error(f'Error processing Messenger webhook: {e}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@csrf_exempt
def whatsapp_webhook(request):
    """
    Handle WhatsApp webhook events
    GET: Webhook verification
    POST: Webhook event processing
    """
    if request.method == 'GET':
        # Webhook verification
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        if mode == 'subscribe' and token == settings.WEBHOOK_VERIFY_TOKEN:
            logger.info('WhatsApp webhook verified successfully')
            return Response(int(challenge), content_type='text/plain')
        else:
            logger.warning('WhatsApp webhook verification failed')
            return Response('Verification failed', status=status.HTTP_403_FORBIDDEN)

    elif request.method == 'POST':
        # Get request body and signature
        body = request.body.decode('utf-8')
        signature = request.headers.get('X-Hub-Signature-256', '')

        # Verify signature
        whatsapp_service = WhatsAppService()
        if not whatsapp_service.verify_webhook_signature(body, signature):
            logger.warning('WhatsApp webhook signature verification failed')
            return Response('Invalid signature', status=status.HTTP_403_FORBIDDEN)

        try:
            # Parse event
            event_data = json.loads(body)

            # Log webhook event
            webhook_log = WebhookLog.objects.create(
                platform='whatsapp',
                event_type='message' if event_data.get('entry', [{}])[0].get('changes', [{}])[0].get('value', {}).get('messages') else 'status',
                payload=event_data,
                headers=dict(request.headers),
                status='pending'
            )

            # Parse and process event
            parsed_event = whatsapp_service.parse_webhook_event(event_data)

            if parsed_event:
                logger.info(f'WhatsApp webhook event received: {parsed_event}')
                # Store message in database and broadcast via WebSocket
                if parsed_event.get('event_type') != 'status':
                    MessageService.process_webhook_message('whatsapp', parsed_event)
                webhook_log.status = 'processed'
                webhook_log.processed_at = timezone.now()
                webhook_log.save()

            return Response({'status': 'success'})

        except Exception as e:
            logger.error(f'Error processing WhatsApp webhook: {e}')
            webhook_log.status = 'failed'
            webhook_log.error_message = str(e)
            webhook_log.save()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
