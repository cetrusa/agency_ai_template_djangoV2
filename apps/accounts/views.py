from __future__ import annotations

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView as DjangoPasswordChangeView
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.mail import send_mail
from django.conf import settings
from apps.core.models import GlobalConfig

from .forms import UserProfileForm, CustomPasswordChangeForm, UserRegisterForm

User = get_user_model()


def login_view(request: HttpRequest) -> HttpResponse:
    """Vista de login."""
    next_param = request.GET.get("next") or request.POST.get("next")
    default_redirect = "dashboard:home"
    target_redirect = next_param if next_param and url_has_allowed_host_and_scheme(next_param, allowed_hosts={request.get_host()}) else default_redirect

    # Si ya está autenticado, redirigir al destino o dashboard
    if request.user.is_authenticated:
        return redirect(target_redirect)
    
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        
        if not username or not password:
            messages.error(request, "Por favor, ingresa usuario y contraseña")
            return render(request, "accounts/login.html", {
                "page_title": "Iniciar Sesión",
                "username": username,
            })
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(target_redirect)
        else:
            messages.error(request, "Usuario o contraseña incorrecto")
            return render(request, "accounts/login.html", {
                "page_title": "Iniciar Sesión",
                "username": username,
                "next": target_redirect,
            })
    
    context = {
        "page_title": "Iniciar Sesión",
        "next": target_redirect,
    }
    return render(request, "accounts/login.html", context)


def logout_view(request: HttpRequest) -> HttpResponse:
    """Vista de logout."""
    logout(request)
    messages.success(request, "Sesión cerrada correctamente")
    return redirect("accounts:login")


@login_required
def profile(request: HttpRequest) -> HttpResponse:
    """Vista de perfil del usuario (lectura)."""
    context = {
        "page_title": "Mi Perfil",
        "user": request.user,
    }
    
    if request.headers.get("HX-Request") == "true":
        return render(request, "accounts/profile.html", context)
    
    return render(request, "pages/shell.html", {"content_template": "accounts/profile.html", **context})


@login_required
def profile_edit(request: HttpRequest) -> HttpResponse:
    """Editar datos básicos del perfil."""
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente")
            return redirect("accounts:profile")
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        "page_title": "Editar Perfil",
        "form": form,
    }
    
    if request.headers.get("HX-Request") == "true":
        return render(request, "accounts/profile_edit.html", context)
    
    return render(request, "pages/shell.html", {"content_template": "accounts/profile_edit.html", **context})


class PasswordChangeView(DjangoPasswordChangeView):
    """Vista para cambio de contraseña."""
    form_class = CustomPasswordChangeForm
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:profile")

    def form_valid(self, form):
        messages.success(self.request, "Contraseña actualizada correctamente")
        return super().form_valid(form)


def register_view(request: HttpRequest) -> HttpResponse:
    """Vista de registro de nuevos usuarios."""
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Generar token de verificación
            signer = TimestampSigner()
            token = signer.sign(str(user.pk))
            
            # Construir enlace
            verify_url = request.build_absolute_uri(
                reverse("accounts:verify_email", args=[token])
            )
            
            # Enviar correo (simulado en consola si no hay SMTP)
            config = GlobalConfig.load()
            site_name = getattr(config, "site_name", "Agency Dashboard")
            subject = f"Verifica tu cuenta en {site_name}"
            message = f"""Hola {user.first_name},

Gracias por registrarte. Para activar tu cuenta, por favor haz clic en el siguiente enlace:

{verify_url}

Este enlace expirará en 24 horas.

Si no solicitaste este registro, ignora este correo.
"""
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, "Cuenta creada. Revisa tu correo para verificarla.")
                return render(request, "accounts/verification_sent.html", {"email": user.email})
            except Exception as e:
                # En producción, loggear el error
                messages.error(request, "Error al enviar el correo. Contacta al soporte.")
                # Opcional: borrar usuario si falla el envío
                
    else:
        form = UserRegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def verify_email_view(request: HttpRequest, token: str) -> HttpResponse:
    """Vista para verificar el email mediante token firmado."""
    signer = TimestampSigner()
    try:
        # Token válido por 24 horas (86400 segundos)
        original_value = signer.unsign(token, max_age=86400)
        user_pk = int(original_value)
        user = get_object_or_404(User, pk=user_pk)
        
        if user.is_active:
            messages.info(request, "Tu cuenta ya estaba activa.")
        else:
            user.is_active = True
            user.save()
            messages.success(request, "¡Cuenta verificada correctamente! Ahora espera a que un administrador te asigne permisos.")
            
        return render(request, "accounts/verification_success.html")
        
    except (BadSignature, SignatureExpired):
        return render(request, "accounts/verification_failed.html")


@login_required
def verification_pending_view(request: HttpRequest) -> HttpResponse:
    """Vista de espera para usuarios sin permisos/empresa."""
    return render(request, "accounts/verification_pending.html")
    form_class = CustomPasswordChangeForm
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:profile")
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Contraseña actualizada correctamente")
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Cambiar Contraseña"
        return context
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("HX-Request") == "true":
            return render(self.request, "accounts/password_change_form.html", context)
        
        context["content_template"] = "accounts/password_change_form.html"
        return render(self.request, "pages/shell.html", context, **response_kwargs)
