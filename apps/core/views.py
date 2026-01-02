from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import get_user_model, login
from django.contrib import messages
from .models import GlobalConfig
from .forms import SetupForm

User = get_user_model()

def setup_wizard(request):
    """Asistente de configuración inicial."""
    config = GlobalConfig.load()
    
    if config.setup_complete:
        return redirect("dashboard:home")
    
    # Verificar si ya existe algún superusuario
    has_superuser = User.objects.filter(is_superuser=True).exists()
        
    if request.method == "POST":
        form = SetupForm(request.POST, request.FILES, instance=config)
        
        # Si no hay superusuario, forzar requerimiento de campos de admin
        if not has_superuser:
            form.fields["admin_email"].required = True
            form.fields["admin_password"].required = True
            form.fields["admin_password_confirm"].required = True

        if form.is_valid():
            # 1. Guardar Configuración
            instance = form.save(commit=False)
            instance.setup_complete = True
            instance.save()
            
            # 2. Crear Superusuario (si aplica)
            email = form.cleaned_data.get("admin_email")
            password = form.cleaned_data.get("admin_password")
            
            if not has_superuser and email and password:
                try:
                    user = User.objects.create_superuser(
                        username=email, # Usamos email como username por defecto
                        email=email,
                        password=password
                    )
                    # Loguear automáticamente
                    login(request, user)
                    messages.success(request, f"¡Bienvenido! Usuario {email} creado correctamente.")
                except Exception as e:
                    messages.error(request, f"Error creando usuario: {e}")
                    # Revertir setup_complete para que no quede en el limbo
                    instance.setup_complete = False
                    instance.save()
                    return render(request, "core/setup_wizard.html", {"form": form, "has_superuser": has_superuser})

            return redirect("dashboard:home")
    else:
        form = SetupForm(instance=config)
        
    return render(request, "core/setup_wizard.html", {"form": form, "has_superuser": has_superuser})
