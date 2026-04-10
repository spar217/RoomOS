"""
Core PMS models — stored in the *opsian-core* (primary) database.

All models use table names prefixed with ``core_`` to match the PMS schema
convention described in the problem statement.
"""

from django.db import models


class CoreUnit(models.Model):
    """A rentable / bookable unit in the property management system."""

    unit_number = models.CharField(max_length=50, unique=True)
    unit_type = models.CharField(max_length=100)
    floor = models.PositiveSmallIntegerField(null=True, blank=True)
    max_occupancy = models.PositiveSmallIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "core"
        db_table = "core_units"
        ordering = ["unit_number"]

    def __str__(self):
        return f"Unit {self.unit_number} ({self.unit_type})"


class CoreVisit(models.Model):
    """A guest visit / reservation record linked to a unit."""

    STATUS_RESERVED = "reserved"
    STATUS_CHECKED_IN = "checked_in"
    STATUS_CHECKED_OUT = "checked_out"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_RESERVED, "Reserved"),
        (STATUS_CHECKED_IN, "Checked In"),
        (STATUS_CHECKED_OUT, "Checked Out"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    unit = models.ForeignKey(
        CoreUnit,
        on_delete=models.PROTECT,
        related_name="visits",
    )
    guest_name = models.CharField(max_length=255)
    guest_email = models.EmailField(blank=True, default="")
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_RESERVED,
    )
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "core"
        db_table = "core_visits"
        ordering = ["-check_in"]

    def __str__(self):
        return f"Visit {self.pk} — {self.guest_name} @ Unit {self.unit.unit_number}"


class CoreProperty(models.Model):
    """Top-level property record (parent of units)."""

    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "core"
        db_table = "core_properties"
        verbose_name_plural = "properties"

    def __str__(self):
        return self.name


class CoreRatePlan(models.Model):
    """Pricing / rate plan attached to one or more units."""

    name = models.CharField(max_length=255)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "core"
        db_table = "core_rate_plans"

    def __str__(self):
        return f"{self.name} ({self.currency} {self.daily_rate}/night)"

