from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction

from apps.orgs.models import Membership
from apps.core.exceptions import ServiceValidationException
from apps.core.services import BaseService, ServiceError, ServiceResult
from apps.usuarios.domain.inputs import CreateMemberInput


class CreateMemberService(BaseService):
    def execute(self, input_data: Any, *, actor: Any = None, context: Any = None) -> ServiceResult:
        self.ensure_dataclass(input_data)
        assert isinstance(input_data, CreateMemberInput)

        # 1. Permission Check: Solo admin puede crear miembros
        if not actor or not actor.is_authenticated:
            return ServiceResult.failure([ServiceError(code="unauthorized", message="Usuario no autenticado.")])

        actor_membership = Membership.objects.filter(
            user=actor,
            organization_id=input_data.organization_id,
            is_active=True
        ).first()

        if not actor_membership or actor_membership.role != "admin":
            return ServiceResult.failure([ServiceError(code="forbidden", message="No tienes permisos para agregar miembros.")])

        email = (input_data.email or "").strip().lower()
        if not email:
            return ServiceResult.failure([ServiceError(code="email_required", message="El email es obligatorio.")])

        if input_data.role not in {"admin", "member"}:
            return ServiceResult.failure([ServiceError(code="invalid_role", message="Rol inválido.")])

        User = get_user_model()
        user_lookup_field = "email" if hasattr(User, "email") else "username"

        with transaction.atomic():
            user = User.objects.filter(**{user_lookup_field: email}).first()
            created_user = False

            if not user:
                user = User(**{user_lookup_field: email})
                if hasattr(user, "username"):
                    user.username = email
                user.email = email if hasattr(user, "email") else user.username
                user.first_name = input_data.first_name or ""
                user.last_name = input_data.last_name or ""
                user.set_unusable_password()
                user.full_clean(exclude=["password"])
                user.save()
                created_user = True
            else:
                user.first_name = user.first_name or input_data.first_name or ""
                user.last_name = user.last_name or input_data.last_name or ""
                user.save(update_fields=["first_name", "last_name"])

            membership_exists = Membership.objects.filter(
                user=user,
                organization_id=input_data.organization_id,
            ).exists()

            if membership_exists:
                return ServiceResult.failure([
                    ServiceError(code="already_member", message="El usuario ya pertenece a la organización."),
                ])

            membership = Membership.objects.create(
                user=user,
                organization_id=input_data.organization_id,
                role=input_data.role,
                is_active=True,
            )

        return ServiceResult.success(
            data={
                "created_user": created_user,
                "member_id": membership.pk,
                "user_id": user.pk,
            }
        )
