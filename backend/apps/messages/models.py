"""
Message and conversation models
"""
import uuid
from django.db import models
from django.conf import settings


class Conversation(models.Model):
    """
    Model to group messages by conversation/thread
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    platform_account = models.ForeignKey(
        'platforms.PlatformAccount',
        on_delete=models.CASCADE,
        related_name='conversations'
    )
    platform_conversation_id = models.CharField(max_length=255, help_text="Conversation ID from platform")

    # Participant info
    participant_id = models.CharField(max_length=255)
    participant_name = models.CharField(max_length=255)
    participant_avatar = models.URLField(blank=True, null=True)

    # Status
    last_message_at = models.DateTimeField()
    unread_count = models.IntegerField(default=0)
    is_archived = models.BooleanField(default=False)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'conversations'
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        unique_together = [['platform_account', 'platform_conversation_id']]
        ordering = ['-last_message_at']
        indexes = [
            models.Index(fields=['-last_message_at']),
            models.Index(fields=['platform_account', 'is_archived']),
        ]

    def __str__(self):
        return f"{self.participant_name} - {self.platform_account.get_platform_display()}"


class Message(models.Model):
    """
    Model to store individual messages
    """
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('file', 'File'),
        ('sticker', 'Sticker'),
        ('location', 'Location'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    platform_account = models.ForeignKey(
        'platforms.PlatformAccount',
        on_delete=models.CASCADE,
        related_name='messages'
    )
    platform_message_id = models.CharField(max_length=255, unique=True, help_text="Message ID from platform")

    # Message content
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    content = models.TextField(blank=True, null=True)
    media_url = models.URLField(blank=True, null=True)

    # Sender info
    sender_id = models.CharField(max_length=255)
    sender_name = models.CharField(max_length=255)
    is_incoming = models.BooleanField(default=True, help_text="True if from user, False if sent by page/business")

    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)

    # Timestamps
    sent_at = models.DateTimeField()
    received_at = models.DateTimeField(auto_now_add=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional message data")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'messages'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['-sent_at']),
            models.Index(fields=['conversation', '-sent_at']),
            models.Index(fields=['platform_account', 'is_read']),
            models.Index(fields=['platform_message_id']),
        ]

    def __str__(self):
        content_preview = self.content[:50] if self.content else f"[{self.message_type}]"
        return f"{self.sender_name}: {content_preview}"
