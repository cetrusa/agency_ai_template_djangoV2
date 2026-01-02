from django.contrib import admin
from django.utils.html import format_html

from .models import GlobalConfig


@admin.register(GlobalConfig)
class GlobalConfigAdmin(admin.ModelAdmin):
    list_display = ["site_name", "color_preview", "navbar_fixed", "setup_complete"]
    fieldsets = (
        ("Identidad", {"fields": ("site_name", "logo", "login_icon", "welcome_message")}),
        ("Tema Visual", {"fields": ("primary_color", "secondary_color")}),
        ("Contacto", {"fields": ("company_address", "company_phone", "company_email")}),
        ("Redes Sociales", {"fields": ("social_facebook", "social_twitter", "social_instagram", "social_linkedin")}),
        ("Layout", {"fields": ("navbar_fixed", "sidebar_collapsed")}),
        ("Sistema", {"fields": ("setup_complete",)}),
    )

    def color_preview(self, obj):
        return format_html(
            '<div style="width: 24px; height: 24px; background-color: {}; border-radius: 4px; border: 1px solid #ccc;"></div>',
            obj.primary_color,
        )

    color_preview.short_description = "Color"

    def has_add_permission(self, request):
        # Solo permitir 1 registro
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False
