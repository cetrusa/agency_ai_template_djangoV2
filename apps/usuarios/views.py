from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from apps.orgs.decorators import organization_required
from apps.orgs.models import Membership
from apps.orgs.utils import get_active_organization
from apps.service_core.infra.context import ExecutionContext
from apps.service_core.base.result import ServiceError
from apps.usuarios.domain.inputs import (
    CreateMemberInput,
    ExportMembersInput,
    ListMembersInput,
    ToggleMemberActiveInput,
    UpdateMemberInput,
)
from apps.usuarios.services.create_member import CreateMemberService
from apps.usuarios.services.export_members import ExportMembersService
from apps.usuarios.services.list_members import ListMembersService
from apps.usuarios.services.toggle_member import ToggleMemberService
from apps.usuarios.services.update_member import UpdateMemberService


def _build_context(request: HttpRequest, memberships):
    return {
        "memberships": memberships,
        "organization": getattr(request, "organization", None),
    }


def _list_members(request: HttpRequest):
    org = getattr(request, "organization", None) or get_active_organization(request)
    if not org:
        return []
    service = ListMembersService()
    search = request.GET.get("q") or None
    role = request.GET.get("role") or None
    status = request.GET.get("status") or None

    is_active = None
    if status == "active":
        is_active = True
    elif status == "inactive":
        is_active = False

    result = service.execute(
        ListMembersInput(
            organization_id=org.id,
            include_inactive=True,
            search=search,
            role=role,
            is_active=is_active,
        ),
        actor=request.user,
    )
    return result.data.get("memberships", []) if result.ok else []


def _get_actor_membership(request: HttpRequest, organization):
    if not organization or not request.user.is_authenticated:
        return None
    return Membership.objects.filter(
        user=request.user,
        organization=organization,
        is_active=True,
    ).first()


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    value = value.strip().lower()
    return value in {"1", "true", "on", "yes"}


@login_required
@organization_required
def index(request: HttpRequest) -> HttpResponse:
    memberships = _list_members(request)
    membership = _get_actor_membership(request, getattr(request, "organization", None))
    context = _build_context(request, memberships)
    can_manage = bool(membership and membership.role == "admin")
    context["can_create_members"] = can_manage
    context["can_manage_members"] = can_manage
    context["filters"] = {
        "q": request.GET.get("q", ""),
        "role": request.GET.get("role", ""),
        "status": request.GET.get("status", ""),
    }

    if request.headers.get("HX-Request"):
        return render(request, "usuarios/_table.html", context)

    return render(request, "usuarios/index.html", context)


@login_required
@organization_required
def create_modal(request: HttpRequest) -> HttpResponse:
    org = getattr(request, "organization", None)
    
    # Check permissions explicitly for UI feedback
    membership = _get_actor_membership(request, org)
    if not membership or membership.role != "admin":
        return render(request, "usuarios/_modal_form.html", {
            "errors": [ServiceError(code="forbidden", message="Solo los administradores pueden agregar miembros.")],
            "org": org
        })

    context = _build_context(request, _list_members(request))
    context.update({"errors": [], "org": org})
    return render(request, "usuarios/_modal_form.html", context)


@login_required
@organization_required
@require_POST
def create_submit(request: HttpRequest) -> HttpResponse:
    org = getattr(request, "organization", None)
    if not org:
        return redirect("orgs:select")

    input_obj = CreateMemberInput(
        organization_id=org.pk,
        email=request.POST.get("email", ""),
        first_name=request.POST.get("first_name", ""),
        last_name=request.POST.get("last_name", ""),
        role=request.POST.get("role", "member"),
    )

    context = ExecutionContext(actor=request.user, organization=org)
    service = CreateMemberService(context=context)
    result = service.execute(input_obj, actor=request.user)

    if result.ok:
        memberships = _list_members(request)
        table_html = render(request, "usuarios/_table.html", _build_context(request, memberships)).content.decode("utf-8")
        # 3. UX HTMX robusta: OOB swap para tabla y limpiar modal
        oob_content = (
            f'<div id="members-table" hx-swap-oob="true">{table_html}</div>'
            f'<div id="modal-container" hx-swap-oob="true"></div>'
        )
        return HttpResponse(oob_content)

    # Si falla, mantenemos el modal abierto (target es #modal-container)
    errors = result.errors or [ServiceError(code="unknown", message="No se pudo crear el miembro.")]

    resp = render(
        request,
        "usuarios/_modal_form.html",
        {"errors": errors, "organization": org},
        status=200, # HTMX handles 200 fine, we just replace content
    )
    return resp


