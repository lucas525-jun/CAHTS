"""
Custom middleware for WebSocket JWT authentication
"""
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from urllib.parse import parse_qs
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@database_sync_to_async
def get_user_from_token(token_string):
    """
    Get user from JWT token
    """
    try:
        # Validate and decode the token
        access_token = AccessToken(token_string)
        user_id = access_token['user_id']

        # Get the user
        user = User.objects.get(id=user_id)
        logger.info(f"WebSocket authenticated user: {user.email}")
        return user
    except TokenError as e:
        logger.warning(f"WebSocket token error: {str(e)}")
        return AnonymousUser()
    except User.DoesNotExist:
        logger.warning(f"WebSocket user not found for token")
        return AnonymousUser()
    except KeyError as e:
        logger.warning(f"WebSocket token missing key: {str(e)}")
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """
    Custom middleware to authenticate WebSocket connections using JWT
    """

    async def __call__(self, scope, receive, send):
        # Extract token from query string
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)

        # Try to get token from query params
        token = None
        if 'token' in query_params:
            token = query_params['token'][0]
            logger.info(f"WebSocket token found in query params")

        # If no token in query params, try headers
        if not token:
            headers = dict(scope.get('headers', []))
            auth_header = headers.get(b'authorization', b'').decode()
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
                logger.info(f"WebSocket token found in headers")

        # Authenticate user
        if token:
            scope['user'] = await get_user_from_token(token)
        else:
            logger.warning("WebSocket no token provided")
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)
