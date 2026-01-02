from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Type
from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.db.models import Q, QuerySet
from django.http import HttpRequest
from django import forms

from .defs import ColumnDef, FilterDef
from .permissions import CrudPermissionSpec


@dataclass(frozen=True)
class CrudParams:
    q: str
    status: str
    sort: str
    dir: str
    page: str
    # Compat con templates del kit (aunque MVP solo use algunos)
    date_from: str
    date_to: str

    def as_dict(self) -> dict[str, str]:
        return {
            "q": self.q,
            "status": self.status,
            "sort": self.sort,
            "dir": self.dir,
            "page": self.page,
            "from": self.date_from,
            "to": self.date_to,
        }


class CrudConfig:
    """Base declarativa mínima (LIST ONLY).

    MVP del motor declarativo: list/table + filtros + ordering + paginación.
    No forms, no exports, no permissions.
    """

    crud_slug: str
    model: type

    page_title: str | None = None
    entity_label: str | None = None
    entity_label_plural: str | None = None

    list_columns: list[ColumnDef]
    filters: list[FilterDef] = []
    search_fields: list[str] = []

    default_sort_key: str = ""
    default_dir: str = "asc"
    page_size: int = 10

    status_options: list[tuple[str, str]] | None = None

    # --- Step 8 (MVP): formularios y metadatos de modales (sin generación automática) ---
    create_form_class: Type[forms.ModelForm] | None = None
    edit_form_class: Type[forms.ModelForm] | None = None

    create_title: str | None = None
    edit_title: str | None = None
    delete_title: str | None = None

    create_submit_label: str | None = None
    edit_submit_label: str | None = None
    delete_confirm_label: str | None = None

    # --- Step 9 (MVP): permisos declarativos (sin row-level) ---
    permission_list: str | None = None
    permission_create: str | None = None
    permission_edit: str | None = None
    permission_delete: str | None = None

    # --- Step 10 (MVP): exports declarativos (reutiliza apps.core.services.exporting) ---
    # Nota: el comportamiento legacy puede vivir en views concretas. Si export_fields no se declara,
    # los views pueden hacer fallback a su lógica actual.
    export_enabled: bool = True
    export_fields: list[str] | None = None
    export_headers: dict[str, str] | None = None
    export_formats: list[str] | set[str] | tuple[str, ...] | None = None  # e.g. ["csv", "xlsx", "pdf"]

    def exports_declared(self) -> bool:
        return bool(self.export_fields)

    def is_export_enabled(self) -> bool:
        return bool(self.export_enabled)

    def get_export_fields(self) -> list[str] | None:
        if not self.export_fields:
            return None
        return list(self.export_fields)

    def get_export_headers(self) -> list[str] | None:
        fields = self.get_export_fields()
        if not fields:
            return None
        mapping = self.export_headers or {}
        return [mapping.get(f, f) for f in fields]

    def get_export_formats(self) -> set[str]:
        raw = self.export_formats
        if not raw:
            return {"csv", "xlsx", "pdf"}
        return {str(x).strip().lower() for x in raw if str(x).strip()}

    def allows_format(self, fmt: str) -> bool:
        fmt = (fmt or "").strip().lower()
        if not fmt:
            return False
        return fmt in self.get_export_formats()

    def can_export(self, request: HttpRequest) -> bool:
        # Por ahora, export se alinea con permiso de list.
        return self.can_list(request)

    def parse_params(self, request: HttpRequest) -> CrudParams:
        q = (request.GET.get("q") or "").strip()
        status = (request.GET.get("status") or "").strip()
        sort = (request.GET.get("sort") or "").strip()
        direction = (request.GET.get("dir") or "").strip().lower()
        page = (request.GET.get("page") or "1").strip()

        if direction not in {"asc", "desc"}:
            direction = "asc"

        return CrudParams(
            q=q,
            status=status,
            sort=sort,
            dir=direction,
            page=page,
            date_from=(request.GET.get("from") or "").strip(),
            date_to=(request.GET.get("to") or "").strip(),
        )

    def build_qs_without_page(self, params: CrudParams) -> str:
        data = {k: v for k, v in params.as_dict().items() if k != "page" and v not in {"", "all"}}
        return urlencode(data)

    def get_base_queryset(self, request: HttpRequest) -> QuerySet:
        return self.model.objects.all()

    def apply_search(self, qs: QuerySet, params: CrudParams) -> QuerySet:
        if not params.q or not self.search_fields:
            return qs

        query = Q()
        for f in self.search_fields:
            query |= Q(**{f"{f}__icontains": params.q})
        return qs.filter(query)

    def apply_filters(self, qs: QuerySet, params: CrudParams, request: HttpRequest) -> QuerySet:
        data = params.as_dict()
        for f in self.filters:
            raw = (data.get(f.name) or "").strip()
            if not raw or raw == "all":
                continue
            qs = f.apply_to(qs, raw, request)
        return qs

    def apply_ordering(self, qs: QuerySet, params: CrudParams) -> QuerySet:
        sort_key = params.sort or self.default_sort_key
        direction = params.dir or self.default_dir
        prefix = "-" if direction == "desc" else ""

        col = next((c for c in self.list_columns if c.key == sort_key), None)
        order_by = col.order_by if col and col.sortable else None

        if not order_by:
            # Fallback: si no hay orden declarada, usa pk estable.
            return qs.order_by(f"{prefix}pk")

        fields: tuple[str, ...]
        if isinstance(order_by, str):
            fields = (order_by, "pk")
        else:
            fields = tuple(order_by) + ("pk",)

        return qs.order_by(*[f"{prefix}{f}" for f in fields])

    def queryset_for_list(self, request: HttpRequest, params: CrudParams) -> QuerySet:
        qs = self.get_base_queryset(request)
        qs = self.apply_search(qs, params)
        qs = self.apply_filters(qs, params, request)
        qs = self.apply_ordering(qs, params)
        return qs

    def columns_for_template(self) -> list[dict]:
        return [c.to_template_dict() for c in self.list_columns]

    def row_cells(self, obj: Any) -> list[Any]:
        cells: list[Any] = []
        for c in self.list_columns:
            if c.value:
                cells.append(c.value(obj))
            else:
                cells.append(getattr(obj, c.key, ""))
        return cells

    def row_urls(self, obj: Any, request: HttpRequest, params: CrudParams) -> dict:
        """MVP: por defecto no define URLs. La app concreta debe sobrescribir."""

        return {"detail": None, "edit": "#", "delete": "#"}

    # --- Step 8 helpers (defaults deben calzar con Step 4) ---
    def get_create_form_class(self) -> Type[forms.ModelForm] | None:
        return self.create_form_class

    def get_edit_form_class(self) -> Type[forms.ModelForm] | None:
        return self.edit_form_class

    def get_create_modal_title(self) -> str:
        if self.create_title:
            return self.create_title
        if self.entity_label:
            return f"Nuevo {self.entity_label}"
        return "Nuevo"

    def get_edit_modal_title(self, obj: Any) -> str:
        if self.edit_title:
            # Permite template simple: "Editar Item #{pk}".
            return self.edit_title.format(pk=getattr(obj, "pk", ""))
        label = self.entity_label or ""
        return f"Editar {label} #{getattr(obj, 'pk', '')}".strip()

    def get_delete_modal_title(self, obj: Any) -> str:
        if self.delete_title:
            return self.delete_title.format(pk=getattr(obj, "pk", ""))
        label = self.entity_label or ""
        return f"Eliminar {label} #{getattr(obj, 'pk', '')}".strip()

    def get_create_submit_label(self) -> str:
        return self.create_submit_label or "Crear"

    def get_edit_submit_label(self) -> str:
        return self.edit_submit_label or "Guardar"

    def get_delete_confirm_label(self) -> str:
        return self.delete_confirm_label or "Eliminar"

    # --- Step 9 helpers (defaults: allow) ---
    def can_list(self, request: HttpRequest) -> bool:
        return CrudPermissionSpec(self.permission_list).is_allowed(request)

    def can_create(self, request: HttpRequest) -> bool:
        return CrudPermissionSpec(self.permission_create).is_allowed(request)

    def can_edit(self, request: HttpRequest) -> bool:
        return CrudPermissionSpec(self.permission_edit).is_allowed(request)

    def can_delete(self, request: HttpRequest) -> bool:
        return CrudPermissionSpec(self.permission_delete).is_allowed(request)

    def build_items(self, page_obj, request: HttpRequest, params: CrudParams) -> list[dict]:
        data = {k: v for k, v in params.as_dict().items() if v not in {"", "all"}}
        qs_with_page = urlencode(data)

        rows: list[dict] = []
        for obj in page_obj.object_list:
            urls = self.row_urls(obj, request, params)
            # Preserva estado (incluye page) como en crud_example.
            if qs_with_page:
                for k in ("edit", "delete", "detail"):
                    if urls.get(k) and urls[k] not in {"#", None} and "?" not in str(urls[k]):
                        urls[k] = f"{urls[k]}?{qs_with_page}"

            # Build rich cells with column definition
            raw_cells = self.row_cells(obj)
            rich_cells = []
            for i, val in enumerate(raw_cells):
                col = self.list_columns[i]
                rich_cells.append({
                    "value": val,
                    "col": col.to_template_dict()
                })

            rows.append(
                {
                    "id": getattr(obj, "pk"),
                    "cells": rich_cells,
                    "urls": urls,
                }
            )
        return rows

    def paginate(self, qs: QuerySet, params: CrudParams):
        paginator = Paginator(qs, self.page_size)
        return paginator.get_page(params.page or 1)
