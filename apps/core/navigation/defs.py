from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Module:
    slug: str
    label: str
    icon: str
    url_name: str
    permission: Optional[str] = None
    kind: str = "business"  # system | business
