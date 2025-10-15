from django.contrib import admin
from .models import PlatformAccount


@admin.register(PlatformAccount)
class PlatformAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'platform', 'platform_username', 'is_active', 'last_sync_at', 'created_at']
    list_filter = ['platform', 'is_active', 'created_at']
    search_fields = ['user__email', 'platform_username', 'platform_user_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
