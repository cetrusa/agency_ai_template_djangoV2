from __future__ import annotations

import uuid

from django.core.cache import cache
from django.db import models
from django.utils.translation import gettext_lazy as _


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SingletonModel(models.Model):
    """Modelo abstracto para tablas que solo deben tener 1 registro."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        self.set_cache()

    def delete(self, *args, **kwargs):
        pass  # No permitir borrar

    @classmethod
    def load(cls):
        if cache.get(cls.__name__) is None:
            obj, created = cls.objects.get_or_create(pk=1)
            if created:
                obj.set_cache()
            return obj
        return cache.get(cls.__name__)

    def set_cache(self):
        cache.set(self.__class__.__name__, self)


class GlobalConfig(SingletonModel):
    """Configuración global de la empresa/instancia."""

    # Identidad
    site_name = models.CharField(
        _("Nombre del Sitio"),
        max_length=100,
        default="Agency Dashboard",
        help_text="Nombre que aparece en el título y navbar.",
    )
    logo = models.ImageField(
        _("Logo"),
        upload_to="branding/",
        null=True,
        blank=True,
        help_text="Logo para el sidebar/navbar (idealmente SVG o PNG transparente).",
    )
    
    # Login / Bienvenida
    login_icon = models.ImageField(
        _("Icono Login"),
        upload_to="branding/",
        null=True,
        blank=True,
        help_text="Icono que aparece en la pantalla de login (opcional).",
    )
    welcome_message = models.TextField(
        _("Mensaje de Bienvenida"),
        default="Bienvenido a tu plataforma",
        help_text="Mensaje que aparece en la pantalla de login.",
    )
    setup_complete = models.BooleanField(
        _("Setup Completado"),
        default=False,
        help_text="Indica si el asistente de configuración inicial ya se completó.",
    )

    # Tema Visual (Sneat overrides)
    primary_color = models.CharField(
        _("Color Primario"),
        max_length=7,
        default="#696cff",
        help_text="Color principal (botones, links, active states). Hexadecimal.",
    )
    secondary_color = models.CharField(
        _("Color Secundario"),
        max_length=7,
        default="#8592a3",
        help_text="Color secundario (bordes, textos secundarios). Hexadecimal.",
    )
    
    # Información de Contacto (Footer / Facturas)
    company_address = models.TextField(_("Dirección"), blank=True)
    company_phone = models.CharField(_("Teléfono"), max_length=50, blank=True)
    company_email = models.EmailField(_("Email de Contacto"), blank=True)
    
    # Redes Sociales
    social_facebook = models.URLField(_("Facebook"), blank=True)
    social_twitter = models.URLField(_("Twitter / X"), blank=True)
    social_instagram = models.URLField(_("Instagram"), blank=True)
    social_linkedin = models.URLField(_("LinkedIn"), blank=True)

    # Opciones de Layout
    navbar_fixed = models.BooleanField(
        _("Navbar Fijo"),
        default=True,
        help_text="Si está activo, el navbar se queda fijo al hacer scroll.",
    )
    
    sidebar_collapsed = models.BooleanField(
        _("Sidebar Colapsado"),
        default=False,
        help_text="Estado inicial del sidebar.",
    )

    class Meta:
        verbose_name = "Configuración Global"
        verbose_name_plural = "Configuración Global"

    def __str__(self):
        return "Configuración del Sistema"
