from django.urls import path
from . import views

app_name = "organization_admin"

urlpatterns = [
    path("", views.detail, name="detail"),
    path("edit/", views.edit, name="edit"),
]
