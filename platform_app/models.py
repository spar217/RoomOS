"""
Platform entitlement models — stored in the *opsian-platform* (secondary)
database.

These models are used to verify what features / modules a property or user
account is entitled to use within the RoomOS platform.
"""

from django.db import models


class Entitlement(models.Model):
    """Records which platform features are enabled for a given tenant."""

    FEATURE_CORE_PMS = "core_pms"
    FEATURE_REPORTING = "reporting"
    FEATURE_CHANNEL_MANAGER = "channel_manager"
    FEATURE_REVENUE_MANAGEMENT = "revenue_management"

    FEATURE_CHOICES = [
        (FEATURE_CORE_PMS, "Core PMS"),
        (FEATURE_REPORTING, "Reporting"),
        (FEATURE_CHANNEL_MANAGER, "Channel Manager"),
        (FEATURE_REVENUE_MANAGEMENT, "Revenue Management"),
    ]

    tenant_id = models.CharField(max_length=255, db_index=True)
    feature = models.CharField(max_length=100, choices=FEATURE_CHOICES)
    is_enabled = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "platform_app"
        db_table = "platform_entitlements"
        unique_together = [("tenant_id", "feature")]

    def __str__(self):
        status = "enabled" if self.is_enabled else "disabled"
        return f"Entitlement({self.tenant_id}, {self.feature}, {status})"


class TenantProfile(models.Model):
    """Basic profile / metadata for a platform tenant."""

    tenant_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "platform_app"
        db_table = "platform_tenants"

    def __str__(self):
        return f"Tenant({self.tenant_id}, {self.name})"

