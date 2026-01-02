from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ExecutionContext:
    actor: Optional[Any] = None
    request_id: Optional[str] = None
    organization: Optional[Any] = None
    locale: Optional[str] = None
    flags: Dict[str, Any] = field(default_factory=dict)
