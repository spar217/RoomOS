"""Tests for the platform entitlement models."""

from django.test import TestCase

from platform_app.models import Entitlement, TenantProfile


class TenantProfileModelTest(TestCase):
    databases = ["opsian-platform"]

    def test_db_table(self):
        self.assertEqual(TenantProfile._meta.db_table, "platform_tenants")

    def test_create_and_str(self):
        tenant = TenantProfile.objects.using("opsian-platform").create(
            tenant_id="tenant-001",
            name="Acme Hotels",
        )
        self.assertIn("tenant-001", str(tenant))
        self.assertIn("Acme Hotels", str(tenant))
        self.assertTrue(tenant.is_active)


class EntitlementModelTest(TestCase):
    databases = ["opsian-platform"]

    def setUp(self):
        self.tenant = TenantProfile.objects.using("opsian-platform").create(
            tenant_id="tenant-002",
            name="Best Stay Inc.",
        )

    def test_db_table(self):
        self.assertEqual(Entitlement._meta.db_table, "platform_entitlements")

    def test_create_entitlement(self):
        ent = Entitlement.objects.using("opsian-platform").create(
            tenant_id="tenant-002",
            feature=Entitlement.FEATURE_CORE_PMS,
        )
        self.assertTrue(ent.is_enabled)
        self.assertIn("tenant-002", str(ent))
        self.assertIn("enabled", str(ent))

    def test_feature_choices(self):
        features = [c[0] for c in Entitlement.FEATURE_CHOICES]
        self.assertIn(Entitlement.FEATURE_CORE_PMS, features)
        self.assertIn(Entitlement.FEATURE_REPORTING, features)
        self.assertIn(Entitlement.FEATURE_CHANNEL_MANAGER, features)
        self.assertIn(Entitlement.FEATURE_REVENUE_MANAGEMENT, features)

    def test_unique_together(self):
        Entitlement.objects.using("opsian-platform").create(
            tenant_id="tenant-002",
            feature=Entitlement.FEATURE_REPORTING,
        )
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Entitlement.objects.using("opsian-platform").create(
                tenant_id="tenant-002",
                feature=Entitlement.FEATURE_REPORTING,
            )

