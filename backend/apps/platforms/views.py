from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class PlatformViewSet(viewsets.ViewSet):
    """
    ViewSet for managing platform connections
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """List all connected platforms for the current user"""
        # TODO: Implement platform listing
        return Response({'message': 'Platform list endpoint - to be implemented'})

    @action(detail=False, methods=['post'], url_path='instagram/connect')
    def connect_instagram(self, request):
        """Initiate Instagram OAuth connection"""
        # TODO: Implement Instagram OAuth flow
        return Response({'message': 'Instagram connection - to be implemented'})

    @action(detail=False, methods=['post'], url_path='messenger/connect')
    def connect_messenger(self, request):
        """Initiate Messenger OAuth connection"""
        # TODO: Implement Messenger OAuth flow
        return Response({'message': 'Messenger connection - to be implemented'})

    @action(detail=False, methods=['post'], url_path='whatsapp/connect')
    def connect_whatsapp(self, request):
        """Connect WhatsApp Business account"""
        # TODO: Implement WhatsApp connection
        return Response({'message': 'WhatsApp connection - to be implemented'})
