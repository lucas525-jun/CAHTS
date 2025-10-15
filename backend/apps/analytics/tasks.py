"""
Celery tasks for analytics aggregation
"""
import logging
from celery import shared_task
from django.utils import timezone
from django.db.models import Count, Q
from datetime import date, timedelta

from apps.messages.models import Message
from apps.platforms.models import PlatformAccount
from .models import DailyAnalytics

logger = logging.getLogger(__name__)


@shared_task(name='apps.analytics.tasks.aggregate_daily_analytics')
def aggregate_daily_analytics():
    """
    Aggregate daily analytics for all users
    Runs every hour (configured in settings)
    """
    logger.info('Starting daily analytics aggregation')

    today = date.today()
    yesterday = today - timedelta(days=1)

    # Get all users who have platform connections
    users_with_platforms = PlatformAccount.objects.values_list('user_id', flat=True).distinct()

    aggregated_count = 0

    for user_id in users_with_platforms:
        try:
            # Aggregate for each platform
            for platform in ['instagram', 'messenger', 'whatsapp']:
                aggregate_user_platform_analytics(user_id, platform, yesterday)
                aggregated_count += 1

            # Aggregate for all platforms combined
            aggregate_user_platform_analytics(user_id, 'all', yesterday)
            aggregated_count += 1

        except Exception as e:
            logger.error(f'Error aggregating analytics for user {user_id}: {e}')

    logger.info(f'Aggregated analytics for {aggregated_count} user-platform combinations')
    return {'aggregated': aggregated_count}


def aggregate_user_platform_analytics(user_id, platform, target_date):
    """
    Aggregate analytics for a specific user and platform on a specific date
    """
    # Get platform accounts for this user and platform
    if platform == 'all':
        platform_accounts = PlatformAccount.objects.filter(user_id=user_id)
    else:
        platform_accounts = PlatformAccount.objects.filter(user_id=user_id, platform=platform)

    if not platform_accounts.exists():
        return

    # Get messages for this date
    messages = Message.objects.filter(
        platform_account__in=platform_accounts,
        sent_at__date=target_date
    )

    # Calculate statistics
    total_messages = messages.count()
    incoming_messages = messages.filter(is_incoming=True).count()
    outgoing_messages = messages.filter(is_incoming=False).count()

    # Get conversation count
    total_conversations = messages.values('conversation_id').distinct().count()

    # Update or create analytics record
    DailyAnalytics.objects.update_or_create(
        user_id=user_id,
        platform=platform,
        date=target_date,
        defaults={
            'total_messages': total_messages,
            'incoming_messages': incoming_messages,
            'outgoing_messages': outgoing_messages,
            'total_conversations': total_conversations,
        }
    )

    logger.debug(f'Aggregated analytics for user {user_id}, platform {platform}, date {target_date}')
