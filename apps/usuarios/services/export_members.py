from __future__ import annotations

from typing import Any

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify

from apps.core.services import exporting
from apps.orgs.models import Membership
from apps.core.services import BaseService, ServiceError, ServiceResult
from apps.usuarios.domain.inputs import ExportMembersInput


class ExportMembersService(BaseService):
    def execute(self, input_data: Any, *, actor: Any = None, context: Any = None) -> ServiceResult:
        self.ensure_dataclass(input_data)
        assert isinstance(input_data, ExportMembersInput)

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
                ServiceError(code="forbidden", message="No tienes permisos para exportar miembros."),
            ])

        qs = self._build_queryset(input_data)

        fmt = (input_data.format or "").lower()
        if fmt not in {"csv", "xlsx", "pdf"}:
            return ServiceResult.failure([
                ServiceError(code="invalid_format", message="Formato de exportación no soportado."),
            ])

        org_slug = None
        if context and getattr(context, "organization", None):
            org_obj = context.organization
            org_slug = getattr(org_obj, "slug", None) or getattr(org_obj, "name", None)
        org_slug = org_slug or "org"
        filename_base = f"miembros_{slugify(org_slug)}"

        fields = [
            "user__email",
            "user__first_name",
            "user__last_name",
            "role",
            "is_active",
            "created_at",
        ]
        headers = ["Email", "Nombre", "Apellido", "Rol", "Activo", "Fecha Alta"]

        if fmt == "csv":
            resp = exporting.stream_csv(
                queryset=qs,
                fields=fields,
                headers=headers,
                filename_base=filename_base,
            )
        elif fmt == "xlsx":
            resp = exporting.build_xlsx(
                queryset=qs,
                fields=fields,
                headers=headers,
                filename_base=filename_base,
                sheet_name="Miembros",
            )
        else:
            resp = exporting.build_pdf_table(
                queryset=qs,
                fields=fields,
                headers=headers,
                title="Miembros",
                filename_base=filename_base,
            )

        return ServiceResult.success(data={"http_response": resp})

    def _build_queryset(self, input_data: ExportMembersInput):
        qs = (
            Membership.objects.select_related("user", "organization")
            .filter(organization_id=input_data.organization_id)
        )

        if input_data.search:
            term = input_data.search.strip()
            if term:
                qs = qs.filter(
                    Q(user__first_name__icontains=term)
                    | Q(user__last_name__icontains=term)
                    | Q(user__email__icontains=term)
                )

        if input_data.role:
            qs = qs.filter(role=input_data.role)

        if input_data.is_active is not None:
            qs = qs.filter(is_active=input_data.is_active)
        elif not input_data.include_inactive:
            qs = qs.filter(is_active=True)

        return qs.order_by("user__email", "user__username")
