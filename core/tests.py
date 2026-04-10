"""Tests for the core PMS models and router behaviour."""

import datetime

from django.test import TestCase

from core.models import CoreUnit, CoreVisit, CoreProperty, CoreRatePlan
from roomos.routers import CorePlatformRouter


class CoreUnitModelTest(TestCase):
    databases = ["default"]

    def setUp(self):
        self.unit = CoreUnit.objects.create(
            unit_number="101",
            unit_type="Studio",
            floor=1,
            max_occupancy=2,
        )

    def test_str(self):
        self.assertEqual(str(self.unit), "Unit 101 (Studio)")

    def test_db_table(self):
        self.assertEqual(CoreUnit._meta.db_table, "core_units")

    def test_default_is_active(self):
        self.assertTrue(self.unit.is_active)

    def test_create_and_retrieve(self):
        retrieved = CoreUnit.objects.get(unit_number="101")
        self.assertEqual(retrieved.unit_type, "Studio")
        self.assertEqual(retrieved.floor, 1)


class CoreVisitModelTest(TestCase):
    databases = ["default"]

    def setUp(self):
        self.unit = CoreUnit.objects.create(
            unit_number="202",
            unit_type="Suite",
        )
        self.visit = CoreVisit.objects.create(
            unit=self.unit,
            guest_name="Alice Smith",
            guest_email="alice@example.com",
            check_in=datetime.date(2026, 5, 1),
            check_out=datetime.date(2026, 5, 5),
        )

    def test_str(self):
        self.assertIn("Alice Smith", str(self.visit))
        self.assertIn("202", str(self.visit))

    def test_db_table(self):
        self.assertEqual(CoreVisit._meta.db_table, "core_visits")

    def test_default_status(self):
        self.assertEqual(self.visit.status, CoreVisit.STATUS_RESERVED)

    def test_status_choices(self):
        statuses = [choice[0] for choice in CoreVisit.STATUS_CHOICES]
        self.assertIn(CoreVisit.STATUS_CHECKED_IN, statuses)
        self.assertIn(CoreVisit.STATUS_CHECKED_OUT, statuses)
        self.assertIn(CoreVisit.STATUS_CANCELLED, statuses)


class CorePropertyModelTest(TestCase):
    databases = ["default"]

    def test_db_table(self):
        self.assertEqual(CoreProperty._meta.db_table, "core_properties")

    def test_create(self):
        prop = CoreProperty.objects.create(name="Grand Hotel", address="123 Main St")
        self.assertEqual(str(prop), "Grand Hotel")
        self.assertTrue(prop.is_active)


class CoreRatePlanModelTest(TestCase):
    databases = ["default"]

    def test_db_table(self):
        self.assertEqual(CoreRatePlan._meta.db_table, "core_rate_plans")

    def test_create(self):
        plan = CoreRatePlan.objects.create(name="Standard", daily_rate="99.99")
        self.assertIn("Standard", str(plan))
        self.assertEqual(plan.currency, "USD")


class CorePlatformRouterCoreTest(TestCase):
    """Router should direct core app operations to the default DB."""

    def setUp(self):
        self.router = CorePlatformRouter()

    def _mock_model(self, app_label):
        class FakeMeta:
            pass
        FakeMeta.app_label = app_label

        class FakeModel:
            _meta = FakeMeta()

        return FakeModel

    def test_db_for_read_core(self):
        model = self._mock_model("core")
        self.assertEqual(self.router.db_for_read(model), "default")

    def test_db_for_write_core(self):
        model = self._mock_model("core")
        self.assertEqual(self.router.db_for_write(model), "default")

    def test_allow_migrate_core_on_default(self):
        self.assertTrue(self.router.allow_migrate("default", "core"))

    def test_deny_migrate_core_on_platform(self):
        self.assertFalse(self.router.allow_migrate("opsian-platform", "core"))

    def test_db_for_read_platform(self):
        model = self._mock_model("platform_app")
        self.assertEqual(self.router.db_for_read(model), "opsian-platform")

    def test_db_for_write_platform(self):
        model = self._mock_model("platform_app")
        self.assertEqual(self.router.db_for_write(model), "opsian-platform")

    def test_allow_migrate_platform_on_platform_db(self):
        self.assertTrue(self.router.allow_migrate("opsian-platform", "platform_app"))

    def test_deny_migrate_platform_on_default_db(self):
        self.assertFalse(self.router.allow_migrate("default", "platform_app"))

    def test_no_opinion_for_other_apps(self):
        self.assertIsNone(self.router.db_for_read(self._mock_model("auth")))
        self.assertIsNone(self.router.db_for_write(self._mock_model("auth")))
        self.assertIsNone(self.router.allow_migrate("default", "auth"))

    def test_allow_relation_within_core(self):
        core1 = self._mock_model("core")()
        core2 = self._mock_model("core")()
        self.assertTrue(self.router.allow_relation(core1, core2))

    def test_deny_relation_across_apps(self):
        core_obj = self._mock_model("core")()
        platform_obj = self._mock_model("platform_app")()
        self.assertFalse(self.router.allow_relation(core_obj, platform_obj))

    def test_no_opinion_relation_outside_managed_apps(self):
        auth_obj = self._mock_model("auth")()
        core_obj = self._mock_model("core")()
        self.assertIsNone(self.router.allow_relation(auth_obj, core_obj))

