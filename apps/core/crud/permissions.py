from __future__ import annotations

from dataclasses import dataclass

from django.http import HttpRequest


@dataclass(frozen=True)
class CrudPermissionSpec:
    """Spec mínimo (Step 9) para permisos declarativos.

    Soporta:
    - None: permitido
    - "app_label.codename": usa user.has_perm
    - "role:owner,admin": requiere rol en org actual
    """

    value: str | None

    def is_allowed(self, request: HttpRequest) -> bool:
        if not self.value:
            return True

        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return False

        raw = self.value.strip()
        if raw.startswith("role:"):
            roles = {r.strip() for r in raw[len("role:") :].split(",") if r.strip()}
            if not roles:
                return False
            try:
                from apps.orgs.services import user_has_org_role

                return user_has_org_role(user, roles=roles)
            except Exception:
                return False

        # Django permission string: "app_label.codename" (ej: "crud_example.view_item")
        return bool(getattr(user, "has_perm", lambda p: False)(raw))
