from django.contrib import admin
from .models import DailyAnalytics


@admin.register(DailyAnalytics)
class DailyAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['user', 'platform', 'date', 'total_messages', 'incoming_messages', 'outgoing_messages']
    list_filter = ['platform', 'date']
    search_fields = ['user__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-date']
