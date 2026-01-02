from __future__ import annotations

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()


class UserCreateForm(forms.ModelForm):
    """Formulario para crear usuarios nuevos.
    
    Incluye validación de contraseña y campos obligatorios para auditoría.
    """
    first_name = forms.CharField(
        label="Nombre",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre del usuario"}),
        help_text="Requerido para auditoría y trazabilidad."
    )
    last_name = forms.CharField(
        label="Apellido",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Apellido del usuario"}),
        help_text="Requerido para auditoría y trazabilidad."
    )
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "correo@ejemplo.com"}),
        help_text="Email corporativo del usuario."
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        strip=False,
        help_text="Debe cumplir con las políticas de seguridad."
    )
    password2 = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        strip=False,
    )

    is_staff = forms.BooleanField(
        label="Acceso al Panel Admin",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        help_text="Permite acceso al panel de administración de Django."
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "is_active", "is_staff")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "usuario.nombre"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_staff": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        help_texts = {
            "username": "Identificador único del usuario. Solo letras, números y @/./+/-/_",
            "is_active": "Marca como activo para permitir el acceso al sistema.",
            "is_staff": "Da permisos de administrador del sistema.",
        }

    def clean_username(self):
        username = (self.cleaned_data.get("username") or "").strip().lower()
        if not username:
            raise ValidationError("El nombre de usuario es obligatorio")
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("Ya existe un usuario con este nombre de usuario")
        return username

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if not email:
            raise ValidationError("El email es obligatorio")
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Ya existe un usuario con este email")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if password:
            validate_password(password)
        return password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1") or ""
        p2 = cleaned.get("password2") or ""
        
        if p1 != p2:
            raise ValidationError("Las contraseñas no coinciden")
        
        if len(p1) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres")
        
        # Validación adicional de seguridad
        if p1 and p1.lower() == cleaned.get("username", "").lower():
            raise ValidationError("La contraseña no puede ser igual al nombre de usuario")
        
        if p1 and p1.lower() in ["password", "12345678", "qwerty123"]:
            raise ValidationError("La contraseña es demasiado común")
        
        return cleaned

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        user.set_password(password)
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):
    """Formulario para editar usuarios existentes.
    
    No permite cambiar username (identificador único).
    No permite eliminar usuarios (solo desactivar por auditoría).
    """
    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop("request_user", None)
        super().__init__(*args, **kwargs)
        
        # Personalizar widgets y ayudas
        self.fields["first_name"].widget.attrs.update({"class": "form-control"})
        self.fields["last_name"].widget.attrs.update({"class": "form-control"})
        self.fields["email"].widget.attrs.update({"class": "form-control"})
        self.fields["is_active"].widget.attrs.update({"class": "form-check-input"})
        self.fields["is_staff"].widget.attrs.update({"class": "form-check-input"})
        
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["email"].required = True
        
        self.fields["is_active"].help_text = (
            "NOTA: Los usuarios nunca se eliminan del sistema por razones de auditoría. "
            "Desactivar impide el acceso pero conserva el historial."
        )
        
        self.fields["is_staff"].help_text = (
            "Solo superusuarios pueden modificar permisos de staff."
        )
        
        # Deshabilitar is_staff si el usuario actual no es superusuario
        if self.request_user and not self.request_user.is_superuser:
            self.fields["is_staff"].disabled = True
            self.fields["is_staff"].help_text = "Solo superusuarios pueden modificar este campo."

    def set_request_user(self, user):
        """Permite asignar el usuario de la petición después de instanciar el formulario."""
        self.request_user = user

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "is_active", "is_staff")

    def clean_first_name(self):
        first_name = (self.cleaned_data.get("first_name") or "").strip()
        if not first_name:
            raise ValidationError("El nombre es obligatorio")
        return first_name

    def clean_last_name(self):
        last_name = (self.cleaned_data.get("last_name") or "").strip()
        if not last_name:
            raise ValidationError("El apellido es obligatorio")
        return last_name

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if not email:
            raise ValidationError("El email es obligatorio")
        qs = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe un usuario con este email")
        return email

    def clean_is_active(self):
        is_active = bool(self.cleaned_data.get("is_active"))
        
        # Protección: no desactivar a sí mismo
        if self.instance and self.request_user and self.instance.pk == self.request_user.pk and not is_active:
            raise ValidationError("No puedes desactivar tu propio usuario")
        
        # Protección: no desactivar superusuarios (opcional pero recomendado)
        if self.instance and self.instance.is_superuser and not is_active:
            if not self.request_user or not self.request_user.is_superuser:
                raise ValidationError("Solo superusuarios pueden desactivar cuentas de administrador")
        
        return is_active
    
    def clean_is_staff(self):
        is_staff = bool(self.cleaned_data.get("is_staff"))
        
        # Protección: solo superusuarios pueden modificar permisos de staff
        if self.instance and self.instance.is_staff != is_staff:
            if not self.request_user or not self.request_user.is_superuser:
                raise ValidationError("Solo superusuarios pueden modificar permisos de administrador")
        
        # Protección: no quitar is_staff a sí mismo
        if self.instance and self.request_user and self.instance.pk == self.request_user.pk:
            if self.instance.is_staff and not is_staff:
                raise ValidationError("No puedes quitarte tus propios permisos de staff")
        
        return is_staff
