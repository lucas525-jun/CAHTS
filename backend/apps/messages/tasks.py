"""
Celery tasks for message synchronization
"""
import logging
from celery import shared_task
from django.utils import timezone

from apps.platforms.models import PlatformAccount
from apps.platforms.services import InstagramService, MessengerService, WhatsAppService
from .models import Conversation, Message
from .services import MessageService

logger = logging.getLogger(__name__)


@shared_task(name='apps.messages.tasks.sync_all_platforms')
def sync_all_platforms():
    """
    Sync messages from all active platform connections
    Runs every 5 minutes (configured in settings)
    """
    logger.info('Starting platform sync task')

    active_platforms = PlatformAccount.objects.filter(is_active=True)

    for platform in active_platforms:
        try:
            if platform.platform == 'instagram':
                sync_instagram_messages.delay(platform.id)
            elif platform.platform == 'messenger':
                sync_messenger_messages.delay(platform.id)
            elif platform.platform == 'whatsapp':
                sync_whatsapp_messages.delay(platform.id)
        except Exception as e:
            logger.error(f'Error triggering sync for platform {platform.id}: {e}')

    logger.info(f'Triggered sync for {active_platforms.count()} platforms')
    return {'synced_platforms': active_platforms.count()}


@shared_task(name='apps.messages.tasks.sync_instagram_messages')
def sync_instagram_messages(platform_account_id):
    """
    Sync Instagram messages for a specific platform account
    """
    try:
        platform = PlatformAccount.objects.get(id=platform_account_id, platform='instagram')
        instagram_service = InstagramService()

        # Use MessageService to sync
        stats = MessageService.sync_platform_messages(platform, instagram_service, limit=50)

        # Update last sync time
        platform.last_sync_at = timezone.now()
        platform.save()

        logger.info(f'Instagram sync completed for {platform_account_id}: {stats}')
        return {'status': 'success', **stats}

    except PlatformAccount.DoesNotExist:
        logger.error(f'Platform account {platform_account_id} not found')
        return {'status': 'error', 'message': 'Platform not found'}
    except Exception as e:
        logger.error(f'Error syncing Instagram messages: {e}')
        return {'status': 'error', 'message': str(e)}


@shared_task(name='apps.messages.tasks.sync_messenger_messages')
def sync_messenger_messages(platform_account_id):
    """
    Sync Messenger messages for a specific platform account
    """
    try:
        platform = PlatformAccount.objects.get(id=platform_account_id, platform='messenger')
        messenger_service = MessengerService()

        # Use MessageService to sync
        stats = MessageService.sync_platform_messages(platform, messenger_service, limit=50)

        # Update last sync time
        platform.last_sync_at = timezone.now()
        platform.save()

        logger.info(f'Messenger sync completed for {platform_account_id}: {stats}')
        return {'status': 'success', **stats}

    except PlatformAccount.DoesNotExist:
        logger.error(f'Platform account {platform_account_id} not found')
        return {'status': 'error', 'message': 'Platform not found'}
    except Exception as e:
        logger.error(f'Error syncing Messenger messages: {e}')
        return {'status': 'error', 'message': str(e)}


@shared_task(name='apps.messages.tasks.sync_whatsapp_messages')
def sync_whatsapp_messages(platform_account_id):
    """
    Sync WhatsApp messages for a specific platform account
    Note: WhatsApp uses webhooks for real-time delivery, so this task
    is mainly for checking status updates or recovering from missed webhooks
    """
    try:
        platform = PlatformAccount.objects.get(id=platform_account_id, platform='whatsapp')

        logger.info(f'WhatsApp sync for platform {platform_account_id} (webhook-based, no polling needed)')

        # Update last sync time
        platform.last_sync_at = timezone.now()
        platform.save()

        return {'status': 'success', 'note': 'WhatsApp uses webhooks'}

    except PlatformAccount.DoesNotExist:
        logger.error(f'Platform account {platform_account_id} not found')
        return {'status': 'error', 'message': 'Platform not found'}
    except Exception as e:
        logger.error(f'Error in WhatsApp sync task: {e}')
        return {'status': 'error', 'message': str(e)}
