"""
Serializers for messages and conversations
"""
from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for message details"""

    platform = serializers.CharField(source='platform_account.get_platform_display', read_only=True)
    conversation_participant = serializers.CharField(source='conversation.participant_name', read_only=True)

    class Meta:
        model = Message
        fields = [
            'id',
            'conversation',
            'conversation_participant',
            'platform',
            'platform_message_id',
            'message_type',
            'content',
            'media_url',
            'sender_id',
            'sender_name',
            'is_incoming',
            'is_read',
            'read_at',
            'delivered_at',
            'sent_at',
            'created_at',
        ]
        read_only_fields = ['id', 'platform_message_id', 'created_at', 'sent_at']


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for conversation details"""

    platform = serializers.CharField(source='platform_account.get_platform_display', read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id',
            'platform',
            'platform_conversation_id',
            'participant_id',
            'participant_name',
            'participant_avatar',
            'last_message_at',
            'unread_count',
            'is_archived',
            'last_message',
            'created_at',
        ]
        read_only_fields = ['id', 'platform_conversation_id', 'created_at']

    def get_last_message(self, obj):
        """Get the last message in the conversation"""
        last_msg = obj.messages.order_by('-sent_at').first()
        if last_msg:
            return {
                'id': str(last_msg.id),
                'content': last_msg.content[:100],  # Preview
                'sender_name': last_msg.sender_name,
                'sent_at': last_msg.sent_at,
                'is_read': last_msg.is_read,
            }
        return None


class ConversationDetailSerializer(ConversationSerializer):
    """Detailed serializer with recent messages"""

    messages = serializers.SerializerMethodField()

    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + ['messages']

    def get_messages(self, obj):
        """Get recent messages with optional limit from context"""
        messages_limit = self.context.get('messages_limit', 50)
        recent_messages = obj.messages.all().order_by('-sent_at')[:messages_limit]
        return MessageSerializer(recent_messages, many=True).data


class SendMessageSerializer(serializers.Serializer):
    """Serializer for sending messages"""

    content = serializers.CharField(required=True, max_length=5000, help_text="Message text content")
    message_type = serializers.ChoiceField(
        choices=['text', 'image', 'video', 'audio', 'file'],
        default='text',
        help_text="Type of message"
    )
    media_url = serializers.URLField(required=False, allow_blank=True, help_text="URL for media messages")

    def validate(self, data):
        """Validate that media_url is provided for non-text messages"""
        if data.get('message_type') != 'text' and not data.get('media_url'):
            raise serializers.ValidationError({
                'media_url': 'Media URL is required for non-text messages'
            })
        return data
