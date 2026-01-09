from __future__ import annotations

from typing import Any

from django.db import transaction

from apps.orgs.models import Membership
from apps.core.services import BaseService, ServiceError, ServiceResult
from apps.usuarios.domain.inputs import ToggleMemberActiveInput


class ToggleMemberService(BaseService):
    def execute(self, input_data: Any, *, actor: Any = None, context: Any = None) -> ServiceResult:
        self.ensure_dataclass(input_data)
        assert isinstance(input_data, ToggleMemberActiveInput)

        if not actor or not actor.is_authenticated:
            return ServiceResult.failure([
                ServiceError(code="unauthorized", message="Usuario no autenticado."),
            ])

        actor_membership = Membership.objects.filter(
            user=actor,
            organization_id=input_data.organization_id,
            is_active=True,
        ).first()
        if not actor_membership or actor_membership.role != "admin":
            return ServiceResult.failure([
                ServiceError(code="forbidden", message="No tienes permisos para actualizar miembros."),
            ])

        with transaction.atomic():
            membership = (
                Membership.objects.select_related("user")
                .filter(id=input_data.member_id, organization_id=input_data.organization_id)
                .first()
            )
            if not membership:
                return ServiceResult.failure([
                    ServiceError(code="not_found", message="Miembro no encontrado."),
                ])

            desired_active = bool(input_data.active)

            # Protección de último admin al desactivar
            if not desired_active and membership.role == "admin" and membership.is_active:
                admin_count = Membership.objects.filter(
                    organization_id=input_data.organization_id,
                    role="admin",
                    is_active=True,
                ).count()
                if admin_count <= 1:
                    return ServiceResult.failure([
                        ServiceError(code="last_admin_forbidden", message="No puedes desactivar al último administrador activo."),
                    ])

            membership.is_active = desired_active
            membership.save(update_fields=["is_active"])

        return ServiceResult.success(data={"member_id": membership.pk, "active": membership.is_active})