@login_required
@organization_required
def edit_member_modal(request: HttpRequest, member_id: int) -> HttpResponse:
    org = getattr(request, "organization", None)
    membership = _get_actor_membership(request, org)
    if not membership or membership.role != "admin":
        return HttpResponse(status=403)

    target = (
        Membership.objects.select_related("user")
        .filter(id=member_id, organization=org)
        .first()
    )
    if not target:
        return HttpResponse(status=404)

    context = {
        "errors": [],
        "membership": target,
        "org": org,
        "email_value": target.user.email or target.user.username,
        "member_id": target.id,
        "form_data": {
            "first_name": target.user.first_name,
            "last_name": target.user.last_name,
            "role": target.role,
            "is_active": target.is_active,
        },
    }
    return render(request, "usuarios/_modal_edit_form.html", context)


@login_required
@organization_required
@require_POST
def edit_member_submit(request: HttpRequest, member_id: int) -> HttpResponse:
    org = getattr(request, "organization", None)
    if not org:
        return redirect("orgs:select")

    target = (
        Membership.objects.select_related("user")
        .filter(id=member_id, organization=org)
        .first()
    )
    email_value = (target.user.email or target.user.username) if target else ""

    input_obj = UpdateMemberInput(
        organization_id=org.id,
        member_id=member_id,
        first_name=request.POST.get("first_name", ""),
        last_name=request.POST.get("last_name", ""),
        role=request.POST.get("role", "member"),
        is_active=_parse_bool(request.POST.get("is_active"), default=False),
    )

    context = ExecutionContext(actor=request.user, organization=org)
    service = UpdateMemberService(context=context)
    result = service.execute(input_obj, actor=request.user)

    if result.ok:
        memberships = _list_members(request)
        table_html = render(request, "usuarios/_table.html", _build_context(request, memberships)).content.decode("utf-8")
        oob_content = (
            f'<div id="members-table" hx-swap-oob="true">{table_html}</div>'
            f'<div id="modal-container" hx-swap-oob="true"></div>'
        )
        return HttpResponse(oob_content)

    errors = result.errors or [ServiceError(code="unknown", message="No se pudo actualizar el miembro.")]
    form_data = {
        "first_name": input_obj.first_name,
        "last_name": input_obj.last_name,
        "role": input_obj.role,
        "is_active": input_obj.is_active,
    }
    resp = render(
        request,
        "usuarios/_modal_edit_form.html",
        {
            "errors": errors,
            "org": org,
            "form_data": form_data,
            "member_id": member_id,
            "membership": target,
            "email_value": email_value,
        },
        status=200,
    )
    return resp


@login_required
@organization_required
@require_POST
def toggle_member_active(request: HttpRequest, member_id: int) -> HttpResponse:
    org = getattr(request, "organization", None)
    if not org:
        return redirect("orgs:select")

    active = _parse_bool(request.POST.get("active"))

    input_obj = ToggleMemberActiveInput(
        organization_id=org.id,
        member_id=member_id,
        active=active,
    )

    context = ExecutionContext(actor=request.user, organization=org)
    service = ToggleMemberService(context=context)
    result = service.execute(input_obj, actor=request.user)

    if result.ok:
        memberships = _list_members(request)
        table_html = render(request, "usuarios/_table.html", _build_context(request, memberships)).content.decode("utf-8")
        oob_content = f'<div id="members-table" hx-swap-oob="true">{table_html}</div>'
        return HttpResponse(oob_content)

    errors = result.errors or [ServiceError(code="unknown", message="No se pudo actualizar el estado del miembro.")]
    error_html = "".join([
        f'<div class="alert alert-danger alert-dismissible fade show" role="alert">{e.message}<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>'
        for e in errors
    ])
    oob_message = f'<div id="messages" hx-swap-oob="true">{error_html}</div>'
    return HttpResponse(oob_message, status=200)


@login_required
@organization_required
def export_members(request: HttpRequest) -> HttpResponse:
    org = getattr(request, "organization", None)
    if not org:
        return redirect("orgs:select")

    fmt = (request.GET.get("format") or "csv").lower()
    search = request.GET.get("q") or None
    role = request.GET.get("role") or None
    status = request.GET.get("status") or None

    is_active = None
    if status == "active":
        is_active = True
    elif status == "inactive":
        is_active = False

    input_obj = ExportMembersInput(
        organization_id=org.id,
        include_inactive=True,
        search=search,
        role=role,
        is_active=is_active,
        format=fmt,
    )

    context = ExecutionContext(actor=request.user, organization=org)
    service = ExportMembersService(context=context)
    result = service.execute(input_obj, actor=request.user)

    if result.ok and result.data.get("http_response"):
        return result.data["http_response"]

    errors = result.errors or [ServiceError(code="unknown", message="No se pudo exportar los miembros.")]
    # Respond with 400 and plain text error
    return HttpResponse("; ".join([e.message for e in errors]), status=400)
