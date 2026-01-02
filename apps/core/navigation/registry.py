from typing import List, Dict
from .defs import Module

class NavigationRegistry:
    _modules: Dict[str, Module] = {}

    @classmethod
    def register(cls, module: Module):
        cls._modules[module.slug] = module

    @classmethod
    def get_modules(cls) -> List[Module]:
        return list(cls._modules.values())

    @classmethod
    def get_system_modules(cls) -> List[Module]:
        return [m for m in cls._modules.values() if m.kind == "system"]

    @classmethod
    def get_business_modules(cls) -> List[Module]:
        return [m for m in cls._modules.values() if m.kind == "business"]

registry = NavigationRegistry()
