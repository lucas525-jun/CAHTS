from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def instagram_webhook(request):
    """
    Handle Instagram webhook events
    GET: Webhook verification
    POST: Webhook event processing
    """
    if request.method == 'GET':
        # TODO: Implement webhook verification
        return Response({'message': 'Instagram webhook verification - to be implemented'})

    # TODO: Implement webhook event processing
    return Response({'message': 'Instagram webhook event - to be implemented'})


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def messenger_webhook(request):
    """
    Handle Messenger webhook events
    GET: Webhook verification
    POST: Webhook event processing
    """
    if request.method == 'GET':
        # TODO: Implement webhook verification
        return Response({'message': 'Messenger webhook verification - to be implemented'})

    # TODO: Implement webhook event processing
    return Response({'message': 'Messenger webhook event - to be implemented'})


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def whatsapp_webhook(request):
    """
    Handle WhatsApp webhook events
    GET: Webhook verification
    POST: Webhook event processing
    """
    if request.method == 'GET':
        # TODO: Implement webhook verification
        return Response({'message': 'WhatsApp webhook verification - to be implemented'})

    # TODO: Implement webhook event processing
    return Response({'message': 'WhatsApp webhook event - to be implemented'})
