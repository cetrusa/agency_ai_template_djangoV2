from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


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
