"""
Message processing and storage services
"""
import logging
from typing import Dict, Any, Optional
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Conversation, Message
from apps.platforms.models import PlatformAccount

logger = logging.getLogger(__name__)


class MessageService:
    """
    Service for processing and storing messages from different platforms
    """

    @staticmethod
    def process_webhook_message(platform: str, event_data: Dict[str, Any]) -> Optional[Message]:
        """
        Process and store a message from webhook event

        Args:
            platform: Platform name (instagram, messenger, whatsapp)
            event_data: Parsed event data from platform service

        Returns:
            Created Message instance or None
        """
        try:
            # Find the platform account
            if platform in ['instagram', 'messenger']:
                # For Instagram and Messenger, match by platform_user_id
                recipient_id = event_data.get('recipient_id')
                platform_account = PlatformAccount.objects.filter(
                    platform=platform,
                    platform_user_id__in=[recipient_id, event_data.get('sender_id')]
                ).first()
            elif platform == 'whatsapp':
                # For WhatsApp, match by phone number in metadata
                platform_account = PlatformAccount.objects.filter(
                    platform='whatsapp',
                    is_active=True
                ).first()
            else:
                logger.error(f'Unknown platform: {platform}')
                return None

            if not platform_account:
                logger.warning(f'No platform account found for {platform} event')
                return None

            # Get or create conversation
            conversation = MessageService._get_or_create_conversation(
                platform_account, event_data
            )

            if not conversation:
                logger.error('Failed to create/get conversation')
                return None

            # Check if message already exists (prevent duplicates)
            message_id = event_data.get('message_id')
            if Message.objects.filter(platform_message_id=message_id).exists():
                logger.debug(f'Message {message_id} already exists, skipping')
                return None

            # Determine message type
            message_type = event_data.get('message_type', 'text')
            if message_type not in ['text', 'image', 'video', 'audio', 'file', 'sticker', 'location']:
                message_type = 'text'

            # Create message
            message = Message.objects.create(
                conversation=conversation,
                platform_account=platform_account,
                platform_message_id=message_id,
                message_type=message_type,
                content=event_data.get('message_text', ''),
                media_url=event_data.get('media_url'),
                sender_id=event_data.get('sender_id'),
                sender_name=event_data.get('sender_name', event_data.get('sender_id')),
                is_incoming=not event_data.get('is_echo', False),
                sent_at=timezone.now(),
            )

            # Update conversation
            conversation.last_message_at = message.sent_at
            if message.is_incoming and not message.is_read:
                conversation.unread_count += 1
            conversation.save()

            # Broadcast message via WebSocket
            MessageService._broadcast_message(platform_account.user_id, message)

            logger.info(f'Stored message {message_id} from {platform}')
            return message

        except Exception as e:
            logger.error(f'Error processing webhook message: {e}')
            return None

    @staticmethod
    def _get_or_create_conversation(
        platform_account: PlatformAccount,
        event_data: Dict[str, Any]
    ) -> Optional[Conversation]:
        """
        Get or create a conversation for a message

        Args:
            platform_account: PlatformAccount instance
            event_data: Event data containing conversation info

        Returns:
            Conversation instance or None
        """
        try:
            # Extract conversation identifier
            conversation_id = event_data.get('conversation_id')
            sender_id = event_data.get('sender_id')
            sender_name = event_data.get('sender_name', sender_id)

            if not conversation_id and not sender_id:
                logger.error('No conversation_id or sender_id in event data')
                return None

            # Use sender_id as conversation_id if not provided
            platform_conversation_id = conversation_id or sender_id

            # Get or create conversation
            conversation, created = Conversation.objects.get_or_create(
                platform_account=platform_account,
                platform_conversation_id=platform_conversation_id,
                defaults={
                    'participant_id': sender_id or 'unknown',
                    'participant_name': sender_name or 'Unknown User',
                    'last_message_at': timezone.now(),
                }
            )

            if created:
                logger.info(f'Created new conversation {platform_conversation_id}')

            return conversation

        except Exception as e:
            logger.error(f'Error creating conversation: {e}')
            return None

    @staticmethod
    def _broadcast_message(user_id: str, message: Message):
        """
        Broadcast new message via WebSocket to the user

        Args:
            user_id: User ID to send message to
            message: Message instance
        """
        try:
            channel_layer = get_channel_layer()
            room_group_name = f'messages_{user_id}'

            # Prepare message data
            message_data = {
                'id': str(message.id),
                'conversation_id': str(message.conversation_id),
                'platform': message.platform_account.get_platform_display(),
                'sender_name': message.sender_name,
                'content': message.content,
                'message_type': message.message_type,
                'is_incoming': message.is_incoming,
                'sent_at': message.sent_at.isoformat(),
            }

            # Send to WebSocket group
            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {
                    'type': 'new_message',
                    'message': message_data
                }
            )

            logger.debug(f'Broadcasted message {message.id} to user {user_id}')

        except Exception as e:
            logger.error(f'Error broadcasting message: {e}')

    @staticmethod
    def sync_platform_messages(platform_account: PlatformAccount, service_instance, limit: int = 50) -> Dict[str, Any]:
        """
        Sync messages from a platform using its service

        Args:
            platform_account: PlatformAccount instance
            service_instance: Platform service instance (InstagramService, etc.)
            limit: Maximum number of messages to fetch

        Returns:
            Sync result dictionary
        """
        try:
            stats = {
                'conversations_synced': 0,
                'messages_synced': 0,
                'new_messages': 0,
            }

            # Get access token (should be decrypted in production)
            access_token = platform_account.access_token

            # Fetch conversations based on platform
            if platform_account.platform == 'instagram':
                ig_account_id = platform_account.metadata.get('ig_account_id')
                conversations = service_instance.get_conversations(ig_account_id, access_token, limit)
            elif platform_account.platform == 'messenger':
                page_id = platform_account.platform_user_id
                conversations = service_instance.get_conversations(page_id, access_token, limit)
            else:
                logger.warning(f'Sync not implemented for {platform_account.platform}')
                return stats

            stats['conversations_synced'] = len(conversations)

            # Process each conversation
            for conv_data in conversations:
                try:
                    # Get or create conversation
                    conversation, created = Conversation.objects.get_or_create(
                        platform_account=platform_account,
                        platform_conversation_id=conv_data.get('id'),
                        defaults={
                            'participant_id': 'unknown',
                            'participant_name': 'Unknown',
                            'last_message_at': timezone.now(),
                        }
                    )

                    # Fetch messages for this conversation
                    messages = service_instance.get_conversation_messages(
                        conv_data.get('id'),
                        access_token,
                        limit=limit
                    )

                    stats['messages_synced'] += len(messages)

                    # Store new messages
                    for msg_data in messages:
                        message_id = msg_data.get('id')

                        # Skip if already exists
                        if Message.objects.filter(platform_message_id=message_id).exists():
                            continue

                        # Create message
                        Message.objects.create(
                            conversation=conversation,
                            platform_account=platform_account,
                            platform_message_id=message_id,
                            message_type='text',  # Simplified for now
                            content=msg_data.get('message', ''),
                            sender_id=msg_data.get('from', {}).get('id', 'unknown'),
                            sender_name=msg_data.get('from', {}).get('username', 'Unknown'),
                            is_incoming=True,  # Determine based on from field
                            sent_at=timezone.now(),
                        )

                        stats['new_messages'] += 1

                    # Update conversation
                    if messages:
                        conversation.last_message_at = timezone.now()
                        conversation.save()

                except Exception as e:
                    logger.error(f'Error processing conversation {conv_data.get("id")}: {e}')
                    continue

            logger.info(f'Sync completed for {platform_account.platform}: {stats}')
            return stats

        except Exception as e:
            logger.error(f'Error syncing platform messages: {e}')
            return {'error': str(e)}
