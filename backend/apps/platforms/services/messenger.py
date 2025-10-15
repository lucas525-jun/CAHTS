"""
Messenger API service for managing Facebook Messenger conversations
"""
import logging
from typing import Dict, Any, List, Optional
from .meta_api import MetaAPIService

logger = logging.getLogger(__name__)


class MessengerService(MetaAPIService):
    """
    Service for Facebook Messenger integration
    """

    def get_conversations(self, page_id: str, access_token: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch Messenger conversations

        Args:
            page_id: Facebook Page ID
            access_token: Page access token
            limit: Maximum number of conversations to fetch

        Returns:
            List of conversation objects
        """
        endpoint = f'{page_id}/conversations'
        params = {
            'fields': 'id,participants,updated_time,message_count,unread_count',
            'limit': limit,
        }

        try:
            response = self.make_api_request('GET', endpoint, access_token, params=params)
            return response.get('data', [])
        except Exception as e:
            logger.error(f'Error fetching Messenger conversations: {e}')
            return []

    def get_conversation_messages(
        self,
        conversation_id: str,
        access_token: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Fetch messages from a specific conversation

        Args:
            conversation_id: Messenger conversation ID
            access_token: Page access token
            limit: Maximum number of messages to fetch

        Returns:
            List of message objects
        """
        endpoint = f'{conversation_id}/messages'
        params = {
            'fields': 'id,message,from,created_time,attachments,sticker',
            'limit': limit,
        }

        try:
            response = self.make_api_request('GET', endpoint, access_token, params=params)
            return response.get('data', [])
        except Exception as e:
            logger.error(f'Error fetching Messenger messages: {e}')
            return []

    def send_message(
        self,
        recipient_id: str,
        message_text: str,
        page_id: str,
        access_token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Send a message via Messenger

        Args:
            recipient_id: Recipient PSID (Page-Scoped ID)
            message_text: Message text content
            page_id: Facebook Page ID
            access_token: Page access token

        Returns:
            Response with message ID or None
        """
        endpoint = f'{page_id}/messages'

        data = {
            'recipient': {'id': recipient_id},
            'message': {'text': message_text},
            'messaging_type': 'RESPONSE'
        }

        try:
            response = self.make_api_request('POST', endpoint, access_token, data=data)
            return response
        except Exception as e:
            logger.error(f'Error sending Messenger message: {e}')
            return None

    def send_message_with_attachment(
        self,
        recipient_id: str,
        attachment_type: str,
        attachment_url: str,
        page_id: str,
        access_token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Send a message with attachment

        Args:
            recipient_id: Recipient PSID
            attachment_type: Type (image, video, audio, file)
            attachment_url: URL of the attachment
            page_id: Facebook Page ID
            access_token: Page access token

        Returns:
            Response with message ID or None
        """
        endpoint = f'{page_id}/messages'

        data = {
            'recipient': {'id': recipient_id},
            'message': {
                'attachment': {
                    'type': attachment_type,
                    'payload': {'url': attachment_url}
                }
            }
        }

        try:
            response = self.make_api_request('POST', endpoint, access_token, data=data)
            return response
        except Exception as e:
            logger.error(f'Error sending Messenger attachment: {e}')
            return None

    def get_user_profile(self, user_id: str, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Get Messenger user profile information

        Args:
            user_id: User PSID
            access_token: Page access token

        Returns:
            User profile data
        """
        endpoint = f'{user_id}'
        params = {
            'fields': 'id,name,first_name,last_name,profile_pic',
        }

        try:
            response = self.make_api_request('GET', endpoint, access_token, params=params)
            return response
        except Exception as e:
            logger.error(f'Error fetching Messenger user profile: {e}')
            return None

    def mark_message_as_read(
        self,
        sender_id: str,
        page_id: str,
        access_token: str
    ) -> bool:
        """
        Mark a message as read

        Args:
            sender_id: Sender PSID
            page_id: Facebook Page ID
            access_token: Page access token

        Returns:
            True if successful
        """
        endpoint = f'{page_id}/messages'

        data = {
            'recipient': {'id': sender_id},
            'sender_action': 'mark_seen'
        }

        try:
            self.make_api_request('POST', endpoint, access_token, data=data)
            return True
        except Exception as e:
            logger.error(f'Error marking Messenger message as read: {e}')
            return False

    def parse_webhook_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse Messenger webhook event into standardized format

        Args:
            event: Raw webhook event data

        Returns:
            Parsed event data or None
        """
        try:
            entry = event.get('entry', [])
            if not entry:
                return None

            for item in entry:
                messaging = item.get('messaging', [])
                for message_event in messaging:
                    # Check if it's a message event
                    if 'message' in message_event:
                        msg = message_event['message']

                        return {
                            'platform': 'messenger',
                            'sender_id': message_event.get('sender', {}).get('id'),
                            'recipient_id': message_event.get('recipient', {}).get('id'),
                            'message_id': msg.get('mid'),
                            'message_text': msg.get('text'),
                            'timestamp': message_event.get('timestamp'),
                            'attachments': msg.get('attachments', []),
                            'is_echo': msg.get('is_echo', False),
                        }
            return None
        except Exception as e:
            logger.error(f'Error parsing Messenger webhook event: {e}')
            return None
