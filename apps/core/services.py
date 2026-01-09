from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, is_dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ExecutionContext:
    actor: Optional[Any] = None
    request_id: Optional[str] = None
    organization: Optional[Any] = None
    locale: Optional[str] = None
    flags: Dict[str, Any] = field(default_factory=dict)


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
        merged_extra = {**self.extra, **extra}
        kwargs["extra"] = merged_extra
        return msg, kwargs


@dataclass(frozen=True)
class ServiceError:
    code: str
    message: str
    field: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class ServiceWarning:
    code: str
    message: str
    field: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class ServiceResult:
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[ServiceError] = field(default_factory=list)
    warnings: List[ServiceWarning] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.data = {} if self.data is None else dict(self.data)
        self.meta = {} if self.meta is None else dict(self.meta)
        self.errors = [] if self.errors is None else list(self.errors)
        self.warnings = [] if self.warnings is None else list(self.warnings)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    @classmethod
    def success(cls, data: Optional[Dict[str, Any]] = None, meta: Optional[Dict[str, Any]] = None) -> "ServiceResult":
        return cls(data=data or {}, errors=[], warnings=[], meta=meta or {})

    @classmethod
    def failure(
        cls,
        errors: List[ServiceError] | tuple[ServiceError, ...] | set[ServiceError],
        meta: Optional[Dict[str, Any]] = None,
    ) -> "ServiceResult":
        err_list = list(errors or [])
        if not err_list:
            raise ValueError("failure() requires at least one ServiceError")
        return cls(data={}, errors=err_list, warnings=[], meta=meta or {})

    def add_error(self, error: ServiceError) -> None:
        if error is None:
            return
        self.errors.append(error)

    def add_warning(self, warning: ServiceWarning) -> None:
        if warning is None:
            return
        self.warnings.append(warning)


class BaseService(ABC):
    """Base contract for application services."""

    def __init__(self, context: ExecutionContext | None = None) -> None:
        service_name = self.__class__.__name__
        self.logger = ServiceLogger(service_name, context)
        self._context = context

    @abstractmethod
    def execute(self, input_data: Any, *, actor: Any = None, context: Any = None) -> ServiceResult:
        """Execute service logic.

        input_data MUST be a dataclass instance (never dict, never HttpRequest).
        actor and context are optional executors/runtime info.
        """

    @staticmethod
    def ensure_dataclass(obj: Any) -> None:
        if not is_dataclass(obj):
            raise TypeError("input_data must be a dataclass instance")
