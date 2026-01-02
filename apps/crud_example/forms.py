from __future__ import annotations

from django import forms

from .models import Item


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["name", "status"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre…",
                    "autocomplete": "off",
                }
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_name(self):
        name = (self.cleaned_data.get("name") or "").strip()
        if not name:
            raise forms.ValidationError("El nombre es obligatorio.")
        return name
