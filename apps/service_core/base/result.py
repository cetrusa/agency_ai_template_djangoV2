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

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, error: ServiceError) -> None:
        self.errors.append(error)

    def add_warning(self, warning: ServiceWarning) -> None:
        self.warnings.append(warning)
