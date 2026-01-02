from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import parse_qs
from urllib.parse import urlparse
from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.http.response import HttpResponseBase
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .models import Item

from apps.core.crud.engine import build_list_context
from apps.core.crud.registry import get_crud
from .crud_config import CRUD_SLUG_ITEM

from apps.core.services.exporting import build_pdf_table, build_xlsx, stream_csv


@dataclass(frozen=True)
class _Col:
    key: str
    label: str
    sortable: bool = True
    nowrap: bool = False


def _get_params(request: HttpRequest) -> dict[str, str]:
    q = (request.GET.get("q") or "").strip()
    status = (request.GET.get("status") or "").strip()
    sort = (request.GET.get("sort") or "").strip()
    direction = (request.GET.get("dir") or "").strip().lower()
    page = (request.GET.get("page") or "1").strip()

    if direction not in {"asc", "desc"}:
        direction = "asc"

    return {
        "q": q,
        "status": status,
        "sort": sort,
        "dir": direction,
        "page": page,
        # presentes para compatibilidad con templates del kit
        "from": (request.GET.get("from") or "").strip(),
        "to": (request.GET.get("to") or "").strip(),
    }


def _build_qs_without_page(params: dict[str, str]) -> str:
    data = {k: v for k, v in params.items() if k != "page" and v not in {"", "all"}}
    return urlencode(data)


def _get_params_from_mapping(data: dict[str, str]) -> dict[str, str]:
    q = (data.get("q") or "").strip()
    status = (data.get("status") or "").strip()
    sort = (data.get("sort") or "").strip()
    direction = (data.get("dir") or "").strip().lower()
    page = (data.get("page") or "1").strip()

    if direction not in {"asc", "desc"}:
        direction = "asc"

    return {
        "q": q,
        "status": status,
        "sort": sort,
        "dir": direction,
        "page": page,
        "from": (data.get("from") or "").strip(),
        "to": (data.get("to") or "").strip(),
    }


def _get_params_from_hx_current_url(request: HttpRequest) -> dict[str, str] | None:
    current = request.headers.get("HX-Current-URL") or ""
    if not current:
        return None

    parsed = urlparse(current)
    if not parsed.query:
        return None

    raw = parse_qs(parsed.query)
    flat = {k: (v[-1] if v else "") for k, v in raw.items()}
    return _get_params_from_mapping(flat)


def _queryset(params: dict[str, str]):
    qs = Item.objects.all()

    if params["q"]:
        qs = qs.filter(Q(name__icontains=params["q"]))

    if params["status"] and params["status"] != "all":
        qs = qs.filter(status=params["status"])

    sort_map = {
        "name": "name",
        "status": "status",
        "created_at": "created_at",
    }
    sort_key = sort_map.get(params["sort"], "created_at")
    prefix = "-" if params["dir"] == "desc" else ""

    # Tie-breaker por PK para estabilidad.
    return qs.order_by(f"{prefix}{sort_key}", f"{prefix}id")


def _columns() -> list[dict]:
    return [
        _Col("name", "Nombre", sortable=True, nowrap=True).__dict__,
        _Col("status", "Estado", sortable=True, nowrap=True).__dict__,
        _Col("created_at", "Creado", sortable=True, nowrap=True).__dict__,
    ]


def _items(page_obj, *, params: dict[str, str]) -> list[dict]:
    rows = []
    qs_with_page = urlencode({k: v for k, v in params.items() if v not in {"", "all"}})
    for obj in page_obj.object_list:
        edit_url = reverse("crud_example:edit", kwargs={"id": obj.pk})
        delete_url = reverse("crud_example:delete", kwargs={"id": obj.pk})
        if qs_with_page:
            edit_url = f"{edit_url}?{qs_with_page}"
            delete_url = f"{delete_url}?{qs_with_page}"
        rows.append(
            {
                "id": obj.pk,
                "cells": [obj.name, obj.get_status_display(), obj.created_at.strftime("%Y-%m-%d")],
                # No implementamos modales en Step 2: dejamos placeholders.
                "urls": {"detail": None, "edit": edit_url, "delete": delete_url},
            }
        )
    return rows


def _context(request: HttpRequest) -> dict:
    params = _get_params(request)
    qs = _queryset(params)

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(params["page"] or 1)

    crud_urls = {
        "list": reverse("crud_example:list"),
        "table": reverse("crud_example:table"),
        # No implementados en Step 2
        "create": reverse("crud_example:create"),
        "bulk": "#",
        "export_csv": reverse("crud_example:export_csv"),
        "export_xlsx": reverse("crud_example:export_xlsx"),
        "export_pdf": reverse("crud_example:export_pdf"),
    }

    return {
        "crud_urls": crud_urls,
        "page_title": "CRUD Example",
        "entity_label": "Item",
        "entity_label_plural": "Items",
        "current_filters": params,
        "status_options": [("all", "Todos"), ("active", "Activo"), ("inactive", "Inactivo")],
        "columns": _columns(),
        "items": _items(page_obj, params=params),
        "page_obj": page_obj,
        "total_count": qs.count(),
        "qs": _build_qs_without_page(params),
    }


