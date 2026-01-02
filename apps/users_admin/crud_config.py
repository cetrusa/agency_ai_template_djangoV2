from __future__ import annotations

from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.urls import reverse
from django.db.models import QuerySet

from apps.core.crud import ColumnDef, CrudConfig, FilterDef, register_crud

from .forms import UserCreateForm, UserEditForm


User = get_user_model()

CRUD_SLUG_USERS = "users_admin.users"


def _filter_by_status(qs: QuerySet, value: str, request: HttpRequest) -> QuerySet:
    """Filtro por estado de usuario (activo/inactivo)."""
    if value == "active":
        return qs.filter(is_active=True)
    elif value == "inactive":
        return qs.filter(is_active=False)
    return qs  # "all" o valor desconocido = sin filtro


def _filter_by_role(qs: QuerySet, value: str, request: HttpRequest) -> QuerySet:
    """Filtro por rol de usuario (staff/superuser/regular)."""
    if value == "superuser":
        return qs.filter(is_superuser=True)
    elif value == "staff":
        return qs.filter(is_staff=True, is_superuser=False)
    elif value == "regular":
        return qs.filter(is_staff=False, is_superuser=False)
    return qs  # "all" = sin filtro


class UserCrudConfig(CrudConfig):
    """Configuración CRUD para gestión de usuarios.
    
    IMPORTANTE: Los usuarios NUNCA se eliminan físicamente del sistema.
    Solo se pueden desactivar (is_active=False) para mantener integridad
    de auditoría y relaciones históricas.
    """
    crud_slug = CRUD_SLUG_USERS
    model = User

    page_title = "Gestión de Usuarios"
    entity_label = "Usuario"
    entity_label_plural = "Usuarios"

    page_size = 20

    search_fields = ["username", "email", "first_name", "last_name"]
    
    # Filtros disponibles
    filters = [
        FilterDef(name="status", apply=_filter_by_status),
        FilterDef(name="role", apply=_filter_by_role),
    ]
    
    status_options = [
        ("all", "Todos"),
        ("active", "Activos"),
        ("inactive", "Inactivos"),
    ]
    
    role_options = [
        ("all", "Todos los Roles"),
        ("superuser", "Superusuarios"),
        ("staff", "Staff"),
        ("regular", "Usuarios Regulares"),
    ]

    list_columns = [
        ColumnDef(
            key="username",
            label="Usuario",
            sortable=True,
            nowrap=True,
            order_by=("username",),
            value=lambda u: u.username,
        ),
        ColumnDef(
            key="full_name",
            label="Nombre Completo",
            sortable=True,
            nowrap=False,
            order_by=("first_name", "last_name"),
            value=lambda u: f"{u.first_name} {u.last_name}".strip() or "-",
        ),
        ColumnDef(
            key="email",
            label="Email",
            type="text",
            sortable=True,
            nowrap=False,
            order_by=("email",),
            value=lambda u: u.email or "-",
        ),
        ColumnDef(
            key="role",
            label="Rol",
            type="badge",
            sortable=True,
            nowrap=True,
            order_by=("is_superuser", "is_staff"),
            value=lambda u: (
                "Superusuario" if u.is_superuser
                else "Staff" if u.is_staff
                else "Usuario"
            ),
            extra={
                "colors": {
                    "Superusuario": "danger",
                    "Staff": "warning",
                    "Usuario": "secondary",
                },
                "labels": {},
            },
        ),
        ColumnDef(
            key="is_active",
            label="Estado",
            type="badge",
            sortable=True,
            nowrap=True,
            order_by=("is_active",),
            value=lambda u: "Activo" if u.is_active else "Inactivo",
            extra={
                "colors": {
                    "Activo": "success",
                    "Inactivo": "secondary",
                },
                "labels": {},
            },
        ),
        ColumnDef(
            key="date_joined",
            label="Fecha de Alta",
            type="date",
            sortable=True,
            nowrap=True,
            order_by=("date_joined",),
            value=lambda u: u.date_joined.strftime("%d/%m/%Y") if u.date_joined else "-",
        ),
        ColumnDef(
            key="last_login",
            label="Último Acceso",
            type="date",
            sortable=True,
            nowrap=True,
            order_by=("last_login",),
            value=lambda u: u.last_login.strftime("%d/%m/%Y %H:%M") if u.last_login else "Nunca",
        ),
    ]

    default_sort_key = "date_joined"
    default_dir = "desc"

    create_form_class = UserCreateForm
    edit_form_class = UserEditForm

    create_title = "Nuevo Usuario"
    edit_title = "Editar Usuario: {pk}"
    delete_title = "Cambiar Estado del Usuario"

    create_submit_label = "Crear Usuario"
    edit_submit_label = "Guardar Cambios"
    delete_confirm_label = "Confirmar"

    permission_list = "auth.view_user"
    permission_create = "auth.add_user"
    permission_edit = "auth.change_user"
    permission_delete = "auth.change_user"  # Solo cambio de estado, no DELETE

    export_enabled = True
    export_fields = [
        "username",
        "first_name",
        "last_name",
        "email",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
        "last_login",
    ]
    export_headers = {
        "username": "Usuario",
        "first_name": "Nombre",
        "last_name": "Apellido",
        "email": "Email",
        "is_active": "Activo",
        "is_staff": "Es Staff",
        "is_superuser": "Es Superusuario",
        "date_joined": "Fecha Alta",
        "last_login": "Último Acceso",
    }
    export_formats = {"csv", "xlsx", "pdf"}

    def row_urls(self, obj, request: HttpRequest, params):
        return {
            "detail": None,
            "edit": reverse("users_admin:edit", args=[obj.pk]),
            "delete": None,
        }
    
    def get_base_queryset(self, request: HttpRequest) -> QuerySet:
        """Query optimizado para listado."""
        return User.objects.all().select_related()


def register() -> None:
    register_crud(UserCrudConfig())