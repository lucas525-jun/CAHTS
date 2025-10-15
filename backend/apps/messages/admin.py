from django.contrib import admin
from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['participant_name', 'platform_account', 'last_message_at', 'unread_count', 'is_archived']
    list_filter = ['platform_account__platform', 'is_archived', 'created_at']
    search_fields = ['participant_name', 'participant_id', 'platform_conversation_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-last_message_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender_name', 'message_type', 'is_incoming', 'is_read', 'sent_at', 'platform_account']
    list_filter = ['message_type', 'is_incoming', 'is_read', 'platform_account__platform', 'sent_at']
    search_fields = ['content', 'sender_name', 'platform_message_id']
    readonly_fields = ['id', 'created_at', 'updated_at', 'received_at']
    ordering = ['-sent_at']