def _context_for_refresh(request: HttpRequest) -> dict:
    """Context para refrescar tabla tras modales.

    Prioriza HX-Current-URL (URL actual del navegador) para preservar filtros/sort/page.
    Fallback: usa request.GET.
    """

    params = _get_params_from_hx_current_url(request) or _get_params(request)
    qs = _queryset(params)

    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(params["page"] or 1)

    crud_urls = {
        "list": reverse("crud_example:list"),
        "table": reverse("crud_example:table"),
        "create": reverse("crud_example:create"),
        "bulk": "#",
        "export_csv": reverse("crud_example:export_csv"),
        "export_xlsx": reverse("crud_example:export_xlsx"),
        "export_pdf": reverse("crud_example:export_pdf"),
    }

    return {
        "crud_urls": crud_urls,
        "page_title": "CRUD Example",
        "entity_label": "Item",
        "entity_label_plural": "Items",
        "current_filters": params,
        "status_options": [("all", "Todos"), ("active", "Activo"), ("inactive", "Inactivo")],
        "columns": _columns(),
        "items": _items(page_obj, params=params),
        "page_obj": page_obj,
        "total_count": qs.count(),
        "qs": _build_qs_without_page(params),
    }


def list_view(request: HttpRequest) -> HttpResponse:
    config = get_crud(CRUD_SLUG_ITEM)
    if not config.can_list(request):
        return HttpResponseForbidden("Forbidden")
    crud_urls = {
        "list": reverse("crud_example:list"),
        "table": reverse("crud_example:table"),
        # Aunque Step 7 es list-only, el UI existente requiere estas URLs.
        "create": reverse("crud_example:create"),
        "bulk": "#",
        "export_csv": reverse("crud_example:export_csv"),
        "export_xlsx": reverse("crud_example:export_xlsx"),
        "export_pdf": reverse("crud_example:export_pdf"),
    }
    ctx = build_list_context(config=config, request=request, crud_urls=crud_urls)
    return render(request, "crud/list.html", ctx)


def table_view(request: HttpRequest) -> HttpResponse:
    # Endpoint HTMX: solo el partial de tabla
    config = get_crud(CRUD_SLUG_ITEM)
    if not config.can_list(request):
        return HttpResponseForbidden("Forbidden")
    crud_urls = {
        "list": reverse("crud_example:list"),
        "table": reverse("crud_example:table"),
        "create": reverse("crud_example:create"),
        "bulk": "#",
        "export_csv": reverse("crud_example:export_csv"),
        "export_xlsx": reverse("crud_example:export_xlsx"),
        "export_pdf": reverse("crud_example:export_pdf"),
    }
    ctx = build_list_context(config=config, request=request, crud_urls=crud_urls)
    return render(request, "crud/_table.html", ctx)


def _export_queryset(request: HttpRequest):
    params = _get_params(request)
    return _queryset(params)


def export_csv_view(request: HttpRequest) -> HttpResponseBase:
    config = get_crud(CRUD_SLUG_ITEM)
    if not config.can_export(request):
        return HttpResponseForbidden("Forbidden")
    if not config.is_export_enabled():
        return HttpResponseForbidden("Export disabled")
    if not config.allows_format("csv"):
        return HttpResponseForbidden("Format not allowed")

    params = config.parse_params(request)
    qs = config.queryset_for_list(request=request, params=params)

    fields = config.get_export_fields() or ["name", "status", "created_at"]
    headers = config.get_export_headers() or ["Nombre", "Estado", "Creado"]
    return stream_csv(
        queryset=qs,
        fields=fields,
        headers=headers,
        filename_base="crud_example_items",
    )


def export_xlsx_view(request: HttpRequest) -> HttpResponseBase:
    config = get_crud(CRUD_SLUG_ITEM)
    if not config.can_export(request):
        return HttpResponseForbidden("Forbidden")
    if not config.is_export_enabled():
        return HttpResponseForbidden("Export disabled")
    if not config.allows_format("xlsx"):
        return HttpResponseForbidden("Format not allowed")

    params = config.parse_params(request)
    qs = config.queryset_for_list(request=request, params=params)

    fields = config.get_export_fields() or ["name", "status", "created_at"]
    headers = config.get_export_headers() or ["Nombre", "Estado", "Creado"]
    return build_xlsx(
        queryset=qs,
        fields=fields,
        headers=headers,
        filename_base="crud_example_items",
        sheet_name="Items",
    )


