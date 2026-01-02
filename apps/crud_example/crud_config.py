from __future__ import annotations

from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse

from apps.core.crud import ColumnDef, CrudConfig, FilterDef, register_crud

from .models import Item
from .forms import ItemForm


CRUD_SLUG_ITEM = "crud_example.items"


def _filter_status(qs: QuerySet, value: str, request: HttpRequest) -> QuerySet:
    return qs.filter(status=value)


class ItemCrudConfig(CrudConfig):
    crud_slug = CRUD_SLUG_ITEM
    model = Item

    page_title = "CRUD Example"
    entity_label = "Item"
    entity_label_plural = "Items"

    page_size = 10

    # Match Step 2 behavior exactly
    search_fields = ["name"]

    list_columns = [
        ColumnDef(
            key="name",
            label="Nombre",
            sortable=True,
            nowrap=True,
            order_by=("name",),
            value=lambda o: o.name,
        ),
        ColumnDef(
            key="status",
            label="Estado",
            type="badge",
            extra={
                "colors": {"active": "success", "inactive": "secondary"},
                "labels": {"active": "Activo", "inactive": "Inactivo"}
            },
            sortable=True,
            nowrap=True,
            order_by=("status",),
            value=lambda o: o.status,
        ),
        ColumnDef(
            key="created_at",
            label="Creado",
            type="date",
            sortable=True,
            nowrap=True,
            order_by=("created_at",),
            value=lambda o: o.created_at,
        ),
    ]

    filters = [FilterDef(name="status", apply=_filter_status)]

    # Default sort: created_at asc (same as Step 2)
    default_sort_key = "created_at"
    default_dir = "asc"

    status_options = [("all", "Todos"), ("active", "Activo"), ("inactive", "Inactivo")]

    # Step 8 (MVP): forms + modal metadata (sin auto-generación)
    create_form_class = ItemForm
    edit_form_class = ItemForm

    create_title = "Nuevo Item"
    # titles con template simple; {pk} se resuelve en runtime.
    edit_title = "Editar Item #{pk}"
    delete_title = "Eliminar Item #{pk}"

    create_submit_label = "Crear"
    edit_submit_label = "Guardar"
    delete_confirm_label = "Eliminar"

    # Step 9 (MVP): permisos declarativos
    # Django crea: add/change/delete/view para el modelo.
    permission_list = "crud_example.view_item"
    permission_create = "crud_example.add_item"
    permission_edit = "crud_example.change_item"
    permission_delete = "crud_example.delete_item"

    # Step 10 (MVP): export declarativo
    export_enabled = True
    export_fields = ["name", "status", "created_at"]
    export_headers = {
        "name": "Nombre",
        "status": "Estado",
        "created_at": "Creado",
    }
    export_formats = {"csv", "xlsx", "pdf"}

    def row_urls(self, obj: Item, request: HttpRequest, params) -> dict:
        return {
            "detail": None,
            "edit": reverse("crud_example:edit", kwargs={"id": obj.pk}),
            "delete": reverse("crud_example:delete", kwargs={"id": obj.pk}),
        }


def register() -> None:
    register_crud(ItemCrudConfig())
