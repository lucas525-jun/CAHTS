"""
Instagram API service for managing Instagram Direct Messages
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from .meta_api import MetaAPIService

logger = logging.getLogger(__name__)


class InstagramService(MetaAPIService):
    """
    Service for Instagram Direct Message integration
    """

    def get_conversations(self, ig_account_id: str, access_token: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch Instagram conversations

        Args:
            ig_account_id: Instagram Business Account ID
            access_token: Page access token
            limit: Maximum number of conversations to fetch

        Returns:
            List of conversation objects
        """
        endpoint = f'{ig_account_id}/conversations'
        params = {
            'fields': 'id,participants,messages.limit(1){message,from,created_time}',
            'limit': limit,
        }

        try:
            response = self.make_api_request('GET', endpoint, access_token, params=params)
            return response.get('data', [])
        except Exception as e:
            logger.error(f'Error fetching Instagram conversations: {e}')
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
            conversation_id: Instagram conversation ID
            access_token: Page access token
            limit: Maximum number of messages to fetch

        Returns:
            List of message objects
        """
        endpoint = f'{conversation_id}/messages'
        params = {
            'fields': 'id,message,from,created_time,attachments',
            'limit': limit,
        }

        try:
            response = self.make_api_request('GET', endpoint, access_token, params=params)
            return response.get('data', [])
        except Exception as e:
            logger.error(f'Error fetching Instagram messages: {e}')
            return []

    def send_message(
        self,
        recipient_id: str,
        message_text: str,
        ig_account_id: str,
        access_token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Send a message to an Instagram user

        Args:
            recipient_id: Instagram user ID (IGSID)
            message_text: Message text content
            ig_account_id: Instagram Business Account ID
            access_token: Page access token

        Returns:
            Response with message ID or None
        """
        endpoint = f'{ig_account_id}/messages'

        data = {
            'recipient': {'id': recipient_id},
            'message': {'text': message_text}
        }

        try:
            response = self.make_api_request('POST', endpoint, access_token, data=data)
            return response
        except Exception as e:
            logger.error(f'Error sending Instagram message: {e}')
            return None

    def get_user_profile(self, user_id: str, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Get Instagram user profile information

        Args:
            user_id: Instagram user ID (IGSID)
            access_token: Page access token

        Returns:
            User profile data
        """
        endpoint = f'{user_id}'
        params = {
            'fields': 'id,username,name,profile_pic',
        }

        try:
            response = self.make_api_request('GET', endpoint, access_token, params=params)
            return response
        except Exception as e:
            logger.error(f'Error fetching Instagram user profile: {e}')
            return None

    def mark_message_as_read(
        self,
        message_id: str,
        access_token: str
    ) -> bool:
        """
        Mark a message as read

        Args:
            message_id: Instagram message ID
            access_token: Page access token

        Returns:
            True if successful
        """
        # Note: Instagram API doesn't have a direct "mark as read" endpoint
        # This is handled automatically when messages are fetched
        return True

    def parse_webhook_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse Instagram webhook event into standardized format

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
                changes = item.get('changes', [])
                for change in changes:
                    if change.get('field') == 'messages':
                        value = change.get('value', {})

                        # Extract message data
                        return {
                            'platform': 'instagram',
                            'conversation_id': value.get('thread_id'),
                            'message_id': value.get('mid'),
                            'sender_id': value.get('from', {}).get('id'),
                            'recipient_id': value.get('to', {}).get('id'),
                            'message_text': value.get('message', {}).get('text'),
                            'timestamp': value.get('timestamp'),
                            'attachments': value.get('attachments', []),
                        }
            return None
        except Exception as e:
            logger.error(f'Error parsing Instagram webhook event: {e}')
            return None
