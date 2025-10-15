"""
File upload views for message attachments
"""
import os
import uuid
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import logging

logger = logging.getLogger(__name__)

# Allowed file types and sizes
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/webm']
ALLOWED_AUDIO_TYPES = ['audio/mpeg', 'audio/ogg', 'audio/wav', 'audio/webm']
ALLOWED_DOCUMENT_TYPES = ['application/pdf', 'application/msword',
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                          'application/vnd.ms-excel',
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                          'text/plain']

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_VIDEO_SIZE = 25 * 1024 * 1024  # 25MB


def get_file_type(content_type: str) -> str:
    """Determine file type from content type"""
    if content_type in ALLOWED_IMAGE_TYPES:
        return 'image'
    elif content_type in ALLOWED_VIDEO_TYPES:
        return 'video'
    elif content_type in ALLOWED_AUDIO_TYPES:
        return 'audio'
    elif content_type in ALLOWED_DOCUMENT_TYPES:
        return 'file'
    return None


def validate_file(file, content_type: str):
    """Validate file size and type"""
    file_type = get_file_type(content_type)

    if not file_type:
        return False, 'File type not allowed', None

    # Check file size
    max_size = MAX_VIDEO_SIZE if file_type == 'video' else MAX_FILE_SIZE
    if file.size > max_size:
        return False, f'File too large. Max size: {max_size / (1024*1024)}MB', None

    return True, None, file_type


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_file(request):
    """
    Upload a file for message attachment

    Accepts: image, video, audio, document files
    Returns: media_url, file_type, file_size
    """
    if 'file' not in request.FILES:
        return Response({
            'error': 'No file provided',
            'detail': 'Please upload a file using the "file" field'
        }, status=status.HTTP_400_BAD_REQUEST)

    uploaded_file = request.FILES['file']
    content_type = uploaded_file.content_type

    # Validate file
    is_valid, error_msg, file_type = validate_file(uploaded_file, content_type)
    if not is_valid:
        return Response({
            'error': 'Invalid file',
            'detail': error_msg
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Generate unique filename
        file_extension = os.path.splitext(uploaded_file.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        # Create directory structure: media/uploads/{user_id}/{file_type}/
        user_id = request.user.id
        upload_path = f"uploads/{user_id}/{file_type}/{unique_filename}"

        # Save file
        file_path = default_storage.save(upload_path, ContentFile(uploaded_file.read()))

        # Generate full URL
        media_url = request.build_absolute_uri(settings.MEDIA_URL + file_path)

        logger.info(f"File uploaded successfully: {file_path} by user {user_id}")

        return Response({
            'message': 'File uploaded successfully',
            'data': {
                'media_url': media_url,
                'file_type': file_type,
                'file_name': uploaded_file.name,
                'file_size': uploaded_file.size,
                'content_type': content_type
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return Response({
            'error': 'Upload failed',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_upload_limits(request):
    """
    Get file upload limits and allowed types
    """
    return Response({
        'max_file_size': MAX_FILE_SIZE,
        'max_video_size': MAX_VIDEO_SIZE,
        'allowed_types': {
            'image': ALLOWED_IMAGE_TYPES,
            'video': ALLOWED_VIDEO_TYPES,
            'audio': ALLOWED_AUDIO_TYPES,
            'document': ALLOWED_DOCUMENT_TYPES
        }
    })
