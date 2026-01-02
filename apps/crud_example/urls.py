from django.urls import path

from . import views

app_name = "crud_example"

urlpatterns = [
    path("", views.list_view, name="list"),
    path("table/", views.table_view, name="table"),
    path("create/", views.create_view, name="create"),
    path("<int:id>/edit/", views.edit_view, name="edit"),
    path("<int:id>/delete/", views.delete_view, name="delete"),
    path("export/csv/", views.export_csv_view, name="export_csv"),
    path("export/xlsx/", views.export_xlsx_view, name="export_xlsx"),
    path("export/pdf/", views.export_pdf_view, name="export_pdf"),
]
