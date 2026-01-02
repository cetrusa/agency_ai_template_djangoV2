from .models import GlobalConfig


def global_config_context(request):
    """Inyecta la configuración global en todos los templates."""
    config = GlobalConfig.load()
    return {
        "GLOBAL_CONFIG": config,
    }
