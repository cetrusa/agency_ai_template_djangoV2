from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect


@login_required
def list_view(request: HttpRequest) -> HttpResponse:
    # Compat shim: en v1 la gestión vive en `apps.usuarios`.
    return redirect("usuarios:index")
