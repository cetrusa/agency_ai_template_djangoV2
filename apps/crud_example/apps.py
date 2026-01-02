from django.apps import AppConfig


class CrudExampleConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.crud_example"
    verbose_name = "CRUD Example"

    def ready(self) -> None:
        # Registro explícito del CRUD declarativo (MVP list-only).
        from . import crud_config

        crud_config.register()
