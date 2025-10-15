from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

from .models import Conversation, Message
from .serializers import MessageSerializer, ConversationSerializer, ConversationDetailSerializer, SendMessageSerializer
from apps.platforms.models import PlatformAccount
from apps.platforms.services.instagram import InstagramService
from apps.platforms.services.messenger import MessengerService
from apps.platforms.services.whatsapp import WhatsAppService


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

    @action(detail=True, methods=['post'], url_path='send-message')
    def send_message(self, request, pk=None):
        """Send a message in a conversation"""
        try:
            conversation = self.get_queryset().get(pk=pk)
            platform_account = conversation.platform_account

            # Validate request data
            serializer = SendMessageSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': 'Invalid message data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            validated_data = serializer.validated_data
            content = validated_data['content']
            message_type = validated_data.get('message_type', 'text')
            media_url = validated_data.get('media_url')

            # Get decrypted access token
            access_token = platform_account.get_decrypted_access_token()

            # Send message based on platform
            response_data = None
            platform_message_id = None

            if platform_account.platform == 'instagram':
                service = InstagramService()
                response_data = service.send_message(
                    recipient_id=conversation.participant_id,
                    message_text=content,
                    ig_account_id=platform_account.platform_user_id,
                    access_token=access_token
                )
                if response_data:
                    platform_message_id = response_data.get('id')

            elif platform_account.platform == 'messenger':
                service = MessengerService()
                if message_type == 'text':
                    response_data = service.send_message(
                        recipient_id=conversation.participant_id,
                        message_text=content,
                        page_id=platform_account.platform_user_id,
                        access_token=access_token
                    )
                else:
                    response_data = service.send_message_with_attachment(
                        recipient_id=conversation.participant_id,
                        attachment_type=message_type,
                        attachment_url=media_url,
                        page_id=platform_account.platform_user_id,
                        access_token=access_token
                    )
                if response_data:
                    platform_message_id = response_data.get('message_id')

            elif platform_account.platform == 'whatsapp':
                service = WhatsAppService()
                if message_type == 'text':
                    response_data = service.send_text_message(
                        recipient_phone=conversation.participant_id,
                        message_text=content,
                        phone_number_id=platform_account.platform_user_id,
                        access_token=access_token
                    )
                else:
                    response_data = service.send_media_message(
                        recipient_phone=conversation.participant_id,
                        media_type=message_type,
                        media_url=media_url,
                        caption=content if content else None,
                        phone_number_id=platform_account.platform_user_id,
                        access_token=access_token
                    )
                if response_data:
                    messages_data = response_data.get('messages', [])
                    if messages_data:
                        platform_message_id = messages_data[0].get('id')

            # Check if message was sent successfully
            if not response_data or not platform_message_id:
                return Response({
                    'error': 'Failed to send message',
                    'details': 'Platform API returned an error'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Create message record in database
            message = Message.objects.create(
                conversation=conversation,
                platform_account=platform_account,
                platform_message_id=platform_message_id,
                message_type=message_type,
                content=content,
                media_url=media_url,
                sender_id=platform_account.platform_user_id,
                sender_name=platform_account.platform_username or 'Me',
                is_incoming=False,
                is_read=True,
                sent_at=timezone.now(),
                delivered_at=timezone.now()
            )

            # Update conversation last_message_at
            conversation.last_message_at = timezone.now()
            conversation.save()

            return Response({
                'message': 'Message sent successfully',
                'data': MessageSerializer(message).data
            }, status=status.HTTP_201_CREATED)

        except Conversation.DoesNotExist:
            return Response({
                'error': 'Conversation not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f'Error sending message: {str(e)}')
            return Response({
                'error': 'Internal server error',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_messages(request):
    """
    Search messages and conversations

    Query parameters:
    - q: Search query (required)
    - platform: Filter by platform (optional: instagram, messenger, whatsapp)
    - is_read: Filter by read status (optional: true, false)
    - limit: Number of results (default: 20, max: 100)
    """
    query = request.query_params.get('q', '').strip()

    if not query:
        return Response({
            'error': 'Search query is required',
            'detail': 'Please provide a search query using the "q" parameter'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Get user's platform accounts
    platform_accounts = PlatformAccount.objects.filter(user=request.user)

    # Search in messages
    messages_query = Message.objects.filter(
        platform_account__in=platform_accounts
    ).filter(
        Q(content__icontains=query) |
        Q(sender_name__icontains=query)
    )

    # Search in conversations
    conversations_query = Conversation.objects.filter(
        platform_account__in=platform_accounts
    ).filter(
        Q(participant_name__icontains=query) |
        Q(participant_id__icontains=query)
    )

    # Apply platform filter if provided
    platform = request.query_params.get('platform')
    if platform:
        messages_query = messages_query.filter(platform_account__platform=platform)
        conversations_query = conversations_query.filter(platform_account__platform=platform)

    # Apply read status filter if provided
    is_read = request.query_params.get('is_read')
    if is_read is not None:
        messages_query = messages_query.filter(is_read=is_read.lower() == 'true')

    # Limit results
    limit = min(int(request.query_params.get('limit', 20)), 100)

    # Get results
    messages = messages_query.select_related('conversation', 'platform_account').order_by('-sent_at')[:limit]
    conversations = conversations_query.select_related('platform_account').order_by('-last_message_at')[:limit]

    return Response({
        'query': query,
        'results': {
            'messages': MessageSerializer(messages, many=True).data,
            'conversations': ConversationSerializer(conversations, many=True).data,
            'total_messages': messages.count(),
            'total_conversations': conversations.count(),
        }
    })
