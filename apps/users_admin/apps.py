from django.apps import AppConfig

class UsersAdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users_admin'
    verbose_name = "Users Admin"

    def ready(self) -> None:
        # Registro explícito del CRUD declarativo.
        from . import crud_config

        crud_config.register()
