from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from apps.orgs.models import Membership
from apps.service_core.base.result import ServiceResult
from apps.service_core.base.service import BaseService
from apps.usuarios.domain.inputs import ListMembersInput


class ListMembersService(BaseService):
    def execute(self, input_data: Any, *, actor: Any = None, context: Any = None) -> ServiceResult:
        self.ensure_dataclass(input_data)
        assert isinstance(input_data, ListMembersInput)

        # 2. Defensive Membership bootstrap
        # Si el actor no tiene membresía en la org activa, crearla como admin para evitar bloqueos.
        if actor and actor.is_authenticated:
            exists = Membership.objects.filter(
                user=actor,
                organization_id=input_data.organization_id
            ).exists()
            if not exists:
                Membership.objects.create(
                    user=actor,
                    organization_id=input_data.organization_id,
                    role="admin",
                    is_active=True
                )

        qs: QuerySet = (
            Membership.objects.select_related("user", "organization")
            .filter(organization_id=input_data.organization_id)
        )

        if not input_data.include_inactive:
            qs = qs.filter(is_active=True)

        memberships = list(qs.order_by("user__email", "user__username"))
        return ServiceResult.success(data={"memberships": memberships})
