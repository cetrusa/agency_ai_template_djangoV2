from __future__ import annotations

from functools import wraps
from typing import Callable

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

from .models import Membership, Organization
from .utils import SESSION_KEY, get_active_organization


def _clear_active_org(request: HttpRequest) -> None:
    try:
        request.session.pop(SESSION_KEY, None)
    except Exception:
        # Si la sesión está corrupta, evitar propagar error.
        pass


def organization_required(view_func: Callable) -> Callable:
    @wraps(view_func)
    def _wrapped(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            login_url = getattr(settings, "LOGIN_URL", None)
            try:
                login_url = reverse("accounts:login")
            except Exception:
                login_url = login_url or "/accounts/login/"
            return redirect(login_url)

        try:
            org = get_active_organization(request)
        except Exception:
            _clear_active_org(request)
            messages.error(request, "Selecciona una organización válida para continuar.")
            return redirect("orgs:select")

        if not org or not getattr(org, "is_active", False):
            _clear_active_org(request)
            return redirect("orgs:select")

        membership_exists = Membership.objects.filter(
            user=user,
            organization=org,
            is_active=True,
            organization__is_active=True,
        ).exists()

        if not membership_exists:
            _clear_active_org(request)
            messages.error(request, "Selecciona una organización válida para continuar.")
            return redirect("orgs:select")

        request.organization = org
        return view_func(request, *args, **kwargs)

    return _wrapped
