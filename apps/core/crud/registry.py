from __future__ import annotations

from typing import Dict

from .config import CrudConfig


_CRUDS: Dict[str, CrudConfig] = {}


def register_crud(config: CrudConfig) -> None:
    """Registro explícito. No hay auto-discovery."""

    slug = (config.crud_slug or "").strip()
    if not slug:
        raise ValueError("CrudConfig.crud_slug es obligatorio")

    if slug in _CRUDS:
        raise ValueError(f"CrudConfig ya registrado: {slug}")

    _CRUDS[slug] = config


def get_crud(slug: str) -> CrudConfig:
    config = _CRUDS.get(slug)
    if not config:
        raise KeyError(f"CrudConfig no registrado: {slug}")
    return config