def export_pdf_view(request: HttpRequest) -> HttpResponseBase:
    config = get_crud(CRUD_SLUG_ITEM)
    if not config.can_export(request):
        return HttpResponseForbidden("Forbidden")
    if not config.is_export_enabled():
        return HttpResponseForbidden("Export disabled")
    if not config.allows_format("pdf"):
        return HttpResponseForbidden("Format not allowed")

    params = config.parse_params(request)
    qs = config.queryset_for_list(request=request, params=params)

    fields = config.get_export_fields() or ["name", "status", "created_at"]
    headers = config.get_export_headers() or ["Nombre", "Estado", "Creado"]
    return build_pdf_table(
        queryset=qs,
        fields=fields,
        headers=headers,
        title="CRUD Example · Items",
        filename_base="crud_example_items",
    )


def _hx_modal_success_refresh(request: HttpRequest) -> HttpResponse:
    """Respuesta estándar de éxito para modales:

    - Cierra modal vía HX-Trigger
    - Refresca tabla preservando filtros/sort/page vía OOB swap
    """

    resp = render(request, "crud_example/_oob_table_refresh.html", _context_for_refresh(request))
    resp["HX-Trigger"] = '{"modalClose": true}'
    return resp


def create_view(request: HttpRequest) -> HttpResponseBase:
    config = get_crud(CRUD_SLUG_ITEM)
    if not config.can_create(request):
        return HttpResponseForbidden("Forbidden")
    form_class = config.get_create_form_class()
    if form_class is None:
        # Fallback explícito (solo si la config no declara). No auto-genera forms.
        from .forms import ItemForm as _FallbackItemForm

        form_class = _FallbackItemForm

    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            return _hx_modal_success_refresh(request)

        return render(
            request,
            "partials/modals/modal_form.html",
            {
                "modal_title": config.get_create_modal_title(),
                "modal_size": "md",
                "modal_backdrop_close": False,
                "form_action": reverse("crud_example:create"),
                "form": form,
                "submit_label": config.get_create_submit_label(),
            },
        )

    form = form_class()
    return render(
        request,
        "partials/modals/modal_form.html",
        {
            "modal_title": config.get_create_modal_title(),
            "modal_size": "md",
            "modal_backdrop_close": False,
            "form_action": reverse("crud_example:create"),
            "form": form,
            "submit_label": config.get_create_submit_label(),
        },
    )


def edit_view(request: HttpRequest, id: int) -> HttpResponseBase:
    config = get_crud(CRUD_SLUG_ITEM)
    if not config.can_edit(request):
        return HttpResponseForbidden("Forbidden")
    form_class = config.get_edit_form_class()
    if form_class is None:
        from .forms import ItemForm as _FallbackItemForm

        form_class = _FallbackItemForm

    obj = get_object_or_404(Item, pk=id)

    if request.method == "POST":
        form = form_class(request.POST, instance=obj)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            return _hx_modal_success_refresh(request)

        return render(
            request,
            "partials/modals/modal_form.html",
            {
                "modal_title": config.get_edit_modal_title(obj),
                "modal_size": "md",
                "modal_backdrop_close": False,
                "form_action": reverse("crud_example:edit", kwargs={"id": obj.pk}),
                "form": form,
                "submit_label": config.get_edit_submit_label(),
            },
        )

    form = form_class(instance=obj)
    return render(
        request,
        "partials/modals/modal_form.html",
        {
            "modal_title": config.get_edit_modal_title(obj),
            "modal_size": "md",
            "modal_backdrop_close": False,
            "form_action": reverse("crud_example:edit", kwargs={"id": obj.pk}),
            "form": form,
            "submit_label": config.get_edit_submit_label(),
        },
    )


def delete_view(request: HttpRequest, id: int) -> HttpResponseBase:
    config = get_crud(CRUD_SLUG_ITEM)
    if not config.can_delete(request):
        return HttpResponseForbidden("Forbidden")
    obj = get_object_or_404(Item, pk=id)

    if request.method == "POST":
        with transaction.atomic():
            obj.delete()
        return _hx_modal_success_refresh(request)

    return render(
        request,
        "partials/modals/modal_confirm.html",
        {
            "modal_title": config.get_delete_modal_title(obj),
            "modal_size": "sm",
            "modal_backdrop_close": True,
            "confirm_action": reverse("crud_example:delete", kwargs={"id": obj.pk}),
            "confirm_label": config.get_delete_confirm_label(),
            "confirm_variant": "danger",
            "confirm_message": "¿Eliminar este registro?",
            "confirm_detail": obj.name,
        },
    )
