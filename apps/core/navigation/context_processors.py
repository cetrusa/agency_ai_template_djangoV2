from django.http import HttpRequest
from apps.core.navigation.registry import registry

def navigation_context(request: HttpRequest):
    """
    Context processor to inject navigation modules into templates.
    Filters modules based on user permissions.
    """
    if not request.user.is_authenticated:
        return {"navigation_modules": []}

    modules = registry.get_modules()
    allowed_modules = []

    for module in modules:
        if module.permission:
            if request.user.has_perm(module.permission):
                allowed_modules.append(module)
        else:
            allowed_modules.append(module)

    return {"navigation_modules": allowed_modules}
