from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import is_dataclass
from typing import Any

from ..infra.context import ExecutionContext
from ..infra.logging import ServiceLogger
from .result import ServiceResult


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
