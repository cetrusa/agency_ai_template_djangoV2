from __future__ import annotations

from django.urls import path

from . import views

app_name = "orgs"

urlpatterns = [
    path("select/", views.select_organization, name="select"),
    path("activate/", views.activate_organization, name="activate"),
]
