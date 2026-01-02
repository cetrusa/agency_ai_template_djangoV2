from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

from django.db.models import QuerySet
from django.http import HttpRequest


ValueFunc = Callable[[Any], str]
ApplyFilterFunc = Callable[[QuerySet, str, HttpRequest], QuerySet]


@dataclass(frozen=True)
class ColumnDef:
    """Declaración explícita de una columna del CRUD Kit.

    - key: sort key público (querystring: sort=<key>)
    - label: texto visible
    - type: tipo de visualización (text, badge, image, boolean, link, date, currency)
    - extra: configuración extra para el tipo (ej: mapa de colores para badge)
    - order_by: campo(s) reales para QuerySet.order_by
    - value: función que produce el string final para la celda
    """

    key: str
    label: str
    type: str = "text"
    extra: dict = field(default_factory=dict)
    sortable: bool = True
    nowrap: bool = False

    order_by: str | tuple[str, ...] | None = None
    value: ValueFunc | None = None

    def to_template_dict(self) -> dict:
        return {
            "key": self.key,
            "label": self.label,
            "type": self.type,
            "extra": self.extra,
            "sortable": self.sortable,
            "nowrap": self.nowrap,
        }


@dataclass(frozen=True)
class FilterDef:
    """Declaración explícita de filtro server-side.

    - name: nombre en querystring (ej: status)
    - apply: función que aplica el filtro al queryset
    """

    name: str
    apply: ApplyFilterFunc

    def apply_to(self, qs: QuerySet, value: str, request: HttpRequest) -> QuerySet:
        return self.apply(qs, value, request)
