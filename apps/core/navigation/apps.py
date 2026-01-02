from django.apps import AppConfig
from .registry import registry
from .defs import Module

class NavigationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core.navigation"

    def ready(self):
        # Register System Modules
        registry.register(Module(
            slug="dashboard",
            label="Dashboard",
            icon="bi-speedometer2",
            url_name="dashboard:home",
            kind="system"
        ))
        registry.register(Module(
            slug="organization",
            label="Empresa",
            icon="bi-building",
            url_name="organization_admin:detail",
            kind="system",
            permission="core.change_globalconfig"
        ))
        registry.register(Module(
            slug="users",
            label="Usuarios",
            icon="bi-people",
            url_name="users_admin:list",
            kind="system",
            permission="auth.view_user"
        ))
