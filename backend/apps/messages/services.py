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
        Sync messages from a platform using its service with improved error handling

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
                'errors': 0,
            }

            # Get decrypted access token
            access_token = platform_account.get_decrypted_access_token()

            if not access_token:
                logger.error(f'No access token for platform {platform_account.id}')
                return {'error': 'No access token available'}

            # Fetch conversations based on platform
            conversations = []
            try:
                if platform_account.platform == 'instagram':
                    ig_account_id = platform_account.metadata.get('ig_account_id')
                    if not ig_account_id:
                        logger.error('No Instagram account ID in metadata')
                        return {'error': 'No Instagram account ID configured'}
                    conversations = service_instance.get_conversations(ig_account_id, access_token, limit)
                elif platform_account.platform == 'messenger':
                    page_id = platform_account.platform_user_id
                    conversations = service_instance.get_conversations(page_id, access_token, limit)
                else:
                    logger.warning(f'Sync not implemented for {platform_account.platform}')
                    return {'error': f'Sync not supported for {platform_account.platform}'}
            except Exception as e:
                logger.error(f'Error fetching conversations: {e}')
                return {'error': f'Failed to fetch conversations: {str(e)}'}

            stats['conversations_synced'] = len(conversations)

            # Process each conversation
            for conv_data in conversations:
                try:
                    conversation_id = conv_data.get('id')
                    if not conversation_id:
                        logger.warning('Conversation missing ID, skipping')
                        stats['errors'] += 1
                        continue

                    # Extract participant info from conversation data
                    participants = conv_data.get('participants', {}).get('data', [])
                    participant_id = 'unknown'
                    participant_name = 'Unknown'

                    # Find the other participant (not the page/business account)
                    for participant in participants:
                        if participant.get('id') != platform_account.platform_user_id:
                            participant_id = participant.get('id', 'unknown')
                            participant_name = participant.get('name') or participant.get('username', 'Unknown')
                            break

                    # Get or create conversation
                    conversation, created = Conversation.objects.get_or_create(
                        platform_account=platform_account,
                        platform_conversation_id=conversation_id,
                        defaults={
                            'participant_id': participant_id,
                            'participant_name': participant_name,
                            'last_message_at': timezone.now(),
                        }
                    )

                    # Fetch messages for this conversation
                    try:
                        messages = service_instance.get_conversation_messages(
                            conversation_id,
                            access_token,
                            limit=limit
                        )
                    except Exception as e:
                        logger.error(f'Error fetching messages for conversation {conversation_id}: {e}')
                        stats['errors'] += 1
                        continue

                    stats['messages_synced'] += len(messages)

                    # Store new messages
                    for msg_data in messages:
                        try:
                            message_id = msg_data.get('id')
                            if not message_id:
                                continue

                            # Skip if already exists
                            if Message.objects.filter(platform_message_id=message_id).exists():
                                continue

                            # Extract message details
                            from_data = msg_data.get('from', {})
                            sender_id = from_data.get('id', 'unknown')
                            sender_name = from_data.get('name') or from_data.get('username', 'Unknown')

                            # Determine if incoming (from customer) or outgoing (from page/business)
                            is_incoming = sender_id != platform_account.platform_user_id

                            # Parse timestamp
                            created_time = msg_data.get('created_time')
                            sent_at = timezone.now()
                            if created_time:
                                from dateutil import parser as date_parser
                                try:
                                    sent_at = date_parser.parse(created_time)
                                except Exception:
                                    pass

                            # Determine message type and content
                            message_text = msg_data.get('message', '')
                            attachments = msg_data.get('attachments', {}).get('data', [])
                            message_type = 'text'
                            media_url = None

                            if attachments:
                                attachment = attachments[0]
                                attachment_type = attachment.get('type', '').lower()
                                if attachment_type in ['image', 'video', 'audio', 'file']:
                                    message_type = attachment_type
                                media_url = attachment.get('url') or attachment.get('image_data', {}).get('url')

                            # Create message
                            Message.objects.create(
                                conversation=conversation,
                                platform_account=platform_account,
                                platform_message_id=message_id,
                                message_type=message_type,
                                content=message_text,
                                media_url=media_url,
                                sender_id=sender_id,
                                sender_name=sender_name,
                                is_incoming=is_incoming,
                                sent_at=sent_at,
                            )

                            stats['new_messages'] += 1

                        except Exception as e:
                            logger.error(f'Error creating message {msg_data.get("id")}: {e}')
                            stats['errors'] += 1
                            continue

                    # Update conversation with latest message time
                    if messages:
                        latest_message = Message.objects.filter(
                            conversation=conversation
                        ).order_by('-sent_at').first()

                        if latest_message:
                            conversation.last_message_at = latest_message.sent_at
                            conversation.save()

                except Exception as e:
                    logger.error(f'Error processing conversation {conv_data.get("id")}: {e}')
                    stats['errors'] += 1
                    continue

            logger.info(f'Sync completed for {platform_account.platform}: {stats}')
            return stats

        except Exception as e:
            logger.error(f'Error syncing platform messages: {e}')
            return {'error': str(e)}
