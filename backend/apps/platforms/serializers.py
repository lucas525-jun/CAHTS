"""
Serializers for platform connections
"""
from rest_framework import serializers
from .models import PlatformAccount


class PlatformAccountSerializer(serializers.ModelSerializer):
    """Serializer for platform account details"""

    platform_display = serializers.CharField(source='get_platform_display', read_only=True)

    class Meta:
        model = PlatformAccount
        fields = [
            'id',
            'platform',
            'platform_display',
            'platform_user_id',
            'platform_username',
            'is_active',
            'last_sync_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_sync_at']


class WhatsAppConnectionSerializer(serializers.Serializer):
    """Serializer for WhatsApp connection"""
    phone_number_id = serializers.CharField(required=True)
    access_token = serializers.CharField(required=True, write_only=True)
    business_account_id = serializers.CharField(required=False, allow_blank=True)
