from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from apps.messages.models import Message, Conversation
from apps.platforms.models import PlatformAccount


class AnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet for analytics and reporting
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='stats/messages')
    def message_stats(self, request):
        """Get message statistics"""
        user = request.user

        # Get all user's platform accounts
        platform_accounts = PlatformAccount.objects.filter(user=user)

        # Get all conversations for user
        conversations = Conversation.objects.filter(platform_account__in=platform_accounts)

        # Get all messages for user
        messages = Message.objects.filter(platform_account__in=platform_accounts)

        # Calculate statistics
        total_messages = messages.count()
        unread_messages = messages.filter(is_incoming=True, is_read=False).count()
        total_conversations = conversations.count()

        # Platform breakdown
        platform_breakdown = {}
        for account in platform_accounts:
            platform = account.platform.lower()
            if platform not in platform_breakdown:
                platform_breakdown[platform] = 0
            platform_breakdown[platform] += Conversation.objects.filter(
                platform_account=account
            ).count()

        return Response({
            'total_messages': total_messages,
            'unread_messages': unread_messages,
            'total_conversations': total_conversations,
            'platform_breakdown': {
                'instagram': platform_breakdown.get('instagram', 0),
                'messenger': platform_breakdown.get('messenger', 0),
                'whatsapp': platform_breakdown.get('whatsapp', 0),
            }
        })

    @action(detail=False, methods=['get'], url_path='stats/daily')
    def daily_stats(self, request):
        """Get daily statistics for the last N days"""
        user = request.user
        days = int(request.query_params.get('days', 7))

        # Get user's platform accounts
        platform_accounts = PlatformAccount.objects.filter(user=user)

        # Calculate date range
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days - 1)

        # Get daily message counts
        daily_messages = Message.objects.filter(
            platform_account__in=platform_accounts,
            sent_at__date__gte=start_date,
            sent_at__date__lte=end_date
        ).annotate(
            date=TruncDate('sent_at')
        ).values('date').annotate(
            message_count=Count('id')
        ).order_by('date')

        # Get daily conversation counts (new conversations)
        daily_conversations = Conversation.objects.filter(
            platform_account__in=platform_accounts,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            conversation_count=Count('id')
        ).order_by('date')

        # Create a dict for easy lookup
        messages_by_date = {str(item['date']): item['message_count'] for item in daily_messages}
        conversations_by_date = {str(item['date']): item['conversation_count'] for item in daily_conversations}

        # Build result for all days in range
        result = []
        current_date = start_date
        while current_date <= end_date:
            date_str = str(current_date)
            result.append({
                'date': date_str,
                'message_count': messages_by_date.get(date_str, 0),
                'conversation_count': conversations_by_date.get(date_str, 0)
            })
            current_date += timedelta(days=1)

        return Response(result)

    @action(detail=False, methods=['get'])
    def platform(self, request):
        """Get platform breakdown"""
        user = request.user

        platform_accounts = PlatformAccount.objects.filter(user=user)

        breakdown = {}
        for account in platform_accounts:
            platform = account.platform.lower()
            if platform not in breakdown:
                breakdown[platform] = {
                    'conversations': 0,
                    'messages': 0,
                    'unread': 0
                }

            conversations = Conversation.objects.filter(platform_account=account)
            messages = Message.objects.filter(platform_account=account)

            breakdown[platform]['conversations'] += conversations.count()
            breakdown[platform]['messages'] += messages.count()
            breakdown[platform]['unread'] += messages.filter(
                is_incoming=True, is_read=False
            ).count()

        return Response(breakdown)

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export analytics data"""
        # TODO: Implement export functionality (CSV/PDF)
        _ = request  # Mark as intentionally unused for now
        return Response({'message': 'Export endpoint - to be implemented'})
