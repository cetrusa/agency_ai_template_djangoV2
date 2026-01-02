from __future__ import annotations

import secrets
from dataclasses import dataclass

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.urls import reverse
from django.utils.text import slugify

from apps.crud_example.models import Item
from apps.orgs.models import Membership, Organization


@dataclass(frozen=True)
class _Result:
    created: bool
    updated: bool


class Command(BaseCommand):
    help = "Bootstrap de DEV: crea org demo, usuario y permisos (SOLO DEBUG=True)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            dest="email",
            default=None,
            help="Email del usuario dev (default: dev@example.com).",
        )
        parser.add_argument(
            "--with-samples",
            "--with_samples",
            action="store_true",
            help="Crea items de ejemplo para probar UI.",
        )
        parser.add_argument(
            "--samples",
            type=int,
            default=10,
            help="Cantidad de items de ejemplo (default: 10).",
        )
        parser.add_argument(
            "--reset-password",
            action="store_true",
            help="Regenera password del usuario (solo DEV).",
        )
        parser.add_argument(
            "--noinput",
            action="store_true",
            help="No pedir input interactivo (usa defaults).",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("bootstrap_dev solo puede ejecutarse cuando DEBUG=True")

        email: str | None = options.get("email")
        noinput: bool = bool(options.get("noinput"))
        with_samples: bool = bool(options.get("with_samples"))
        samples: int = int(options.get("samples") or 0)
        reset_password: bool = bool(options.get("reset_password"))

        if not email:
            if noinput:
                email = "dev@example.com"
            else:
                raw = input("Email para usuario dev [dev@example.com]: ").strip()
                email = raw or "dev@example.com"

        if "@" not in email:
            raise CommandError("Email inválido")

        org_slug = slugify("Demo Org") or "demo-org"

        with transaction.atomic():
            org, org_res = self._get_or_create_org(slug=org_slug)
            user, user_res, generated_password = self._get_or_create_user(email=email, reset_password=reset_password)
            membership, mem_res = self._get_or_create_membership(user=user, org=org)
            perms_added = self._ensure_item_permissions(user=user)

            items_created = 0
            if with_samples:
                items_created = self._ensure_sample_items(target=max(samples, 0))

        self._print_summary(
            email=email,
            password=generated_password,
            org=org,
            org_res=org_res,
            user_res=user_res,
            mem_res=mem_res,
            perms_added=perms_added,
            items_created=items_created,
        )

    def _get_or_create_org(self, *, slug: str):
        org = Organization.objects.filter(slug=slug).first()
        if org:
            # Idempotente: si existe, no forzamos cambios destructivos.
            return org, _Result(created=False, updated=False)

        org = Organization.objects.create(name="Demo Org", slug=slug, is_active=True)
        return org, _Result(created=True, updated=False)

    def _get_or_create_user(self, *, email: str, reset_password: bool):
        User = get_user_model()

        user = User.objects.filter(username=email).first()  # type: ignore[attr-defined]
        if not user:
            user = User.objects.filter(email=email).first()

        generated_password: str | None = None

        if not user:
            generated_password = self._strong_password()
            user = User.objects.create_user(username=email, email=email, password=generated_password)
            return user, _Result(created=True, updated=False), generated_password

        if reset_password:
            generated_password = self._strong_password()
            user.set_password(generated_password)
            user.save(update_fields=["password"])
            return user, _Result(created=False, updated=True), generated_password

        return user, _Result(created=False, updated=False), None

    def _get_or_create_membership(self, *, user, org: Organization):
        mem = Membership.objects.filter(user=user, organization=org).first()
        if not mem:
            mem = Membership.objects.create(
                user=user,
                organization=org,
                role=Membership.ROLE_ADMIN,
                is_active=True,
            )
            return mem, _Result(created=True, updated=False)

        updated = False
        if not mem.is_active:
            mem.is_active = True
            updated = True
        if mem.role != Membership.ROLE_ADMIN:
            mem.role = Membership.ROLE_ADMIN
            updated = True
        if updated:
            mem.save(update_fields=["is_active", "role"])
            return mem, _Result(created=False, updated=True)

        return mem, _Result(created=False, updated=False)

    def _ensure_item_permissions(self, *, user) -> list[str]:
        ct = ContentType.objects.get_for_model(Item)
        wanted = ["view_item", "add_item", "change_item", "delete_item"]
        perms = list(Permission.objects.filter(content_type=ct, codename__in=wanted))
        current = set(user.user_permissions.values_list("pk", flat=True))

        added: list[str] = []
        for p in perms:
            if p.pk not in current:
                user.user_permissions.add(p)
                added.append(p.codename)
        return added

    def _ensure_sample_items(self, *, target: int) -> int:
        if target <= 0:
            return 0

        # Idempotente: asegura al menos N items con nombres deterministas.
        existing = set(Item.objects.filter(name__startswith="Sample Item ").values_list("name", flat=True))
        created = 0

        for i in range(1, target + 1):
            name = f"Sample Item {i:03d}"
            if name in existing:
                continue
            status = "active" if i % 2 else "inactive"
            Item.objects.create(name=name, status=status)
            created += 1
        return created

    def _strong_password(self) -> str:
        # token_urlsafe(24) ~ 32 chars; suficientemente fuerte para dev.
        return secrets.token_urlsafe(24)

    def _print_summary(
        self,
        *,
        email: str,
        password: str | None,
        org: Organization,
        org_res: _Result,
        user_res: _Result,
        mem_res: _Result,
        perms_added: list[str],
        items_created: int,
    ) -> None:
        def _status(res: _Result) -> str:
            if res.created:
                return "created"
            if res.updated:
                return "updated"
            return "unchanged"

        self.stdout.write(self.style.SUCCESS("bootstrap_dev (DEBUG-only)"))
        self.stdout.write(f"Organization: {org.name} ({org.slug}) -> {_status(org_res)}")
        self.stdout.write(f"User: {email} -> {_status(user_res)}")
        self.stdout.write(f"Membership (role=admin): -> {_status(mem_res)}")

        if perms_added:
            self.stdout.write(self.style.SUCCESS(f"Permissions added: {', '.join(perms_added)}"))
        else:
            self.stdout.write("Permissions: unchanged")

        if items_created:
            self.stdout.write(self.style.SUCCESS(f"Sample Items created: {items_created}"))

        if password:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING("LOGIN (imprimir una sola vez):"))
            self.stdout.write(f"  email: {email}")
            self.stdout.write(f"  password: {password}")
        else:
            self.stdout.write("")
            self.stdout.write("LOGIN:")
            self.stdout.write(f"  email: {email}")
            self.stdout.write("  password: (no cambiado; usa --reset-password para regenerar en DEV)")

        self.stdout.write("")
        self.stdout.write(f"Test URL: {reverse('crud_example:list')}")
