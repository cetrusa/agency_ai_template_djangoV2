from django.shortcuts import redirect
from django.urls import reverse
from .models import GlobalConfig

class SetupMiddleware:
    """Redirige al wizard de setup si la configuración no está completa."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Rutas exentas de redirección
        if request.path.startswith("/setup/") or \
           request.path.startswith("/static/") or \
           request.path.startswith("/media/") or \
           request.path.startswith("/admin/"):
            return self.get_response(request)

        # Verificar estado del setup
        try:
            config = GlobalConfig.load()
            if not config.setup_complete:
                return redirect("setup_wizard")
        except Exception:
            # Si falla la DB (ej. migraciones pendientes), dejar pasar para no bloquear
            pass

        return self.get_response(request)
