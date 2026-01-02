"""Vistas para gestión de configuración global de empresa (Singleton).

GlobalConfig es un modelo Singleton que solo tiene 1 registro (pk=1).
Las vistas detail y edit son las únicas operaciones CRUD aplicables.
Los permisos se validan al nivel de vista para garantizar acceso seguro.
"""

from __future__ import annotations

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.contrib import messages
from apps.core.models import GlobalConfig
from .forms import GlobalConfigForm


def _check_permission(user, perm: str) -> bool:
    """Verifica si el usuario tiene el permiso especificado."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.has_perm(perm)


@login_required
def detail(request: HttpRequest) -> HttpResponse:
    """Mostrar detalles de la configuración global (singleton)."""
    # Validar permisos: usuario debe ser superusuario o tener change_globalconfig
    if not _check_permission(request.user, "core.change_globalconfig"):
        return HttpResponseForbidden("No tienes permisos para acceder a esta sección")

    config = GlobalConfig.load()

    context = {"config": config, "page_title": "Configuración de Empresa"}

    if request.headers.get("HX-Request") == "true":
        return render(request, "organization_admin/settings.html", context)

    return render(
        request,
        "pages/shell.html",
        {"content_template": "organization_admin/settings.html", **context},
    )


@login_required
def edit(request: HttpRequest) -> HttpResponse:
    """Editar configuración global (singleton)."""
    # Validar permisos: usuario debe ser superusuario o tener change_globalconfig
    if not _check_permission(request.user, "core.change_globalconfig"):
        return HttpResponseForbidden("No tienes permisos para acceder a esta sección")

    config = GlobalConfig.load()

    if request.method == "POST":
        form = GlobalConfigForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Configuración actualizada correctamente")
            return redirect("organization_admin:detail")
    else:
        form = GlobalConfigForm(instance=config)

    context = {
        "form": form,
        "config": config,
        "page_title": "Editar Configuración de Empresa",
    }

    if request.headers.get("HX-Request") == "true":
        return render(request, "organization_admin/form.html", context)

    return render(
        request,
        "pages/shell.html",
        {"content_template": "organization_admin/form.html", **context},
    )
