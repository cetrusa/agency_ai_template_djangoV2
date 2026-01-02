from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    # Dashboard (full page o partial según HTMX)
    path("", views.dashboard, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),

    # Widgets / módulos
    path("dashboard/kpis/", views.kpis, name="kpis"),
    path("dashboard/charts/", views.charts, name="charts"),
    path("dashboard/table/", views.table, name="table"),

    # UI demos
    path("ui/quick-action/", views.quick_action, name="quick_action"),
    path("ui/modal/content/", views.modal_content, name="modal_content"),
]
