from __future__ import annotations

from typing import Any

from django.db import transaction

from apps.orgs.models import Membership
from apps.service_core.base.result import ServiceError, ServiceResult
from apps.service_core.base.service import BaseService
from apps.usuarios.domain.inputs import UpdateMemberInput


class UpdateMemberService(BaseService):
    def execute(self, input_data: Any, *, actor: Any = None, context: Any = None) -> ServiceResult:
        self.ensure_dataclass(input_data)
        assert isinstance(input_data, UpdateMemberInput)

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
                ServiceError(code="forbidden", message="No tienes permisos para editar miembros."),
            ])

        if input_data.role not in {"admin", "member"}:
            return ServiceResult.failure([
                ServiceError(code="invalid_role", message="Rol inválido."),
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

            is_role_downgrade = membership.role == "admin" and membership.is_active and input_data.role != "admin"
            is_deactivation = membership.role == "admin" and membership.is_active and not input_data.is_active
            if is_role_downgrade or is_deactivation:
                admin_count = Membership.objects.filter(
                    organization_id=input_data.organization_id,
                    role="admin",
                    is_active=True,
                ).count()
                if admin_count <= 1:
                    return ServiceResult.failure([
                        ServiceError(code="last_admin_forbidden", message="No puedes dejar la organización sin administradores activos."),
                    ])

            user = membership.user
            user.first_name = input_data.first_name or ""
            user.last_name = input_data.last_name or ""
            user.save(update_fields=["first_name", "last_name"])

            membership.role = input_data.role
            membership.is_active = input_data.is_active
            membership.save(update_fields=["role", "is_active"])

        return ServiceResult.success(data={"member_id": membership.pk, "updated": True})
