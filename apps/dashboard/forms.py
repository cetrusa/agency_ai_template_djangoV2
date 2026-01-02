"""Formularios demo (UI-only).

Objetivo:
- Mostrar formularios dinámicos con HTMX
- Sin modelos / sin persistencia
"""

from __future__ import annotations

from django import forms


class DemoQuickActionForm(forms.Form):
    title = forms.CharField(
        label="Título",
        max_length=60,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Revisar facturas"}),
    )
    priority = forms.ChoiceField(
        label="Prioridad",
        choices=[("low", "Baja"), ("med", "Media"), ("high", "Alta")],
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class DemoTableFilterForm(forms.Form):
    q = forms.CharField(
        label="Buscar",
        required=False,
        max_length=40,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Buscar por nombre…"}),
    )
    status = forms.ChoiceField(
        label="Estado",
        required=False,
        choices=[("", "Todos"), ("ok", "OK"), ("warn", "Alerta"), ("down", "Caído")],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
