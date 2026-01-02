"""Views UI-only para demostrar Server-Driven UI + HTMX.

Patrón clave:
- Si la request es HTMX (HX-Request: true), devolvemos SOLO el fragmento.
- Si no lo es, devolvemos página completa extendiendo base.html.

Esto permite:
- Navegación parcial (sin SPA)
- Deep-linking (URL real)
- Reutilización de templates
"""

from __future__ import annotations

from dataclasses import dataclass
import random
from datetime import timedelta
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from apps.core.dashboard.defs import KpiDef, ChartDef, ChartDataset
from .forms import DemoQuickActionForm, DemoTableFilterForm


def _is_htmx(request: HttpRequest) -> bool:
    return request.headers.get("HX-Request") == "true"


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    # Verificación de acceso post-registro
    if not request.user.is_staff and not request.user.groups.exists():
        return redirect("accounts:verification_pending")

    template = "dashboard/index.html" if _is_htmx(request) else "pages/dashboard.html"
    return render(request, template)


@login_required
def kpis(request: HttpRequest) -> HttpResponse:
    User = get_user_model()
    user_count = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    
    # Simulación de datos reales
    kpi_list = [
        KpiDef(
            label="Usuarios Totales",
            value=str(user_count),
            sub_label="Registrados",
            badge_text="Total",
            badge_color="primary"
        ),
        KpiDef(
            label="Usuarios Activos",
            value=str(active_users),
            sub_label="En plataforma",
            badge_text="Activos",
            badge_color="success"
        ),
        KpiDef(
            label="Incidencias",
            value="0",
            sub_label="Últimas 24h",
            badge_text="Healthy",
            badge_color="success"
        ),
        KpiDef(
            label="SLA",
            value="100%",
            sub_label="30 días",
            badge_text="Stable",
            badge_color="info"
        ),
    ]
    return render(request, "dashboard/_kpis.html", {"kpis": kpi_list})


@login_required
def charts(request: HttpRequest) -> HttpResponse:
    # Gráfico real: Usuarios registrados últimos 7 días
    User = get_user_model()
    today = timezone.now().date()
    labels = []
    data_users = []
    
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = User.objects.filter(date_joined__date=day).count()
        labels.append(day.strftime("%a"))
        data_users.append(count)
    
    chart_main = ChartDef(
        id="mainChart",
        title="Nuevos Usuarios (7 días)",
        type="line",
        labels=labels,
        datasets=[
            ChartDataset(
                label="Registros",
                data=data_users,
                color="primary",
                fill=True
            ),
        ]
    )

    return render(request, "dashboard/_charts.html", {"charts": [chart_main]})



@dataclass(frozen=True)
class _Row:
    name: str
    status: str
    updated: str
    owner: str


@login_required
def table(request: HttpRequest) -> HttpResponse:
    # Dataset demo (UI-only).
    rows = [
        _Row("API Billing", "ok", "hace 2m", "System"),
        _Row("Jobs Scheduler", "warn", "hace 12m", "Ops"),
        _Row("Payments", "ok", "hace 5m", "Finance"),
        _Row("Email Delivery", "down", "hace 1h", "Comms"),
        _Row("CRM Sync", "ok", "hace 9m", "Sales"),
        _Row("Data Warehouse", "warn", "hace 30m", "Data"),
        _Row("Search", "ok", "hace 3m", "Platform"),
        _Row("Webhooks", "ok", "hace 6m", "Platform"),
        _Row("SLA Monitor", "warn", "hace 17m", "Ops"),
        _Row("Exports", "ok", "hace 4m", "Finance"),
        _Row("Invoicing", "ok", "hace 11m", "Finance"),
        _Row("Audit Logs", "ok", "hace 8m", "Security"),
    ]

    form = DemoTableFilterForm(request.GET or None)
    if form.is_valid():
        q = (form.cleaned_data.get("q") or "").strip().lower()
        status = (form.cleaned_data.get("status") or "").strip()
        if q:
            rows = [r for r in rows if q in r.name.lower()]
        if status:
            rows = [r for r in rows if r.status == status]

    paginator = Paginator(rows, 5)
    page = paginator.get_page(request.GET.get("page") or 1)

    return render(
        request,
        "dashboard/_tables.html",
        {
            "filter_form": form,
            "page": page,
        },
    )


@login_required
def quick_action(request: HttpRequest) -> HttpResponse:
    """Formulario HTMX: GET render + POST validation.

    No persiste nada; devuelve un mensaje de éxito para demostrar el flujo.
    """

    if request.method == "POST":
        form = DemoQuickActionForm(request.POST)
        if form.is_valid():
            return render(request, "ui/_quick_action_success.html", {"data": form.cleaned_data})
    else:
        form = DemoQuickActionForm()

    return render(request, "ui/_quick_action_form.html", {"form": form})


@login_required
def modal_content(request: HttpRequest) -> HttpResponse:
    return render(request, "ui/_modal_content.html")
