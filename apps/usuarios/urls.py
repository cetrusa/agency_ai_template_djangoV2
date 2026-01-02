from __future__ import annotations

from django.urls import path

from . import views

app_name = "usuarios"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create_modal, name="create"),
    path("create/submit/", views.create_submit, name="create_submit"),
    path("<int:member_id>/edit/", views.edit_member_modal, name="edit"),
    path("<int:member_id>/edit/submit/", views.edit_member_submit, name="edit_submit"),
    path("<int:member_id>/toggle/", views.toggle_member_active, name="toggle"),
]
