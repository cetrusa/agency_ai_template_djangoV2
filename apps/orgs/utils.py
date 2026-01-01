from __future__ import annotations

from typing import Optional

from .models import Membership, Organization

SESSION_KEY = "active_org_id"


def set_active_organization(request, org_id: int) -> bool:
    user = getattr(request, "user", None)
    if not user or not getattr(user, "is_authenticated", False):
        return False

    membership = (
        Membership.objects.select_related("organization")
        .filter(
            user=user,
            organization_id=org_id,
            is_active=True,
            organization__is_active=True,
        )
        .first()
    )
    if not membership:
        return False

    request.session[SESSION_KEY] = membership.organization_id
    return True


def get_active_organization(request) -> Optional[Organization]:
    org_id = request.session.get(SESSION_KEY)
    if not org_id:
        request.session.pop(SESSION_KEY, None)
        return None

    organization = Organization.objects.filter(pk=org_id, is_active=True).first()
    if not organization:
        request.session.pop(SESSION_KEY, None)
        return None

    return organization
