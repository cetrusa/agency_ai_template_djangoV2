from django import forms
from .models import GlobalConfig

class SetupForm(forms.ModelForm):
    # Campos opcionales para crear superusuario (si no existe)
    admin_email = forms.EmailField(
        required=False, 
        label="Email del Administrador",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "admin@empresa.com"})
    )
    admin_password = forms.CharField(
        required=False, 
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    admin_password_confirm = forms.CharField(
        required=False, 
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = GlobalConfig
        fields = [
            "site_name", "logo", "login_icon",
            "welcome_message",
            "primary_color", "secondary_color",
            "company_address", "company_phone", "company_email",
        ]
        widgets = {
            "site_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. Mi Agencia Digital"}),
            "logo": forms.FileInput(attrs={"class": "form-control"}),
            "login_icon": forms.FileInput(attrs={"class": "form-control"}),
            "welcome_message": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Bienvenido a..."}),
            "primary_color": forms.TextInput(attrs={"class": "form-control form-control-color", "type": "color", "title": "Elige el color primario"}),
            "secondary_color": forms.TextInput(attrs={"class": "form-control form-control-color", "type": "color", "title": "Elige el color secundario"}),
            "company_address": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "company_phone": forms.TextInput(attrs={"class": "form-control"}),
            "company_email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("admin_password")
        confirm = cleaned_data.get("admin_password_confirm")
        email = cleaned_data.get("admin_email")

        # Si se provee password, deben coincidir
        if password or confirm:
            if password != confirm:
                self.add_error("admin_password_confirm", "Las contraseñas no coinciden.")
            if not email:
                self.add_error("admin_email", "El email es requerido si vas a crear un usuario.")
        
        return cleaned_data

