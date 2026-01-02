from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm

User = get_user_model()


class UserProfileForm(forms.ModelForm):
    """Formulario para actualizar el perfil del usuario."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()
        if not email:
            raise forms.ValidationError("El email es obligatorio")
        
        qs = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise forms.ValidationError("Ya existe un usuario con este email")
        return email


class CustomPasswordChangeForm(PasswordChangeForm):
    """Formulario personalizado para cambio de contraseña."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class UserRegisterForm(forms.ModelForm):
    """Formulario de registro de usuario público."""
    
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "············"}),
        min_length=8,
    )
    password_confirm = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "············"}),
    )

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "jdoe"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "john@example.com"}),
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "John"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Doe"}),
        }

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()
        if not email:
            raise forms.ValidationError("El email es obligatorio")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe un usuario con este email")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "Las contraseñas no coinciden")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_active = False  # Inactivo hasta verificar email
        if commit:
            user.save()
        return user
