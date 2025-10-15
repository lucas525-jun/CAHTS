"""
Analytics and reporting models
"""
import uuid
from django.db import models
from django.conf import settings


class DailyAnalytics(models.Model):
    """
    Model to store aggregated daily analytics
    """
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('messenger', 'Messenger'),
        ('whatsapp', 'WhatsApp'),
        ('all', 'All Platforms'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='analytics')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    date = models.DateField()

    # Message statistics
    total_messages = models.IntegerField(default=0)
    incoming_messages = models.IntegerField(default=0)
    outgoing_messages = models.IntegerField(default=0)

    # Conversation statistics
    total_conversations = models.IntegerField(default=0)
    new_conversations = models.IntegerField(default=0)

    # Response metrics
    avg_response_time_minutes = models.FloatField(blank=True, null=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'daily_analytics'
        verbose_name = 'Daily Analytics'
        verbose_name_plural = 'Daily Analytics'
        unique_together = [['user', 'platform', 'date']]
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', '-date']),
            models.Index(fields=['user', 'platform', '-date']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.get_platform_display()} - {self.date}"
