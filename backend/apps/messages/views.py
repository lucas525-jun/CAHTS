from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone

from .models import Conversation, Message
from .serializers import MessageSerializer, ConversationSerializer, ConversationDetailSerializer
from apps.platforms.models import PlatformAccount


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Get messages for the current user's platform accounts"""
        platform_accounts = PlatformAccount.objects.filter(user=self.request.user)
        queryset = Message.objects.filter(platform_account__in=platform_accounts)

        # Filter by conversation if provided
        conversation_id = self.request.query_params.get('conversation', None)
        if conversation_id:
            queryset = queryset.filter(conversation_id=conversation_id)

        # Filter by platform if provided
        platform = self.request.query_params.get('platform', None)
        if platform:
            queryset = queryset.filter(platform_account__platform=platform)

        # Filter by read status
        is_read = self.request.query_params.get('is_read', None)
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')

        return queryset.select_related('conversation', 'platform_account').order_by('-sent_at')

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        """Mark a message as read"""
        try:
            message = self.get_queryset().get(pk=pk)

            if not message.is_read:
                message.is_read = True
                message.read_at = timezone.now()
                message.save()

                # Update conversation unread count
                if message.conversation:
                    message.conversation.unread_count = max(
                        0, message.conversation.unread_count - 1
                    )
                    message.conversation.save()

            return Response({
                'message': 'Message marked as read',
                'data': MessageSerializer(message).data
            })
        except Message.DoesNotExist:
            return Response({
                'error': 'Message not found'
            }, status=status.HTTP_404_NOT_FOUND)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Get conversations for the current user's platform accounts"""
        platform_accounts = PlatformAccount.objects.filter(user=self.request.user)
        queryset = Conversation.objects.filter(platform_account__in=platform_accounts)

        # Filter by platform if provided
        platform = self.request.query_params.get('platform', None)
        if platform:
            queryset = queryset.filter(platform_account__platform=platform)

        # Filter by archived status
        is_archived = self.request.query_params.get('is_archived', None)
        if is_archived is not None:
            queryset = queryset.filter(is_archived=is_archived.lower() == 'true')

        return queryset.select_related('platform_account').order_by('-last_message_at')

    def retrieve(self, request, pk=None):
        """Get a specific conversation with recent messages"""
        try:
            conversation = self.get_queryset().get(pk=pk)

            # Get recent messages for this conversation
            messages_limit = int(request.query_params.get('messages_limit', 50))
            conversation.messages = conversation.messages.all().order_by('-sent_at')[:messages_limit]

            serializer = ConversationDetailSerializer(conversation)
            return Response(serializer.data)
        except Conversation.DoesNotExist:
            return Response({
                'error': 'Conversation not found'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request, pk=None):
        """Mark all messages in a conversation as read"""
        try:
            conversation = self.get_queryset().get(pk=pk)

            # Mark all unread messages as read
            unread_messages = conversation.messages.filter(is_read=False, is_incoming=True)
            count = unread_messages.update(is_read=True, read_at=timezone.now())

            # Reset unread count
            conversation.unread_count = 0
            conversation.save()

            return Response({
                'message': f'Marked {count} messages as read',
                'conversation': ConversationSerializer(conversation).data
            })
        except Conversation.DoesNotExist:
            return Response({
                'error': 'Conversation not found'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a conversation"""
        try:
            conversation = self.get_queryset().get(pk=pk)
            conversation.is_archived = True
            conversation.save()

            return Response({
                'message': 'Conversation archived',
                'conversation': ConversationSerializer(conversation).data
            })
        except Conversation.DoesNotExist:
            return Response({
                'error': 'Conversation not found'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def unarchive(self, request, pk=None):
        """Unarchive a conversation"""
        try:
            conversation = self.get_queryset().get(pk=pk)
            conversation.is_archived = False
            conversation.save()

            return Response({
                'message': 'Conversation unarchived',
                'conversation': ConversationSerializer(conversation).data
            })
        except Conversation.DoesNotExist:
            return Response({
                'error': 'Conversation not found'
            }, status=status.HTTP_404_NOT_FOUND)
