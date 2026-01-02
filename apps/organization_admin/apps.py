from django.apps import AppConfig


class OrganizationAdminConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.organization_admin"

    def ready(self):
        """Registrar configuración CRUD cuando la app esté lista."""
        from . import crud_config
        crud_config.register()
