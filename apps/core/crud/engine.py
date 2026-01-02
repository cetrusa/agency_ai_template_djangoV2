from __future__ import annotations

from django.http import HttpRequest

from .config import CrudConfig


def build_list_context(
    *,
    config: CrudConfig,
    request: HttpRequest,
    crud_urls: dict,
) -> dict:
    """Construye el context contract requerido por templates/crud/*.

    LIST ONLY: columnas/items/page_obj/filters/ordering/paginación.
    """

    params = config.parse_params(request)
    qs = config.queryset_for_list(request, params)
    page_obj = config.paginate(qs, params)

    return {
        "crud_urls": crud_urls,
        "page_title": config.page_title or "Listado",
        "entity_label": config.entity_label or "",
        "entity_label_plural": config.entity_label_plural or "",
        "current_filters": params.as_dict(),
        "status_options": config.status_options,
        "columns": config.columns_for_template(),
        "items": config.build_items(page_obj, request, params),
        "page_obj": page_obj,
        "total_count": qs.count(),
        "qs": config.build_qs_without_page(params),
    }
