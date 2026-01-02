"""Configuración CRUD para GlobalConfig (Empresa).

GlobalConfig es un modelo singleton (un único registro).
No tiene lista de múltiples registros, solo CRUD de su único registro.
"""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.http import HttpRequest

from apps.core.crud import CrudConfig, register_crud
from apps.core.models import GlobalConfig

from .forms import GlobalConfigForm


User = get_user_model()

CRUD_SLUG_ORGANIZATION = "organization_admin.config"


class OrganizationCrudConfig(CrudConfig):
    """Configuración CRUD para GlobalConfig (Empresa/Plataforma).
    
    NOTA: GlobalConfig es un modelo Singleton.
    - No hay listado de múltiples registros
    - Solo hay un registro (pk=1) que se edita
    - Las vistas de detail/edit son las únicas aplicables
    """
    
    crud_slug = CRUD_SLUG_ORGANIZATION
    model = GlobalConfig

    page_title = "Configuración de Empresa"
    entity_label = "Empresa"
    entity_label_plural = "Empresa"

    page_size = 1  # Singleton

    search_fields = ["site_name"]

    list_columns = []  # No aplica para singleton

    default_sort_key = ""
    default_dir = "asc"

    create_form_class = GlobalConfigForm
    edit_form_class = GlobalConfigForm

    create_title = "Configurar Empresa"
    edit_title = "Editar Configuración"
    delete_title = "Empresa"

    create_submit_label = "Guardar Configuración"
    edit_submit_label = "Guardar Cambios"
    delete_confirm_label = "Confirmar"

    permission_list = "core.view_globalconfig"
    permission_create = "core.add_globalconfig"
    permission_edit = "core.change_globalconfig"
    permission_delete = None  # No permitir borrar GlobalConfig

    export_enabled = False  # No aplica para singleton
    export_fields = []
    export_headers = None  # No aplica para singleton
    export_formats = set()

    def get_base_queryset(self, request: HttpRequest) -> QuerySet:
        """Retorna el QuerySet base (solo el singleton)."""
        return GlobalConfig.objects.all()


def register() -> None:
    """Registrar la configuración CRUD."""
    register_crud(OrganizationCrudConfig())
