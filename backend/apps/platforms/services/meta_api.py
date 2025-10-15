"""
Base Meta Graph API service for Instagram and Messenger
"""
import requests
import logging
from typing import Dict, Any, Optional
from django.conf import settings
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class MetaAPIService:
    """
    Base service for interacting with Meta Graph API
    Used by both Instagram and Messenger services
    """

    def __init__(self):
        self.app_id = settings.META_APP_ID
        self.app_secret = settings.META_APP_SECRET
        self.redirect_uri = settings.META_REDIRECT_URI
        self.api_version = settings.META_API_VERSION
        self.base_url = f'https://graph.facebook.com/{self.api_version}'

    def get_oauth_url(self, platform: str, state: str = None) -> str:
        """
        Generate OAuth authorization URL

        Args:
            platform: 'instagram' or 'messenger'
            state: Optional state parameter for CSRF protection

        Returns:
            Authorization URL
        """
        scopes = self._get_scopes(platform)

        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'scope': ','.join(scopes),
            'response_type': 'code',
        }

        if state:
            params['state'] = state

        return f'https://www.facebook.com/{self.api_version}/dialog/oauth?{urlencode(params)}'

    def _get_scopes(self, platform: str) -> list:
        """Get required OAuth scopes for platform"""
        if platform == 'instagram':
            return [
                'instagram_basic',
                'instagram_manage_messages',
                'pages_show_list',
                'pages_messaging',
            ]
        elif platform == 'messenger':
            return [
                'pages_show_list',
                'pages_messaging',
                'pages_manage_metadata',
            ]
        return []

    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Token response with access_token and expires_in
        """
        url = f'{self.base_url}/oauth/access_token'

        params = {
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'redirect_uri': self.redirect_uri,
            'code': code,
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f'Error exchanging code for token: {e}')
            raise

    def get_long_lived_token(self, short_lived_token: str) -> Dict[str, Any]:
        """
        Exchange short-lived token for long-lived token (60 days)

        Args:
            short_lived_token: Short-lived access token

        Returns:
            Long-lived token response
        """
        url = f'{self.base_url}/oauth/access_token'

        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'fb_exchange_token': short_lived_token,
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f'Error getting long-lived token: {e}')
            raise

    def get_user_pages(self, access_token: str) -> list:
        """
        Get list of Facebook Pages the user manages

        Args:
            access_token: User access token

        Returns:
            List of pages with id, name, and access_token
        """
        url = f'{self.base_url}/me/accounts'

        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('data', [])
        except requests.exceptions.RequestException as e:
            logger.error(f'Error fetching user pages: {e}')
            raise

    def get_instagram_business_account(self, page_id: str, page_access_token: str) -> Optional[str]:
        """
        Get Instagram Business Account ID linked to a Facebook Page

        Args:
            page_id: Facebook Page ID
            page_access_token: Page access token

        Returns:
            Instagram Business Account ID or None
        """
        url = f'{self.base_url}/{page_id}'

        params = {
            'fields': 'instagram_business_account',
        }

        headers = {
            'Authorization': f'Bearer {page_access_token}',
        }

        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            ig_account = data.get('instagram_business_account', {})
            return ig_account.get('id')
        except requests.exceptions.RequestException as e:
            logger.error(f'Error fetching Instagram business account: {e}')
            return None

    def make_api_request(
        self,
        method: str,
        endpoint: str,
        access_token: str,
        params: Dict[str, Any] = None,
        data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Make a request to Meta Graph API

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., 'me/messages')
            access_token: Access token
            params: Query parameters
            data: Request body data

        Returns:
            API response data
        """
        url = f'{self.base_url}/{endpoint}'

        if params is None:
            params = {}

        # Use Authorization header instead of query parameter for security
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }

        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, params=params, json=data, headers=headers, timeout=10)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, params=params, headers=headers, timeout=10)
            else:
                raise ValueError(f'Unsupported HTTP method: {method}')

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f'API request error: {method} {endpoint} - {e}')
            raise

    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Verify webhook signature from Meta

        Args:
            payload: Request body as string
            signature: X-Hub-Signature-256 header value

        Returns:
            True if signature is valid
        """
        import hmac
        import hashlib

        if not signature.startswith('sha256='):
            return False

        expected_signature = hmac.new(
            self.app_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        received_signature = signature.replace('sha256=', '')

        return hmac.compare_digest(expected_signature, received_signature)
