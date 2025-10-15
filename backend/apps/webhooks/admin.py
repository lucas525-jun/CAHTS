from django.contrib import admin
from .models import WebhookLog


@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    list_display = ['platform', 'event_type', 'status', 'created_at', 'processed_at']
    list_filter = ['platform', 'status', 'event_type', 'created_at']
    search_fields = ['event_type', 'error_message']
    readonly_fields = ['id', 'created_at', 'updated_at', 'payload', 'headers']
    ordering = ['-created_at']
