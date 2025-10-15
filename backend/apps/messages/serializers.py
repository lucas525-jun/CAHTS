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

    messages = MessageSerializer(many=True, read_only=True)

    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + ['messages']
