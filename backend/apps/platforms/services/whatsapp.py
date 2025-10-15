"""
WhatsApp Business API service
"""
import requests
import logging
from typing import Dict, Any, List, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    """
    Service for WhatsApp Business API integration
    """

    def __init__(self):
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.business_account_id = settings.WHATSAPP_BUSINESS_ACCOUNT_ID
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.api_version = settings.META_API_VERSION
        self.base_url = f'https://graph.facebook.com/{self.api_version}'

    def send_text_message(
        self,
        recipient_phone: str,
        message_text: str,
        phone_number_id: str = None,
        access_token: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Send a text message via WhatsApp

        Args:
            recipient_phone: Recipient phone number (international format)
            message_text: Message text content
            phone_number_id: WhatsApp Phone Number ID (optional, uses default if not provided)
            access_token: Access token (optional, uses default if not provided)

        Returns:
            Response with message ID or None
        """
        phone_id = phone_number_id or self.phone_number_id
        token = access_token or self.access_token

        url = f'{self.base_url}/{phone_id}/messages'

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }

        data = {
            'messaging_product': 'whatsapp',
            'to': recipient_phone,
            'type': 'text',
            'text': {'body': message_text}
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f'Error sending WhatsApp message: {e}')
            return None

    def send_template_message(
        self,
        recipient_phone: str,
        template_name: str,
        language_code: str = 'en',
        parameters: List[str] = None,
        phone_number_id: str = None,
        access_token: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Send a template message via WhatsApp

        Args:
            recipient_phone: Recipient phone number
            template_name: Name of the approved template
            language_code: Template language code
            parameters: Template parameter values
            phone_number_id: WhatsApp Phone Number ID
            access_token: Access token

        Returns:
            Response with message ID or None
        """
        phone_id = phone_number_id or self.phone_number_id
        token = access_token or self.access_token

        url = f'{self.base_url}/{phone_id}/messages'

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }

        # Build template components
        components = []
        if parameters:
            components.append({
                'type': 'body',
                'parameters': [{'type': 'text', 'text': param} for param in parameters]
            })

        data = {
            'messaging_product': 'whatsapp',
            'to': recipient_phone,
            'type': 'template',
            'template': {
                'name': template_name,
                'language': {'code': language_code},
                'components': components
            }
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f'Error sending WhatsApp template: {e}')
            return None

    def send_media_message(
        self,
        recipient_phone: str,
        media_type: str,
        media_url: str,
        caption: str = None,
        phone_number_id: str = None,
        access_token: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Send a media message (image, video, audio, document)

        Args:
            recipient_phone: Recipient phone number
            media_type: Type (image, video, audio, document)
            media_url: URL of the media file
            caption: Optional caption
            phone_number_id: WhatsApp Phone Number ID
            access_token: Access token

        Returns:
            Response with message ID or None
        """
        phone_id = phone_number_id or self.phone_number_id
        token = access_token or self.access_token

        url = f'{self.base_url}/{phone_id}/messages'

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }

        media_object = {'link': media_url}
        if caption and media_type in ['image', 'video', 'document']:
            media_object['caption'] = caption

        data = {
            'messaging_product': 'whatsapp',
            'to': recipient_phone,
            'type': media_type,
            media_type: media_object
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f'Error sending WhatsApp media: {e}')
            return None

    def mark_message_as_read(
        self,
        message_id: str,
        phone_number_id: str = None,
        access_token: str = None
    ) -> bool:
        """
        Mark a message as read

        Args:
            message_id: WhatsApp message ID
            phone_number_id: WhatsApp Phone Number ID
            access_token: Access token

        Returns:
            True if successful
        """
        phone_id = phone_number_id or self.phone_number_id
        token = access_token or self.access_token

        url = f'{self.base_url}/{phone_id}/messages'

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }

        data = {
            'messaging_product': 'whatsapp',
            'status': 'read',
            'message_id': message_id
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f'Error marking WhatsApp message as read: {e}')
            return False

    def get_media_url(
        self,
        media_id: str,
        access_token: str = None
    ) -> Optional[str]:
        """
        Get media URL from media ID

        Args:
            media_id: WhatsApp media ID
            access_token: Access token

        Returns:
            Media URL or None
        """
        token = access_token or self.access_token

        url = f'{self.base_url}/{media_id}'

        headers = {
            'Authorization': f'Bearer {token}',
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('url')
        except requests.exceptions.RequestException as e:
            logger.error(f'Error getting WhatsApp media URL: {e}')
            return None

    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Verify webhook signature from WhatsApp

        Args:
            payload: Request body as string
            signature: X-Hub-Signature-256 header value

        Returns:
            True if signature is valid
        """
        import hmac
        import hashlib

        app_secret = settings.META_APP_SECRET

        if not signature.startswith('sha256='):
            return False

        expected_signature = hmac.new(
            app_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        received_signature = signature.replace('sha256=', '')

        return hmac.compare_digest(expected_signature, received_signature)

    def validate_credentials(
        self,
        phone_number_id: str,
        access_token: str
    ) -> Dict[str, Any]:
        """
        Validate WhatsApp Business credentials by fetching phone number info

        Args:
            phone_number_id: WhatsApp Phone Number ID
            access_token: Access token

        Returns:
            Dict with 'valid' boolean and optional error message or phone data
        """
        url = f'{self.base_url}/{phone_number_id}'

        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        params = {
            'fields': 'id,verified_name,display_phone_number,quality_rating'
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            return {
                'valid': True,
                'phone_number_id': data.get('id'),
                'verified_name': data.get('verified_name'),
                'display_phone_number': data.get('display_phone_number'),
                'quality_rating': data.get('quality_rating')
            }
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return {
                    'valid': False,
                    'error': 'Invalid access token'
                }
            elif e.response.status_code == 404:
                return {
                    'valid': False,
                    'error': 'Phone number ID not found'
                }
            else:
                return {
                    'valid': False,
                    'error': f'HTTP {e.response.status_code}: {e.response.text}'
                }
        except requests.exceptions.RequestException as e:
            logger.error(f'Error validating WhatsApp credentials: {e}')
            return {
                'valid': False,
                'error': f'Connection error: {str(e)}'
            }

    def parse_webhook_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse WhatsApp webhook event into standardized format

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
                    value = change.get('value', {})

                    # Check for message
                    messages = value.get('messages', [])
                    if messages:
                        msg = messages[0]

                        # Extract message content based on type
                        message_text = None
                        media_id = None
                        message_type = msg.get('type', 'text')

                        if message_type == 'text':
                            message_text = msg.get('text', {}).get('body')
                        elif message_type in ['image', 'video', 'audio', 'document']:
                            media_id = msg.get(message_type, {}).get('id')
                            if message_type in ['image', 'video', 'document']:
                                message_text = msg.get(message_type, {}).get('caption')

                        return {
                            'platform': 'whatsapp',
                            'message_id': msg.get('id'),
                            'sender_phone': msg.get('from'),
                            'recipient_phone': value.get('metadata', {}).get('display_phone_number'),
                            'message_text': message_text,
                            'message_type': message_type,
                            'media_id': media_id,
                            'timestamp': msg.get('timestamp'),
                        }

                    # Check for status update
                    statuses = value.get('statuses', [])
                    if statuses:
                        status = statuses[0]
                        return {
                            'platform': 'whatsapp',
                            'event_type': 'status',
                            'message_id': status.get('id'),
                            'status': status.get('status'),  # sent, delivered, read, failed
                            'timestamp': status.get('timestamp'),
                        }

            return None
        except Exception as e:
            logger.error(f'Error parsing WhatsApp webhook event: {e}')
            return None
