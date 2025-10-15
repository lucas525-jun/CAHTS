"""
WebSocket URL routing for messages
"""
from django.urls import path, re_path
from .consumers import MessageConsumer

websocket_urlpatterns = [
    path('ws/messages/', MessageConsumer.as_asgi()),
    re_path(r'^ws/messages/(?P<user_id>[0-9a-f-]+)/$', MessageConsumer.as_asgi()),
]
