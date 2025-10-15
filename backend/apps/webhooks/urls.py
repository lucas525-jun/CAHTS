from django.urls import path
from .views import instagram_webhook, messenger_webhook, whatsapp_webhook

urlpatterns = [
    path('instagram/', instagram_webhook, name='instagram_webhook'),
    path('messenger/', messenger_webhook, name='messenger_webhook'),
    path('whatsapp/', whatsapp_webhook, name='whatsapp_webhook'),
]
