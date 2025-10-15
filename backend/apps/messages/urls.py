from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, ConversationViewSet, search_messages
from .upload_views import upload_file, get_upload_limits

router = DefaultRouter()
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'conversations', ConversationViewSet, basename='conversation')

urlpatterns = [
    path('', include(router.urls)),
    path('upload/', upload_file, name='upload-file'),
    path('upload/limits/', get_upload_limits, name='upload-limits'),
    path('search/', search_messages, name='search-messages'),
]
