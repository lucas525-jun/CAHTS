"""
Webhook log models
"""
import uuid
from django.db import models


class WebhookLog(models.Model):
    """
    Model to log incoming webhook events for debugging and auditing
    """
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('messenger', 'Messenger'),
        ('whatsapp', 'WhatsApp'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    event_type = models.CharField(max_length=100, help_text="Type of webhook event")

    # Request data
    payload = models.JSONField(help_text="Full webhook payload")
    headers = models.JSONField(default=dict, blank=True, help_text="Request headers")

    # Processing status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processed_at = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'webhook_logs'
        verbose_name = 'Webhook Log'
        verbose_name_plural = 'Webhook Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['platform', 'status']),
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return f"{self.get_platform_display()} - {self.event_type} - {self.get_status_display()}"
