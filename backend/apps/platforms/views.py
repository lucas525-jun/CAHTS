"""
Platform connection views
"""
import secrets
from datetime import datetime, timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import redirect
from django.utils import timezone

from .models import PlatformAccount
from .serializers import PlatformAccountSerializer, WhatsAppConnectionSerializer
from .services import MetaAPIService, InstagramService, MessengerService, WhatsAppService


class PlatformViewSet(viewsets.ViewSet):
    """
    ViewSet for managing platform connections
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """List all connected platforms for the current user"""
        platforms = PlatformAccount.objects.filter(user=request.user)
        serializer = PlatformAccountSerializer(platforms, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='instagram/connect')
    def connect_instagram(self, request):
        """
        Initiate Instagram OAuth connection
        Returns OAuth URL for user to authorize
        """
        meta_service = MetaAPIService()

        # Generate state token for CSRF protection
        state = secrets.token_urlsafe(32)
        request.session['oauth_state'] = state
        request.session['oauth_platform'] = 'instagram'

        # Get OAuth URL
        oauth_url = meta_service.get_oauth_url('instagram', state=state)

        return Response({
            'oauth_url': oauth_url,
            'message': 'Redirect user to this URL to authorize Instagram connection'
        })

    @action(detail=False, methods=['get'], url_path='messenger/connect')
    def connect_messenger(self, request):
        """
        Initiate Messenger OAuth connection
        Returns OAuth URL for user to authorize
        """
        meta_service = MetaAPIService()

        # Generate state token for CSRF protection
        state = secrets.token_urlsafe(32)
        request.session['oauth_state'] = state
        request.session['oauth_platform'] = 'messenger'

        # Get OAuth URL
        oauth_url = meta_service.get_oauth_url('messenger', state=state)

        return Response({
            'oauth_url': oauth_url,
            'message': 'Redirect user to this URL to authorize Messenger connection'
        })

    @action(detail=False, methods=['post'], url_path='whatsapp/connect')
    def connect_whatsapp(self, request):
        """
        Connect WhatsApp Business account using provided credentials
        """
        serializer = WhatsAppConnectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number_id = serializer.validated_data['phone_number_id']
        access_token = serializer.validated_data['access_token']
        business_account_id = serializer.validated_data.get('business_account_id', phone_number_id)

        # Validate the credentials
        whatsapp_service = WhatsAppService()
        validation_result = whatsapp_service.validate_credentials(phone_number_id, access_token)

        if not validation_result.get('valid'):
            return Response({
                'error': 'invalid_credentials',
                'message': validation_result.get('error', 'Failed to validate WhatsApp credentials')
            }, status=status.HTTP_400_BAD_REQUEST)

        # Use validated data
        verified_name = validation_result.get('verified_name', phone_number_id)
        display_phone = validation_result.get('display_phone_number', phone_number_id)

        # Encrypt and store token
        platform_account = PlatformAccount.objects.create(
            user=request.user,
            platform='whatsapp',
            platform_user_id=business_account_id or phone_number_id,
            platform_username=verified_name,
            access_token=access_token,  # Will be encrypted on save
            is_active=True,
            metadata={
                'phone_number_id': phone_number_id,
                'business_account_id': business_account_id,
                'verified_name': verified_name,
                'display_phone_number': display_phone,
                'quality_rating': validation_result.get('quality_rating'),
            }
        )

        return Response({
            'message': 'WhatsApp connected successfully',
            'platform': PlatformAccountSerializer(platform_account).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='callback', permission_classes=[AllowAny])
    def oauth_callback(self, request):
        """
        OAuth callback endpoint for Instagram and Messenger
        Handles the redirect after user authorizes the app
        """
        # Get authorization code and state
        code = request.query_params.get('code')
        state = request.query_params.get('state')
        error = request.query_params.get('error')

        # Handle error
        if error:
            return Response({
                'error': error,
                'error_description': request.query_params.get('error_description', 'Authorization failed')
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verify state (CSRF protection)
        session_state = request.session.get('oauth_state')
        if not state or state != session_state:
            return Response({
                'error': 'invalid_state',
                'message': 'Invalid state parameter'
            }, status=status.HTTP_400_BAD_REQUEST)

        platform = request.session.get('oauth_platform')
        if not platform:
            return Response({
                'error': 'invalid_session',
                'message': 'OAuth session expired'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            meta_service = MetaAPIService()

            # Exchange code for access token
            token_response = meta_service.exchange_code_for_token(code)
            short_lived_token = token_response.get('access_token')

            # Get long-lived token (60 days)
            long_lived_response = meta_service.get_long_lived_token(short_lived_token)
            access_token = long_lived_response.get('access_token')
            expires_in = long_lived_response.get('expires_in', 5184000)  # Default 60 days

            # Get user's pages
            pages = meta_service.get_user_pages(access_token)

            if not pages:
                return Response({
                    'error': 'no_pages',
                    'message': 'No Facebook Pages found. Please create a page first.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # For this example, use the first page
            # In production, let user select which page to connect
            page = pages[0]
            page_id = page['id']
            page_name = page['name']
            page_access_token = page['access_token']

            if platform == 'instagram':
                # Get Instagram Business Account linked to the page
                ig_account_id = meta_service.get_instagram_business_account(page_id, page_access_token)

                if not ig_account_id:
                    return Response({
                        'error': 'no_instagram_account',
                        'message': 'No Instagram Business Account linked to this page.'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Store Instagram connection
                platform_account, created = PlatformAccount.objects.update_or_create(
                    user=request.user,
                    platform='instagram',
                    platform_user_id=ig_account_id,
                    defaults={
                        'platform_username': page_name,
                        'access_token': page_access_token,  # Should be encrypted
                        'token_expires_at': timezone.now() + timedelta(seconds=expires_in),
                        'is_active': True,
                        'metadata': {
                            'page_id': page_id,
                            'page_name': page_name,
                            'ig_account_id': ig_account_id,
                        }
                    }
                )

            elif platform == 'messenger':
                # Store Messenger connection
                platform_account, created = PlatformAccount.objects.update_or_create(
                    user=request.user,
                    platform='messenger',
                    platform_user_id=page_id,
                    defaults={
                        'platform_username': page_name,
                        'access_token': page_access_token,  # Should be encrypted
                        'token_expires_at': timezone.now() + timedelta(seconds=expires_in),
                        'is_active': True,
                        'metadata': {
                            'page_id': page_id,
                            'page_name': page_name,
                        }
                    }
                )

            # Clear session
            request.session.pop('oauth_state', None)
            request.session.pop('oauth_platform', None)

            return Response({
                'message': f'{platform.capitalize()} connected successfully',
                'platform': PlatformAccountSerializer(platform_account).data
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': 'connection_failed',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['delete'])
    def disconnect(self, request, pk=None):
        """Disconnect a platform"""
        try:
            platform_account = PlatformAccount.objects.get(
                id=pk,
                user=request.user
            )
            platform_name = platform_account.get_platform_display()
            platform_account.delete()

            return Response({
                'message': f'{platform_name} disconnected successfully'
            })
        except PlatformAccount.DoesNotExist:
            return Response({
                'error': 'Platform not found'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Manually trigger sync for a platform"""
        try:
            platform_account = PlatformAccount.objects.get(
                id=pk,
                user=request.user
            )

            # Trigger appropriate sync task based on platform
            from apps.messages.tasks import (
                sync_instagram_messages,
                sync_messenger_messages,
                sync_whatsapp_messages
            )

            task_id = None
            if platform_account.platform == 'instagram':
                result = sync_instagram_messages.delay(str(platform_account.id))
                task_id = result.id
            elif platform_account.platform == 'messenger':
                result = sync_messenger_messages.delay(str(platform_account.id))
                task_id = result.id
            elif platform_account.platform == 'whatsapp':
                result = sync_whatsapp_messages.delay(str(platform_account.id))
                task_id = result.id

            return Response({
                'message': 'Sync started',
                'task_id': task_id,
                'platform': PlatformAccountSerializer(platform_account).data
            })
        except PlatformAccount.DoesNotExist:
            return Response({
                'error': 'Platform not found'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], url_path='instagram/complete-oauth')
    def complete_instagram_oauth(self, request):
        """
        Stateless Instagram OAuth completion endpoint
        Called by frontend with code and state from OAuth callback
        """
        code = request.data.get('code')
        state = request.data.get('state')

        if not code:
            return Response({
                'error': 'missing_code',
                'message': 'Authorization code is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            meta_service = MetaAPIService()

            # Exchange code for access token
            token_response = meta_service.exchange_code_for_token(code)
            short_lived_token = token_response.get('access_token')

            if not short_lived_token:
                return Response({
                    'error': 'token_exchange_failed',
                    'message': 'Failed to exchange code for token'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get long-lived token (60 days)
            long_lived_response = meta_service.get_long_lived_token(short_lived_token)
            access_token = long_lived_response.get('access_token')
            expires_in = long_lived_response.get('expires_in', 5184000)  # Default 60 days

            # Get user's pages
            pages = meta_service.get_user_pages(access_token)

            if not pages:
                return Response({
                    'error': 'no_pages',
                    'message': 'No Facebook Pages found. Please create a page first.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Use the first page (in production, let user select)
            page = pages[0]
            page_id = page['id']
            page_name = page['name']
            page_access_token = page['access_token']

            # Get Instagram Business Account linked to the page
            ig_account_id = meta_service.get_instagram_business_account(page_id, page_access_token)

            if not ig_account_id:
                return Response({
                    'error': 'no_instagram_account',
                    'message': 'No Instagram Business Account linked to this page.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Store Instagram connection
            platform_account, created = PlatformAccount.objects.update_or_create(
                user=request.user,
                platform='instagram',
                platform_user_id=ig_account_id,
                defaults={
                    'platform_username': page_name,
                    'access_token': page_access_token,  # Will be encrypted when save() is fixed
                    'token_expires_at': timezone.now() + timedelta(seconds=expires_in),
                    'is_active': True,
                    'metadata': {
                        'page_id': page_id,
                        'page_name': page_name,
                        'ig_account_id': ig_account_id,
                    }
                }
            )

            return Response({
                'message': 'Instagram connected successfully',
                'platform': PlatformAccountSerializer(platform_account).data
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': 'connection_failed',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='messenger/complete-oauth')
    def complete_messenger_oauth(self, request):
        """
        Stateless Messenger OAuth completion endpoint
        Called by frontend with code and state from OAuth callback
        """
        code = request.data.get('code')
        state = request.data.get('state')

        if not code:
            return Response({
                'error': 'missing_code',
                'message': 'Authorization code is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            meta_service = MetaAPIService()

            # Exchange code for access token
            token_response = meta_service.exchange_code_for_token(code)
            short_lived_token = token_response.get('access_token')

            if not short_lived_token:
                return Response({
                    'error': 'token_exchange_failed',
                    'message': 'Failed to exchange code for token'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get long-lived token (60 days)
            long_lived_response = meta_service.get_long_lived_token(short_lived_token)
            access_token = long_lived_response.get('access_token')
            expires_in = long_lived_response.get('expires_in', 5184000)  # Default 60 days

            # Get user's pages
            pages = meta_service.get_user_pages(access_token)

            if not pages:
                return Response({
                    'error': 'no_pages',
                    'message': 'No Facebook Pages found. Please create a page first.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Use the first page (in production, let user select)
            page = pages[0]
            page_id = page['id']
            page_name = page['name']
            page_access_token = page['access_token']

            # Store Messenger connection
            platform_account, created = PlatformAccount.objects.update_or_create(
                user=request.user,
                platform='messenger',
                platform_user_id=page_id,
                defaults={
                    'platform_username': page_name,
                    'access_token': page_access_token,  # Will be encrypted when save() is fixed
                    'token_expires_at': timezone.now() + timedelta(seconds=expires_in),
                    'is_active': True,
                    'metadata': {
                        'page_id': page_id,
                        'page_name': page_name,
                    }
                }
            )

            return Response({
                'message': 'Messenger connected successfully',
                'platform': PlatformAccountSerializer(platform_account).data
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': 'connection_failed',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
