from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Membership, Organization
from .utils import SESSION_KEY, get_active_organization, set_active_organization


@login_required
def select_organization(request: HttpRequest) -> HttpResponse:
    memberships = (
        Membership.objects.select_related("organization")
        .filter(user=request.user, is_active=True, organization__is_active=True)
        .order_by("organization__name")
    )

    count = memberships.count()
    if count == 0:
        return render(request, "orgs/no_organization.html")

    if count == 1:
        membership = memberships.first()
        if membership and set_active_organization(request, membership.organization_id):
            return redirect("dashboard:home")

    return render(request, "orgs/select.html", {"memberships": memberships})


@login_required
@require_POST
def activate_organization(request: HttpRequest) -> HttpResponse:
    org_id = request.POST.get("org_id")
    membership = get_object_or_404(
        Membership.objects.select_related("organization"),
        user=request.user,
        organization_id=org_id,
        is_active=True,
        organization__is_active=True,
    )

    request.session[SESSION_KEY] = membership.organization_id
    messages.success(request, "Organización activada correctamente.")
    return redirect("dashboard:home")
