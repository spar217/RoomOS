"""
Database router for RoomOS.

Routing rules:
  - Models in the ``core`` app (core_* tables, core_units, core_visits)
    are directed to the **default** database alias, which maps to
    *opsian-core* (the primary PMS database).
  - Models in the ``platform_app`` app (entitlement checks) are directed
    to the **opsian-platform** database alias.
  - All other models fall back to the default database.
"""

CORE_APP_LABEL = "core"
PLATFORM_APP_LABEL = "platform_app"
PLATFORM_DB = "opsian-platform"


class CorePlatformRouter:
    """Route database operations to opsian-core or opsian-platform."""

    def db_for_read(self, model, **hints):
        if model._meta.app_label == PLATFORM_APP_LABEL:
            return PLATFORM_DB
        if model._meta.app_label == CORE_APP_LABEL:
            return "default"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == PLATFORM_APP_LABEL:
            return PLATFORM_DB
        if model._meta.app_label == CORE_APP_LABEL:
            return "default"
        return None

    def allow_relation(self, obj1, obj2, **hints):
        # Allow relations within the same database.
        db_set = {CORE_APP_LABEL, PLATFORM_APP_LABEL}
        if obj1._meta.app_label in db_set and obj2._meta.app_label in db_set:
            return obj1._meta.app_label == obj2._meta.app_label
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == PLATFORM_APP_LABEL:
            return db == PLATFORM_DB
        if app_label == CORE_APP_LABEL:
            return db == "default"
        return None
