from __future__ import annotations

from django.urls import path

from . import views

app_name = "users_admin"

urlpatterns = [
    path("", views.list_view, name="list"),
]
