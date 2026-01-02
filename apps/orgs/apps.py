from __future__ import annotations

from django.apps import AppConfig


class OrgsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.orgs"
    verbose_name = "Organizations"

    def ready(self) -> None:
        # Additive, tenant-ready: expose user.current_org without custom User model.
        from django.contrib.auth import get_user_model

        from .services import get_current_organization

        User = get_user_model()
        if not hasattr(User, "current_org"):
            setattr(User, "current_org", property(get_current_organization))
