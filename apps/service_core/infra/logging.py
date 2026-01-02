from __future__ import annotations

import logging
from typing import Any

from .context import ExecutionContext


class ServiceLogger(logging.LoggerAdapter):
    def __init__(self, service_name: str, context: ExecutionContext | None = None) -> None:
        base = logging.getLogger(f"service_core.{service_name}")
        extra = {
            "request_id": getattr(context, "request_id", None) if context else None,
            "actor": getattr(context, "actor", None) if context else None,
            "organization": getattr(context, "organization", None) if context else None,
            "service": service_name,
        }
        super().__init__(base, extra)

    def process(self, msg: Any, kwargs: dict[str, Any]) -> tuple[Any, dict[str, Any]]:
        extra = kwargs.get("extra") or {}
        # Preserve existing extra; do not mutate message
        merged_extra = {**self.extra, **extra}
        kwargs["extra"] = merged_extra
        return msg, kwargs
