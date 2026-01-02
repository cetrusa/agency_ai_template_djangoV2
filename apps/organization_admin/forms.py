from django import forms
from django.core.exceptions import ValidationError
from apps.core.models import GlobalConfig


class GlobalConfigForm(forms.ModelForm):
    """Formulario para editar la configuración global de la empresa.
    
    NOTA: GlobalConfig es un modelo Singleton (un único registro).
    Este formulario siempre edita el mismo registro (pk=1).
    """

    class Meta:
        model = GlobalConfig
        fields = [
            "site_name",
            "logo",
            "login_icon",
            "welcome_message",
            "primary_color",
            "secondary_color",
            "company_address",
            "company_phone",
            "company_email",
            "social_facebook",
            "social_twitter",
            "social_instagram",
            "social_linkedin",
            "navbar_fixed",
            "sidebar_collapsed",
        ]
        widgets = {
            "site_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de tu empresa"}),
            "logo": forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "login_icon": forms.FileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "welcome_message": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Mensaje que aparecerá en login"}),
            "primary_color": forms.TextInput(attrs={"class": "form-control", "type": "color", "style": "height: 40px;"}),
            "secondary_color": forms.TextInput(attrs={"class": "form-control", "type": "color", "style": "height: 40px;"}),
            "company_address": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Dirección completa"}),
            "company_phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+34 900 123 456"}),
            "company_email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "contacto@empresa.com"}),
            "social_facebook": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://facebook.com/tuempresa"}),
            "social_twitter": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://twitter.com/tuempresa"}),
            "social_instagram": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://instagram.com/tuempresa"}),
            "social_linkedin": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://linkedin.com/company/tuempresa"}),
            "navbar_fixed": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "sidebar_collapsed": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        help_texts = {
            "site_name": "Nombre que aparecerá en toda la plataforma",
            "logo": "Logo para el sidebar (PNG o SVG recomendado)",
            "login_icon": "Icono opcional para la pantalla de login",
            "welcome_message": "Mensaje que ven los usuarios al iniciar sesión",
            "primary_color": "Color principal para botones y elementos activos",
            "secondary_color": "Color secundario para bordes y textos secundarios",
            "company_phone": "Teléfono de contacto corporativo",
            "company_email": "Email de contacto oficial",
            "navbar_fixed": "Si está marcado, la barra de navegación quedará fija al scroll",
            "sidebar_collapsed": "Estado inicial del sidebar (colapsado o expandido)",
        }

    def clean_site_name(self):
        site_name = (self.cleaned_data.get("site_name") or "").strip()
        if not site_name:
            raise ValidationError("El nombre de la empresa es obligatorio")
        if len(site_name) < 2:
            raise ValidationError("El nombre debe tener al menos 2 caracteres")
        return site_name

    def clean_company_email(self):
        email = (self.cleaned_data.get("company_email") or "").strip()
        # Email es opcional pero si se proporciona debe ser válido
        return email

    def clean_company_phone(self):
        phone = (self.cleaned_data.get("company_phone") or "").strip()
        # Teléfono es opcional pero si se proporciona, validar formato básico
        if phone and len(phone) < 8:
            raise ValidationError("El teléfono debe tener al menos 8 dígitos")
        return phone

    def save(self, commit: bool = True):
        config = super().save(commit=False)
        # GlobalConfig es singleton, siempre pk=1
        config.pk = 1
        if commit:
            config.save()
        return config
