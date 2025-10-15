"""
Platform connection models
"""
import uuid
from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet


class PlatformAccount(models.Model):
    """
    Model to store connected platform accounts and their tokens
    """
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('messenger', 'Messenger'),
        ('whatsapp', 'WhatsApp'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='platform_accounts')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    platform_user_id = models.CharField(max_length=255, help_text="User ID from the platform")
    platform_username = models.CharField(max_length=255, blank=True, null=True)

    # Encrypted tokens
    access_token = models.TextField(help_text="Encrypted access token")
    refresh_token = models.TextField(blank=True, null=True, help_text="Encrypted refresh token")
    token_expires_at = models.DateTimeField(blank=True, null=True)

    # Status
    is_active = models.BooleanField(default=True)
    last_sync_at = models.DateTimeField(blank=True, null=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional platform-specific data")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'platform_accounts'
        verbose_name = 'Platform Account'
        verbose_name_plural = 'Platform Accounts'
        unique_together = [['user', 'platform', 'platform_user_id']]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.get_platform_display()}"

    def encrypt_token(self, token):
        """Encrypt a token using the encryption key"""
        if settings.ENCRYPTION_KEY:
            f = Fernet(settings.ENCRYPTION_KEY)
            return f.encrypt(token.encode()).decode()
        return token

    def decrypt_token(self, encrypted_token):
        """Decrypt a token using the encryption key"""
        if settings.ENCRYPTION_KEY:
            f = Fernet(settings.ENCRYPTION_KEY)
            return f.decrypt(encrypted_token.encode()).decode()
        return encrypted_token

    def save(self, *args, **kwargs):
        """Override save to encrypt tokens before saving"""
        # Note: In production, implement proper token encryption/decryption
        super().save(*args, **kwargs)
