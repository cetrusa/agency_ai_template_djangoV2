from __future__ import annotations

from typing import Optional

from django.contrib.auth.models import AnonymousUser

from .models import Membership, Organization


def get_current_organization(user) -> Optional[Organization]:
    """Determina la organización actual del usuario.

    MVP (tenant-ready, sin UI):
    - Si el usuario no está autenticado -> None
    - Si tiene memberships -> primera activa (por created_at)

    En el futuro:
    - org switcher UI
    - session-based selection (current_org_id)
    """

    if not user or isinstance(user, AnonymousUser) or not getattr(user, "is_authenticated", False):
        return None

    # Cache por request/ciclo de vida del objeto User.
    cached = getattr(user, "_current_org_cache", None)
    if cached is not None:
        return cached

    membership = (
        Membership.objects.select_related("organization")
        .filter(user=user, is_active=True, organization__is_active=True)
        .order_by("created_at")
        .first()
    )

    org = membership.organization if membership else None
    setattr(user, "_current_org_cache", org)
    return org


def user_has_org_role(user, *, roles: set[str]) -> bool:
    org = getattr(user, "current_org", None)
    if not org:
        return False

    return Membership.objects.filter(
        user=user,
        organization=org,
        is_active=True,
        role__in=list(roles),
    ).exists()
