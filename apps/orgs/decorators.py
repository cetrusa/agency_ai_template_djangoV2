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


def organization_required(view_func: Callable) -> Callable:
    @wraps(view_func)
    def _wrapped(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            login_url = None
            try:
                login_url = reverse("accounts:login")
            except Exception:
                login_url = getattr(settings, "LOGIN_URL", "/accounts/login/")
            return redirect(login_url)

        org = get_active_organization(request)
        if not org:
            return redirect("orgs:select")

        membership_exists = Membership.objects.filter(
            user=user,
            organization=org,
            is_active=True,
            organization__is_active=True,
        ).exists()

        if not membership_exists:
            request.session.pop(SESSION_KEY, None)
            messages.error(request, "Selecciona una organización válida para continuar.")
            return redirect("orgs:select")

        request.organization = org
        return view_func(request, *args, **kwargs)

    return _wrapped
