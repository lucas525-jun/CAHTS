"""
Celery tasks for platform token management
"""
import logging
from datetime import timedelta
from celery import shared_task
from django.utils import timezone
from django.db.models import Q

from .models import PlatformAccount
from .services import MetaAPIService

logger = logging.getLogger(__name__)


@shared_task(name='apps.platforms.tasks.refresh_expiring_tokens')
def refresh_expiring_tokens():
    """
    Check for tokens expiring in the next 7 days and refresh them
    Runs daily via Celery Beat
    """
    logger.info('Starting token refresh task')

    # Find tokens expiring in the next 7 days
    seven_days_from_now = timezone.now() + timedelta(days=7)

    expiring_platforms = PlatformAccount.objects.filter(
        Q(platform__in=['instagram', 'messenger']),  # Only Meta platforms support refresh
        Q(is_active=True),
        Q(token_expires_at__lte=seven_days_from_now),
        Q(token_expires_at__gt=timezone.now())  # Not already expired
    )

    logger.info(f'Found {expiring_platforms.count()} tokens expiring soon')

    refreshed = 0
    failed = 0

    for platform in expiring_platforms:
        try:
            # Refresh the token
            meta_service = MetaAPIService()

            # Get current access token
            access_token = platform.get_decrypted_access_token()

            # Refresh to get new long-lived token
            token_response = meta_service.get_long_lived_token(access_token)
            new_access_token = token_response.get('access_token')
            expires_in = token_response.get('expires_in', 5184000)  # Default 60 days

            if new_access_token:
                # Update platform with new token
                platform.access_token = new_access_token  # Will be encrypted on save
                platform.token_expires_at = timezone.now() + timedelta(seconds=expires_in)
                platform.save()

                logger.info(f'Refreshed token for platform {platform.id} ({platform.platform})')
                refreshed += 1
            else:
                logger.error(f'Failed to refresh token for platform {platform.id}: No token in response')
                failed += 1

        except Exception as e:
            logger.error(f'Error refreshing token for platform {platform.id}: {e}')
            failed += 1

    logger.info(f'Token refresh completed: {refreshed} refreshed, {failed} failed')
    return {
        'total_expiring': expiring_platforms.count(),
        'refreshed': refreshed,
        'failed': failed
    }


@shared_task(name='apps.platforms.tasks.deactivate_expired_tokens')
def deactivate_expired_tokens():
    """
    Deactivate platforms with expired tokens
    Runs daily via Celery Beat
    """
    logger.info('Starting expired token deactivation task')

    # Find platforms with expired tokens that are still active
    expired_platforms = PlatformAccount.objects.filter(
        is_active=True,
        token_expires_at__lt=timezone.now()
    )

    count = expired_platforms.count()
    logger.info(f'Found {count} platforms with expired tokens')

    # Deactivate them
    expired_platforms.update(is_active=False)

    logger.info(f'Deactivated {count} platforms with expired tokens')
    return {
        'deactivated': count
    }
