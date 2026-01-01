"""URL routing for the base dashboard template.

Este archivo se mantiene intencionalmente simple.
"""

from __future__ import annotations

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from apps.core.views import setup_wizard

urlpatterns = [
    path("admin/", admin.site.urls),
    path("setup/", setup_wizard, name="setup_wizard"),
    # Accounts: profile, password change
    path("accounts/", include(("apps.accounts.urls", "accounts"), namespace="accounts")),
    # Auth: login, logout, password_change, password_reset, etc.
    path(
        "accounts-auth/",
        include(("django.contrib.auth.urls", "accounts_auth"), namespace="accounts-auth"),
    ),
    # Apps
    path("crud-example/", include("apps.crud_example.urls")),
    path("dashboard/", include(("apps.dashboard.urls", "dashboard"), namespace="dashboard")),
    path("organization/", include("apps.organization_admin.urls")),
    path("users/", include("apps.users_admin.urls")),
    path("orgs/", include(("apps.orgs.urls", "orgs"), namespace="orgs")),
    path("", include(("apps.dashboard.urls", "dashboard"), namespace="home")),  # Default redirect (namespace distinto para evitar colisión)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
